"""Offline lab integrity tests. Fixture workers never load a neural model."""
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import lab_tiers as runner
from lab_tiers_common import completed_cases, gguf_file_type, inside, read, sha, verify, write
from lab_tiers_analyze import paired


def row(identifier):
    return {'case_id': identifier, 'delivered': False, 'score': {'case_success': False, 'raw_execution_match': False},
        'initial_score': {'case_success': False, 'raw_execution_match': False}, 'tokens': 0, 'stages': []}


class LabIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.local')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_completed_prefix_rejects_duplicate_or_reordered_cases(self):
        p = self.root / 'cases.jsonl'
        for ids in [('b',), ('a', 'a')]:
            p.write_text(''.join(json.dumps(row(i)) + '\n' for i in ids))
            with self.assertRaisesRegex(ValueError, 'exact unique frozen prefix'):
                completed_cases(p, ['a', 'b'])

    def test_torn_last_line_is_preserved_and_only_completed_records_recovered(self):
        p = self.root / 'cases.jsonl'
        prefix = json.dumps(row('a')).encode() + b'\n'
        torn = b'{"case_id":"b"'
        p.write_bytes(prefix + torn)
        records = completed_cases(p, ['a', 'b'], repair_tail=True)
        self.assertEqual([x['case_id'] for x in records], ['a'])
        self.assertEqual(p.read_bytes(), prefix)
        self.assertEqual(next(self.root.glob('*.torn-*')).read_bytes(), torn)
        p.write_bytes(prefix + b'not json\n')
        with self.assertRaises(ValueError):
            completed_cases(p, ['a', 'b'], repair_tail=True)

    def test_complete_json_without_newline_does_not_concatenate_on_resume(self):
        p = self.root / 'cases.jsonl'
        p.write_text(json.dumps(row('a')))
        completed_cases(p, ['a', 'b'], repair_tail=True)
        self.assertTrue(p.read_bytes().endswith(b'\n'))

    def test_hash_cache_detects_same_size_mutation(self):
        p = self.root / 'input'
        p.write_text('one')
        expected, cache = sha(p), {}
        verify(p, expected, cache)
        p.write_text('two')
        with self.assertRaisesRegex(ValueError, 'Changed input'):
            verify(p, expected, cache)

    def test_paths_cannot_escape_ssd(self):
        for value in ('../outside', '/tmp/outside'):
            with self.assertRaises(ValueError):
                inside(self.root, value)

    def test_freeze_rejects_modified_code(self):
        p = self.root / 'scripts/example.py'
        p.parent.mkdir()
        p.write_text('x=1\n')
        write(self.root / 'configs/lab_tiers/freeze.json', {'status': 'sealed_for_lab', 'code_sha256': {'scripts/example.py': sha(p)}})
        with patch.object(runner, 'ROOT', self.root):
            runner.freeze_check()
            p.write_text('x=2\n')
            with self.assertRaisesRegex(ValueError, 'differs from frozen'):
                runner.freeze_check()

    def test_precision_metadata_is_read_without_tensor_loading(self):
        p = self.root / 'metadata.gguf'
        key = b'general.file_type'
        p.write_bytes(b'GGUF' + struct.pack('<IQQ', 3, 0, 1) + struct.pack('<Q', len(key)) + key + struct.pack('<II', 4, 15))
        self.assertEqual(gguf_file_type(p), 15)

    def test_paired_analysis_requires_real_pairs_and_reports_cluster_count(self):
        def v(correct, delivered=True):
            return {'delivered': delivered, 'score': {'case_success': correct}}
        left = {'a': v(False), 'b': v(False), 'c': v(True)}
        right = {'a': v(True), 'b': v(False, False), 'c': v(True)}
        groups = {'a': 'r1', 'b': 'r1', 'c': 'r2'}
        result = paired(left, right, groups, 'case_success', repeats=200)
        self.assertEqual(result['reports'], 2)
        self.assertEqual(result['delta_counts'], {'correct_delivered': 1, 'wrong_delivered': -2, 'withheld': 1})
        self.assertEqual(result, paired(left, right, groups, 'case_success', repeats=200))
        with self.assertRaises(ValueError):
            paired(left, {'a': right['a']}, groups, 'case_success')

    def fixture_code(self, slow=False):
        code = self.root / 'code'
        (code / 'scripts').mkdir(parents=True)
        write(code / 'configs/lab_tiers/protocol.json', {})
        write(code / 'configs/lab_tiers/freeze.json', {'code_sha256': {}})
        source = '''import json,sys,time
from pathlib import Path
folder=Path(sys.argv[sys.argv.index('--job-dir')+1])
'''
        if slow:
            source += 'time.sleep(10)\n'
        else:
            source += '''ids=json.loads((folder/'manifest.json').read_text())['dataset']['ids']
p=folder/'cases.jsonl'
n=len(p.read_text().splitlines()) if p.exists() else 0
for key in ids[n:]:
 r={'case_id':key,'delivered':False,'score':{'case_success':False,'raw_execution_match':False},'initial_score':{'case_success':False,'raw_execution_match':False},'tokens':0,'stages':[]}
 with p.open('a') as f:f.write(json.dumps(r)+'\\n')
print('Fixture only: no neural calls')
'''
        (code / 'scripts/lab_tiers.py').write_text(source)
        return code

    def test_monitored_resume_skips_completed_cases_and_retains_attempt_logs(self):
        code = self.fixture_code()
        out = self.root / 'run'
        out.mkdir()
        folder = out / 'tier16-sas-primary'
        folder.mkdir()
        (folder / 'cases.jsonl').write_text(json.dumps(row('a')) + '\n')
        spec = {'dataset': {'ids': ['a', 'b'], 'n': 2}}
        job = {'tier': 16, 'arm': 'sas', 'profile': 'primary'}
        with patch.object(runner, 'verify_inputs'), patch.dict(os.environ, {'AGERE_PYTHON_LAUNCHER': sys.executable}):
            runner.monitor_job(self.root, out, code, job, 512000000, {}, spec)
        summary = read(folder / 'summary.json')
        self.assertEqual(summary['n'], 2)
        self.assertEqual(summary['resumed_cases'], 1)
        self.assertTrue((folder / 'attempt-0001/worker.log').exists())
        self.assertGreater(summary['sampled_peak_tree_rss_bytes'], 0)
        with patch.object(runner.subprocess, 'Popen', side_effect=AssertionError('No repeat worker')):
            runner.monitor_job(self.root, out, code, job, 512000000, {}, spec)
        manifest = read(folder / 'manifest.json')
        manifest['cap_bytes'] += 1
        write(folder / 'manifest.json', manifest)
        with self.assertRaisesRegex(ValueError, 'Resume would change'):
            runner.monitor_job(self.root, out, code, job, 512000000, {}, spec)

    def test_breach_kills_only_owned_fixture_worker_and_blocks_resume(self):
        code = self.fixture_code(slow=True)
        out = self.root / 'run'
        out.mkdir()
        spec = {'dataset': {'ids': ['a'], 'n': 1}}
        job = {'tier': 16, 'arm': 'sas', 'profile': 'primary'}
        with patch.object(runner, 'verify_inputs'), patch.dict(os.environ, {'AGERE_PYTHON_LAUNCHER': sys.executable}):
            with self.assertRaisesRegex(ValueError, 'Worker failed'):
                runner.monitor_job(self.root, out, code, job, 1000000, {}, spec)
            folder = out / 'tier16-sas-primary'
            self.assertTrue(read(folder / 'attempt-0001/state.json')['memory_breach'])
            self.assertFalse((folder / 'summary.json').exists())
            with self.assertRaisesRegex(ValueError, 'memory breach invalidated'):
                runner.monitor_job(self.root, out, code, job, 1000000, {}, spec)

    def test_resume_recovers_peak_after_controller_loss_and_preserves_torn_sample(self):
        code = self.fixture_code()
        out = self.root / 'run'
        attempt = out / 'tier16-sas-primary/attempt-0001'
        attempt.mkdir(parents=True)
        write(attempt / 'state.json', {'status': 'running', 'worker': {'pid': 999999999, 'create_time': 0}})
        (attempt / 'memory.jsonl').write_bytes(b'{"tree_rss_bytes":123,"tree_swap_bytes":0}\n{"tree_rss')
        spec = {'dataset': {'ids': ['a'], 'n': 1}}
        job = {'tier': 16, 'arm': 'sas', 'profile': 'primary'}
        with patch.object(runner, 'verify_inputs'), patch.dict(os.environ, {'AGERE_PYTHON_LAUNCHER': sys.executable}):
            runner.monitor_job(self.root, out, code, job, 512000000, {}, spec)
        self.assertEqual(read(attempt / 'state.json')['peak_tree_rss_bytes'], 123)
        self.assertEqual(len(list(attempt.glob('state-before-recovery-*'))), 1)
        self.assertEqual(next(attempt.glob('memory.jsonl.torn-*')).read_bytes(), b'{"tree_rss')


if __name__ == '__main__':
    unittest.main()
