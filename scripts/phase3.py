"""Run the untouched SAS and resident MAS dev floors across Agere RAM tiers.

Code and runtime stay on the host. Inputs, traces, logs, and results use only
the validated external AGERE_SSD_ROOT. Frozen test files are never opened.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from phase2 import (GB, HardMemoryCap, MemoryMonitor, Paths, REPO, SOURCE_MODELS,
                    TIERS, Tee, binary, capture, free_port, kill_tree, request_json,
                    runtime_commit, sha256, validate_paths, verify_locked_tiers,
                    wait_ready, write_json)


DATA_VERSION = "agere-synth-v1"
PROTOCOL_VERSION = "naive-dev-v1"
MAX_GENERATED_TOKENS = 2048
MAS_BUDGETS = {"extractor": 614, "retriever": 205, "drafter": 819, "verifier": 409}
EXPECTED_COUNTS = {"kyc": 100, "credit": 50}
FIELDS = {
    "kyc": ("registry_name", "declared_name", "screening_status", "identity_expiry_date"),
    "credit": ("e_cib_status", "e_cib_last_review_date", "dscr", "current_ratio"),
}
TOOL_SCHEMAS = {
    "document_extractor": {"input": {"case_id": "string", "source_lines": "array[string]"},
                           "output": {"fields": "map[field, {value, span_id, quote}]"}},
    "policy_retriever": {"input": {"case_id": "string", "jurisdiction": "string", "query": "string"},
                         "output": {"status": "UNAVAILABLE until a versioned corpus is staged", "citations": "array"}},
    "financial_calculator": {"input": {"metric": "dscr|current_ratio", "source_values": "map"},
                             "output": {"value": "number", "span_id": "CALC identifier", "source_spans": "array"}},
    "citation_verifier": {"input": {"case_id": "string", "facts": "map[field, {value, span_id}]"},
                          "output": {"checks": "map[field, {supported, reason}]", "all_supported": "boolean"}},
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def append_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def dev_inputs(paths: Paths) -> tuple[list[dict], dict]:
    data_manifest = REPO / "manifests" / "synthetic_datasets.json"
    test_manifest = REPO / "manifests" / "test.sha256"
    if not data_manifest.is_file() or not test_manifest.is_file():
        fail("The committed dataset and frozen test manifests are required")
    entries = load_json(data_manifest)["files"]
    frozen_lines = [line.strip() for line in test_manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any("  " not in line for line in frozen_lines):
        fail("Malformed frozen test SHA-256 manifest")
    test_paths = {line.split("  ", 1)[1] for line in frozen_lines}
    if len(test_paths) != len(frozen_lines):
        fail("The frozen test manifest contains duplicate or malformed paths")
    root = paths.ssd / "datasets" / "agere_synthetic" / DATA_VERSION / "dev"
    cases = []
    inputs = []
    for kind, count in EXPECTED_COUNTS.items():
        relative = f"datasets/agere_synthetic/{DATA_VERSION}/dev/{kind}.jsonl"
        if relative in test_paths:
            fail(f"Dev input is also named in the frozen test manifest: {relative}")
        matching = [entry for entry in entries if entry.get("path") == relative]
        if len(matching) != 1 or matching[0].get("rows") != count:
            fail(f"The committed dev manifest differs from the locked {kind} count")
        path = (paths.ssd / relative).resolve(strict=True)
        if not path.is_relative_to(root):
            fail(f"Dev input escapes the SSD dev directory: {path}")
        checksum = sha256(path)
        if checksum != matching[0]["sha256"]:
            fail(f"Dev input SHA-256 differs from the committed manifest: {path}")
        rows = load_jsonl(path)
        if len(rows) != count:
            fail(f"Expected {count} {kind} dev rows; found {len(rows)}")
        for row in rows:
            if row.get("split") != "dev" or row.get("generation_version") != DATA_VERSION or not row.get("synthetic_only"):
                fail(f"Invalid dev case: {row.get('id')}")
            row["_kind"] = kind
            cases.append(row)
        inputs.append({"path": relative, "rows": count, "sha256": checksum})
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        fail("Duplicate dev case IDs")
    return cases, {
        "dataset_version": DATA_VERSION,
        "dataset_manifest_sha256": sha256(data_manifest),
        "dev_inputs": inputs,
        "dev_case_ids": ids,
        "frozen_test_manifest_sha256": sha256(test_manifest),
        "frozen_test_entries": frozen_lines,
        "test_files_opened": False,
    }


def source_index(case: dict) -> dict[str, dict]:
    index = {}
    for doc in case["case_documents"]:
        for line in doc["lines"]:
            match = re.match(r"^(L\d+)\s", line)
            if not match:
                fail(f"Unlabeled source line in {case['id']}")
            span = f"{doc['id']}#{match.group(1)}"
            index[span] = {"document_id": doc["id"], "text": line}
    return index


def document_extractor(case: dict) -> dict:
    """Return exact source fields and their spans; never derive a decision."""
    extracted = {}
    for span, item in source_index(case).items():
        for key, value in re.findall(r"([A-Za-z][A-Za-z0-9_]*)=([^;]+)", item["text"]):
            extracted.setdefault(key, []).append({"value": value.strip().rstrip("."),
                                                    "span_id": span, "quote": item["text"]})
    return {"tool": "document_extractor", "status": "ok", "fields": extracted}


def financial_calculator(case: dict, extraction: dict) -> dict:
    """Compute ratios from source spans. Both arms receive the same result."""
    if case["_kind"] != "credit":
        return {"tool": "financial_calculator", "status": "not_applicable", "results": {}}
    fields = extraction["fields"]
    required = ("operating_profit_pkr", "annual_debt_service_pkr",
                "current_assets_pkr", "current_liabilities_pkr")
    if any(len(fields.get(key, [])) != 1 for key in required):
        fail(f"Calculator source field missing or ambiguous in {case['id']}")
    numbers = {key: int(fields[key][0]["value"]) for key in required}
    if numbers["annual_debt_service_pkr"] <= 0 or numbers["current_liabilities_pkr"] <= 0:
        fail(f"Calculator denominator is nonpositive in {case['id']}")
    return {"tool": "financial_calculator", "status": "ok", "results": {
        "dscr": {"value": round(numbers["operating_profit_pkr"] / numbers["annual_debt_service_pkr"], 4),
                 "span_id": "CALC#DSCR", "source_spans": [fields["operating_profit_pkr"][0]["span_id"],
                                                       fields["annual_debt_service_pkr"][0]["span_id"]]},
        "current_ratio": {"value": round(numbers["current_assets_pkr"] / numbers["current_liabilities_pkr"], 4),
                          "span_id": "CALC#CURRENT_RATIO",
                          "source_spans": [fields["current_assets_pkr"][0]["span_id"],
                                           fields["current_liabilities_pkr"][0]["span_id"]]},
    }}


def policy_retriever(case: dict) -> dict:
    """The versioned SBP/FATF policy index is not staged; never invent policy."""
    return {"tool": "policy_retriever", "status": "UNAVAILABLE",
            "case_id": case["id"], "citations": [],
            "reason": "No versioned policy corpus/index is staged for Phase 3."}


def expected_facts(case: dict, tools: dict) -> dict[str, dict]:
    labels = case["labels"]
    index = source_index(case)
    def line_span(number: str) -> str:
        matches = [span for span in index if span.endswith(f"#{number}")]
        if len(matches) != 1:
            fail(f"Missing unique {number} span in {case['id']}")
        return matches[0]
    if case["_kind"] == "kyc":
        expiry = tools["document_extractor"]["fields"]["expiry"][0]["value"]
        return {
            "registry_name": {"value": labels["registry_name"], "span_id": line_span("L03")},
            "declared_name": {"value": labels["declared_name"], "span_id": line_span("L05")},
            "screening_status": {"value": labels["screening_status"], "span_id": line_span("L04")},
            "identity_expiry_date": {"value": "MISSING" if expiry == "NOT_PROVIDED" else expiry,
                                     "span_id": None if expiry == "NOT_PROVIDED" else line_span("L01")},
        }
    calculations = tools["financial_calculator"]["results"]
    review = tools["document_extractor"]["fields"]["last_review_date"][0]["value"]
    return {
        "e_cib_status": {"value": labels["e_cib_status"], "span_id": line_span("L04")},
        "e_cib_last_review_date": {"value": "MISSING" if review == "NOT_PROVIDED" else review,
                                   "span_id": None if review == "NOT_PROVIDED" else line_span("L04")},
        "dscr": {"value": calculations["dscr"]["value"], "span_id": "CALC#DSCR"},
        "current_ratio": {"value": calculations["current_ratio"]["value"], "span_id": "CALC#CURRENT_RATIO"},
    }


def common_tools(case: dict) -> dict:
    extraction = document_extractor(case)
    return {"document_extractor": extraction,
            "financial_calculator": financial_calculator(case, extraction),
            "policy_retriever": policy_retriever(case)}


def parse_json_object(text: str) -> dict | None:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", stripped, flags=re.IGNORECASE)
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def citation_verifier(case: dict, facts: dict, truth: dict) -> dict:
    """Exact span match for document claims; calculator IDs for derived ratios."""
    index = source_index(case)
    checks = {}
    for field, expected in truth.items():
        stated = facts.get(field)
        if not isinstance(stated, dict):
            checks[field] = {"supported": False, "reason": "missing_structured_fact"}
            continue
        value, span = stated.get("value"), stated.get("span_id")
        if expected["value"] == "MISSING":
            supported = value == "MISSING" and span is None
        elif field in ("dscr", "current_ratio"):
            supported = value == expected["value"] and span == expected["span_id"]
        else:
            supported = (value == expected["value"] and span == expected["span_id"] and
                         span in index and str(value) in index[span]["text"])
        checks[field] = {"supported": supported,
                         "reason": "exact_source_or_calculator_match" if supported else "unsupported_value_or_span"}
    return {"tool": "citation_verifier", "checks": checks,
            "all_supported": all(item["supported"] for item in checks.values())}


def score_case(case: dict, answer: dict | None, tools: dict, arm: str) -> dict:
    truth = expected_facts(case, tools)
    if answer is None:
        missing_count = sum(item["value"] == "MISSING" for item in truth.values())
        return {"valid_json": False, "structured_claims_complete": False,
                "structured_invention": None,
                "mismatch_eligible": bool(case["_kind"] == "kyc" and case["labels"]["identity_name_mismatch"]),
                "mismatch_detected": False, "grounded": 0,
                "grounding_total": len(truth) - missing_count,
                "refusal_correct": 0, "refusal_total": missing_count,
                "citation_verifier": {"tool": "citation_verifier", "all_supported": False, "checks": {}},
                "failure_tag": "S3" if arm == "sas" else "M2"}
    facts = answer.get("facts") if isinstance(answer.get("facts"), dict) else {}
    verifier = citation_verifier(case, facts, truth)
    claims = [field for field, expected in truth.items() if expected["value"] != "MISSING"]
    claims_complete = all(isinstance(facts.get(field), dict) and
                          facts[field].get("value") is not None and
                          (truth[field]["value"] == "MISSING" or facts[field]["value"] != "MISSING")
                          for field in truth)
    invented_fields = [field for field in truth if isinstance(facts.get(field), dict) and
                       facts[field].get("value") not in (None, "MISSING", truth[field]["value"])]
    invented = bool(invented_fields)
    grounded = sum(verifier["checks"][field]["supported"] for field in claims)
    missing = [field for field, expected in truth.items() if expected["value"] == "MISSING"]
    refusal_correct = sum(verifier["checks"][field]["supported"] for field in missing)
    mismatch_eligible = case["_kind"] == "kyc" and bool(case["labels"]["identity_name_mismatch"])
    mismatch_detected = answer.get("identity_name_mismatch") is True if mismatch_eligible else False
    mismatch_false_positive = (case["_kind"] == "kyc" and not mismatch_eligible and
                               answer.get("identity_name_mismatch") is True)
    valid_case_id = answer.get("case_id") == case["id"]
    if not valid_case_id:
        failure_tag = "S3" if arm == "sas" else "M2"
    elif invented:
        failure_tag = ("S4" if any(field in ("dscr", "current_ratio") for field in invented_fields)
                       else "S6") if arm == "sas" else "M3"
    elif grounded < len(claims):
        failure_tag = "S6" if arm == "sas" else "M7"
    elif refusal_correct < len(missing):
        failure_tag = "S2" if arm == "sas" else "M2"
    elif mismatch_eligible and not mismatch_detected:
        failure_tag = "S7" if arm == "sas" else "M10"
    elif mismatch_false_positive:
        failure_tag = "S7" if arm == "sas" else "M10"
    else:
        failure_tag = None
    return {"valid_json": True, "valid_case_id": valid_case_id,
            "structured_claims_complete": claims_complete,
            "structured_invention": invented, "invented_fields": invented_fields,
            "mismatch_eligible": mismatch_eligible,
            "mismatch_detected": mismatch_detected,
            "mismatch_false_positive": mismatch_false_positive,
            "grounded": grounded,
            "grounding_total": len(claims), "refusal_correct": refusal_correct,
            "refusal_total": len(missing), "citation_verifier": verifier,
            "failure_tag": failure_tag}


def prompt_text(case: dict, tools: dict, *, extractor_proposal: dict | None = None) -> str:
    kind = case["_kind"]
    document = "\n".join(line for doc in case["case_documents"] for line in doc["lines"])
    schema = {"case_id": case["id"],
              "facts": {field: {"value": "source value, calculator value, or MISSING",
                                "span_id": "exact source span, CALC ID, or null"}
                        for field in FIELDS[kind]},
              "identity_name_mismatch": "boolean or null",
              "draft": "short factual draft for human review only"}
    text = (f"Case type: {kind}. Case id: {case['id']}.\n"
            "Source documents:\n" + document + "\n\n"
            "Identical deterministic tool results available to both systems:\n" +
            json.dumps(tools, ensure_ascii=False, sort_keys=True) + "\n\n"
            "Return exactly one JSON object with this shape:\n" +
            json.dumps(schema, ensure_ascii=False) + "\n"
            "Use source spans for document facts and CALC IDs for ratios. "
            "Represent absent source fields as MISSING with null span. "
            "For credit cases set identity_name_mismatch to null. "
            "Do not infer a policy decision while policy_retriever is UNAVAILABLE. "
            "Draft only; a human makes every approval or compliance decision.")
    if extractor_proposal is not None:
        text += "\n\nExtractor model proposal (may contain errors; check against tools):\n"
        text += json.dumps(extractor_proposal, ensure_ascii=False, sort_keys=True)
    return text


def chat_prompt(user: str, system: str) -> str:
    return (f"<|im_start|>system\n{system}<|im_end|>\n"
            f"<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n")


class ServerGroup:
    def __init__(self, paths: Paths, tier: str, arm: str, cap_bytes: int,
                 context: int, directory: Path, timeout_seconds: int):
        self.paths, self.tier, self.arm = paths, tier, arm
        self.cap_bytes, self.context = cap_bytes, context
        self.directory, self.timeout_seconds = directory, timeout_seconds
        self.processes: list[subprocess.Popen] = []
        self.handles = []
        self.ports: dict[str, int] = {}
        self.monitor = MemoryMonitor(cap_bytes, GB)
        self.hard: HardMemoryCap | None = None
        self.monitoring = False
        self.started_at = now()

    def __enter__(self) -> "ServerGroup":
        import psutil

        idle = psutil.virtual_memory()
        if idle.available < self.cap_bytes + GB:
            fail(f"Host idle memory {idle.available / GB:.2f} GB cannot support the frozen "
                 f"{self.cap_bytes / GB:.2f} GB process cap plus 1 GB OS reserve. "
                 "Use a new run id on this host, or free background memory.")
        self.idle = idle
        self.hard = HardMemoryCap(self.cap_bytes, f"phase3-{self.tier}-{self.arm}")
        self.monitor.start()
        self.monitoring = True
        try:
            if self.arm == "sas":
                models = (("sas", TIERS[self.tier]["sas"], "q4_k_m"),)
            else:
                models = tuple((instance, size, "f16") for instance, size in TIERS[self.tier]["mas"])
            for instance, size, kind in models:
                model = self.paths.output(size, kind)
                port = free_port()
                log = self.directory / "logs" / f"server_{instance}.log"
                log.parent.mkdir(parents=True, exist_ok=True)
                handle = log.open("a", encoding="utf-8")
                self.handles.append(handle)
                command = [str(binary(self.paths, "llama-server")), "--model", str(model),
                           "--host", "127.0.0.1", "--port", str(port),
                           "--ctx-size", str(self.context), "--n-gpu-layers", "0",
                           "--fit", "off", "--threads", "4" if self.arm == "sas" else "2",
                           "--parallel", "1"]
                handle.write(f"\n[{now()}] command={subprocess.list2cmdline(command)}\n")
                handle.flush()
                process = subprocess.Popen(command, cwd=REPO, stdout=handle, stderr=subprocess.STDOUT)
                self.processes.append(process)
                self.monitor.processes.append(process)
                self.hard.add(process.pid)
                print(f"Loading {self.tier} GB {self.arm} {instance} ({size}); log={log}", flush=True)
                wait_ready(process, port, self.monitor, instance, self.timeout_seconds, log)
                self.ports[instance] = port
            return self
        except BaseException:
            self.__exit__(*sys.exc_info())
            raise

    def complete(self, instance: str, prompt: str, limit: int) -> tuple[str, int, float]:
        if self.monitor.breach:
            fail(self.monitor.breach)
        started = time.monotonic()
        response = request_json(f"http://127.0.0.1:{self.ports[instance]}/completion",
                                {"prompt": prompt, "n_predict": limit,
                                 "temperature": 0.0, "seed": 42,
                                 "stop": ["<|im_end|>"]}, timeout=1800)
        if self.monitor.breach:
            fail(self.monitor.breach)
        tokens = response.get("tokens_predicted")
        if not isinstance(tokens, int) or tokens < 0 or tokens > limit:
            fail(f"Server returned an invalid token count for {instance}: {tokens!r}")
        return str(response.get("content", "")), tokens, time.monotonic() - started

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.monitoring:
            self.monitor.stop()
        for process in self.processes:
            kill_tree(process)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        if self.hard is not None:
            self.hard.close()
        for handle in self.handles:
            handle.close()
        report = {
            "started_at_utc": self.started_at, "completed_at_utc": now(),
            "tier_gb": int(self.tier), "arm": self.arm,
            "host_physical_bytes": self.idle.total,
            "idle_host_available_bytes": self.idle.available,
            "idle_non_job_use_bytes": self.idle.total - self.idle.available,
            "nominal_process_cap_bytes": int(TIERS[self.tier]["cap_gb"] * GB),
            "effective_process_cap_bytes": self.cap_bytes,
            "os_safety_reserve_bytes": GB,
            "peak_process_tree_rss_bytes": self.monitor.peak_rss_bytes,
            "minimum_host_available_bytes": self.monitor.minimum_host_available_bytes if self.monitor.samples else None,
            "hard_cap_method": self.hard.method if self.hard else None,
            "memory_breach": self.monitor.breach,
            "run_error": str(exc) if exc else None,
        }
        sessions_path = self.directory / "memory_sessions.jsonl"
        append_jsonl(sessions_path, report)
        sessions = load_jsonl(sessions_path)
        availability = [item["minimum_host_available_bytes"] for item in sessions
                        if item["minimum_host_available_bytes"] is not None]
        write_json(self.directory / "memory.json", {
            "sessions": len(sessions),
            "effective_process_cap_bytes": self.cap_bytes,
            "peak_process_tree_rss_bytes": max(item["peak_process_tree_rss_bytes"] for item in sessions),
            "minimum_host_available_bytes": min(availability) if availability else None,
            "memory_breaches": [item["memory_breach"] for item in sessions if item["memory_breach"]],
            "run_errors": [item["run_error"] for item in sessions if item["run_error"]],
        })


def model_inputs(paths: Paths, tier: str) -> dict:
    manifest = paths.manifests / "gguf_artifacts.json"
    if not manifest.is_file():
        fail(f"Phase 2 GGUF manifest is missing: {manifest}")
    data = load_json(manifest)
    if data.get("llama_cpp_commit") != runtime_commit(paths):
        fail("Phase 2 GGUF manifest and current llama.cpp runtime commits differ")
    required = [(TIERS[tier]["sas"], "q4_k_m")]
    required += [(size, "f16") for _, size in TIERS[tier]["mas"]]
    results = []
    for size, kind in dict.fromkeys(required):
        expected = paths.output(size, kind).relative_to(paths.ssd).as_posix()
        matches = [entry for entry in data.get("artifacts", []) if entry.get("path") == expected]
        if len(matches) != 1:
            fail(f"Missing unique GGUF manifest entry for {expected}")
        item = matches[0]
        model = paths.output(size, kind)
        if not model.is_file() or model.stat().st_size != item.get("size_bytes"):
            fail(f"Missing or different GGUF file: {model}")
        print(f"Verifying {model.name}...", flush=True)
        if sha256(model, progress=True) != item.get("sha256"):
            fail(f"GGUF SHA-256 mismatch: {model}")
        results.append({"size": size, "kind": kind, "repo_id": SOURCE_MODELS[size],
                        "path": expected, "size_bytes": model.stat().st_size,
                        "sha256": item["sha256"], "source_revision": item["source_revision"]})
    return {"manifest_path": "phase2/manifests/gguf_artifacts.json",
            "manifest_sha256": sha256(manifest), "llama_cpp_commit": data["llama_cpp_commit"],
            "models": results}


def smoke_context(paths: Paths, tier: str) -> int:
    contexts = []
    for arm in ("sas", "mas"):
        path = paths.runs / f"smoke_{arm}_{tier}gb.json"
        if not path.is_file():
            fail(f"Run Phase 2 {tier} GB smoke before Phase 3: {path}")
        record = load_json(path)
        if record.get("status") != "passed" or record.get("tier_ram_gb") != int(tier):
            fail(f"Phase 2 {tier} GB {arm} smoke did not pass: {path}")
        contexts.append(record.get("context_tokens_per_model"))
    if contexts[0] != contexts[1] or not isinstance(contexts[0], int):
        fail(f"Phase 2 SAS and MAS contexts differ for {tier} GB")
    return contexts[0]


def run_directory(paths: Paths, run_id: str, tier: str) -> Path:
    return paths.ssd / "runs" / "phase3" / run_id / f"tier{tier}"


def prepare_tier(paths: Paths, tier: str, run_id: str, limit: int) -> tuple[Path, list[dict], dict]:
    import psutil

    cases, datasets = dev_inputs(paths)
    if limit > len(cases):
        fail(f"--limit {limit} exceeds {len(cases)} dev cases")
    cases = cases[:limit]
    models = model_inputs(paths, tier)
    context = smoke_context(paths, tier)
    directory = run_directory(paths, run_id, tier)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / "run_manifest.json"
    cap = min(int(TIERS[tier]["cap_gb"] * GB), psutil.virtual_memory().available - GB)
    if cap <= 0:
        fail("Insufficient host memory after the required 1 GB OS reserve")
    fixed = {"protocol_version": PROTOCOL_VERSION, "tier_gb": int(tier),
             "limit": limit, "case_ids": [case["id"] for case in cases],
             "datasets": datasets, "models": models, "context_tokens_per_model": context,
             "token_cap": MAX_GENERATED_TOKENS, "mas_token_schedule": MAS_BUDGETS,
             "tool_schemas": TOOL_SCHEMAS, "policy_corpus_status": "UNAVAILABLE",
             "project_commit": capture(["git", "rev-parse", "HEAD"]),
             "problem_taxonomy_sha256": sha256(REPO / "configs" / "locked" / "problems.yaml"),
             "residency": "resident", "device": "cpu", "seed": 42}
    if manifest.is_file():
        existing = load_json(manifest)
        if any(existing.get(key) != value for key, value in fixed.items()):
            fail(f"Phase 3 inputs/settings changed. Choose a new --run-id: {manifest}")
        cap = existing["effective_process_cap_bytes"]
    else:
        write_json(manifest, {**fixed, "created_at_utc": now(),
                              "effective_process_cap_bytes": cap,
                              "nominal_process_cap_bytes": int(TIERS[tier]["cap_gb"] * GB),
                              "os_safety_reserve_bytes": GB,
                              "status": "provisional_synthetic_dev"})
    print(f"Tier {tier} GB: {len(cases)} dev cases; shared cap {cap / GB:.2f} GB; "
          f"context {context}; SSD output {directory}", flush=True)
    return directory, cases, load_json(manifest)


def already_done(path: Path, expected_ids: list[str]) -> set[str]:
    if not path.exists():
        return set()
    records = load_jsonl(path)
    ids = [row.get("case_id") for row in records]
    if len(ids) != len(set(ids)) or any(case_id not in expected_ids for case_id in ids):
        fail(f"Case output has duplicate or unexpected IDs: {path}")
    return set(ids)


def run_case(case: dict, arm: str, tools: dict, group: ServerGroup,
             stage_file: Path) -> dict:
    base_system = ("You are a careful local finance drafting assistant. Use only the case packet, "
                   "deterministic tool results, and exact citations. Return one JSON object. "
                   "Never approve or clear a case; a human reviews all outputs.")
    stages = []
    if arm == "sas":
        prompt = chat_prompt(prompt_text(case, tools), base_system)
        response, tokens, elapsed = group.complete("sas", prompt, MAX_GENERATED_TOKENS)
        stages.append({"stage": "sas", "model": TIERS[group.tier]["sas"],
                       "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                       "response": response, "generated_tokens": tokens,
                       "elapsed_seconds": elapsed})
        answer = parse_json_object(response)
    else:
        document = "\n".join(line for doc in case["case_documents"] for line in doc["lines"])
        extract_prompt = chat_prompt(
            f"Extract source facts for {case['id']} from these lines. Return JSON with a facts map "
            f"using exact values and span IDs; do not draft or decide.\n{document}", base_system)
        extraction_text, extract_tokens, extract_elapsed = group.complete(
            "extractor", extract_prompt, MAS_BUDGETS["extractor"])
        proposal = parse_json_object(extraction_text)
        stages.append({"stage": "extractor", "model": dict(TIERS[group.tier]["mas"])["extractor"],
                       "prompt_sha256": hashlib.sha256(extract_prompt.encode()).hexdigest(),
                       "response": extraction_text, "generated_tokens": extract_tokens,
                       "elapsed_seconds": extract_elapsed})
        draft_prompt = chat_prompt(prompt_text(case, tools, extractor_proposal=proposal), base_system)
        draft_text, draft_tokens, draft_elapsed = group.complete(
            "orchestrator_drafter", draft_prompt, MAS_BUDGETS["drafter"])
        answer = parse_json_object(draft_text)
        stages.append({"stage": "orchestrator_drafter",
                       "model": dict(TIERS[group.tier]["mas"])["orchestrator_drafter"],
                       "prompt_sha256": hashlib.sha256(draft_prompt.encode()).hexdigest(),
                       "response": draft_text, "generated_tokens": draft_tokens,
                       "elapsed_seconds": draft_elapsed})
        verify_prompt = chat_prompt(
            f"Inspect this draft for unsupported claims. Return JSON with verdict PASS or FAIL "
            f"and an unsupported_fields array. Do not rewrite the draft.\n"
            f"Source documents and tools:\n{prompt_text(case, tools)}\n"
            f"Draft:\n{draft_text}", base_system)
        verify_text, verify_tokens, verify_elapsed = group.complete(
            "verifier", verify_prompt, MAS_BUDGETS["verifier"])
        stages.append({"stage": "verifier", "model": dict(TIERS[group.tier]["mas"])["verifier"],
                       "prompt_sha256": hashlib.sha256(verify_prompt.encode()).hexdigest(),
                       "response": verify_text, "generated_tokens": verify_tokens,
                       "elapsed_seconds": verify_elapsed})
    total_tokens = sum(stage["generated_tokens"] for stage in stages)
    if total_tokens > MAX_GENERATED_TOKENS:
        fail(f"Case {case['id']} exceeded the shared {MAX_GENERATED_TOKENS} generated-token cap")
    outcome = score_case(case, answer, tools, arm)
    for stage in stages:
        append_jsonl(stage_file, {"case_id": case["id"], "arm": arm, "tier_gb": int(group.tier),
                                  "peak_process_tree_rss_bytes_so_far": group.monitor.peak_rss_bytes,
                                  "minimum_host_available_bytes_so_far": group.monitor.minimum_host_available_bytes,
                                  "recorded_at_utc": now(), **stage})
    return {"case_id": case["id"], "corpus": case["corpus"], "kind": case["_kind"],
            "arm": arm, "tier_gb": int(group.tier), "answer": answer,
            "model_verifier": parse_json_object(stages[-1]["response"]) if arm == "mas" else None,
            "tools": tools, "score": outcome, "generated_tokens": total_tokens,
            "elapsed_seconds": sum(stage["elapsed_seconds"] for stage in stages),
            "peak_process_tree_rss_bytes_so_far": group.monitor.peak_rss_bytes,
            "completed_at_utc": now()}


def summarize_arm(directory: Path, arm: str, expected_ids: list[str]) -> dict:
    output = directory / f"naive_{arm}" / "cases.jsonl"
    if not output.is_file():
        return {"status": "not_started", "cases_completed": 0, "cases_expected": len(expected_ids)}
    records = load_jsonl(output)
    seen = [row["case_id"] for row in records]
    if len(seen) != len(set(seen)) or any(case_id not in expected_ids for case_id in seen):
        fail(f"Duplicate or unknown cases in {output}")
    valid = [row for row in records if row["score"]["valid_json"]]
    scorable = [row for row in valid if row["score"]["structured_claims_complete"]]
    mismatch = [row for row in records if row["score"]["mismatch_eligible"]]
    grounding_total = sum(row["score"]["grounding_total"] for row in records)
    refusal_total = sum(row["score"]["refusal_total"] for row in records)
    failures = Counter(row["score"].get("failure_tag") for row in records if row["score"].get("failure_tag"))
    memory_path = directory / f"naive_{arm}" / "memory.json"
    memory = load_json(memory_path) if memory_path.is_file() else None
    memory_valid = (memory is not None and not memory["memory_breaches"] and
                    memory["peak_process_tree_rss_bytes"] <= memory["effective_process_cap_bytes"] and
                    memory["minimum_host_available_bytes"] is not None and
                    memory["minimum_host_available_bytes"] >= GB)
    summary = {
        "status": "complete" if len(records) == len(expected_ids) and memory_valid
        else "invalid_memory" if len(records) == len(expected_ids) and not memory_valid else "partial",
        "arm": arm, "cases_completed": len(records), "cases_expected": len(expected_ids),
        "valid_json_rate": sum(row["score"]["valid_json"] for row in records) / len(records) if records else None,
        "structured_invention_rate_among_complete_claim_sets":
            sum(row["score"]["structured_invention"] for row in scorable) / len(scorable) if scorable else None,
        "complete_structured_claim_sets": len(scorable),
        "unscorable_invalid_or_incomplete_cases": len(records) - len(scorable),
        "mismatch_recall": sum(row["score"]["mismatch_detected"] for row in mismatch) / len(mismatch) if mismatch else None,
        "mismatch_positive_cases": len(mismatch),
        "mismatch_false_positives": sum(bool(row["score"].get("mismatch_false_positive")) for row in records),
        "grounding_accuracy": sum(row["score"]["grounded"] for row in records) / grounding_total if grounding_total else None,
        "grounded_claims": sum(row["score"]["grounded"] for row in records),
        "grounding_claims_total": grounding_total,
        "refusal_correctness": sum(row["score"]["refusal_correct"] for row in records) / refusal_total if refusal_total else None,
        "correct_missing_refusals": sum(row["score"]["refusal_correct"] for row in records),
        "missing_refusals_total": refusal_total,
        "generated_tokens": sum(row["generated_tokens"] for row in records),
        "generation_seconds": sum(row["elapsed_seconds"] for row in records),
        "failure_tags": dict(sorted(failures.items())),
        "case_output": f"naive_{arm}/cases.jsonl",
        "stage_trace": f"naive_{arm}/stages.jsonl",
        "memory": f"naive_{arm}/memory.json",
        "memory_valid": memory_valid,
        "effective_process_cap_bytes": memory["effective_process_cap_bytes"] if memory else None,
        "peak_process_tree_rss_bytes": memory["peak_process_tree_rss_bytes"] if memory else None,
        "minimum_host_available_bytes": memory["minimum_host_available_bytes"] if memory else None,
        "metric_scope": "structured claims on synthetic dev cases; draft prose and policy grounding need later review",
    }
    write_json(directory / f"naive_{arm}" / "summary.json", summary)
    return summary


def summarize_tier(directory: Path, expected_ids: list[str], *, full_run: bool) -> dict:
    arms = {arm: summarize_arm(directory, arm, expected_ids) for arm in ("sas", "mas")}
    complete = all(value["status"] == "complete" for value in arms.values())
    result = {"generated_at_utc": now(), "status": "complete_provisional" if complete else "incomplete",
              "tier_gb": load_json(directory / "run_manifest.json")["tier_gb"],
              "dataset": "Agere-KYC-Synth and Agere-Credit-Synth dev",
              "cases_expected_per_arm": len(expected_ids), "arms": arms,
              "comparison": {
                  "structured_invention_delta_mas_minus_sas": (
                      arms["mas"]["structured_invention_rate_among_complete_claim_sets"] -
                      arms["sas"]["structured_invention_rate_among_complete_claim_sets"])
                  if complete and all(arms[arm]["structured_invention_rate_among_complete_claim_sets"] is not None for arm in arms)
                  else None,
                  "mismatch_recall_delta_mas_minus_sas": (
                      arms["mas"]["mismatch_recall"] - arms["sas"]["mismatch_recall"])
                  if complete and all(arms[arm]["mismatch_recall"] is not None for arm in arms) else None,
              },
              "limitations": ["Synthetic starter corpus has not passed the roadmap data-quality gate",
                              "No versioned policy corpus/index; policy retrieval is UNAVAILABLE",
                              "Invention metric covers structured facts; draft prose requires later review",
                              "The 2048 ceiling counts generated output tokens, not private reasoning tokens",
                              "Dev floor only; the frozen test split was not read"]}
    write_json(directory / "phase3_summary.json", result)
    floor_path = directory / "naive_floor.json"
    if complete and full_run and not floor_path.exists():
        floor = {"frozen_at_utc": now(), "status": "provisional_synthetic_dev_floor",
                 "tier_gb": result["tier_gb"], "run_manifest_sha256": sha256(directory / "run_manifest.json"),
                 "sas": arms["sas"], "mas": arms["mas"],
                 "limitations": result["limitations"]}
        try:
            with floor_path.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(floor, indent=2) + "\n")
        except FileExistsError:
            pass
    print(f"Tier summary: {directory / 'phase3_summary.json'} ({result['status']})", flush=True)
    return result


def run_arm(paths: Paths, tier: str, arm: str, directory: Path,
            cases: list[dict], manifest: dict, timeout_seconds: int) -> None:
    arm_dir = directory / f"naive_{arm}"
    arm_dir.mkdir(parents=True, exist_ok=True)
    output = arm_dir / "cases.jsonl"
    stage_file = arm_dir / "stages.jsonl"
    expected_ids = manifest["case_ids"]
    completed = already_done(output, expected_ids)
    remaining = [case for case in cases if case["id"] not in completed]
    if not remaining:
        print(f"Tier {tier} GB {arm}: already completed {len(completed)} cases", flush=True)
        return
    with ServerGroup(paths, tier, arm, manifest["effective_process_cap_bytes"],
                     manifest["context_tokens_per_model"], arm_dir, timeout_seconds) as group:
        for index, case in enumerate(remaining, 1):
            if group.monitor.breach:
                fail(group.monitor.breach)
            tools = common_tools(case)
            record = run_case(case, arm, tools, group, stage_file)
            append_jsonl(output, record)
            print(f"{tier} GB {arm.upper()} {len(completed) + index}/{len(cases)} "
                  f"{case['id']} tokens={record['generated_tokens']} "
                  f"invention={record['score']['structured_invention']} "
                  f"RSS_peak={group.monitor.peak_rss_bytes / GB:.2f} GB", flush=True)
        if group.monitor.breach:
            fail(group.monitor.breach)


def execute(paths: Paths, args: argparse.Namespace) -> int:
    verify_locked_tiers()
    runtime_commit(paths)
    tiers = ("16", "8", "32") if args.tier == "all" else (args.tier,)
    failures = []
    tier_status = {}
    for tier in tiers:
        try:
            directory, cases, manifest = prepare_tier(paths, tier, args.run_id, args.limit)
            if args.step == "run":
                arms = ("sas", "mas") if args.arm == "both" else (args.arm,)
                for arm in arms:
                    try:
                        run_arm(paths, tier, arm, directory, cases, manifest, args.load_timeout)
                    except (RuntimeError, OSError, subprocess.SubprocessError,
                            urllib.error.URLError, TimeoutError) as exc:
                        failure = {"tier": tier, "arm": arm, "at_utc": now(), "error": str(exc)}
                        failures.append(failure)
                        write_json(directory / f"naive_{arm}" / "failure.json", failure)
                        print(f"Tier {tier} GB {arm} failed: {exc}", file=sys.stderr, flush=True)
            result = summarize_tier(directory, manifest["case_ids"], full_run=args.limit == 150)
            tier_status[tier] = result["status"]
        except (RuntimeError, OSError, ValueError, KeyError) as exc:
            failures.append({"tier": tier, "at_utc": now(), "error": str(exc)})
            tier_status[tier] = "failed"
            print(f"Tier {tier} GB preparation failed: {exc}", file=sys.stderr, flush=True)
            continue
    aggregate = paths.ssd / "runs" / "phase3" / args.run_id / "all_tiers_summary.json"
    write_json(aggregate, {"generated_at_utc": now(), "tier_status": tier_status,
                           "failure_count": len(failures), "failures": failures,
                           "status": "complete_provisional" if all(value == "complete_provisional" for value in tier_status.values())
                           and len(tier_status) == len(tiers) else "incomplete"})
    print(f"All-tier status: {aggregate}", flush=True)
    return 1 if failures or any(value != "complete_provisional" for value in tier_status.values()) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=("run", "summarize"))
    parser.add_argument("--tier", choices=("8", "16", "32", "all"), default="all")
    parser.add_argument("--arm", choices=("sas", "mas", "both"), default="both")
    parser.add_argument("--run-id", default="untouched_dev_v1")
    parser.add_argument("--limit", type=int, default=150,
                        help="dev cases per arm; use a new run id for a preview")
    parser.add_argument("--load-timeout", type=int, default=900)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", args.run_id):
        parser.error("--run-id must be a simple name up to 64 characters")
    if not 1 <= args.limit <= 150 or args.load_timeout < 30:
        parser.error("--limit must be 1–150 and --load-timeout must be at least 30")
    try:
        paths = validate_paths()
        session_log = paths.ssd / "runs" / "phase3" / args.run_id / "logs" / f"session_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.log"
        session_log.parent.mkdir(parents=True, exist_ok=True)
        with session_log.open("a", encoding="utf-8") as stream:
            with redirect_stdout(Tee(sys.stdout, stream)), redirect_stderr(Tee(sys.stderr, stream)):
                print(f"[{now()}] Phase 3 {args.step}; repository={REPO}; SSD={paths.ssd}", flush=True)
                try:
                    return execute(paths, args)
                except (RuntimeError, OSError, ValueError, KeyError) as exc:
                    print(f"ERROR: {exc}", file=sys.stderr, flush=True)
                    return 1
                except KeyboardInterrupt:
                    print("Interrupted; rerun with the same run id to resume completed cases.", file=sys.stderr)
                    return 130
    except (RuntimeError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        return 1
    except KeyboardInterrupt:
        print("Interrupted; rerun with the same run id to resume completed cases.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
