from copy import deepcopy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from program_graph import audit_graph, prune_unused, edge_candidates
from evidence_atoms import compile_plan
from evidence_calculator import execute
from tier8_v2_graph_audit import completed_records


class GraphTests(unittest.TestCase):
    def test_unused_intermediate_is_identified_without_gold(self):
        steps = [{"op": "add", "left": "A000", "right": "A001"},
                 {"op": "divide", "left": "#0", "right": "CONST:100"},
                 {"op": "multiply", "left": "#0", "right": "CONST:100"}]
        self.assertEqual(audit_graph(steps)["unused_steps"], [1])

    def test_pruning_renumbers_references_and_preserves_value(self):
        atoms = {"A000": {"value": "10", "span_id": "S"}, "A001": {"value": "2", "span_id": "S"}}
        evidence = {"S": "values 10 and 2"}
        plan = {"decision": "ANSWER", "answer_unit": "number", "steps": [
            {"op": "multiply", "left": "A000", "right": "A001"},
            {"op": "subtract", "left": "A000", "right": "A001"},
            {"op": "divide", "left": "#1", "right": "A001"}]}
        before = deepcopy(plan)
        fixed = prune_unused(plan)
        self.assertEqual(fixed["steps"][-1]["left"], "#0")
        self.assertEqual(plan, before)
        for p in (plan, fixed):
            self.assertEqual(execute(compile_plan(p, atoms)["steps"], evidence)["value"], "4")

    def test_valid_branching_uses_both_parents(self):
        steps = [{"op": "add", "left": "A", "right": "B"},
                 {"op": "add", "left": "C", "right": "D"},
                 {"op": "divide", "left": "#0", "right": "#1"}]
        self.assertEqual(audit_graph(steps)["unused_steps"], [])

    def test_future_edge_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Noncausal"):
            audit_graph([{"left": "#0", "right": "A"}])

    def test_edge_candidates_preserve_operations_and_other_operands(self):
        def quantity(value):
            return {"value": value, "span_id": "S"}
        def ref(index):
            return {"value": f"#{index}", "span_id": f"STEP#{index}"}
        answer = {"decision": "ANSWER", "answer_unit": "percent", "steps": [
            {"op": "subtract", "left": quantity("193.5"), "right": quantity("100")},
            {"op": "divide", "left": ref(0), "right": quantity("100")},
            {"op": "multiply", "left": ref(0), "right": quantity("100")}]}
        before = deepcopy(answer)
        candidates = edge_candidates(answer, {"S": "193.5 and 100"})
        self.assertEqual(candidates[0]["id"], "KEEP")
        self.assertTrue(any(c["execution"]["value"] == "93.500" for c in candidates))
        for candidate in candidates[1:]:
            edit = candidate["edit"]
            self.assertEqual(candidate["answer"]["answer_unit"], answer["answer_unit"])
            changes = 0
            for i, step in enumerate(candidate["answer"]["steps"]):
                self.assertEqual(step["op"], answer["steps"][i]["op"])
                for side in ("left", "right"):
                    changes += step[side] != answer["steps"][i][side]
            self.assertEqual(changes, 1)
            self.assertIn(edit["after"]["value"], ("#1",))
        self.assertEqual(answer, before)

    def test_no_dead_steps_leaves_only_keep(self):
        answer = {"steps": [{"op": "add", "left": {"value": "1", "span_id": "S"}, "right": {"value": "2", "span_id": "S"}}]}
        self.assertEqual([c["id"] for c in edge_candidates(answer, {"S": "1 and 2"})], ["KEEP"])

    def test_live_snapshot_ignores_only_incomplete_tail(self):
        self.assertEqual(completed_records('{"id":1}\n{"id":'), [{"id": 1}])
        with self.assertRaises(ValueError):
            completed_records('{broken}\n')
