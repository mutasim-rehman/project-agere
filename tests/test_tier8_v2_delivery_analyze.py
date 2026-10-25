from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tier8_v2_delivery_analyze import analyze

class DeliveryAnalysisTests(unittest.TestCase):
    def row(self,i,correct,delivered):
        return {'case_id':i,'delivered':delivered,'score':{'case_success':correct,'raw_execution_match':correct},'tokens':2,'stages':[{'generated_tokens':2,'prompt_tokens':10,'seconds':1}]}
    def test_coverage_gain_can_increase_wrong_deliveries_without_dominance(self):
        ids=['A/2010/page_1.pdf-1','B/2011/page_1.pdf-1']
        left=[self.row(ids[0],True,False),self.row(ids[1],False,False)]
        right=[self.row(ids[0],True,True),self.row(ids[1],False,True)]
        m=analyze(left,right)['metrics']['case_success']
        self.assertIsNone(m['conditions']['plain']['precision_when_delivered'])
        self.assertEqual(m['delta_correct_delivery_coverage'],.5);self.assertEqual(m['delta_incorrect_delivery_rate'],.5)
        self.assertFalse(m['empirical_delivery_pareto_dominance']);self.assertEqual(m['break_even_penalty_ratio'],1)
        self.assertLess(m['illustrative_utility_delta']['5']['per_case'],0)
    def test_fewer_errors_at_same_coverage_is_descriptive_dominance(self):
        ids=['A/2010/page_1.pdf-1','A/2010/page_2.pdf-1']
        left=[self.row(ids[0],True,True),self.row(ids[1],False,True)];right=[left[0],self.row(ids[1],False,False)]
        result=analyze(left,right);self.assertEqual(result['n_report_groups'],1)
        self.assertTrue(result['metrics']['case_success']['empirical_delivery_pareto_dominance'])
    def test_changed_candidate_or_missing_case_refused(self):
        row=self.row('A/2010/page_1.pdf-1',True,False)
        with self.assertRaises(ValueError):analyze([row],[self.row(row['case_id'],False,True)])
        with self.assertRaises(ValueError):analyze([row],[self.row('B/2010/page_1.pdf-1',True,True)])

if __name__=='__main__':unittest.main()
