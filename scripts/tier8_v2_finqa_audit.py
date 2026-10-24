"""Pre-inference audit of reported-answer and executable-answer conventions.

Retain every selected case. This audit does not select questions or enter prompts.
"""
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

from tier8_v2_financial_pipeline import reported_reference

ROOT = Path(__file__).resolve().parents[1]


def main():
    root = ROOT / "research/tier8_v2"
    rows = json.loads((root / "external/finqa/dataset-dev.json").read_text())[:24]
    audit = []
    for row in rows:
        qa = row["qa"]
        ref = reported_reference(qa["answer"])
        convention = "unsupported_reference"
        try:
            value = Decimal(str(qa["exe_ans"]))
            if ref and value.is_finite():
                raw = abs(value - ref["value"]) <= max(ref["tolerance"], Decimal("0.00001"))
                points = ref["percent"] and abs(value / 100 - ref["value"]) <= max(ref["tolerance"], Decimal("0.00001"))
                convention = "fraction" if raw and ref["percent"] else "number" if raw else "percentage_points" if points else "reported_execution_disagreement"
        except InvalidOperation:
            pass
        audit.append({"id": row["id"], "question": qa["question"], "reported_answer": qa["answer"],
                      "exe_ans": qa["exe_ans"], "program": qa["program"], "convention": convention})
    result = {"n": len(audit), "scope": "fixed first 24 development cases, audited before model inference",
              "cases_removed": 0, "audit": audit,
              "decision": "Report declared-unit reported-answer correctness and raw executable correctness separately; neither is official program equivalence."}
    (root / "evidence/finqa-reference-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"n": len(audit), "counts": {k: sum(r["convention"] == k for r in audit) for k in sorted({r["convention"] for r in audit})}}, indent=2))


if __name__ == "__main__":
    main()
