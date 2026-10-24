"""Offline strict-shape diagnostic; never imported by deployment code.

Select training sketches from the public question FIRST. Only then inspect a
development annotation. Exact shape equality is sufficient to express that
annotated program with some bindings, not a complete algebraic coverage test.
Alternative valid formulas can have different shapes. No oracle choices/bindings
are exported to public packets or the model-facing bank.
"""
from decimal import InvalidOperation
import hashlib
import json
from pathlib import Path

from evidence_atoms import atom_catalog
from tier8_v2_demo_retrieval import BANK, DemoIndex
from tier8_v2_demos import target_plan
from tier8_v2_financial_pipeline import question_units
from tier8_v2_sketches import make_sketch

ROOT = Path(__file__).resolve().parents[1]


def shape(sketch):
    return {"answer_unit": sketch["answer_unit"], "steps": sketch["steps"]}


def main():
    bank_file = ROOT / BANK
    bank = json.loads(bank_file.read_text())
    index = DemoIndex(bank["examples"])
    gold = {r["id"]: r for r in json.loads((ROOT / "research/tier8_v2/external/finqa/dataset-dev.json").read_text())}
    public_path = ROOT / "research/tier8_v2/data/finqa-development-public.jsonl"
    records = []
    for public in map(json.loads, public_path.read_text().splitlines()):
        # The selection occurs without access to a target/answer/program.
        selected = index.select(public["question"], 2)
        units = question_units(public["question"], "question")
        eligible = [e for e in selected if e["sketch"]["answer_unit"] in units]
        row = {"case_id": public["id"], "selected_source_ids": [e["source_id"] for e in selected],
               "unit_compatible_ids": [e["source_id"] for e in eligible],
               "reference_shape_available": False, "selected_shape_matches": [],
               "whole_bank_shape_matches": None}
        try:
            target = target_plan(gold[public["id"]], public, atom_catalog(public["evidence"]))
        except (ValueError, InvalidOperation) as exc:
            row["reference_unavailable_reason"] = str(exc)
        else:
            signature = shape(make_sketch(target, atom_catalog(public["evidence"])))
            row["reference_shape_available"] = True
            row["selected_shape_matches"] = [e["source_id"] for e in eligible if shape(e["sketch"]) == signature]
            row["whole_bank_shape_matches"] = sum(shape(e["sketch"]) == signature for e in bank["examples"])
        records.append(row)
    output = {"n": len(records), "bank_sha256": hashlib.sha256(bank_file.read_bytes()).hexdigest(),
              "public_packets_sha256": hashlib.sha256(public_path.read_bytes()).hexdigest(),
              "reference_shapes_available": sum(r["reference_shape_available"] for r in records),
              "selected_shape_matched_cases": sum(bool(r["selected_shape_matches"]) for r in records),
              "whole_bank_shape_matched_cases": sum(bool(r["whole_bank_shape_matches"]) for r in records),
              "cautions": ["Offline development diagnostic only; oracle shape matches never enter deployment.",
                           "Strict full-program shape+unit equality; not complete coverage over equivalent formulas.",
                           "No exact tokenizer fit applied; model prompt may retain fewer sketches.",
                           "Unavailable references remain in the 24-case denominator, with reasons recorded.",
                           "Shape match does not establish correct variable binding or achieved model accuracy."],
              "cases": records}
    (ROOT / "research/tier8_v2/evidence/sketch-shape-audit.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k: v for k, v in output.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
