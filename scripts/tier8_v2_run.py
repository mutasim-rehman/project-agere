"""Audited CPU development pilot: strong SAS/MAS and controlled repair ablations.

Run through the parent monitor (default), never --worker directly for evidence.
All inputs/outputs resolve inside ROOT. No gold is passed to model stages.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from evidence_contract import TokenLedger, commit_patch, source_spans, validate
from tier8_v2_data import FIELDS, evaluate

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ROOT / "weights/tier8_v2"
MODEL_FILES = {"sas": {"sas": "qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf"},
               "mas": {"extractor": "qwen2.5-0.5b-instruct-native-f16.gguf",
                       "drafter": "qwen2.5-1.5b-instruct-native-f16.gguf",
                       "verifier": "qwen2.5-0.5b-instruct-native-f16.gguf"}}
SCHEMA = {"type": "object", "properties": {
    "case_id": {"type": "string"},
    "facts": {"type": "object", "properties": {f: {"type": "object", "properties": {
        "value": {"type": "string"}, "span_id": {"type": "string"}},
        "required": ["value", "span_id"], "additionalProperties": False} for f in FIELDS},
        "required": list(FIELDS), "additionalProperties": False},
    "identity_name_mismatch": {"type": "boolean"}},
    "required": ["case_id", "facts", "identity_name_mismatch"], "additionalProperties": False}
VERIFY_SCHEMA = {"type": "object", "properties": {"verdict": {"enum": ["PASS", "FAIL"]},
    "unsupported_fields": {"type": "array", "items": {"enum": list(FIELDS) + ["identity_name_mismatch", "case_id"]}}},
    "required": ["verdict", "unsupported_fields"], "additionalProperties": False}
FIELD_VERIFY_SCHEMA = {"type": "object", "properties": {"checks": {"type": "object",
    "properties": {field: {"enum": ["PASS", "FAIL", "UNKNOWN"]} for field in FIELDS},
    "required": list(FIELDS), "additionalProperties": False}},
    "required": ["checks"], "additionalProperties": False}


def answer_schema(public, citations="enum"):
    schema = deepcopy(SCHEMA)
    schema["properties"]["case_id"] = {"enum": [public["id"]]}
    if citations == "enum":
        ids = sorted(source_spans(public["case_documents"]))
        for field in FIELDS:
            schema["properties"]["facts"]["properties"][field]["properties"]["span_id"] = {"enum": ids}
    return schema


def normalize_verdict(raw, mode):
    if mode == "joint":
        return raw
    checks = raw.get("checks") if isinstance(raw, dict) else None
    if not isinstance(checks, dict) or set(checks) != set(FIELDS) or any(v not in ("PASS", "FAIL", "UNKNOWN") for v in checks.values()):
        return None
    failed = [f for f in FIELDS if checks[f] != "PASS"]
    return {"verdict": "FAIL" if failed else "PASS", "unsupported_fields": failed, "checks": checks}


def inside(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("All paths must stay inside the project")
    return path


def append(path, record):
    with path.open("a") as out:
        out.write(json.dumps(record, sort_keys=True) + "\n")
        out.flush()
        os.fsync(out.fileno())


class Models:
    def __init__(self, arm, context, residency="distinct"):
        from llama_cpp import Llama, LlamaGrammar
        self.grammar = LlamaGrammar
        self.models = {}
        self.context = context
        files = MODEL_FILES[arm]
        opened = {}
        for role, filename in files.items():
            if residency == "shared" and filename in opened:
                self.models[role] = opened[filename]
                print(json.dumps({"role": role, "weights": filename, "shared_instance": True}), flush=True)
                continue
            self.models[role] = Llama(model_path=str(WEIGHTS / filename), n_ctx=context,
                n_gpu_layers=0, n_threads=8, n_threads_batch=8, n_batch=64,
                n_ubatch=64, seed=42, use_mmap=False, verbose=False)
            opened[filename] = self.models[role]
            print(json.dumps({"role": role, "weights": filename, "shared_instance": False}), flush=True)

    def call(self, role, content, schema, budget, requested, stage):
        model = self.models[role]
        # Roles never inherit conversational KV state, including when weights share.
        model.reset()
        prompt = ("<|im_start|>system\nYou reconcile financial evidence for human review. "
                  "Use authoritative sources only. Return JSON only.<|im_end|>\n"
                  f"<|im_start|>user\n{content}<|im_end|>\n<|im_start|>assistant\n")
        prompt_tokens = len(model.tokenize(prompt.encode(), add_bos=True))
        available = max(0, self.context - prompt_tokens - 8)
        limit = min(available, budget.allowance(requested))
        start = time.monotonic()
        if limit == 0:
            return None, {"stage": stage, "role": role, "prompt": content, "prompt_tokens": prompt_tokens,
                          "generated_tokens": 0, "finish_reason": "no_context_or_budget", "response": "", "seconds": 0}
        output = model.create_completion(prompt, max_tokens=limit, temperature=0,
            top_k=1, seed=42, repeat_penalty=1, stop=["<|im_end|>"],
            grammar=self.grammar.from_json_schema(json.dumps(schema), verbose=False))
        choice = output["choices"][0]
        used = output["usage"]["completion_tokens"]
        budget.charge(used)
        text = choice["text"]
        try:
            answer = json.loads(text)
        except json.JSONDecodeError:
            answer = None
        return answer, {"stage": stage, "role": role, "prompt": content, "prompt_tokens": prompt_tokens,
            "requested_tokens": requested, "effective_limit": limit, "generated_tokens": used,
            "finish_reason": choice["finish_reason"], "response": text, "seconds": time.monotonic() - start}


def run_case(public, models, arm, repair, *, verification="joint", handoff="proposal", citations="enum", event_sink=None):
    budget = TokenLedger()
    trace = []
    spans = source_spans(public["case_documents"])
    evidence = json.dumps(spans, sort_keys=True)
    task = public["task"] + "\nCase ID: " + public["id"]
    schema = answer_schema(public, citations)
    schema_text = json.dumps(schema)
    def call(role, text, schema, requested, stage):
        answer, event = models.call(role, text, schema, budget, requested, stage)
        trace.append(event)
        if event_sink:
            event_sink({"case_id": public["id"], **event})
        return answer
    proposal = None
    if arm == "mas":
        proposal = call("extractor", task + "\nSelect the requested values from these sources.\n" + evidence
                        + "\nRequired output schema:\n" + schema_text, schema, 384, "extract")
    draft_prompt = task + "\nEvidence:\n" + evidence + "\nRequired output schema:\n" + schema_text
    if proposal is not None and handoff == "proposal":
        draft_prompt += "\nUntrusted specialist proposal; recheck sources:\n" + json.dumps(proposal)
    drafter = "sas" if arm == "sas" else "drafter"
    answer = call(drafter, draft_prompt, schema, 640, "draft")
    # This comparison is deterministic and shared by every arm and ablation.
    answer = derive_mismatch(answer)
    initial = answer
    issues = validate(answer, case_id=public["id"], fields=FIELDS, spans=spans, calculations={})
    def verify(candidate, stage):
        instruction = ("Check source authority, date precedence, field identity, citations and the mismatch boolean. "
            "PASS only if all are correct. On FAIL identify every wrong field. Return verdict and unsupported_fields.") if verification == "joint" else (
            "Judge each fact independently against its authoritative source, including registry issue dates. "
            "A value quoted from the wrong source FAILS. MISSING must cite the explicit absence statement. "
            "Return checks with registered_owner, declared_applicant and identity_expiry_date, each PASS, FAIL or UNKNOWN. "
            "Use UNKNOWN when evidence is insufficient. Name mismatch is checked separately by code.")
        raw = call("sas" if arm == "sas" else "verifier", task + "\nEvidence:\n" + evidence
            + "\nAnswer:\n" + json.dumps(candidate) + "\n" + instruction,
            VERIFY_SCHEMA if verification == "joint" else FIELD_VERIFY_SCHEMA, budget.allowance(192), stage)
        return normalize_verdict(raw, verification)
    verdict = verify(answer, "verify")
    verifier_pass = passed(verdict)
    initial_verdict = verdict
    needs_repair = bool(issues) or not verifier_pass
    repair_accepted = False
    allowed = set()
    if repair != "none" and needs_repair:
        semantic_fields = verdict.get("unsupported_fields", []) if isinstance(verdict, dict) else list(FIELDS)
        allowed = {i.field for i in issues if i.field in FIELDS} | (set(semantic_fields) & set(FIELDS))
        # A failed/missing verifier verdict without localization cannot safely lock any claim.
        if not allowed and not verifier_pass:
            allowed = set(FIELDS)
        if repair == "patch" and isinstance(answer, dict) and isinstance(answer.get("facts"), dict):
            patch_schema = {"type": "object", "properties": {f: schema["properties"]["facts"]["properties"][f] for f in sorted(allowed)},
                            "required": sorted(allowed), "additionalProperties": False}
            patch = call(drafter, task + "\nEvidence:\n" + evidence + "\nCurrent answer:\n" + json.dumps(answer)
                + "\nRepair ONLY these facts; return a map of field to value/span_id: " + json.dumps(sorted(allowed))
                + "\nFeedback:\n" + json.dumps({"issues": [asdict(i) for i in issues], "verifier": verdict}),
                patch_schema, budget.allowance(768, reserve=192), "repair_patch")
            answer, repair_accepted = commit_patch(answer, patch, allowed=allowed, spans=spans, calculations={})
            # Derived mismatch is recomputed from the final named facts for both repair methods.
        else:
            candidate = call(drafter, draft_prompt + "\nCorrect this previous answer:\n" + json.dumps(answer)
                + "\nFeedback:\n" + json.dumps({"issues": [asdict(i) for i in issues], "verifier": verdict}),
                schema, budget.allowance(768, reserve=192), "repair_full")
            if candidate is not None:
                answer, repair_accepted = candidate, True
    answer = derive_mismatch(answer)
    final_issues = validate(answer, case_id=public["id"], fields=FIELDS, spans=spans, calculations={})
    # Reverify after changing facts. No repair is released solely because it parses.
    if repair_accepted:
        verdict = verify(answer, "verify_repair")
        verifier_pass = passed(verdict)
    delivered = not final_issues and verifier_pass
    return {"case_id": public["id"], "arm": arm, "repair": repair, "initial_answer": initial,
            "answer": answer, "delivered": delivered, "repair_attempted": needs_repair and repair != "none",
            "repair_accepted": repair_accepted, "tokens": budget.spent, "stages": trace,
            "initial_verdict": initial_verdict, "final_verdict": verdict,
            "specialist_agreement": {f: (proposal.get("facts", {}).get(f) == initial.get("facts", {}).get(f))
                                      for f in FIELDS} if isinstance(proposal, dict) and isinstance(initial, dict) else None,
            "repair_scope": sorted(allowed), "initial_support_issues": [asdict(i) for i in issues],
            "final_support_issues": [asdict(i) for i in final_issues]}


def derive_mismatch(answer):
    if isinstance(answer, dict) and isinstance(answer.get("facts"), dict):
        facts = answer["facts"]
        a, b = facts.get("registered_owner", {}).get("value"), facts.get("declared_applicant", {}).get("value")
        if a not in (None, "MISSING") and b not in (None, "MISSING"):
            return {**answer, "identity_name_mismatch": a != b}
    return answer


def passed(verdict):
    return isinstance(verdict, dict) and verdict.get("verdict") == "PASS" and verdict.get("unsupported_fields") == []


def verified_models(arm):
    manifest_path = ROOT / "research/tier8_v2/evidence/models.json"
    entries = json.loads(manifest_path.read_text())
    native = ROOT / "research/tier8_v2/evidence/native-models.json"
    if native.exists():
        entries += json.loads(native.read_text())
    required = set(MODEL_FILES[arm].values())
    if arm == "sas":
        required.add("qwen2.5-7b-instruct-q4_k_m-00002-of-00002.gguf")
    selected = []
    for name in sorted(required):
        matches = [e for e in entries if Path(e["file"]).name == name]
        if len(matches) != 1:
            raise ValueError(f"One verified weight manifest entry required: {name}")
        entry = matches[0]
        path = inside(entry["file"])
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                digest.update(block)
        if path.stat().st_size != entry["bytes"] or digest.hexdigest() != entry["sha256"]:
            raise ValueError(f"Weight integrity mismatch: {name}")
        selected.append(entry)
    return selected


def worker(args, out):
    models = Models(args.arm, args.context, args.residency)
    rows = [json.loads(line) for line in inside(args.data).read_text().splitlines() if line][:args.limit]
    if args.task == "finqa":
        from tier8_v2_financial_pipeline import run_financial, evaluate_financial
        gold_rows = json.loads(inside("research/tier8_v2/external/finqa/dataset-dev.json").read_text())
        gold = {r["id"]: r for r in gold_rows}
        if len(gold) != len(gold_rows):
            raise ValueError("Duplicate financial evaluation IDs")
    for case in rows:
        if case.get("split") not in ("development", "dev"):
            raise ValueError("This runner accepts development data only")
        public = {k: v for k, v in case.items() if k != "gold"}
        sink = lambda event: append(out / "stages.jsonl", event)
        if args.task == "finqa":
            if public["question"] != gold[case["id"]]["qa"]["question"]:
                raise ValueError("Public question differs from evaluation source")
            result = run_financial(public, models, args.arm, args.repair, event_sink=sink,
                                   representation=args.program_mode, unit_mode=args.unit_mode, selector=args.selector,
                                   causal_mode=args.causal_mode, catalog_style=args.catalog_style)
            result["initial_score"] = evaluate_financial(gold[case["id"]], result["initial_answer"], result["initial_execution"])
            result["score"] = evaluate_financial(gold[case["id"]], result["answer"], result["execution"])
            result["all_gold_evidence_retrieved"] = set(gold[case["id"]]["qa"]["gold_inds"]) <= set(public["evidence"])
        else:
            result = run_case(public, models, args.arm, args.repair, verification=args.verification,
                              handoff=args.handoff, citations=args.citations, event_sink=sink)
            result["initial_score"] = evaluate(case, result["initial_answer"])
            result["score"] = evaluate(case, result["answer"])
        result["residency"] = args.residency
        append(out / "cases.jsonl", result)
        print(json.dumps({"id": case["id"], "success": result["score"]["case_success"],
                          "delivered": result["delivered"], "tokens": result["tokens"]}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("sas", "mas"), required=True)
    parser.add_argument("--repair", choices=("none", "full", "patch"), required=True)
    parser.add_argument("--task", choices=("kyc", "finqa"), default="kyc")
    parser.add_argument("--data")
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--context", type=int)
    parser.add_argument("--verification", choices=("joint", "field"), default="field")
    parser.add_argument("--handoff", choices=("proposal", "independent"), default="independent")
    parser.add_argument("--citations", choices=("free", "enum"), default="enum")
    parser.add_argument("--residency", choices=("distinct", "shared"), default="shared")
    parser.add_argument("--program-mode", choices=("literal", "reference"), default="literal")
    parser.add_argument("--unit-mode", choices=("free", "question"), default="free")
    parser.add_argument("--selector", choices=("suggest", "none"), default="suggest")
    parser.add_argument("--causal-mode", choices=("check", "grammar"), default="check")
    parser.add_argument("--catalog-style", choices=("full", "compact"), default="full")
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    if args.data is None:
        args.data = "research/tier8_v2/data/finqa-development-public.jsonl" if args.task == "finqa" else "research/tier8_v2/data/development.jsonl"
    if args.context is None:
        args.context = 4096 if args.task == "finqa" else 2048
    if args.program_mode != "reference" and (args.causal_mode != "check" or args.catalog_style != "full"):
        raise ValueError("Causal grammar and compact catalogs require reference programs")
    if args.task == "finqa" and (args.handoff != "independent" or args.verification != "field" or args.citations != "enum"):
        raise ValueError("KYC-specific handoff/verification/citation overrides are not implemented for FinQA")
    if args.limit <= 0:
        raise ValueError("Positive case limit required")
    out = inside(args.out)
    if args.worker:
        worker(args, out)
        return
    import psutil
    if out.exists():
        raise ValueError("Use a new output directory; never mix runs")
    out.mkdir(parents=True)
    data = inside(args.data)
    sources = [Path(__file__), ROOT / "scripts/evidence_contract.py", ROOT / "scripts/tier8_v2_data.py",
               ROOT / "scripts/tier8_v2_financial_pipeline.py", ROOT / "scripts/evidence_calculator.py", ROOT / "scripts/tier8_v2_finqa.py"]
    sources.append(ROOT / "scripts/evidence_atoms.py")
    manifest = {"config": vars(args), "data_sha256": hashlib.sha256(data.read_bytes()).hexdigest(),
                "code_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "host_total_bytes": psutil.virtual_memory().total,
                "cap_bytes": min(6_400_000_000, psutil.virtual_memory().available - 1_000_000_000),
                "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "runtime": subprocess.check_output([sys.executable, "-c", "import llama_cpp;print(llama_cpp.__version__)"], text=True).strip()}
    manifest["models"] = verified_models(args.arm)
    if args.task == "finqa":
        manifest["evaluation_source_sha256"] = hashlib.sha256(inside("research/tier8_v2/external/finqa/dataset-dev.json").read_bytes()).hexdigest()
        manifest["task_policy"] = {"verification": "operand-operation-unit checks", "handoff": "fallible source-ID suggestion" if args.selector == "suggest" else "no selector; draft/verify pair",
                                   "selector": args.selector, "program_mode": args.program_mode, "unit_mode": args.unit_mode,
                                   "causal_mode": args.causal_mode, "catalog_style": args.catalog_style,
                                   "citations": "enumerated source and step IDs", "metric": "declared-unit reported answer with rounding; raw exe_ans separately"}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    peak = 0
    breached = False
    with (out / "worker.log").open("w") as log, (out / "memory.jsonl").open("w") as memory:
        process = subprocess.Popen([sys.executable, str(Path(__file__)), *sys.argv[1:], "--worker"], cwd=ROOT, stdout=log, stderr=log)
        parent = psutil.Process(process.pid)
        try:
            while process.poll() is None:
                try:
                    rss = psutil.Process().memory_info().rss + sum(p.memory_info().rss for p in [parent, *parent.children(recursive=True)] if p.is_running())
                except psutil.Error:
                    continue
                peak = max(peak, rss)
                memory.write(json.dumps({"time": time.time(), "tree_rss_bytes": rss}) + "\n")
                memory.flush()
                if rss > manifest["cap_bytes"]:
                    breached = True
                    for child in parent.children(recursive=True):
                        child.kill()
                    process.kill()
                    break
                time.sleep(0.1)
            code = process.wait()
        except BaseException:
            for child in parent.children(recursive=True):
                child.kill()
            process.kill()
            process.wait()
            raise
    rows = [json.loads(s) for s in (out / "cases.jsonl").read_text().splitlines()] if (out / "cases.jsonl").exists() else []
    summary = {"status": "invalid_memory" if breached else "complete" if code == 0 and len(rows) == args.limit else "failed_or_partial",
               "exit_code": code, "n": len(rows), "expected": args.limit, "peak_tree_rss_bytes": peak,
               "cap_bytes": manifest["cap_bytes"], "case_successes": sum(r["score"]["case_success"] for r in rows),
               "delivered_correct": sum(r["delivered"] and r["score"]["case_success"] for r in rows),
               "delivered_incorrect": sum(r["delivered"] and not r["score"]["case_success"] for r in rows),
               "repair_regressions": sum(r["initial_score"]["case_success"] and not r["score"]["case_success"] for r in rows),
               "repair_gains": sum(not r["initial_score"]["case_success"] and r["score"]["case_success"] for r in rows),
               "initial_case_successes": sum(r["initial_score"]["case_success"] for r in rows),
               "withheld": sum(not r["delivered"] for r in rows),
               "total_generated_tokens": sum(r["tokens"] for r in rows)}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
