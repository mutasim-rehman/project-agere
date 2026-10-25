from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tier8_v2_critic_data import negative_candidates,validate_groups,rank,prompt
from evidence_atoms import atom_catalog

class CriticDataTests(unittest.TestCase):
    def test_wrong_operand_and_operation_candidates_preserve_execution(self):
        evidence={'x':'value: 10 ; denominator: 2 ; alternative: 4'};atoms=atom_catalog(evidence);refs={a['value']:k for k,a in atoms.items()}
        row={'source_id':'sample','public':{'evidence':evidence},'target':{'decision':'ANSWER','answer_unit':'number','steps':[{'left':refs['10'],'right':refs['2'],'op':'divide'}]},'cell_view':{'catalog':{k:{'cell_role':'data'} for k in atoms}}}
        results=list(negative_candidates(row,{'qa':{'answer':'5','exe_ans':5}}))
        self.assertEqual({r[2]['kind'] for r in results},{'operand','operation'})
        for answer,execution,change in results:self.assertFalse(execution['issues']);self.assertNotEqual(execution['value'],'5')
    def test_group_leakage_refused(self):
        rows=[{'split':'train','report_group':'same'},{'split':'validation','report_group':'same'}]
        with self.assertRaises(ValueError):validate_groups(rows,[])
        with self.assertRaises(ValueError):validate_groups([rows[0]],['same'])
    def test_deterministic_selection_and_label_free_prompt(self):
        self.assertEqual(rank('source',{'a':1,'b':2}),rank('source',{'b':2,'a':1}))
        public={'question':'calculate','evidence':{'x':'2'},'answer':'SECRET'}
        self.assertNotIn('SECRET',prompt(public,{'steps':[]},{'value':'0'}))

if __name__=='__main__':unittest.main()
