from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from financial_review_protocol import BINARY_INSTRUCTION,BINARY_SCHEMA,binary_review
from tier8_v2_critic_probe import BINARY_INSTRUCTION as TRAINING_INSTRUCTION,BINARY as TRAINING_SCHEMA
from tier8_v2_financial_pipeline import run_financial

class BinaryReviewTests(unittest.TestCase):
    def test_runtime_protocol_matches_training_exactly(self):
        self.assertEqual(BINARY_INSTRUCTION,TRAINING_INSTRUCTION)
        self.assertEqual(BINARY_SCHEMA,TRAINING_SCHEMA)
    def test_unknown_withholds_without_inventing_localization(self):
        result=binary_review({'verdict':'UNKNOWN'})
        self.assertEqual(result['verdict'],'FAIL');self.assertEqual(result['binary_verdict'],'UNKNOWN')
        self.assertFalse(result['repair_localization_available']);self.assertEqual(result['steps_to_repair'],[])
        self.assertNotIn('checks',result)
    def test_malformed_and_extra_fields_refused(self):
        for raw in [None,{'verdict':'MAYBE'},{'verdict':'PASS','steps_to_repair':[0]}]:self.assertIsNone(binary_review(raw))
        self.assertEqual(binary_review({'verdict':'PASS'})['verdict'],'PASS')
    def test_unknown_blocks_an_executable_program(self):
        class Runtime:
            context=4096
            def count_prompt_tokens(self,*args):return 100
            def call(self,role,content,schema,budget,requested,stage):
                budget.charge(3)
                answer={'decision':'ANSWER','answer_unit':'number','steps':[{'op':'divide','left':{'value':'10','span_id':'x'},'right':{'value':'2','span_id':'x'}}]} if stage=='program' else {'verdict':'UNKNOWN'}
                return answer,{'role':role,'stage':stage,'prompt':content,'generated_tokens':3}
        public={'id':'case','question':'what is 10 divided by 2?','evidence':{'x':'a: 10 ; b: 2'},'retrieval':{}}
        result=run_financial(public,Runtime(),'mas','none',selector='none',critic_protocol='binary')
        self.assertEqual(result['execution']['value'],'5');self.assertFalse(result['delivered'])
        self.assertEqual(result['tokens'],6);self.assertEqual(result['final_verdict']['binary_verdict'],'UNKNOWN')
    def test_binary_feedback_cannot_claim_bounded_patch_scope(self):
        with self.assertRaisesRegex(ValueError,'does not localize'):
            run_financial({},None,'mas','patch',critic_protocol='binary')

if __name__=='__main__':unittest.main()
