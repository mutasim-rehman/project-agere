from copy import deepcopy
from pathlib import Path
import sys
import unittest
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_adaptation_data import adaptation_split, prepare, validate_prepared


class AdaptationDataTests(unittest.TestCase):
    def setUp(self):
        self.row = {"id": "COMPANY/2020/page_1.pdf-1", "table": [
            ["measure", "2020"], ["profit", "200"], ["debt service", "50"]],
            "pre_text": [], "post_text": [], "qa": {"question": "What is the ratio of profit to debt service?",
            "program": "divide(200, 50)", "exe_ans": 4, "answer": "4.0",
            "gold_inds": {"table_1": "profit", "table_2": "debt"}}}

    def test_report_group_cannot_cross_training_validation(self):
        self.assertEqual(adaptation_split("COMPANY/2020/page_1.pdf-1"),
                         adaptation_split("COMPANY/2020/page_99.pdf-2"))
        splits = {adaptation_split(f"C{i}/2020/page_1.pdf-1") for i in range(100)}
        self.assertEqual(splits, {"train", "validation"})

    def test_unique_source_target_has_no_gold_fields_in_public_input(self):
        result = prepare(self.row)
        self.assertEqual(result["target"]["decision"], "ANSWER")
        self.assertTrue(result["bindings"])
        self.assertNotIn("qa", result["public"])
        self.assertNotIn("gold_inds", result["public"])
        self.assertNotIn("exe_ans", result["public"])

    def test_ambiguous_operand_is_not_replaced_by_first_matching_cell(self):
        row = deepcopy(self.row)
        row["table"].append(["another unrelated measure", "200"])
        with self.assertRaisesRegex(ValueError, "ambiguous_source_identity"):
            prepare(row)

    def test_target_outside_deployment_units_is_quarantined(self):
        row = deepcopy(self.row)
        row["qa"]["answer"] = "400%"
        with self.assertRaisesRegex(ValueError, "outside_deployment_grammar"):
            prepare(row)

    def test_serialized_reload_preserves_target_source_identities(self):
        result = prepare(self.row)
        validate_prepared(json.loads(json.dumps(result, sort_keys=True)))
        reversed_evidence = dict(reversed(list(result["public"]["evidence"].items())))
        result["public"]["evidence"] = reversed_evidence
        with self.assertRaisesRegex(ValueError, "Persisted quantity IDs"):
            validate_prepared(result)


if __name__ == "__main__":
    unittest.main()
