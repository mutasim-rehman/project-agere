from copy import deepcopy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evidence_atoms import atom_catalog, compile_plan, patch_plan
from evidence_calculator import execute


class AtomTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {"table_3": "company: A ; revenue: $1,200 ; transactions: 5.0"}
        self.atoms = atom_catalog(self.evidence)
        self.plan = {"decision": "ANSWER", "answer_unit": "number", "steps": [{"op": "divide", "left": "A000", "right": "A001"}]}

    def test_source_pointers_copy_values_with_citations(self):
        compiled = compile_plan(self.plan, self.atoms)
        self.assertEqual(compiled["steps"][0]["left"], {"value": "1200", "span_id": "table_3"})
        self.assertEqual(execute(compiled["steps"], self.evidence)["value"], "2.4E+2")

    def test_unknown_reference_cannot_invent_a_value(self):
        bad = deepcopy(self.plan)
        bad["steps"][0]["left"] = "1200000"
        with self.assertRaisesRegex(ValueError, "Unknown"):
            compile_plan(bad, self.atoms)

    def test_column_year_is_context_not_copied_as_cell_value(self):
        atoms = atom_catalog({"table_1": "item: profit ; 2025: 100"})
        self.assertEqual([a["value"] for a in atoms.values()], ["100"])
        self.assertIn("2025", atoms["A000"]["context"])

    def test_patch_recomputes_dependent_step_without_editing_it(self):
        plan = deepcopy(self.plan)
        plan["steps"].append({"op": "multiply", "left": "#0", "right": "CONST:100"})
        fixed, accepted = patch_plan(plan, {"updates": [{"index": 0, "step": {"op": "subtract", "left": "A000", "right": "A001"}}]}, {0}, self.atoms, self.evidence)
        self.assertTrue(accepted)
        self.assertEqual(fixed["steps"][1], plan["steps"][1])
        self.assertEqual(execute(compile_plan(fixed, self.atoms)["steps"], self.evidence)["value"], "119500.0")

    def test_patch_cannot_modify_a_locked_step(self):
        fixed, accepted = patch_plan(self.plan, {"updates": [{"index": 0, "step": self.plan["steps"][0]}]}, set(), self.atoms, self.evidence)
        self.assertFalse(accepted)
        self.assertEqual(fixed, self.plan)


if __name__ == "__main__":
    unittest.main()
