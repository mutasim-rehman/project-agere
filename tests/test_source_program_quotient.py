import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evidence_atoms import atom_catalog
from source_program_quotient import analyze, equivalent, partition


def plan(*steps, unit='number'):
    return {'decision': 'ANSWER', 'answer_unit': unit,
            'steps': [dict(zip(('op', 'left', 'right'), s)) for s in steps]}


class QuotientTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {'s1': 'Revenue 10, expenses 5, prior revenue 10, tax 3.'}
        self.atoms = atom_catalog(self.evidence)

    def compare(self, a, b, **limits):
        return equivalent(analyze(a, self.atoms, self.evidence),
                          analyze(b, self.atoms, self.evidence), **limits)

    def test_commutation_and_distributivity(self):
        a = plan(('add', 'A000', 'A001'), ('multiply', '#0', 'A003'))
        b = plan(('multiply', 'A003', 'A001'), ('multiply', 'A000', 'A003'), ('add', '#1', '#0'))
        self.assertTrue(self.compare(a, b)['equivalent'])

    def test_ratio_rewrite_preserves_division_domain(self):
        a = plan(('subtract', 'A000', 'A001'), ('divide', '#0', 'A001'))
        b = plan(('divide', 'A000', 'A001'), ('subtract', '#0', 'CONST:1'))
        self.assertTrue(self.compare(a, b)['equivalent'])

    def test_equal_values_do_not_merge_distinct_sources(self):
        a, b = plan(('add', 'A000', 'A001')), plan(('add', 'A002', 'A001'))
        self.assertEqual(self.compare(a, b)['reason'], 'sources')
        self.assertEqual(partition([a, b], self.atoms, self.evidence, mode='numeric')['groups'], [[0, 1]])
        self.assertEqual(partition([a, b], self.atoms, self.evidence)['groups'], [[0], [1]])

    def test_same_value_sources_but_distinct_function_not_merged(self):
        # Both give1 for this document, with exactly the same source footprint.
        a = plan(('subtract', 'A000', 'A001'), ('divide', '#0', 'A001'))
        b = plan(('subtract', 'A000', 'A000'), ('add', '#0', 'A001'), ('divide', '#1', 'A001'))
        self.assertFalse(self.compare(a, b)['equivalent'])
        self.assertEqual(self.compare(a, b)['reason'], 'different_rational_functions')
        self.assertEqual(partition([a, b], self.atoms, self.evidence, mode='numeric_sources')['groups'], [[0, 1]])

    def test_cancellation_does_not_erase_domain(self):
        a = plan(('divide', 'A000', 'A000'))
        b = plan(('subtract', 'A000', 'A000'), ('add', '#0', 'CONST:1'))
        self.assertEqual(self.compare(a, b)['reason'], 'guards')

    def test_units_distinct(self):
        a = plan(('divide', 'A000', 'A001'))
        b = plan(('divide', 'A000', 'A001'), unit='percent')
        self.assertEqual(self.compare(a, b)['reason'], 'unit')

    def test_decimal_rounding_prevents_merge(self):
        a = plan(('divide', 'A000', 'A003'), ('multiply', '#0', 'A003'))
        b = plan(('multiply', 'A000', 'A003'), ('divide', '#0', 'A003'))
        self.assertEqual(self.compare(a, b)['reason'], 'observed')

    def test_work_exhaustion_never_merges(self):
        a = plan(('add', 'A000', 'A001'))
        result = partition([a, a], self.atoms, self.evidence, max_operations=0)
        self.assertEqual(result['groups'], [[0], [1]])
        self.assertTrue(all(v['status'] == 'unknown' for v in result['analyses']))
        total = partition([a] * 64, self.atoms, self.evidence, max_total_operations=10)
        self.assertLessEqual(total['symbolic_operations'], 10)
        self.assertEqual(sum(map(len, total['groups'])), 64)

    def test_invalid_and_abstention_never_merge(self):
        a = plan(('divide', 'A000', 'CONST:0'))
        b = {'decision': 'INSUFFICIENT', 'answer_unit': 'number', 'steps': []}
        self.assertEqual(partition([a, a, b, b], self.atoms, self.evidence)['groups'], [[0], [1], [2], [3]])

    def test_stable_groups_and_candidate_cap(self):
        a, b = plan(('add', 'A000', 'A001')), plan(('add', 'A001', 'A000'))
        self.assertEqual(partition([a, b, a], self.atoms, self.evidence)['groups'], [[0, 1, 2]])
        self.assertEqual(partition([a, b, a], self.atoms, self.evidence, mode='bytes')['groups'], [[0, 2], [1]])
        with self.assertRaisesRegex(ValueError, 'candidate_limit'):
            partition([a] * 65, self.atoms, self.evidence)


if __name__ == '__main__':
    unittest.main()
