"""Predict a calculation structure before assigning source quantities."""
from copy import deepcopy

from evidence_calculator import OPERATIONS
from program_graph import audit_graph


PLAN_TOKENS = 192


def shape_request(context):
    steps = []
    for index in range(8):
        refs = ["VALUE", *(f"#{i}" for i in range(index))]
        steps.append({"type": "object", "properties": {
            "op": {"enum": list(OPERATIONS)}, "left": {"enum": refs}, "right": {"enum": refs}},
            "required": ["op", "left", "right"], "additionalProperties": False})
    lengths = [{"const": []}] + [{"type": "array", "prefixItems": steps[:n],
                                  "minItems": n, "maxItems": n} for n in range(1, 9)]
    schema = {"type": "object", "properties": {"steps": {"oneOf": lengths}},
        "required": ["steps"], "additionalProperties": False}
    prompt = (context + "\nPlan the shortest arithmetic calculation that answers the exact question. "
              "Identify the requested operation, direction and denominator. "
              "Write VALUE for a quantity to be filled in later, including a standard constant. "
              "Use #0, #1, and so on for earlier results. "
              "Every operation must contribute to the final result. "
              "Return only steps with op, left and right. Return empty steps if unsure.")
    return prompt, schema


def predicted_shape_schema(prediction, schema, atoms):
    if not isinstance(prediction, dict) or set(prediction) != {"steps"} or not atoms:
        return None
    shape = prediction["steps"]
    constrained = deepcopy(schema)
    try:
        constrain_shape(constrained, shape, atoms)
        if audit_graph(shape)["unused_steps"]:
            return None
    except ValueError:
        return None
    return constrained


def constrain_shape(schema, shape, atoms):
    """Fix the operation graph while leaving each source slot to the drafter."""
    lengths = schema["oneOf"][0]["properties"]["steps"]["oneOf"]
    if not isinstance(shape, list) or not 1 <= len(shape) <= len(lengths):
        raise ValueError("Expected a bounded reference shape")
    length = lengths[len(shape) - 1]
    for step, options in zip(shape, length["prefixItems"]):
        if not isinstance(step, dict) or set(step) != {"op", "left", "right"}:
            raise ValueError("Invalid reference shape step")
        narrowed = []
        for branch in options["oneOf"]:
            props = branch["properties"]
            for key, value in step.items():
                values = props[key]["enum"]
                if value == "VALUE" and key != "op":
                    allowed = [ref for ref in values if ref in atoms or ref.startswith("CONST:")]
                elif value == "SOURCE" and key != "op":
                    allowed = [ref for ref in values if ref in atoms]
                else:
                    allowed = [value] if value in values else []
                props[key]["enum"] = allowed
            if all(prop["enum"] for prop in props.values()):
                narrowed.append(branch)
        if not narrowed:
            raise ValueError("Shape must identify a grounded operation per step")
        options["oneOf"] = narrowed
    lengths[:] = [length]


