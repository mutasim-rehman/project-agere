import sys
from pathlib import Path
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_run import Models
from evidence_contract import TokenLedger


class RuntimeTokensTests(unittest.TestCase):
    def models(self, actual=5):
        class Stub:
            _model = SimpleNamespace(token_cls=lambda: 10, token_sep=lambda: -1,
                add_bos_token=lambda: False, add_eos_token=lambda: False)
            calls = 0
            def token_bos(self):return 10
            def token_eos(self):return 20
            def tokenize(self, text, add_bos, special):
                assert special and not add_bos
                return [1, 2, 3, 4, 5]
            def reset(self):pass
            def create_completion(self, *args, **kwargs):
                self.calls += 1
                return {"choices": [{"text": "analysis", "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": actual, "completion_tokens": 1}}
        models = Models.__new__(Models)
        models.models, models.context = {"sas": Stub()}, 4096
        return models

    def test_runtime_usage_and_preflight_must_agree(self):
        models = self.models()
        self.assertEqual(models.count_prompt_tokens("sas", "Q"), 5)
        answer, event = models.call("sas", "Q", None, TokenLedger(), 8, "analyze_question")
        self.assertEqual(answer, "analysis")
        self.assertEqual(event["prompt_tokens"], 5)
        self.assertEqual(event["prompt_tokens_source"], "runtime_usage_verified")

    def test_skipped_call_has_no_prefill_cost(self):
        models = self.models()
        _, event = models.call("sas", "Q", None, TokenLedger(), 0, "analyze_question")
        self.assertEqual(event["prompt_tokens"], 0)
        self.assertEqual(event["prompt_tokens_required"], 5)
        self.assertEqual(models.models["sas"].calls, 0)

    def test_usage_mismatch_rejects_the_run(self):
        with self.assertRaisesRegex(ValueError, "differs from runtime"):
            self.models(6).call("sas", "Q", None, TokenLedger(), 8, "analyze_question")


if __name__ == "__main__":
    unittest.main()
