import sys
from pathlib import Path
import unittest
from copy import deepcopy
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'research/tier8_v2/experiments'))
from source_span_catalog import complete_catalog
from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import execute, numeric_tokens


class SourceSpanCatalog(unittest.TestCase):
    def test_exposes_header_value_without_changing_source_or_old_ids(self):
        evidence = {'table_1': 'buildings: vehicles ; 39: 5'}
        before = deepcopy(evidence)
        old, new = atom_catalog(evidence), complete_catalog(evidence)
        self.assertEqual(evidence, before)
        self.assertEqual(list(new.items())[:len(old)], list(old.items()))
        key = next(k for k, a in new.items() if a['value'] == '39')
        plan = {'steps': [{'op': 'add', 'left': key, 'right': 'CONST:0'}]}
        result = execute(compile_plan(plan, new)['steps'], evidence)
        self.assertEqual(result['value'], '39')
        self.assertEqual(result['issues'], [])
        self.assertNotIn('location', new[key])

    def test_keeps_all_source_spans_instead_of_first_matching_value(self):
        evidence = {'table_1': '2019: 5', 'table_2': '2019: 6'}
        catalog = complete_catalog(evidence)
        self.assertEqual({a['span_id'] for a in catalog.values() if a['value'] == '2019'},
            {'table_1', 'table_2'})
        for atom in catalog.values():
            self.assertIn(Decimal(atom['value']), numeric_tokens(evidence[atom['span_id']]))

    def test_does_not_fabricate_values_or_add_rejected_magnitudes(self):
        evidence = {'table_1': '1e25: (3) ; rate: 4.5%', 'text_0': 'amount 12'}
        catalog = complete_catalog(evidence)
        self.assertNotIn(Decimal('1e25'), {Decimal(a['value']) for a in catalog.values()})
        self.assertEqual(list(catalog.items()), list(atom_catalog(evidence).items()))


if __name__ == '__main__':
    unittest.main()
