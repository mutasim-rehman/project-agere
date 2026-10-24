"""Prepare train-only, numerically unambiguous source-binding targets.

This is structured adaptation data, not tokenizer-fitted SFT messages. Exact
deployment prompt capture, training and adapter application remain separate work.
No first-match binding is emitted when a gold numeric operand has multiple cells.
"""
from collections import Counter
from decimal import InvalidOperation
import hashlib
import json

from evidence_atoms import atom_catalog, compile_plan
from evidence_cells import cell_catalog, compile_cells
from program_binding_domains import binding_domains
from tier8_v2_demo_retrieval import BANK, report_group
from tier8_v2_demos import target_plan
from tier8_v2_financial_pipeline import question_units
from tier8_v2_finqa import packet
from tier8_v2_sequence import inside
from evidence_calculator import execute


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def adaptation_split(source_id):
    group = report_group(source_id)
    return "validation" if int(hashlib.sha256(("agere-adapt-42:" + group).encode()).hexdigest(), 16) % 10 == 0 else "train"


def prepare(row):
    public = packet(row)
    # A-IDs follow evidence iteration order. Canonicalize BEFORE labelling so
    # JSON sort_keys and reloading cannot silently reassign source identities.
    public["evidence"] = dict(sorted(public["evidence"].items()))
    atoms = atom_catalog(public["evidence"])
    target = target_plan(row, public, atoms)
    partial = binding_domains(row["qa"]["program"], atoms)
    if not partial["numeric_binding_unique"]:
        raise ValueError("ambiguous_source_identity")
    if target["steps"] != partial["resolved_steps"]:
        raise ValueError("unique_target_inconsistent")
    if target["answer_unit"] not in question_units(public["question"], "question"):
        raise ValueError("target_unit_outside_deployment_grammar")
    view = cell_catalog(public["evidence"], row["table"])
    result = compile_cells(target, view)
    if result["execution"] is None or result["execution"]["issues"]:
        raise ValueError("cell_support_failure")
    return {"source_id": row["id"], "report_group": report_group(row["id"]),
            "split": adaptation_split(row["id"]), "public": public,
            "cell_view": view, "target": target, "bindings": result["bindings"],
            "quality_scope": "Unique numeric-to-source mapping plus checked gold arithmetic/units; not independently adjudicated semantic labels."}


def validate_prepared(row):
    atoms = atom_catalog(row["public"]["evidence"])
    saved = row["cell_view"]["catalog"]
    if set(atoms) != set(saved) or any(atoms[key][field] != saved[key][field]
            for key in atoms for field in ("value", "span_id", "context")):
        raise ValueError("Persisted quantity IDs differ from source catalog")
    cell = compile_cells(row["target"], row["cell_view"])
    compiled = compile_plan(row["target"], atoms)
    execution = execute(compiled["steps"], row["public"]["evidence"])
    if execution["issues"] or cell["execution"]["issues"] or execution["value"] != cell["execution"]["value"]:
        raise ValueError("Persisted target loses source consistency")
    if cell["bindings"] != row["bindings"]:
        raise ValueError("Persisted source bindings differ")


def main():
    source, bank_path = inside(".local/datasets/finqa/train.json"), inside(BANK)
    bank = json.loads(bank_path.read_text())
    if sha(source) != bank["source_sha256"]:
        raise ValueError("Pinned training source changed")
    excluded = set(bank["excluded_report_groups"])
    root = inside("research/tier8_v2")
    outputs = {split: root / "data" / f"finqa-cell-adaptation-{split}-02.jsonl" for split in ("train", "validation")}
    audit_path = root / "evidence/cell-adaptation-data-02.json"
    if audit_path.exists() or any(p.exists() for p in outputs.values()):
        raise ValueError("Refusing to overwrite adaptation data")
    rows = json.loads(source.read_text())
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate training source IDs")
    examples, skipped, skipped_ids = [], Counter(), []
    for row in sorted(rows, key=lambda r: r["id"]):
        if report_group(row["id"]) in excluded:
            skipped["development_report_overlap"] += 1
            continue
        try:
            examples.append(prepare(row))
        except (ValueError, InvalidOperation) as exc:
            reason = str(exc)
            skipped[reason] += 1
            skipped_ids.append({"id": row["id"], "reason": reason})
    groups = {split: {r["report_group"] for r in examples if r["split"] == split} for split in outputs}
    if not examples or not all(groups.values()) or groups["train"] & groups["validation"] or set.union(*groups.values()) & excluded:
        raise ValueError("Empty or leaking adaptation split")
    for split, path in outputs.items():
        with path.open("x") as stream:
            for row in examples:
                if row["split"] == split:
                    stream.write(json.dumps(row, sort_keys=True) + "\n")
        for line in path.read_text().splitlines():
            validate_prepared(json.loads(line))
    report = {"source_sha256": sha(source), "bank_sha256": sha(bank_path),
              "code_sha256": {name: sha(inside("scripts/" + name)) for name in
                  ("tier8_v2_adaptation_data.py", "evidence_cells.py", "program_binding_domains.py",
                   "tier8_v2_demos.py", "tier8_v2_finqa.py", "evidence_atoms.py", "evidence_calculator.py")},
              "source_n": len(rows), "eligible_n": len(examples), "skipped": dict(skipped), "skipped_ids": skipped_ids,
              "split_policy": "SHA256 agere-adapt-42:report-group modulo 10 == 0 validation; otherwise train",
              "splits": {split: {"n": sum(r["split"] == split for r in examples), "report_groups": len(groups[split]),
                                  "file": str(path.relative_to(inside("."))), "sha256": sha(path)} for split, path in outputs.items()},
              "excluded_development_report_groups": sorted(excluded), "development_answers_used": False,
              "test_opened": False, "tokenizer_fitted": False, "model_trained": False,
              "serialization_policy": "Evidence keys sorted before target construction; every persisted row reloaded and source/target bindings revalidated.",
              "supersedes": "cell-adaptation-data-01.json (invalid persisted A-ID mappings; never used for training)",
              "limitations": ["Numeric uniqueness is not semantic adjudication.",
                  "Eligibility biases toward available, <=4-operation source-grounded programs; no 1800-character demo cap.",
                  "Bare percentage-point annotation issues are not resolved by this export.",
                  "Capture exact deployment prompts and fit tokenized examples before training; measure applied adapters."]}
    audit_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("skipped_ids", "excluded_development_report_groups")}, indent=2))


if __name__ == "__main__":
    main()
