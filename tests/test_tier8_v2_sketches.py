from copy import deepcopy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evidence_atoms import atom_catalog
from tier8_v2_sketches import make_sketch, instantiate_choice, choice_schema
from tier8_v2_financial_pipeline import run_financial


class FakeModels:
    context = 4096
    def __init__(self, answers):
        self.answers = iter(answers)
        self.prompts = []
    def count_prompt_tokens(self, role, content):
        return len(content) // 4
    def call(self, role, content, schema, budget, requested, stage):
        self.prompts.append(content)
        budget.charge(10)
        return next(self.answers), {"stage": stage, "role": role, "generated_tokens": 10}


class SketchTests(unittest.TestCase):
    def setUp(self):
        self.atoms = atom_catalog({"T": "ending index 193.5 and starting index 100"})
        self.target = {"decision": "ANSWER", "answer_unit": "fraction", "steps": [
            {"op": "subtract", "left": "A000", "right": "A001"},
            {"op": "divide", "left": "#0", "right": "A001"}]}
        self.example = {"source_id": "TRAIN/2014/p.pdf-1", "question": "percentage cumulative return?",
                        "sketch": make_sketch(self.target, self.atoms)}

    def test_sketch_retains_repeated_variables_and_dependencies(self):
        sketch = self.example["sketch"]
        self.assertEqual(list(sketch["slots"]), ["V0", "V1"])
        self.assertEqual(sketch["steps"][1], {"op": "divide", "left": "#0", "right": "V1"})
        before = deepcopy(self.example)
        bound = instantiate_choice({"sketch_id": "T0", "bindings": {"V0": "A001", "V1": "A000"}}, [self.example], self.atoms)
        self.assertEqual(bound["steps"][0], {"op": "subtract", "left": "A001", "right": "A000"})
        self.assertEqual(self.example, before)

    def test_constants_are_not_bindable_variables(self):
        target = deepcopy(self.target)
        target["steps"].append({"op": "multiply", "left": "#1", "right": "CONST:100"})
        self.assertEqual(make_sketch(target, self.atoms)["steps"][-1]["right"], "CONST:100")

    def test_binding_cannot_insert_literals_or_dependencies(self):
        for bad in ("100", "#0", "CONST:100", "A999"):
            result = instantiate_choice({"sketch_id": "T0", "bindings": {"V0": "A000", "V1": bad}}, [self.example], self.atoms)
            self.assertEqual(result["decision"], "INSUFFICIENT")

    def test_missing_or_extra_bindings_rejected(self):
        for binding in ({"V0": "A000"}, {"V0": "A000", "V1": "A001", "V2": "A000"}):
            self.assertEqual(instantiate_choice({"sketch_id": "T0", "bindings": binding}, [self.example], self.atoms)["decision"], "INSUFFICIENT")
        self.assertEqual(len(choice_schema([self.example], {})["oneOf"]), 1)

    def test_pipeline_executes_bound_sketch_then_verifies(self):
        public = {"id": "DEV", "question": "what was the percentage cumulative return?",
                  "evidence": {"T": "ending index 150 and starting index 100"}, "retrieval": {"gold_used": False}}
        verdict = {"checks": {k: "PASS" for k in ("operands", "operations", "units")}, "steps_to_repair": [], "repair_kind": "NONE"}
        model = FakeModels([{"sketch_id": "T0", "bindings": {"V0": "A000", "V1": "A001"}}, verdict])
        result = run_financial(public, model, "mas", "none", representation="reference", selector="none", planner="sketch", demonstrations=[self.example])
        self.assertEqual(result["execution"]["value"], "0.5")
        self.assertEqual([s["stage"] for s in result["stages"]], ["bind_sketch", "verify_program"])
        self.assertTrue(result["delivered"])
        self.assertEqual(result["demonstrations_used"], [self.example["source_id"]])


if __name__ == "__main__":
    unittest.main()
