"""Build and run a fixed-candidate verifier challenge on Windows."""
import argparse
from collections import Counter
from decimal import InvalidOperation
import hashlib
import importlib.util
import json
from pathlib import Path

from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import execute
from evidence_contract import TokenLedger
from financial_review_protocol import BINARY_INSTRUCTION, BINARY_SCHEMA
from tier8_v2_adaptation_data import prepare, report_group
from tier8_v2_critic_data import negative_candidates, select_negative
from tier8_windows_pilot import Models, jsonl


def official_evaluator(path):
    spec = importlib.util.spec_from_file_location("finqa_official", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.eval_program


def official_result(evaluate, row, candidate):
    tokens = []
    for step in candidate["steps"]:
        tokens.extend((step["op"] + "(", step["left"]["value"], step["right"]["value"], ")"))
    invalid, value = evaluate(tokens + ["EOF"], row["table"])
    if invalid:
        raise ValueError("Official evaluator rejected the translated program")
    return value


def freeze(args):
    evaluate = official_evaluator(args.evaluator)
    exposed = {report_group(row["id"]) for path in args.exclude
               for row in json.loads(path.read_text(encoding="utf-8"))}
    source = json.loads(args.source.read_text(encoding="utf-8"))
    source.sort(key=lambda row: hashlib.sha256(("win-verify-v1|" + row["id"]).encode()).digest())
    chosen, used, rejected = [], set(), Counter()
    for row in source:
        group = report_group(row["id"])
        if group in exposed or group in used:
            continue
        try:
            prepared = prepare(row)
            public = prepared["public"]
            evidence = public["evidence"]
            positive = compile_plan(prepared["target"], atom_catalog(evidence))
            correct = execute(positive["steps"], evidence)
            if correct["issues"] or official_result(evaluate, row, positive) != row["qa"]["exe_ans"]:
                raise ValueError("Reference fails official execution")
            choices = []
            for candidate, execution, change in negative_candidates(prepared, row):
                if official_result(evaluate, row, candidate) != row["qa"]["exe_ans"]:
                    choices.append((candidate, execution, change))
            if not choices:
                raise ValueError("No scorer-concordant near miss")
            negative, wrong, change = select_negative(row["id"], choices)
        except (ValueError, InvalidOperation) as exc:
            rejected[str(exc)] += 1
            continue
        chosen.append(dict(case_id=row["id"], report_group=group, question=public["question"],
                           evidence=evidence, positive=dict(program=positive, execution=correct),
                           negative=dict(program=negative, execution=wrong), mutation=change))
        used.add(group)
        if len(chosen) == 4:
            break
    if len(chosen) != 4:
        raise ValueError(f"Only {len(chosen)} eligible reports: {rejected}")
    with args.output.open("x", encoding="utf-8") as out:
        for case in chosen:
            out.write(json.dumps(case) + "\n")
    print([case["case_id"] for case in chosen], dict(rejected), flush=True)


def replay(args):
    model = Models(args)
    args.output.mkdir(parents=True, exist_ok=False)
    choice_schema = {"type": "object", "properties": {"choice": {"enum": ["A", "B"]}},
                     "required": ["choice"], "additionalProperties": False}
    with (args.output / "replay.jsonl").open("x", encoding="utf-8") as out:
        for index, case in enumerate(jsonl(args.cohort)):
            context = ("Question: " + case["question"] + "\nFinancial report evidence by source ID:\n"
                       + json.dumps(case["evidence"]))
            order = ("positive", "negative") if index % 2 == 0 else ("negative", "positive")
            for role in ("verifier", "drafter"):
                for label in order:
                    item = case[label]
                    prompt = (context + "\nProposed program:\n" + json.dumps(item["program"])
                              + "\nDeterministic execution:\n" + json.dumps(item["execution"])
                              + "\n" + BINARY_INSTRUCTION)
                    raw, event = model.call(role, prompt, BINARY_SCHEMA, TokenLedger(), 192, "binary")
                    record = dict(case_id=case["case_id"], role=role, expected=label,
                                  response=raw, event=event)
                    out.write(json.dumps(record) + "\n")
                    out.flush()
                    print(case["case_id"], role, label, raw, flush=True)
            for first, second in (order, order[::-1]):
                prompt = (context + "\nCandidate A:\n" + json.dumps(case[first])
                          + "\nCandidate B:\n" + json.dumps(case[second])
                          + "\nChoose the program that best answers the question. Check the source"
                            " operands, arithmetic operations, and units. Return choice A or B.")
                raw, event = model.call("drafter", prompt, choice_schema, TokenLedger(), 192, "pairwise")
                expected = "A" if first == "positive" else "B"
                out.write(json.dumps(dict(case_id=case["case_id"], role="drafter",
                                         expected=expected, response=raw, event=event)) + "\n")
                out.flush()
                print(case["case_id"], "pairwise", expected, raw, flush=True)


def summarize(args):
    rows = jsonl(args.ledger)
    groups = {}
    seen = set()
    for row in rows:
        stage = row["event"]["stage"]
        key = (row["case_id"], row["role"], stage, row["expected"])
        if key in seen:
            raise ValueError(f"Duplicate observation: {key}")
        seen.add(key)
        groups.setdefault((stage, row["role"]), []).append(row)
    ids = {row["case_id"] for row in rows}
    if len(ids) != 4 or len(rows) != 24:
        raise ValueError("Expected all 24 observations from four reports")
    result = {}
    for (stage, role), members in groups.items():
        summary = {"observations": len(members), "peak_sampled_rss": max(
            row["event"]["peak_sampled_rss"] for row in members)}
        if stage == "binary":
            summary["verdicts_by_label"] = {label: Counter(
                (row["response"] or {}).get("verdict", "INVALID") for row in members
                if row["expected"] == label) for label in ("positive", "negative")}
        else:
            scores = {case: [((row["response"] or {}).get("choice") == row["expected"])
                              for row in members if row["case_id"] == case] for case in ids}
            summary["correct_choices"] = sum(sum(values) for values in scores.values())
            summary["correct_in_both_orders"] = sum(values == [True, True] for values in scores.values())
            summary["wrong_in_both_orders"] = sum(values == [False, False] for values in scores.values())
        result[f"{stage}_{role}"] = summary
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    build = commands.add_parser("freeze")
    for name in ("source", "evaluator", "output"):
        build.add_argument(f"--{name}", type=Path, required=True)
    build.add_argument("--exclude", type=Path, action="append", required=True)
    build.set_defaults(run=freeze)
    run = commands.add_parser("replay")
    for name in ("cli", "weights", "cohort", "output"):
        run.add_argument(f"--{name}", type=Path, required=True)
    run.set_defaults(run=replay)
    report = commands.add_parser("summarize")
    report.add_argument("ledger", type=Path)
    report.set_defaults(run=summarize)
    args = parser.parse_args()
    args.run(args)
