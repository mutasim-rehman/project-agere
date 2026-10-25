import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import tier8_v2_run as runner

class FinancialSourceTests(unittest.TestCase):
    def test_source_copy_must_be_byte_identical_to_pin(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
            folder=Path(d);source=folder/'source.json';source.write_text('[]\n')
            pin=folder/'research/tier8_v2/evidence';pin.mkdir(parents=True)
            (pin/'finqa-development-manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}))
            with patch.object(runner,'ROOT',folder):
                self.assertEqual(runner.financial_source(str(source)),source)
                source.write_text('[{"changed":true}]\n')
                with self.assertRaisesRegex(ValueError,'pinned FinQA'):runner.financial_source(str(source))

if __name__=='__main__':unittest.main()
