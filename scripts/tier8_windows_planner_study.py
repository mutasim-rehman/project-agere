"""Score the four-arm held-out Windows planner study after inference."""
import argparse
import ast
from collections import Counter
import importlib
import json
from math import comb
from pathlib import Path
import random
import re
from statistics import median
import sys

from tier8_windows_pilot import CAP, jsonl
from tier8_windows_tatqa import normalize_prediction


OPERATORS = {ast.Add: "add", ast.Sub: "subtract", ast.Mult: "multiply", ast.Div: "divide"}


def node(op, left, right):
    if op in ("add", "multiply"):
        left, right = sorted((left, right))
    return (op, left, right)


def reference_tree(derivation):
    """Keep only a parseable binary operator tree. Ignore numeric leaf identity."""
    def visit(value):
        if isinstance(value, ast.Constant) and type(value.value) in (int, float):
            return ("quantity",)
        if isinstance(value, ast.UnaryOp) and isinstance(value.op, (ast.UAdd, ast.USub)):
            if isinstance(value.operand, ast.Constant):
                return visit(value.operand)
        if isinstance(value, ast.BinOp) and type(value.op) in OPERATORS:
            return node(OPERATORS[type(value.op)], visit(value.left), visit(value.right))
        raise ValueError("Unsupported derivation")

    text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", derivation).strip()
    text = text.translate(str.maketrans({"[": "(", "]": ")", "×": "*", "÷": "/", "−": "-"}))
    text = re.sub(r"(?<=\d)%", "", text)
    try:
        root = ast.parse(text, mode="eval").body
        return visit(root) if isinstance(root, ast.BinOp) else None
    except (SyntaxError, ValueError):
        return None


def program_tree(program):
    nodes = []
    for step in program["steps"]:
        operands = []
        for side in ("left", "right"):
            value = step[side]["value"]
            operands.append(nodes[int(value[1:])] if value.startswith("#") else ("quantity",))
        nodes.append(node(step["op"], *operands))
    return nodes[-1]


def candidate(program, execution):
    if not program or execution["issues"]:
        return None
    return normalize_prediction(execution["value"], program["answer_unit"])


def scores(metric, label, prediction):
    if prediction is None:
        return False, 0.0
    scorer = metric.TaTQAEmAndF1()
    scorer(label, [prediction["answer"]], pred_scale=prediction["scale"])
    exact, f1, _, _ = scorer.get_overall_metric()
    return bool(exact), f1


def resource_summary(times, commits, rss, generated, decode_runs):
    return dict(median_seconds=median(times), peak_job_commit=max(commits),
                peak_sampled_rss=max(rss), generated_tokens=generated, decode_eval_runs=decode_runs)


def paired(first, second):
    gains = sum(not a and b for a, b in zip(first, second))
    losses = sum(a and not b for a, b in zip(first, second))
    discordance = gains + losses
    p = min(1.0, 2 * sum(comb(discordance, k) for k in range(min(gains, losses) + 1)) / 2**discordance)
    differences = [int(b) - int(a) for a, b in zip(first, second)]
    rng = random.Random(73)
    replicates = sorted(sum(rng.choices(differences, k=len(differences))) / len(differences)
                        for _ in range(10000))
    return dict(gains=gains, losses=losses, rate_delta=sum(differences) / len(differences),
                paired_context_bootstrap_95=[replicates[250], replicates[9749]], exact_mcnemar_p=p)


def read_arms(args):
    ids = [row["id"] for row in jsonl(args.cohort)]
    if len(set(ids)) != len(ids) or not ids:
        raise ValueError("Expected unique frozen cases")
    ledgers = [jsonl(path) for path in (args.large, args.mas, args.planner)]
    if any([row["case_id"] for row in ledger] != ids for ledger in ledgers):
        raise ValueError("Each ledger must exactly reproduce the frozen cohort order")
    resources = [json.loads(path.read_bytes()) for path in (args.mas_resources, args.planner_resources)]
    for r in resources:
        if (r["status"] != "completed" or r["sampled_rss_breached"]
                or r["peak_sampled_rss"] > CAP or r["peak_worker_job_commit"] > 6_100_000_000
                or not r["prompt_cache_ram_disabled"]):
            raise ValueError("Resident run did not satisfy the frozen resource checks")
    return zip(*ledgers), resources


def summarize(args):
    sys.path.insert(0, str(args.metric_directory.resolve()))
    metric = importlib.import_module("tatqa_metric")
    gold = {q["uid"]: q for item in json.loads(args.source.read_bytes()) for q in item["questions"]}
    arms = ("direct7b", "program7b", "mas", "planner_mas")
    counts = {arm: Counter() for arm in arms}
    event_lists = {arm: [] for arm in arms}
    rows, resident = read_arms(args)
    cases = []
    for large, mas, planned in rows:
        case = large["case_id"]
        label = gold[case]
        reference = reference_tree(label["derivation"])
        results = {}
        for name, key in zip(arms[:2], ("direct_large", "program")):
            record = large["arms"][key]
            event = record["event"]
            if (event["token_ceiling"] != 960 or event["job_commit_limit"] != 6_100_000_000
                    or event["peak_job_commit"] > 6_100_000_000 or event["peak_sampled_rss"] > CAP):
                raise ValueError(f"Invalid 7B budget or resource trace on {case}")
            pred = record["prediction"]
            results[name] = (pred, pred, record.get("candidate", {}).get("program"))
            event_lists[name].append([event])
        for name, mode, row in zip(arms[2:], ("direct", "shape"), (mas, planned)):
            stages = row["stages"]
            expected = [768, 192] if mode == "direct" else [192, 576, 192]
            if (row["task"] != "tatqa" or row["planner"] != mode or row["tokens"] > 960
                    or [stage["token_ceiling"] for stage in stages] != expected
                    or row["tokens"] != sum(stage["generated_tokens"] for stage in stages)):
                raise ValueError(f"Invalid MAS configuration or budget on {case}")
            pred = candidate(row["initial_answer"], row["initial_execution"])
            results[name] = (pred, pred if row["delivered"] else None, row["initial_answer"])
            event_lists[name].append(stages)
        labels = {}
        for name, (draft, delivered, program) in results.items():
            candidate_correct, _ = scores(metric, label, draft)
            correct, f1 = scores(metric, label, delivered)
            shape_match = (program_tree(program) == reference
                           if reference and draft is not None and program else None)
            outcome = "withheld" if delivered is None else "correct" if correct else "wrong"
            counts[name].update({outcome: 1, "candidate_correct": candidate_correct,
                                 "candidate_valid": draft is not None,
                                 "f1_sum": f1, "shape_matches": shape_match is True})
            labels[name] = dict(candidate_correct=candidate_correct, outcome=outcome,
                                reference_shape_match=shape_match)
        cases.append(dict(case_id=case, reference_shape_available=reference is not None,
                          planner_shape_used=planned["shape_used"], arms=labels))
    resources = {}
    for index, name in enumerate(arms):
        event_groups = event_lists[name]
        events = [event for group in event_groups for event in group]
        times = [sum(stage["elapsed_seconds"] for stage in group) for group in event_groups]
        if index < 2:
            commits = [e["peak_job_commit"] for e in events]
            rss = [e["peak_sampled_rss"] for e in events]
            generated, decoded = None, sum(e["decode_eval_runs"] or 0 for e in events)
        else:
            resource = resident[index - 2]
            commits, rss = [resource["peak_worker_job_commit"]], [resource["peak_sampled_rss"]]
            generated, decoded = sum(e["generated_tokens"] for e in events), None
        resources[name] = resource_summary(times, commits, rss, generated, decoded)
    contrasts = {}
    for baseline in ("mas", "direct7b", "program7b"):
        contrasts[baseline] = {}
        for outcome in ("correct", "wrong", "candidate_correct", "shape_match"):
            if outcome == "shape_match" and baseline == "direct7b":
                continue
            def indicator(row, arm):
                label = row["arms"][arm]
                if outcome == "candidate_correct":
                    return label[outcome]
                if outcome == "shape_match":
                    return label["reference_shape_match"] is True
                return label["outcome"] == outcome
            included = [row for row in cases if outcome != "shape_match" or row["reference_shape_available"]]
            if included:
                contrasts[baseline][outcome] = paired(
                    [indicator(row, baseline) for row in included],
                    [indicator(row, "planner_mas") for row in included])
    print(json.dumps(dict(contexts=len(cases), counts=counts, resources=resources,
                          reference_shapes=sum(c["reference_shape_available"] for c in cases),
                          planner_shape_used=sum(c["planner_shape_used"] for c in cases),
                          planner_contrasts=contrasts, cases=cases), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "cohort", "metric-directory", "large", "mas", "mas-resources",
                 "planner", "planner-resources"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    summarize(parser.parse_args())
