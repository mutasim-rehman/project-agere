import sys
from pathlib import Path
import unittest
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from table_header_materialization import materialize, atom_facts
from evidence_atoms import atom_catalog


class HeaderPreservation(unittest.TestCase):
    def test_first_row_value_recovered_without_losing_old_facts_or_mutating_input(self):
        public = {'id': 'example', 'question': 'ratio?', 'evidence': {
            'table_1': 'buildings and improvements: vehicles ; 39: 5', 'text_0': 'Other amount 12'}}
        original = deepcopy(public)
        result = materialize(public, [['buildings and improvements', '39'], ['vehicles', '5']])
        self.assertEqual(public, original)
        self.assertEqual(list(public['evidence']), list(result['evidence']))
        self.assertEqual(result['evidence']['text_0'], public['evidence']['text_0'])
        self.assertFalse(atom_facts(public['evidence']) - atom_facts(result['evidence']))
        self.assertIn('39', {v['value'] for v in atom_catalog(result['evidence']).values()})
        cell = result['first_row_materialization']['appended_cells'][1]
        self.assertEqual((cell['source_row'], cell['source_column'], cell['original_cell']), (0, 1, '39'))
        self.assertEqual(result['evidence'][cell['augmented_span']][cell['text_start']:cell['text_end']], '39')

    def test_header_literals_added_once_with_no_fabricated_column_numbers(self):
        public = {'evidence': {'table_9': 'label: item ; value: 5', 'table_2': 'label: other ; value: 6'}}
        result = materialize(public, [['metric: 213', '47']])
        self.assertEqual(result['evidence']['table_2'], public['evidence']['table_2'])
        values = [a['value'] for a in atom_catalog(result['evidence']).values()]
        self.assertCountEqual(values, ['5', '6', '213', '47'])
        self.assertEqual(len(result['first_row_materialization']['appended_cells']), 2)

    def test_no_table_selected_does_not_inject_first_row(self):
        public = {'evidence': {'text_0': 'Revenue 12'}}
        result = materialize(public, [['hidden amount', '999']])
        self.assertEqual(result['evidence'], public['evidence'])
        self.assertFalse(result['first_row_materialization']['appended_cells'])


if __name__ == '__main__': unittest.main()
