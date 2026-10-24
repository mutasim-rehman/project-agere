import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_analyze import paired, diagnostics


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

    def test_false_lock_is_visible_despite_no_regression(self):
        row = {"initial_score": {"case_success": False, "field_correct": {"owner": False, "expiry": True}},
               "score": {"case_success": False, "field_correct": {"owner": False, "expiry": True}},
               "initial_verdict": {"verdict": "FAIL", "unsupported_fields": ["expiry"]},
               "repair": "patch", "repair_attempted": True, "repair_scope": ["expiry"],
               "delivered": False, "tokens": 50, "stages": []}
        result = diagnostics([row])
        self.assertEqual(result["field_repair_regressions"], 0)
        self.assertEqual(result["wrong_fields_left_locked"], 1)
        self.assertEqual(result["initial_verifier_true_rejects"], 1)

    def test_false_accept_is_not_hidden_by_support_gate(self):
        row = {"initial_score": {"case_success": False, "field_correct": {"owner": False}},
               "score": {"case_success": False, "field_correct": {"owner": False}},
               "initial_verdict": {"verdict": "PASS", "unsupported_fields": []},
               "repair": "none", "repair_attempted": False, "repair_scope": [],
               "delivered": False, "tokens": 50, "stages": []}
        self.assertEqual(diagnostics([row])["initial_verifier_false_accepts"], 1)


if __name__ == "__main__":
    unittest.main()
