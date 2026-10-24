import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evidence_calculator import execute, numeric_tokens


def op(value, span):
    return {"value": value, "span_id": span}


class CalculatorTests(unittest.TestCase):
    def test_cited_multistep_result_has_transitive_lineage(self):
        program = [{"op": "subtract", "left": op("200", "T1"), "right": op("100", "T2")},
                   {"op": "divide", "left": op("#0", "STEP#0"), "right": op("100", "T2")}]
        result = execute(program, {"T1": "profit 200", "T2": "prior profit 100"})
        self.assertEqual(result["value"], "1")
        self.assertEqual(result["nodes"][-1]["source_spans"], ["T1", "T2"])

    def test_invented_operand_rejected_despite_valid_arithmetic(self):
        result = execute([{"op": "divide", "left": op("200", "T1"), "right": op("100", "CONST")}], {"T1": "profit 20"})
        self.assertEqual(result["issues"][0]["code"], "unsupported_operand")

    def test_future_reference_rejected(self):
        result = execute([{"op": "add", "left": op("#1", "STEP#1"), "right": op("1", "CONST")}], {})
        self.assertEqual(result["issues"][0]["code"], "noncausal_reference")

    def test_constants_cannot_replace_all_evidence(self):
        result = execute([{"op": "add", "left": op("1", "CONST"), "right": op("1", "CONST")}], {})
        self.assertEqual(result["issues"][0]["code"], "no_source_dependency")

    def test_numeric_units_and_accounting_negatives(self):
        values = numeric_tokens("revenue $1,200; loss (300); margin 5.0%; prior 50")
        self.assertIn(1200, values)
        self.assertIn(-300, values)
        self.assertIn(5, values)
        self.assertNotIn(0.05, values)

    def test_decimal_before_sentence_period_is_not_lost(self):
        from decimal import Decimal
        self.assertIn(Decimal("120.5"), numeric_tokens("The profit was 120.5."))


if __name__ == "__main__":
    unittest.main()
