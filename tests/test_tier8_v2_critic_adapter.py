import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import tier8_v2_adapter_runtime as runtime
from tier8_v2_run import Models

class CriticAdapterTests(unittest.TestCase):
    def test_full_critic_provenance_and_tampered_inputs(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
            root=Path(d);run=root/'train';weights=run/'adapter';weights.mkdir(parents=True);converted=root/'converted';converted.mkdir()
            source=root/'data.jsonl';source.write_text('training fixture\n')
            for name in ['adapter_config.json','adapter_model.safetensors']:(weights/name).write_bytes(b'integrity fixture')
            (run/'manifest.json').write_text(json.dumps({'mode':'train','profile':'3b','purpose':'critic','training_n':3140,'validation_n':382,'input_sha256':{str(source):runtime.sha(source)}}))
            (run/'summary.json').write_text(json.dumps({'status':'complete','mode':'train','optimizer_updates':393,'examples_processed':3140,'validation_teacher_forced_loss':.2,'changed_adapter_tensors':2,'adapter_files':{p.name:runtime.sha(p) for p in weights.iterdir()}}))
            gguf=converted/'adapter.gguf';gguf.write_bytes(b'GGUF fixture')
            info={'status':'complete','training_mode':'train','diagnostic_only':False,'profile':'3b','purpose':'critic','tensor_count':2,'run':str(run),'file':str(gguf),'bytes':gguf.stat().st_size,'sha256':runtime.sha(gguf),'input_sha256':{str((run/n).relative_to(ROOT)):runtime.sha(run/n) for n in ['manifest.json','summary.json']}}
            (converted/'manifest.json').write_text(json.dumps(info))
            loaded=runtime.load_critic_adapter(str(converted));self.assertEqual(loaded['role'],'verifier');self.assertEqual(loaded['purpose'],'critic')
            with self.assertRaisesRegex(ValueError,'drafter'):runtime.load_adapter(str(converted),'mas','3b-q4')
            source.write_text('modified fixture\n')
            with self.assertRaisesRegex(ValueError,'input provenance'):runtime.load_critic_adapter(str(converted))
    def test_actor_and_critic_policies_have_separate_runtime_instances(self):
        calls=[]
        def llama(**kwargs):calls.append(kwargs);return SimpleNamespace(_lora_adapter=object())
        actor={'role':'drafter','purpose':'drafter','file':'weights/actor.gguf','sha256':'actor','scale':1.0}
        critic={'role':'verifier','purpose':'critic','file':'weights/critic.gguf','sha256':'critic','scale':1.0}
        with patch.dict(sys.modules,{'llama_cpp':SimpleNamespace(Llama=llama,LlamaGrammar=object)}),patch('tier8_v2_run.load_adapter',return_value=actor),patch('tier8_v2_run.load_critic_adapter',return_value=critic):
            models=Models('mas',4096,residency='shared',verifier_model='3b',use_selector=False,drafter_model='3b-q4',adapter='actor',verifier_adapter='critic')
        self.assertEqual(len(calls),2);self.assertNotEqual(calls[0]['lora_path'],calls[1]['lora_path'])
        self.assertIsNot(models.models['drafter'],models.models['verifier']);self.assertEqual(set(models.adapter_applications),{'drafter','verifier'})
    def test_wrong_verifier_profile_refused_before_file_access(self):
        with self.assertRaisesRegex(ValueError,'3B'):runtime.load_critic_adapter('not-a-directory','0.5b')

if __name__=='__main__':unittest.main()
