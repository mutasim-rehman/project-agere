from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
try:
    import torch
    from transformers import Qwen2Config
    from sas_cpu_weight_storage import StorageDetachedQwen2ForCausalLM
except ImportError:
    torch = None


@unittest.skipIf(torch is None, 'Requires training runtime')
class CpuStorageTests(unittest.TestCase):
    def test_assigned_cpu_weights_have_independent_storage_and_identical_values(self):
        torch.set_num_threads(1)
        config = Qwen2Config(vocab_size=31, hidden_size=16, intermediate_size=32,
                             num_hidden_layers=1, num_attention_heads=2,
                             num_key_value_heads=1, tie_word_embeddings=False)
        model = StorageDetachedQwen2ForCausalLM(config)
        for module in [model.get_input_embeddings(), model.get_output_embeddings()]:
            source = torch.randn_like(module.weight)
            expected = source.clone()
            module.load_state_dict({'weight': source}, assign=True)
            self.assertNotEqual(module.weight.data_ptr(), source.data_ptr())
            torch.testing.assert_close(module.weight, expected, atol=0, rtol=0)
            source.zero_()
            torch.testing.assert_close(module.weight, expected, atol=0, rtol=0)
            self.assertEqual(module._cpu_storage_detach_count, 1)


if __name__ == '__main__':
    unittest.main()
