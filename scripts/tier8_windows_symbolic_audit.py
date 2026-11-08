"""Audit exact execution versus symbolic equivalence on saved FinQA drafts."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import importlib.util
import json
from pathlib import Path

from program_graph import prune_unused
from tier8_windows_pilot import jsonl


def numeric_spelling(token):
    if token.startswith("#"):
        return token
    prefix = "const_" if token.startswith("const_") else ""
    text = token.removeprefix(prefix).replace(",", "")
    if prefix and text == "m1":
        text = "-1"
    try:
        value = Decimal(text[:-1]) / 100 if text.endswith("%") else Decimal(text)
    except InvalidOperation:
        return token
    return prefix + (format(value.normalize(), "f") if value else "0")


def normalize(tokens):
    return [numeric_spelling(token) if index % 4 in (1, 2) and token != "EOF" else token
            for index, token in enumerate(tokens)]


def program_tokens(program, constants):
    result = []
    for step in program["steps"]:
        operands = [(("const_" if constants and step[side]["span_id"] == "CONST" else "")
                     + step[side]["value"]) for side in ("left", "right")]
        result.extend([step["op"] + "(", *operands, ")"])
    return result + ["EOF"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "evaluator"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("ledgers", type=Path, nargs="+")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("finqa_evaluator", args.evaluator)
    finqa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finqa)
    gold = {row["id"]: row for row in json.loads(args.source.read_bytes())}
    result = {}
    for path in args.ledgers:
        arms = [Counter(), Counter()]
        cases = []
        for row in jsonl(path):
            label = gold[row["case_id"]]
            target = normalize(finqa.program_tokenization(label["qa"]["program"]))
            scores = []
            for draft, stats in zip(row["drafts"], arms):
                candidate = draft["candidate"]
                execution, program, sliced_program = False, False, False
                if not candidate["execution"]["issues"]:
                    original = candidate["program"]
                    raw = program_tokens(original, constants=False)
                    invalid, value = finqa.eval_program(raw, label["table"])
                    execution = not invalid and value == label["qa"]["exe_ans"]
                    sliced = prune_unused(original)
                    removed = len(original["steps"]) - len(sliced["steps"])
                    stats["with_dead_operations"] += removed > 0
                    stats["dead_operations"] += removed
                    sliced_result = finqa.eval_program(program_tokens(sliced, constants=False), label["table"])
                    if sliced_result != (invalid, value):
                        raise ValueError(f"Backward slice changed execution on {row['case_id']}")
                    equivalents = []
                    for candidate_program in (original, sliced):
                        prediction = normalize(program_tokens(candidate_program, constants=True))
                        try:
                            equivalents.append(bool(finqa.equal_program(target, prediction)))
                        except (ValueError, TypeError, KeyError, AssertionError):
                            equivalents.append(False)
                    program, sliced_program = equivalents
                stats["n"] += 1
                stats["execution_correct"] += execution
                stats["symbolic_correct"] += program
                stats["sliced_symbolic_correct"] += sliced_program
                stats["execution_only"] += execution and not program
                stats["symbolic_only"] += program and not execution
                scores.append(dict(execution=execution, symbolic=program, sliced_symbolic=sliced_program))
            cases.append(dict(case_id=row["case_id"], arms=scores))
        result[path.parent.name] = dict(arms=arms, cases=cases)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
