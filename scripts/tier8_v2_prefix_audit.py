"""Offline audit of naturally occurring correct intermediates, not model gains.

Candidate construction uses saved programs/evidence only. Gold evaluates the
already constructed prefixes afterward, with the original declared unit fixed.
This tests a possible answer-endpoint repair, not a claim of novel program slicing.
"""
import hashlib
import argparse
import json
from pathlib import Path

from program_endpoints import endpoint_candidates
from tier8_v2_financial_pipeline import evaluate_financial

ROOT = Path(__file__).resolve().parents[1]


def prefixes(answer, evidence):
    return endpoint_candidates(answer, evidence)[1:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="*", default=["finqa-mas-demos-dev24-01", "finqa-sas-demos-dev24-01", "finqa-sas-analysis-dev24-01"])
    args = parser.parse_args()
    base = ROOT / "research/tier8_v2"
    public = {r["id"]: r for r in map(json.loads, (base / "data/finqa-development-public.jsonl").read_text().splitlines())}
    gold = {r["id"]: r for r in json.loads((base / "external/finqa/dataset-dev.json").read_text())}
    reports = []
    for name in args.runs:
        if Path(name).name != name:
            raise ValueError("Run names must be directory basenames")
        path = base / "runs" / name
        summary = json.loads((path / "summary.json").read_text())
        if summary["status"] != "complete" or summary["peak_tree_rss_bytes"] > summary["cap_bytes"]:
            raise ValueError("Only completed memory-valid runs may be audited")
        records = []
        for row in map(json.loads, (path / "cases.jsonl").read_text().splitlines()):
            candidates = prefixes(row["answer"], public[row["case_id"]]["evidence"])
            matches = [c["id"] for c in candidates if evaluate_financial(gold[row["case_id"]], c["answer"], c["execution"])["case_success"]]
            records.append({"case_id": row["case_id"], "original_correct": row["score"]["case_success"],
                            "original_unit": row["answer"].get("answer_unit"),
                            "candidate_values": {c["id"]: c["execution"]["value"] for c in candidates},
                            "oracle_correct_prefix_ids": matches,
                            "oracle_potential_gain": not row["score"]["case_success"] and bool(matches)})
        reports.append({"run": name, "case_file_sha256": hashlib.sha256((path / "cases.jsonl").read_bytes()).hexdigest(),
                        "n": len(records), "oracle_prefix_potential_gains": sum(r["oracle_potential_gain"] for r in records),
                        "cases": records})
    result = {"policy": "Select an earlier computed answer; original operations/operands/declared unit fixed; trailing steps removed.",
              "caution": "Offline oracle candidate coverage only. Not model-selected gains, semantic certification, or established novelty. KEEP must remain available in any deployment policy.",
              "runs": reports}
    (base / "evidence/program-prefix-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps([{k: v for k, v in r.items() if k != "cases"} for r in reports], indent=2))


if __name__ == "__main__":
    main()
