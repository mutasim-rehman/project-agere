from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_adaptation_prompts import capture, tokenized_target


class ByteTokenizer:
    def tokenize(self, value, add_bos, special):
        assert special and not add_bos
        return ([999] if add_bos else []) + list(value)


class PromptCaptureTests(unittest.TestCase):
    def test_capture_uses_same_actual_prompt_for_both_arms_without_gold(self):
        public = {"id": "R", "question": "What is the ratio?",
                  "evidence": {"text_0": "Profit 200; debt 50"}, "retrieval": {"gold_used": False}}
        mas, sas = capture(public, "mas"), capture(public, "sas")
        self.assertEqual(mas["role"], "drafter")
        self.assertEqual(sas["role"], "sas")
        self.assertEqual(mas["prompt"], sas["prompt"])
        self.assertEqual(mas["requested_output_tokens"], 768)
        self.assertTrue(mas["prompt"].endswith("<|im_start|>assistant\n"))
        self.assertNotIn("Correct program", mas["prompt"])
        with self.assertRaisesRegex(ValueError, "Gold"):
            capture({**public, "qa": {}}, "sas")

    def test_labels_start_at_first_completion_token(self):
        result = tokenized_target(ByteTokenizer(), "prompt", {"decision": "ANSWER"}, 1024)
        self.assertEqual(result["label_mask_prefix_tokens"], 6)
        self.assertEqual(result["prompt_tokens"] + result["completion_tokens"], result["total_tokens"])
        self.assertTrue(result["response"].endswith("<|im_end|>"))

    def test_overflow_is_rejected_instead_of_truncating_target(self):
        with self.assertRaisesRegex(ValueError, "training_length_overflow"):
            tokenized_target(ByteTokenizer(), "x" * 1024, {"decision": "ANSWER"}, 1024)

    def test_cross_boundary_token_merge_is_rejected(self):
        class MergingTokenizer:
            def tokenize(self, value, add_bos, special):
                return [1, 2] if value == b"prompt" else [1, 3, 4]
        with self.assertRaisesRegex(ValueError, "boundary_mismatch"):
            tokenized_target(MergingTokenizer(), "prompt", {}, 1024)


if __name__ == "__main__":
    unittest.main()
