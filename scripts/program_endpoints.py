"""Bounded answer-endpoint alternatives for executable cited programs.

Selecting a prefix can remove a harmful trailing calculation; it cannot repair
wrong quantities or operations inside that prefix. KEEP is always available.
No labels, expected answers, training targets or neural decisions enter here.
"""
from copy import deepcopy
import json

from evidence_calculator import execute


def endpoint_candidates(answer, evidence):
    if (not isinstance(answer, dict) or set(answer) != {"decision", "answer_unit", "steps"}
            or answer["decision"] != "ANSWER"
            or answer["answer_unit"] not in ("number", "fraction", "percent")):
        return []
    execution = execute(answer["steps"], evidence)
    if execution["issues"]:
        return []
    count = len(answer["steps"])
    candidates = [{"id": "KEEP", "answer": deepcopy(answer), "execution": execution, "edit": None}]
    for length in range(1, count):
        candidate = deepcopy(answer)
        candidate["steps"] = candidate["steps"][:length]
        result = execute(candidate["steps"], evidence)
        if result["issues"]:
            continue
        # Keep equal-valued alternatives: source lineage can differ even when
        # numerical values happen to coincide. Equality does not prove relevance.
        candidates.append({"id": f"P{length:03d}", "answer": candidate, "execution": result,
            "edit": {"kind": "answer_endpoint", "before": count - 1, "after": length - 1,
                     "dropped_steps": list(range(length, count))}})
    return candidates


def select_endpoint(answer, candidates, candidate_id):
    """Apply only an exactly preserved prefix; fail closed on tampered candidates."""
    selected = next((c for c in candidates if c["id"] == candidate_id), None)
    if not selected:
        return deepcopy(answer), False
    if selected["id"] == "KEEP":
        if selected["answer"] != answer or selected["edit"] is not None:
            raise ValueError("KEEP candidate changed the answer")
        return deepcopy(answer), False
    edit = selected["edit"]
    if not isinstance(edit, dict) or edit.get("kind") != "answer_endpoint" or type(edit.get("after")) is not int:
        raise ValueError("Invalid endpoint edit")
    length = edit["after"] + 1
    if (not 1 <= length < len(answer["steps"]) or edit.get("before") != len(answer["steps"]) - 1
            or edit.get("dropped_steps") != list(range(length, len(answer["steps"])))):
        raise ValueError("Endpoint edit exceeds its declared scope")
    expected = deepcopy(answer)
    expected["steps"] = expected["steps"][:length]
    if selected["answer"] != expected:
        raise ValueError("Endpoint candidate changed retained computation or units")
    return expected, True


def choose_endpoint(answer, evidence, question, choose):
    """Choose via a caller-budgeted model callback; never infer correctness here.

    The deployment caller must reverify any changed answer and account for the
    choice and verification in its shared token ledger. This helper only limits
    what can change. It never treats a chosen prefix as a certified answer.
    """
    candidates = endpoint_candidates(answer, evidence)
    menu = [{"id": c["id"], "conditional_value": c["execution"]["value"], "edit": c["edit"]} for c in candidates]
    trace = {"attempted": len(candidates) > 1, "candidates": menu,
             "selection": None, "accepted": False, "gold_used": False}
    if len(candidates) <= 1:
        return deepcopy(answer), trace
    prompt = ("Question: " + question + "\nFinancial source evidence:\n" + json.dumps(evidence)
        + "\nOriginal cited program:\n" + json.dumps(answer)
        + "\nAlternative answer endpoints (hypothetical results, not asserted answers):\n" + json.dumps(menu)
        + "\nSelect the endpoint whose retained calculation answers the question in the ORIGINAL declared unit. "
          "Check the requested measure, entity, year, denominator and scaling against the source. "
          "KEEP retains the complete original program. An earlier endpoint removes all later steps. "
          "Do not remove a necessary operation or select a result merely because the number looks plausible. "
          "Choose KEEP if the full calculation is appropriate or no earlier endpoint is a justified improvement. "
          "Return candidate_id.")
    schema = {"type": "object", "properties": {"candidate_id": {"enum": [c["id"] for c in candidates]}},
              "required": ["candidate_id"], "additionalProperties": False}
    selection = choose(prompt, schema)
    trace["selection"] = selection
    candidate_id = selection.get("candidate_id") if isinstance(selection, dict) else None
    result, accepted = select_endpoint(answer, candidates, candidate_id)
    trace["accepted"] = accepted
    return result, trace
