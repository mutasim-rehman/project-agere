import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import tier8_artifact_paths as paths

class ArtifactPathTests(unittest.TestCase):
    def test_only_configured_ssd_with_expected_structure_allowed(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
            base=Path(d);repo=base/'repo';ssd=base/'ssd';repo.mkdir();ssd.mkdir()
            with patch.object(paths,'ROOT',repo),patch.dict(os.environ,{'AGERE_SSD_ROOT':str(ssd)}):
                self.assertEqual(paths.artifact_path('runs/one'),repo/'runs/one')
                with self.assertRaises(ValueError):paths.artifact_path(ssd/'runs/one')
                (ssd/'datasets').mkdir();(ssd/'weights').mkdir()
                self.assertEqual(paths.artifact_path(ssd/'runs/one'),ssd/'runs/one')
                with self.assertRaises(ValueError):paths.artifact_path(base/'other')
    def test_symlink_escape_and_unconfigured_external_path_refused(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
            base=Path(d);repo=base/'repo';repo.mkdir();(repo/'escape').symlink_to(base/'outside')
            with patch.object(paths,'ROOT',repo),patch.dict(os.environ,{'AGERE_SSD_ROOT':''}):
                with self.assertRaises(ValueError):paths.artifact_path(repo/'escape/file')
                with self.assertRaises(ValueError):paths.artifact_path(base/'other')

if __name__=='__main__':unittest.main()
