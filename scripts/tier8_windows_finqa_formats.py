"""Compare direct numeric answers and cited programs using one 7B checkpoint."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from statistics import median

from evidence_atoms import atom_catalog, compile_plan, reference_schema
from evidence_contract import TokenLedger
from tier8_v2_financial_pipeline import checked, evaluate_financial, question_units
from tier8_windows_challenge import official_evaluator, official_result
from tier8_windows_pilot import Models, jsonl
from tier8_windows_trained_critic import agrees


def valid_number(raw):
    if not isinstance(raw, dict) or type(raw.get("answer")) not in (int, float):
        return None
    try:
        number = Decimal(str(raw["answer"]))
    except InvalidOperation:
        return None
    return str(number) if number.is_finite() and abs(number.adjusted()) <= 50 else None


def run(args):
    model = Models(args)
    model.drafter_weights = args.model
    model.forced = True
    cohort = jsonl(args.cohort)
    if not cohort or len({row["report_group"] for row in cohort}) != len(cohort):
        raise ValueError("Expected one question per report")
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "cases.jsonl").open("x", encoding="utf8") as out:
        for index, case in enumerate(cohort):
            evidence = case["evidence"]
            context = ("Question: " + case["question"] + "\nFinancial report evidence by source ID:\n"
                       + json.dumps(evidence))
            units = question_units(case["question"], "question")
            unit_instruction = ("Percent means percentage points, fraction means a dimensionless ratio,"
                                " and number means the requested count or amount. Allowed units: "
                                + ", ".join(units))
            atoms = atom_catalog(evidence)
            catalog = "\n".join(f"{key}={atom['value']}@{atom['span_id']}" for key, atom in atoms.items())
            arms = {}
            order = ("direct", "program") if index % 2 == 0 else ("program", "direct")
            for arm in order:
                if arm == "direct":
                    schema = {"type": "object", "properties": {
                        "calculation": {"type": "string"}, "answer": {"type": "number"},
                        "unit": {"enum": list(units)}},
                        "required": ["calculation", "answer", "unit"], "additionalProperties": False}
                    prompt = (context + "\nCompute the answer from the evidence. Show the arithmetic"
                              " briefly in calculation. Return a numeric answer and unit. " + unit_instruction)
                    raw, event = model.call("drafter", prompt, schema, TokenLedger(), 768, "direct")
                    arms[arm] = dict(raw=raw, value=valid_number(raw), unit=(raw or {}).get("unit"), event=event)
                else:
                    prompt = (context + "\nQuantity references:\n" + catalog
                              + "\nReturn decision ANSWER, answer_unit, and steps. Use catalog IDs as operands,"
                                " CONST:value for permitted constants, and #0, #1 for earlier results."
                                " Use the shortest complete calculation. The final step is the answer. "
                              + unit_instruction)
                    raw, event = model.call("drafter", prompt, reference_schema(atoms, units, causal=True),
                                            TokenLedger(), 768, "program")
                    try:
                        program = compile_plan(raw, atoms)
                    except (ValueError, TypeError, AttributeError):
                        program = None
                    execution = checked(program, evidence)
                    arms[arm] = dict(program=program, execution=execution, event=event)
            out.write(json.dumps(dict(case_id=case["id"], arms=arms)) + "\n")
            out.flush()
            print(case["id"], arms["direct"]["value"], arms["program"]["execution"]["value"], flush=True)


def summarize(args):
    rows = jsonl(args.ledger)
    ids = {row["id"] for row in jsonl(args.cohort)}
    if not rows or len(rows) != len(ids) or {row["case_id"] for row in rows} != ids:
        raise ValueError("Format comparison is incomplete")
    gold = {row["id"]: row for row in json.loads(args.source.read_bytes())}
    scorer = official_evaluator(args.evaluator)
    counts = {arm: Counter() for arm in ("direct", "program", "agreement")}
    cases = []
    for row in rows:
        label = gold[row["case_id"]]
        direct, program = row["arms"]["direct"], row["arms"]["program"]
        direct_valid = direct["value"] is not None and direct["unit"] in ("number", "fraction", "percent")
        direct_match = direct_valid and evaluate_financial(label, {
            "decision": "ANSWER", "answer_unit": direct["unit"]},
            {"value": direct["value"], "issues": []})["case_success"]
        program_valid = not program["execution"]["issues"]
        program_match = evaluate_financial(label, program["program"], program["execution"])["case_success"]
        accepted = program_valid and direct_valid and agrees(
            direct["raw"], program["execution"]["value"], program["program"]["answer_unit"])
        try:
            official_match = program_valid and official_result(scorer, label, program["program"]) == label["qa"]["exe_ans"]
        except ValueError:
            official_match = False
        for arm, delivered, correct in (("direct", direct_valid, direct_match),
                                        ("program", program_valid, program_match),
                                        ("agreement", accepted, program_match)):
            counts[arm]["correct" if delivered and correct else "wrong" if delivered else "withheld"] += 1
        counts["program"]["official_execution_correct"] += official_match
        cases.append(dict(case_id=row["case_id"], reported=[direct_match, program_match],
                          program_official=official_match, agreement_delivered=accepted))
    resources = {}
    for arm in ("direct", "program"):
        events = [row["arms"][arm]["event"] for row in rows]
        resources[arm] = dict(peak_sampled_rss=max(event["peak_sampled_rss"] for event in events),
                             peak_job_commit=max(event["peak_job_commit"] for event in events),
                             median_seconds=median(event["elapsed_seconds"] for event in events))
    print(json.dumps(dict(questions=len(rows), counts=counts, resources=resources, cases=cases,
        direct_only_correct=sum(first and not second for first, second in (c["reported"] for c in cases)),
        program_only_correct=sum(second and not first for first, second in (c["reported"] for c in cases))), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    inference = commands.add_parser("run")
    for name in ("cli", "weights", "cohort", "output"):
        inference.add_argument(f"--{name}", type=Path, required=True)
    inference.add_argument("--model", required=True)
    inference.add_argument("--job-commit-limit", type=int, default=6_100_000_000)
    inference.set_defaults(run=run, one_step=False)
    report = commands.add_parser("summarize")
    for name in ("ledger", "cohort", "source", "evaluator"):
        report.add_argument(f"--{name}", type=Path, required=True)
    report.set_defaults(run=summarize)
    args = parser.parse_args()
    args.run(args)
