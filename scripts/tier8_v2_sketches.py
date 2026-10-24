"""Training-derived formula sketches with source bindings: a staged baseline.

No evaluation targets are accepted. Formula choice and variable binding remain
semantic predictions, not proofs. Operations/constants/units are copied from the
chosen training sketch, and only current-report quantity IDs can fill its slots.
"""
from copy import deepcopy
import json


def make_sketch(target, atoms):
    steps, mapping, slots = deepcopy(target["steps"]), {}, {}
    for step in steps:
        for side in ("left", "right"):
            ref = step[side]
            if ref in atoms:
                if ref not in mapping:
                    key = f"V{len(mapping)}"
                    mapping[ref] = key
                    slots[key] = {"training_value": atoms[ref]["value"], "context": atoms[ref]["context"]}
                step[side] = mapping[ref]
    return {"answer_unit": target["answer_unit"], "steps": steps, "slots": slots}


def render_sketch(example, key):
    return {"sketch_id": key, "training_question": example["question"], **example["sketch"]}


def choice_schema(examples, atoms):
    variants = []
    for i, example in enumerate(examples):
        if not atoms:
            continue
        bindings = {name: {"enum": list(atoms)} for name in example["sketch"]["slots"]}
        variants.append({"type": "object", "properties": {"sketch_id": {"const": f"T{i}"},
            "bindings": {"type": "object", "properties": bindings, "required": list(bindings), "additionalProperties": False}},
            "required": ["sketch_id", "bindings"], "additionalProperties": False})
    variants.append({"type": "object", "properties": {"sketch_id": {"const": "NONE"}, "bindings": {"const": {}}},
                     "required": ["sketch_id", "bindings"], "additionalProperties": False})
    return {"oneOf": variants}


def instantiate_choice(choice, examples, atoms):
    insufficient = {"decision": "INSUFFICIENT", "answer_unit": "number", "steps": []}
    if not isinstance(choice, dict) or set(choice) != {"sketch_id", "bindings"}:
        return insufficient
    selected = next((e for i, e in enumerate(examples) if choice["sketch_id"] == f"T{i}"), None)
    if not selected:
        return insufficient
    sketch = selected["sketch"]
    bindings = choice["bindings"]
    if not isinstance(bindings, dict) or set(bindings) != set(sketch["slots"]):
        return insufficient
    if any(not isinstance(ref, str) or ref not in atoms for ref in bindings.values()):
        return insufficient
    steps = deepcopy(sketch["steps"])
    for step in steps:
        for side in ("left", "right"):
            if step[side] in bindings:
                step[side] = bindings[step[side]]
    return {"decision": "ANSWER", "answer_unit": sketch["answer_unit"], "steps": steps}


def fit_sketches(context, examples, models, role, units):
    instruction = ("Choose a training-derived formula sketch for the CURRENT question, then bind each V slot to a CURRENT Axxx quantity ID. "
        "The training question and slot contexts explain each variable's role; training values are not current evidence. "
        "Check metric, entity and period. Preserve the sketch's operations/constants/units. "
        "Use NONE and empty bindings if no sketch applies or required evidence is missing. Return sketch_id and bindings.\n")
    chosen = []
    def prompt(items):
        return context + "\n" + instruction + json.dumps([render_sketch(e, f"T{i}") for i, e in enumerate(items)])
    for example in examples:
        if example["sketch"]["answer_unit"] not in units:
            continue
        candidate = [*chosen, example]
        if models.count_prompt_tokens(role, prompt(candidate)) + 768 + 8 <= models.context:
            chosen = candidate
    return prompt(chosen), chosen
