"""Exact, bounded symbolic value-influence diagnostics for reference programs.

Each source quantity ID is a separate variable, even when observed values match.
Zero rational derivative proves value independence on the program's defined
domain. This is not semantic irrelevance: legitimate ratios can cancel, and
source values can still establish that division is defined. Never reject an
answer solely from this diagnostic. Standard symbolic algebra is not novel.
"""
from collections import Counter
from fractions import Fraction

from evidence_calculator import CONSTANTS


class SymbolicLimit(Exception):
    pass


def functional_influence(plan, atoms, *, max_monomials=2048, max_operations=100000, max_coefficient_bits=4096):
    work = 0
    def charge(n):
        nonlocal work
        work += n
        if work > max_operations:
            raise SymbolicLimit("symbolic_work_limit")
    def bounded(poly):
        result = {term: coefficient for term, coefficient in poly.items() if coefficient}
        if len(result) > max_monomials:
            raise SymbolicLimit("symbolic_monomial_limit")
        if any(max(c.numerator.bit_length(), c.denominator.bit_length()) > max_coefficient_bits for c in result.values()):
            raise SymbolicLimit("symbolic_coefficient_limit")
        return result
    def plus(a, b, sign=1):
        charge(len(a) + len(b))
        result = dict(a)
        for key, value in b.items():
            result[key] = result.get(key, Fraction(0)) + sign * value
        return bounded(result)
    def times(a, b):
        charge(len(a) * len(b))
        result = {}
        for x, u in a.items():
            for y, v in b.items():
                key = tuple(sorted(x + y))
                result[key] = result.get(key, Fraction(0)) + u * v
        return bounded(result)
    def derivative(poly, variable):
        charge(len(poly))
        result = {}
        for term, coefficient in poly.items():
            power = Counter(term)[variable]
            if power:
                index = term.index(variable)
                result[term[:index] + term[index + 1:]] = coefficient * power
        return bounded(result)
    one = {(): Fraction(1)}
    nodes, guards = [], []
    def operand(ref, index):
        if not isinstance(ref, str):
            raise ValueError("non_reference_operand")
        if ref in atoms:
            return {"n": {(ref,): Fraction(1)}, "d": one, "sources": {ref}}
        if ref.startswith("#") and ref[1:].isdigit() and int(ref[1:]) < index:
            return nodes[int(ref[1:])]
        if ref.startswith("CONST:"):
            value = Fraction(ref[6:])
            if value in CONSTANTS:
                return {"n": {(): value} if value else {}, "d": one, "sources": set()}
        raise ValueError("unknown_or_noncausal_reference")
    try:
        steps = plan.get("steps") if isinstance(plan, dict) else None
        if not isinstance(steps, list) or not 1 <= len(steps) <= 8:
            raise ValueError("program_schema")
        for index, step in enumerate(steps):
            if not isinstance(step, dict) or set(step) != {"op", "left", "right"}:
                raise ValueError("step_schema")
            a, b = operand(step["left"], index), operand(step["right"], index)
            op = step["op"]
            if op in ("add", "subtract"):
                n = plus(times(a["n"], b["d"]), times(b["n"], a["d"]), -1 if op == "subtract" else 1)
                d = times(a["d"], b["d"])
            elif op == "multiply":
                n, d = times(a["n"], b["n"]), times(a["d"], b["d"])
            elif op == "divide":
                if not b["n"]:
                    raise ValueError("identically_zero_denominator")
                guards.append({"step": index, "denominator_sources": sorted(b["sources"]),
                               "condition": "denominator must be defined and nonzero"})
                n, d = times(a["n"], b["d"]), times(a["d"], b["n"])
            else:
                raise ValueError("unknown_operation")
            nodes.append({"n": n, "d": d, "sources": a["sources"] | b["sources"]})
        final = nodes[-1]
        active, inactive = [], []
        for source in sorted(final["sources"]):
            numerator = plus(times(derivative(final["n"], source), final["d"]),
                             times(final["n"], derivative(final["d"], source)), -1)
            (active if numerator else inactive).append(source)
        return {"status": "analyzed", "syntactic_sources": sorted(final["sources"]),
                "value_active_sources": active, "value_inactive_sources": inactive,
                "value_independent_of_all_sources": bool(final["sources"]) and not active,
                "division_guards": guards, "symbolic_operations": work,
                "caution": "Exact value dependence only, conditional on defined divisions; not semantic correctness or a rejection rule."}
    except SymbolicLimit as exc:
        return {"status": "unknown", "reason": str(exc), "symbolic_operations": work}
    except (ValueError, ZeroDivisionError) as exc:
        return {"status": "unsupported", "reason": str(exc), "symbolic_operations": work}
