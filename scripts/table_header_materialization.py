"""Prototype: expose first-row literals without changing retrieved span selection.

Only raw table cells are accepted; answer/program annotations are not inputs.
Augmented spans are context groups, not original unmodified FinQA rows. Every
appended cell carries its original row/column and exact normalized text offsets.
This is a preprocessing baseline candidate, not an adopted or novel QA method.
"""
from collections import Counter
from copy import deepcopy
from evidence_atoms import atom_catalog


def atom_facts(evidence):
    return Counter((a['span_id'], a['value'], a['context']) for a in atom_catalog(evidence).values())


def materialize(public, table):
    result = deepcopy(public); ledger = []
    first = next((k for k in result['evidence'] if k.startswith('table_')), None)
    if first is not None and table:
        text = result['evidence'][first]
        for column, value in enumerate(table[0]):
            if not isinstance(value, str):
                raise ValueError('Prototype requires original string table cells')
            normalized = value.replace(': ', ':')
            label = ' ; original first-row cell: '
            start = len(text) + len(label); text += label + normalized
            ledger.append({'augmented_span': first, 'source_row': 0, 'source_column': column,
                'original_cell': value, 'normalized_cell': normalized,
                'normalization': 'remove space after internal colon to preserve existing parser delimiter',
                'text_start': start, 'text_end': len(text)})
        result['evidence'][first] = text
    result['first_row_materialization'] = {'kind': 'source_traced_first_row_literals',
        'retrieved_span_selection_unchanged': True, 'appended_cells': ledger,
        'scope': 'Augmented context-group span; source cell identity is in this ledger. No financial role or semantic correctness certified.'}
    if list(result['evidence']) != list(public['evidence']) or atom_facts(public['evidence']) - atom_facts(result['evidence']):
        raise ValueError('Original selected spans or catalog facts were lost')
    for cell in ledger:
        if result['evidence'][cell['augmented_span']][cell['text_start']:cell['text_end']] != cell['normalized_cell']:
            raise ValueError('Source origin offsets do not reproduce')
    return result
