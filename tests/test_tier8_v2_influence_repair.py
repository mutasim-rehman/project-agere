from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evidence_atoms import atom_catalog, compile_plan
from tier8_v2_influence_repair import repair_snapshot


class FakeModels:
    def __init__(self, values):
        self.values = iter(values)
        self.prompts = []
    def call(self, role, prompt, schema, budget, requested, stage):
        self.prompts.append(prompt)
        budget.charge(10)
        return next(self.values), {"stage": stage, "role": role, "generated_tokens": 10}


class InfluenceRepairTests(unittest.TestCase):
    def setUp(self):
        self.public = {"id": "R", "question": "What is projected cost if the same increase repeats?",
                       "evidence": {"S": "current cost 1654; previous cost 1251"}}
        self.plan = {"decision": "ANSWER", "answer_unit": "number", "steps": [
            {"op": "divide", "left": "A001", "right": "A000"},
            {"op": "multiply", "left": "#0", "right": "A000"}]}
        self.passed = {"checks": {k: "PASS" for k in ("operands", "operations", "units")}, "steps_to_repair": [], "repair_kind": "NONE", "verdict": "PASS"}
        self.snapshot = {"plan": self.plan, "answer": compile_plan(self.plan, atom_catalog(self.public["evidence"])), "verdict": self.passed, "tokens": 200}
        self.fixed = {"decision": "ANSWER", "answer_unit": "number", "steps": [
            {"op": "subtract", "left": "A000", "right": "A001"},
            {"op": "add", "left": "#0", "right": "A000"}]}

    def test_proof_and_plain_share_trigger_but_only_proof_exposes_audit(self):
        for condition in ("plain", "proof"):
            model = FakeModels([{"action": "KEEP"}])
            result = repair_snapshot(self.public, self.snapshot, model, "sas", condition)
            self.assertTrue(result["eligible"])
            self.assertEqual("Exact symbolic" in model.prompts[0], condition == "proof")
            self.assertEqual(result["fresh_tokens"], 10)

    def test_replacement_reexecutes_and_reverifies_with_baseline_budget_debited(self):
        result = repair_snapshot(self.public, self.snapshot, FakeModels([{"action": "REPLACE", "plan": self.fixed}, self.passed]), "sas", "proof")
        self.assertEqual(result["execution"]["value"], "2057")
        self.assertTrue(result["repair_accepted"])
        self.assertTrue(result["delivered"])
        self.assertEqual(result["combined_output_tokens"], 220)
        self.assertEqual(result["fresh_stages"][-1]["stage"], "verify_influence_retry")

    def test_invalid_new_reference_preserves_snapshot(self):
        bad = deepcopy(self.fixed)
        bad["steps"][0]["left"] = "A999"
        result = repair_snapshot(self.public, self.snapshot, FakeModels([{"action": "REPLACE", "plan": bad}]), "sas", "proof")
        self.assertEqual(result["plan"], self.plan)
        self.assertFalse(result["repair_accepted"])

    def test_zero_remaining_budget_does_not_call_model(self):
        result = repair_snapshot(self.public, {**self.snapshot, "tokens": 2048}, FakeModels([]), "sas", "proof")
        self.assertTrue(result["eligible"])
        self.assertFalse(result["repair_attempted"])
        self.assertEqual(result["combined_output_tokens"], 2048)

    def test_target_fields_never_enter_repair(self):
        with self.assertRaises(ValueError):
            repair_snapshot({**self.public, "gold": "SECRET"}, self.snapshot, FakeModels([]), "sas", "proof")
        with self.assertRaises(ValueError):
            repair_snapshot(self.public, {**self.snapshot, "score": "SECRET"}, FakeModels([]), "sas", "proof")

    def test_legitimate_cancellation_can_keep_original(self):
        plan = {"decision": "ANSWER", "answer_unit": "number", "steps": [{"op": "subtract", "left": "A000", "right": "A000"}]}
        state = {**self.snapshot, "plan": plan, "answer": compile_plan(plan, atom_catalog(self.public["evidence"]))}
        result = repair_snapshot(self.public, state, FakeModels([{"action": "KEEP"}]), "sas", "proof")
        self.assertEqual(result["execution"]["value"], "0")
        self.assertFalse(result["repair_accepted"])

    def test_non_canceling_program_does_not_call_model(self):
        plan = {"decision": "ANSWER", "answer_unit": "number", "steps": [{"op": "subtract", "left": "A000", "right": "A001"}]}
        state = {**self.snapshot, "plan": plan, "answer": compile_plan(plan, atom_catalog(self.public["evidence"]))}
        result = repair_snapshot(self.public, state, FakeModels([]), "sas", "proof")
        self.assertFalse(result["eligible"])
        self.assertEqual(result["fresh_tokens"], 0)

    def test_replacement_still_requires_post_verifier_pass(self):
        failed = {**self.passed, "checks": {k: "FAIL" for k in ("operands", "operations", "units")}, "repair_kind": "REPLAN"}
        result = repair_snapshot(self.public, self.snapshot, FakeModels([{"action": "REPLACE", "plan": self.fixed}, failed]), "sas", "proof")
        self.assertTrue(result["repair_accepted"])
        self.assertFalse(result["delivered"])


if __name__ == "__main__":
    unittest.main()
