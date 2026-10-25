from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tier8_v2_critic_probe_analyze import analyze

class ProbeAnalysisTests(unittest.TestCase):
    def fixture(self):
        labels=[{'id':'p','report_group':'g','expected_accept':True},{'id':'n','report_group':'g','expected_accept':False}]
        rows=[]
        for protocol in ['rich','binary']:
            for ident in ['p','n']:
                rows.append({'id':ident,'protocol':protocol,'verdict':'PASS' if protocol=='binary' and ident=='p' else 'FAIL','event':{'generated_tokens':2,'prompt_tokens':10,'seconds':1}})
        return labels,{'3b':rows}
    def test_joint_discrimination_differs_from_rejection(self):
        l,r=self.fixture();a=analyze(l,r)['profiles']['3b']
        self.assertEqual(a['protocols']['rich']['both_rejected_pairs'],1)
        self.assertEqual(a['protocols']['rich']['complete_pair_discriminations'],0)
        self.assertEqual(a['protocols']['binary']['complete_pair_discriminations'],1)
        self.assertEqual(a['binary_minus_rich_gate_accuracy'],.5)
    def test_incomplete_and_imbalanced_data_refused(self):
        l,r=self.fixture();r['3b'].pop()
        with self.assertRaises(ValueError):analyze(l,r)
        l,r=self.fixture();l[1]['expected_accept']=True
        with self.assertRaises(ValueError):analyze(l,r)

if __name__=='__main__':unittest.main()
