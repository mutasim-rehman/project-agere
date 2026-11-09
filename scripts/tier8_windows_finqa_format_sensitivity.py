"""Audit the effect of a declared percentage unit on official FinQA execution."""
import argparse
from collections import Counter
import json
from pathlib import Path

from tier8_v2_financial_pipeline import reported_reference
from tier8_windows_challenge import official_evaluator
from tier8_windows_error_ceiling import official_match
from tier8_windows_pilot import jsonl


def converted(program):
    if program["answer_unit"] != "percent":
        return program
    steps = program["steps"]
    last = f"#{len(steps) - 1}"
    return {**program, "steps": [*steps, {
        "op": "divide", "left": {"value": last, "span_id": "STEP" + last},
        "right": {"value": "100", "span_id": "CONST"},
    }]}


def audit(rows, primary, gold, evaluate):
    cases = {row["case_id"]: row for row in rows}
    ids = {row["case_id"] for row in primary}
    if len(cases) != len(rows) or len(ids) != len(primary) or cases.keys() != ids:
        raise ValueError("Saved score and draft case IDs differ")
    stats, details = {}, []
    for row in primary:
        case = row["case_id"]
        annotation = gold[case]
        label = reported_reference(annotation["qa"]["answer"])
        kind = "unsupported" if label is None else "percent" if label["percent"] else "number"
        group = stats.setdefault(kind, Counter())
        draft = cases[case]["arms"]["program"]
        program = draft["program"]
        valid = not draft["execution"]["issues"]
        original = valid and official_match(evaluate, annotation, program)
        if original != row["program_official"]:
            raise ValueError(f"Original score did not reproduce on {case}")
        unit_converted = valid and official_match(evaluate, annotation, converted(program))
        direct_reported, program_reported = row["reported"]
        group.update(dict(
            cases=1, direct_reported=direct_reported, program_reported=program_reported,
            direct_only=direct_reported and not program_reported,
            program_only=program_reported and not direct_reported,
            official_original=original, unit_converted_official=unit_converted,
            reported_and_converted_official=program_reported and unit_converted,
        ))
        details.append(dict(case_id=case, group=kind, official_original=original,
                            unit_converted_official=unit_converted, reported=row["reported"]))
    return dict(groups=stats, cases=details)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "evaluator", "ledger", "summary"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    primary = json.loads(args.summary.read_bytes())["cases"]
    gold = {row["id"]: row for row in json.loads(args.source.read_bytes())}
    evaluate = official_evaluator(args.evaluator)
    print(json.dumps(audit(jsonl(args.ledger), primary, gold, evaluate), indent=2))


if __name__ == "__main__":
    main()
