from pathlib import Path
import sys
import hashlib
import json
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tier8_v2_quartet_probe import select_training, analyze


class QuartetProbeTests(unittest.TestCase):
    def data(self, n=10):
        rows = []
        for i in range(n):
            for j, label in enumerate(('PASS', 'FAIL', 'FAIL', 'PASS')):
                rows.append({'source_id': f'{i:02d}::{j}', 'quartet_id': f'{i:02d}', 'report_group': 'r' + str(i // 2),
                    'split': 'train', 'target': {'verdict': label}, 'prompt': f'prompt{i}:{j}'})
        return rows

    def responses(self, rows, verdict='UNKNOWN'):
        return [{'source_id': r['source_id'], 'prompt_sha256': hashlib.sha256(r['prompt'].encode()).hexdigest(),
                 'verdict': verdict, 'prompt_tokens': 3, 'generated_tokens': 1,
                 'response': json.dumps({'verdict': verdict}),
                 'finish_reason': 'stop', 'seconds': 1.} for r in rows]

    def test_selection_keeps_whole_quartets_and_one_per_training_report(self):
        rows = self.data()
        rows.extend({**r, 'source_id': 'v' + r['source_id'], 'quartet_id': 'v' + r['quartet_id'], 'split': 'validation'} for r in self.data())
        selected = select_training(rows[::-1], count=4)
        self.assertEqual(len(selected), 16)
        self.assertEqual({r['quartet_id'] for r in selected}, {'00', '02', '04', '06'})
        self.assertEqual({r['split'] for r in selected}, {'train'})
        self.assertEqual(len({r['report_group'] for r in selected}), 4)

    def test_partial_quartet_refused_before_inference(self):
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            select_training(self.data()[:-1], count=8)

    def test_unknown_all_is_zero_exact_not_correct_negative_claim(self):
        rows = self.data(2)
        result = analyze(rows, self.responses(rows))
        self.assertEqual(result['exact_label_correct'], 0)
        self.assertEqual(result['gate_accuracy'], .5)
        self.assertEqual(result['complete_exact_quartets'], 0)
        self.assertEqual(result['cross_negative_accepts'], 0)

    def test_missing_duplicate_or_changed_prompt_outputs_refused(self):
        rows = self.data(2)
        saved = self.responses(rows)
        with self.assertRaisesRegex(ValueError, 'Unmatched'):
            analyze(rows, saved[:-1])
        with self.assertRaisesRegex(ValueError, 'Unmatched'):
            analyze(rows, saved + saved[:1])
        saved[0]['prompt_sha256'] = 'bad'
        with self.assertRaisesRegex(ValueError, 'prompt changed'):
            analyze(rows, saved)

    def test_mislabelled_raw_response_or_impossible_token_usage_refused(self):
        rows = self.data(2)
        saved = self.responses(rows)
        saved[0]['verdict'] = 'PASS'
        with self.assertRaisesRegex(ValueError, 'actual response'):
            analyze(rows, saved)
        saved = self.responses(rows)
        saved[0]['generated_tokens'] = 193
        with self.assertRaisesRegex(ValueError, 'usage'):
            analyze(rows, saved)


if __name__ == '__main__':
    unittest.main()
