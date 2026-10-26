"""Continuation integrity checks; tiny CPU state only, no model evaluation."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tier8_v2_continue import identity, RECIPE, discovery_gate, restore_exact_adapter, deployment_input_hashes


class ContinuationContract(unittest.TestCase):
    def test_only_base_shards_leave_deployment_rehash_inputs(self):
        folder = Path(__file__).resolve().parents[1] / 'weights/provenance-test-source'
        weight = str(folder / 'model.safetensors')
        for profile, base in [('3b', {'folder': str(folder), 'weight_file': 'model.safetensors'}),
                ('3b', {'folder': 'weights/provenance-test-source', 'weight_file': 'model.safetensors'}),
                ('7b', {'folder': str(folder), 'artifacts': [{'path': 'weights/source/model.safetensors'}]})]:
            plan = {'profile': profile, 'training_base': base, 'input_sha256': {
                weight: 'base', '/initializer/adapter_model.safetensors': 'adapter',
                '/source/config.json': 'config', '/dataset.jsonl': 'data'}}
            inputs, retained = deployment_input_hashes(plan)
            self.assertEqual(retained, {weight: 'base'})
            self.assertEqual(inputs['/initializer/adapter_model.safetensors'], 'adapter')
            self.assertEqual(inputs['/source/config.json'], 'config')
            self.assertEqual(plan['input_sha256'][weight], 'base')
            del plan['input_sha256'][weight]
            with self.assertRaises(ValueError):
                deployment_input_hashes(plan)

    def test_fit_identity_excludes_output_but_binds_initializer_and_optimizer(self):
        keys = ('profile', 'purpose', 'dataset_manifest', 'parity_manifest', 'initializer',
                'recipe', 'input_sha256', 'runtime_versions', 'training_base', 'training_n', 'validation_n')
        plan = {k: k for k in keys}; plan.update(mode='fit', out='fit')
        full = copy.deepcopy(plan); full.update(mode='train', out='train')
        self.assertEqual(identity(plan), identity(full))
        full['initializer'] = 'independently_initialized'
        self.assertNotEqual(identity(plan), identity(full))
        full = copy.deepcopy(plan); full['recipe'] = {'learning_rate': 2e-4}
        self.assertNotEqual(identity(plan), identity(full))

    def test_undeclared_discovery_cannot_prepare(self):
        # Wrong or incomplete inputs fail before continuation can be launched.
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises((ValueError, FileNotFoundError)):
                discovery_gate(Path(temp))

    def test_actual_peft_checkpoint_is_restored_exactly(self):
        try:
            import torch
            from peft import get_peft_model, LoraConfig, get_peft_model_state_dict
            from transformers import Qwen2Config, Qwen2ForCausalLM
        except ImportError:
            self.skipTest('Requires training runtime for tiny CPU PEFT state check')
        config = Qwen2Config(vocab_size=32, hidden_size=16, intermediate_size=32,
                            num_hidden_layers=1, num_attention_heads=2, num_key_value_heads=1)
        model = get_peft_model(Qwen2ForCausalLM(config),
                              LoraConfig(**RECIPE['lora'], bias='none', task_type='CAUSAL_LM'))
        with torch.no_grad():
            for name, p in model.named_parameters():
                if 'lora_B' in name:
                    p.fill_(.125)
        saved = {n: p.detach().clone() for n, p in get_peft_model_state_dict(model).items()}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp); model.save_pretrained(path, safe_serialization=True)
            with torch.no_grad():
                for name, p in model.named_parameters():
                    if 'lora_' in name:
                        p.zero_()
            self.assertEqual(restore_exact_adapter(model, path), len(saved))
            actual = get_peft_model_state_dict(model)
            self.assertTrue(all(torch.equal(saved[n], actual[n]) for n in saved))
            # A fresh untrained adapter must fail the learned-initializer check.
            with torch.no_grad():
                for name, p in model.named_parameters():
                    if 'lora_B' in name:
                        p.zero_()
            model.save_pretrained(path, safe_serialization=True)
            with self.assertRaisesRegex(ValueError, 'no learned B'):
                restore_exact_adapter(model, path)


if __name__ == '__main__':
    unittest.main()
