"""Paired fixed-output component analysis with cohort and accounting checks."""
import argparse
import hashlib
import json

from evidence_atoms import atom_catalog, compile_plan
from program_influence import functional_influence
from tier8_v2_analyze import paired
from tier8_v2_financial_pipeline import checked, evaluate_financial
from tier8_v2_sequence import inside, require_complete


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def by_id(rows):
    result = {r["case_id"]: r for r in rows}
    if len(result) != len(rows) or not rows:
        raise ValueError("Require unique nonempty case IDs")
    return result


def validate_pair(manifests, records):
    if [m["feedback"] for m in manifests] != ["plain", "proof"]:
        raise ValueError("Pass plain first, proof second")
    for key in ("baseline_cases_sha256", "baseline_manifest_sha256", "snapshots_sha256", "data_sha256",
                "evaluation_source_sha256", "code_sha256", "baseline_config"):
        if not manifests[0].get(key) or manifests[0][key] != manifests[1].get(key):
            raise ValueError(f"Replay inputs differ: {key}")
    if any(m["execution_mode"] != "fixed_output_repair_component" for m in manifests):
        raise ValueError("Cannot mix component replay with fresh end-to-end runs")
    if {(m["file"], m["sha256"]) for m in manifests[0]["models"]} != {(m["file"], m["sha256"]) for m in manifests[1]["models"]}:
        raise ValueError("Replay checkpoints differ")
    if set(records[0]) != set(records[1]) or not records[0]:
        raise ValueError("Replay case cohorts differ")
    for key in records[0]:
        for field in ("initial_plan", "initial_answer", "initial_execution", "initial_verdict", "baseline_tokens", "eligible"):
            if records[0][key][field] != records[1][key][field]:
                raise ValueError(f"Baseline/trigger differs for {key}: {field}")


def validate_accounting(row):
    fresh = sum(s["generated_tokens"] for s in row["fresh_stages"])
    if fresh != row["fresh_tokens"] or row["combined_output_tokens"] != row["baseline_tokens"] + fresh:
        raise ValueError("Recorded token debit is inconsistent")
    if not 0 <= row["combined_output_tokens"] <= 2048:
        raise ValueError("Case output budget exceeded")
    if not row["eligible"] and (fresh or row["repair_attempted"] or row["plan"] != row["initial_plan"]):
        raise ValueError("Unflagged case changed or consumed repair tokens")


def condition_metrics(raw, scores):
    rows = list(raw.values())
    return {"n": len(rows), "eligible": sum(r["eligible"] for r in rows),
            "correct": sum(r["score"]["case_success"] for r in scores.values()),
            "raw_execution_matches": sum(r["score"]["raw_execution_match"] for r in scores.values()),
            "delivered_correct": sum(r["delivered"] and scores[k]["score"]["case_success"] for k, r in raw.items()),
            "delivered_incorrect": sum(r["delivered"] and not scores[k]["score"]["case_success"] for k, r in raw.items()),
            "withheld": sum(not r["delivered"] for r in rows),
            "gains": sum(not r["initial_score"]["case_success"] and r["score"]["case_success"] for r in scores.values()),
            "regressions": sum(r["initial_score"]["case_success"] and not r["score"]["case_success"] for r in scores.values()),
            "fresh_output_tokens": sum(r["fresh_tokens"] for r in rows),
            "baseline_recorded_output_tokens": sum(r["baseline_tokens"] for r in rows),
            "baseline_recorded_inference_seconds": sum(r["baseline_recorded_inference_seconds"] for r in rows),
            "fresh_prompt_tokens": sum(s["prompt_tokens"] for r in rows for s in r["fresh_stages"]),
            "fresh_inference_seconds": sum(s["seconds"] for r in rows for s in r["fresh_stages"]),
            "fresh_model_calls": sum(len(r["fresh_stages"]) for r in rows),
            "fresh_truncated_stages": sum(s["finish_reason"] == "length" for r in rows for s in r["fresh_stages"]),
            "max_case_combined_output_tokens": max(r["combined_output_tokens"] for r in rows)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plain")
    parser.add_argument("proof")
    args = parser.parse_args()
    manifests, raw, scores, summaries, hashes = [], [], [], [], []
    for name in (args.plain, args.proof):
        path = inside(name)
        summary = require_complete(name)
        manifest = json.loads((path / "manifest.json").read_text())
        records = by_id([json.loads(line) for line in (path / "cases.jsonl").read_text().splitlines()])
        scored = by_id([json.loads(line) for line in (path / "scored_cases.jsonl").read_text().splitlines()])
        snapshots = by_id([json.loads(line) for line in (path / "snapshots.jsonl").read_text().splitlines()])
        if len(records) != summary["expected"] or set(records) != set(scored) or set(records) != set(snapshots):
            raise ValueError("Component record counts/IDs differ")
        if digest(path / "snapshots.jsonl") != manifest["snapshots_sha256"]:
            raise ValueError("Saved snapshots changed")
        packets_file = inside(manifest["baseline_config"]["data"])
        gold_file = inside("research/tier8_v2/external/finqa/dataset-dev.json")
        if digest(packets_file) != manifest["data_sha256"] or digest(gold_file) != manifest["evaluation_source_sha256"]:
            raise ValueError("Saved data/evaluation source changed")
        public = {r["id"]: r for r in map(json.loads, packets_file.read_text().splitlines())}
        gold = {r["id"]: r for r in json.loads(gold_file.read_text())}
        for case_id, row in records.items():
            validate_accounting(row)
            if row["condition"] != manifest["feedback"] or row["execution_mode"] != "fixed_output_repair_component":
                raise ValueError("Saved condition/mode differs from manifest")
            state = snapshots[case_id]["snapshot"]
            if state != {"plan": row["initial_plan"], "answer": row["initial_answer"],
                         "verdict": row["initial_verdict"], "tokens": row["baseline_tokens"]}:
                raise ValueError("Initial state differs from exported snapshot")
            if row["baseline_recorded_inference_seconds"] != snapshots[case_id]["baseline_recorded_inference_seconds"]:
                raise ValueError("Recorded baseline cost differs from exported snapshot")
            if checked(row["answer"], public[case_id]["evidence"]) != row["execution"]:
                raise ValueError("Saved execution differs from source recomputation")
            if checked(row["initial_answer"], public[case_id]["evidence"]) != row["initial_execution"]:
                raise ValueError("Saved baseline execution differs from source recomputation")
            atoms = atom_catalog(public[case_id]["evidence"])
            audit = functional_influence(row["initial_plan"], atoms) if not row["initial_execution"]["issues"] else {"status": "not_executable"}
            if audit != row["influence"] or row["eligible"] != (audit.get("status") == "analyzed" and bool(audit.get("value_inactive_sources"))):
                raise ValueError("Saved trigger differs from recomputed algebraic cohort")
            retries = [s for s in row["fresh_stages"] if s["stage"] == "influence_retry"]
            if len(retries) != int(row["repair_attempted"]):
                raise ValueError("Repair call count differs from attempted flag")
            if retries:
                exposes_proof = "Exact symbolic value-influence diagnostic:" in retries[0]["prompt"]
                if exposes_proof != (manifest["feedback"] == "proof"):
                    raise ValueError("Feedback intervention differs from recorded condition")
            if not row["execution"]["issues"] and compile_plan(row["plan"], atom_catalog(public[case_id]["evidence"])) != row["answer"]:
                raise ValueError("Saved plan does not reproduce its source bindings")
            for score_key, answer, execution in (("initial_score", row["initial_answer"], row["initial_execution"]), ("score", row["answer"], row["execution"])):
                if evaluate_financial(gold[case_id], answer, execution) != scored[case_id][score_key]:
                    raise ValueError("Cached evaluation differs from recomputed score")
            delivered = not row["execution"]["issues"] and isinstance(row["final_verdict"], dict) and row["final_verdict"].get("verdict") == "PASS"
            if row["delivered"] != delivered or row["delivered"] != scored[case_id]["delivered"]:
                raise ValueError("Delivery gate differs from saved result")
        manifests.append(manifest)
        raw.append(records)
        scores.append(scored)
        summaries.append(summary)
        hashes.append({file: digest(path / file) for file in ("manifest.json", "cases.jsonl", "scored_cases.jsonl", "summary.json")})
    validate_pair(manifests, raw)
    eligible = {key for key, row in raw[0].items() if row["eligible"]}
    output = {"execution_mode": "fixed_output_repair_component", "n": len(raw[0]), "eligible_ids": sorted(eligible),
              "analysis_code_sha256": {name: digest(inside("scripts/" + name)) for name in
                  ("tier8_v2_replay_analyze.py", "tier8_v2_analyze.py", "tier8_v2_financial_pipeline.py",
                   "program_influence.py", "evidence_atoms.py", "evidence_calculator.py", "tier8_v2_sequence.py")},
              "paired_all_cases": paired(*scores),
              "paired_eligible_cases": paired(*[{k: r for k, r in rows.items() if k in eligible} for rows in scores]) if eligible else None,
              "plain": condition_metrics(raw[0], scores[0]), "proof": condition_metrics(raw[1], scores[1]),
              "fresh_worker_wall_seconds": [s["fresh_wall_seconds"] for s in summaries],
              "fresh_peak_tree_rss_bytes": [s["peak_tree_rss_bytes"] for s in summaries], "artifact_sha256": hashes,
              "cautions": ["Development replay only; not fresh end-to-end generation or confirmatory evaluation.",
                           "Same trigger/output ceilings; actual prompts, tokens and post-repair verification calls can differ.",
                           "Retained unflagged cases remain in the primary denominator. Eligible-only results are secondary.",
                           "Neither unchanged outputs nor zero discordance establishes statistical equivalence or novelty."]}
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
