"""Check if a known correct FinQA program can run with each draft's input catalog."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

from evidence_atoms import atom_catalog, compile_plan
from program_binding_domains import binding_domains, resolve_domains
from program_graph import prune_unused
from tier8_v2_financial_pipeline import checked, question_units
from tier8_windows_challenge import official_evaluator
from tier8_windows_error_ceiling import official_match
from tier8_windows_pilot import jsonl


def witness(annotation, packet, atoms, evaluate):
    qa = annotation["qa"]
    try:
        domains = binding_domains(qa["program"], atoms, qa["gold_inds"])
    except InvalidOperation:
        return "unsupported_operand_spelling", None
    except ValueError as exc:
        return str(exc), None
    # Equal-valued cells are interchangeable for this numerical witness.
    # This assignment does not identify the intended source cell.
    assignment = {slot: (info["annotated_span_candidates"] or info["candidate_quantity_ids"])[0]
                  for slot, info in domains["slots"].items()}
    steps = resolve_domains(domains, assignment)
    if any(all(step[side].startswith("CONST:") for side in ("left", "right")) for step in steps):
        return "constant_only_step_outside_grammar", None
    plan = dict(decision="ANSWER", answer_unit=question_units(packet["question"], "question")[0],
                steps=steps)
    program = compile_plan(plan, atoms)
    execution = checked(program, packet["evidence"])
    if execution["issues"]:
        return execution["issues"][0]["code"], None
    if not official_match(evaluate, annotation, program):
        return "reference_does_not_match_official_label", None
    return "executable_official_match", program


def source_numbers(program):
    return {Decimal(operand["value"]) for step in program["steps"]
            for operand in (step["left"], step["right"])
            if operand["span_id"] != "CONST" and not operand["value"].startswith("#")}


def audit(rows, packets, gold, evaluate, catalogs):
    ids = [row["case_id"] for row in rows]
    if len(ids) != len(packets) or set(ids) != set(packets):
        raise ValueError("Expected one paired record per frozen report")
    arms = [Counter() for _ in catalogs]
    records = []
    for row in rows:
        case = row["case_id"]
        packet = packets[case]
        annotation = gold[case]
        if len(row["drafts"]) != len(catalogs):
            raise ValueError(f"Unexpected draft count on {case}")
        result = []
        for draft, stats, catalog in zip(row["drafts"], arms, catalogs):
            if draft.get("evidence") and draft["evidence"] != packet["evidence"]:
                raise ValueError(f"Frozen evidence differs on {case}")
            atoms = catalog(packet["evidence"])
            if "catalog_size" in draft and draft["catalog_size"] != len(atoms):
                raise ValueError(f"Catalog count differs on {case}")
            status, reference = witness(annotation, packet, atoms, evaluate)
            candidate = draft["candidate"]
            executable = not candidate["execution"]["issues"]
            program = candidate["program"]
            if executable and compile_plan(draft["plan"], atoms) != program:
                raise ValueError(f"Catalog does not reproduce the saved draft on {case}")
            correct = executable and official_match(evaluate, annotation, program)
            stats["reports"] += 1
            stats[status] += 1
            stats["generated_correct"] += correct
            missing_live, missing_any = None, None
            if reference and not correct:
                stats["witness_available_generated_wrong"] += 1
                if executable:
                    required = source_numbers(prune_unused(reference))
                    missing_live = len(required - source_numbers(prune_unused(program)))
                    missing_any = len(required - source_numbers(program))
                    stats["wrong_executable_missing_reference_number_in_final"] += missing_live > 0
                    stats["wrong_executable_missing_reference_number_anywhere"] += missing_any > 0
                    stats["wrong_executable_all_reference_numbers_in_final"] += missing_live == 0
                else:
                    stats["witness_available_generated_nonexecutable"] += 1
            result.append(dict(witness=status, executable=executable, correct=correct,
                               missing_live_reference_numbers=missing_live,
                               missing_reference_numbers_anywhere=missing_any))
        records.append(dict(case_id=case, arms=result))
    return dict(arms=arms, cases=records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "source", "evaluator", "ledger"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--expanded-second-arm", action="store_true")
    args = parser.parse_args()
    catalogs = [atom_catalog, atom_catalog]
    if args.expanded_second_arm:
        from tier8_windows_catalog_audit import load_prototype
        catalogs[1] = load_prototype()
    packets = {row["id"]: row for row in jsonl(args.cohort)}
    gold = {row["id"]: row for row in json.loads(args.source.read_bytes())}
    evaluate = official_evaluator(args.evaluator)
    print(json.dumps(audit(jsonl(args.ledger), packets, gold, evaluate, catalogs), indent=2))


if __name__ == "__main__":
    main()
