"""8 GB tier study: naive floor, MAS repair, and one held-out comparison.

Code stays in the repository. Cases, weights, traces, and reports stay on
AGERE_SSD_ROOT. The frozen test split is opened only by the `final` command.
Inference is CPU. The job is capped at the 8 GB tier budget even when the
host has more RAM.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import subprocess
import sys
import threading
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import phase2
import phase3

STUDY = "tier8-8gb-v1"
TIER = "8"
NOMINAL_CAP = int(6.4 * phase2.GB)
CONTEXT = 4096
SEED = 42
MAX_TOKENS = phase3.MAX_GENERATED_TOKENS
BUDGETS = phase3.MAS_BUDGETS
REPAIR_TOKENS = MAX_TOKENS - BUDGETS["extractor"] - BUDGETS["drafter"] - BUDGETS["verifier"]


def study_dir(paths: phase2.Paths) -> Path:
    path = paths.ssd / "runs" / "tier8" / STUDY
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, value: dict) -> None:
    phase2.write_json(path, value)


def append_jsonl(path: Path, value: dict) -> None:
    phase3.append_jsonl(path, value)


def load_jsonl(path: Path) -> list[dict]:
    return phase3.load_jsonl(path) if path.is_file() else []


def rss_bytes() -> int:
    import psutil
    return int(psutil.Process().memory_info().rss)


def threads() -> int:
    return max(2, (os.cpu_count() or 4) - 2)


def tier_cap() -> int:
    """Locked 8 GB formula: min(6.4 GB, memory still available after a 1 GB safety reserve)."""
    import psutil
    memory = psutil.virtual_memory()
    cap = min(NOMINAL_CAP, memory.available - phase2.GB)
    print(f"Host total {memory.total / phase2.GB:.2f} GB, available {memory.available / phase2.GB:.2f} GB, "
          f"8 GB-tier cap {cap / phase2.GB:.2f} GB", flush=True)
    if cap < int(5.2 * phase2.GB):
        raise RuntimeError(
            "The 7B Q4 model needs about 5.2 GB inside the cap. Close other heavy apps "
            "(ChatGPT, Spotify, browsers) so available memory is at least 7.4 GB, then rerun.")
    return cap


def policy_path(paths: phase2.Paths) -> Path:
    return paths.ssd / "datasets" / "policy" / "agere-policy-v1" / "sop.jsonl"


def ensure_policy(paths: phase2.Paths) -> Path:
    """Stage an original synthetic SOP. Official SBP text is not invented here."""
    path = policy_path(paths)
    if path.is_file() and path.stat().st_size > 0:
        return path
    rows = [
        {"id": "SOP-01", "jurisdiction": "PK", "topic": "missing_fields",
         "text": "If a source line says NOT_PROVIDED, or the requested field is absent, the draft value is MISSING and the span id is null. Do not invent an identity date, a tax number, a deposit, or a credit-bureau status."},
        {"id": "SOP-02", "jurisdiction": "PK", "topic": "name_mismatch",
         "text": "Compare the registry beneficial-owner name with the onboarding applicant name. If they differ, identity_name_mismatch is true. Do not replace either name with the other."},
        {"id": "SOP-03", "jurisdiction": "PK", "topic": "calculator",
         "text": "DSCR and the current ratio are copied from the calculator ids CALC#DSCR and CALC#CURRENT_RATIO. The draft must not recompute those ratios in prose."},
        {"id": "SOP-04", "jurisdiction": "PK", "topic": "human_review",
         "text": "The assistant prepares a draft for a human reviewer. It does not approve credit, assign a risk rating, or file a report."},
        {"id": "SOP-05", "jurisdiction": "PK", "topic": "screening",
         "text": "Copy screening_status from the screening line. A potential match stays a potential match. The assistant does not clear it."},
        {"id": "SOP-06", "jurisdiction": "PK", "topic": "citations",
         "text": "Every non-missing fact carries the span id of the source line that contains that value. A span that does not contain the value is unsupported."},
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def load_policy(paths: phase2.Paths) -> list[dict]:
    return load_jsonl(ensure_policy(paths))


def retrieve_policy(case: dict, chunks: list[dict]) -> dict:
    document = " ".join(line for doc in case["case_documents"] for line in doc["lines"]).lower()
    scored = []
    for chunk in chunks:
        words = [word for word in chunk["text"].lower().split() if len(word) > 4]
        score = len({word for word in words if word in document})
        scored.append((score, chunk))
    chosen = [chunk for score, chunk in sorted(scored, key=lambda item: (-item[0], item[1]["id"]))[:3]]
    return {"tool": "policy_retriever", "status": "ok", "corpus": "agere-policy-v1",
            "synthetic_only": True, "case_id": case["id"], "citations": chosen}


def hardened_tools(case: dict, chunks: list[dict]) -> dict:
    tools = phase3.common_tools(case)
    tools["policy_retriever"] = retrieve_policy(case, chunks)
    return tools


def extract_json(text: str) -> dict | None:
    direct = phase3.parse_json_object(text)
    if direct is not None:
        return direct
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        return phase3.parse_json_object(text[start:end + 1])
    return None


class Engine:
    """One CPU llama.cpp context per role, inside a single process RSS cap."""

    def __init__(self, paths: phase2.Paths, cap: int, context: int, seed: int, use_lora: bool = False):
        from llama_cpp import Llama
        self.Llama = Llama
        self.paths = paths
        self.cap = cap
        self.context = context
        self.seed = seed
        self.use_lora = use_lora
        self.models: dict = {}
        self.mode = "resident"
        self.peak = rss_bytes()

    def note(self) -> None:
        self.peak = max(self.peak, rss_bytes())

    def guard(self) -> None:
        current = rss_bytes()
        self.peak = max(self.peak, current)
        if current > self.cap:
            raise MemoryError(f"Process RSS {current / phase2.GB:.2f} GB exceeded the {self.cap / phase2.GB:.2f} GB cap")

    def close(self) -> None:
        for model in self.models.values():
            closer = getattr(model, "close", None)
            if closer:
                closer()
        self.models.clear()
        gc.collect()
        self.note()

    def _open(self, role: str, size: str, kind: str) -> None:
        path = self.paths.output(size, kind)
        lora = os.environ.get("AGERE_TIER8_LORA", "")
        kwargs = {}
        if role == "sas" and self.use_lora and lora:
            kwargs["lora_path"] = lora
            print(f"Applying LoRA {lora}", flush=True)
        print(f"Loading {role} from {path.name}", flush=True)
        stop = threading.Event()

        def watch() -> None:
            while not stop.wait(0.5):
                current = rss_bytes()
                self.peak = max(self.peak, current)
                if current > self.cap:
                    print(f"Stopping load: RSS {current / phase2.GB:.2f} GB exceeded {self.cap / phase2.GB:.2f} GB",
                          flush=True)
                    os._exit(2)

        watcher = threading.Thread(target=watch, daemon=True)
        watcher.start()
        try:
            self.models[role] = self.Llama(
                model_path=str(path), n_ctx=self.context, n_gpu_layers=0,
                n_threads=threads(), n_batch=256, seed=self.seed, verbose=False,
                use_mmap=True, logits_all=False, **kwargs,
            )
        finally:
            stop.set()
        self.guard()
        print(f"Loaded {role}; RSS {rss_bytes() / phase2.GB:.2f} GB", flush=True)

    def load(self, specs: list[tuple[str, str, str]], *, resident: bool) -> str:
        self.close()
        weight_bytes = sum(self.paths.output(size, kind).stat().st_size for _, size, kind in specs)
        if resident and weight_bytes > int(self.cap * 0.90):
            print(f"Combined weights {weight_bytes / phase2.GB:.2f} GB do not fit the "
                  f"{self.cap / phase2.GB:.2f} GB cap together. Using sequential load/unload.", flush=True)
            resident = False
        if resident:
            try:
                for role, size, kind in specs:
                    self._open(role, size, kind)
                self.mode = "resident"
                return self.mode
            except MemoryError:
                print("Resident load crossed the cap. Switching this arm to sequential load/unload.", flush=True)
                self.close()
                self.peak = rss_bytes()
        self.mode = "sequential"
        self._specs = {role: (size, kind) for role, size, kind in specs}
        return self.mode

    def complete(self, role: str, prompt: str, limit: int) -> tuple[str, int, float]:
        if self.mode == "sequential":
            if role not in self.models:
                self.close()
                size, kind = self._specs[role]
                self._open(role, size, kind)
        elif role not in self.models:
            raise RuntimeError(f"{role} is not loaded")
        started = time.monotonic()
        out = self.models[role].create_completion(
            prompt, max_tokens=limit, temperature=0.0, top_k=1, top_p=1.0,
            repeat_penalty=1.0, seed=self.seed, stop=["<|im_end|>"], echo=False,
        )
        self.guard()
        text = str(out["choices"][0]["text"])
        tokens = int(out["usage"]["completion_tokens"])
        return text, tokens, time.monotonic() - started


def arm_dir(root: Path, split: str, name: str) -> Path:
    path = root / split / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def done_ids(path: Path) -> set[str]:
    return {row.get("case_id") for row in load_jsonl(path)}


def summarize(records: list[dict], expected: int) -> dict:
    valid = [row for row in records if row["score"]["valid_json"]]
    scorable = [row for row in valid if row["score"]["structured_claims_complete"]]
    mismatch = [row for row in records if row["score"]["mismatch_eligible"]]
    grounding_total = sum(row["score"]["grounding_total"] for row in records)
    refusal_total = sum(row["score"]["refusal_total"] for row in records)
    failures = Counter(row["score"].get("failure_tag") for row in records if row["score"].get("failure_tag"))
    def ratio(num: float, den: float):
        return (num / den) if den else None
    return {
        "status": "complete" if len(records) == expected else "partial",
        "cases_completed": len(records), "cases_expected": expected,
        "valid_json_rate": ratio(sum(row["score"]["valid_json"] for row in records), len(records)),
        "structured_invention_rate_among_complete_claim_sets": ratio(
            sum(bool(row["score"]["structured_invention"]) for row in scorable), len(scorable)),
        "complete_structured_claim_sets": len(scorable),
        "mismatch_recall": ratio(sum(bool(row["score"]["mismatch_detected"]) for row in mismatch), len(mismatch)),
        "mismatch_positive_cases": len(mismatch),
        "grounding_accuracy": ratio(sum(row["score"]["grounded"] for row in records), grounding_total),
        "refusal_correctness": ratio(sum(row["score"]["refusal_correct"] for row in records), refusal_total),
        "generated_tokens": sum(row["generated_tokens"] for row in records),
        "generation_seconds": round(sum(row["elapsed_seconds"] for row in records), 1),
        "peak_rss_bytes": max((row.get("peak_rss_bytes") or 0) for row in records) if records else 0,
        "failure_tags": dict(sorted(failures.items())),
    }


def finish_arm(directory: Path, records_path: Path, expected: int, meta: dict) -> dict:
    summary = summarize(load_jsonl(records_path), expected)
    summary.update(meta)
    summary["memory_within_cap"] = summary["peak_rss_bytes"] <= meta["cap_bytes"]
    if summary["status"] == "complete" and not summary["memory_within_cap"]:
        summary["status"] = "invalid_memory"
    write_json(directory / "summary.json", summary)
    print(json.dumps({key: summary[key] for key in (
        "status", "valid_json_rate", "structured_invention_rate_among_complete_claim_sets",
        "mismatch_recall", "grounding_accuracy", "refusal_correctness", "failure_tags")},
        indent=2), flush=True)
    return summary


def system_prompt() -> str:
    return ("You are a careful local finance drafting assistant. Use only the case packet, "
            "deterministic tool results, and exact citations. Return one JSON object. "
            "Never approve or clear a case; a human reviews all outputs.")


def run_naive_case(case: dict, arm: str, tools: dict, engine: Engine) -> dict:
    stages = []
    if arm == "sas":
        prompt = phase3.chat_prompt(phase3.prompt_text(case, tools), system_prompt())
        text, tokens, elapsed = engine.complete("sas", prompt, MAX_TOKENS)
        stages.append({"stage": "sas", "response": text, "generated_tokens": tokens, "elapsed_seconds": elapsed})
        answer = phase3.parse_json_object(text)
    else:
        document = "\n".join(line for doc in case["case_documents"] for line in doc["lines"])
        extract_prompt = phase3.chat_prompt(
            f"Extract source facts for {case['id']} from these lines. Return JSON with a facts map "
            f"using exact values and span IDs; do not draft or decide.\n{document}", system_prompt())
        extraction_text, extract_tokens, extract_elapsed = engine.complete(
            "extractor", extract_prompt, BUDGETS["extractor"])
        proposal = phase3.parse_json_object(extraction_text)
        stages.append({"stage": "extractor", "response": extraction_text,
                       "generated_tokens": extract_tokens, "elapsed_seconds": extract_elapsed})
        draft_prompt = phase3.chat_prompt(
            phase3.prompt_text(case, tools, extractor_proposal=proposal), system_prompt())
        draft_text, draft_tokens, draft_elapsed = engine.complete(
            "orchestrator_drafter", draft_prompt, BUDGETS["drafter"])
        answer = phase3.parse_json_object(draft_text)
        stages.append({"stage": "orchestrator_drafter", "response": draft_text,
                       "generated_tokens": draft_tokens, "elapsed_seconds": draft_elapsed})
        verify_prompt = phase3.chat_prompt(
            "Inspect this draft for unsupported claims. Return JSON with verdict PASS or FAIL "
            "and an unsupported_fields array. Do not rewrite the draft.\n"
            f"Draft:\n{draft_text}", system_prompt())
        verify_text, verify_tokens, verify_elapsed = engine.complete(
            "verifier", verify_prompt, BUDGETS["verifier"])
        stages.append({"stage": "verifier", "response": verify_text,
                       "generated_tokens": verify_tokens, "elapsed_seconds": verify_elapsed,
                       "gates_delivery": False})
    total = sum(stage["generated_tokens"] for stage in stages)
    if total > MAX_TOKENS:
        answer = None
    return {"case_id": case["id"], "corpus": case["corpus"], "kind": case["_kind"], "arm": arm,
            "answer": answer, "score": phase3.score_case(case, answer, tools, arm),
            "stages": stages, "generated_tokens": total,
            "elapsed_seconds": sum(stage["elapsed_seconds"] for stage in stages),
            "peak_rss_bytes": engine.peak, "residency": engine.mode,
            "completed_at_utc": phase3.now()}


def hardened_instructions() -> str:
    return ("\n\nWork in this order. Copy facts only from the tool packet. "
            "Use MISSING and a null span when the source says NOT_PROVIDED or the field is absent. "
            "Copy dscr and current_ratio from CALC#DSCR and CALC#CURRENT_RATIO. "
            "Set identity_name_mismatch true only when registry_name and declared_name differ; "
            "otherwise false for KYC and null for credit. "
            "Write a short draft for a human reviewer. Do not approve the case.")


def run_hardened_case(case: dict, arm: str, tools: dict, engine: Engine, lora: bool) -> dict:
    stages = []
    if arm == "sas":
        prompt = phase3.chat_prompt(phase3.prompt_text(case, tools) + hardened_instructions(), system_prompt())
        text, tokens, elapsed = engine.complete("sas", prompt, MAX_TOKENS)
        stages.append({"stage": "sas", "response": text, "generated_tokens": tokens,
                       "elapsed_seconds": elapsed, "lora": lora})
        answer = extract_json(text)
    else:
        document = "\n".join(line for doc in case["case_documents"] for line in doc["lines"])
        extract_prompt = phase3.chat_prompt(
            "Return one JSON object {\"facts\": {field: {\"value\": string, \"span_id\": string|null}}}. "
            "Use only the lines below. Unknown fields are MISSING with a null span. No prose.\n" + document,
            system_prompt())
        extraction_text, extract_tokens, extract_elapsed = engine.complete(
            "extractor", extract_prompt, BUDGETS["extractor"])
        proposal = extract_json(extraction_text) or {"facts": {}, "parse_error": True}
        stages.append({"stage": "extractor", "response": extraction_text, "generated_tokens": extract_tokens,
                       "elapsed_seconds": extract_elapsed})
        draft_prompt = phase3.chat_prompt(
            phase3.prompt_text(case, tools, extractor_proposal=proposal) + hardened_instructions()
            + "\nThe extractor proposal can be wrong. Check it against the tool packet before drafting.",
            system_prompt())
        draft_text, draft_tokens, draft_elapsed = engine.complete(
            "orchestrator_drafter", draft_prompt, BUDGETS["drafter"])
        answer = extract_json(draft_text)
        stages.append({"stage": "orchestrator_drafter", "response": draft_text,
                       "generated_tokens": draft_tokens, "elapsed_seconds": draft_elapsed})
        spent = extract_tokens + draft_tokens
        verdict = phase3.score_case(case, answer, tools, "mas")
        repaired = False
        if verdict.get("failure_tag") and REPAIR_TOKENS > 0 and spent + BUDGETS["verifier"] < MAX_TOKENS:
            repair_prompt = phase3.chat_prompt(
                "The draft failed a deterministic citation check. Return one corrected JSON object "
                "with the same schema. Change only unsupported fields. "
                f"Failure tag: {verdict['failure_tag']}. Checker:\n"
                + json.dumps(verdict["citation_verifier"], ensure_ascii=False)
                + "\n\nOriginal request:\n" + phase3.prompt_text(case, tools) + hardened_instructions(),
                system_prompt())
            repair_text, repair_tokens, repair_elapsed = engine.complete(
                "orchestrator_drafter", repair_prompt, min(REPAIR_TOKENS, MAX_TOKENS - spent - BUDGETS["verifier"]))
            repaired_answer = extract_json(repair_text)
            stages.append({"stage": "repair", "response": repair_text, "generated_tokens": repair_tokens,
                           "elapsed_seconds": repair_elapsed})
            if repaired_answer is not None:
                answer = repaired_answer
                repaired = True
            spent += repair_tokens
        verify_limit = min(BUDGETS["verifier"], max(0, MAX_TOKENS - spent))
        if verify_limit > 0:
            verify_prompt = phase3.chat_prompt(
                "Return JSON {\"verdict\": \"PASS\"|\"FAIL\", \"unsupported_fields\": []}. "
                "PASS only if every amount and name matches a source span or calculator id. Do not rewrite.\n"
                f"Draft:\n{json.dumps(answer, ensure_ascii=False) if answer else draft_text}",
                system_prompt())
            verify_text, verify_tokens, verify_elapsed = engine.complete("verifier", verify_prompt, verify_limit)
            stages.append({"stage": "verifier", "response": verify_text, "generated_tokens": verify_tokens,
                           "elapsed_seconds": verify_elapsed, "gates_delivery": True, "repair_used": repaired})
    total = sum(stage["generated_tokens"] for stage in stages)
    if total > MAX_TOKENS:
        answer = None
    return {"case_id": case["id"], "corpus": case["corpus"], "kind": case["_kind"], "arm": arm,
            "answer": answer, "score": phase3.score_case(case, answer, tools, arm),
            "stages": stages, "generated_tokens": total,
            "elapsed_seconds": sum(stage["elapsed_seconds"] for stage in stages),
            "peak_rss_bytes": engine.peak, "residency": engine.mode,
            "completed_at_utc": phase3.now()}


def iter_cases(paths: phase2.Paths, split: str, limit: int) -> list[dict]:
    if split == "dev":
        cases, _ = phase3.dev_inputs(paths)
        return cases[:limit] if limit else cases
    if split != "test":
        raise RuntimeError(f"Unknown split {split}")
    rows = []
    root = paths.ssd / "datasets" / "agere_synthetic" / phase3.DATA_VERSION / "test"
    for kind, count in (("kyc", 100), ("credit", 75)):
        path = root / f"{kind}.jsonl"
        loaded = phase3.load_jsonl(path)
        if len(loaded) != count:
            raise RuntimeError(f"Expected {count} {kind} test rows; found {len(loaded)}")
        for row in loaded:
            if row.get("split") != "test":
                raise RuntimeError(f"Non-test row in frozen split: {row.get('id')}")
            row["_kind"] = kind
            rows.append(row)
    return rows[:limit] if limit else rows


SAS_SPEC = [("sas", "7b", "q4_k_m")]
MAS_SPEC = [("orchestrator_drafter", "1.5b", "f16"), ("extractor", "0.5b", "f16"), ("verifier", "0.5b", "f16")]


def run_split(paths: phase2.Paths, root: Path, split: str, name: str, arm: str,
              mode: str, cap: int, context: int, seed: int, limit: int, lora: bool) -> dict:
    cases = iter_cases(paths, split, limit)
    directory = arm_dir(root, split, name)
    output = directory / "cases.jsonl"
    expected_ids = [case["id"] for case in cases]
    completed = done_ids(output)
    remaining = [case for case in cases if case["id"] not in completed]
    chunks = load_policy(paths) if mode == "hardened" else []
    meta = {"arm": arm, "mode": mode, "lora": lora, "split": split, "seed": seed,
            "context": context, "cap_bytes": cap, "residency": None}
    if not remaining:
        print(f"{split} {name}: already complete ({len(completed)})", flush=True)
        prior = load_jsonl(output)
        if prior:
            meta["residency"] = prior[-1].get("residency")
        return finish_arm(directory, output, len(expected_ids), meta)
    engine = Engine(paths, cap, context, seed, use_lora=lora)
    try:
        specs = SAS_SPEC if arm == "sas" else MAS_SPEC
        meta["residency"] = engine.load(specs, resident=True)
        for index, case in enumerate(remaining, 1):
            tools = hardened_tools(case, chunks) if mode == "hardened" else phase3.common_tools(case)
            try:
                if mode == "naive":
                    record = run_naive_case(case, arm, tools, engine)
                else:
                    record = run_hardened_case(case, arm, tools, engine, lora)
            except MemoryError:
                raise
            except Exception as exc:
                record = {"case_id": case["id"], "corpus": case["corpus"], "kind": case["_kind"],
                          "arm": arm, "answer": None, "error": str(exc),
                          "score": phase3.score_case(case, None, tools, arm),
                          "stages": [], "generated_tokens": 0, "elapsed_seconds": 0,
                          "peak_rss_bytes": engine.peak, "residency": engine.mode,
                          "completed_at_utc": phase3.now()}
            record["peak_rss_bytes"] = engine.peak
            append_jsonl(output, record)
            append_jsonl(directory / "stages.jsonl", {"case_id": case["id"], "stages": record["stages"]})
            print(f"{split} {name} {len(completed) + index}/{len(cases)} {case['id']} "
                  f"tokens={record['generated_tokens']} tag={record['score'].get('failure_tag')} "
                  f"RSS={engine.peak / phase2.GB:.2f} GB", flush=True)
    finally:
        engine.close()
    return finish_arm(directory, output, len(expected_ids), meta)


def better(candidate: dict, baseline: dict) -> bool:
    """Keep a change when invention falls or mismatch recall rises, and the other does not collapse."""
    def metric(row: dict, key: str):
        value = row.get(key)
        return None if value is None else float(value)
    inv_c, inv_b = metric(candidate, "structured_invention_rate_among_complete_claim_sets"), metric(baseline, "structured_invention_rate_among_complete_claim_sets")
    mis_c, mis_b = metric(candidate, "mismatch_recall"), metric(baseline, "mismatch_recall")
    json_c = metric(candidate, "valid_json_rate") or 0
    if json_c < 0.5:
        return False
    invention_better = inv_c is not None and (inv_b is None or inv_c < inv_b - 1e-9)
    mismatch_better = mis_c is not None and (mis_b is None or mis_c > mis_b + 1e-9)
    invention_collapse = inv_c is not None and inv_b is not None and inv_c > inv_b + 0.15
    mismatch_collapse = mis_c is not None and mis_b is not None and mis_c + 0.15 < mis_b
    if invention_collapse or mismatch_collapse:
        return False
    return invention_better or mismatch_better


def diagnose(root: Path) -> dict:
    report = {"generated_at_utc": phase3.now(), "arms": {}}
    inherent = {
        "M2": "Naive extractor output is not checked, so a soft or empty fact can be copied into the draft.",
        "M3": "Naive verifier is recorded and does not reject the draft, so one bad amount continues.",
        "M6": "No debate is used. The naive team still spends three generations without a repair budget.",
        "M7": "The naive verifier is another prose model, not a span match.",
        "M8": "Verifier tokens are not reserved ahead of the draft in the naive runner.",
        "M13": "Nothing stops a verifier that marks a bad draft as fine.",
    }
    for arm in ("sas", "mas"):
        path = root / "dev" / f"naive_{arm}" / "summary.json"
        summary = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"status": "missing"}
        tags = summary.get("failure_tags", {})
        report["arms"][arm] = {"summary": summary, "observed_tags": tags,
                               "inherent_design_gaps": inherent if arm == "mas" else {}}
    report["fixes_in_hardened_mas"] = [
        "JSON object recovery and a schema-only extractor prompt (M2).",
        "Deterministic citation check before delivery, with one repair and no debate (M3, M6, M7).",
        "Verifier token share reserved after the draft and the repair (M8).",
        "Model verifier cannot replace the span check (M13).",
        "Shared staged instructions for missing values, calculator ids, and name mismatch (S2, S4, S7).",
        "Same synthetic policy snippets on both hardened arms.",
    ]
    write_json(root / "diagnosis.json", report)
    print(f"Diagnosis: {root / 'diagnosis.json'}", flush=True)
    return report


def freeze(root: Path) -> dict:
    naive_sas = json.loads((root / "dev" / "naive_sas" / "summary.json").read_text(encoding="utf-8"))
    naive_mas = json.loads((root / "dev" / "naive_mas" / "summary.json").read_text(encoding="utf-8"))
    hardened_mas = json.loads((root / "dev" / "hardened_mas" / "summary.json").read_text(encoding="utf-8"))
    sas_base = json.loads((root / "dev" / "hardened_sas_base" / "summary.json").read_text(encoding="utf-8"))
    lora_path = root / "dev" / "hardened_sas_lora" / "summary.json"
    sas_lora = json.loads(lora_path.read_text(encoding="utf-8")) if lora_path.is_file() else None
    sas_choice = "hardened_sas_base"
    sas_reason = "Staged prompt is the hardened SAS. No adapter beat it on dev."
    if sas_lora and sas_lora.get("status") == "complete" and better(sas_lora, sas_base):
        sas_choice = "hardened_sas_lora"
        sas_reason = "QLoRA adapter improved dev invention or mismatch recall without collapsing the other."
    elif sas_lora and sas_lora.get("status") == "complete":
        sas_reason = "QLoRA adapter did not improve dev invention or mismatch recall without a collapse. Base Q4 stays."
    mas_choice = "naive_mas"
    mas_reason = "Hardened team did not improve the dev floor. The naive team remains the frozen MAS."
    if hardened_mas.get("status") == "complete" and better(hardened_mas, naive_mas):
        mas_choice = "hardened_mas"
        mas_reason = "Hardened team improved dev invention or mismatch recall without collapsing the other."
    decision = {"frozen_at_utc": phase3.now(), "sas": sas_choice, "mas": mas_choice,
                "sas_reason": sas_reason, "mas_reason": mas_reason,
                "naive_floor": {"sas": naive_sas, "mas": naive_mas}}
    write_json(root / "frozen_systems.json", decision)
    print(json.dumps({"sas": sas_choice, "mas": mas_choice, "sas_reason": sas_reason, "mas_reason": mas_reason}, indent=2), flush=True)
    return decision


def write_report(root: Path) -> Path:
    lines = ["# 8 GB tier result", "", f"Study `{STUDY}`. Host job cap is the 8 GB tier budget, 6.4 GB nominal.", ""]
    decision_path = root / "frozen_systems.json"
    if decision_path.is_file():
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        lines += [f"Frozen SAS: `{decision['sas']}`. {decision['sas_reason']}",
                  f"Frozen MAS: `{decision['mas']}`. {decision['mas_reason']}", ""]
    lines.append("## Dev")
    for name in ("naive_sas", "naive_mas", "hardened_sas_base", "hardened_sas_lora", "hardened_mas"):
        path = root / "dev" / name / "summary.json"
        if not path.is_file():
            continue
        row = json.loads(path.read_text(encoding="utf-8"))
        lines.append(
            f"- {name}: status {row.get('status')}, valid JSON {row.get('valid_json_rate')}, "
            f"invention {row.get('structured_invention_rate_among_complete_claim_sets')}, "
            f"mismatch recall {row.get('mismatch_recall')}, grounding {row.get('grounding_accuracy')}, "
            f"refusal {row.get('refusal_correctness')}, tags {row.get('failure_tags')}")
    final_sas = root / "test" / "final_sas" / "summary.json"
    final_mas = root / "test" / "final_mas" / "summary.json"
    if final_sas.is_file() and final_mas.is_file():
        sas = json.loads(final_sas.read_text(encoding="utf-8"))
        mas = json.loads(final_mas.read_text(encoding="utf-8"))
        lines += ["", "## Held-out test, pooled KYC 100 and credit 75",
                  f"- SAS invention {sas.get('structured_invention_rate_among_complete_claim_sets')}, "
                  f"mismatch recall {sas.get('mismatch_recall')}, grounding {sas.get('grounding_accuracy')}",
                  f"- MAS invention {mas.get('structured_invention_rate_among_complete_claim_sets')}, "
                  f"mismatch recall {mas.get('mismatch_recall')}, grounding {mas.get('grounding_accuracy')}",
                  "", "Invention is lower-better. Mismatch recall is higher-better. "
                  "Greedy decoding, temperature 0, seed 42. Extra seeds would repeat the same outputs."]
    frames = root / "test" / "frames_summary.json"
    if frames.is_file():
        row = json.loads(frames.read_text(encoding="utf-8"))
        lines += ["", "## FRAMES control", f"- {json.dumps(row)}"]
    path = root / "results.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(path, flush=True)
    return path


def verify(paths: phase2.Paths, cap: int) -> dict:
    cases, datasets = phase3.dev_inputs(paths)
    policy = ensure_policy(paths)
    models = []
    for size, kind in (("7b", "q4_k_m"), ("1.5b", "f16"), ("0.5b", "f16")):
        model = paths.output(size, kind)
        if not model.is_file():
            raise RuntimeError(f"Missing 8 GB weight: {model}")
        models.append({"file": model.name, "bytes": model.stat().st_size})
    manifest = {"study": STUDY, "created_at_utc": phase3.now(), "ssd": str(paths.ssd),
                "tier_gb": 8, "nominal_cap_bytes": NOMINAL_CAP, "effective_cap_bytes": cap,
                "context": CONTEXT, "seed": SEED, "temperature": 0.0,
                "dev_cases": len(cases), "datasets": datasets, "models": models,
                "policy": str(policy), "test_files_opened": False,
                "host_note": "Job is capped at the 8 GB tier even if the host has more RAM."}
    write_json(study_dir(paths) / "manifest.json", manifest)
    print(f"Verified {len(cases)} dev cases and 8 GB weights. Policy: {policy}", flush=True)
    return manifest


def frames_control(paths: phase2.Paths, root: Path, cap: int, context: int) -> dict:
    path = paths.ssd / "datasets" / "external" / "FRAMES" / "58d9fb6330f3ab1316d1eca12e5e8ef23dcc22ef" / "frames_100.jsonl"
    rows = phase3.load_jsonl(path)
    engine = Engine(paths, cap, context, SEED)
    scores = {}
    try:
        for arm, specs, role in (("sas", SAS_SPEC, "sas"), ("mas", [("orchestrator_drafter", "1.5b", "f16")], "orchestrator_drafter")):
            engine.load(specs, resident=True)
            correct = 0
            out = arm_dir(root, "test", f"frames_{arm}") / "cases.jsonl"
            seen = done_ids(out)
            for row in rows:
                if row["id"] in seen:
                    continue
                prompt = phase3.chat_prompt(
                    "Answer the question with the shortest factual phrase only. No citation and no explanation.\n"
                    + row["question"], system_prompt())
                text, tokens, elapsed = engine.complete(role, prompt, 64)
                match = text.strip().lower() == row["answer"].strip().lower()
                correct += int(match)
                append_jsonl(out, {"case_id": row["id"], "prediction": text.strip(), "match": match,
                                   "generated_tokens": tokens, "elapsed_seconds": elapsed})
            done = load_jsonl(out)
            scores[arm] = {"n": len(done), "exact_match": sum(bool(item["match"]) for item in done) / len(done)}
            engine.close()
    finally:
        engine.close()
    scores["note"] = "Closed-book control. A team win here does not override the KYC and credit invention result."
    write_json(root / "test" / "frames_summary.json", scores)
    return scores


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("step", choices=("verify", "naive", "diagnose", "train", "hardened", "freeze", "final", "report", "all"))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--context", type=int, default=CONTEXT)
    args = parser.parse_args()
    os.environ.setdefault("AGERE_SSD_ROOT", r"H:\AGERE")
    paths = phase2.validate_paths()
    cap = tier_cap()
    root = study_dir(paths)
    print(f"8 GB study cap {cap / phase2.GB:.2f} GB; context {args.context}; SSD {paths.ssd}", flush=True)
    if args.step in ("verify", "all"):
        verify(paths, cap)
    if args.step in ("naive", "all"):
        run_split(paths, root, "dev", "naive_sas", "sas", "naive", cap, args.context, SEED, args.limit, False)
        run_split(paths, root, "dev", "naive_mas", "mas", "naive", cap, args.context, SEED, args.limit, False)
    if args.step in ("diagnose", "all"):
        diagnose(root)
    if args.step in ("train", "all"):
        script = Path(__file__).resolve().parent / "tier8_finetune.py"
        print(f"Fine-tune: {script}", flush=True)
        subprocess.run([sys.executable, str(script)], cwd=str(phase2.REPO), check=False)
    if args.step in ("hardened", "all"):
        run_split(paths, root, "dev", "hardened_sas_base", "sas", "hardened", cap, args.context, SEED, args.limit, False)
        lora_file = paths.ssd / "weights" / "adapters" / "tier8-7b-qlora" / "adapter.gguf"
        if lora_file.is_file():
            os.environ["AGERE_TIER8_LORA"] = str(lora_file)
            run_split(paths, root, "dev", "hardened_sas_lora", "sas", "hardened", cap, args.context, SEED, args.limit, True)
        run_split(paths, root, "dev", "hardened_mas", "mas", "hardened", cap, args.context, SEED, args.limit, False)
    if args.step in ("freeze", "all"):
        freeze(root)
    if args.step in ("final", "all"):
        if not (root / "frozen_systems.json").is_file():
            raise RuntimeError("Refusing to open the test split before freeze.")
        decision = json.loads((root / "frozen_systems.json").read_text(encoding="utf-8"))
        for label, choice in (("final_sas", decision["sas"]), ("final_mas", decision["mas"])):
            arm = "sas" if "sas" in choice else "mas"
            mode = "naive" if choice.startswith("naive") else "hardened"
            run_split(paths, root, "test", label, arm, mode, cap, args.context, SEED, args.limit, "lora" in choice)
        frames_control(paths, root, cap, args.context)
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        manifest["test_files_opened"] = True
        write_json(root / "manifest.json", manifest)
    if args.step in ("report", "all"):
        write_report(root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, MemoryError, OSError, KeyError, ValueError) as exc:
        print(f"tier8 study failed: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1)
