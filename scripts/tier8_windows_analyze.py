"""Summarize paired Windows pilot outcomes from the saved case ledger."""
import argparse
from collections import Counter
import json
from pathlib import Path

from evidence_atoms import atom_catalog, compile_plan
from tier8_v2_financial_pipeline import checked, evaluate_financial


def prefix_diagnostic(rows, packets, gold):
    """Count recoverable early correct results with a gold-aware oracle."""
    counts = Counter()
    for row in rows:
        plan = row["initial_plan"] or {}
        steps = plan.get("steps", [])
        if not row["forced"] or len(steps) < 2:
            continue
        counts["forced_multistep"] += 1
        if row["score"]["case_success"]:
            continue
        evidence = packets[row["case_id"]]["evidence"]
        atoms = atom_catalog(evidence)
        for length in range(1, len(steps)):
            answer = compile_plan({**plan, "steps": steps[:length]}, atoms)
            if evaluate_financial(gold[row["case_id"]], answer, checked(answer, evidence))["case_success"]:
                counts["wrong_final_with_correct_prefix"] += 1
                break
    return counts


def summarize(rows):
    cases = {}
    counts = {False: Counter(), True: Counter()}
    for row in rows:
        forced = row["forced"]
        pair = cases.setdefault(row["case_id"], {})
        if forced in pair:
            raise ValueError(f"Duplicate case-arm pair: {row['case_id']}")
        pair[forced] = row
    for pair in cases.values():
        if set(pair) != {False, True}:
            raise ValueError("Incomplete pair")
        for forced, row in pair.items():
            counter = counts[forced]
            plan = row["initial_plan"] or {}
            counter["refused"] += plan.get("decision") == "INSUFFICIENT"
            counter["attempted"] += plan.get("decision") == "ANSWER"
            counter["parse_failure"] += not plan
            counter["executable"] += row["initial_execution"]["value"] is not None
            counter["withheld"] += not row["delivered"]
            for metric in ("case_success", "raw_execution_match"):
                correct = row["score"][metric]
                counter[f"{metric}_candidate_correct"] += correct
                counter[f"{metric}_correct_withheld"] += correct and not row["delivered"]
                counter[f"{metric}_correct_delivered"] += correct and row["delivered"]
                counter[f"{metric}_wrong_delivered"] += not correct and row["delivered"]
            for stage in row["stages"]:
                counter["peak_sampled_rss"] = max(counter["peak_sampled_rss"], stage["peak_sampled_rss"])
    return {"pairs": len(cases), "baseline": counts[False], "forced": counts[True]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--gold", type=Path)
    parser.add_argument("--one-step-ledger", type=Path)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.ledger.read_text(encoding="utf-8").splitlines()]
    result = summarize(rows)
    if args.one_step_ledger:
        one_step = [json.loads(line) for line in
                    args.one_step_ledger.read_text(encoding="utf-8").splitlines()]
        if not one_step or not all(row.get("one_step") and row["forced"] for row in one_step):
            raise ValueError("Expected one-step forced rows")
        ids = {row["case_id"] for row in one_step}
        unrestricted = [{**row, "forced": False} for row in rows
                        if row["forced"] and row["case_id"] in ids]
        contrast = summarize(unrestricted + one_step)
        result["step_limit_contrast"] = {"pairs": contrast["pairs"],
            "unrestricted_forced": contrast["baseline"], "one_step_forced": contrast["forced"]}
    if args.gold:
        public_path = (Path(__file__).resolve().parents[1]
                       / "research/tier8_v2/data/finqa-development-public.jsonl")
        public_rows = [json.loads(line) for line in public_path.read_text(encoding="utf-8").splitlines()]
        gold_rows = json.loads(args.gold.read_text(encoding="utf-8"))
        result["oracle_prefix_diagnostic"] = prefix_diagnostic(
            rows, {row["id"]: row for row in public_rows}, {row["id"]: row for row in gold_rows})
    print(json.dumps(result, indent=2))
