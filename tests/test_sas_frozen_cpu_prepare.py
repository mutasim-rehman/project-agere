from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
try:
    import torch
    from transformers import Qwen2Config, Qwen2ForCausalLM
    from peft import prepare_model_for_kbit_training
    from frozen_head_loss import causal_frozen_head_loss
except ImportError:
    torch = None
from sas_frozen_cpu_prepare import prepare_frozen_cpu_model


@unittest.skipIf(torch is None, 'Requires training runtime')
class FrozenCpuPrepareTests(unittest.TestCase):
    def test_storage_change_preserves_lookup_and_head_loss_and_gradient(self):
        torch.set_num_threads(1)
        torch.manual_seed(42)
        config = Qwen2Config(vocab_size=31, hidden_size=16, intermediate_size=32,
                             num_hidden_layers=1, num_attention_heads=2,
                             num_key_value_heads=1, tie_word_embeddings=False)
        baseline = Qwen2ForCausalLM(config).to(torch.bfloat16)
        baseline.is_loaded_in_4bit = True
        compact = deepcopy(baseline)
        prepare_model_for_kbit_training(baseline, gradient_checkpointing_kwargs={'use_reentrant': False})
        prepare_frozen_cpu_model(compact)
        ids = torch.tensor([[1, 7, 9, 2]])
        torch.testing.assert_close(baseline.get_input_embeddings()(ids),
                                   compact.get_input_embeddings()(ids).float(), atol=0, rtol=0)
        self.assertTrue(compact.is_gradient_checkpointing)
        self.assertTrue(all(not p.requires_grad for p in compact.parameters()))
        old, new = baseline.state_dict(), compact.state_dict()
        matrix_names = {'model.embed_tokens.weight', 'lm_head.weight'}
        for name, value in new.items():
            self.assertEqual(value.dtype, torch.bfloat16 if name in matrix_names else torch.float32)
            torch.testing.assert_close(value.float(), old[name], atol=0, rtol=0)
        h1 = torch.randn(1, 4, 16, dtype=torch.bfloat16, requires_grad=True)
        h2 = h1.detach().clone().requires_grad_(True)
        a = causal_frozen_head_loss(h1, baseline.lm_head.weight, ids, 7)
        b = causal_frozen_head_loss(h2, compact.lm_head.weight, ids, 7)
        a.backward(); b.backward()
        torch.testing.assert_close(a, b, atol=0, rtol=0)
        torch.testing.assert_close(h1.grad, h2.grad, atol=0, rtol=0)

    def test_wrong_policy_refused(self):
        config = Qwen2Config(vocab_size=31, hidden_size=16, intermediate_size=32,
                             num_hidden_layers=1, num_attention_heads=2,
                             num_key_value_heads=1, tie_word_embeddings=False)
        model = Qwen2ForCausalLM(config)
        with self.assertRaisesRegex(ValueError, 'NF4'):
            prepare_frozen_cpu_model(model)
        model.is_loaded_in_4bit = True
        with self.assertRaisesRegex(ValueError, 'BF16'):
            prepare_frozen_cpu_model(model)

    def test_actual_tiny_lora_decoder_loss_and_adapter_gradients(self):
        from peft import get_peft_model, LoraConfig
        torch.set_num_threads(1)
        torch.manual_seed(19)
        config = Qwen2Config(vocab_size=31, hidden_size=16, intermediate_size=32,
                             num_hidden_layers=1, num_attention_heads=2,
                             num_key_value_heads=1, tie_word_embeddings=False)
        original = Qwen2ForCausalLM(config).to(torch.bfloat16)
        original.is_loaded_in_4bit = True
        compact = deepcopy(original)
        prepare_model_for_kbit_training(original, gradient_checkpointing_kwargs={'use_reentrant': False})
        prepare_frozen_cpu_model(compact)
        policies = []
        for model in (original, compact):
            torch.manual_seed(42)
            policies.append(get_peft_model(model, LoraConfig(r=2, lora_alpha=4, lora_dropout=.05,
                target_modules='all-linear', bias='none', task_type='CAUSAL_LM')))
        ids = torch.tensor([[1, 7, 9, 2]])
        losses, parameters = [], []
        for policy in policies:
            policy.train()
            base = policy.get_base_model()
            torch.manual_seed(42)
            embeddings = base.get_input_embeddings()(ids).float()
            with torch.autocast('cpu', dtype=torch.bfloat16):
                hidden = base.model(inputs_embeds=embeddings, use_cache=False).last_hidden_state
                loss = causal_frozen_head_loss(hidden.to(torch.bfloat16), base.lm_head.weight, ids, 7)
            loss.backward()
            losses.append(loss.detach())
            parameters.append({name: (p.detach().clone(), p.grad.detach().clone())
                               for name, p in policy.named_parameters() if p.requires_grad})
        torch.testing.assert_close(losses[0], losses[1], atol=0, rtol=0)
        self.assertEqual(set(parameters[0]), set(parameters[1]))
        for name in parameters[0]:
            for left, right in zip(parameters[0][name], parameters[1][name]):
                torch.testing.assert_close(left, right, atol=0, rtol=0)


if __name__ == '__main__':
    unittest.main()
