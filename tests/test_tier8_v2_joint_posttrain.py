from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tier8_v2_joint_posttrain import complete_sas, sha


class JointQueueGateTests(unittest.TestCase):
    def test_fit_success_cannot_release_full_training_queue(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'plan.json').write_text('{}')
            (root / 'state.json').write_text(json.dumps({'state': 'complete', 'fit_only': True}))
            with self.assertRaisesRegex(ValueError, 'full epoch'):
                complete_sas(root, sha(root / 'plan.json'))

    def test_incomplete_counts_nonfinite_validation_and_memory_breach_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'plan.json').write_text(json.dumps({'training_n': 3801, 'host_tree_cap_bytes': 10500000000}))
            state = {'state': 'complete', 'fit_only': False, 'peak_tree_rss_bytes': 8300000000}
            (root / 'state.json').write_text(json.dumps(state))
            manifest = {'profile': '7b', 'training_tasks': ['drafter', 'critic']}
            summary = {'mode': 'train', 'examples_processed': 3801, 'optimizer_updates': 476,
                       'validation_teacher_forced_loss': 0.5}
            with patch('tier8_v2_joint_posttrain.check_inputs'), patch(
                    'tier8_v2_joint_posttrain.validate_adapter', return_value=(manifest, summary, None)):
                self.assertEqual(complete_sas(root, sha(root / 'plan.json')), summary)
                for change in ({'examples_processed': 2}, {'optimizer_updates': 2},
                               {'validation_teacher_forced_loss': float('nan')}, {'mode': 'fit'}):
                    with patch('tier8_v2_joint_posttrain.validate_adapter', return_value=(manifest, {**summary, **change}, None)):
                        with self.assertRaisesRegex(ValueError, 'incomplete'):
                            complete_sas(root, sha(root / 'plan.json'))
                (root / 'state.json').write_text(json.dumps({**state, 'peak_tree_rss_bytes': 10500000001}))
                with self.assertRaisesRegex(ValueError, 'incomplete'):
                    complete_sas(root, sha(root / 'plan.json'))


if __name__ == '__main__':
    unittest.main()
