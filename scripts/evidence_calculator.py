"""Bounded arithmetic over cited financial operands; no eval or gold access.

Program generation plus deterministic execution is existing FinQA methodology,
not an Agere novelty claim. Source support does not establish semantic relevance.
"""
from decimal import Decimal, InvalidOperation, localcontext
import re

CONSTANTS = {Decimal(str(n)) for n in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 100, 1000, 1000000, 1000000000)}
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
OPERATIONS = ("add", "subtract", "multiply", "divide")


def numeric_tokens(text):
    text = re.sub(r"(?<=\d),(?=\d)", "", text)
    text = re.sub(r"\((\d[\d.]*)\)", r"-\1", text)
    values = set()
    for match in re.finditer(r"(?<![\w.])" + NUMBER + r"(?![\w.])", text):
        try:
            number = Decimal(match[0])
            if number.is_finite():
                values.add(number)
        except InvalidOperation:
            pass
    return values


def execute(program, evidence):
    if not isinstance(program, list) or not 1 <= len(program) <= 8:
        return {"value": None, "issues": [{"step": None, "code": "program_schema"}], "nodes": []}
    values, lineage, nodes, issues = [], [], [], []
    def operand(item, i, side):
        if not isinstance(item, dict) or set(item) != {"value", "span_id"} or not isinstance(item["value"], str):
            issues.append({"step": i, "side": side, "code": "operand_schema"})
            return None, set()
        value, span = item["value"], item["span_id"]
        if value.startswith("#"):
            if not re.fullmatch(r"#\d+", value) or span != "STEP" + value:
                issues.append({"step": i, "side": side, "code": "step_reference_schema"})
                return None, set()
            index = int(value[1:])
            if index >= i:
                issues.append({"step": i, "side": side, "code": "noncausal_reference"})
                return None, set()
            return values[index], set(lineage[index])
        try:
            number = Decimal(value)
        except InvalidOperation:
            number = Decimal("NaN")
        if not number.is_finite() or abs(number) > Decimal("1e20"):
            issues.append({"step": i, "side": side, "code": "invalid_number"})
            return None, set()
        if span == "CONST" and number in CONSTANTS:
            return number, set()
        if not isinstance(span, str) or span not in evidence or number not in numeric_tokens(evidence[span]):
            issues.append({"step": i, "side": side, "code": "unsupported_operand"})
            return None, set()
        return number, {span}
    with localcontext() as ctx:
        ctx.prec = 28
        for i, step in enumerate(program):
            if not isinstance(step, dict) or set(step) != {"op", "left", "right"} or step["op"] not in OPERATIONS:
                issues.append({"step": i, "code": "step_schema"})
                break
            left, a = operand(step["left"], i, "left")
            right, b = operand(step["right"], i, "right")
            if issues:
                break
            if step["op"] == "divide" and right == 0:
                issues.append({"step": i, "code": "division_by_zero"})
                break
            if step["op"] == "add":
                result = left + right
            elif step["op"] == "subtract":
                result = left - right
            elif step["op"] == "multiply":
                result = left * right
            else:
                result = left / right
            if not result.is_finite() or abs(result) > Decimal("1e20"):
                issues.append({"step": i, "code": "result_out_of_range"})
                break
            values.append(result)
            lineage.append(a | b)
            nodes.append({"step": i, "value": str(result), "source_spans": sorted(a | b)})
    if not issues and not lineage[-1]:
        issues.append({"step": len(program) - 1, "code": "no_source_dependency"})
    return {"value": str(values[-1]) if not issues else None, "issues": issues, "nodes": nodes}
