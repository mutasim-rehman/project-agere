import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from supervised_logits import supervised_window


class SupervisedLogitsTests(unittest.TestCase):
    def test_prefix_context_and_first_target_prediction_preserved(self):
        row = {"input_ids": [1, 2, 3, 4, 5], "labels": [-100, -100, -100, 4, 5]}
        result = supervised_window(row)
        self.assertEqual(result["input_ids"], row["input_ids"])
        self.assertEqual(result["labels"], [-100, 4, 5])
        self.assertEqual(result["logits_to_keep"], 3)
        self.assertEqual(result["supervised_tokens"], 2)

    def test_empty_gapped_or_changed_targets_rejected(self):
        for labels in ([-100] * 3, [1, 2, 3], [-100, 2, -100], [-100, 9, 3]):
            with self.subTest(labels=labels), self.assertRaises(ValueError):
                supervised_window({"input_ids": [1, 2, 3], "labels": labels})


if __name__ == "__main__":
    unittest.main()
