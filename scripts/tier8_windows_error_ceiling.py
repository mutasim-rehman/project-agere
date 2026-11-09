"""Estimate separate retrieval, representation, endpoint and scale constraints."""
import argparse
from collections import Counter
from decimal import InvalidOperation
import json
from pathlib import Path

from evidence_atoms import atom_catalog
from program_binding_domains import binding_domains
from tier8_v2_finqa import packet
from tier8_windows_challenge import official_evaluator, official_result
from tier8_windows_pilot import jsonl


def official_match(evaluate, annotation, program):
    try:
        return official_result(evaluate, annotation, program) == annotation["qa"]["exe_ans"]
    except ValueError:
        return False


def audit(ledger, gold, evaluate):
    arms = [Counter(), Counter()]
    details = []
    for row in jsonl(ledger):
        annotation = gold[row["case_id"]]
        records = []
        for index, draft in enumerate(row["drafts"]):
            stats = arms[index]
            stats["questions"] += 1
            evidence = draft.get("evidence") or packet(annotation)["evidence"]
            complete = set(annotation["qa"]["gold_inds"]) <= evidence.keys()
            stats["annotated_spans_complete"] += complete
            try:
                binding_domains(annotation["qa"]["program"], atom_catalog(evidence))
                bindable = True
            except (ValueError, InvalidOperation):
                bindable = False
            stats["reference_bindable_with_original_catalog"] += bindable
            candidate = draft["candidate"]
            program = candidate["program"]
            executable = not candidate["execution"]["issues"]
            correct, prefix, scale = False, False, []
            if executable:
                correct = official_match(evaluate, annotation, program)
                if not correct:
                    steps = program["steps"]
                    prefix = any(official_match(evaluate, annotation, {**program, "steps": steps[:n]})
                                 for n in range(1, len(steps)))
                    if annotation["qa"].get("answer", "").strip().endswith("%"):
                        for op in ("multiply", "divide"):
                            adjusted = {**program, "steps": [*steps, {"op": op,
                                "left": {"value": f"#{len(steps)-1}", "span_id": f"STEP#{len(steps)-1}"},
                                "right": {"value": "100", "span_id": "CONST"}}]}
                            if official_match(evaluate, annotation, adjusted):
                                scale.append(op)
            stats["final_correct"] += correct
            stats["wrong_final_correct_prefix"] += prefix
            stats["wrong_final_percent_scale_match"] += bool(scale)
            stats["wrong_final_prefix_or_scale_match"] += prefix or bool(scale)
            stats["final_or_endpoint_or_percent_match"] += correct or prefix or bool(scale)
            records.append(dict(complete=complete, bindable=bindable, final_correct=correct,
                                correct_prefix=prefix, gold_matching_percent_adjustments=scale))
        details.append(dict(case_id=row["case_id"], arms=records))
    return dict(arms=arms, cases=details)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "evaluator"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("ledgers", type=Path, nargs="+")
    args = parser.parse_args()
    gold = {row["id"]: row for row in json.loads(args.source.read_bytes())}
    evaluate = official_evaluator(args.evaluator)
    result = {f"{path.parent.name}/{path.name}": audit(path, gold, evaluate)
              for path in args.ledgers}
    print(json.dumps(result, indent=2))
