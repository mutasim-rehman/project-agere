"""Offline functional-influence audit with model and training counterchecks."""
import argparse
import hashlib
import json
from pathlib import Path
import time

from evidence_atoms import atom_catalog
from program_influence import functional_influence
from tier8_v2_demo_retrieval import BANK

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="*", default=["finqa-mas-demos-dev24-01", "finqa-sas-demos-dev24-01",
                                                    "finqa-sas-analysis-dev24-01", "finqa-mas-3b-analysis-dev8-01"])
    args = parser.parse_args()
    base = ROOT / "research/tier8_v2"
    reports = []
    for name in args.runs:
        if Path(name).name != name:
            raise ValueError("Run names must be directory basenames")
        path = base / "runs" / name
        summary = json.loads((path / "summary.json").read_text())
        manifest = json.loads((path / "manifest.json").read_text())
        if summary["status"] != "complete" or summary["peak_tree_rss_bytes"] > summary["cap_bytes"]:
            raise ValueError("Audit only completed memory-valid runs")
        packet_path = (ROOT / manifest["config"]["data"]).resolve()
        if not packet_path.is_relative_to(ROOT) or hashlib.sha256(packet_path.read_bytes()).hexdigest() != manifest["data_sha256"]:
            raise ValueError("Saved packet source is unavailable or changed")
        if manifest["config"]["task"] != "finqa" or manifest["config"]["program_mode"] != "reference":
            raise ValueError("Functional influence requires financial reference programs")
        if manifest["code_sha256"]["evidence_atoms.py"] != hashlib.sha256((ROOT / "scripts/evidence_atoms.py").read_bytes()).hexdigest():
            raise ValueError("Quantity catalog code changed; use the historical catalog implementation")
        packets = {r["id"]: r for r in map(json.loads, packet_path.read_text().splitlines())}
        cases = []
        for row in map(json.loads, (path / "cases.jsonl").read_text().splitlines()):
            atoms = atom_catalog(packets[row["case_id"]]["evidence"])
            start = time.perf_counter()
            result = functional_influence(row["plan"], atoms) if not row["execution"]["issues"] else {"status": "not_executable"}
            elapsed = time.perf_counter() - start
            inactive = result.get("value_inactive_sources", [])
            cases.append({"case_id": row["case_id"], "influence": result,
                          "inactive_source_contexts": {key: atoms[key] for key in inactive},
                          "analysis_seconds": elapsed, "correct": row["score"]["case_success"],
                          "delivered": row["delivered"]})
        flagged = [row for row in cases if row["influence"].get("value_inactive_sources")]
        reports.append({"run": name, "n": len(cases), "analyzed": sum(r["influence"]["status"] == "analyzed" for r in cases),
                        "cases_with_cancelled_source_value_influence": len(flagged),
                        "flagged_correct_cases": sum(r["correct"] for r in flagged),
                        "flagged_wrong_deliveries": sum(r["delivered"] and not r["correct"] for r in flagged),
                        "max_analysis_seconds": max(r["analysis_seconds"] for r in cases),
                        "case_file_sha256": hashlib.sha256((path / "cases.jsonl").read_bytes()).hexdigest(), "cases": cases})
    bank_path = ROOT / BANK
    bank = json.loads(bank_path.read_text())
    controls = []
    for example in bank["examples"]:
        result = functional_influence({"steps": example["sketch"]["steps"]}, example["sketch"]["slots"])
        if result.get("value_inactive_sources") or result["status"] != "analyzed":
            controls.append({"source_id": example["source_id"], "question": example["question"],
                             "sketch": example["sketch"], "influence": result})
    output = {"scope": "Offline program-value influence. No semantic correctness certificate or achieved repair gain.",
              "cautions": ["Source IDs are independent symbolic variables; observed equal numbers do not merge.",
                           "Zero derivative is an exact rational identity, conditional on defined division, not a local numerical gradient.",
                           "Legitimate formulas and domain conditions can cancel source values; do not gate answers solely on this result.",
                           "Unknown/unsupported cases are not certified. This is standard bounded symbolic algebra, not established novelty."],
              "runs": reports, "training_bank_sha256": hashlib.sha256(bank_path.read_bytes()).hexdigest(),
              "training_examples": len(bank["examples"]), "training_cancelled_or_unknown_examples": controls}
    (base / "evidence/program-influence-audit.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"runs": [{k: v for k, v in r.items() if k != "cases"} for r in reports],
                      "training_cancelled_or_unknown_examples": len(controls)}, indent=2))


if __name__ == "__main__":
    main()
