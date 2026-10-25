import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tier8_external_eval import source_lines, normalize, score, packet

class ExternalEvaluationTests(unittest.TestCase):
    def test_source_packet_cannot_read_labels(self):
        class Tokenizer:
            def tokenize(self,b,add_bos=False): return list(b)
        public={'question':'find payroll', 'answer_type':'txn_id_list',
                'bank_statement':'{"transactions":[{"transaction_id":"t1","description":"payroll"}]}',
                'ulad_du':'<LOAN><Employer>ABC</Employer></LOAN>'}
        a=packet({**public,'answer':'SECRET_A'},Tokenizer())
        b=packet({**public,'answer':'SECRET_B'},Tokenizer())
        self.assertEqual(a,b)
        self.assertIn('transactions/0',str(a))
        self.assertIn('Employer',str(source_lines(public)))
    def test_typed_metrics_reject_malformed_answers(self):
        row={'answer':'none','answer_type':'txn_id_list'}
        self.assertTrue(score({'answer':[]},row,'mortar')['exact_match'])
        self.assertFalse(score(None,row,'mortar')['exact_match'])
        self.assertEqual(normalize('false','boolean'),False)
        self.assertTrue(score({'answer':['b','a']},{'answer':'a,b','answer_type':'txn_id_list'},'mortar')['exact_match'])
        self.assertFalse(score({'answer':['a']},{'answer':'a,b','answer_type':'txn_id_list'},'mortar')['exact_match'])
    def test_frames_preserves_strict_score(self):
        result=score('21 years',{'answer':'21 years.'},'frames')
        self.assertFalse(result['exact_match'])
        self.assertTrue(result['punctuation_normalized_match'])

if __name__=='__main__':unittest.main()
