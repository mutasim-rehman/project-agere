"""Check FinQA reference execution and reported-answer compatibility."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import json
from pathlib import Path

from tier8_v2_financial_pipeline import reported_reference


def audit(path, evaluator):
    raw = path.read_bytes()
    counts, exceptions = Counter(), []
    for row in json.loads(raw):
        qa = row["qa"]
        counts["questions"] += 1
        invalid, replay = evaluator.eval_program(evaluator.program_tokenization(qa["program"]), row["table"])
        if invalid:
            counts["official_reference_invalid"] += 1
        elif replay != qa["exe_ans"]:
            counts["official_reference_execution_disagreement"] += 1
        reference = reported_reference(qa.get("answer"))
        if reference is None:
            counts["reported_reference_not_simple_numeric"] += 1
            continue
        try:
            value = Decimal(str(qa["exe_ans"]))
        except InvalidOperation:
            counts["official_answer_not_numeric"] += 1
            continue
        if not value.is_finite():
            counts["official_answer_not_numeric"] += 1
            continue
        counts["numeric_comparison_eligible"] += 1
        tolerance = max(reference["tolerance"], Decimal("0.00001"))
        matches_raw = abs(value - reference["value"]) <= tolerance
        matches_percent_points = (reference["percent"]
                                  and abs(value / 100 - reference["value"]) <= tolerance)
        if matches_raw:
            counts["matches_raw"] += 1
        elif matches_percent_points:
            counts["matches_only_if_raw_is_percent_points"] += 1
        else:
            counts["incompatible_simple_numeric_labels"] += 1
            alternatives = [value, value / 100] if reference["percent"] else [value]
            best = min(abs(option - reference["value"]) for option in alternatives)
            relative = best / max(abs(reference["value"]), Decimal("0.00001"))
            counts["incompatible_exceeds_1pct_relative"] += relative > Decimal("0.01")
            counts["incompatible_exceeds_10pct_relative"] += relative > Decimal("0.1")
            counts["incompatible_sign_reversed"] += (value * reference["value"] < 0)
            exceptions.append(dict(id=row["id"], raw=qa["exe_ans"], reported=qa["answer"],
                                   percent=reference["percent"], official_replay=replay, invalid=invalid,
                                   best_relative_gap=str(relative)))
    return dict(sha256=hashlib.sha256(raw).hexdigest(), counts=counts, exceptions=exceptions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("sources", type=Path, nargs="+")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("finqa_evaluator", args.evaluator)
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    result = {path.name: audit(path, evaluator) for path in args.sources}
    with args.output.open("x", encoding="utf-8") as out:
        json.dump(result, out, indent=2)
        out.write("\n")
    print(json.dumps({name: value["counts"] for name, value in result.items()}, indent=2))


if __name__ == "__main__":
    main()
