"""Dataflow diagnostics for bounded financial programs; no gold or model access.

Unused intermediates are repair hints, not proof of a semantic error. Pruning them
is a semantics-preserving baseline and cannot itself fix an incorrect answer.
"""
from copy import deepcopy
from decimal import Decimal
import re
from evidence_calculator import execute


def dependencies(steps):
    if not isinstance(steps, list) or not steps:
        return []
    result = []
    for i, step in enumerate(steps):
        parents = set()
        if not isinstance(step, dict):
            raise ValueError("Invalid step")
        for side in ("left", "right"):
            operand = step[side]
            ref = operand.get("value") if isinstance(operand, dict) else operand
            if isinstance(ref, str) and ref.startswith("#"):
                if not re.fullmatch(r"#\d+", ref) or int(ref[1:]) >= i:
                    raise ValueError("Noncausal dependency")
                parents.add(int(ref[1:]))
        result.append(parents)
    return result


def audit_graph(steps):
    parents = dependencies(steps)
    if not parents:
        return {"steps": 0, "answer_ancestors": [], "unused_steps": [], "repair_hints": []}
    reachable, pending = set(), [len(steps) - 1]
    while pending:
        node = pending.pop()
        if node not in reachable:
            reachable.add(node)
            pending.extend(parents[node])
    unused = sorted(set(range(len(steps))) - reachable)
    hints = []
    for orphan in unused:
        # Only later live nodes can legally consume this intermediate.
        consumers = [i for i in sorted(reachable) if i > orphan]
        hints.append({"unused_step": orphan, "possible_consumer_steps": consumers,
                      "caution": "Check intended formula; do not assume unused work belongs in the answer."})
    return {"steps": len(steps), "answer_ancestors": sorted(reachable), "unused_steps": unused,
            "repair_hints": hints}


def prune_unused(plan):
    """For executable pure programs, remove dead steps without changing the value."""
    result = deepcopy(plan)
    steps = result.get("steps")
    live = audit_graph(steps)["answer_ancestors"]
    if not live:
        return result
    mapping = {old: new for new, old in enumerate(live)}
    kept = []
    for old in live:
        step = deepcopy(steps[old])
        for side in ("left", "right"):
            operand = step[side]
            ref = operand.get("value") if isinstance(operand, dict) else operand
            if isinstance(ref, str) and ref.startswith("#"):
                replacement = f"#{mapping[int(ref[1:])]}"
                if isinstance(operand, dict):
                    operand["value"] = replacement
                    operand["span_id"] = "STEP" + replacement
                else:
                    step[side] = replacement
        kept.append(step)
    result["steps"] = kept
    return result


def edge_candidates(answer, evidence):
    """Enumerate bounded single-edge reconnections, never consulting an answer key.

    Input is a canonical cited program. Operations, quantities, units and all
    other edges remain fixed. KEEP is always available; equivalent values merge.
    """
    execution = execute(answer.get("steps"), evidence) if isinstance(answer, dict) else {"issues": ["schema"]}
    if execution["issues"]:
        return []
    graph = audit_graph(answer["steps"])
    candidates = [{"id": "KEEP", "answer": deepcopy(answer), "execution": execution, "edit": None}]
    seen = {Decimal(execution["value"])}
    for consumer in graph["answer_ancestors"]:
        for side in ("left", "right"):
            for orphan in graph["unused_steps"]:
                if orphan >= consumer:
                    continue
                candidate = deepcopy(answer)
                original = deepcopy(candidate["steps"][consumer][side])
                replacement = {"value": f"#{orphan}", "span_id": f"STEP#{orphan}"}
                candidate["steps"][consumer][side] = replacement
                computed = execute(candidate["steps"], evidence)
                if computed["issues"] or Decimal(computed["value"]) in seen:
                    continue
                seen.add(Decimal(computed["value"]))
                candidates.append({"id": f"E{len(candidates):03d}", "answer": candidate,
                                   "execution": computed,
                                   "edit": {"step": consumer, "side": side, "before": original, "after": replacement}})
    return candidates
