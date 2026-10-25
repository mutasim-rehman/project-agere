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
            original = torch.randn_like(module.weight)
            source = torch.frombuffer(bytearray(original.numpy().tobytes()), dtype=original.dtype).reshape_as(original)
            self.assertFalse(source.untyped_storage().resizable())
            expected = source.clone()
            module.load_state_dict({'weight': source}, assign=True)
            self.assertNotEqual(module.weight.data_ptr(), source.data_ptr())
            torch.testing.assert_close(module.weight, expected, atol=0, rtol=0)
            source.zero_()
            torch.testing.assert_close(module.weight, expected, atol=0, rtol=0)
            self.assertEqual(module._cpu_storage_detach_count, 1)

    def test_owned_cpu_storage_is_not_copied_again(self):
        from sas_cpu_weight_storage import detach_cpu_storage
        module = torch.nn.Linear(4, 3, bias=False)
        source = torch.randn_like(module.weight)
        self.assertTrue(source.untyped_storage().resizable())
        module.register_load_state_dict_post_hook(detach_cpu_storage)
        module.load_state_dict({'weight': source}, assign=True)
        self.assertEqual(module.weight.data_ptr(), source.data_ptr())
        self.assertEqual(getattr(module, '_cpu_storage_clone_count', 0), 0)

    def test_real_safetensors_mapping_and_dtype_conversion(self):
        import tempfile
        from safetensors import safe_open
        from safetensors.torch import save_file
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / '.local/tmp') as folder:
            p = Path(folder) / 'tiny.safetensors'
            save_file({'weight': torch.randn(3, 4, dtype=torch.bfloat16)}, str(p))
            with safe_open(str(p), framework='pt', device='cpu') as f:
                mapped = f.get_tensor('weight')
                self.assertFalse(mapped.untyped_storage().resizable())
                converted = mapped.float()
                self.assertTrue(converted.untyped_storage().resizable())
                torch.testing.assert_close(converted, mapped.float(), atol=0, rtol=0)


if __name__ == '__main__':
    unittest.main()
