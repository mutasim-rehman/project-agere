import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lab_tiers_resume_metadata import reconcile


class ResumeMetadata(unittest.TestCase):
    def test_one_page_is_audited_and_other_changes_refused(self):
        actual = int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines()
                          if line.startswith('MemTotal:'))) * 1024
        import os
        page = os.sysconf('SC_PAGE_SIZE')
        current = dict.fromkeys(('python', 'llama_cpp', 'numpy', 'psutil', 'cpu_runtime',
                                'runtime_manifest_sha256', 'cpu_model', 'host_id_sha256'), 'same')
        current['physical_ram_bytes'] = actual
        for delta, runtime_change in ((page, False), (2*page, False), (page, True)):
            with self.subTest(delta=delta, runtime_change=runtime_change), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                report = out / 'report.json'
                report.write_text(json.dumps({'status': 'passed', 'environment': current}))
                previous = {**current, 'physical_ram_bytes': actual - delta}
                if runtime_change:
                    previous['cpu_runtime'] = 'different'
                manifest = out / 'manifest.json'
                manifest.write_text(json.dumps({'environment': previous, 'protocol': 'unchanged'}))
                original = manifest.read_bytes()
                if delta != page or runtime_change:
                    with self.assertRaises(ValueError):
                        reconcile(out, report)
                    self.assertEqual(original, manifest.read_bytes())
                else:
                    self.assertTrue(reconcile(out, report))
                    backup, = out.glob('resume-metadata-audit/*/manifest-before.json')
                    self.assertEqual(original, backup.read_bytes())
                    self.assertEqual(json.loads(manifest.read_text())['environment'], current)
                    self.assertFalse(reconcile(out, report))
