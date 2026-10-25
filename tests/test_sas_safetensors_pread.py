from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
try:
    import torch
    from transformers import Qwen2Config, modeling_utils
    from sas_cpu_weight_storage import StorageDetachedQwen2ForCausalLM
except ImportError:
    torch = None
from sas_safetensors_pread import pread_checkpoint_loading


@unittest.skipIf(torch is None, 'Requires training runtime')
class PreadTests(unittest.TestCase):
    def test_actual_sharded_meta_loader_keeps_identical_weights(self):
        torch.set_num_threads(1)
        config = Qwen2Config(vocab_size=31, hidden_size=16, intermediate_size=32,
                             num_hidden_layers=1, num_attention_heads=2,
                             num_key_value_heads=1, tie_word_embeddings=False)
        model = StorageDetachedQwen2ForCausalLM(config)
        original = modeling_utils.safe_open
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / '.local/tmp') as folder:
            model.save_pretrained(folder, max_shard_size='3KB')
            calls = []
            def spy(*args, **kwargs):
                calls.append(kwargs.get('backend'))
                return original(*args, **kwargs)
            modeling_utils.safe_open = spy
            try:
                with pread_checkpoint_loading():
                    loaded = StorageDetachedQwen2ForCausalLM.from_pretrained(folder, device_map={'': 'cpu'})
                self.assertIs(modeling_utils.safe_open, spy)
            finally:
                modeling_utils.safe_open = original
            self.assertTrue(calls)
            self.assertEqual(set(calls), {'pread'})
            self.assertEqual(set(model.state_dict()), set(loaded.state_dict()))
            for name, expected in model.state_dict().items():
                torch.testing.assert_close(loaded.state_dict()[name], expected, atol=0, rtol=0)

    def test_restores_module_reference_on_exception(self):
        original = modeling_utils.safe_open
        with self.assertRaisesRegex(RuntimeError, 'sentinel'):
            with pread_checkpoint_loading():
                self.assertIsNot(modeling_utils.safe_open, original)
                raise RuntimeError('sentinel')
        self.assertIs(modeling_utils.safe_open, original)


if __name__ == '__main__':
    unittest.main()
