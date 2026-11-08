"""Generate and review two evidence-only FinQA candidates per report on Windows."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from math import comb
from pathlib import Path
import re
import random
from statistics import median

from evidence_atoms import atom_catalog, compile_plan, reference_schema
from evidence_contract import TokenLedger
from tier8_v2_demo_retrieval import report_group
from tier8_v2_financial_pipeline import checked, evaluate_financial, question_units
from tier8_v2_finqa import packet
from tier8_windows_challenge import official_evaluator, official_result
from tier8_windows_pilot import Models, jsonl


def freeze(args):
    if args.count < 1:
        raise ValueError("Cohort count must be positive")
    excluded = {report_group(row["id"]) for path in args.exclude
                for row in json.loads(path.read_text(encoding="utf-8"))}
    for path in args.exclude_cohort:
        excluded.update(row["report_group"] for row in jsonl(path))
    for path in args.exclude_records:
        for row in jsonl(path):
            group = row.get("report_group")
            if group is None:
                identity = row.get("id") or row.get("case_id")
                if not identity or "/" not in identity:
                    raise ValueError(f"Cannot identify FinQA report in {path}")
                group = report_group(identity)
            excluded.add(group)
    source = json.loads(args.source.read_text(encoding="utf-8"))
    if args.include_ids:
        include = set(json.loads(args.include_ids.read_text(encoding="utf-8")))
        source = [row for row in source if row["id"] in include]
    source.sort(key=lambda row: hashlib.sha256(("windows-natural-v1|" + row["id"]).encode()).digest())
    selected = []
    for row in source:
        group = report_group(row["id"])
        if group in excluded:
            continue
        public = packet(row)
        if not atom_catalog(public["evidence"]):
            continue
        selected.append({**public, "report_group": group})
        excluded.add(group)
        if len(selected) == args.count:
            break
    if len(selected) != args.count:
        raise ValueError(f"Only {len(selected)} eligible reports for a {args.count}-report cohort")
    with args.output.open("x", encoding="utf-8") as out:
        for public in selected:
            out.write(json.dumps(public) + "\n")
            print(public["id"], flush=True)


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
    if args.capacity_control and not args.adapter:
        raise ValueError("Capacity comparison requires the matched 3B adapter")
    if args.planned_length and (not args.adapter or args.capacity_control):
        raise ValueError("Length planning requires the adapter and excludes capacity control")
    if args.retrieval_cohort and (not args.adapter or args.capacity_control or args.planned_length):
        raise ValueError("Retrieval comparison requires an adapter and no other intervention")
    if args.precision_control and (args.adapter or args.capacity_control or args.planned_length
                                   or args.retrieval_cohort or args.complete_catalog):
        raise ValueError("Matched precision comparison uses only its two base checkpoints")
    if args.complete_catalog and (not args.adapter or args.capacity_control or args.planned_length
                                  or args.retrieval_cohort):
        raise ValueError("Catalog comparison requires an adapter and no other intervention")
    if args.oracle_lengths and (not args.adapter or args.capacity_control or args.planned_length
                                or args.retrieval_cohort or args.precision_control or args.complete_catalog):
        raise ValueError("Oracle-length diagnostic requires only the adapted model")
    if args.complete_catalog:
        from tier8_windows_catalog_audit import load_prototype
        expanded_catalog = load_prototype()
    model = Models(args)
    public = jsonl(args.cohort)
    if not public or len({case["report_group"] for case in public}) != len(public):
        raise ValueError("Expected one question per report")
    oracle = json.loads(args.oracle_lengths.read_bytes()) if args.oracle_lengths else {}
    if args.oracle_lengths and set(oracle) != {case["id"] for case in public}:
        raise ValueError("Oracle length diagnostic must cover the entire frozen cohort")
    alternative = {case["id"]: case for case in jsonl(args.retrieval_cohort)} if args.retrieval_cohort else {}
    if args.retrieval_cohort and set(alternative) != {case["id"] for case in public}:
        raise ValueError("Retrieval case IDs differ")
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "cases.jsonl").open("x", encoding="utf-8") as out:
        for case_index, case in enumerate(public):
            budget = TokenLedger()
            drafts = [None, None]
            shortest = ("Use the shortest calculation that fully answers the question."
                        " Stop once the requested quantity is computed.")
            matched = args.adapter or args.precision_control
            instructions = (shortest, shortest) if matched else (
                "Check that the final operation answers the exact question.", shortest)
            order = (1, 0) if matched and case_index % 2 else (0, 1)
            for index in order:
                current = alternative[case["id"]] if index == 1 and alternative else case
                if current["question"] != case["question"]:
                    raise ValueError("Retrieval variant changed the question")
                evidence = current["evidence"]
                context = ("Question: " + case["question"] + "\nFinancial report evidence by source ID:\n"
                           + json.dumps(evidence))
                atoms = expanded_catalog(evidence) if args.complete_catalog and index == 1 else atom_catalog(evidence)
                units = question_units(case["question"], "question")
                catalog = "\n".join(f"{key}={atom['value']}@{atom['span_id']}" for key, atom in atoms.items())
                prompt = (context + "\nQuantity references:\n" + catalog
                          + "\nReturn an arithmetic program with decision ANSWER, answer_unit, and steps."
                            " Use catalog IDs as operands, CONST:value for permitted constants, and #0, #1"
                            " for earlier results. The last step gives the requested answer."
                            " Percent means percentage points and fraction means a dimensionless ratio."
                          + "\nAllowed units: " + ", ".join(units))
                model.forced = True
                use_adapter = (args.planned_length or args.retrieval_cohort or args.complete_catalog
                               or args.oracle_lengths or index == int(not args.capacity_control))
                model.adapter = args.adapter if use_adapter else None
                model.drafter_weights = (str(args.precision_control[index].resolve())
                                         if args.precision_control else
                                         args.capacity_control if index == 1 else None)
                schema = reference_schema(atoms, units, causal=True)
                planner_event, steps = None, None
                limit = 768
                if args.planned_length and index == 1:
                    count_schema = {"type": "object", "properties": {"steps": {"enum": list(range(1, 9))}},
                                    "required": ["steps"], "additionalProperties": False}
                    selection, planner_event = model.call(
                        "drafter", context + "\nHow many primitive arithmetic operations are necessary"
                        " to compute the requested quantity? Count add, subtract, multiply and divide,"
                        " including any necessary scale conversion. Retrieving or reading a source value"
                        " does not count. Choose the smallest sufficient operation count from 1 to 8.",
                        count_schema, budget, 96, "length_plan")
                    steps = (selection or {}).get("steps")
                    limit -= 96
                elif oracle and index == 1:
                    steps = oracle[case["id"]]
                if type(steps) is int and 1 <= steps <= 8:
                    lengths = schema["oneOf"][0]["properties"]["steps"]["oneOf"]
                    lengths[:] = [lengths[steps - 1]]
                plan, event = model.call("drafter", prompt + "\n" + instructions[index],
                                         schema, budget, limit, "program")
                try:
                    program = compile_plan(plan, atoms)
                except (ValueError, TypeError, AttributeError):
                    program = None
                execution = checked(program, evidence)
                drafts[index] = dict(plan=plan, candidate=dict(program=program, execution=execution),
                                     adapter_applied=model.adapter is not None,
                                     weights_override=model.drafter_weights, event=event,
                                     planned_steps=steps, planner_event=planner_event,
                                     catalog_size=len(atoms),
                                     evidence=evidence if alternative else None)
            model.adapter = None
            model.drafter_weights = None
            executable = all(not draft["candidate"]["execution"]["issues"] for draft in drafts)
            review_enabled = not (args.capacity_control or args.planned_length
                                  or args.retrieval_cohort or args.precision_control or args.complete_catalog
                                  or args.oracle_lengths)
            reviews = review(model, context, drafts, budget) if executable and review_enabled else []
            out.write(json.dumps(dict(case_id=case["id"], drafts=drafts, reviews=reviews,
                                      review_enabled=review_enabled,
                                      oracle_diagnostic=bool(args.oracle_lengths),
                                      reserved_tokens=budget.spent)) + "\n")
            out.flush()
            print(case["id"], [draft["candidate"]["execution"]["value"] for draft in drafts],
                  [review["choice"] for review in reviews], flush=True)


def summarize(args):
    rows = jsonl(args.ledger)
    ids = {row["case_id"] for row in rows}
    if not rows or len(ids) != len(rows):
        raise ValueError("Expected distinct completed questions")
    if args.cohort and ids != {row["id"] for row in jsonl(args.cohort)}:
        raise ValueError("Completed question IDs differ from frozen cohort")
    evaluate = official_evaluator(args.evaluator)
    gold = {row["id"]: row for row in json.loads(args.source.read_text(encoding="utf-8"))}
    result = dict(questions=len(rows), official=Counter(), reported=Counter(), cases=[])
    peaks = []
    for row in rows:
        annotation = gold[row["case_id"]]
        evidence = packet(annotation)["evidence"]
        annotated = set(annotation["qa"]["gold_inds"])
        complete_evidence = annotated <= evidence.keys()
        candidates = [draft["candidate"] for draft in row["drafts"]]
        peaks.extend(item["event"]["peak_sampled_rss"] for item in row["drafts"] + row["reviews"])
        peaks.extend(draft["planner_event"]["peak_sampled_rss"] for draft in row["drafts"]
                     if draft.get("planner_event"))
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
        correct_prefix_lengths = [[], []]
        for index, (candidate, correct) in enumerate(zip(candidates, official)):
            program = candidate["program"]
            if correct or not program:
                continue
            for length in range(1, len(program["steps"])):
                prefix = {**program, "steps": program["steps"][:length]}
                candidate_evidence = row["drafts"][index].get("evidence") or evidence
                if checked(prefix, candidate_evidence)["issues"]:
                    continue
                try:
                    if official_result(evaluate, annotation, prefix) == annotation["qa"]["exe_ans"]:
                        correct_prefix_lengths[index].append(length)
                except ValueError:
                    continue
        result["cases"].append(dict(case_id=row["case_id"], official=official, reported=reported,
                                    annotated_steps=len(re.findall(r"\b[a-z_]+\(", annotation["qa"]["program"])),
                                    planned_steps=[draft.get("planned_steps") for draft in row["drafts"]],
                                    duplicate_program=equivalent, selected_indices=indices,
                                    delivered=delivered, complete_annotated_evidence=complete_evidence,
                                    per_arm_complete_evidence=[
                                        annotated <= (draft.get("evidence") or evidence).keys()
                                        for draft in row["drafts"]],
                                    correct_prefix_of_wrong_draft=any(correct_prefix_lengths),
                                    correct_prefix_lengths=correct_prefix_lengths))
        for metric, labels in (("official", official), ("reported", reported)):
            counts = result[metric]
            counts["first_draft_correct"] += labels[0]
            counts["second_draft_correct"] += labels[1]
            counts["first_only_correct"] += labels[0] and not labels[1]
            counts["second_only_correct"] += labels[1] and not labels[0]
            counts["oracle_correct_available"] += any(labels)
            if not row.get("review_enabled", True):
                continue
            counts["correct_delivery"] += delivered is not None and labels[delivered]
            counts["wrong_delivery"] += delivered is not None and not labels[delivered]
            counts["withheld"] += delivered is None
            for order in range(2):
                selection = indices[order] if indices else None
                outcome = ("withheld" if selection is None
                           else "correct" if labels[selection] else "wrong")
                counts[f"single_order_{order + 1}_{outcome}"] += 1
    result["peak_sampled_rss"] = max(peaks)
    result["draft_resources"] = []
    for index in range(2):
        drafts = [row["drafts"][index] for row in rows]
        events = [event for draft in drafts
                  for event in (draft["event"], draft.get("planner_event")) if event]
        commit_peaks = [event["peak_job_commit"] for event in events
                        if event.get("peak_job_commit") is not None]
        prompt_tokens = [event["prompt_eval_tokens"] for event in events
                         if event.get("prompt_eval_tokens") is not None]
        decode_runs = [event["decode_eval_runs"] for event in events
                       if event.get("decode_eval_runs") is not None]
        host_available = [event["host_available_min_sampled"] for event in events
                          if event.get("host_available_min_sampled") is not None]
        result["draft_resources"].append(dict(
            executable=sum(not draft["candidate"]["execution"]["issues"] for draft in drafts),
            median_steps=median(len((draft["plan"] or {}).get("steps", [])) for draft in drafts),
            median_seconds=median(draft["event"]["elapsed_seconds"] +
                                  (draft.get("planner_event") or {}).get("elapsed_seconds", 0) for draft in drafts),
            peak_sampled_rss=max(event["peak_sampled_rss"] for event in events),
            peak_job_commit=max(commit_peaks, default=None),
            min_host_available_sampled=min(host_available, default=None),
            prompt_eval_tokens=sum(prompt_tokens) if len(prompt_tokens) == len(events) else None,
            decode_eval_runs=sum(decode_runs) if len(decode_runs) == len(events) else None))
    for metric in ("official", "reported"):
        stats = result[metric]
        gains = stats["second_only_correct"]
        losses = stats["first_only_correct"]
        discordant = gains + losses
        stats["paired_accuracy_delta"] = (gains - losses) / len(rows)
        stats["exact_mcnemar_p"] = min(1, 2 * sum(
            comb(discordant, i) for i in range(min(gains, losses) + 1)) / 2 ** discordant)
        companies = defaultdict(list)
        for case in result["cases"]:
            first, second = case[metric]
            companies[case["case_id"].split("/", 1)[0]].append(int(second) - int(first))
        groups = [(sum(deltas), len(deltas)) for deltas in companies.values()]
        rng = random.Random(42)
        replicates = []
        for _ in range(2000):
            sample = rng.choices(groups, k=len(groups))
            replicates.append(sum(delta for delta, _ in sample) / sum(n for _, n in sample))
        replicates.sort()
        stats["companies"] = len(groups)
        stats["company_cluster_delta_95"] = [replicates[50], replicates[1949]]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    build = commands.add_parser("freeze")
    for name in ("source", "output"):
        build.add_argument(f"--{name}", type=Path, required=True)
    build.add_argument("--exclude", type=Path, action="append", required=True)
    build.add_argument("--exclude-cohort", type=Path, action="append", required=True)
    build.add_argument("--exclude-records", type=Path, action="append", default=[])
    build.add_argument("--count", type=int, default=6)
    build.add_argument("--include-ids", type=Path,
                       help="Limit the cohort to named IDs for an explicitly enriched diagnostic")
    build.set_defaults(run=freeze)
    inference = commands.add_parser("run")
    for name in ("cli", "weights", "cohort", "output"):
        inference.add_argument(f"--{name}", type=Path, required=True)
    inference.add_argument("--adapter", type=Path,
                           help="Compare base vs. adapted under the same prompt")
    inference.add_argument("--capacity-control",
                           help="Compare adapted 3B vs. this larger GGUF filename, without review")
    inference.add_argument("--planned-length", action="store_true",
                           help="Compare adapted drafting with and without a separate length prediction")
    inference.add_argument("--retrieval-cohort", type=Path,
                           help="Compare the same adapted drafter under alternate evidence packets")
    inference.add_argument("--precision-control", type=Path, nargs=2,
                           help="Compare two GGUF quantizations of the same base checkpoint")
    inference.add_argument("--job-commit-limit", type=int)
    inference.add_argument("--complete-catalog", action="store_true",
                           help="Compare original and span-complete source quantity catalogs")
    inference.add_argument("--oracle-lengths", type=Path,
                           help="Gold-informed diagnostic only: compare against exact annotated lengths")
    inference.set_defaults(run=run, one_step=False)
    report = commands.add_parser("summarize")
    for name in ("ledger", "source", "evaluator"):
        report.add_argument(f"--{name}", type=Path, required=True)
    report.add_argument("--cohort", type=Path)
    report.set_defaults(run=summarize)
    args = parser.parse_args()
    args.run(args)
