from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tier8_v2_critic_quartets import crossed, verify_balance
from tier8_v2_critic_artifact_audit import features, fit_tree, predict


class QuartetTests(unittest.TestCase):
    def pair(self):
        rows = []
        for index, (op, constant) in enumerate([('add', '1'), ('multiply', '2')]):
            rows.append({'id': 'R/2020/p.pdf-' + str(index), 'page': 'R/2020/p.pdf',
                'report_group': 'R/2020', 'split': 'train',
                'public': {'question': ['Amount plus one?', 'Twice the amount?'][index],
                           'evidence': {'source': 'Amount 5'}},
                'candidate': {'decision': 'ANSWER', 'answer_unit': 'number', 'steps': [{'op': op,
                    'left': {'value': '5', 'span_id': 'source'}, 'right': {'value': constant, 'span_id': 'CONST'}}]}})
        gold = {r['id']: {'qa': {'exe_ans': value, 'answer': str(value)}} for r, value in zip(rows, [6, 10])}
        return rows, gold

    def test_exact_program_and_question_marginals_balanced(self):
        sources, gold = self.pair()
        rows = crossed(*sources, gold)
        self.assertTrue(verify_balance(rows))
        self.assertEqual([r['target']['verdict'] for r in rows], ['PASS', 'FAIL', 'FAIL', 'PASS'])
        self.assertEqual(rows[0]['candidate'], rows[2]['candidate'])
        self.assertEqual(rows[0]['question'], rows[1]['question'])
        self.assertTrue(all(r['evidence'] == rows[0]['evidence'] for r in rows))
        examples = [{'x': features(r['candidate']), 'y': int(r['target']['verdict'] == 'PASS')} for r in rows]
        tree = fit_tree(examples, sorted(examples[0]['x']), depth=3, minimum_leaf=1)
        self.assertEqual(sum(predict(tree, r['x']) == r['y'] for r in examples), 2)

    def test_missing_or_relabelled_quartet_is_rejected(self):
        sources, gold = self.pair()
        rows = crossed(*sources, gold)
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            verify_balance(rows[:3])
        rows[1]['target'] = {'verdict': 'PASS'}
        with self.assertRaisesRegex(ValueError, 'Unbalanced'):
            verify_balance(rows)

    def test_positive_rows_also_receive_both_questions_source_union(self):
        sources, gold = self.pair()
        before = deepcopy(sources)
        sources[1]['public']['evidence']['extra'] = 'Another source measure99'
        rows = crossed(*sources, gold)
        self.assertIn('extra', rows[0]['evidence'])
        self.assertTrue(all(r['evidence'] == rows[0]['evidence'] for r in rows))
        self.assertEqual(rows[0]['candidate'], before[0]['candidate'])
        self.assertNotIn('extra', sources[0]['public']['evidence'])

    def test_equal_numeric_answers_cannot_be_called_negative(self):
        sources, gold = self.pair()
        gold[sources[1]['id']] = {'qa': {'exe_ans': 6, 'answer': '6'}}
        with self.assertRaisesRegex(ValueError, 'not wrong'):
            crossed(*sources, gold)

    def test_source_collision_unit_or_report_split_changes_rejected(self):
        sources, gold = self.pair()
        for field, value in [('split', 'validation'), ('page', 'R/2020/other.pdf')]:
            altered = deepcopy(sources)
            altered[1][field] = value
            with self.assertRaisesRegex(ValueError, 'same-page'):
                crossed(*altered, gold)
        altered = deepcopy(sources)
        altered[1]['public']['evidence']['source'] = 'Amount 8'
        with self.assertRaisesRegex(ValueError, 'collision'):
            crossed(*altered, gold)
        altered = deepcopy(sources)
        altered[1]['candidate']['answer_unit'] = 'percent'
        with self.assertRaisesRegex(ValueError, 'units'):
            crossed(*altered, gold)


if __name__ == '__main__':
    unittest.main()
