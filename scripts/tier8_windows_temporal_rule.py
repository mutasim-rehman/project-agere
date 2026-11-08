"""A narrow, abstaining no-model baseline for explicit two-year table changes."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re

from tier8_v2_financial_pipeline import checked, evaluate_financial
from tier8_v2_finqa import packet, tokens
from tier8_v2_demo_retrieval import report_group
from tier8_windows_challenge import official_evaluator, official_result
from tier8_windows_pilot import jsonl


QUERY = re.compile(
    r"^what (?:was|is) the (?P<relative>percent(?:age)? )?"
    r"(?P<direction>change|increase|decrease) in (?P<metric>.+?) "
    r"from (?P<start>(?:19|20)\d{2}) to (?P<end>(?:19|20)\d{2})\??$",
    re.IGNORECASE,
)


def cell_value(text):
    text = text.replace(",", "").replace("$", "").strip()
    accounting = re.fullmatch(r"(?:(-\d+(?:\.\d+)?)\s*)?\(\s*(\d+(?:\.\d+)?)\s*\)", text)
    if accounting:
        value = "-" + accounting[2]
        if accounting[1] and Decimal(accounting[1]) != Decimal(value):
            raise ValueError("ambiguous_accounting_value")
        text = value
    if not re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text):
        raise ValueError("nonnumeric_cell")
    return Decimal(text)


def candidate(question, table, evidence):
    match = QUERY.fullmatch(question.strip())
    if not match:
        raise ValueError("outside_template")
    phrase = match["metric"].lower()
    scale = re.match(r"^(thousands|millions|billions) of (.+)$", phrase)
    if scale:
        if not table or not any(scale[1] in heading.lower() for heading in table[0]):
            raise ValueError("requested_scale_not_explicit")
        phrase = scale[2]
    metric = tokens(phrase)
    if not metric or not table:
        raise ValueError("no_metric_or_table")
    rows = [(index, row) for index, row in enumerate(table[1:], 1)
            if row and tokens(row[0]) == metric and f"table_{index}" in evidence]
    if len(rows) != 1:
        raise ValueError("ambiguous_or_missing_row")
    index, row = rows[0]
    span = f"table_{index}"
    values = []
    for year in (match["start"], match["end"]):
        matches = [i for i, heading in enumerate(table[0]) if i and
                   re.search(r"\b" + year + r"\b", heading)]
        if len(matches) != 1 or matches[0] >= len(row):
            raise ValueError("ambiguous_or_missing_year")
        values.append(cell_value(row[matches[0]]))
    start, end = values
    direction = match["direction"].lower()
    if match["start"] == match["end"] or (direction != "change" and start == end):
        raise ValueError("no_change")
    if (direction == "increase" and end < start) or (direction == "decrease" and end > start):
        raise ValueError("direction_conflict")
    if match["relative"] and start <= 0:
        raise ValueError("nonpositive_reference")
    left, right = (start, end) if direction == "decrease" else (end, start)
    operand = lambda value: {"value": str(value), "span_id": span}
    steps = [{"op": "subtract", "left": operand(left), "right": operand(right)}]
    if match["relative"]:
        steps.append({"op": "divide", "left": {"value": "#0", "span_id": "STEP#0"},
                      "right": operand(start)})
    answer = {"decision": "ANSWER", "answer_unit": "fraction" if match["relative"] else "number",
              "steps": steps}
    result = checked(answer, evidence)
    if result["issues"]:
        raise ValueError("source_execution_failed")
    return answer, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "evaluator", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--exclude-source", type=Path, action="append", default=[])
    parser.add_argument("--exclude-cohort", type=Path, action="append", default=[])
    args = parser.parse_args()
    evaluate = official_evaluator(args.evaluator)
    raw = args.source.read_bytes()
    excluded = {report_group(row["id"]) for path in args.exclude_source
                for row in json.loads(path.read_bytes())}
    excluded.update(row["report_group"] for path in args.exclude_cohort for row in jsonl(path))
    source = json.loads(raw)
    rows = [row for row in source if report_group(row["id"]) not in excluded]
    records, reasons = [], Counter()
    for row in rows:
        public = packet(row)
        try:
            answer, execution = candidate(public["question"], row["table"], public["evidence"])
        except (ValueError, InvalidOperation) as exc:
            reasons[str(exc)] += 1
            continue
        official = official_result(evaluate, row, answer) == row["qa"]["exe_ans"]
        reported = evaluate_financial(row, answer, execution)["case_success"]
        records.append(dict(case_id=row["id"], program=answer, execution=execution,
                            official=official, reported=reported))
    result = dict(source_sha256=hashlib.sha256(raw).hexdigest(), questions=len(rows),
                  reports=len({report_group(row["id"]) for row in rows}),
                  questions_excluded=len(source) - len(rows),
                  delivered=len(records), withheld=sum(reasons.values()),
                  official_correct=sum(row["official"] for row in records),
                  reported_correct=sum(row["reported"] for row in records),
                  delivered_reports=len({report_group(row["case_id"]) for row in records}),
                  withholding_reasons=reasons, records=records)
    with args.output.open("x", encoding="utf-8") as out:
        json.dump(result, out, indent=2)
        out.write("\n")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}, indent=2))


if __name__ == "__main__":
    main()
