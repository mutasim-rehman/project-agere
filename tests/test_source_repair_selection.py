from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from binary_verifier_score import VerificationBudget, select_representatives
from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import execute
from source_program_quotient import partition
from source_repair_pool import local_pool


def plan(op='add', left='A000', right='A001'):
    return {'decision': 'ANSWER', 'answer_unit': 'number',
            'steps': [{'op': op, 'left': left, 'right': right}]}


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.public = {'id': 'example', 'question': 'Compute total.',
                       'evidence': {'s1': 'Revenue 10, expense 5, prior 10.', 's2': 'Tax 3.'}}
        self.atoms = atom_catalog(self.public['evidence'])

    def test_pool_is_public_deterministic_executable_and_bounded(self):
        first = local_pool(self.public, plan(), plan('subtract'), maximum=12)
        self.assertEqual(first, local_pool(self.public, plan(), plan('subtract'), maximum=12))
        self.assertEqual(first['plans'][:2], [plan(), plan('subtract')])
        self.assertEqual(len(first['plans']), 12)
        for p in first['plans']:
            self.assertFalse(execute(compile_plan(p, self.atoms)['steps'], self.public['evidence'])['issues'])
        self.assertTrue({'operation', 'source', 'scale'} <= {v['family'] for v in first['origins']})
        self.assertFalse(any(v['family'] == 'order' for v in first['origins']))
        with self.assertRaisesRegex(ValueError, 'public'):
            local_pool({**self.public, 'gold': 15}, plan())

    def test_invalid_draft_can_be_rescued_only_by_actual_regeneration(self):
        bad = plan('divide', 'A000', 'CONST:0')
        result = local_pool(self.public, bad, plan())
        self.assertEqual(result['plans'], [plan()])
        self.assertEqual(result['origins'], [{'family': 'regenerated'}])

    def test_duplicate_forms_cannot_amplify_margin_or_votes(self):
        a, b = plan(), plan(left='A001', right='A000')
        plans = [a, b, a, plan('subtract')]
        grouping = partition(plans, self.atoms, self.public['evidence'])
        called = []
        def scorer(index, candidate):
            called.append(index)
            return {'status': 'scored', 'pass_margin': 1.0}
        result = select_representatives(plans, grouping, scorer)
        self.assertEqual(called, [0, 3])
        self.assertEqual(result['selected_index'], 0)

    def test_budget_denial_does_not_block_a_cheaper_later_candidate(self):
        plans = [plan(), plan('subtract')]
        grouping = partition(plans, self.atoms, self.public['evidence'])
        def scorer(index, candidate):
            return {'status': 'no_budget'} if index == 0 else {'status': 'scored', 'pass_margin': 0.1}
        self.assertEqual(select_representatives(plans, grouping, scorer)['selected_index'], 1)

    def test_symbolic_unknown_remains_individually_scoreable(self):
        plans = [plan(), plan()]
        grouping = partition(plans, self.atoms, self.public['evidence'], max_operations=0)
        result = select_representatives(plans, grouping,
                                       lambda i, p: {'status': 'scored', 'pass_margin': float(i)})
        self.assertEqual(len(result['events']), 2)
        self.assertEqual(result['selected_index'], 1)

    def test_nonpositive_margins_withhold_and_nonfinite_rejected(self):
        grouping = partition([plan()], self.atoms, self.public['evidence'])
        for value in [0.0, -1.0]:
            result = select_representatives([plan()], grouping,
                                           lambda i, p: {'status': 'scored', 'pass_margin': value})
            self.assertFalse(result['delivered'])
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            select_representatives([plan()], grouping,
                                   lambda i, p: {'status': 'scored', 'pass_margin': float('nan')})

    def test_prefill_and_check_caps_both_enforced(self):
        budget = VerificationBudget(max_prefill_tokens=10, max_checks=2)
        budget.charge(7)
        self.assertFalse(budget.can_charge(4))
        budget.charge(3)
        self.assertEqual((budget.prefill_tokens, budget.checks), (10, 2))
        with self.assertRaisesRegex(ValueError, 'exhausted'):
            budget.charge(1)
        for value in [-1, 0, True, 1.5]:
            with self.assertRaisesRegex(ValueError, 'charge'):
                budget.can_charge(value)


if __name__ == '__main__':
    unittest.main()
