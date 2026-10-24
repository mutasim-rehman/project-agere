"""Deployment-side checks and transactional repair; never consumes case labels.

This deliberately checks support, not benchmark correctness. Independent evaluation
must still detect incorrect extraction, omissions, and semantic contradictions.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re


@dataclass(frozen=True)
class Issue:
    field: str
    code: str


def source_spans(documents: list[dict]) -> dict[str, str]:
    spans = {}
    for doc in documents:
        for line in doc["lines"]:
            match = re.match(r"^(L\d+)\s", line)
            if match:
                key = f"{doc['id']}#{match[1]}"
                if key in spans:
                    raise ValueError(f"Duplicate evidence span: {key}")
                spans[key] = line
    return spans


def equal_value(left, right) -> bool:
    # JSON true must not equal the financial number 1.
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        try:
            return Decimal(str(left)).is_finite() and Decimal(str(left)) == Decimal(str(right))
        except InvalidOperation:
            return False
    return type(left) is type(right) and left == right


def check_claim(claim, spans: dict[str, str], calculations: dict) -> str | None:
    if not isinstance(claim, dict) or set(claim) != {"value", "span_id"}:
        return "claim_schema"
    value, span = claim["value"], claim["span_id"]
    if value == "MISSING":
        # Explicit absence must itself be cited. This is lexical support only;
        # the independent evaluator still checks which field the absence concerns.
        if isinstance(span, str) and span in spans and re.search(
                r"\b(not supplied|not provided|not recorded|unavailable)\b", spans[span], re.I):
            return None
        return "absence_unverified"
    if value is None or isinstance(value, (bool, list, dict)):
        return "invalid_value"
    if not isinstance(span, str):
        return "invalid_citation"
    if span.startswith("CALC#"):
        result = calculations.get(span)
        return None if result is not None and equal_value(value, result) else "calculator_mismatch"
    if span not in spans:
        return "unknown_span"
    # Whole tokens prevent 12 being accepted merely because a line contains 1200.
    pattern = r"(?<!\w)(?<!\d\.)" + re.escape(str(value)) + r"(?!\w|\.\d)"
    return None if re.search(pattern, spans[span]) else "unsupported_value"


def validate(answer, *, case_id: str, fields: tuple[str, ...],
             spans: dict[str, str], calculations: dict) -> list[Issue]:
    if not isinstance(answer, dict):
        return [Issue("$", "invalid_json_object")]
    issues = []
    if answer.get("case_id") != case_id:
        issues.append(Issue("case_id", "wrong_case_id"))
    facts = answer.get("facts")
    if not isinstance(facts, dict):
        return issues + [Issue("facts", "facts_schema")]
    for field in fields:
        code = check_claim(facts.get(field), spans, calculations)
        if code:
            issues.append(Issue(field, code))
    for field in sorted(set(facts) - set(fields)):
        issues.append(Issue(field, "unexpected_field"))
    return issues


def commit_patch(answer: dict, patch: dict, *, allowed: set[str],
                 spans: dict[str, str], calculations: dict) -> tuple[dict, bool]:
    """Apply all supported repairs atomically, preserving every unrelated claim.

    Rejected patches leave the original answer untouched. Missing-value repairs
    require a separate absence resolver, rather than accepting an unsupported null.
    """
    if not isinstance(patch, dict) or not patch or not set(patch) <= allowed:
        return deepcopy(answer), False
    if any(check_claim(claim, spans, calculations) for claim in patch.values()):
        return deepcopy(answer), False
    result = deepcopy(answer)
    result.setdefault("facts", {}).update(deepcopy(patch))
    return result, True


@dataclass
class TokenLedger:
    cap: int = 2048
    spent: int = 0

    def __post_init__(self):
        if self.cap < 0 or not 0 <= self.spent <= self.cap:
            raise ValueError("Invalid token ledger")

    def allowance(self, requested: int, reserve: int = 0) -> int:
        if requested < 0 or reserve < 0:
            raise ValueError("Negative token request")
        return max(0, min(requested, self.cap - self.spent - reserve))

    def charge(self, tokens: int) -> None:
        if tokens < 0 or self.spent + tokens > self.cap:
            raise ValueError("Token cap exceeded")
        self.spent += tokens
