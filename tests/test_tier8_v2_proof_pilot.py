from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_proof_pilot import select_baseline


class ProofPilotTests(unittest.TestCase):
    def test_baseline_accuracy_precedes_favorable_repair_or_delivery_precision(self):
        a = {"case_successes": 13, "delivered_correct": 13, "delivered_incorrect": 5, "total_generated_tokens": 5000}
        b = {"case_successes": 14, "delivered_correct": 12, "delivered_incorrect": 6, "total_generated_tokens": 6000}
        self.assertEqual(select_baseline({"A": a, "B": b}), "B")

    def test_ties_use_delivery_then_cost_then_stable_name(self):
        a = {"case_successes": 13, "delivered_correct": 13, "delivered_incorrect": 5, "total_generated_tokens": 5000}
        self.assertEqual(select_baseline({"A": a, "B": {**a, "delivered_incorrect": 4}}), "B")
        self.assertEqual(select_baseline({"A": a, "B": {**a, "total_generated_tokens": 4999}}), "B")
        self.assertEqual(select_baseline({"B": a, "A": a}), "A")


if __name__ == "__main__":
    unittest.main()
