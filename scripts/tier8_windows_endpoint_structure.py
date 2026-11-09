"""Compare unused operations and fixed endpoint selection on paired FinQA drafts."""
import argparse
from collections import Counter
import json
from pathlib import Path

from program_endpoints import endpoint_candidates
from program_graph import audit_graph
from tier8_v2_financial_pipeline import evaluate_financial
from tier8_windows_challenge import official_evaluator
from tier8_windows_error_ceiling import official_match
from tier8_windows_pilot import jsonl


def analyze(rows, packets, gold, evaluate):
    ids = [row["case_id"] for row in rows]
    if len(ids) != len(packets) or set(ids) != set(packets):
        raise ValueError("Expected one paired record per frozen report")
    arms = [Counter(), Counter()]
    paired = Counter()
    cases = []
    for row in rows:
        case = row["case_id"]
        records = []
        if len(row["drafts"]) != 2:
            raise ValueError(f"Expected two arms on {case}")
        for draft, stats in zip(row["drafts"], arms):
            program = draft["candidate"]["program"]
            evidence = draft.get("evidence") or packets[case]["evidence"]
            endpoints = endpoint_candidates(program, evidence)
            unused = audit_graph(program["steps"])["unused_steps"] if endpoints else []
            labels = {item["id"]: official_match(evaluate, gold[case], item["answer"])
                      for item in endpoints}
            reported = {item["id"]: evaluate_financial(
                gold[case], item["answer"], item["execution"])["case_success"] for item in endpoints}
            final = labels.get("KEEP", False)
            first = labels.get("P001", final)
            final_reported = reported.get("KEEP", False)
            first_reported = reported.get("P001", final_reported)
            correct_prefixes = [item["edit"]["after"] for item in endpoints
                                if item["edit"] and labels[item["id"]]]
            stats.update({
                "reports": 1,
                "executable": bool(endpoints),
                "with_unused": bool(unused),
                "unused_operations": len(unused),
                "final_correct": final,
                "first_correct": first,
                "first_gains": first and not final,
                "first_losses": final and not first,
                "final_reported": final_reported,
                "first_reported": first_reported,
                "first_reported_gains": first_reported and not final_reported,
                "first_reported_losses": final_reported and not first_reported,
                "oracle_correct": final or bool(correct_prefixes),
                "wrong_final_with_unused_correct_prefix": not final and bool(
                    set(correct_prefixes) & set(unused)),
                "wrong_final_with_used_correct_prefix": not final and bool(
                    set(correct_prefixes) - set(unused)),
            })
            records.append(dict(
                executable=bool(endpoints), unused_steps=unused,
                final_correct=final, first_correct=first, correct_prefixes=correct_prefixes,
                final_reported=final_reported, first_reported=first_reported,
            ))
        paired["both_executable"] += all(record["executable"] for record in records)
        left, right = (bool(record["unused_steps"]) for record in records)
        paired["both_with_unused"] += left and right
        paired["only_first_with_unused"] += left and not right
        paired["only_second_with_unused"] += right and not left
        cases.append(dict(case_id=case, arms=records))
    return dict(arms=arms, paired=paired, cases=cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "source", "evaluator"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("ledgers", type=Path, nargs="+")
    args = parser.parse_args()
    packets = {row["id"]: row for row in jsonl(args.cohort)}
    gold = {row["id"]: row for row in json.loads(args.source.read_bytes())}
    evaluate = official_evaluator(args.evaluator)
    print(json.dumps({path.name: analyze(jsonl(path), packets, gold, evaluate)
                      for path in args.ledgers}, indent=2))


if __name__ == "__main__":
    main()
