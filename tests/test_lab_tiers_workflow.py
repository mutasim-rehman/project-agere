"""Fixture-only tests for the detached workflow's selected tier and fail-fast chain."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Workflow(unittest.TestCase):
    def test_selected_tier_reaches_every_stage_and_errors_stop_export(self):
        for failed, expected in [('', ['preflight', 'run', 'export']),
                ('preflight', ['preflight']), ('run', ['preflight', 'run']),
                ('export', ['preflight', 'run', 'export'])]:
            with self.subTest(failed=failed), tempfile.TemporaryDirectory(dir=ROOT / '.local') as tmp:
                base = Path(tmp)
                scripts, ssd = base / 'repo/scripts', base / 'ssd'
                scripts.mkdir(parents=True)
                (ssd / 'weights').mkdir(parents=True)
                (ssd / 'datasets').mkdir()
                shutil.copyfile(ROOT / 'scripts/lab_tiers_all.sh', scripts / 'lab_tiers_all.sh')
                (scripts / 'lab_tiers.sh').write_text('set -eu\necho "$*" >> "$AGERE_SSD_ROOT/calls"\n'
                    'if [[ "${FAIL_STAGE:-}" == "$1" ]]; then exit 17; fi\n')
                env = {**os.environ, 'AGERE_SSD_ROOT': str(ssd), 'AGERE_LAB_TIERS': '16',
                    'AGERE_LAB_RUN_ID': 'fixture-v2', 'FAIL_STAGE': failed}
                result = subprocess.run(['bash', str(scripts / 'lab_tiers_all.sh'), '_worker'],
                    env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 17 if failed else 0, result.stderr)
                calls = (ssd / 'calls').read_text().splitlines()
                self.assertEqual([c.split()[0] for c in calls], expected)
                self.assertEqual(calls[0], 'preflight --tiers 16')
                if 'run' in expected:
                    self.assertEqual(calls[1], 'run --tiers 16 --run-id fixture-v2')
                status = (ssd / 'runs/lab_tiers_v1/fixture-v2/workflow-status.txt').read_text()
                self.assertTrue(status.startswith('FAILED' if failed else 'COMPLETE'))


if __name__ == '__main__':
    unittest.main()
