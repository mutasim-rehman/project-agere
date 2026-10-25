import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from tier8_v2_posttrain_queue import check_inputs,sha,natural_pair,require_training

class PosttrainQueueTests(unittest.TestCase):
    def test_frozen_file_change_refused(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
            p=Path(d)/'input';p.write_text('original');plan={'input_sha256':{str(p):sha(p)}};check_inputs(plan)
            p.write_text('changed')
            with self.assertRaises(ValueError):check_inputs(plan)
    def test_incomplete_epoch_does_not_authorize_evaluation(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
            p=Path(d);(p/'manifest.json').write_text(json.dumps({'purpose':'critic','profile':'3b','training_n':3140}))
            (p/'summary.json').write_text(json.dumps({'status':'complete','mode':'train','examples_processed':8,'optimizer_updates':1,'changed_adapter_tensors':2,'validation_teacher_forced_loss':.2}))
            with self.assertRaises(ValueError):require_training(str(p))
    def test_changed_draft_invalidates_critic_causal_pair(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
            roots=[Path(d)/n for n in ['left','right']]
            for index,p in enumerate(roots):
                p.mkdir();m={'data_sha256':'same','evaluation_source_sha256':'same','code_sha256':{'code':'same'},'cap_bytes':6400000000,'models':['same'],'adapter':{'sha256':'actor'},'verifier_adapter':{'sha256':'critic'} if index else None}
                (p/'manifest.json').write_text(json.dumps(m));apps={'drafter':{'runtime_handle_initialized':True}}
                if index:apps['verifier']={'runtime_handle_initialized':True}
                row={'case_id':'case','initial_plan':{'steps':[]},'initial_answer':{'steps':[]},'stages':[{'stage':'verify_program','prompt':'same'}],'adapter_applications':apps}
                (p/'cases.jsonl').write_text(json.dumps(row)+'\n')
            self.assertTrue(natural_pair(*map(str,roots))['identical_initial_drafts'])
            p=roots[1]/'cases.jsonl';row=json.loads(p.read_text());row['initial_plan']={'steps':['different']};p.write_text(json.dumps(row)+'\n')
            with self.assertRaises(ValueError):natural_pair(*map(str,roots))

if __name__=='__main__':unittest.main()
