import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import tier8_v2_adapter_runtime as runtime
from tier8_v2_run import Models, model_files


class AdapterRuntimeTests(unittest.TestCase):
    def test_fit_and_wrong_checkpoint_cannot_be_primary_systems(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".local") as temp:
            folder = Path(temp);(folder / "converted").mkdir()
            manifest = {"status": "complete", "training_mode": "fit", "diagnostic_only": True}
            (folder / "converted/manifest.json").write_text(json.dumps(manifest))
            with patch.object(runtime, "ROOT", folder):
                with self.assertRaisesRegex(ValueError, "full trained"):
                    runtime.load_adapter("converted", "mas", "3b-q4")
                manifest.update(training_mode="train", diagnostic_only=False, profile="7b", tensor_count=2)
                (folder / "converted/manifest.json").write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, "profile differs"):
                    runtime.load_adapter("converted", "mas", "3b-q4")
                with self.assertRaisesRegex(ValueError, "profile requires"):
                    runtime.load_adapter("converted", "mas", "1.5b-f16")

    def test_provenance_and_final_file_are_verified(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".local") as temp:
            folder = Path(temp);run = folder / "train";adapter = run / "adapter"
            adapter.mkdir(parents=True);(folder / "converted").mkdir()
            for name in ("adapter_config.json", "adapter_model.safetensors"):
                (adapter / name).write_bytes(b"integrity fixture")
            (run / "manifest.json").write_text(json.dumps({"mode": "train", "profile": "3b"}))
            (run / "summary.json").write_text(json.dumps({"status": "complete", "mode": "train",
                "optimizer_updates": 83, "changed_adapter_tensors": 2,
                "adapter_files": {p.name: runtime.sha(p) for p in adapter.iterdir()}}))
            gguf = folder / "converted/adapter.gguf";gguf.write_bytes(b"GGUF integrity fixture")
            info = {"status": "complete", "training_mode": "train", "diagnostic_only": False,
                    "profile": "3b", "tensor_count": 2, "run": "train", "file": "converted/adapter.gguf",
                    "bytes": gguf.stat().st_size, "sha256": runtime.sha(gguf),
                    "input_sha256": {"train/" + n: runtime.sha(run / n) for n in ("manifest.json", "summary.json")}}
            (folder / "converted/manifest.json").write_text(json.dumps(info))
            with patch.object(runtime, "ROOT", folder):
                self.assertEqual(runtime.load_adapter("converted", "mas", "3b-q4")["role"], "drafter")
                gguf.write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "file integrity"):
                    runtime.load_adapter("converted", "mas", "3b-q4")

    def test_adapter_attaches_to_drafter_only(self):
        calls = []
        def fake_llama(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(_lora_adapter=object() if kwargs.get("lora_path") else None)
        info = {"role": "drafter", "file": "weights/fixture.gguf", "sha256": "fixture", "scale": 1.0}
        with patch.dict(sys.modules, {"llama_cpp": SimpleNamespace(Llama=fake_llama, LlamaGrammar=object)}), patch("tier8_v2_run.load_adapter", return_value=info):
            models = Models("mas", 4096, use_selector=False, drafter_model="3b-q4", adapter="fixture")
        self.assertEqual(sum("lora_path" in x for x in calls), 1)
        self.assertIn("3b", next(x["model_path"] for x in calls if "lora_path" in x))
        self.assertEqual(set(models.adapter_applications), {"drafter"})

    def test_backend_must_create_real_handle(self):
        info = {"role": "drafter", "file": "weights/fixture.gguf", "sha256": "fixture", "scale": 1.0}
        with patch.dict(sys.modules, {"llama_cpp": SimpleNamespace(Llama=lambda **kw: SimpleNamespace(), LlamaGrammar=object)}), patch("tier8_v2_run.load_adapter", return_value=info):
            with self.assertRaisesRegex(RuntimeError, "not initialized"):
                Models("mas", 4096, use_selector=False, drafter_model="3b-q4", adapter="fixture")

    def test_same_base_with_different_adapter_policies_has_distinct_instances(self):
        calls = []
        def fake_llama(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(_lora_adapter=object() if kwargs.get("lora_path") else None)
        info = {"role": "drafter", "file": "weights/fixture.gguf", "sha256": "fixture", "scale": 1.0}
        with patch.dict(sys.modules, {"llama_cpp": SimpleNamespace(Llama=fake_llama, LlamaGrammar=object)}), patch("tier8_v2_run.load_adapter", return_value=info):
            models = Models("mas", 4096, residency="shared", verifier_model="3b", use_selector=False, drafter_model="3b-q4", adapter="fixture")
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]["model_path"], calls[1]["model_path"])
        self.assertIsNot(models.models["drafter"], models.models["verifier"])
        self.assertEqual(sum("lora_path" in x for x in calls), 1)

    def test_unadapted_same_base_roles_are_explicitly_shared(self):
        files = model_files("mas", verifier_model="3b", use_selector=False, drafter_model="3b-q4")
        self.assertEqual(files["drafter"], files["verifier"])
        with patch.dict(sys.modules, {"llama_cpp": SimpleNamespace(Llama=lambda **kw: object(), LlamaGrammar=object)}):
            models = Models("mas", 4096, residency="shared", verifier_model="3b", use_selector=False, drafter_model="3b-q4")
        self.assertIs(models.models["drafter"], models.models["verifier"])


if __name__ == "__main__":
    unittest.main()
