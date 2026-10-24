"""Proof-feedback versus plain retry on a fixed, gold-free output snapshot.

Both conditions use the same cancellation-based cohort and output allowances.
The feedback condition exposes the exact value-influence diagnostic. Selection
does not mean the answer is wrong; KEEP is allowed for legitimate cancellation.
This is a component experiment, not fresh end-to-end inference.
"""
from copy import deepcopy
import json

from evidence_atoms import atom_catalog, compile_plan, reference_schema
from evidence_contract import TokenLedger
from program_influence import functional_influence
from tier8_v2_financial_pipeline import checked, question_units, verdict, VERIFY


def repair_snapshot(public, snapshot, models, arm, feedback, *, event_sink=None):
    if set(public) & {"gold", "qa", "answer", "program", "model_input", "gold_inds"}:
        raise ValueError("Evaluation targets must not enter repair")
    if set(snapshot) != {"plan", "answer", "verdict", "tokens"}:
        raise ValueError("Repair snapshot accepts model state only")
    if feedback not in ("plain", "proof") or arm not in ("sas", "mas"):
        raise ValueError("Unknown repair condition")
    atoms, evidence = atom_catalog(public["evidence"]), public["evidence"]
    plan, answer, review = deepcopy(snapshot["plan"]), deepcopy(snapshot["answer"]), deepcopy(snapshot["verdict"])
    initial_execution = checked(answer, evidence)
    if not initial_execution["issues"] and compile_plan(plan, atoms) != answer:
        raise ValueError("Snapshot references do not reproduce the saved answer")
    audit = functional_influence(plan, atoms) if not initial_execution["issues"] else {"status": "not_executable"}
    eligible = audit.get("status") == "analyzed" and bool(audit.get("value_inactive_sources"))
    budget = TokenLedger(spent=snapshot["tokens"])
    stages, accepted, attempted, reason = [], False, False, "not_flagged"
    def call(role, prompt, schema, requested, stage):
        value, event = models.call(role, prompt, schema, budget, requested, stage)
        stages.append(event)
        if event_sink:
            event_sink({"case_id": public["id"], **event})
        return value
    units = question_units(public["question"], "question")
    choice = None
    role = "sas" if arm == "sas" else "drafter"
    source_context = "Question: " + public["question"] + "\nFinancial source evidence:\n" + json.dumps(evidence)
    if eligible:
        limit = budget.allowance(512, reserve=192)
        reason = "budget_exhausted"
        if limit:
            attempted, reason = True, "kept"
            prompt = (source_context + "\nCurrent source-quantity catalog:\n"
                + "\n".join(f"{key}={a['value']}@{a['span_id']}" for key, a in atoms.items())
                + "\nPrevious program (may be wrong):\n" + json.dumps(plan))
            if feedback == "proof":
                prompt += ("\nExact symbolic value-influence diagnostic:\n" + json.dumps(audit)
                    + "\nThe listed inactive source quantities cancel from the answer value on the defined division domain. "
                      "This can be legitimate; it does NOT prove the answer is wrong. Check whether the requested financial measures and periods are actually used.")
            prompt += ("\nIndependently check the formula, source measures, dates, units and scaling. "
                "Choose KEEP if the original calculation correctly answers the question. Otherwise return REPLACE with a corrected source-reference plan. "
                "Do not invent missing evidence; an insufficient replacement has decision INSUFFICIENT and empty steps. "
                "Use current Axxx quantity IDs, earlier # step references and permitted CONST values; last step is the result. "
                "Percent means percentage points; fraction means a dimensionless fraction; number is the requested amount/count/ratio. "
                "Return action KEEP, or action REPLACE with plan.")
            schema = {"oneOf": [
                {"type": "object", "properties": {"action": {"const": "KEEP"}}, "required": ["action"], "additionalProperties": False},
                {"type": "object", "properties": {"action": {"const": "REPLACE"}, "plan": reference_schema(atoms, units, causal=True)},
                 "required": ["action", "plan"], "additionalProperties": False}]}
            choice = call(role, prompt, schema, limit, "influence_retry")
            if isinstance(choice, dict) and choice.get("action") == "REPLACE":
                proposed = choice.get("plan")
                valid = (isinstance(proposed, dict) and set(proposed) == {"decision", "answer_unit", "steps"}
                         and proposed.get("answer_unit") in units)
                candidate = None
                if valid:
                    try:
                        candidate = compile_plan(proposed, atoms)
                    except ValueError:
                        pass
                abstained = candidate and candidate.get("decision") == "INSUFFICIENT" and candidate.get("steps") == []
                valid_answer = candidate and candidate.get("decision") == "ANSWER" and not checked(candidate, evidence)["issues"]
                if (abstained or valid_answer) and proposed != plan:
                    plan, answer, accepted, reason = deepcopy(proposed), candidate, True, "replaced"
                    content = source_context + "\nProposed repaired program:\n" + json.dumps(answer)
                    content += "\nDeterministic execution:\n" + json.dumps(checked(answer, evidence))
                    content += ("\nIndependently judge operand relevance, operations and units. Execution alone does not prove relevance. "
                                "Return checks, steps_to_repair, repair_kind; NONE only when all checks PASS. UNKNOWN means insufficient evidence.")
                    review = verdict(call("sas" if arm == "sas" else "verifier", content, VERIFY,
                                          budget.allowance(192), "verify_influence_retry"))
                elif proposed != plan:
                    reason = "invalid_replacement_kept"
            elif not isinstance(choice, dict) or choice.get("action") != "KEEP":
                reason = "invalid_choice_kept"
    execution = checked(answer, evidence)
    good = isinstance(review, dict) and review.get("verdict") == "PASS"
    return {"case_id": public["id"], "condition": feedback, "execution_mode": "fixed_output_repair_component",
            "initial_plan": snapshot["plan"], "plan": plan, "initial_answer": snapshot["answer"], "answer": answer,
            "initial_execution": initial_execution, "execution": execution,
            "initial_verdict": snapshot["verdict"], "final_verdict": review,
            "eligible": eligible, "repair_attempted": attempted, "repair_accepted": accepted, "reason": reason,
            "influence": audit, "choice": choice, "delivered": not execution["issues"] and good,
            "baseline_tokens": snapshot["tokens"], "fresh_tokens": budget.spent - snapshot["tokens"],
            "combined_output_tokens": budget.spent, "fresh_stages": stages}
