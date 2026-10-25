from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from tier8_v2_sas_offload_fit import completed_dependency, load_policy, restore_cpu_matrices


class SasOffloadFitGateTests(unittest.TestCase):
    def test_policy_keeps_both_frozen_matrices_off_gpu(self):
        policy = load_policy()
        self.assertEqual(policy['device_map']['model.embed_tokens'], 'cpu')
        self.assertEqual(policy['device_map']['lm_head'], 'cpu')
        self.assertEqual(policy['device_map']['model.layers'], 0)
        self.assertTrue(policy['quantization']['llm_int8_enable_fp32_cpu_offload'])
        self.assertEqual(policy['lora']['r'], 8)
        self.assertEqual(policy['lora']['target_modules'], 'all-linear')

    def check(self, events, state, accepted):
        with tempfile.TemporaryDirectory(dir=ROOT / '.local/tmp') as folder:
            root = Path(folder)
            (root / 'journal.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in events))
            (root / 'state.json').write_text(json.dumps(state))
            plan = {'jobs': [{'name': 'first'}, {'name': 'external'}], 'cap_bytes': 6400000000}
            with patch('tier8_v2_sas_offload_fit.validate_job') as validate:
                if accepted:
                    completed_dependency(root, plan)
                    validate.assert_called_once_with(plan['jobs'][-1], plan['cap_bytes'])
                else:
                    with self.assertRaises(ValueError):
                        completed_dependency(root, plan)
                    validate.assert_not_called()

    def test_complete_state_alone_cannot_release_training(self):
        state = {'state': 'complete', 'all_jobs_finished': True}
        self.check([state], state, False)
        self.check([{'state': 'job_complete', 'job': 'first'}, state], state, False)

    def test_out_of_order_jobs_and_stale_state_fail(self):
        state = {'state': 'complete', 'all_jobs_finished': True}
        events = [{'state': 'job_complete', 'job': name} for name in ['external', 'first']]
        self.check(events + [state], state, False)
        events.reverse()
        self.check(events + [state, {'state': 'failed'}], state, False)

    def test_terminal_queue_still_requires_external_result_validation(self):
        state = {'state': 'complete', 'all_jobs_finished': True}
        events = [{'state': 'job_complete', 'job': name} for name in ['first', 'external']]
        self.check(events + [state], state, True)

    def test_failed_or_running_queue_never_releases_training(self):
        for state in [{'state': 'failed'}, {'state': 'starting'},
                      {'state': 'complete', 'all_jobs_finished': False}]:
            events = [{'state': 'job_complete', 'job': name} for name in ['first', 'external']]
            self.check(events + [state], state, False)

    def test_all_linear_lora_preserves_frozen_qwen_head(self):
        try:
            import torch
            from transformers import Qwen2Config, Qwen2ForCausalLM
            from peft import get_peft_model, LoraConfig
        except ImportError:
            self.skipTest('Requires training runtime torch/transformers/peft')
        torch.set_num_threads(1)
        config = Qwen2Config(vocab_size=31, hidden_size=16, intermediate_size=32,
                             num_hidden_layers=1, num_attention_heads=2,
                             num_key_value_heads=1, tie_word_embeddings=False)
        model = get_peft_model(Qwen2ForCausalLM(config), LoraConfig(
            **load_policy()['lora'], bias='none', task_type='CAUSAL_LM'))
        base = model.get_base_model()
        self.assertFalse(base.get_input_embeddings().weight.requires_grad)
        self.assertFalse(base.lm_head.weight.requires_grad)
        self.assertIsNone(base.lm_head.bias)
        names = [n for n, p in model.named_parameters() if p.requires_grad]
        self.assertTrue(names)
        self.assertTrue(all('lora_' in n for n in names))
        for projection in ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']:
            self.assertTrue(any(projection in n for n in names))

    def test_detaching_offload_hooks_restores_cpu_weights_and_decoder_input_path(self):
        try:
            import torch
            from transformers import Qwen2Config, Qwen2ForCausalLM
            from accelerate.hooks import add_hook_to_module, AlignDevicesHook
        except ImportError:
            self.skipTest('Requires training runtime torch/transformers/accelerate')
        torch.set_num_threads(1)
        config = Qwen2Config(vocab_size=31, hidden_size=16, intermediate_size=32,
                             num_hidden_layers=1, num_attention_heads=2,
                             num_key_value_heads=1, tie_word_embeddings=False)
        model = Qwen2ForCausalLM(config).eval()
        original = [m.weight.detach().clone() for m in [model.get_input_embeddings(), model.get_output_embeddings()]]
        for module in [model.get_input_embeddings(), model.get_output_embeddings()]:
            add_hook_to_module(module, AlignDevicesHook(execution_device='cpu', offload=True))
            self.assertEqual(module.weight.device.type, 'meta')
        restore_cpu_matrices(model)
        for module, expected in zip([model.get_input_embeddings(), model.get_output_embeddings()], original):
            self.assertEqual(module.weight.device.type, 'cpu')
            self.assertFalse(hasattr(module, '_hf_hook'))
            torch.testing.assert_close(module.weight, expected)
        ids = torch.tensor([[2, 3, 4, 5]])
        with torch.no_grad():
            a = model.model(input_ids=ids).last_hidden_state
            b = model.model(inputs_embeds=model.get_input_embeddings()(ids)).last_hidden_state
        torch.testing.assert_close(a, b)

    def test_checkpointed_all_linear_adapter_gradients_with_explicit_embeddings(self):
        try:
            import torch
            from transformers import Qwen2Config, Qwen2ForCausalLM
            from peft import get_peft_model, LoraConfig
            from frozen_head_loss import causal_frozen_head_loss
        except ImportError:
            self.skipTest('Requires training runtime')
        import copy
        torch.set_num_threads(1); torch.manual_seed(42)
        config = Qwen2Config(vocab_size=31, hidden_size=16, intermediate_size=32,
                             num_hidden_layers=1, num_attention_heads=2,
                             num_key_value_heads=1, tie_word_embeddings=False)
        model = get_peft_model(Qwen2ForCausalLM(config), LoraConfig(
            **load_policy()['lora'], bias='none', task_type='CAUSAL_LM'))
        model.get_base_model().gradient_checkpointing_enable(
            gradient_checkpointing_kwargs={'use_reentrant': False})
        dense = copy.deepcopy(model)
        ids = torch.tensor([[2, 3, 4, 5, 6]])
        labels = torch.tensor([[-100, -100, 4, 5, 6]])
        torch.manual_seed(7)
        with torch.autocast('cpu', dtype=torch.bfloat16):
            base = model.get_base_model()
            embeddings = base.get_input_embeddings()(ids)
            self.assertFalse(embeddings.requires_grad)
            states = base.model(inputs_embeds=embeddings, use_cache=False).last_hidden_state
            loss = causal_frozen_head_loss(states.to(torch.bfloat16), base.lm_head.weight, labels, 7)
        loss.backward()
        torch.manual_seed(7)
        with torch.autocast('cpu', dtype=torch.bfloat16):
            reference = dense(input_ids=ids, labels=labels, use_cache=False).loss
        reference.backward()
        torch.testing.assert_close(loss, reference, atol=.002, rtol=.002)
        gradients = []
        for name, p in model.named_parameters():
            if p.requires_grad:
                q = dict(dense.named_parameters())[name]
                self.assertIsNotNone(p.grad)
                torch.testing.assert_close(p.grad, q.grad, atol=.0002, rtol=.03)
                gradients.append(p.grad.abs().sum().item())
        self.assertGreater(sum(gradients), 0)


if __name__ == '__main__':
    unittest.main()
