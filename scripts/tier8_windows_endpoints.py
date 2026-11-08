"""Replay an evidence-only endpoint selector on frozen Windows candidates."""
import argparse
from collections import Counter
import json
from pathlib import Path

from evidence_contract import TokenLedger
from program_endpoints import choose_endpoint, endpoint_candidates
from tier8_windows_challenge import official_evaluator, official_result
from tier8_windows_pilot import Models, jsonl


def replay(args):
    packets = {row["id"]: row for row in jsonl(args.cohort)}
    rows = jsonl(args.drafts)
    if {row["case_id"] for row in rows} != set(packets):
        raise ValueError("Case ledger and evidence cohort must match")
    model = Models(args)
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "endpoints.jsonl").open("x", encoding="utf-8") as out:
        for row in rows:
            public = packets[row["case_id"]]
            if set(public) & {"gold", "qa", "answer", "program", "gold_inds"}:
                raise ValueError("Endpoint review requires an evidence-only packet")
            for index, draft in enumerate(row["drafts"]):
                answer = draft["candidate"]["program"]
                events = []

                def choose(prompt, schema):
                    raw, event = model.call("drafter", prompt, schema, TokenLedger(), 192, "endpoint")
                    events.append(event)
                    return raw

                selected, trace = choose_endpoint(answer, public["evidence"], public["question"], choose)
                out.write(json.dumps(dict(case_id=row["case_id"], draft=index, answer=answer,
                                          selected=selected, trace=trace, events=events)) + "\n")
                out.flush()
                print(row["case_id"], index, trace["selection"], flush=True)


def summarize(args):
    evaluate = official_evaluator(args.evaluator)
    gold = {row["id"]: row for row in json.loads(args.source.read_text(encoding="utf-8"))}
    packets = {row["id"]: row for row in jsonl(args.cohort)}
    rows = jsonl(args.replay)
    keys = [(row["case_id"], row["draft"]) for row in rows]
    if set(keys) != {(case, arm) for case in packets for arm in (0, 1)} or len(keys) != len(set(keys)):
        raise ValueError("Expected a complete paired endpoint ledger")
    counts = [Counter(), Counter()]
    cases = []
    for row in rows:
        case, arm = row["case_id"], row["draft"]
        evidence = packets[case]["evidence"]

        def correct(program):
            if not endpoint_candidates(program, evidence):
                return False
            try:
                return official_result(evaluate, gold[case], program) == gold[case]["qa"]["exe_ans"]
            except ValueError:
                return False

        endpoints = endpoint_candidates(row["answer"], evidence)
        labels = {item["id"]: correct(item["answer"]) for item in endpoints}
        baseline = labels.get("KEEP", False)
        first = labels.get("P001", baseline)
        selected = correct(row["selected"])
        stats = counts[arm]
        stats["drafts"] += 1
        stats["keep_correct"] += baseline
        stats["first_correct"] += first
        stats["model_correct"] += selected
        stats["oracle_correct"] += any(labels.values())
        stats["first_gains"] += first and not baseline
        stats["first_losses"] += baseline and not first
        stats["model_gains"] += selected and not baseline
        stats["model_losses"] += baseline and not selected
        stats["model_edits"] += row["trace"]["accepted"]
        for event in row["events"]:
            stats["peak_review_rss"] = max(stats["peak_review_rss"], event["peak_sampled_rss"])
        cases.append(dict(case_id=case, draft=arm, labels=labels, selected=row["trace"]["selection"],
                          model_correct=selected))
    print(json.dumps(dict(reports=len(packets), draft_arms=counts, cases=cases), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    run = commands.add_parser("replay")
    for name in ("cli", "weights", "cohort", "drafts", "output"):
        run.add_argument(f"--{name}", type=Path, required=True)
    run.set_defaults(run=replay)
    report = commands.add_parser("summarize")
    for name in ("replay", "cohort", "source", "evaluator"):
        report.add_argument(f"--{name}", type=Path, required=True)
    report.set_defaults(run=summarize)
    args = parser.parse_args()
    args.run(args)
