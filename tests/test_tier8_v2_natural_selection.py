import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tier8_v2_natural_selection import partition, public_packet
from tier8_v2_demo_retrieval import report_group


class NaturalSelectionTests(unittest.TestCase):
    def rows(self):
        return [{'id': f'{company}/2010/page_{page}.pdf-1', 'qa': {'answer': 'secret'}}
                for company in 'ABCDEFGH' for page in [1, 2]]

    def test_whole_report_exclusions_and_disjoint_partitions(self):
        result = partition(self.rows(), {'A/2010'}, 2, 2)
        groups = [{report_group(r['id']) for r in rows} for rows in result.values()]
        self.assertEqual([len(s) for s in groups], [3, 2, 2])
        self.assertEqual(len(set.union(*groups)), sum(map(len, groups)))
        self.assertNotIn('A/2010', set.union(*groups))
        self.assertEqual(sum(map(len, result.values())), 14)

    def test_labels_and_source_order_cannot_change_assignment(self):
        rows = self.rows()
        changed = copy.deepcopy(rows[::-1])
        for row in changed:
            row['qa']['answer'] = 'different'
        ids = lambda p: {k: [r['id'] for r in v] for k, v in p.items()}
        self.assertEqual(ids(partition(rows, set(), 2, 2)),
                         ids(partition(changed, set(), 2, 2)))

    def test_invalid_or_insufficient_sources_refused(self):
        for rows, a, b in [(self.rows()[:2], 1, 1), (self.rows() * 2, 1, 1),
                           ([], 1, 1), (self.rows(), 0, 1)]:
            with self.assertRaises(ValueError):
                partition(rows, set(), a, b)

    def test_public_packet_omits_labels_and_uses_training_split(self):
        row = {'id': 'A/2010/page_1.pdf-1', 'table': [['year', 'amount'], ['2010', '10']],
               'pre_text': ['Amount is ten.'], 'post_text': [],
               'qa': {'question': 'what amount in 2010?', 'answer': 'SECRET',
                      'program': 'SECRET', 'gold_inds': {'SECRET': 'SECRET'}}}
        packet = public_packet(row)
        self.assertEqual(packet['split'], 'train')
        self.assertNotIn('SECRET', str(packet))
        self.assertFalse(packet['retrieval']['gold_used'])


if __name__ == '__main__':
    unittest.main()
