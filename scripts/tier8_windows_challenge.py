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
    for path in args.exclude_cohort:
        exposed.update(row["report_group"] for row in jsonl(path))
    sample_size = 6 if args.reject_both else 4
    salt = "win-verify-reject-v1|" if args.reject_both else "win-verify-v1|"
    source = json.loads(args.source.read_text(encoding="utf-8"))
    source.sort(key=lambda row: hashlib.sha256((salt + row["id"]).encode()).digest())
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
            if args.reject_both:
                remaining = [item for item in choices if item[1]["value"] != wrong["value"]]
                if not remaining:
                    raise ValueError("No distinct second near miss")
                other, other_wrong, other_change = select_negative(row["id"], remaining)
        except (ValueError, InvalidOperation) as exc:
            rejected[str(exc)] += 1
            continue
        chosen.append(dict(case_id=row["id"], report_group=group, question=public["question"],
                           evidence=evidence, positive=dict(program=positive, execution=correct),
                           negative=dict(program=negative, execution=wrong), mutation=change))
        if args.reject_both:
            chosen[-1].update(other_negative=dict(program=other, execution=other_wrong),
                              other_mutation=other_change)
        used.add(group)
        if len(chosen) == sample_size:
            break
    if len(chosen) != sample_size:
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


def replay_reject(args):
    model = Models(args)
    cohort = jsonl(args.cohort)
    if len(cohort) != 6 or len({case["report_group"] for case in cohort}) != 6:
        raise ValueError("Expected six distinct reports")
    schema = {"type": "object", "properties": {"choice": {"enum": ["A", "B", "NEITHER"]}},
              "required": ["choice"], "additionalProperties": False}
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "replay.jsonl").open("x", encoding="utf-8") as out:
        for index, case in enumerate(cohort):
            context = ("Question: " + case["question"] + "\nFinancial report evidence by source ID:\n"
                       + json.dumps(case["evidence"]))
            groups = [("positive", "negative"), ("negative", "other_negative")]
            if index % 2:
                groups.reverse()
            for group in groups:
                for first, second in (group, group[::-1]):
                    prompt = (context + "\nCandidate A:\n" + json.dumps(case[first])
                              + "\nCandidate B:\n" + json.dumps(case[second])
                              + "\nChoose A or B only if that program correctly answers the question."
                                " Check its source operands, arithmetic, and units."
                                " Return NEITHER if neither program is supported and correct.")
                    raw, event = model.call("drafter", prompt, schema, TokenLedger(), 192, "pairwise_reject")
                    expected = "A" if first == "positive" else "B" if second == "positive" else "NEITHER"
                    choice = (raw or {}).get("choice", "INVALID")
                    out.write(json.dumps(dict(case_id=case["case_id"], order=[first, second],
                                              expected=expected, choice=choice, event=event)) + "\n")
                    out.flush()
                    print(case["case_id"], expected, choice, flush=True)


def summarize_reject(args):
    rows = jsonl(args.ledger)
    cases = {row["case_id"] for row in rows}
    if len(rows) != 24 or len(cases) != 6:
        raise ValueError("Expected 24 presentations from six distinct reports")
    result = {"reports": len(cases), "peak_sampled_rss": max(
        row["event"]["peak_sampled_rss"] for row in rows)}
    for name, reject_expected in (("one_correct", False), ("both_wrong", True)):
        subsets = [[row for row in rows if row["case_id"] == case
                    and (row["expected"] == "NEITHER") == reject_expected] for case in sorted(cases)]
        if any(len(pair) != 2 or pair[0]["order"] != pair[1]["order"][::-1] for pair in subsets):
            raise ValueError("Incomplete or duplicated presentation order")
        agreed = Counter()
        for pair in subsets:
            selected = [row["order"][ord(row["choice"]) - ord("A")]
                        if row["choice"] in ("A", "B") else None for row in pair]
            if selected[0] is None or selected[0] != selected[1]:
                agreed["withheld"] += 1
            elif selected[0] == "positive":
                agreed["correct_delivery"] += 1
            else:
                agreed["wrong_delivery"] += 1
        result[name] = dict(
            presentations=12,
            correct=sum(row["choice"] == row["expected"] for pair in subsets for row in pair),
            wrong_accepts=sum(row["choice"] in ("A", "B") and row["choice"] != row["expected"]
                              for pair in subsets for row in pair),
            withheld=sum(row["choice"] not in ("A", "B") for pair in subsets for row in pair),
            reports_correct_both_orders=sum(all(row["choice"] == row["expected"] for row in pair)
                                            for pair in subsets),
            order_agreement_gate={key: agreed[key] for key in
                                  ("correct_delivery", "wrong_delivery", "withheld")})
    print(json.dumps(result, indent=2))


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
    build.add_argument("--exclude-cohort", type=Path, action="append", default=[])
    build.add_argument("--reject-both", action="store_true")
    build.set_defaults(run=freeze)
    run = commands.add_parser("replay")
    for name in ("cli", "weights", "cohort", "output"):
        run.add_argument(f"--{name}", type=Path, required=True)
    run.set_defaults(run=replay)
    reject = commands.add_parser("replay-reject")
    for name in ("cli", "weights", "cohort", "output"):
        reject.add_argument(f"--{name}", type=Path, required=True)
    reject.set_defaults(run=replay_reject)
    report = commands.add_parser("summarize")
    report.add_argument("ledger", type=Path)
    report.set_defaults(run=summarize)
    report_reject = commands.add_parser("summarize-reject")
    report_reject.add_argument("ledger", type=Path)
    report_reject.set_defaults(run=summarize_reject)
    args = parser.parse_args()
    args.run(args)
