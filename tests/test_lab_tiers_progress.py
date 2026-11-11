"""Progress reporting must reflect durable checkpoints without changing them."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lab_tiers_progress import checksum_activity, snapshot


class Progress(unittest.TestCase):
    def test_open_model_read_position_is_visible(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / 'fixture.gguf'
            model.write_bytes(b'x' * 100)
            with model.open('rb', buffering=0) as stream:
                stream.read(25)
                activity = checksum_activity(os.getpid())
                self.assertIn('fixture.gguf', activity)
                self.assertIn('25%', activity)

    def test_startup_resume_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.assertIn('startup', snapshot(out))
            job = out / 'tier16-sas-primary'
            attempt = job / 'attempt-0002'
            attempt.mkdir(parents=True)
            (job / 'manifest.json').write_text(json.dumps({'dataset': {'n': 160}}))
            (attempt / 'state.json').write_text(json.dumps({'status': 'running', 'completed_before': 5}))
            self.assertIn('5/160', snapshot(out))
            (attempt / 'progress.json').write_text(json.dumps({'completed': 6}))
            (attempt / 'worker.log').write_text('Resident model loaded: sas\n')
            before = {p: p.read_bytes() for p in job.rglob('*') if p.is_file()}
            text = snapshot(out)
            self.assertIn('6/160', text)
            self.assertIn('Resident model loaded: sas', text)
            self.assertEqual(before, {p: p.read_bytes() for p in job.rglob('*') if p.is_file()})
