from copy import deepcopy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evidence_atoms import atom_catalog
from evidence_cells import cell_catalog, compile_cells


class CellTests(unittest.TestCase):
    def setUp(self):
        self.table = [["metric", "2025", "2024"], ["revenue", "$100", "$100"],
                      ["profit", "(20)", "10"]]
        self.evidence = {"table_1": "metric: revenue ; 2025: $100 ; 2024: $100",
                         "table_2": "metric: profit ; 2025: (20) ; 2024: 10",
                         "text_0": "There were 4 divisions."}

    def test_equal_values_in_one_row_keep_distinct_column_identity(self):
        view = cell_catalog(self.evidence, self.table)
        a, b = view["catalog"]["A000"], view["catalog"]["A001"]
        self.assertEqual(a["value"], b["value"])
        self.assertNotEqual(a["cell_id"], b["cell_id"])
        self.assertEqual(a["column_label"], "2025")
        self.assertEqual(b["column_label"], "2024")
        plan = {"decision": "ANSWER", "answer_unit": "number", "steps": [
            {"op": "subtract", "left": "A000", "right": "A001"}]}
        result = compile_cells(plan, view)
        self.assertEqual(result["execution"]["value"], "0")
        self.assertEqual(result["execution"]["nodes"][0]["source_spans"],
                         ["table_1/cell/1", "table_1/cell/2"])

    def test_quantity_ids_and_values_preserved_including_negative_and_text(self):
        view = cell_catalog(self.evidence, self.table)
        legacy = atom_catalog(self.evidence)
        self.assertEqual(list(view["catalog"]), list(legacy))
        for key, atom in legacy.items():
            for field in ("value", "span_id", "context"):
                self.assertEqual(view["catalog"][key][field], atom[field])
        self.assertEqual(view["catalog"]["A002"]["value"], "-20")
        self.assertEqual(view["catalog"]["A004"]["identity_scope"], "text_span")
        self.assertNotIn("2025", [a["value"] for a in view["catalog"].values()])

    def test_no_unselected_row_is_exposed(self):
        view = cell_catalog({"table_1": self.evidence["table_1"]}, self.table)
        self.assertTrue(all(a["span_id"] == "table_1" for a in view["catalog"].values()))
        self.assertFalse(any(key.startswith("table_2") for key in view["cell_evidence"]))

    def test_altered_table_cannot_substitute_another_equal_shape_row(self):
        table = deepcopy(self.table)
        table[1][0] = "liabilities"
        with self.assertRaisesRegex(ValueError, "differs"):
            cell_catalog(self.evidence, table)

    def test_ambiguous_flattening_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "delimiter"):
            cell_catalog({"table_1": "m: income ; profit ; 2025: 1"},
                         [["m", "2025"], ["income ; profit", "1"]])

    def test_unknown_source_reference_cannot_invent_a_cell(self):
        with self.assertRaisesRegex(ValueError, "Unknown"):
            compile_cells({"decision": "ANSWER", "answer_unit": "number", "steps": [
                {"op": "add", "left": "A999", "right": "CONST:1"}]},
                cell_catalog(self.evidence, self.table))


if __name__ == "__main__":
    unittest.main()
