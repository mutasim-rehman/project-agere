import copy
import json
import sys
import hashlib
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_data import generate
from tier8_v2_run import run_case, verified_models


class FakeModels:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.prompts = []

    def call(self, role, content, schema, budget, requested, stage):
        self.prompts.append(content)
        budget.charge(10)
        return next(self.responses), {"stage": stage, "role": role, "generated_tokens": 10}


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.case = generate(0)
        self.public = {k: v for k, v in self.case.items() if k != "gold"}
        self.good = {"case_id": self.case["id"], **copy.deepcopy(self.case["gold"])}

    def test_semantic_verifier_fail_blocks_supported_answer(self):
        models = FakeModels([self.good, {"verdict": "FAIL", "unsupported_fields": ["registered_owner"]}])
        result = run_case(self.public, models, "sas", "none")
        self.assertFalse(result["delivered"])
        self.assertIn("2025-09-01", models.prompts[-1])
        self.assertNotIn('"gold"', "".join(models.prompts))

    def test_patch_repair_needs_fresh_verdict(self):
        bad = copy.deepcopy(self.good)
        bad["facts"]["identity_expiry_date"] = {"value": "2035-01-01", "span_id": "invented"}
        patch = {"identity_expiry_date": self.good["facts"]["identity_expiry_date"]}
        models = FakeModels([bad, {"verdict": "FAIL", "unsupported_fields": ["identity_expiry_date"]},
                             patch, {"verdict": "PASS", "unsupported_fields": []}])
        result = run_case(self.public, models, "sas", "patch")
        self.assertTrue(result["delivered"])
        self.assertEqual(result["answer"], self.good)
        self.assertEqual(result["stages"][-1]["stage"], "verify_repair")

    def test_unsupported_patch_is_rejected_and_not_delivered(self):
        bad = copy.deepcopy(self.good)
        bad["facts"]["registered_owner"] = {"value": "Imaginary Person", "span_id": "invented"}
        models = FakeModels([bad, {"verdict": "FAIL", "unsupported_fields": ["registered_owner"]},
                             {"registered_owner": {"value": "Another Fiction", "span_id": "invented"}}])
        result = run_case(self.public, models, "sas", "patch")
        self.assertFalse(result["repair_accepted"])
        self.assertFalse(result["delivered"])

    def test_contradictory_pass_is_not_delivery_authorization(self):
        models = FakeModels([self.good, {"verdict": "PASS", "unsupported_fields": ["registered_owner"]}])
        result = run_case(self.public, models, "sas", "none")
        self.assertFalse(result["delivered"])

    def test_changed_weight_fails_integrity_gate(self):
        root = Path(__file__).resolve().parents[1]
        (root / ".local/tmp").mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root / ".local/tmp") as directory:
            base = Path(directory)
            evidence = base / "research/tier8_v2/evidence"
            evidence.mkdir(parents=True)
            entries = []
            for name in ("qwen2.5-0.5b-instruct-fp16.gguf", "qwen2.5-1.5b-instruct-fp16.gguf"):
                (base / name).write_bytes(b"verified-fixture")
                entries.append({"file": name, "bytes": 16, "sha256": hashlib.sha256(b"verified-fixture").hexdigest()})
            (evidence / "models.json").write_text(json.dumps(entries))
            with patch("tier8_v2_run.ROOT", base):
                self.assertEqual(len(verified_models("mas")), 2)
                (base / entries[0]["file"]).write_bytes(b"tampered-fixture")
                with self.assertRaisesRegex(ValueError, "integrity mismatch"):
                    verified_models("mas")


if __name__ == "__main__":
    unittest.main()
