from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tier8_v2_sequence_recover import prefix, ReadOnlyHashCache


class ExplicitRecovery(unittest.TestCase):
    def setUp(self):
        self.jobs = [{'name': 'trained', 'kind': 'train', 'command': ['train']},
                     {'name': 'prepare-next', 'kind': 'prepare', 'command': ['prepare']}]
        self.events = [{'state': 'job_started', 'job': 'trained', 'command': ['train']},
            {'state': 'job_exited', 'job': 'trained', 'exit_code': 0, 'memory_breach': False},
            {'state': 'job_complete', 'job': 'trained'},
            {'state': 'job_started', 'job': 'prepare-next', 'command': ['prepare']}]

    def test_only_successful_prefix_and_interrupted_preparation_qualify(self):
        self.assertEqual(prefix(self.jobs, self.events), 1)
        for field, value in [('exit_code', 1), ('memory_breach', True)]:
            changed = [dict(x) for x in self.events]; changed[1][field] = value
            with self.assertRaises(ValueError): prefix(self.jobs, changed)
        changed = [dict(x) for x in self.jobs]; changed[1]['kind'] = 'train'
        with self.assertRaises(ValueError): prefix(changed, self.events)

    def test_rejects_unobserved_exit_changed_command_and_terminal_failure(self):
        for events in [self.events[:1] + self.events[2:],
                self.events + [{'state': 'failed'}],
                [{'state': 'job_exited', 'job': None, 'exit_code': 0, 'memory_breach': False}],
                [{'state': 'job_complete', 'job': None}]]:
            with self.assertRaises(ValueError): prefix(self.jobs, events)
        changed = [dict(x) for x in self.events]; changed[-1]['command'] = ['different']
        with self.assertRaises(ValueError): prefix(self.jobs, changed)

    def test_hash_cache_rereads_changed_input_and_rejects_change_during_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input'; path.write_text('a'); reads = []
            def digest(p): reads.append(p); return p.read_text()
            cache = ReadOnlyHashCache(digest)
            self.assertEqual(cache(path), 'a'); self.assertEqual(cache(path), 'a'); self.assertEqual(len(reads), 1)
            path.write_text('bb'); self.assertEqual(cache(path), 'bb'); self.assertEqual(len(reads), 2)
            def mutate(p): p.write_text('changed again'); return 'untrusted'
            with self.assertRaises(ValueError): ReadOnlyHashCache(mutate)(path)


if __name__ == '__main__': unittest.main()
