"""Reclaim only two redundant, reproducibly downloadable source GGUF caches.

Retains native runtime files; verifies both forms before removing the originals.
This never touches logs, datasets, active model weights or Git-tracked files.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from tier8_v2_sequence import check_inputs, inside


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", required=True)
    parser.parse_args()
    base = inside("research/tier8_v2")
    audit_path = base / "evidence/reclaimed-source-cache-01.json"
    if audit_path.exists():
        raise ValueError("Cache reclamation already has evidence; do not replay")
    plan = json.loads((base / "data/analysis256-sequence-01.json").read_text())
    check_inputs(plan)
    originals = json.loads((base / "evidence/models.json").read_text())
    native = {r["source_file"]: r for r in json.loads((base / "evidence/native-models.json").read_text())}
    wanted = {f"weights/tier8_v2/qwen2.5-{size}-instruct-fp16.gguf" for size in ("0.5b", "1.5b")}
    sources = [r for r in originals if r["file"] in wanted]
    if {r["file"] for r in sources} != wanted or wanted & set(plan["input_sha256"]):
        raise ValueError("Unexpected source-cache inventory/freeze")
    records = []
    for source in sources:
        retained = native[source["file"]]
        for entry in (source, retained):
            path = inside(entry["file"])
            if path.stat().st_size != entry["bytes"] or sha(path) != entry["sha256"]:
                raise ValueError("Source or retained runtime file integrity differs")
        if retained["source_sha256"] != source["sha256"]:
            raise ValueError("Native conversion provenance differs")
        records.append({"source": source, "retained_native": retained["file"],
                        "retained_native_sha256": retained["sha256"], "removed": False})
    report = {"purpose": "Free disk for separate adaptation runtime; redundant public download caches only",
              "before_free_bytes": shutil.disk_usage(inside(".")).free, "records": records,
              "native_runtime_files_verified_and_retained": True, "script_sha256": sha(Path(__file__))}
    audit_path.write_text(json.dumps(report, indent=2) + "\n")
    for record in records:
        inside(record["source"]["file"]).unlink()
        record["removed"] = True
        audit_path.write_text(json.dumps(report, indent=2) + "\n")
    check_inputs(plan)
    report.update({"after_free_bytes": shutil.disk_usage(inside(".")).free,
                   "bytes_reclaimed": sum(r["source"]["bytes"] for r in records),
                   "all_frozen_inputs_unchanged": True, "status": "complete"})
    audit_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
