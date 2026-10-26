from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from tier8_v2_matched_sequence import require_fresh


class FreshSequenceJobs(unittest.TestCase):
    def test_prepared_controller_is_allowed_but_started_controller_is_not(self):
        with tempfile.TemporaryDirectory() as temp, \
                patch('tier8_v2_matched_sequence.artifact_path', side_effect=Path):
            root = Path(temp); job = {'name': 'train-x', 'kind': 'train', 'result': str(root)}
            with self.assertRaises(ValueError):
                require_fresh(job)
            (root / 'plan.json').write_text('{}')
            require_fresh(job)
            (root / 'state.json').write_text('{"state":"failed"}')
            with self.assertRaises(ValueError):
                require_fresh(job)

    def test_natural_or_proof_output_must_not_exist(self):
        with tempfile.TemporaryDirectory() as temp, \
                patch('tier8_v2_matched_sequence.artifact_path', side_effect=Path):
            target = Path(temp) / 'proof'
            for kind in ('proof', 'natural'):
                require_fresh({'name': kind, 'kind': kind, 'result': str(target)})
            target.mkdir()
            with self.assertRaises(ValueError):
                require_fresh({'name': 'proof', 'kind': 'proof', 'result': str(target)})


if __name__ == '__main__':
    unittest.main()
