import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_financial_pipeline import evaluate_financial
from tier8_v2_unit_audit import evaluate_v2


class UnitAuditTests(unittest.TestCase):
    def test_prompt_permitted_ratio_is_not_rejected_for_number_label(self):
        row = {"qa": {"answer": "10.94%", "exe_ans": .10935}}
        answer = {"decision": "ANSWER", "answer_unit": "number"}
        execution = {"value": "0.10935", "issues": []}
        self.assertFalse(evaluate_financial(row, answer, execution)["case_success"])
        self.assertTrue(evaluate_v2(row, answer, execution)["case_success"])
        self.assertEqual(answer["answer_unit"], "number")

    def test_no_gold_dependent_rescale_or_invalid_label_rescue(self):
        row = {"qa": {"answer": "10.94%", "exe_ans": .10935}}
        for label, value in (("number", "10.94"), ("percent", ".10935"), ("invalid", ".10935")):
            with self.subTest(label=label):
                self.assertFalse(evaluate_v2(row, {"decision": "ANSWER", "answer_unit": label},
                                             {"value": value, "issues": []})["case_success"])

    def test_abstention_and_execution_failures_remain_failures(self):
        row = {"qa": {"answer": "10.94%", "exe_ans": .10935}}
        for decision, issues in (("INSUFFICIENT", []), ("ANSWER", [{"code": "unsupported"}])):
            self.assertFalse(evaluate_v2(row, {"decision": decision, "answer_unit": "number"},
                                         {"value": ".10935", "issues": issues})["case_success"])

    def test_bare_numeric_gold_is_not_silently_reinterpreted_as_percent(self):
        row = {"qa": {"answer": ".2", "exe_ans": .2}}
        self.assertFalse(evaluate_v2(row, {"decision": "ANSWER", "answer_unit": "percent"},
                                     {"value": ".2", "issues": []})["case_success"])


if __name__ == "__main__":
    unittest.main()
