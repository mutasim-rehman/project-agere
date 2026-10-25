"""Conservative, bounded equivalence for source-reference arithmetic programs.

This certifies rational equality, matching division conditions and current-document
Decimal execution. It does NOT certify financial relevance or global Decimal
equivalence. Source IDs remain distinct even when their observed values coincide.
Unknown/unsupported programs must never be merged using this certificate.
"""
from dataclasses import dataclass
from fractions import Fraction

from evidence_atoms import compile_plan
from evidence_calculator import execute, CONSTANTS


class Limit(Exception):
    pass


class Algebra:
    def __init__(self, max_operations=100000, max_monomials=2048, max_bits=4096):
        self.operations = 0
        self.max_operations, self.max_monomials, self.max_bits = max_operations, max_monomials, max_bits

    def charge(self, n):
        if self.operations + n > self.max_operations:
            raise Limit('operations')
        self.operations += n

    def bound(self, p):
        p = {t: c for t, c in p.items() if c}
        if len(p) > self.max_monomials:
            raise Limit('monomials')
        if any(max(c.numerator.bit_length(), c.denominator.bit_length()) > self.max_bits for c in p.values()):
            raise Limit('coefficient_bits')
        return p

    def add(self, a, b, sign=1):
        self.charge(len(a) + len(b))
        p = dict(a)
        for t, c in b.items():
            p[t] = p.get(t, Fraction(0)) + sign * c
        return self.bound(p)

    def mul(self, a, b):
        self.charge(len(a) * len(b))
        p = {}
        for x, u in a.items():
            for y, v in b.items():
                t = tuple(sorted(x + y))
                p[t] = p.get(t, Fraction(0)) + u * v
        return self.bound(p)


def normalized_guard(poly):
    """Only remove a nonzero scalar; deliberately no factorization heuristic."""
    if not poly:
        raise ValueError('identically_zero_divisor')
    leading = poly[sorted(poly)[0]]
    return tuple((term, value / leading) for term, value in sorted(poly.items()))


@dataclass
class Form:
    numerator: dict
    denominator: dict
    guards: frozenset
    sources: frozenset
    unit: str
    observed: Fraction


def analyze(plan, atoms, evidence, **limits):
    algebra = Algebra(**limits)
    try:
        if (not isinstance(plan, dict) or set(plan) != {'decision', 'answer_unit', 'steps'}
                or plan['decision'] != 'ANSWER' or plan['answer_unit'] not in ('number', 'percent', 'fraction')
                or not isinstance(plan['steps'], list) or not 1 <= len(plan['steps']) <= 8):
            raise ValueError('plan_schema')
        compiled = compile_plan(plan, atoms)
        execution = execute(compiled['steps'], evidence)
        if execution['issues']:
            raise ValueError('not_executable')
        one, nodes, guards, sources = {(): Fraction(1)}, [], set(), set()

        def operand(ref, index):
            if ref in atoms:
                sources.add(ref)
                return {(ref,): Fraction(1)}, one
            if ref.startswith('#') and ref[1:].isdigit() and int(ref[1:]) < index:
                return nodes[int(ref[1:])]
            if ref.startswith('CONST:') and Fraction(ref[6:]) in CONSTANTS:
                n = Fraction(ref[6:])
                return ({(): n} if n else {}), one
            raise ValueError('noncausal_or_unknown_reference')

        for index, step in enumerate(plan['steps']):
            a, b = operand(step['left'], index), operand(step['right'], index)
            if step['op'] in ('add', 'subtract'):
                n = algebra.add(algebra.mul(a[0], b[1]), algebra.mul(b[0], a[1]),
                                -1 if step['op'] == 'subtract' else 1)
                d = algebra.mul(a[1], b[1])
            elif step['op'] == 'multiply':
                n, d = algebra.mul(a[0], b[0]), algebra.mul(a[1], b[1])
            elif step['op'] == 'divide':
                guard = normalized_guard(b[0])
                # Nonzero constants impose no additional input-domain restriction.
                if any(term for term, _ in guard):
                    guards.add(guard)
                n, d = algebra.mul(a[0], b[1]), algebra.mul(a[1], b[0])
            else:
                raise ValueError('operation')
            nodes.append((n, d))
        form = Form(n, d, frozenset(guards), frozenset(sources), plan['answer_unit'], Fraction(execution['value']))
        return {'status': 'analyzed', 'form': form, 'operations': algebra.operations,
                'execution': execution}
    except Limit as exc:
        return {'status': 'unknown', 'reason': str(exc), 'operations': algebra.operations,
                'execution': execution}
    except (ValueError, TypeError, KeyError, ZeroDivisionError) as exc:
        return {'status': 'unsupported', 'reason': str(exc), 'operations': algebra.operations}


def equivalent(left, right, **limits):
    """Return a bounded certificate; a negative result is not inequivalence proof."""
    if left['status'] != 'analyzed' or right['status'] != 'analyzed':
        return {'equivalent': False, 'reason': 'unanalyzed', 'operations': 0}
    a, b = left['form'], right['form']
    for key in ('sources', 'unit', 'observed', 'guards'):
        if getattr(a, key) != getattr(b, key):
            return {'equivalent': False, 'reason': key, 'operations': 0}
    algebra = Algebra(**limits)
    try:
        delta = algebra.add(algebra.mul(a.numerator, b.denominator),
                            algebra.mul(b.numerator, a.denominator), -1)
        return {'equivalent': not delta, 'reason': 'rational_identity' if not delta else 'different_rational_functions',
                'operations': algebra.operations}
    except Limit as exc:
        return {'equivalent': False, 'reason': 'unknown_' + str(exc), 'operations': algebra.operations}


def partition(plans, atoms, evidence, *, mode='source_symbolic', max_candidates=64,
              max_total_operations=1000000, **limits):
    """Stable first-representative groups. No gold, scores, or majority voting.

    Controls intentionally differ: bytes only; current numeric result plus unit;
    numeric result plus source footprint; source-aware symbolic certificate.
    Invalid/unknown inputs retain their own group in every control.
    """
    import json
    if mode not in ('bytes', 'numeric', 'numeric_sources', 'source_symbolic'):
        raise ValueError('partition_mode')
    if len(plans) > max_candidates:
        raise ValueError('candidate_limit')
    if type(max_total_operations) is not int or max_total_operations < 0:
        raise ValueError('total_operation_limit')
    operations, analyses = 0, []
    def remaining_limits():
        return {**limits, 'max_operations': min(limits.get('max_operations', 100000),
                                               max_total_operations - operations)}
    for plan in plans:
        analysis = analyze(plan, atoms, evidence, **remaining_limits())
        operations += analysis['operations']
        analyses.append(analysis)
    groups, comparisons = [], []
    for i, (plan, analysis) in enumerate(zip(plans, analyses)):
        matched = False
        if analysis['status'] == 'analyzed':
            for group in groups:
                j = group[0]
                other = analyses[j]
                if other['status'] != 'analyzed':
                    continue
                a, b = analysis['form'], other['form']
                if mode == 'source_symbolic':
                    check = equivalent(analysis, other, **remaining_limits())
                else:
                    same = (json.dumps(plan, sort_keys=True) == json.dumps(plans[j], sort_keys=True)
                            if mode == 'bytes' else (a.observed, a.unit) == (b.observed, b.unit)
                            and (mode == 'numeric' or a.sources == b.sources))
                    check = {'equivalent': same, 'reason': mode, 'operations': 0}
                comparisons.append({'left': i, 'right': j, **check})
                operations += check['operations']
                if check['equivalent']:
                    group.append(i)
                    matched = True
                    break
        if not matched:
            groups.append([i])
    return {'mode': mode, 'groups': groups, 'comparisons': comparisons, 'symbolic_operations': operations,
            'analyses': [{k: v for k, v in a.items() if k != 'form'} for a in analyses],
            'claim': 'Rational identity with matching source IDs, guards, units and observed Decimal value only; not semantic correctness.'}
