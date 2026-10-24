from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from program_binding_domains import binding_domains, resolve_domains


class BindingDomainTests(unittest.TestCase):
    def test_equal_values_in_distinct_cells_do_not_force_alias(self):
        atoms = {"A0": {"value": "65", "span_id": "year_2019"}, "A1": {"value": "65", "span_id": "year_2020"}}
        result = binding_domains("subtract(65, 65)", atoms)
        self.assertEqual(result["steps"], [{"op": "subtract", "left": "V0", "right": "V1"}])
        self.assertEqual(result["slots"]["V0"]["candidate_quantity_ids"], ["A0", "A1"])
        self.assertIsNone(result["resolved_steps"])
        self.assertFalse(result["numeric_binding_unique"])

    def test_annotation_is_a_hint_not_a_cell_identity_certificate(self):
        atoms = {"A0": {"value": "65", "span_id": "year_2019"}, "A1": {"value": "65", "span_id": "year_2021"}}
        result = binding_domains("subtract(65, 65)", atoms, {"year_2021"})
        self.assertEqual(result["slots"]["V0"]["annotated_span_candidates"], ["A1"])
        self.assertEqual(len(result["slots"]["V0"]["candidate_quantity_ids"]), 2)
        self.assertIsNone(result["resolved_steps"])

    def test_unique_repeated_cell_and_step_dependencies_are_preserved(self):
        atoms = {"A0": {"value": "1654", "span_id": "S"}, "A1": {"value": "1251", "span_id": "S"}}
        result = binding_domains("subtract(1654, 1251), add(#0, 1654)", atoms)
        self.assertEqual(result["steps"][1]["right"], result["steps"][0]["left"])
        self.assertEqual(result["resolved_steps"][1], {"op": "add", "left": "#0", "right": "A0"})

    def test_constant_is_never_rebound_to_equal_evidence_value(self):
        result = binding_domains("multiply(2, const_2)", {"A0": {"value": "2", "span_id": "S"}})
        self.assertEqual(result["resolved_steps"], [{"op": "multiply", "left": "A0", "right": "CONST:2"}])

    def test_unparsed_text_and_future_references_are_rejected(self):
        for text in ("junk add(2, 2)", "add(2, 2) junk", "add(#0, 2)", "add(2, 2)add(2, 2)"):
            with self.assertRaises(ValueError):
                binding_domains(text, {"A0": {"value": "2", "span_id": "S"}})

    def test_explicit_resolution_preserves_distinct_or_shared_choices(self):
        partial = binding_domains("subtract(65, 65)", {"A0": {"value": "65", "span_id": "S0"}, "A1": {"value": "65", "span_id": "S1"}})
        self.assertEqual(resolve_domains(partial, {"V0": "A1", "V1": "A0"}), [{"op": "subtract", "left": "A1", "right": "A0"}])
        with self.assertRaises(ValueError):
            resolve_domains(partial, {"V0": "A0"})
        with self.assertRaises(ValueError):
            resolve_domains(partial, {"V0": "A0", "V1": "A2"})


if __name__ == "__main__":
    unittest.main()
