import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_analyze import paired


class AnalysisTests(unittest.TestCase):
    def test_paired_identity_has_zero_difference(self):
        rows = {str(i): {"score": {"case_success": i % 2 == 0}} for i in range(4)}
        result = paired(rows, rows)
        self.assertEqual(result["right_minus_left_success"], 0)
        self.assertEqual(result["paired_bootstrap_95_interval"], [0, 0])
        self.assertEqual(result["exact_mcnemar_p"], 1)

    def test_unpaired_cases_are_rejected(self):
        with self.assertRaises(ValueError):
            paired({"a": {}}, {"b": {}})


if __name__ == "__main__":
    unittest.main()
