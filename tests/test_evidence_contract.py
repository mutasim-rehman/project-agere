import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evidence_contract import TokenLedger, check_claim, commit_patch, validate


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.spans = {"D#L01": "L01 name=Amina Cedar; balance=1200; expiry=2028-12-31."}
        self.calcs = {"CALC#DSCR": 1.25}
        self.answer = {"case_id": "C", "facts": {
            "name": {"value": "Amina Cedar", "span_id": "D#L01"},
            "balance": {"value": 120, "span_id": "D#L01"}}}

    def test_substring_is_not_numeric_evidence(self):
        self.assertEqual(check_claim(self.answer["facts"]["balance"], self.spans, {}), "unsupported_value")

    def test_boolean_is_not_calculator_number(self):
        self.assertEqual(check_claim({"value": True, "span_id": "CALC#DSCR"}, {}, {"CALC#DSCR": 1}), "invalid_value")

    def test_atomic_repair_preserves_good_claims(self):
        before = copy.deepcopy(self.answer)
        fixed, accepted = commit_patch(self.answer, {"balance": {"value": 1200, "span_id": "D#L01"}},
                                      allowed={"balance"}, spans=self.spans, calculations={})
        self.assertTrue(accepted)
        self.assertEqual(fixed["facts"]["name"], before["facts"]["name"])
        self.assertEqual(self.answer, before)

    def test_repair_cannot_change_locked_claim(self):
        fixed, accepted = commit_patch(self.answer, {"name": {"value": "Amina Cedar", "span_id": "D#L01"}},
                                      allowed={"balance"}, spans=self.spans, calculations={})
        self.assertFalse(accepted)
        self.assertEqual(fixed, self.answer)

    def test_batch_with_bad_claim_is_rejected_atomically(self):
        fixed, accepted = commit_patch(self.answer, {
            "balance": {"value": 1200, "span_id": "D#L01"},
            "name": {"value": "Invented", "span_id": "D#L01"}},
            allowed={"balance", "name"}, spans=self.spans, calculations={})
        self.assertFalse(accepted)
        self.assertEqual(fixed, self.answer)

    def test_missing_needs_absence_evidence(self):
        self.assertEqual(check_claim({"value": "MISSING", "span_id": None}, {}, {}), "absence_unverified")

    def test_checker_does_not_need_labels(self):
        issues = validate(self.answer, case_id="C", fields=("name", "balance"), spans=self.spans, calculations={})
        self.assertEqual([(i.field, i.code) for i in issues], [("balance", "unsupported_value")])

    def test_ledger_reserves_and_enforces_budget(self):
        ledger = TokenLedger(100)
        self.assertEqual(ledger.allowance(100, reserve=25), 75)
        ledger.charge(75)
        self.assertEqual(ledger.allowance(100), 25)
        with self.assertRaises(ValueError):
            ledger.charge(26)


if __name__ == "__main__":
    unittest.main()
