"""Score a completed resident Windows run with official and reported FinQA metrics."""
import argparse
from collections import Counter
import json
from pathlib import Path
from statistics import median

from tier8_v2_financial_pipeline import evaluate_financial
from tier8_windows_challenge import official_evaluator, official_result
from tier8_windows_pilot import jsonl


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "evaluator", "ledger", "cohort", "resources"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    rows = jsonl(args.ledger)
    ids = {row["id"] for row in jsonl(args.cohort)}
    if len(rows) != len(ids) or {row["case_id"] for row in rows} != ids:
        raise ValueError("Resident run did not cover the frozen cohort")
    resource = json.loads(args.resources.read_bytes())
    if resource["status"] != "completed" or resource["sampled_rss_breached"]:
        raise ValueError("Resident resource guard did not complete")
    gold = {row["id"]: row for row in json.loads(args.source.read_bytes())}
    official = official_evaluator(args.evaluator)
    result = {"reports": len(rows), "official": Counter(), "reported": Counter(), "resources": resource}
    times = []
    for row in rows:
        label = gold[row["case_id"]]
        answer, execution = row["answer"], row["execution"]
        try:
            correct = not execution["issues"] and official_result(official, label, answer) == label["qa"]["exe_ans"]
        except ValueError:
            correct = False
        reported = evaluate_financial(label, answer, execution)["case_success"]
        for name, matches in (("official", correct), ("reported", reported)):
            counts = result[name]
            counts["correct_candidates"] += matches
            counts["executable_candidates"] += not execution["issues"]
            outcome = "withheld" if not row["delivered"] else "correct" if matches else "wrong"
            counts[outcome] += 1
        times.append(sum(stage["elapsed_seconds"] for stage in row["stages"]))
    result["median_seconds"] = median(times)
    result["generated_tokens"] = sum(row["tokens"] for row in rows)
    print(json.dumps(result, indent=2))
