import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from tier8_v2_adapter_convert import check_architecture, validate_adapter


class AdapterConversionTests(unittest.TestCase):
    def test_architecture_mismatch_and_incomplete_config_rejected(self):
        config = {"model_type": "qwen2", **{k: 8 for k in
                 ("hidden_size", "intermediate_size", "num_attention_heads", "num_key_value_heads", "num_hidden_layers", "vocab_size")}}
        check_architecture(config, dict(config))
        with self.assertRaisesRegex(ValueError, "differs"):
            check_architecture(config, {**config, "hidden_size": 16})
        with self.assertRaisesRegex(ValueError, "complete"):
            check_architecture({}, {})

    def test_initialized_or_tampered_adapter_rejected_before_conversion(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".local") as temp:
            folder = Path(temp);adapter = folder / "adapter";adapter.mkdir()
            for name in ("adapter_config.json", "adapter_model.safetensors"):
                (adapter / name).write_text("fixture")
            hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in adapter.iterdir()}
            (folder / "manifest.json").write_text(json.dumps({"mode": "fit"}))
            summary = {"status": "complete", "changed_adapter_tensors": 0, "optimizer_updates": 2,
                       "mode": "fit", "adapter_files": hashes}
            (folder / "summary.json").write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError, "real adapter updates"):
                validate_adapter(folder)
            summary["changed_adapter_tensors"] = 1
            (folder / "summary.json").write_text(json.dumps(summary))
            validate_adapter(folder)  # Metadata/integrity fixture only, not a real trained adapter.
            (adapter / "adapter_model.safetensors").write_text("modified")
            with self.assertRaisesRegex(ValueError, "integrity"):
                validate_adapter(folder)


if __name__ == "__main__":
    unittest.main()
