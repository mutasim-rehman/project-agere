"""Audit what the final program actually uses after evidence expansion."""
import argparse
from collections import Counter
import json
from pathlib import Path

from program_graph import prune_unused
from tier8_windows_pilot import jsonl


def audit(cases, summary):
    annotations = {row["case_id"]: row for row in summary["cases"]}
    if {row["case_id"] for row in cases} != set(annotations):
        raise ValueError("Case IDs differ between drafts and scores")
    counts, records = Counter(), []
    for row in cases:
        base, wide = row["drafts"]
        baseline, wider = base["evidence"], wide["evidence"]
        added = wider.keys() - baseline.keys()
        if any(wider.get(key) != text for key, text in baseline.items()):
            raise ValueError("Expanded packet changed original source evidence")
        candidate = wide["candidate"]
        live = (prune_unused(candidate["program"])["steps"]
                if not candidate["execution"]["issues"] else [])
        consumed = {operand["span_id"] for step in live for operand in (step["left"], step["right"])}
        used_new = added & consumed
        case = annotations[row["case_id"]]
        first, second = case["official"]
        transition = "gain" if second and not first else "loss" if first and not second else "tie"
        counts[transition] += 1
        counts[f"{transition}_uses_added_span"] += bool(used_new)
        counts[f"{transition}_newly_complete"] += case["per_arm_complete_evidence"] == [False, True]
        records.append(dict(case_id=row["case_id"], transition=transition,
                            added_spans=sorted(added), live_new_spans=sorted(used_new)))
    return dict(counts=counts, cases=records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    result = audit(jsonl(args.cases), json.loads(args.summary.read_bytes()))
    print(json.dumps(result, indent=2))
