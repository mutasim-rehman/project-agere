import sys
from pathlib import Path
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from completion_tokenization import completion_tokens


class CompletionTokenizationTests(unittest.TestCase):
    def model(self, bos=False, eos=False, cls=-1, sep=-1):
        def tokenize(value, add_bos, special):
            self.assertFalse(add_bos)
            self.assertTrue(special)
            self.assertEqual(value, b"chat")
            return [30, 31]
        return SimpleNamespace(_model=SimpleNamespace(token_cls=lambda: cls, token_sep=lambda: sep,
            add_bos_token=lambda: bos, add_eos_token=lambda: eos), token_bos=lambda: 10,
            token_eos=lambda: 20, tokenize=tokenize)

    def test_qwen_unused_cls_is_not_added(self):
        self.assertEqual(completion_tokens(self.model(cls=10), "chat"), [30, 31])

    def test_actual_automatic_bos_and_eos_are_preserved(self):
        self.assertEqual(completion_tokens(self.model(bos=True, eos=True), "chat"), [10, 30, 31, 20])

    def test_cls_and_sep_match_runtime_precedence(self):
        self.assertEqual(completion_tokens(self.model(bos=True, cls=11, sep=21), "chat"), [11, 30, 31, 21])

    def test_other_prompt_modes_are_not_silently_approximated(self):
        for prompt in ("", [1, 2]):
            with self.assertRaises(ValueError):
                completion_tokens(self.model(), prompt)


if __name__ == "__main__":
    unittest.main()
