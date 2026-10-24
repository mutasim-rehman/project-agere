from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_table_retrieval import table_complete_packet


class TableRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.row = {"id": "R", "qa": {"question": "what was revenue?", "answer": "SECRET", "gold_inds": {"text_4": "SECRET"}},
                    "table": [["metric", "2014"], ["revenue", "100"], ["unrelated", "200"]],
                    "pre_text": ["revenue alpha", "revenue beta", "revenue gamma", "revenue delta", "unrelated omega"], "post_text": []}

    def test_all_table_rows_survive_and_text_count_is_bounded(self):
        p = table_complete_packet(self.row, text_limit=2)
        self.assertEqual({k for k in p["evidence"] if k.startswith("table_")}, {"table_1", "table_2"})
        self.assertEqual(p["retrieval"]["text_units_retained"], 2)

    def test_gold_and_supplied_retrieval_cannot_change_selection(self):
        altered = deepcopy(self.row)
        altered["qa"] = {"question": self.row["qa"]["question"], "program": "SECRET", "gold_inds": {"table_2": "OTHER"}}
        altered["model_input"] = "FORCE OTHER EVIDENCE"
        self.assertEqual(table_complete_packet(self.row), table_complete_packet(altered))
        self.assertNotIn("SECRET", str(table_complete_packet(self.row)))


if __name__ == "__main__":
    unittest.main()
