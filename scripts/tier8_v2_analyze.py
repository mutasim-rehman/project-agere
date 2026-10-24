"""Paired analysis of complete, memory-valid pilots on identical case IDs."""
import argparse
import json
import math
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]


def diagnostics(rows):
    def verifier_passed(row):
        verdict = row.get("initial_verdict")
        return isinstance(verdict, dict) and verdict.get("verdict") == "PASS" and verdict.get("unsupported_fields") == []
    result = {"n": len(rows), "field_repair_gains": 0, "field_repair_regressions": 0,
              "wrong_fields_left_locked": 0, "initial_verifier_true_accepts": 0,
              "initial_verifier_false_accepts": 0, "initial_verifier_true_rejects": 0,
              "initial_verifier_false_rejects": 0,
              "delivered_correct": sum(r["delivered"] and r["score"]["case_success"] for r in rows),
              "delivered_incorrect": sum(r["delivered"] and not r["score"]["case_success"] for r in rows),
              "withheld": sum(not r["delivered"] for r in rows),
              "generated_tokens": sum(r["tokens"] for r in rows),
              "prompt_tokens": sum(s.get("prompt_tokens", 0) for r in rows for s in r["stages"]),
              "inference_seconds": sum(s.get("seconds", 0) for r in rows for s in r["stages"]),
              "truncated_stages": sum(s.get("finish_reason") == "length" for r in rows for s in r["stages"])}
    for row in rows:
        correct = row["initial_score"]["case_success"]
        key = "initial_verifier_" + ("true_accepts" if correct else "false_accepts") if verifier_passed(row) else "initial_verifier_" + ("false_rejects" if correct else "true_rejects")
        result[key] += 1
        for field, before in row["initial_score"]["field_correct"].items():
            after = row["score"]["field_correct"][field]
            result["field_repair_gains"] += int(not before and after)
            result["field_repair_regressions"] += int(before and not after)
            result["wrong_fields_left_locked"] += int(row["repair"] == "patch" and row["repair_attempted"] and not before and not after and field not in row.get("repair_scope", []))
    return result


def paired(left, right):
    if set(left) != set(right) or not left:
        raise ValueError("Paired comparisons require identical nonempty case sets")
    ids = sorted(left)
    differences = [int(right[i]["score"]["case_success"]) - int(left[i]["score"]["case_success"]) for i in ids]
    wins = sum(d == 1 for d in differences)
    losses = sum(d == -1 for d in differences)
    discordant = wins + losses
    exact_p = min(1, 2 * sum(math.comb(discordant, k) for k in range(min(wins, losses) + 1)) / 2**discordant) if discordant else 1.0
    rng = random.Random(42)
    boot = sorted(sum(rng.choices(differences, k=len(ids))) / len(ids) for _ in range(10000))
    return {"n": len(ids), "right_minus_left_success": sum(differences) / len(ids),
            "paired_bootstrap_95_interval": [boot[249], boot[9749]], "right_only_correct": wins,
            "left_only_correct": losses, "exact_mcnemar_p": exact_p,
            "note": "Exploratory development comparison; no multiple-comparison adjustment or publication claim."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("left")
    parser.add_argument("right")
    args = parser.parse_args()
    records, manifests = [], []
    for name in (args.left, args.right):
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Paths must remain in project")
        summary = json.loads((path / "summary.json").read_text())
        if summary["status"] != "complete" or summary["peak_tree_rss_bytes"] > summary["cap_bytes"]:
            raise ValueError("Cannot compare incomplete or memory-invalid runs")
        manifests.append(json.loads((path / "manifest.json").read_text()))
        rows = [json.loads(line) for line in (path / "cases.jsonl").read_text().splitlines()]
        by_id = {r["case_id"]: r for r in rows}
        if len(by_id) != len(rows):
            raise ValueError("Duplicate case IDs")
        records.append(by_id)
    if manifests[0]["data_sha256"] != manifests[1]["data_sha256"]:
        raise ValueError("Dataset hashes differ")
    print(json.dumps({"paired": paired(*records), "left": diagnostics(list(records[0].values())),
                      "right": diagnostics(list(records[1].values()))}, indent=2))


if __name__ == "__main__":
    main()
