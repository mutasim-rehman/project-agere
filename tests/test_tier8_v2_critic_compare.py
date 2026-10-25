from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tier8_v2_critic_compare import compare

class CriticComparisonTests(unittest.TestCase):
    def test_accepting_everything_is_not_pair_discrimination(self):
        labels=[{'id':'p','report_group':'g','expected_accept':True},{'id':'n','report_group':'g','expected_accept':False}]
        def rows(vs):return [{'id':i,'protocol':'binary','verdict':v,'event':{'prompt':'same '+i,'generated_tokens':2,'prompt_tokens':10}} for i,v in zip(['p','n'],vs)]
        result=compare(labels,rows(['UNKNOWN','UNKNOWN']),rows(['PASS','PASS']))
        self.assertEqual(result['delta_gate_accuracy'],0)
        self.assertEqual(result['conditions']['adapted']['complete_pair_discriminations'],0)
        better=compare(labels,rows(['UNKNOWN','UNKNOWN']),rows(['PASS','FAIL']))
        self.assertEqual(better['delta_gate_accuracy'],.5)
        self.assertEqual(better['conditions']['adapted']['complete_pair_discriminations'],1)
    def test_changed_prompt_or_duplicate_case_refused(self):
        labels=[{'id':'p','report_group':'g','expected_accept':True},{'id':'n','report_group':'g','expected_accept':False}]
        rows=[{'id':i,'protocol':'binary','verdict':'PASS','event':{'prompt':i,'generated_tokens':1,'prompt_tokens':1}} for i in ['p','n']]
        with self.assertRaises(ValueError):compare(labels,rows,[rows[0],rows[0]])
        changed=[dict(r,event={**r['event'],'prompt':'different'}) for r in rows]
        with self.assertRaises(ValueError):compare(labels,rows,changed)

if __name__=='__main__':unittest.main()
