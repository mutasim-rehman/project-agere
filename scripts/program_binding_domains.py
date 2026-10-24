"""Retain underdetermined source identities in value-annotated programs.

Numerical labels do not identify a source cell when several cells have the same
value. Annotated source spans are recorded as hints, not trusted tie breakers.
Distinct ambiguous occurrences are NOT asserted independent; their candidate
domains may alias. This representation is not a resolved training target.
"""
from decimal import Decimal
import re

from evidence_calculator import CONSTANTS, OPERATIONS


def binding_domains(program, atoms, annotated_spans=()):
    if not isinstance(program, str):
        raise ValueError("program_must_be_text")
    matches = list(re.finditer(r"([a-z_]+)\(([^,]+),\s*([^\)]+)\)", program))
    if not 1 <= len(matches) <= 8:
        raise ValueError("unsupported_program_length")
    cursor = 0
    steps, slots, unique_cells = [], {}, {}
    hints = set(annotated_spans)
    for index, match in enumerate(matches):
        separator = program[cursor:match.start()].strip()
        if (index == 0 and separator) or (index > 0 and separator != ","):
            raise ValueError("unparsed_program_text")
        cursor = match.end()
        op, left, right = match.groups()
        if op not in OPERATIONS:
            raise ValueError("unsupported_operation")
        step = {"op": op}
        for side, raw in (("left", left.strip()), ("right", right.strip())):
            if re.fullmatch(r"#\d+", raw):
                if int(raw[1:]) >= index:
                    raise ValueError("noncausal_reference")
                step[side] = raw
                continue
            value = Decimal(raw.removeprefix("const_").replace("m1", "-1"))
            if not value.is_finite():
                raise ValueError("nonfinite_operand")
            if raw.startswith("const_"):
                if value not in CONSTANTS:
                    raise ValueError("unsupported_constant")
                step[side] = "CONST:" + str(int(value))
                continue
            candidates = sorted(key for key, atom in atoms.items() if Decimal(atom["value"]) == value)
            if not candidates:
                raise ValueError("unretrieved_operand")
            key = unique_cells.get(candidates[0]) if len(candidates) == 1 else None
            if key is None:
                key = f"V{len(slots)}"
                slots[key] = {"value": str(value), "candidate_quantity_ids": candidates,
                              "annotated_span_candidates": [k for k in candidates if atoms[k]["span_id"] in hints],
                              "numeric_identity_unique": len(candidates) == 1, "occurrences": []}
                if len(candidates) == 1:
                    unique_cells[candidates[0]] = key
            slots[key]["occurrences"].append({"step": index, "side": side})
            step[side] = key
        steps.append(step)
    if program[cursor:].strip() not in ("", ","):
        raise ValueError("unparsed_program_text")
    unique = bool(slots) and all(slot["numeric_identity_unique"] for slot in slots.values())
    resolved = None
    if unique:
        resolved = [{key: slots[value]["candidate_quantity_ids"][0] if key in ("left", "right") and value in slots else value
                     for key, value in step.items()} for step in steps]
    return {"steps": steps, "slots": slots, "numeric_binding_unique": unique, "resolved_steps": resolved,
            "caution": "Ambiguous occurrences may share or differ in source identity; no independence or semantic correctness is certified."}


def resolve_domains(partial, assignment):
    """Require an explicit admissible cell assignment; never select a first match.

    This checks domain membership, not whether the assignment matches the question.
    """
    if not isinstance(assignment, dict) or set(assignment) != set(partial["slots"]):
        raise ValueError("Every source slot needs an explicit assignment")
    if any(ref not in partial["slots"][key]["candidate_quantity_ids"] for key, ref in assignment.items()):
        raise ValueError("Assignment is outside the source candidate domain")
    return [{key: assignment[value] if key in ("left", "right") and value in assignment else value
             for key, value in step.items()} for step in partial["steps"]]
