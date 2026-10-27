"""Unadopted baseline: close the action catalog over executable span values.

Preserve original quantity IDs and facts. Append missing (span, numeric value)
entries without changing source text, selecting a financial role, or inventing
cell coordinates. Numeric support is deliberately only span-level support.
"""
from copy import deepcopy
from decimal import Decimal

from evidence_atoms import atom_catalog
from evidence_calculator import numeric_tokens


def complete_catalog(evidence):
    result = deepcopy(atom_catalog(evidence))
    for span, text in evidence.items():
        existing = {Decimal(a['value']) for a in result.values() if a['span_id'] == span}
        for value in sorted(numeric_tokens(text) - existing):
            if abs(value) > Decimal('1e20'):
                continue  # The executor also rejects input magnitudes above this.
            result[f'A{len(result):03d}'] = {'value': str(value), 'span_id': span,
                'context': 'Unlocalized numeric value in original source span; financial role and cell identity unverified.'}
    return result
