from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import execute
from tier8_v2_critic_curriculum import proposals, extension_candidates, selected_extension, paired


class CriticCurriculumTests(unittest.TestCase):
    def fixture(self):
        evidence = {'table_1': 'gross: 10 ; allowance: 3 ; prior: 7 ; prior allowance: 2'}
        refs = {a['value']: k for k, a in atom_catalog(evidence).items()}
        row = {'source_id': 'sample', 'public': {'question': 'net ratio', 'evidence': evidence},
               'target': {'decision': 'ANSWER', 'answer_unit': 'number', 'steps': [
                   {'op': 'subtract', 'left': refs['10'], 'right': refs['3']},
                   {'op': 'subtract', 'left': refs['7'], 'right': refs['2']},
                   {'op': 'divide', 'left': '#0', 'right': '#1'}]}}
        return row, {'qa': {'answer': '1.4', 'exe_ans': 1.4}}

    def test_new_families_are_executable_and_wrong_on_both_metrics(self):
        row, gold = self.fixture(); before = deepcopy(row)
        choices = list(extension_candidates(row, gold))
        self.assertEqual({c[2]['kind'] for c in choices}, {'output_scale', 'node_bypass'})
        self.assertEqual(row, before)
        for _, result, _ in choices:
            self.assertFalse(result['issues'])
            self.assertNotEqual(result['value'], '1.4')

    def test_deleted_node_references_are_rewired_and_later_indices_shift(self):
        row, _ = self.fixture()
        choices = [(p, c) for p, c in proposals(row['target']) if c == {
            'kind': 'node_bypass', 'step': 0, 'keep_operand': 'left'}]
        self.assertEqual(len(choices), 1)
        changed, _ = choices[0]
        self.assertEqual(len(changed['steps']), 2)
        self.assertEqual(changed['steps'][-1]['right'], '#0')
        self.assertEqual(changed['steps'][-1]['left'], row['target']['steps'][0]['left'])
        answer = compile_plan(changed, atom_catalog(row['public']['evidence']))
        self.assertEqual(execute(answer['steps'], row['public']['evidence'])['value'], '2')

    def test_multiple_consumers_of_deleted_node_are_all_rewired(self):
        row, _ = self.fixture()
        row['target']['steps'][1]['left'] = '#0'
        for plan, change in proposals(row['target']):
            if change == {'kind': 'node_bypass', 'step': 0, 'keep_operand': 'right'}:
                self.assertEqual(plan['steps'][0]['left'], row['target']['steps'][0]['right'])
                self.assertEqual(plan['steps'][1]['left'], row['target']['steps'][0]['right'])
                answer = compile_plan(plan, atom_catalog(row['public']['evidence']))
                self.assertFalse(execute(answer['steps'], row['public']['evidence'])['issues'])

    def test_program_length_and_causal_constraints_preserved(self):
        target = {'decision': 'ANSWER', 'answer_unit': 'number', 'steps': [
            {'op': 'add', 'left': 'CONST:1', 'right': 'CONST:2'}] + [
            {'op': 'add', 'left': '#' + str(i), 'right': 'CONST:1'} for i in range(7)]}
        choices = list(proposals(target))
        self.assertNotIn('output_scale', {c['kind'] for _, c in choices})
        for plan, _ in choices:
            self.assertLessEqual(len(plan['steps']), 8)
            for i, step in enumerate(plan['steps']):
                for side in ['left', 'right']:
                    if step[side].startswith('#'):
                        self.assertLess(int(step[side][1:]), i)

    def test_zero_scaling_is_not_falsely_labelled_negative(self):
        evidence = {'x': 'amount: 0'}
        ref = next(iter(atom_catalog(evidence)))
        row = {'public': {'evidence': evidence}, 'target': {'decision': 'ANSWER',
               'answer_unit': 'number', 'steps': [{'op': 'add', 'left': ref, 'right': 'CONST:0'}]}}
        self.assertEqual(list(extension_candidates(row, {'qa': {'answer': '0', 'exe_ans': 0}})), [])

    def test_selection_is_candidate_order_invariant(self):
        row, gold = self.fixture(); choices = list(extension_candidates(row, gold))
        selected = [selected_extension(str(i), choices) for i in range(20)]
        self.assertTrue(any(x is None for x in selected))
        self.assertTrue(any(x is not None for x in selected))
        for i, item in enumerate(selected):
            self.assertEqual(item, selected_extension(str(i), list(reversed(choices))))

    def test_source_pairs_must_preserve_identity_split_and_group(self):
        rows = [{'original_source_id': 'one', 'source_id': 'one::' + kind,
                 'target': {'verdict': verdict}, 'split': 'train', 'report_group': 'group'}
                for kind, verdict in [('reference', 'PASS'), ('mutation', 'FAIL')]]
        self.assertEqual(len(paired(rows)), 1)
        with self.assertRaises(ValueError):
            paired(rows + [rows[0]])
        bad = deepcopy(rows); bad[1]['split'] = 'validation'
        with self.assertRaises(ValueError):
            paired(bad)


if __name__ == '__main__':
    unittest.main()
