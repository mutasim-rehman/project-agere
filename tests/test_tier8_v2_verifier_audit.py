import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tier8_v2_verifier_audit import analyze

class CriticAuditTests(unittest.TestCase):
    def row(self,correct=True):
        return {'case_id':'one','initial_plan':{'steps':[]},'stages':[{'stage':'verify_program','prompt':'same sources and candidate'}],
                'initial_verdict':{'checks':{k:'PASS' for k in ['operands','operations','units']},'repair_kind':'NONE','verdict':'PASS'},
                'initial_score':{'case_success':correct},'score':{'case_success':correct},'delivered':True}
    def test_rejection_and_prompt_contradiction_are_distinct(self):
        a=self.row();b=copy.deepcopy(a);b['initial_verdict']['checks']['operands']='FAIL';b['initial_verdict']['verdict']='FAIL';b['delivered']=False
        r=analyze([a],[b]);self.assertEqual(r['identical_initial_plans'],1)
        self.assertEqual(r['arms']['right']['false_reject'],1)
        self.assertEqual(r['arms']['right']['repair_NONE_with_nonPASS_check'],1)
    def test_changed_candidate_or_input_refused(self):
        for key,value in [('initial_plan',{'steps':['different']})]:
            a=self.row();b=copy.deepcopy(a);b[key]=value
            with self.assertRaises(ValueError):analyze([a],[b])
        a=self.row();b=copy.deepcopy(a);b['stages'][0]['prompt']='different'
        with self.assertRaises(ValueError):analyze([a],[b])
    def test_duplicate_ids_refused(self):
        with self.assertRaises(ValueError):analyze([self.row(),self.row()],[self.row(),self.row()])

if __name__=='__main__':unittest.main()
