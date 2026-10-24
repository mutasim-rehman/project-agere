from copy import deepcopy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_financial_pipeline import checked, evaluate_financial, patch_program, run_financial, verdict, question_units, fit_demonstrations


def operand(value, span):
    return {"value": value, "span_id": span}


class FakeModels:
    def __init__(self, results):
        self.results = iter(results)
        self.prompts = []
    def call(self, role, content, schema, budget, requested, stage):
        self.prompts.append(content)
        budget.charge(10)
        return next(self.results), {"stage": stage, "role": role, "generated_tokens": 10}


class FinancialTests(unittest.TestCase):
    def setUp(self):
        self.public = {"id": "R", "question": "What is the ratio of profit to debt service?",
                       "evidence": {"T1": "profit 200; debt service 100"}, "retrieval": {"gold_used": False}}
        self.answer = {"decision": "ANSWER", "answer_unit": "number", "steps": [{"op": "divide", "left": operand("200", "T1"), "right": operand("100", "T1")}]}
        self.passed = {"checks": {k: "PASS" for k in ("operands", "operations", "units")}, "steps_to_repair": [], "repair_kind": "NONE"}

    def test_deployment_rejects_gold_fields(self):
        with self.assertRaisesRegex(ValueError, "Gold"):
            run_financial({**self.public, "gold": "LEAK"}, FakeModels([]), "sas", "none")

    def test_numeric_scoring_happens_after_generation(self):
        model = FakeModels([self.answer, self.passed])
        result = run_financial(self.public, model, "sas", "none")
        score = evaluate_financial({"qa": {"exe_ans": 2, "answer": "2.00"}}, result["answer"], result["execution"])
        self.assertTrue(score["case_success"])
        self.assertTrue(result["delivered"])
        self.assertNotIn("exe_ans", "".join(model.prompts))

    def test_wrong_units_can_block_arithmetically_correct_program(self):
        review = deepcopy(self.passed)
        review["checks"]["units"] = "FAIL"
        review["repair_kind"] = "REPLAN"
        result = run_financial(self.public, FakeModels([self.answer, review]), "sas", "none")
        self.assertEqual(result["execution"]["value"], "2")
        self.assertFalse(result["delivered"])

    def test_repair_preserves_unrelated_step_and_recomputes_dependents(self):
        answer = deepcopy(self.answer)
        answer["steps"].append({"op": "multiply", "left": operand("#0", "STEP#0"), "right": operand("100", "CONST")})
        replacement = {"op": "subtract", "left": operand("200", "T1"), "right": operand("100", "T1")}
        fixed, accepted = patch_program(answer, {"updates": [{"index": 0, "step": replacement}]}, {0}, self.public["evidence"])
        self.assertTrue(accepted)
        self.assertEqual(fixed["steps"][1], answer["steps"][1])
        self.assertEqual(checked(fixed, self.public["evidence"])["value"], "10000")

    def test_repair_cannot_modify_locked_step(self):
        result, accepted = patch_program(self.answer, {"updates": [{"index": 0, "step": self.answer["steps"][0]}]}, set(), self.public["evidence"])
        self.assertFalse(accepted)
        self.assertEqual(result, self.answer)

    def test_gold_does_not_rescale_prediction(self):
        execution = {"value": "0.02", "issues": []}
        self.assertFalse(evaluate_financial({"qa": {"exe_ans": 2, "answer": "2.00"}}, self.answer, execution)["case_success"])

    def test_explicit_percent_unit_can_match_reported_answer_without_raw_match(self):
        answer = {**self.answer, "answer_unit": "percent"}
        score = evaluate_financial({"qa": {"exe_ans": 0.935, "answer": "93.5%"}}, answer, {"value": "93.5", "issues": []})
        self.assertTrue(score["case_success"])
        self.assertFalse(score["raw_execution_match"])

    def test_reported_and_execution_disagreements_remain_visible(self):
        score = evaluate_financial({"qa": {"exe_ans": 19.2, "answer": "18.6"}}, self.answer, {"value": "18.6", "issues": []})
        self.assertTrue(score["reported_answer_match"])
        self.assertFalse(score["raw_execution_match"])

    def test_incorrect_unit_is_not_rescued_by_gold(self):
        answer = {**self.answer, "answer_unit": "percent"}
        score = evaluate_financial({"qa": {"exe_ans": 0.935, "answer": "93.5%"}}, answer, {"value": "0.935", "issues": []})
        self.assertFalse(score["case_success"])

    def test_integer_percentage_reference_allows_display_rounding(self):
        answer = {**self.answer, "answer_unit": "fraction"}
        score = evaluate_financial({"qa": {"exe_ans": 0.56197, "answer": "56%"}}, answer, {"value": "0.56197", "issues": []})
        self.assertTrue(score["case_success"])

    def test_non_numeric_prediction_is_a_failure_not_an_exception(self):
        score = evaluate_financial({"qa": {"exe_ans": 2, "answer": "2.00"}}, self.answer, {"value": "not_a_number", "issues": []})
        self.assertFalse(score["case_success"])

    def test_contradictory_review_is_rejected(self):
        review = deepcopy(self.passed)
        review["steps_to_repair"] = [0]
        self.assertEqual(verdict(review)["verdict"], "FAIL")

    def test_reference_pipeline_executes_source_choices_without_generated_values(self):
        plan = {"decision": "ANSWER", "answer_unit": "number", "steps": [{"op": "divide", "left": "A000", "right": "A001"}]}
        models = FakeModels([plan, self.passed])
        result = run_financial(self.public, models, "mas", "none", representation="reference", unit_mode="question", selector="none")
        self.assertEqual(result["execution"]["value"], "2")
        self.assertTrue(result["delivered"])
        self.assertEqual(result["active_roles"], ["drafter", "verifier"])
        self.assertEqual(len(models.prompts), 2)

    def test_unit_constraint_comes_from_question_only(self):
        self.assertEqual(question_units("Average payment volume per transaction?", "question"), ("number",))
        self.assertEqual(question_units("What percentage came from Canada?", "question"), ("percent", "fraction"))

    def test_reference_patch_is_followed_by_verification(self):
        plan = {"decision": "ANSWER", "answer_unit": "number", "steps": [{"op": "multiply", "left": "A000", "right": "A001"}]}
        failed = {"checks": {"operands": "PASS", "operations": "FAIL", "units": "PASS"}, "steps_to_repair": [0], "repair_kind": "PATCH"}
        update = {"updates": [{"index": 0, "step": {"op": "divide", "left": "A000", "right": "A001"}}]}
        model = FakeModels([plan, failed, update, self.passed])
        result = run_financial(self.public, model, "sas", "patch", representation="reference")
        self.assertEqual(result["execution"]["value"], "2")
        self.assertTrue(result["repair_accepted"])
        self.assertEqual(result["stages"][-1]["stage"], "verify_program_repair")

    def test_demonstrations_are_omitted_when_output_reserve_would_not_fit(self):
        from types import SimpleNamespace
        model = SimpleNamespace(context=800, count_prompt_tokens=lambda role, text: len(text))
        text, ids = fit_demonstrations("Q", [{"text": "x" * 100, "source_id": "TRAIN"}], model, "sas")
        self.assertEqual(text, "Q")
        self.assertEqual(ids, [])

    def test_training_example_is_identified_and_separate_from_actual_question(self):
        from types import SimpleNamespace
        model = SimpleNamespace(context=4096, count_prompt_tokens=lambda role, text: len(text))
        text, ids = fit_demonstrations("ACTUAL", [{"text": "TRAINING", "source_id": "TRAIN"}], model, "sas")
        self.assertEqual(ids, ["TRAIN"])
        self.assertLess(text.index("TRAINING"), text.index("ACTUAL"))

    def test_analysis_is_an_extra_budgeted_stage_not_gold_input(self):
        models = FakeModels(["Use profit divided by debt service.", self.answer, self.passed])
        result = run_financial(self.public, models, "sas", "none", analysis_tokens=128)
        self.assertEqual([s["stage"] for s in result["stages"]], ["analyze_question", "program", "verify_program"])
        self.assertEqual(result["tokens"], 30)
        self.assertIn("Use profit divided", models.prompts[1])
        self.assertNotIn("Preliminary reasoning", models.prompts[2])


if __name__ == "__main__":
    unittest.main()
