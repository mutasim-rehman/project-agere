import ast
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tier8_v2_critic_probe import mutations,RICH_INSTRUCTION,prepare
from evidence_atoms import atom_catalog

class ProbeTests(unittest.TestCase):
    def test_mutations_change_only_one_operation_and_preserve_sources(self):
        evidence={'x':'a: 10 ; b: 2'};atoms=atom_catalog(evidence)
        refs={a['value']:k for k,a in atoms.items()}
        target={'decision':'ANSWER','answer_unit':'number','steps':[{'left':refs['10'],'right':refs['2'],'op':'divide'}]}
        candidates=list(mutations(target,evidence,{'qa':{'exe_ans':5,'answer':'5'}}))
        self.assertEqual(len(candidates),3)
        for answer,execution,change in candidates:
            self.assertFalse(execution['issues']);self.assertNotEqual(execution['value'],'5')
            self.assertEqual(answer['steps'][0]['left'],{'value':'10','span_id':'x'})
            self.assertEqual(answer['steps'][0]['right'],{'value':'2','span_id':'x'})
            self.assertEqual(change['step'],0)
    def test_numerically_equivalent_mutation_not_labeled_negative(self):
        evidence={'x':'value: 2'};ref=next(iter(atom_catalog(evidence)))
        target={'decision':'ANSWER','answer_unit':'number','steps':[{'left':ref,'right':ref,'op':'add'}]}
        ops=[change['new_operation'] for _,_,change in mutations(target,evidence,{'qa':{'exe_ans':4,'answer':'4'}})]
        self.assertNotIn('multiply',ops)
    def test_rich_prompt_exactly_matches_existing_instruction(self):
        path=Path(__file__).resolve().parents[1]/'scripts/tier8_v2_financial_pipeline.py'
        literals=[n.value for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
        self.assertIn('\n'+RICH_INSTRUCTION,literals)
    def test_probe_balance_and_report_independence(self):
        public,labels,meta=prepare(2)
        self.assertEqual(len(public),4);self.assertEqual(sum(r['expected_accept'] for r in labels),2)
        self.assertEqual(len(meta['report_groups']),2)
        for row in public:
            self.assertEqual(set(row),{'id','question','evidence','candidate','execution'})
            self.assertNotIn('expected_accept',row)

if __name__=='__main__':unittest.main()
