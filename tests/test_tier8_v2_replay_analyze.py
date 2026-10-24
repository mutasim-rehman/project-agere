from copy import deepcopy
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tier8_v2_replay_analyze import validate_pair, validate_accounting, main
from tier8_v2_influence_repair import repair_snapshot
from tier8_v2_financial_pipeline import evaluate_financial


class ReplayAnalysisTests(unittest.TestCase):
    def setUp(self):
        base = {"execution_mode": "fixed_output_repair_component", "baseline_cases_sha256": "C", "baseline_manifest_sha256": "M",
                "snapshots_sha256": "S", "data_sha256": "D", "evaluation_source_sha256": "G", "code_sha256": {"source": "H"},
                "baseline_config": {"task": "finqa"}, "models": [{"file": "model", "sha256": "WEIGHT"}]}
        self.manifests = [{**base, "feedback": mode} for mode in ("plain", "proof")]
        row = {"initial_plan": {}, "initial_answer": {}, "initial_execution": {}, "initial_verdict": {}, "baseline_tokens": 100, "eligible": True}
        self.records = [{"R": deepcopy(row)}, {"R": deepcopy(row)}]

    def test_different_baseline_or_checkpoint_is_rejected(self):
        for key, value in (("snapshots_sha256", "OTHER"), ("models", [{"file": "model", "sha256": "OTHER"}])):
            manifests = deepcopy(self.manifests)
            manifests[1][key] = value
            with self.assertRaises(ValueError):
                validate_pair(manifests, self.records)

    def test_unequal_trigger_or_initial_state_is_rejected(self):
        for key, value in (("eligible", False), ("baseline_tokens", 99)):
            records = deepcopy(self.records)
            records[1]["R"][key] = value
            with self.assertRaises(ValueError):
                validate_pair(self.manifests, records)

    def test_conditions_cannot_be_reversed(self):
        with self.assertRaises(ValueError):
            validate_pair(list(reversed(self.manifests)), self.records)

    def test_budget_and_unflagged_preservation_are_checked(self):
        row = {"baseline_tokens": 100, "fresh_tokens": 10, "combined_output_tokens": 110,
               "fresh_stages": [{"generated_tokens": 10}], "eligible": True, "repair_attempted": True,
               "initial_plan": {}, "plan": {"different": True}}
        validate_accounting(row)
        for changed in ({"combined_output_tokens": 109}, {"eligible": False}, {"baseline_tokens": 2040, "combined_output_tokens": 2050}):
            with self.assertRaises(ValueError):
                validate_accounting({**row, **changed})

    def test_full_analysis_recomputes_fixture_scores_and_paired_effect(self):
        root = Path(__file__).resolve().parents[1]
        data_path = root / "research/tier8_v2/data/finqa-development-public.jsonl"
        gold_path = root / "research/tier8_v2/external/finqa/dataset-dev.json"
        baseline_path = root / "research/tier8_v2/runs/finqa-sas-analysis-dev24-01/cases.jsonl"
        case_id = "MRO/2007/page_149.pdf-2"
        base = next(r for r in map(json.loads, baseline_path.read_text().splitlines()) if r["case_id"] == case_id)
        public = next(r for r in map(json.loads, data_path.read_text().splitlines()) if r["id"] == case_id)
        gold = next(r for r in json.loads(gold_path.read_text()) if r["id"] == case_id)
        state = {"plan": base["plan"], "answer": base["answer"], "verdict": base["final_verdict"], "tokens": base["tokens"]}
        current, previous = base["plan"]["steps"][0]["right"], base["plan"]["steps"][0]["left"]
        fixed = {"decision": "ANSWER", "answer_unit": "number", "steps": [
            {"op": "subtract", "left": current, "right": previous}, {"op": "add", "left": "#0", "right": current}]}
        passed = {"checks": {k: "PASS" for k in ("operands", "operations", "units")}, "steps_to_repair": [], "repair_kind": "NONE"}
        class Fake:
            def __init__(self, values):
                self.values = iter(values)
            def call(self, role, prompt, schema, budget, requested, stage):
                budget.charge(10)
                return next(self.values), {"stage": stage, "role": role, "prompt": prompt,
                    "prompt_tokens": 100, "generated_tokens": 10, "seconds": 0.01, "finish_reason": "stop"}
        (root / ".local").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root / ".local", prefix="analysis-fixture-") as temporary:
            paths = []
            for condition in ("plain", "proof"):
                path = Path(temporary) / condition
                path.mkdir()
                values = [{"action": "KEEP"}] if condition == "plain" else [{"action": "REPLACE", "plan": fixed}, passed]
                result = repair_snapshot(public, state, Fake(values), "sas", condition)
                result["baseline_recorded_inference_seconds"] = 1.0
                scored = {"case_id": case_id, "initial_score": evaluate_financial(gold, result["initial_answer"], result["initial_execution"]),
                          "score": evaluate_financial(gold, result["answer"], result["execution"]), "delivered": result["delivered"]}
                (path / "cases.jsonl").write_text(json.dumps(result) + "\n")
                (path / "scored_cases.jsonl").write_text(json.dumps(scored) + "\n")
                (path / "snapshots.jsonl").write_text(json.dumps({"case_id": case_id, "snapshot": state, "baseline_recorded_inference_seconds": 1.0}) + "\n")
                manifest = {**self.manifests[0], "feedback": condition,
                    "data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
                    "evaluation_source_sha256": hashlib.sha256(gold_path.read_bytes()).hexdigest(),
                    "snapshots_sha256": hashlib.sha256((path / "snapshots.jsonl").read_bytes()).hexdigest(),
                    "baseline_config": {"data": str(data_path)}}
                (path / "manifest.json").write_text(json.dumps(manifest))
                (path / "summary.json").write_text(json.dumps({"status": "complete", "exit_code": 0, "n": 1, "expected": 1,
                    "peak_tree_rss_bytes": 50, "cap_bytes": 100, "fresh_wall_seconds": 0.1}))
                paths.append(str(path))
            output = io.StringIO()
            with patch.object(sys, "argv", ["analyze", *paths]), redirect_stdout(output):
                main()
            report = json.loads(output.getvalue())
            self.assertEqual(report["paired_all_cases"]["right_only_correct"], 1)
            self.assertEqual(report["proof"]["fresh_output_tokens"], 20)
            self.assertEqual(report["eligible_ids"], [case_id])


if __name__ == "__main__":
    unittest.main()
