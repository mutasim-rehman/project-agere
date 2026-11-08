"""Measure paired accuracy with and without incompatible numeric reference flags."""
import argparse
from math import comb
import json
from pathlib import Path


def contrast(rows, metric):
    arms = [row[metric] for row in rows]
    gained = sum(second and not first for first, second in arms)
    lost = sum(first and not second for first, second in arms)
    discordant = gained + lost
    return dict(n=len(rows), first_correct=sum(first for first, _ in arms),
                second_correct=sum(second for _, second in arms), gains=gained, losses=lost,
                exact_mcnemar_p=min(1, 2 * sum(comb(discordant, k)
                    for k in range(min(gained, lost) + 1)) / 2**discordant))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("summaries", nargs="+", type=Path)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_bytes())["agere-finqa-test.json"]
    flagged = {row["id"] for row in audit["exceptions"]}
    result = {}
    for path in args.summaries:
        rows = json.loads(path.read_bytes())["cases"]
        clean = [row for row in rows if row["case_id"] not in flagged]
        result[f"{path.parent.name}/{path.name}"] = {
            "flagged": len(rows) - len(clean),
            "all": {metric: contrast(rows, metric) for metric in ("official", "reported")},
            "excluding_flags": {metric: contrast(clean, metric) for metric in ("official", "reported")},
        }
    print(json.dumps(result, indent=2))
