from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from program_influence import functional_influence


def step(op, left, right):
    return {"op": op, "left": left, "right": right}


class InfluenceTests(unittest.TestCase):
    def audit(self, steps, **kwargs):
        return functional_influence({"steps": steps}, {"A0": {"value": "5"}, "A1": {"value": "5"}}, **kwargs)

    def test_cancelled_divisor_is_value_inactive_but_has_domain_guard(self):
        result = self.audit([step("divide", "A0", "A1"), step("multiply", "#0", "A1")])
        self.assertEqual(result["value_active_sources"], ["A0"])
        self.assertEqual(result["value_inactive_sources"], ["A1"])
        self.assertEqual(result["division_guards"][0]["denominator_sources"], ["A1"])

    def test_stationary_point_is_not_global_independence(self):
        result = self.audit([step("subtract", "A0", "A1"), step("multiply", "#0", "#0")])
        self.assertEqual(result["value_active_sources"], ["A0", "A1"])

    def test_equal_observed_values_remain_distinct_variables(self):
        self.assertEqual(self.audit([step("divide", "A0", "A1")])["value_active_sources"], ["A0", "A1"])

    def test_self_ratio_is_constant_only_on_its_defined_domain(self):
        result = self.audit([step("divide", "A0", "A0")])
        self.assertTrue(result["value_independent_of_all_sources"])
        self.assertEqual(result["division_guards"][0]["denominator_sources"], ["A0"])

    def test_zero_multiplication_removes_numeric_influence(self):
        self.assertEqual(self.audit([step("multiply", "A0", "CONST:0")])["value_inactive_sources"], ["A0"])

    def test_add_subtract_cancellation_is_exact(self):
        result = self.audit([step("add", "A0", "A1"), step("subtract", "#0", "A1")])
        self.assertEqual(result["value_inactive_sources"], ["A1"])

    def test_resource_limit_returns_unknown(self):
        result = self.audit([step("add", "A0", "A1"), step("multiply", "#0", "#0")], max_operations=1)
        self.assertEqual(result["status"], "unknown")

    def test_identically_zero_denominator_is_not_certified(self):
        result = self.audit([step("subtract", "A0", "A0"), step("divide", "A1", "#0")])
        self.assertEqual(result["status"], "unsupported")


if __name__ == "__main__":
    unittest.main()
