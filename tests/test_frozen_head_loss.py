from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
try:
    import torch
except ImportError:
    torch = None

if torch is not None:
    from frozen_head_loss import frozen_head_loss, causal_frozen_head_loss


@unittest.skipIf(torch is None, 'Requires training runtime torch')
class FrozenHeadLossTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(42)

    def compare(self, dtype, block, scale=1.0):
        h = torch.randn(2, 4, 7, dtype=dtype, requires_grad=True)
        full = h.detach().clone().requires_grad_(True)
        w = torch.randn(13, 7, dtype=dtype)
        targets = torch.tensor([[0, 12, 5, -100], [1, -100, 8, 2]])
        result = frozen_head_loss(h, w, targets, block)
        logits = full @ w.T
        if dtype != torch.float64:
            logits = logits.float()
        expected = torch.nn.functional.cross_entropy(logits.reshape(-1, 13), targets.reshape(-1))
        (result * scale).backward()
        (expected * scale).backward()
        tolerance = 0.02 if dtype == torch.bfloat16 else 2e-6 if dtype == torch.float32 else 1e-12
        torch.testing.assert_close(result, expected, atol=tolerance, rtol=tolerance)
        torch.testing.assert_close(h.grad, full.grad, atol=tolerance, rtol=tolerance)
        self.assertEqual(h.grad[0, 3].abs().sum().item(), 0)
        self.assertEqual(h.grad[1, 1].abs().sum().item(), 0)
        self.assertIsNone(w.grad)

    def test_dense_loss_and_gradient_across_block_boundaries(self):
        for dtype in [torch.float64, torch.float32, torch.bfloat16]:
            for block in [1, 5, 13, 20]:
                with self.subTest(dtype=dtype, block=block):
                    self.compare(dtype, block, scale=0.125)

    def test_finite_difference_gradient(self):
        h = torch.randn(2, 3, dtype=torch.float64, requires_grad=True)
        w = torch.randn(5, 3, dtype=torch.float64)
        y = torch.tensor([4, 0])
        self.assertTrue(torch.autograd.gradcheck(lambda a: frozen_head_loss(a, w, y, 2), (h,)))

    def test_extreme_logits_are_stable(self):
        h = torch.tensor([[1e4, -1e4]], requires_grad=True)
        w = torch.tensor([[1., -1.], [-1., 1.], [0., 0.]])
        y = torch.tensor([1])
        loss = frozen_head_loss(h, w, y, 2)
        loss.backward()
        self.assertTrue(torch.isfinite(loss))
        self.assertTrue(torch.isfinite(h.grad).all())
        self.assertAlmostEqual(loss.item(), 40000)

    def test_unsafe_usage_fails_instead_of_silently_changing_objective(self):
        h = torch.ones(2, 3)
        w = torch.ones(5, 3)
        for target, block in [(torch.tensor([-100, -100]), 2), (torch.tensor([5, 0]), 2),
                              (torch.tensor([-1, 0]), 2), (torch.tensor([0, 1]), 0),
                              (torch.tensor([0., 1.]), 2)]:
            with self.assertRaises(ValueError):
                frozen_head_loss(h, w, target, block)
        with self.assertRaises(ValueError):
            frozen_head_loss(h, w.requires_grad_(True), torch.tensor([0, 1]), 2)

    def test_causal_mask_keeps_last_prefix_prediction(self):
        hidden = torch.randn(1, 5, 3, requires_grad=True)
        other = hidden.detach().clone().requires_grad_(True)
        w = torch.randn(7, 3)
        labels = torch.tensor([[-100, -100, -100, 4, 6]])
        result = causal_frozen_head_loss(hidden, w, labels, 3)
        expected = torch.nn.functional.cross_entropy((other[:, :-1] @ w.T).reshape(-1, 7),
                                                     labels[:, 1:].reshape(-1))
        result.backward()
        expected.backward()
        torch.testing.assert_close(result, expected)
        torch.testing.assert_close(hidden.grad, other.grad)
        self.assertGreater(hidden.grad[0, 2].abs().sum().item(), 0)
        self.assertEqual(hidden.grad[0, 4].abs().sum().item(), 0)

    def test_tiny_qwen_lora_optimizer_matches_dense_causal_loss(self):
        try:
            from transformers import Qwen2Config, Qwen2ForCausalLM
            from peft import LoraConfig, get_peft_model
        except ImportError:
            self.skipTest('Requires training runtime transformers and peft')
        import copy
        config = Qwen2Config(vocab_size=31, hidden_size=16, intermediate_size=32,
                             num_hidden_layers=1, num_attention_heads=2,
                             num_key_value_heads=1, tie_word_embeddings=False,
                             attention_dropout=0.0)
        model = get_peft_model(Qwen2ForCausalLM(config), LoraConfig(
            r=2, lora_alpha=4, lora_dropout=0.0, target_modules=['q_proj'],
            task_type='CAUSAL_LM'))
        dense = copy.deepcopy(model)
        self.assertFalse(model.get_base_model().lm_head.weight.requires_grad)
        x = torch.tensor([[2, 5, 7, 8, 4]])
        y = torch.tensor([[-100, -100, 7, 8, 4]])
        a = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-3)
        b = torch.optim.AdamW([p for p in dense.parameters() if p.requires_grad], lr=1e-3)
        initial = {n: p.detach().clone() for n, p in model.named_parameters() if p.requires_grad}
        for _ in range(2):
            a.zero_grad(); b.zero_grad()
            base = model.get_base_model()
            states = base.model(input_ids=x, use_cache=False).last_hidden_state
            result = causal_frozen_head_loss(states, base.lm_head.weight, y, 7)
            expected = dense(input_ids=x, labels=y, use_cache=False).loss
            torch.testing.assert_close(result, expected)
            result.backward(); expected.backward()
            for (n, p), (m, q) in zip(model.named_parameters(), dense.named_parameters()):
                self.assertEqual(n, m)
                if p.requires_grad:
                    torch.testing.assert_close(p.grad, q.grad, atol=2e-7, rtol=1e-4)
            a.step(); b.step()
        changed = False
        for n, p in model.named_parameters():
            if p.requires_grad:
                changed |= not torch.equal(initial[n], p)
                torch.testing.assert_close(p, dict(dense.named_parameters())[n], atol=2e-6, rtol=1e-4)
        self.assertTrue(changed)


if __name__ == '__main__':
    unittest.main()
