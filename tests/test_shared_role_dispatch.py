import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from tier8_v2_shared_role_dispatch import require_complete


class DispatchCompletion(unittest.TestCase):
    def test_all_jobs_are_reverified_after_exact_completion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); jobs = [{'name': str(i)} for i in range(8)]
            state = {'state': 'complete', 'all_jobs_finished': True}
            events = [{'state': 'job_complete', 'job': j['name']} for j in jobs] + [state]
            (root / 'state.json').write_text(json.dumps(state))
            (root / 'journal.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))
            with patch('tier8_v2_shared_role_dispatch.check_inputs') as inputs, \
                    patch('tier8_v2_shared_role_dispatch.verify_result') as verify:
                require_complete(root, {'jobs': jobs})
                inputs.assert_called_once()
                self.assertEqual([c.args[0] for c in verify.call_args_list], jobs)

    def test_incomplete_or_missing_job_never_dispatches(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); jobs = [{'name': str(i)} for i in range(8)]
            for state in ({'state': 'failed', 'all_jobs_finished': False},
                          {'state': 'complete', 'all_jobs_finished': True}):
                events = [{'state': 'job_complete', 'job': j['name']} for j in jobs[:-1]] + [state]
                (root / 'state.json').write_text(json.dumps(state))
                (root / 'journal.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))
                with patch('tier8_v2_shared_role_dispatch.verify_result') as verify:
                    with self.assertRaises(ValueError):
                        require_complete(root, {'jobs': jobs})
                    verify.assert_not_called()


if __name__ == '__main__':
    unittest.main()
