import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tier8_external_recover import validate_prefix,read_rows

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.source=[{'id':'one','answer':'Paris'},{'id':'two','answer':'Rome'}]
        self.record={'id':'one','gold':'Paris','prediction':'Paris',
            'score':{'exact_match':True,'punctuation_normalized_match':True},
            'generated_tokens':3,'stages':[
                {'role':'sas','response':'analysis','usage':{'completion_tokens':2}},
                {'role':'sas','response':'Paris','usage':{'completion_tokens':1}}]}
    def test_valid_prefix_is_reusable(self):
        self.assertEqual(validate_prefix([self.record],self.source,'frames','sas'),1)
        self.assertEqual(validate_prefix([],self.source,'frames','sas'),0)
    def test_reordered_duplicate_and_tampered_cases_refused(self):
        for mutate in [lambda r:r.update(id='two'),lambda r:r.update(gold='Lyon'),
                       lambda r:r['score'].update(exact_match=False),
                       lambda r:r.update(generated_tokens=2049),
                       lambda r:r['stages'][-1].update(response='Rome')]:
            r=copy.deepcopy(self.record);mutate(r)
            with self.assertRaises(ValueError):validate_prefix([r],self.source,'frames','sas')
        with self.assertRaises(ValueError):validate_prefix([self.record,self.record],self.source,'frames','sas')
    def test_incomplete_jsonl_tail_is_preserved_and_refused(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'.local') as d:
            p=Path(d)/'cases.jsonl';raw=b'{"id":"one"}\n{"id":';p.write_bytes(raw)
            with self.assertRaises(ValueError):read_rows(p)
            self.assertEqual(p.read_bytes(),raw)
    def test_wrong_role_or_missing_stage_refused(self):
        r=copy.deepcopy(self.record);r['stages'].pop()
        with self.assertRaises(ValueError):validate_prefix([r],self.source,'frames','sas')

if __name__=='__main__':unittest.main()
