"""Generate and review two evidence-only FinQA candidates per report on Windows."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from evidence_atoms import atom_catalog, compile_plan, reference_schema
from evidence_contract import TokenLedger
from tier8_v2_demo_retrieval import report_group
from tier8_v2_financial_pipeline import checked, evaluate_financial, question_units
from tier8_v2_finqa import packet
from tier8_windows_challenge import official_evaluator, official_result
from tier8_windows_pilot import Models, jsonl


def freeze(args):
    excluded = {report_group(row["id"]) for path in args.exclude
                for row in json.loads(path.read_text(encoding="utf-8"))}
    for path in args.exclude_cohort:
        excluded.update(row["report_group"] for row in jsonl(path))
    source = json.loads(args.source.read_text(encoding="utf-8"))
    source.sort(key=lambda row: hashlib.sha256(("windows-natural-v1|" + row["id"]).encode()).digest())
    with args.output.open("x", encoding="utf-8") as out:
        selected = 0
        for row in source:
            group = report_group(row["id"])
            if group in excluded:
                continue
            public = packet(row)
            if not atom_catalog(public["evidence"]):
                continue
            out.write(json.dumps({**public, "report_group": group}) + "\n")
            excluded.add(group)
            selected += 1
            print(row["id"], flush=True)
            if selected == 6:
                return
    raise ValueError("Insufficient eligible reports")


def review(model, context, drafts, budget):
    schema = {"type": "object", "properties": {"choice": {"enum": ["A", "B", "NEITHER"]}},
              "required": ["choice"], "additionalProperties": False}
    choices = []
    for order in ((0, 1), (1, 0)):
        first, second = [drafts[i]["candidate"] for i in order]
        prompt = (context + "\nCandidate A:\n" + json.dumps(first)
                  + "\nCandidate B:\n" + json.dumps(second)
                  + "\nChoose A or B only if that program correctly answers the question."
                    " Check its source operands, arithmetic, and units."
                    " Return NEITHER if neither program is supported and correct.")
        raw, event = model.call("drafter", prompt, schema, budget, 192, "pairwise_reject")
        choice = (raw or {}).get("choice")
        index = {"A": order[0], "B": order[1]}.get(choice)
        choices.append(dict(order=order, choice=choice, index=index, event=event))
    return choices


def run(args):
    model = Models(args)
    public = jsonl(args.cohort)
    if len(public) != 6 or len({case["report_group"] for case in public}) != 6:
        raise ValueError("Expected six separate reports")
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "cases.jsonl").open("x", encoding="utf-8") as out:
        for case in public:
            context = ("Question: " + case["question"] + "\nFinancial report evidence by source ID:\n"
                       + json.dumps(case["evidence"]))
            atoms = atom_catalog(case["evidence"])
            units = question_units(case["question"], "question")
            catalog = "\n".join(f"{key}={atom['value']}@{atom['span_id']}" for key, atom in atoms.items())
            prompt = (context + "\nQuantity references:\n" + catalog
                      + "\nReturn an arithmetic program with decision ANSWER, answer_unit, and steps."
                        " Use catalog IDs as operands, CONST:value for permitted constants, and #0, #1"
                        " for earlier results. The last step gives the requested answer."
                        " Percent means percentage points and fraction means a dimensionless ratio."
                      + "\nAllowed units: " + ", ".join(units))
            budget = TokenLedger()
            drafts = []
            for instruction in ("Check that the final operation answers the exact question.",
                                "Use the shortest calculation that fully answers the question."
                                " Stop once the requested quantity is computed."):
                model.forced = True
                plan, event = model.call("drafter", prompt + "\n" + instruction,
                                         reference_schema(atoms, units, causal=True), budget, 768, "program")
                try:
                    program = compile_plan(plan, atoms)
                except (ValueError, TypeError, AttributeError):
                    program = None
                execution = checked(program, case["evidence"])
                drafts.append(dict(plan=plan, candidate=dict(program=program, execution=execution),
                                   event=event))
            executable = all(not draft["candidate"]["execution"]["issues"] for draft in drafts)
            reviews = review(model, context, drafts, budget) if executable else []
            out.write(json.dumps(dict(case_id=case["id"], drafts=drafts, reviews=reviews,
                                      reserved_tokens=budget.spent)) + "\n")
            out.flush()
            print(case["id"], [draft["candidate"]["execution"]["value"] for draft in drafts],
                  [review["choice"] for review in reviews], flush=True)


def summarize(args):
    rows = jsonl(args.ledger)
    if len(rows) != 6 or len({row["case_id"] for row in rows}) != 6:
        raise ValueError("Expected six distinct completed questions")
    evaluate = official_evaluator(args.evaluator)
    gold = {row["id"]: row for row in json.loads(args.source.read_text(encoding="utf-8"))}
    result = dict(questions=len(rows), official=Counter(), reported=Counter(), cases=[])
    peaks = []
    for row in rows:
        annotation = gold[row["case_id"]]
        evidence = packet(annotation)["evidence"]
        complete_evidence = set(annotation["qa"]["gold_inds"]) <= evidence.keys()
        candidates = [draft["candidate"] for draft in row["drafts"]]
        peaks.extend(item["event"]["peak_sampled_rss"] for item in row["drafts"] + row["reviews"])
        indices = [review["index"] for review in row["reviews"]]
        equivalent = candidates[0] == candidates[1]
        agreed = (len(indices) == 2 and None not in indices
                  and (indices[0] == indices[1] or equivalent))
        delivered = indices[0] if agreed else None
        official = []
        for candidate in candidates:
            try:
                correct = (not candidate["execution"]["issues"]
                           and official_result(evaluate, annotation, candidate["program"])
                           == annotation["qa"]["exe_ans"])
            except ValueError:
                correct = False
            official.append(correct)
        reported = [evaluate_financial(annotation, item["program"], item["execution"])["case_success"]
                    for item in candidates]
        correct_prefix = False
        for candidate, correct in zip(candidates, official):
            program = candidate["program"]
            if correct or not program:
                continue
            for length in range(1, len(program["steps"])):
                prefix = {**program, "steps": program["steps"][:length]}
                if checked(prefix, evidence)["issues"]:
                    continue
                try:
                    if official_result(evaluate, annotation, prefix) == annotation["qa"]["exe_ans"]:
                        correct_prefix = True
                        break
                except ValueError:
                    continue
        result["cases"].append(dict(case_id=row["case_id"], official=official, reported=reported,
                                    duplicate_program=equivalent, selected_indices=indices,
                                    delivered=delivered, complete_annotated_evidence=complete_evidence,
                                    correct_prefix_of_wrong_draft=correct_prefix))
        for metric, labels in (("official", official), ("reported", reported)):
            counts = result[metric]
            counts["first_draft_correct"] += labels[0]
            counts["second_draft_correct"] += labels[1]
            counts["oracle_correct_available"] += any(labels)
            counts["correct_delivery"] += delivered is not None and labels[delivered]
            counts["wrong_delivery"] += delivered is not None and not labels[delivered]
            counts["withheld"] += delivered is None
            for order in range(2):
                selection = indices[order] if indices else None
                outcome = ("withheld" if selection is None
                           else "correct" if labels[selection] else "wrong")
                counts[f"single_order_{order + 1}_{outcome}"] += 1
    result["peak_sampled_rss"] = max(peaks)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    build = commands.add_parser("freeze")
    for name in ("source", "output"):
        build.add_argument(f"--{name}", type=Path, required=True)
    build.add_argument("--exclude", type=Path, action="append", required=True)
    build.add_argument("--exclude-cohort", type=Path, action="append", required=True)
    build.set_defaults(run=freeze)
    inference = commands.add_parser("run")
    for name in ("cli", "weights", "cohort", "output"):
        inference.add_argument(f"--{name}", type=Path, required=True)
    inference.set_defaults(run=run, one_step=False)
    report = commands.add_parser("summarize")
    for name in ("ledger", "source", "evaluator"):
        report.add_argument(f"--{name}", type=Path, required=True)
    report.set_defaults(run=summarize)
    args = parser.parse_args()
    args.run(args)
