"""Known statistical identities and dependency-aware fixture contrasts."""
import sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/reporting'))
from analyze_completed_tiers import holm,mcnemar,signflip,paired


class Statistics(unittest.TestCase):
    def test_exact_discordance_and_holm_known_values(self):
        self.assertEqual(mcnemar(3,0),.25)
        self.assertEqual(mcnemar(0,0),1.)
        self.assertEqual(holm([.01,.04,.03]),[.03,.06,.06])

    def test_sign_flips_operate_on_clusters_not_questions(self):
        self.assertEqual(signflip([1,1])['p'],.5)
        self.assertEqual(signflip([0,0])['p'],1.)
        self.assertEqual(signflip([2,2,0])['draws'],4)

    def test_pairing_rejects_missing_case_and_matches_complement_identity(self):
        def row(k,delivered,correct):
            return {'case_id':k,'delivered':delivered,'score':{'case_success':correct}}
        left=[row('A/2020/p-1',True,False),row('A/2020/p-2',True,True),row('B/2021/p-1',True,False)]
        right=[row('A/2020/p-1',False,False),row('A/2020/p-2',True,True),row('B/2021/p-1',True,True)]
        estimates=[paired(left,right,'case_success',e) for e in ['correct','wrong','withheld']]
        self.assertEqual(sum(v['delta_count'] for v in estimates),0)
        self.assertEqual(estimates[0]['clusters'],2)
        self.assertEqual(estimates[0]['delta_count'],1)
        with self.assertRaises(ValueError):paired(left,right[:-1],'case_success','correct')


if __name__=='__main__':unittest.main()
