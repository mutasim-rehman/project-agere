"""Evaluate matched trained critics on frozen, naturally generated drafts."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
from statistics import median

from evidence_contract import TokenLedger
from financial_review_protocol import BINARY_INSTRUCTION, BINARY_SCHEMA
from tier8_v2_financial_pipeline import evaluate_financial
from tier8_windows_challenge import official_evaluator, official_result
from tier8_windows_pilot import Models, jsonl


def freeze(args):
    excluded = {row["report_group"] for path in args.exclude_records for row in jsonl(path)}
    packets = {row["id"]: row for row in jsonl(args.cohort)}
    drafts = jsonl(args.drafts)
    if {row["case_id"] for row in drafts} != set(packets) or len(drafts) != len(packets):
        raise ValueError("Frozen drafts and evidence must cover the same cases")
    count = 0
    with args.output.open("x", encoding="utf-8") as out:
        for row in drafts:
            public = packets[row["case_id"]]
            if public["report_group"] in excluded:
                continue
            draft = row["drafts"][1]
            if draft.get("evidence") != public["evidence"]:
                raise ValueError(f"Expanded candidate evidence mismatch for {row['case_id']}")
            out.write(json.dumps(dict(case_id=row["case_id"], report_group=public["report_group"],
                                      evidence=public["evidence"], question=public["question"],
                                      candidate=draft["candidate"])) + "\n")
            count += 1
    print(json.dumps(dict(eligible=count, excluded=len(drafts)-count,
        exclusions={str(path):hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in args.exclude_records}), indent=2))


def replay(args):
    rows = jsonl(args.cohort)
    if not rows or len(rows) != len({row["report_group"] for row in rows}):
        raise ValueError("Expected one candidate per report")
    model = Models(args)
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "replay.jsonl").open("x", encoding="utf-8") as out:
        for index, row in enumerate(rows):
            candidate = row["candidate"]
            prompt = ("Question: " + row["question"] + "\nFinancial report evidence by source ID:\n"
                      + json.dumps(row["evidence"]) + "\nProposed program:\n"
                      + json.dumps(candidate["program"]) + "\nDeterministic execution:\n"
                      + json.dumps(candidate["execution"]) + "\n" + BINARY_INSTRUCTION)
            arms = {}
            order = ("control", "crossed") if index % 2 == 0 else ("crossed", "control")
            for arm in order:
                if candidate["execution"]["issues"]:
                    arms[arm] = dict(verdict=None, event=None)
                    continue
                model.adapter = getattr(args, arm)
                raw, event = model.call("drafter", prompt, BINARY_SCHEMA, TokenLedger(), 192, "trained_critic")
                arms[arm] = dict(verdict=(raw or {}).get("verdict"), event=event)
            out.write(json.dumps(dict(case_id=row["case_id"], arms=arms)) + "\n")
            out.flush()
            print(row["case_id"], {arm: result["verdict"] for arm, result in arms.items()}, flush=True)


def independent(args):
    rows = jsonl(args.cohort)
    model = Models(args)
    model.drafter_weights = args.direct_weights
    schema = {"type": "object", "properties": {"answer": {"type": "number"},
        "unit": {"enum": ["number", "fraction", "percent"]}},
        "required": ["answer", "unit"], "additionalProperties": False}
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "replay.jsonl").open("x", encoding="utf-8") as out:
        for row in rows:
            prompt = ("Question: " + row["question"] + "\nFinancial report evidence by source ID:\n"
                      + json.dumps(row["evidence"]) + "\nSolve the question from the evidence."
                        " Return a numeric answer and its unit. Percent means percentage points,"
                        " fraction means a dimensionless ratio, and number means the requested"
                        " count or amount. Respect the question's scale.")
            raw, event = model.call("drafter", prompt, schema, TokenLedger(), 192, "independent")
            candidate = row["candidate"]
            accepted = (not candidate["execution"]["issues"] and agrees(
                raw, candidate["execution"]["value"], candidate["program"]["answer_unit"]))
            arms = {"independent": dict(verdict="PASS" if accepted else "UNKNOWN", event=event,
                                        direct=raw)}
            out.write(json.dumps(dict(case_id=row["case_id"], arms=arms)) + "\n")
            out.flush()
            print(row["case_id"], accepted, raw, flush=True)


def agrees(direct, executed, unit):
    if not isinstance(direct, dict) or type(direct.get("answer")) not in (int, float):
        return False
    other_unit = direct.get("unit")
    if unit not in ("number", "fraction", "percent") or other_unit not in ("number", "fraction", "percent"):
        return False
    if (unit == "number") != (other_unit == "number"):
        return False
    try:
        left, right = Decimal(executed), Decimal(str(direct["answer"]))
    except (InvalidOperation, TypeError):
        return False
    if not left.is_finite() or not right.is_finite():
        return False
    left = left / 100 if unit == "percent" else left
    right = right / 100 if other_unit == "percent" else right
    return abs(left - right) <= Decimal("0.00001") * max(1, abs(left))


def summarize(args):
    cohort = {row["case_id"]: row for row in jsonl(args.cohort)}
    gold = {row["id"]: row for row in json.loads(args.source.read_bytes())}
    evaluate = official_evaluator(args.evaluator)
    rows = jsonl(args.ledger)
    if len(rows) != len(cohort) or {row["case_id"] for row in rows} != set(cohort):
        raise ValueError("Critic replay is incomplete")
    conditions = tuple(rows[0]["arms"])
    if any(set(row["arms"]) != set(conditions) for row in rows):
        raise ValueError("Critic conditions changed during replay")
    totals = {arm: {"official": Counter(), "reported": Counter()}
              for arm in ("accept_executable", *conditions)}
    details = []
    for row in rows:
        case = row["case_id"]
        candidate = cohort[case]["candidate"]
        annotation = gold[case]
        program, execution = candidate["program"], candidate["execution"]
        executable = not execution["issues"]
        try:
            official = executable and official_result(evaluate, annotation, program) == annotation["qa"]["exe_ans"]
        except ValueError:
            official = False
        reported = evaluate_financial(annotation, program, execution)["case_success"]
        verdicts = {arm: data["verdict"] for arm, data in row["arms"].items()}
        details.append(dict(case_id=case, official=official, reported=reported, verdicts=verdicts))
        for arm, accepted in {"accept_executable": executable,
                              **{k: executable and v == "PASS" for k, v in verdicts.items()}}.items():
            for metric, correct in (("official", official), ("reported", reported)):
                outcome = "correct" if accepted and correct else "wrong" if accepted else "withheld"
                totals[arm][metric][outcome] += 1
    for metrics in totals.values():
        for counts in metrics.values():
            coverage = counts["correct"] + counts["wrong"]
            counts["coverage"] = coverage / len(rows)
            counts["accepted_error"] = counts["wrong"] / coverage if coverage else None
    resources = {}
    for arm in conditions:
        events = [row["arms"][arm]["event"] for row in rows if row["arms"][arm]["event"]]
        commits = [event["peak_job_commit"] for event in events
                   if event.get("peak_job_commit") is not None]
        resources[arm] = dict(calls=len(events),
            peak_sampled_rss=max((event["peak_sampled_rss"] for event in events), default=0),
            peak_job_commit=max(commits, default=None),
            median_seconds=median(event["elapsed_seconds"] for event in events) if events else None)
    print(json.dumps(dict(reports=len(rows), totals=totals, resources=resources, cases=details), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    build = commands.add_parser("freeze")
    for name in ("cohort", "drafts", "output"):
        build.add_argument(f"--{name}", type=Path, required=True)
    build.add_argument("--exclude-records", type=Path, action="append", required=True)
    build.set_defaults(run=freeze)
    run = commands.add_parser("replay")
    for name in ("cli", "weights", "cohort", "output", "control", "crossed"):
        run.add_argument(f"--{name}", type=Path, required=True)
    run.add_argument("--job-commit-limit", type=int)
    run.set_defaults(run=replay)
    blind = commands.add_parser("independent")
    for name in ("cli", "weights", "cohort", "output"):
        blind.add_argument(f"--{name}", type=Path, required=True)
    blind.add_argument("--direct-weights", required=True)
    blind.add_argument("--job-commit-limit", type=int)
    blind.set_defaults(run=independent)
    report = commands.add_parser("summarize")
    for name in ("cohort", "ledger", "source", "evaluator"):
        report.add_argument(f"--{name}", type=Path, required=True)
    report.set_defaults(run=summarize)
    args = parser.parse_args()
    args.run(args)
