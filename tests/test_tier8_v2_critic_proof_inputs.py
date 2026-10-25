import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from tier8_v2_adapter_proof import diagnostic_prompt,sha

class CriticProofInputTests(unittest.TestCase):
    def test_only_bound_training_validation_prompt_allowed(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
            root=Path(d);train=root/'train';train.mkdir();data=root/'data.jsonl'
            data.write_text(json.dumps({'purpose':'critic','split':'validation','prompt':'validation prompt','source_id':'source'})+'\n')
            (train/'manifest.json').write_text(json.dumps({'input_sha256':{str(data.relative_to(ROOT)):sha(data)}}))
            args=SimpleNamespace(dataset=str(data),purpose='critic')
            path,row=diagnostic_prompt(args,{'training_run':str(train)})
            self.assertEqual(row['prompt'],'validation prompt');self.assertEqual(path,data)
            data.write_text(json.dumps({'purpose':'critic','split':'validation','prompt':'changed'})+'\n')
            with self.assertRaisesRegex(ValueError,'not bound'):diagnostic_prompt(args,{'training_run':str(train)})

if __name__=='__main__':unittest.main()
