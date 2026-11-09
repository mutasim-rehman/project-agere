"""Compare original and closed quantity catalogs on frozen evidence."""
import argparse
from collections import Counter
from decimal import InvalidOperation
import hashlib
import importlib.util
import json
from pathlib import Path

from evidence_atoms import atom_catalog
from program_binding_domains import binding_domains
from tier8_v2_finqa import packet
from tier8_windows_pilot import ROOT


def load_prototype():
    path = ROOT / "research/tier8_v2/experiments/source_span_catalog.py"
    spec = importlib.util.spec_from_file_location("source_span_catalog", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.complete_catalog


def audit(path):
    raw = path.read_bytes()
    complete_catalog = load_prototype()
    counts = Counter()
    records = []
    for row in json.loads(raw):
        public = packet(row)
        evidence = public["evidence"]
        original = atom_catalog(evidence)
        expanded = complete_catalog(evidence)
        if any(expanded.get(key) != value for key, value in original.items()):
            raise ValueError("Catalog changed an existing quantity ID")
        statuses = []
        for atoms in (original, expanded):
            try:
                binding_domains(row["qa"]["program"], atoms, row["qa"]["gold_inds"])
                statuses.append("bindable")
            except (ValueError, InvalidOperation) as exc:
                statuses.append(str(exc))
        if statuses[0] == "bindable" and statuses[1] != "bindable":
            raise ValueError("Expanded catalog lost reference support")
        counts["questions"] += 1
        counts["original_bindable"] += statuses[0] == "bindable"
        counts["closed_bindable"] += statuses[1] == "bindable"
        counts["added_quantities"] += len(expanded) - len(original)
        if statuses[0] != "bindable" and statuses[1] == "bindable":
            records.append(dict(case_id=row["id"], previous=statuses[0],
                                added_quantities=len(expanded) - len(original)))
    return dict(source_sha256=hashlib.sha256(raw).hexdigest(), counts=counts, recovered=records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("sources", type=Path, nargs="+")
    args = parser.parse_args()
    result = {path.name: audit(path) for path in args.sources}
    with args.output.open("x", encoding="utf-8") as out:
        json.dump(result, out, indent=2)
        out.write("\n")
    print(json.dumps({name: value["counts"] for name, value in result.items()}, indent=2))
