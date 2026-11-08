"""Matched direct-number and executable-program study on TAT-QA arithmetic."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import importlib
import json
from pathlib import Path
import sys

from evidence_atoms import atom_catalog, compile_plan, reference_schema
from evidence_contract import TokenLedger
from tier8_v2_financial_pipeline import checked
from tier8_v2_finqa import packet
from tier8_windows_pilot import Models, jsonl


SCALES = ("", "thousand", "million", "billion", "percent")


def freeze(args):
    source = json.loads(args.source.read_text(encoding="utf-8"))
    ranked = sorted(((context, question) for context in source for question in context["questions"]
                     if question["answer_type"] == "arithmetic"),
                    key=lambda item: hashlib.sha256(("agere-tatqa-v1|" + item[1]["uid"]).encode()).digest())
    rows, seen = [], set()
    for context, question in ranked:
        table = context["table"]
        if table["uid"] in seen:
            continue
        public = packet({"id": question["uid"], "table": table["table"],
                         "qa": {"question": question["question"]},
                         "pre_text": [paragraph["text"] for paragraph in context["paragraphs"]],
                         "post_text": []})
        if not atom_catalog(public["evidence"]):
            continue
        rows.append({**public, "table_id": table["uid"]})
        seen.add(table["uid"])
        if len(rows) == args.count:
            break
    if len(rows) != args.count:
        raise ValueError("Insufficient distinct TAT-QA tables")
    with args.output.open("x", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row) + "\n")


def normalize_prediction(value, scale):
    if isinstance(value, bool) or scale not in SCALES:
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        return None
    if not number.is_finite() or abs(number.adjusted()) > 50:
        return None
    return {"answer": format(number, "f"), "scale": scale}


def run(args):
    model = Models(args)
    cohort = jsonl(args.cohort)
    if len(cohort) != len({row["table_id"] for row in cohort}):
        raise ValueError("Expected one question per TAT-QA table")
    args.output.mkdir(parents=True, exist_ok=False)
    direct_schema = {"type": "object", "properties": {"calculation": {"type": "string"},
        "answer": {"type": "number"}, "scale": {"enum": list(SCALES)}},
        "required": ["calculation", "answer", "scale"], "additionalProperties": False}
    with (args.output / "cases.jsonl").open("x", encoding="utf-8") as out:
        for index, row in enumerate(cohort):
            evidence = row["evidence"]
            context = ("Question: " + row["question"] + "\nFinancial report evidence by source ID:\n"
                       + json.dumps(evidence))
            scale_instruction = ("Use the requested display scale: thousand, million, billion, percent,"
                                 " or empty for an unscaled number. A percent is in percentage points.")
            atoms = atom_catalog(evidence)
            arms = {}
            for arm in (("direct", "program") if index % 2 == 0 else ("program", "direct")):
                budget = TokenLedger()
                if arm == "direct":
                    prompt = (context + "\nCompute the answer using the evidence. State the arithmetic briefly"
                              " in calculation, then return a numeric answer and scale. " + scale_instruction)
                    raw, event = model.call("drafter", prompt, direct_schema, budget, 768, "direct")
                    prediction = normalize_prediction((raw or {}).get("answer"), (raw or {}).get("scale"))
                else:
                    catalog = "\n".join(f"{key}={atom['value']}@{atom['span_id']}" for key, atom in atoms.items())
                    prompt = (context + "\nQuantity references:\n" + catalog
                              + "\nReturn decision ANSWER, answer_unit, and steps. Use catalog IDs as operands,"
                                " CONST:value for permitted constants, and #0, #1 for earlier results."
                                " Use the shortest complete calculation. Its final operation is the answer."
                                " Use answer_unit as the display scale. " + scale_instruction)
                    model.forced = True
                    raw, event = model.call("drafter", prompt, reference_schema(atoms, SCALES, causal=True),
                                            budget, 768, "program")
                    try:
                        program = compile_plan(raw, atoms)
                    except (ValueError, TypeError, AttributeError):
                        program = None
                    execution = checked(program, evidence)
                    prediction = normalize_prediction(execution["value"], (program or {}).get("answer_unit"))
                arms[arm] = dict(prediction=prediction, output=raw, event=event)
            out.write(json.dumps(dict(case_id=row["id"], arms=arms)) + "\n")
            out.flush()
            print(row["id"], {arm: result["prediction"] for arm, result in arms.items()}, flush=True)


def summarize(args):
    sys.path.insert(0, str(args.metric_directory.resolve()))
    metric = importlib.import_module("tatqa_metric")
    gold = {question["uid"]: question for item in json.loads(args.source.read_bytes())
            for question in item["questions"]}
    rows = jsonl(args.ledger)
    ids = {row["id"] for row in jsonl(args.cohort)}
    if len(rows) != len(ids) or {row["case_id"] for row in rows} != ids:
        raise ValueError("Case ledger differs from the frozen TAT-QA cohort")
    result = {"questions": len(rows), "direct": Counter(), "program": Counter(), "cases": []}
    for row in rows:
        annotation = gold[row["case_id"]]
        labels = {}
        for arm, output in row["arms"].items():
            pred = output["prediction"]
            scorer = metric.TaTQAEmAndF1()
            scorer(annotation, [pred["answer"]] if pred else [], pred_scale=pred["scale"] if pred else "")
            em, f1, _, _ = scorer.get_overall_metric()
            labels[arm] = bool(em)
            result[arm]["exact"] += em
            result[arm]["f1"] += f1
            result[arm]["valid"] += pred is not None
            result[arm]["peak_sampled_rss"] = max(result[arm]["peak_sampled_rss"],
                                                  output["event"]["peak_sampled_rss"])
        result["cases"].append(dict(case_id=row["case_id"], exact=labels))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    build = commands.add_parser("freeze")
    for name in ("source", "output"):
        build.add_argument(f"--{name}", type=Path, required=True)
    build.add_argument("--count", type=int, default=16)
    build.set_defaults(run=freeze)
    inference = commands.add_parser("run")
    for name in ("cli", "weights", "cohort", "output"):
        inference.add_argument(f"--{name}", type=Path, required=True)
    inference.add_argument("--job-commit-limit", type=int)
    inference.set_defaults(run=run, one_step=False)
    report = commands.add_parser("summarize")
    for name in ("source", "cohort", "ledger", "metric-directory"):
        report.add_argument(f"--{name}", type=Path, required=True)
    report.set_defaults(run=summarize)
    args = parser.parse_args()
    args.run(args)
