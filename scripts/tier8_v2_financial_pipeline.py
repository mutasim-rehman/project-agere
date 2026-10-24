"""FinQA development adapter: cited programs, source-visible checks and repair.

Only public question/evidence packets enter generation. Deterministic execution
is a strong baseline from prior work, not a claimed research contribution.
"""
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import json
import re

from evidence_calculator import CONSTANTS, OPERATIONS, execute
from evidence_contract import TokenLedger
from evidence_atoms import atom_catalog, reference_schema, reference_step_schema, compile_plan, patch_plan
from program_graph import audit_graph, edge_candidates


def program_schema(evidence, units=("number", "percent", "fraction")):
    operand = {"type": "object", "properties": {"value": {"type": "string"},
        "span_id": {"enum": sorted(evidence) + ["CONST"] + [f"STEP#{i}" for i in range(8)]}},
        "required": ["value", "span_id"], "additionalProperties": False}
    step = {"type": "object", "properties": {"op": {"enum": list(OPERATIONS)},
        "left": operand, "right": operand}, "required": ["op", "left", "right"], "additionalProperties": False}
    return {"type": "object", "properties": {"decision": {"enum": ["ANSWER", "INSUFFICIENT"]},
        "answer_unit": {"enum": list(units)},
        "steps": {"type": "array", "items": step, "minItems": 0, "maxItems": 8}},
        "required": ["decision", "answer_unit", "steps"], "additionalProperties": False}


VERIFY = {"type": "object", "properties": {
    "checks": {"type": "object", "properties": {k: {"enum": ["PASS", "FAIL", "UNKNOWN"]}
        for k in ("operands", "operations", "units")}, "required": ["operands", "operations", "units"], "additionalProperties": False},
    "steps_to_repair": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 7}, "maxItems": 8},
    "repair_kind": {"enum": ["NONE", "PATCH", "REPLAN"]}},
    "required": ["checks", "steps_to_repair", "repair_kind"], "additionalProperties": False}


def verdict(raw):
    checks = raw.get("checks") if isinstance(raw, dict) else None
    if not isinstance(checks, dict) or set(checks) != {"operands", "operations", "units"}:
        return None
    if any(v not in ("PASS", "FAIL", "UNKNOWN") for v in checks.values()):
        return None
    failed = [k for k, v in checks.items() if v != "PASS"]
    consistent = not raw.get("steps_to_repair") and raw.get("repair_kind") == "NONE"
    return {**raw, "verdict": "PASS" if not failed and consistent else "FAIL", "unsupported_fields": failed}


def checked(answer, evidence):
    if not isinstance(answer, dict) or answer.get("decision") != "ANSWER":
        return {"value": None, "issues": [{"step": None, "code": "insufficient_or_invalid_answer"}], "nodes": []}
    return execute(answer.get("steps"), evidence)


def patch_program(answer, updates, allowed, evidence):
    """Keep topology/untouched steps fixed, then re-execute the dependent graph."""
    original = deepcopy(answer)
    if not isinstance(answer, dict) or not isinstance(answer.get("steps"), list) or not isinstance(updates, dict):
        return original, False
    items = updates.get("updates")
    if not isinstance(items, list) or not items:
        return original, False
    indices = [item.get("index") for item in items if isinstance(item, dict)]
    if len(indices) != len(items) or any(type(i) is not int for i in indices) or len(set(indices)) != len(indices):
        return original, False
    if not set(indices) <= allowed or any(not 0 <= i < len(answer["steps"]) for i in indices):
        return original, False
    candidate = deepcopy(answer)
    for item in items:
        if set(item) != {"index", "step"}:
            return original, False
        candidate["steps"][item["index"]] = deepcopy(item["step"])
    return (candidate, True) if not checked(candidate, evidence)["issues"] else (original, False)


def question_units(question, mode):
    if mode == "free":
        return ("number", "percent", "fraction")
    if "%" in question or re.search(r"\bpercent(?:age)?\b", question, re.I):
        return ("percent", "fraction")
    if re.search(r"\b(average|ratio|how many)\b|\bin (?:millions|billions)\b", question, re.I):
        return ("number",)
    return ("number", "percent", "fraction")


def fit_demonstrations(prompt, demonstrations, models, role):
    used = []
    for example in demonstrations:
        candidate = [*used, example]
        text = ("Examples from separate training documents. Quantity IDs restart in each example.\n"
                + "\n\n".join(e["text"] for e in candidate) + "\n\nNow solve the actual question using its own source IDs:\n" + prompt)
        if models.count_prompt_tokens(role, text) + 768 + 8 <= models.context:
            used = candidate
    if not used:
        return prompt, []
    return ("Examples from separate training documents. Quantity IDs restart in each example.\n"
            + "\n\n".join(e["text"] for e in used) + "\n\nNow solve the actual question using its own source IDs:\n" + prompt), [e["source_id"] for e in used]


def run_financial(public, models, arm, repair, *, event_sink=None, representation="literal", unit_mode="free", selector="suggest", causal_mode="check", catalog_style="full", demonstrations=(), analysis_tokens=0):
    if set(public) & {"gold", "qa", "answer", "program", "model_input", "gold_inds"}:
        raise ValueError("Gold/annotated fields must not enter deployment")
    evidence = public["evidence"]
    units = question_units(public["question"], unit_mode)
    atoms = atom_catalog(evidence) if representation == "reference" else {}
    schema = reference_schema(atoms, units, causal=causal_mode == "grammar") if representation == "reference" else program_schema(evidence, units)
    def decode(plan):
        if representation == "literal":
            return plan
        try:
            return compile_plan(plan, atoms)
        except ValueError as exc:
            return {"decision": "ANSWER", "steps": None, "compile_error": str(exc)}
    budget, stages = TokenLedger(), []
    def call(role, content, output_schema, limit, stage):
        result, event = models.call(role, content, output_schema, budget, limit, stage)
        stages.append(event)
        if event_sink:
            event_sink({"case_id": public["id"], **event})
        return result
    source_context = "Question: " + public["question"] + "\nFinancial report evidence by source ID:\n" + json.dumps(evidence)
    context = source_context
    if representation == "reference":
        catalog = json.dumps(atoms) if catalog_style == "full" else "\n".join(f"{key}={atom['value']}@{atom['span_id']}" for key, atom in atoms.items())
        context += "\nQuantity references (code copies these source values):\n" + catalog
    selection = None
    if arm == "mas" and selector == "suggest":
        selection_schema = {"type": "object", "properties": {"source_ids": {"type": "array",
            "items": {"enum": sorted(evidence)}, "minItems": 0, "maxItems": 8}},
            "required": ["source_ids"], "additionalProperties": False}
        selection = call("extractor", context + "\nSelect the source IDs needed for the calculation; return source_ids.", selection_schema, 96, "select_evidence")
    instruction = ("Build an arithmetic program, not a guessed answer. Operations are add, subtract, multiply, divide. "
        "Each left/right operand is {value: numeric string, span_id: source ID}. Copy numbers with citations. "
        "For a previous step use value '#0' with span_id 'STEP#0' (zero-based; earlier steps only). "
        "For a standard counting/scaling constant use span_id CONST. Allowed constants: "
        + ", ".join(str(n) for n in sorted(CONSTANTS))
        + ". Declare answer_unit: percent for percentage points (e.g. 25 means 25%), fraction for a dimensionless fraction (0.25), otherwise number in the requested units. "
          "Respect percentage scaling. Return decision ANSWER with steps and answer_unit; "
          "if evidence is insufficient return decision INSUFFICIENT and an empty steps array. "
          "The final step is the answer. Never insert gold answers or unexplained numbers.\nSchema:\n" + json.dumps(schema))
    if representation == "reference":
        instruction = ("Build a calculation using source-quantity references. Return JSON with decision ANSWER or INSUFFICIENT, "
            "answer_unit, and steps. Each step has op (add/subtract/multiply/divide), left and right reference strings. "
            "Use Axxx source IDs from the quantity catalog. For a prior step use #0, #1, etc. (earlier steps only). "
            "For a counting or scaling constant use CONST:value. Allowed constants: "
            + ", ".join(str(n) for n in sorted(CONSTANTS))
            + ". The last step gives the answer. Do not copy numeric values into left/right. "
            "Allowed answer_unit: " + ", ".join(units)
            + ". Percent means percentage points; fraction means a dimensionless ratio; number means the requested amount/count/ratio. "
              "If necessary evidence is missing, use INSUFFICIENT and empty steps. Check the row labels and years carefully.")
    draft_prompt = context + "\n" + instruction
    if isinstance(selection, dict):
        draft_prompt += "\nA fallible evidence selector suggests these IDs; recheck all report evidence: " + json.dumps(selection)
    drafter = "sas" if arm == "sas" else "drafter"
    notes = None
    if analysis_tokens:
        notes = call(drafter, context + "\nIdentify the exact requested financial measures, row labels and dates. "
            "State the formula in named variables, then map each variable to a source or quantity ID. "
            "Distinguish similarly named metrics. Do not invent missing evidence. Keep the reasoning concise.",
            None, analysis_tokens, "analyze_question")
        draft_prompt += "\nPreliminary reasoning (may be wrong; recheck the sources):\n" + str(notes)
    draft_prompt, used_demos = fit_demonstrations(draft_prompt, demonstrations, models, drafter)
    plan = call(drafter, draft_prompt, schema, 768, "program")
    initial_plan = deepcopy(plan)
    answer = decode(plan)
    initial = deepcopy(answer)
    initial_execution = checked(answer, evidence)
    def verify(candidate, stage):
        content = source_context + "\nProposed program:\n" + json.dumps(candidate)
        content += "\nDeterministic execution:\n" + json.dumps(checked(candidate, evidence))
        content += ("\nIndependently judge operand relevance (correct row/year), operations, and units for the question. "
                    "Arithmetic execution alone does not prove relevance. Return checks, steps_to_repair, repair_kind. "
                    "Use NONE only if all checks PASS and no steps need repair; PATCH for localized step corrections; "
                    "REPLAN for an incorrect/missing sequence of operations. UNKNOWN means evidence is insufficient.")
        return verdict(call("sas" if arm == "sas" else "verifier", content, VERIFY, budget.allowance(192), stage))
    review = verify(answer, "verify_program")
    initial_review = deepcopy(review)
    good = lambda v: isinstance(v, dict) and v.get("verdict") == "PASS"
    needs_repair = bool(initial_execution["issues"]) or not good(review)
    accepted = False
    scope = set()
    edge_trace = None
    if repair == "edge":
        pool = edge_candidates(answer, evidence) if not initial_execution["issues"] else []
        graph = audit_graph(answer["steps"]) if pool else {"unused_steps": []}
        # Rank structurally, never by gold: prefer reconnecting more dead work,
        # then a shorter backward edge. KEEP is always retained.
        alternatives = sorted(pool[1:], key=lambda c: (
            len(audit_graph(c["answer"]["steps"])["unused_steps"]),
            c["edit"]["step"] - int(c["edit"]["after"]["value"][1:]),
            c["id"]))
        shown = pool[:1] + alternatives[:7]
        needs_repair = len(shown) > 1
        edge_trace = {"unused_steps": graph["unused_steps"], "pool_size": len(pool),
                      "shown": [{"id": c["id"], "value": c["execution"]["value"], "edit": c["edit"]} for c in shown],
                      "selection": None, "gold_used": False}
        if needs_repair:
            scope = {c["edit"]["step"] for c in shown if c["edit"]}
            selection_schema = {"type": "object", "properties": {"candidate_id": {"enum": [c["id"] for c in shown]}},
                                "required": ["candidate_id"], "additionalProperties": False}
            menu = [{"id": c["id"], "conditional_result": c["execution"]["value"],
                     "edit": c["edit"]} for c in shown]
            selection = call(drafter, source_context + "\nCurrent program:\n" + json.dumps(answer)
                + "\nUnused computed steps: " + json.dumps(graph["unused_steps"])
                + "\nCandidate single-edge reconnections (hypothetical calculations, not asserted answers):\n" + json.dumps(menu)
                + "\nChoose the candidate whose calculation answers the question in the declared units. "
                  "Check the source measures and formula. Choose KEEP if none improves the program. "
                  "Do not select a number merely because it looks plausible. Return candidate_id.",
                selection_schema, budget.allowance(192, reserve=192), "repair_edge_choice")
            edge_trace["selection"] = selection
            selected = next((c for c in shown if isinstance(selection, dict) and c["id"] == selection.get("candidate_id")), None)
            if selected and selected["edit"]:
                plan = deepcopy(plan)
                edit = selected["edit"]
                plan["steps"][edit["step"]][edit["side"]] = edit["after"]["value"]
                answer = decode(plan)
                if answer != selected["answer"]:
                    raise ValueError("Selected edge repair changed more than its declared edge")
                accepted = True
                review = verify(answer, "verify_edge_repair")
    elif repair != "none" and needs_repair:
        steps = plan.get("steps", []) if isinstance(plan, dict) else []
        scope = {e["step"] for e in initial_execution["issues"] if type(e.get("step")) is int}
        if isinstance(review, dict):
            scope |= {i for i in review.get("steps_to_repair", []) if type(i) is int and 0 <= i < len(steps)}
        if not scope:
            scope = set(range(len(steps)))
        feedback = {"checker": initial_execution, "review": review}
        if repair == "patch" and steps and isinstance(review, dict) and review.get("repair_kind") != "REPLAN":
            item_schema = {"type": "object", "properties": {"index": {"enum": sorted(scope)},
                "step": reference_step_schema(atoms) if representation == "reference" else schema["properties"]["steps"]["items"]},
                "required": ["index", "step"], "additionalProperties": False}
            if representation == "reference" and causal_mode == "grammar":
                item_schema = {"oneOf": [{"type": "object", "properties": {"index": {"const": i},
                    "step": reference_step_schema(atoms, i)}, "required": ["index", "step"], "additionalProperties": False} for i in sorted(scope)]}
            patch_schema = {"type": "object", "properties": {"updates": {"type": "array", "minItems": 1,
                "maxItems": len(scope), "items": item_schema}},
                "required": ["updates"], "additionalProperties": False}
            patch = call(drafter, context + "\n" + instruction + "\nCurrent program:\n" + json.dumps(plan)
                + "\nFeedback:\n" + json.dumps(feedback) + "\nReturn updates of index and corrected step only for these indices: " + json.dumps(sorted(scope)),
                patch_schema, budget.allowance(768, reserve=192), "repair_program_patch")
            if representation == "reference":
                plan, accepted = patch_plan(plan, patch, scope, atoms, evidence)
            else:
                plan, accepted = patch_program(plan, patch, scope, evidence)
            answer = decode(plan)
        else:
            candidate = call(drafter, draft_prompt + "\nCorrect this program:\n" + json.dumps(plan)
                + "\nFeedback:\n" + json.dumps(feedback), schema, budget.allowance(768, reserve=192), "repair_program_full")
            if isinstance(candidate, dict):
                plan, accepted = candidate, True
                answer = decode(plan)
        if accepted:
            review = verify(answer, "verify_program_repair")
    execution = checked(answer, evidence)
    return {"task": "finqa", "case_id": public["id"], "arm": arm, "repair": repair,
            "initial_answer": initial, "answer": answer, "initial_execution": initial_execution, "execution": execution,
            "initial_plan": initial_plan, "plan": plan, "representation": representation, "unit_mode": unit_mode, "selector": selector,
            "causal_mode": causal_mode, "catalog_style": catalog_style,
            "demonstrations_used": used_demos,
            "analysis_tokens_requested": analysis_tokens, "analysis_notes": notes,
            "edge_repair": edge_trace,
            "active_roles": sorted({s["role"] for s in stages}),
            "initial_verdict": initial_review, "final_verdict": review,
            "delivered": not execution["issues"] and good(review), "repair_attempted": repair != "none" and needs_repair,
            "repair_accepted": accepted, "repair_scope": sorted(scope), "tokens": budget.spent, "stages": stages,
            "retrieval": public["retrieval"]}


def reported_reference(value):
    text = str(value).strip().replace(",", "").replace("$", "").strip()
    match = re.fullmatch(r"([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*(%)?", text)
    if not match:
        return None
    number = Decimal(match[1])
    # Reported answers may be rounded (24.69% vs. a longer program result).
    tolerance = Decimal(1).scaleb(number.as_tuple().exponent) / 2 if number.as_tuple().exponent < 0 or match[2] else Decimal("0.00001")
    return {"value": number / 100 if match[2] else number,
            "tolerance": tolerance / 100 if match[2] else tolerance,
            "percent": bool(match[2])}


def evaluate_financial(row, answer, execution):
    # Two disclosed metrics: reported-answer rounding with explicit output units,
    # and raw exe_ans tolerance. No metric is used by deployment or repair.
    target = row["qa"]["exe_ans"]
    predicted = Decimal("NaN")
    try:
        predicted = Decimal(execution["value"]) if execution["value"] is not None else Decimal("NaN")
        truth = Decimal(str(target))
        equal = predicted.is_finite() and truth.is_finite() and abs(predicted - truth) <= max(Decimal("0.00001"), abs(truth) * Decimal("0.00001"))
    except (InvalidOperation, TypeError, ValueError):
        equal = False
    reference = reported_reference(row["qa"].get("answer", ""))
    reported_equal = False
    unit = answer.get("answer_unit") if isinstance(answer, dict) else None
    if reference is not None and predicted.is_finite():
        normalized = predicted / 100 if unit == "percent" else predicted
        unit_valid = unit in ("percent", "fraction") if reference["percent"] else unit in ("number", "fraction")
        reported_equal = unit_valid and abs(normalized - reference["value"]) <= max(reference["tolerance"], Decimal("0.00001"))
    success = bool(reported_equal and not execution["issues"] and isinstance(answer, dict) and answer.get("decision") == "ANSWER")
    return {"case_success": success, "field_correct": {"numeric_answer": success},
            "raw_execution_match": bool(equal), "reported_answer_match": bool(reported_equal),
            "reported_reference_supported": reference is not None,
            "source_supported_program": not bool(execution["issues"]),
            "metric": "reported-answer rounding with declared units; raw exe_ans tolerance 1e-5 separately; not official program equivalence"}
