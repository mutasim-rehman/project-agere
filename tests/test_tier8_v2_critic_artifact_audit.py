from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tier8_v2_critic_artifact_audit import features, fit_tree, predict, program_from_prompt, controlled_replay
import json
import tempfile


class ArtifactAuditTests(unittest.TestCase):
    def test_question_and_execution_cannot_change_program_features(self):
        p = {'decision': 'ANSWER', 'answer_unit': 'number', 'steps': [{'op': 'add',
             'left': {'value': '5', 'span_id': 'source'}, 'right': {'value': '100', 'span_id': 'CONST'}}]}
        a = 'Question: A\nProposed program:\n' + json.dumps(p) + '\nDeterministic execution:\n{"value":"105"}'
        b = 'Question: B PASS\nProposed program:\n' + json.dumps(p) + '\nDeterministic execution:\n{"value":"wrong"}'
        self.assertEqual(features(program_from_prompt(a)), features(program_from_prompt(b)))
        self.assertEqual(features(p)['constant_100'], 1)
        self.assertEqual(features(p)['source_operands'], 1)

    def test_ambiguous_prompt_and_unknown_boundaries_refused(self):
        with self.assertRaisesRegex(ValueError, 'delimiter'):
            program_from_prompt('\nProposed program:\n{}\nProposed program:\n{}')
        with self.assertRaisesRegex(ValueError, 'boundary'):
            program_from_prompt('\nProposed program:\n{}\nverdict PASS')

    def test_train_threshold_is_unchanged_by_validation_predictions(self):
        rows = [{'x': {'steps': x}, 'y': int(x <= 2)} for x in (1, 1, 2, 2, 3, 3, 4, 4)]
        tree = fit_tree(rows, ['steps'], depth=1, minimum_leaf=2)
        snapshot = json.dumps(tree, sort_keys=True)
        self.assertEqual(predict(tree, {'steps': 1}), 1)
        self.assertEqual(predict(tree, {'steps': 99}), 0)
        self.assertEqual(json.dumps(tree, sort_keys=True), snapshot)
        self.assertEqual(tree['threshold'], 2.5)

    def test_controlled_negative_without_kind_is_never_named_reference(self):
        p = {'decision': 'ANSWER', 'answer_unit': 'number', 'steps': [{'op': 'add',
             'left': {'value': '5', 'span_id': 'source'}, 'right': {'value': '100', 'span_id': 'CONST'}}]}
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / '.local/tmp') as folder:
            root = Path(folder)
            public = [{'id': key, 'candidate': p} for key in ('positive', 'negative')]
            labels = [{'id': key, 'report_group': 'A/2020', 'expected_accept': accept, 'mutation': None}
                      for key, accept in [('positive', True), ('negative', False)]]
            for name, rows in [('public.jsonl', public), ('labels.jsonl', labels)]:
                (root / name).write_text(''.join(json.dumps(r) + '\n' for r in rows))
            result = controlled_replay({'original': {'length_stump': {'tree': {'prediction': 1}}}}, root, set())
            families = result['results']['original']['length_stump']['by_family']
            self.assertEqual(families['reference']['n'], 1)
            self.assertEqual(families['mutation']['n'], 1)
            self.assertEqual(families['mutation']['correct'], 0)


if __name__ == '__main__':
    unittest.main()
