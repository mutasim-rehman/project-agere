from pathlib import Path
import sys
from copy import deepcopy
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tier8_v2_continuation_data import extended_control, select_replay
from tier8_v2_critic_quartets import crossed
from tier8_v2_critic_data import prompt
from evidence_calculator import execute


class ContinuationDataTests(unittest.TestCase):
    def fixture(self):
        evidence = {'s': 'Amount5'}
        def program(op, c):
            return {'decision': 'ANSWER', 'answer_unit': 'number', 'steps': [{'op': op,
                'left': {'value': '5', 'span_id': 's'}, 'right': {'value': c, 'span_id': 'CONST'}}]}
        sources = [{'id': f'R/p.pdf-{i}', 'page': 'R/p.pdf', 'report_group': 'R', 'split': 'train',
                    'public': {'question': q, 'evidence': evidence}, 'candidate': p}
                   for i, q, p in [(0, 'Add one?', program('add', '1')), (1, 'Double?', program('multiply', '2'))]]
        # Standalone numeric token, rather than a digit embedded in a word.
        for source in sources:
            source['public']['evidence'] = {'s': 'Amount 5'}
        evidence = sources[0]['public']['evidence']
        gold = {r['id']: {'qa': {'exe_ans': n, 'answer': str(n)}} for r, n in zip(sources, (6, 10))}
        negatives = {}
        for source, p in zip(sources, (program('subtract', '1'), program('add', '2'))):
            negatives[source['id']] = {'prompt': prompt(source['public'], p, execute(p['steps'], evidence)),
                                       'mutation': {'kind': 'operation'}}
        return sources, gold, negatives

    def test_only_negatives_changed_and_same_source_question_evidence_target(self):
        sources, gold, negatives = self.fixture()
        quartet = crossed(*sources, gold)
        before = deepcopy(quartet)
        control = extended_control(quartet, negatives, gold)
        self.assertEqual(quartet, before)
        self.assertEqual(control[0], quartet[0])
        self.assertEqual(control[3], quartet[3])
        for index in (1, 2):
            self.assertNotEqual(control[index]['candidate'], quartet[index]['candidate'])
            for key in ('question', 'evidence', 'target', 'report_group', 'split'):
                self.assertEqual(control[index][key], quartet[index][key])

    def test_invalid_existing_negative_cannot_silently_be_used(self):
        sources, gold, negatives = self.fixture()
        p = sources[0]['candidate']
        negatives[sources[0]['id']]['prompt'] = prompt(sources[0]['public'], p, execute(p['steps'], sources[0]['public']['evidence']))
        with self.assertRaisesRegex(ValueError, 'wrong under both'):
            extended_control(crossed(*sources, gold), negatives, gold)

    def test_rehearsal_prefers_reports_and_fills_sources_without_duplicates(self):
        items = [(str(i), 'r' + str(i % 2), [{'id': i}]) for i in range(5)]
        selected = select_replay(items, 3, 'fixed')
        self.assertEqual(len({r['id'] for r in selected}), 3)
        self.assertEqual(len({r['id'] % 2 for r in selected[:2]}), 2)
        self.assertEqual(selected, select_replay(items[::-1], 3, 'fixed'))
        with self.assertRaisesRegex(ValueError, 'Insufficient'):
            select_replay(items, 6, 'fixed')


if __name__ == '__main__':
    unittest.main()
