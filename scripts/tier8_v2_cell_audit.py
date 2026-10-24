"""Audit exact table-cell identities without changing any running experiment."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from evidence_cells import cell_catalog, compile_cells
from tier8_v2_demo_retrieval import BANK
from tier8_v2_finqa import packet
from tier8_v2_sequence import inside, require_complete


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collisions(view):
    groups = defaultdict(list)
    for key, atom in view["catalog"].items():
        groups[(atom["span_id"], atom["value"])].append(key)
    return [{"span_id": span, "value": value, "quantity_ids": refs,
             "cell_ids": sorted({view["catalog"][ref]["cell_id"] for ref in refs})}
            for (span, value), refs in groups.items()
            if len({view["catalog"][ref]["cell_id"] for ref in refs}) > 1]


def main():
    base = inside("research/tier8_v2")
    source = base / "external/finqa/dataset-dev.json"
    dev = {r["id"]: r for r in json.loads(source.read_text())}
    paths = [base / "data" / name for name in
             ("finqa-development-public.jsonl", "finqa-development-table-complete.jsonl")]
    views, summaries, records = {}, [], []
    for path in paths:
        packets = [json.loads(line) for line in path.read_text().splitlines()]
        for public in packets:
            view = cell_catalog(public["evidence"], dev[public["id"]]["table"])
            views[(sha(path), public["id"])] = view
            records.append({"packet_file": path.name, "id": public["id"],
                            "collisions": collisions(view), "view": view})
        selected = [r for r in records if r["packet_file"] == path.name]
        summaries.append({"packet_file": path.name, "packet_sha256": sha(path), "n": len(packets),
                          "cases_with_same_row_value_in_distinct_cells": sum(bool(r["collisions"]) for r in selected),
                          "collision_groups": sum(len(r["collisions"]) for r in selected)})
    run_checks = []
    for name in ("finqa-sas-analysis-dev24-01", "finqa-sas-table-analysis-dev24-01",
                 "finqa-mas-analysis-dev24-01", "finqa-mas-3b-analysis-dev24-01"):
        run = base / "runs" / name
        require_complete(str(run))
        manifest = json.loads((run / "manifest.json").read_text())
        if manifest["evaluation_source_sha256"] != sha(source):
            raise ValueError("Evaluation source differs")
        checked, traces = 0, []
        for line in (run / "cases.jsonl").read_text().splitlines():
            r = json.loads(line)
            if r["execution"]["issues"]:
                continue
            view = views[(manifest["data_sha256"], r["case_id"])]
            result = compile_cells(r["plan"], view)
            if result["execution"]["issues"] or result["execution"]["value"] != r["execution"]["value"]:
                raise ValueError("Cell support changes executable answer")
            checked += 1
            traces.append({"case_id": r["case_id"], "bindings": result["bindings"]})
        run_checks.append({"run": name, "executable_programs_checked": checked,
                           "case_sha256": sha(run / "cases.jsonl"), "bindings": traces})
    bank_path, train_path = inside(BANK), inside(".local/datasets/finqa/train.json")
    bank = json.loads(bank_path.read_text())
    if sha(train_path) != bank["source_sha256"]:
        raise ValueError("Training source differs")
    train = {r["id"]: r for r in json.loads(train_path.read_text())}
    training = []
    for example in bank["examples"]:
        r = train[example["source_id"]]
        public = packet(r)
        view = cell_catalog(public["evidence"], r["table"])
        result = compile_cells(example["target"], view)
        if result["execution"] is None or result["execution"]["issues"]:
            raise ValueError("Training target loses cell-level support")
        training.append({"id": r["id"], "collisions": collisions(view)})
    report = {"purpose": "Cell-level support/identity validation only; no semantic correctness, repair gain or novelty claim.",
              "source_sha256": sha(source), "code_sha256": {name: sha(inside("scripts/" + name)) for name in
                  (Path(__file__).name, "evidence_cells.py", "evidence_atoms.py", "evidence_calculator.py")},
              "packets": summaries, "completed_run_checks": run_checks,
              "training": {"bank_sha256": sha(bank_path), "source_sha256": sha(train_path), "n": len(training),
                           "cases_with_same_row_value_in_distinct_cells": sum(bool(r["collisions"]) for r in training),
                           "cases": [r for r in training if r["collisions"]]},
              "cases": records, "running_inputs_modified": False, "test_split_opened": False}
    output = base / "evidence/source-cell-identity-audit.json"
    if output.exists():
        raise ValueError("Use a new audit output; do not overwrite evidence")
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"packets": summaries,
        "executable_programs_checked": sum(r["executable_programs_checked"] for r in run_checks),
        "training_targets_checked": len(training),
        "training_collision_cases": report["training"]["cases_with_same_row_value_in_distinct_cells"]}, indent=2))


if __name__ == "__main__":
    main()
