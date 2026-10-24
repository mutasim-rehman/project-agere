import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_finqa import packet


class FinQATests(unittest.TestCase):
    def test_gold_annotations_cannot_influence_packet(self):
        row = {"id": "R", "table": [["year", "profit"], ["2025", "10"]],
               "pre_text": ["Revenue was 20."], "post_text": [],
               "qa": {"question": "What was profit in 2025?", "answer": "10", "program": "SECRET", "gold_inds": {"table_1": "SECRET"}},
               "table_retrieved": "SECRET", "model_input": "SECRET"}
        altered = copy.deepcopy(row)
        altered["qa"].update({"answer": "WRONG", "program": "WRONG", "gold_inds": {}})
        altered["table_retrieved"] = "WRONG"
        self.assertEqual(packet(row), packet(altered))
        self.assertNotIn("SECRET", str(packet(row)))

    def test_original_table_row_identifiers_are_preserved(self):
        row = {"id": "R", "table": [["company", "profit"], ["A", "10"], ["B", "20"]],
               "pre_text": [], "post_text": [], "qa": {"question": "profit B"}}
        result = packet(row, limit=1)
        self.assertEqual(list(result["evidence"]), ["table_2"])
        self.assertIn("profit: 20", result["evidence"]["table_2"])


if __name__ == "__main__":
    unittest.main()
