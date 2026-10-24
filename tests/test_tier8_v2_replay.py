import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_replay import snapshot_rows


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.row = {"case_id": "R", "plan": {"steps": []}, "answer": {"decision": "INSUFFICIENT"},
                    "final_verdict": {"verdict": "FAIL"}, "tokens": 20,
                    "stages": [{"generated_tokens": 20, "seconds": 1.0}],
                    "score": {"case_success": True, "SECRET_GOLD": "DO NOT EXPORT"}}

    def test_snapshot_export_removes_evaluation_state(self):
        rows = snapshot_rows([self.row])
        self.assertEqual(set(rows[0]["snapshot"]), {"plan", "answer", "verdict", "tokens"})
        self.assertNotIn("SECRET_GOLD", json.dumps(rows))
        self.assertNotIn("score", json.dumps(rows))

    def test_token_debit_must_agree_with_original_trace(self):
        with self.assertRaises(ValueError):
            snapshot_rows([{**self.row, "tokens": 19}])

    def test_duplicate_cohort_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            snapshot_rows([self.row, self.row])


if __name__ == "__main__":
    unittest.main()
