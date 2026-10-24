"""Memory-monitored fixed-output repair experiment; never a fresh generation run.

Parent exports model-only snapshots. Worker never reads baseline scores, and gold
evaluation starts only after its repair calls finish. Baseline output tokens are
debited from the same 2048-case ledger; latency scopes remain separate.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import psutil

from tier8_v2_run import ROOT, Models, append, inside, verified_models
from tier8_v2_influence_repair import repair_snapshot
from tier8_v2_financial_pipeline import evaluate_financial


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_rows(rows):
    output, seen = [], set()
    for row in rows:
        if row["case_id"] in seen:
            raise ValueError("Duplicate baseline IDs")
        seen.add(row["case_id"])
        if row["tokens"] != sum(s["generated_tokens"] for s in row["stages"]):
            raise ValueError("Baseline token debit differs from stage trace")
        output.append({"case_id": row["case_id"], "snapshot": {
            "plan": row["plan"], "answer": row["answer"], "verdict": row["final_verdict"], "tokens": row["tokens"]},
            "baseline_recorded_inference_seconds": sum(s["seconds"] for s in row["stages"])})
    return output


def function_ast(source, name, cls=None):
    nodes = ast.parse(source).body
    if cls:
        nodes = next(n for n in nodes if isinstance(n, ast.ClassDef) and n.name == cls).body
    return ast.dump(next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == name), include_attributes=False)


def model_constructor_ast(source):
    cls = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == "Models")
    call = next(n for n in ast.walk(cls) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "Llama")
    return ast.dump(call, include_attributes=False)


def complete_rows(path):
    if not path.exists():
        return []
    text = path.read_text()
    return [json.loads(line) for line in text[:text.rfind("\n") + 1].splitlines() if line]


def validate_base(base):
    summary = json.loads((base / "summary.json").read_text())
    manifest = json.loads((base / "manifest.json").read_text())
    cfg = manifest["config"]
    if summary["status"] != "complete" or summary["exit_code"] != 0 or summary["peak_tree_rss_bytes"] > summary["cap_bytes"]:
        raise ValueError("Baseline must be complete and memory-valid")
    if (cfg["task"] != "finqa" or cfg["program_mode"] != "reference" or cfg["repair"] != "none"
            or cfg["unit_mode"] != "question" or cfg["selector"] != "none"):
        raise ValueError("Replay accepts no-repair FinQA source-reference baselines with question units and no selector")
    data = inside(cfg["data"])
    if sha(data) != manifest["data_sha256"]:
        raise ValueError("Baseline public packets changed")
    if sha(inside("research/tier8_v2/external/finqa/dataset-dev.json")) != manifest["evaluation_source_sha256"]:
        raise ValueError("Baseline evaluation source changed")
    for name in ("evidence_atoms.py", "evidence_calculator.py", "evidence_contract.py"):
        if sha(ROOT / "scripts" / name) != manifest["code_sha256"][name]:
            raise ValueError(f"Baseline helper changed: {name}")
    # Whole pipeline files may add unrelated modes; compare actual runtime and
    # scoring helpers, rather than silently treating changed behavior as replay.
    for filename, names, cls in (("tier8_v2_run.py", ("prompt", "call", "count_prompt_tokens"), "Models"),
                                  ("tier8_v2_financial_pipeline.py", ("checked", "verdict", "evaluate_financial", "reported_reference"), None)):
        old = subprocess.check_output(["git", "show", f"{manifest['git_head']}:scripts/{filename}"], cwd=ROOT, text=True)
        current = (ROOT / "scripts" / filename).read_text()
        if any(function_ast(old, name, cls) != function_ast(current, name, cls) for name in names):
            raise ValueError(f"Replay runtime/scoring behavior changed: {filename}")
        if cls and model_constructor_ast(old) != model_constructor_ast(current):
            raise ValueError("Replay model constructor options changed")
    rows = [json.loads(line) for line in (base / "cases.jsonl").read_text().splitlines()]
    if len(rows) != summary["n"] or summary["n"] != summary["expected"]:
        raise ValueError("Baseline case count differs from summary")
    sanitized = snapshot_rows(rows)
    return manifest, summary, sanitized


def worker(out):
    manifest = json.loads((out / "manifest.json").read_text())
    cfg = manifest["baseline_config"]
    public = {p["id"]: p for p in map(json.loads, inside(cfg["data"]).read_text().splitlines())}
    inputs = [json.loads(line) for line in (out / "snapshots.jsonl").read_text().splitlines()]
    models = Models(cfg["arm"], cfg["context"], cfg["residency"], cfg["verifier_model"], False,
                    cfg.get("drafter_model", "1.5b-f16"))
    for item in inputs:
        result = repair_snapshot(public[item["case_id"]], item["snapshot"], models, cfg["arm"], manifest["feedback"],
                                 event_sink=lambda event: append(out / "stages.jsonl", event))
        result["baseline_recorded_inference_seconds"] = item["baseline_recorded_inference_seconds"]
        append(out / "cases.jsonl", result)
    # Gold is consumed after every model call has completed. It never enters the
    # repair API, trigger, prompts, or exported snapshots.
    gold = {r["id"]: r for r in json.loads(inside("research/tier8_v2/external/finqa/dataset-dev.json").read_text())}
    for row in map(json.loads, (out / "cases.jsonl").read_text().splitlines()):
        append(out / "scored_cases.jsonl", {"case_id": row["case_id"],
            "initial_score": evaluate_financial(gold[row["case_id"]], row["initial_answer"], row["initial_execution"]),
            "score": evaluate_financial(gold[row["case_id"]], row["answer"], row["execution"]),
            "delivered": row["delivered"], "eligible": row["eligible"], "repair_accepted": row["repair_accepted"],
            "fresh_tokens": row["fresh_tokens"], "combined_output_tokens": row["combined_output_tokens"]})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--feedback", choices=("plain", "proof"), required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    out = inside(args.out)
    if args.worker:
        worker(out)
        return
    base = inside(args.base)
    bm, bs, inputs = validate_base(base)
    if args.check:
        print(json.dumps({"status": "compatible", "n": len(inputs), "execution_mode": "fixed_output_repair_component"}))
        return
    for proc in psutil.process_iter(["cmdline"]):
        if proc.pid != os.getpid() and any(Path(arg).name in ("tier8_v2_run.py", "tier8_v2_replay.py") for arg in (proc.info["cmdline"] or [])):
            raise ValueError("Another inference run is active; do not launch replay concurrently")
    if out.exists():
        raise ValueError("Replay output already exists")
    out.mkdir(parents=True)
    cfg = bm["config"]
    selected = verified_models(cfg["arm"], cfg["verifier_model"], False, cfg.get("drafter_model", "1.5b-f16"))
    if {(m["file"], m["sha256"]) for m in selected} != {(m["file"], m["sha256"]) for m in bm["models"]}:
        raise ValueError("Replay checkpoints differ from baseline")
    import llama_cpp
    if llama_cpp.__version__ != bm["runtime"]:
        raise ValueError("Inference runtime differs from baseline")
    for item in inputs:
        append(out / "snapshots.jsonl", item)
    source_paths = [Path(__file__), ROOT / "scripts/tier8_v2_influence_repair.py", ROOT / "scripts/program_influence.py",
                    ROOT / "scripts/tier8_v2_run.py", ROOT / "scripts/tier8_v2_financial_pipeline.py",
                    ROOT / "scripts/evidence_atoms.py", ROOT / "scripts/evidence_calculator.py", ROOT / "scripts/evidence_contract.py"]
    manifest = {"execution_mode": "fixed_output_repair_component", "feedback": args.feedback,
        "baseline": str(base.relative_to(ROOT)), "baseline_config": cfg, "baseline_summary": bs,
        "baseline_cases_sha256": sha(base / "cases.jsonl"), "baseline_manifest_sha256": sha(base / "manifest.json"),
        "snapshots_sha256": sha(out / "snapshots.jsonl"), "data_sha256": bm["data_sha256"],
        "evaluation_source_sha256": bm["evaluation_source_sha256"], "models": selected,
        "code_sha256": {p.name: sha(p) for p in source_paths},
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "cap_bytes": min(6_400_000_000, psutil.virtual_memory().available - 1_000_000_000),
        "cost_scope": "Baseline recorded tokens debited; fresh repair tokens/latency measured separately. No fresh baseline generation."}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    start, peak, breached = time.monotonic(), 0, False
    with (out / "worker.log").open("w") as log, (out / "memory.jsonl").open("w") as memory:
        proc = subprocess.Popen([sys.executable, str(Path(__file__)), *sys.argv[1:], "--worker"], cwd=ROOT, stdout=log, stderr=log)
        process = psutil.Process(proc.pid)
        while proc.poll() is None:
            try:
                rss = psutil.Process().memory_info().rss + sum(p.memory_info().rss for p in [process, *process.children(recursive=True)] if p.is_running())
            except psutil.Error:
                continue
            peak = max(peak, rss)
            memory.write(json.dumps({"time": time.time(), "tree_rss_bytes": rss}) + "\n")
            memory.flush()
            if rss > manifest["cap_bytes"]:
                breached = True
                for child in process.children(recursive=True):
                    child.kill()
                proc.kill()
                break
            time.sleep(0.1)
        code = proc.wait()
    rows = complete_rows(out / "scored_cases.jsonl")
    raw = complete_rows(out / "cases.jsonl")
    summary = {"status": "invalid_memory" if breached else "complete" if code == 0 and len(rows) == len(inputs) else "failed_or_partial",
        "execution_mode": "fixed_output_repair_component", "exit_code": code, "n": len(rows), "expected": len(inputs),
        "peak_tree_rss_bytes": peak, "cap_bytes": manifest["cap_bytes"], "fresh_wall_seconds": time.monotonic() - start,
        "eligible_cases": sum(r["eligible"] for r in rows), "correct": sum(r["score"]["case_success"] for r in rows),
        "initial_correct": sum(r["initial_score"]["case_success"] for r in rows),
        "delivered_correct": sum(r["delivered"] and r["score"]["case_success"] for r in rows),
        "delivered_incorrect": sum(r["delivered"] and not r["score"]["case_success"] for r in rows),
        "withheld": sum(not r["delivered"] for r in rows), "fresh_tokens": sum(r["fresh_tokens"] for r in rows),
        "combined_output_tokens": sum(r["combined_output_tokens"] for r in rows),
        "max_case_combined_output_tokens": max((r["combined_output_tokens"] for r in rows), default=0),
        "baseline_recorded_inference_seconds": sum(r["baseline_recorded_inference_seconds"] for r in raw),
        "fresh_inference_seconds": sum(s["seconds"] for r in raw for s in r["fresh_stages"]),
        "gains": sum(not r["initial_score"]["case_success"] and r["score"]["case_success"] for r in rows),
        "regressions": sum(r["initial_score"]["case_success"] and not r["score"]["case_success"] for r in rows)}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
