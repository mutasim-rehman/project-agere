"""Audit value-only training bindings without modifying model-facing targets."""
import hashlib
import json
import math
from pathlib import Path

from evidence_atoms import atom_catalog
from program_binding_domains import binding_domains
from program_influence import functional_influence
from tier8_v2_demo_retrieval import BANK
from tier8_v2_finqa import packet

ROOT = Path(__file__).resolve().parents[1]


def main():
    train_path = ROOT / ".local/datasets/finqa/train.json"
    bank_path = ROOT / BANK
    bank = json.loads(bank_path.read_text())
    if hashlib.sha256(train_path.read_bytes()).hexdigest() != bank["source_sha256"]:
        raise ValueError("Training source changed")
    train = {row["id"]: row for row in json.loads(train_path.read_text())}
    records = []
    for example in bank["examples"]:
        row = train[example["source_id"]]
        public = packet(row)
        atoms = atom_catalog(public["evidence"])
        partial = binding_domains(row["qa"]["program"], atoms, row["qa"]["gold_inds"])
        if partial["numeric_binding_unique"] and partial["resolved_steps"] != example["target"]["steps"]:
            raise ValueError("Unique mapping differs from the historical target")
        old = functional_influence({"steps": example["sketch"]["steps"]}, example["sketch"]["slots"])
        candidates = {key for slot in partial["slots"].values() for key in slot["candidate_quantity_ids"]}
        records.append({"source_id": example["source_id"], "question": public["question"],
                        "numeric_binding_unique": partial["numeric_binding_unique"],
                        "numeric_assignment_upper_bound": str(math.prod(len(s["candidate_quantity_ids"]) for s in partial["slots"].values())),
                        "legacy_cancelled_sources": old.get("value_inactive_sources", []),
                        "partial": partial,
                        "candidate_contexts": {key: atoms[key] for key in sorted(candidates)}})
    output = {"training_bank_sha256": hashlib.sha256(bank_path.read_bytes()).hexdigest(),
              "training_source_sha256": bank["source_sha256"], "n": len(records),
              "numeric_unique_examples": sum(r["numeric_binding_unique"] for r in records),
              "numeric_ambiguous_examples": sum(not r["numeric_binding_unique"] for r in records),
              "legacy_cancelled_and_ambiguous": sum(bool(r["legacy_cancelled_sources"]) and not r["numeric_binding_unique"] for r in records),
              "caution": "Numeric compatibility/identity only, not semantic correctness. Annotation hints do not narrow domains. No model-facing bank was replaced and no development/test labels were read.",
              "examples": records}
    (ROOT / "research/tier8_v2/evidence/training-binding-audit.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k: v for k, v in output.items() if k != "examples"}, indent=2))


if __name__ == "__main__":
    main()
