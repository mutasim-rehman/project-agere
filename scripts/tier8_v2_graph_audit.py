"""Audit saved development programs; generation/repair never receives gold."""
import json
from pathlib import Path

from program_graph import audit_graph, prune_unused, edge_candidates
from evidence_calculator import execute
from tier8_v2_financial_pipeline import evaluate_financial

ROOT = Path(__file__).resolve().parents[1]


def completed_records(text):
    # A live writer may be midway through its final JSONL record. Ignore only
    # that unfinished tail; malformed completed records remain hard failures.
    complete = text[:text.rfind("\n") + 1]
    return [json.loads(line) for line in complete.splitlines() if line]


def main():
    public = {r["id"]: r for r in map(json.loads, (ROOT / "research/tier8_v2/data/finqa-development-public.jsonl").read_text().splitlines())}
    gold = {r["id"]: r for r in json.loads((ROOT / "research/tier8_v2/external/finqa/dataset-dev.json").read_text())}
    reports = []
    for name in ("finqa-mas-demos-dev24-01", "finqa-sas-demos-dev24-01"):
        path = ROOT / "research/tier8_v2/runs" / name
        rows = completed_records((path / "cases.jsonl").read_text())
        audited = []
        for row in rows:
            if row["execution"]["issues"]:
                continue
            answer = row["answer"]
            graph = audit_graph(answer["steps"])
            pruned = prune_unused(answer)
            value = execute(pruned["steps"], public[row["case_id"]]["evidence"])["value"]
            if value != row["execution"]["value"]:
                raise ValueError("Pruning changed an executed result")
            candidates = edge_candidates(answer, public[row["case_id"]]["evidence"])
            oracle = [c["id"] for c in candidates if evaluate_financial(gold[row["case_id"]], c["answer"], c["execution"])["case_success"]]
            audited.append({"id": row["case_id"], **graph, "case_correct": row["score"]["case_success"],
                            "pruning_value_preserved": True, "candidate_count": len(candidates),
                            "oracle_correct_candidate_ids": oracle,
                            "oracle_potential_gain": not row["score"]["case_success"] and bool(oracle),
                            "candidates": [{"id": c["id"], "value": c["execution"]["value"], "edit": c["edit"]} for c in candidates]})
        summary = json.loads((path / "summary.json").read_text()) if (path / "summary.json").exists() else {}
        reports.append({"run": name, "complete": summary.get("status") == "complete", "run_status": summary.get("status", "live_snapshot"), "cases_observed": len(rows),
                        "executable_programs": len(audited),
                        "programs_with_unused_steps": sum(bool(a["unused_steps"]) for a in audited),
                        "correct_programs_with_unused_steps": sum(a["case_correct"] and bool(a["unused_steps"]) for a in audited),
                        "oracle_reconnection_potential_gains": sum(a["oracle_potential_gain"] for a in audited),
                        "oracle_caution": "Candidate coverage only, not a model-selected repair gain; gold used after candidate enumeration.",
                        "audit": audited})
    output = {"scope": "Development diagnostics; incomplete runs are snapshots, not final counts", "runs": reports}
    (ROOT / "research/tier8_v2/evidence/program-graph-audit.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps([{k: v for k, v in r.items() if k != "audit"} for r in reports], indent=2))


if __name__ == "__main__":
    main()
