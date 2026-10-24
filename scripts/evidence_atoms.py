"""Source-pointer program baseline: models select quantities, code copies values.

Copying input quantities is established numerical-QA practice, not a novelty claim.
References prove provenance only; relevance and operation choice remain fallible.
"""
from copy import deepcopy
from decimal import Decimal
import re

from evidence_calculator import CONSTANTS, NUMBER_TOKEN, execute


def atom_catalog(evidence):
    atoms = {}
    for span, text in evidence.items():
        clauses = text.split(" ; ") if span.startswith("table_") else [text]
        for clause in clauses:
            content = clause.rsplit(": ", 1)[-1] if span.startswith("table_") else clause
            normalized = re.sub(r"(?<=\d),(?=\d)", "", content)
            normalized = re.sub(r"\((\d[\d.]*)\)", r"-\1", normalized)
            for match in re.finditer(NUMBER_TOKEN, normalized):
                number = Decimal(match[0])
                if not number.is_finite():
                    continue
                key = f"A{len(atoms):03d}"
                context = (clauses[0] + " | " + clause) if len(clauses) > 1 and clause != clauses[0] else clause
                atoms[key] = {"value": str(number), "span_id": span, "context": context}
    return atoms


def reference_schema(atoms, units=("number", "percent", "fraction")):
    references = list(atoms) + [f"CONST:{n}" for n in sorted(CONSTANTS)] + [f"#{i}" for i in range(8)]
    step = {"type": "object", "properties": {"op": {"enum": ["add", "subtract", "multiply", "divide"]},
        "left": {"enum": references}, "right": {"enum": references}},
        "required": ["op", "left", "right"], "additionalProperties": False}
    return {"type": "object", "properties": {"decision": {"enum": ["ANSWER", "INSUFFICIENT"]},
        "answer_unit": {"enum": list(units)}, "steps": {"type": "array", "items": step, "minItems": 0, "maxItems": 8}},
        "required": ["decision", "answer_unit", "steps"], "additionalProperties": False}


def compile_plan(plan, atoms):
    if not isinstance(plan, dict) or not isinstance(plan.get("steps"), list):
        raise ValueError("Reference plan schema")
    result = deepcopy(plan)
    for step in result["steps"]:
        if not isinstance(step, dict) or set(step) != {"op", "left", "right"}:
            raise ValueError("Reference step schema")
        for side in ("left", "right"):
            ref = step[side]
            if not isinstance(ref, str):
                raise ValueError("Reference must be a string")
            if ref in atoms:
                step[side] = {k: atoms[ref][k] for k in ("value", "span_id")}
            elif re.fullmatch(r"#\d+", ref):
                step[side] = {"value": ref, "span_id": "STEP" + ref}
            elif ref.startswith("CONST:") and ref[6:] in {str(n) for n in CONSTANTS}:
                step[side] = {"value": ref[6:], "span_id": "CONST"}
            else:
                raise ValueError(f"Unknown source reference: {ref}")
    return result


def patch_plan(plan, updates, allowed, atoms, evidence):
    original = deepcopy(plan)
    if not isinstance(plan, dict) or not isinstance(plan.get("steps"), list) or not isinstance(updates, dict):
        return original, False
    changes = updates.get("updates")
    if not isinstance(changes, list) or not changes:
        return original, False
    indices = [c.get("index") for c in changes if isinstance(c, dict)]
    if len(indices) != len(changes) or any(type(i) is not int for i in indices) or len(set(indices)) != len(indices):
        return original, False
    if not set(indices) <= allowed or any(not 0 <= i < len(plan["steps"]) for i in indices):
        return original, False
    candidate = deepcopy(plan)
    for change in changes:
        if set(change) != {"index", "step"}:
            return original, False
        candidate["steps"][change["index"]] = deepcopy(change["step"])
    try:
        compiled = compile_plan(candidate, atoms)
    except ValueError:
        return original, False
    if compiled.get("decision") != "ANSWER" or execute(compiled["steps"], evidence)["issues"]:
        return original, False
    return candidate, True
