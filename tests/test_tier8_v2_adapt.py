import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_adapt import encode_example


class AdaptTests(unittest.TestCase):
    def setUp(self):
        class Tokenizer:
            def encode(self, text, add_special_tokens):
                assert not add_special_tokens
                return list(text.encode())
        self.tokenizer = Tokenizer()
        self.row = {"source_id": "TRAIN", "split": "train", "prompt": "prompt",
                    "tokenization": {"P": {"response": "target", "label_mask_prefix_tokens": 6,
                    "input_ids_sha256": hashlib.sha256(json.dumps(list(b"prompttarget")).encode()).hexdigest()}}}

    def test_only_complete_target_tokens_are_trainable(self):
        row = encode_example(self.tokenizer, self.row, "P")
        self.assertEqual(row["labels"][:6], [-100] * 6)
        self.assertEqual(row["labels"][6:], list(b"target"))
        self.assertEqual(row["split"], "train")

    def test_any_tokenizer_difference_rejects_example(self):
        self.row["tokenization"]["P"]["input_ids_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "differs from deployment"):
            encode_example(self.tokenizer, self.row, "P")

    def test_empty_supervision_rejected(self):
        m = self.row["tokenization"]["P"]
        m["response"] = ""
        m["input_ids_sha256"] = hashlib.sha256(json.dumps(list(b"prompt")).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, "boundary/length"):
            encode_example(self.tokenizer, self.row, "P")


if __name__ == "__main__":
    unittest.main()
