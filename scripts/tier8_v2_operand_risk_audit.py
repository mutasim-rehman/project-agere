"""Post-hoc year-range operand diagnostic, not a deployment rejection rule.

Numbers in 1900..2100 can also be legitimate amounts; this heuristic does NOT
label dates or establish per-step semantic correctness. Source contexts are kept
for manual review. No programs, packets, selections or evaluation labels change.
"""
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from evidence_atoms import atom_catalog
from tier8_v2_demo_retrieval import BANK

ROOT = Path(__file__).resolve().parents[1]


def main():
    base = ROOT / "research/tier8_v2"
    packets = base / "data/finqa-development-public.jsonl"
    public = {r["id"]: r for r in map(json.loads, packets.read_text().splitlines())}
    reports = []
    for name in ("finqa-mas-demos-dev24-01", "finqa-sas-demos-dev24-01"):
        path = base / "runs" / name
        summary = json.loads((path / "summary.json").read_text())
        manifest = json.loads((path / "manifest.json").read_text())
        if summary["status"] != "complete" or summary["peak_tree_rss_bytes"] > summary["cap_bytes"] or manifest["config"]["program_mode"] != "reference":
            raise ValueError("Require completed memory-valid source-reference runs")
        records = []
        for row in map(json.loads, (path / "cases.jsonl").read_text().splitlines()):
            atoms = atom_catalog(public[row["case_id"]]["evidence"])
            occurrences = []
            for i, step in enumerate(row["plan"].get("steps", [])):
                for side in ("left", "right"):
                    ref = step[side]
                    if ref not in atoms:
                        continue
                    value = Decimal(atoms[ref]["value"])
                    if value == value.to_integral_value() and 1900 <= value <= 2100:
                        occurrences.append({"step": i, "side": side, "quantity_id": ref, **atoms[ref]})
            records.append({"case_id": row["case_id"], "flagged": bool(occurrences), "occurrences": occurrences,
                            "correct": row["score"]["case_success"], "delivered": row["delivered"],
                            "verifier_pass": row["initial_verdict"].get("verdict") == "PASS" if row["initial_verdict"] else False})
        flagged = [r for r in records if r["flagged"]]
        reports.append({"run": name, "n": len(records), "flagged_cases": len(flagged),
                        "flagged_correct_cases": sum(r["correct"] for r in flagged),
                        "flagged_wrong_deliveries": sum(r["delivered"] and not r["correct"] for r in flagged),
                        "case_file_sha256": hashlib.sha256((path / "cases.jsonl").read_bytes()).hexdigest(),
                        "cases": records})
    bank_file = ROOT / BANK
    bank = json.loads(bank_file.read_text())
    counterexamples = []
    for example in bank["examples"]:
        slots = {name: slot for name, slot in example["sketch"]["slots"].items()
                 if Decimal(slot["training_value"]) == Decimal(slot["training_value"]).to_integral_value()
                 and 1900 <= Decimal(slot["training_value"]) <= 2100}
        if slots:
            counterexamples.append({"source_id": example["source_id"], "question": example["question"],
                                    "required_annotated_slots": slots})
    result = {"policy": "Post-hoc diagnostic: flag source-quantity integer values in inclusive range 1900..2100.",
              "cautions": ["This is not a date classifier or proof that the flagged operand is the primary error.",
                           "Legitimate financial amounts can lie in the same range; no hard rejection is justified.",
                           "Some contexts suggest escaped punctuation artifacts; origin requires independent source verification.",
                           "No achieved repair gain or fresh held-out detector performance is measured."],
              "packets_sha256": hashlib.sha256(packets.read_bytes()).hexdigest(),
              "training_bank_sha256": hashlib.sha256(bank_file.read_bytes()).hexdigest(),
              "training_examples_requiring_year_range_slots": len(counterexamples),
              "training_caution": "Annotated executable examples contradict blanket range removal; not an estimated detector false-positive rate on unseen data.",
              "training_counterexamples": counterexamples, "runs": reports}
    (base / "evidence/operand-risk-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps([{k: v for k, v in r.items() if k != "cases"} for r in reports], indent=2))


if __name__ == "__main__":
    main()
