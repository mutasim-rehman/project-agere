"""Versioned, offline unit-contract audit; never rewrites recorded experiments.

V2 treats `number` as a canonical amount/count/ratio, as the reference prompt
already permits. Only `percent` scales a prediction by 100. Bare numeric gold
with percentage-point semantics remains an explicit unresolved annotation issue.
"""
import argparse
import hashlib
import json
from pathlib import Path

from tier8_v2_financial_pipeline import checked, evaluate_financial, question_units
from tier8_v2_sequence import inside, require_complete

VERSION = "reported-units-v2-number-ratio"


def evaluate_v2(row, answer, execution):
    # Equivalent canonical ratio labels; no value-dependent rescaling or best-of.
    canonical = dict(answer) if isinstance(answer, dict) else answer
    if isinstance(canonical, dict) and canonical.get("answer_unit") == "number":
        canonical["answer_unit"] = "fraction"
    result = evaluate_financial(row, canonical, execution)
    return {**result, "metric_version": VERSION,
            "metric": "reported-answer rounding; number/fraction canonical, percent /100; raw exe_ans separately"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path, key):
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    result = {r[key]: r for r in rows}
    if not rows or len(result) != len(rows):
        raise ValueError("Require unique nonempty IDs")
    return result


def audit_run(run):
    run = inside(run)
    summary = require_complete(str(run))
    manifest_path = run / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    replay = manifest.get("execution_mode") == "fixed_output_repair_component"
    config = manifest["baseline_config"] if replay else manifest["config"]
    if config.get("task") != "finqa":
        raise ValueError("Unit audit supports FinQA only")
    source = inside("research/tier8_v2/external/finqa/dataset-dev.json")
    packets_path = inside(config["data"])
    if sha(source) != manifest["evaluation_source_sha256"] or sha(packets_path) != manifest["data_sha256"]:
        raise ValueError("Evaluation source or public packet hash differs")
    gold = {r["id"]: r for r in json.loads(source.read_text())}
    public = read_rows(packets_path, "id")
    records = read_rows(run / "cases.jsonl", "case_id")
    scores_path = run / "scored_cases.jsonl" if replay else run / "cases.jsonl"
    scores = read_rows(scores_path, "case_id")
    if set(scores) != set(records) or len(records) != summary["expected"]:
        raise ValueError("Incomplete/different score cohort")
    cases = []
    for case_id, r in records.items():
        if public[case_id]["question"] != gold[case_id]["qa"]["question"]:
            raise ValueError("Public question differs from evaluation source")
        for prefix in ("initial_", ""):
            answer, execution = r[prefix + "answer"], r[prefix + "execution"]
            if checked(answer, public[case_id]["evidence"]) != execution:
                raise ValueError("Execution differs from source recomputation")
            if evaluate_financial(gold[case_id], answer, execution) != scores[case_id][prefix + "score"]:
                raise ValueError("Recorded legacy metric cannot be reproduced")
        old = scores[case_id]["score"]
        new = evaluate_v2(gold[case_id], r["answer"], r["execution"])
        cases.append({"case_id": case_id, "legacy_correct": old["case_success"],
                      "v2_correct": new["case_success"], "delivered": r["delivered"],
                      "initial_v2_correct": evaluate_v2(gold[case_id], r["initial_answer"], r["initial_execution"])["case_success"],
                      "unit": r["answer"].get("answer_unit") if isinstance(r["answer"], dict) else None})
    return {"run": str(run.relative_to(inside("."))), "n": len(cases),
            "legacy_correct": sum(c["legacy_correct"] for c in cases),
            "v2_correct": sum(c["v2_correct"] for c in cases),
            "v2_delivered_correct": sum(c["delivered"] and c["v2_correct"] for c in cases),
            "v2_wrong_deliveries": sum(c["delivered"] and not c["v2_correct"] for c in cases),
            "changed_cases": [c for c in cases if c["legacy_correct"] != c["v2_correct"]],
            "cases": cases,
            "artifact_sha256": {p.name: sha(p) for p in {manifest_path, run / "summary.json", run / "cases.jsonl", scores_path}}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+")
    args = parser.parse_args()
    source = inside("research/tier8_v2/external/finqa/dataset-dev.json")
    rows = json.loads(source.read_text())[:24]
    incompatible = [r["id"] for r in rows if "%" in str(r["qa"]["answer"])
                    and question_units(r["qa"]["question"], "question") == ("number",)]
    print(json.dumps({"metric_version": VERSION, "source_sha256": sha(source),
        "code_sha256": {name: sha(inside("scripts/" + name)) for name in
                        (Path(__file__).name, "tier8_v2_financial_pipeline.py", "evidence_calculator.py")},
        "question_grammar_vs_legacy_percent_label_conflicts": incompatible,
        "unresolved": [{"id": "AAPL/2004/page_36.pdf-2", "issue": "Bare .2 gold for gross-margin decline; percent-point versus canonical-fraction annotation needs adjudication. No special-case rescoring."}],
        "scope": "Offline sensitivity audit of fixed outputs, not new inference or a performance improvement; historical metrics unchanged.",
        "runs": [audit_run(run) for run in args.runs]}, indent=2))


if __name__ == "__main__":
    main()
