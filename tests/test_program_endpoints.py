from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from program_endpoints import endpoint_candidates, select_endpoint, choose_endpoint


def operand(value, span="S"):
    return {"value": value, "span_id": span}


class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {"S": "payment volume 637; transactions 5; cards 86"}
        self.answer = {"decision": "ANSWER", "answer_unit": "number", "steps": [
            {"op": "divide", "left": operand("637"), "right": operand("5")},
            {"op": "multiply", "left": operand("#0", "STEP#0"), "right": operand("86")}]}

    def test_natural_trailing_error_has_preserved_prefix_candidate(self):
        original = deepcopy(self.answer)
        candidates = endpoint_candidates(self.answer, self.evidence)
        self.assertEqual([c["id"] for c in candidates], ["KEEP", "P001"])
        self.assertEqual(candidates[1]["execution"]["value"], "127.4")
        fixed, accepted = select_endpoint(self.answer, candidates, "P001")
        self.assertTrue(accepted)
        self.assertEqual(fixed, {**self.answer, "steps": self.answer["steps"][:1]})
        self.assertEqual(self.answer, original)

    def test_keep_and_unknown_selection_do_not_edit(self):
        candidates = endpoint_candidates(self.answer, self.evidence)
        for selected in ("KEEP", "UNKNOWN", None):
            fixed, accepted = select_endpoint(self.answer, candidates, selected)
            self.assertEqual(fixed, self.answer)
            self.assertFalse(accepted)

    def test_tampered_units_or_retained_operands_are_rejected(self):
        for field in ("unit", "operand"):
            candidates = endpoint_candidates(self.answer, self.evidence)
            if field == "unit":
                candidates[1]["answer"]["answer_unit"] = "percent"
            else:
                candidates[1]["answer"]["steps"][0]["right"] = operand("86")
            with self.assertRaisesRegex(ValueError, "retained computation or units"):
                select_endpoint(self.answer, candidates, "P001")

    def test_equal_numbers_with_different_sources_are_not_collapsed(self):
        answer = {"decision": "ANSWER", "answer_unit": "number", "steps": [
            {"op": "add", "left": operand("2", "S1"), "right": operand("0", "CONST")},
            {"op": "add", "left": operand("2", "S2"), "right": operand("0", "CONST")}]}
        candidates = endpoint_candidates(answer, {"S1": "cash 2", "S2": "debt 2"})
        self.assertEqual(len(candidates), 2)
        self.assertNotEqual(candidates[0]["execution"]["nodes"][-1]["source_spans"], candidates[1]["execution"]["nodes"][-1]["source_spans"])

    def test_single_step_leaves_keep_and_invalid_program_has_no_candidates(self):
        answer = {**self.answer, "steps": self.answer["steps"][:1]}
        self.assertEqual([c["id"] for c in endpoint_candidates(answer, self.evidence)], ["KEEP"])
        self.assertEqual(endpoint_candidates(self.answer, {}), [])
        self.assertEqual(endpoint_candidates({**self.answer, "decision": "INSUFFICIENT"}, self.evidence), [])

    def test_model_choice_can_only_select_an_enumerated_prefix(self):
        calls = []
        def choose(prompt, schema):
            calls.append((prompt, schema))
            return {"candidate_id": "P001"}
        result, trace = choose_endpoint(self.answer, self.evidence, "average payment volume per transaction?", choose)
        self.assertEqual(result["steps"], self.answer["steps"][:1])
        self.assertTrue(trace["accepted"])
        self.assertFalse(trace["gold_used"])
        self.assertEqual(calls[0][1]["properties"]["candidate_id"]["enum"], ["KEEP", "P001"])

    def test_no_alternative_does_not_invoke_a_model(self):
        def forbidden(*args):
            self.fail("A one-step program should not call a selector")
        answer = {**self.answer, "steps": self.answer["steps"][:1]}
        result, trace = choose_endpoint(answer, self.evidence, "question", forbidden)
        self.assertEqual(result, answer)
        self.assertFalse(trace["attempted"])

    def test_malformed_choice_preserves_original_program(self):
        for response in (None, {}, {"candidate_id": "P999"}):
            result, trace = choose_endpoint(self.answer, self.evidence, "question", lambda *args: response)
            self.assertEqual(result, self.answer)
            self.assertFalse(trace["accepted"])


if __name__ == "__main__":
    unittest.main()
