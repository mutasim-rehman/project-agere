"""Validate a fully trained, converted adapter before CPU inference loads it."""
import hashlib
import json
from pathlib import Path

from tier8_v2_adapter_convert import validate_adapter

ROOT = Path(__file__).resolve().parents[1]


def inside(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Adapter path outside repository")
    return path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_adapter(directory, arm, drafter_model):
    role = "sas" if arm == "sas" else "drafter"
    expected = "7b" if arm == "sas" else "3b"
    if arm not in ("sas", "mas") or (arm == "mas" and drafter_model != "3b-q4"):
        raise ValueError("Adapter profile requires SAS 7B or MAS 3B Q4 drafter")
    converted = inside(directory) / "manifest.json"
    info = json.loads(converted.read_text())
    if info["status"] != "complete" or info["training_mode"] != "train" or info["diagnostic_only"]:
        raise ValueError("Require full trained adapter; fit diagnostics are not QA systems")
    if info["profile"] != expected or info["tensor_count"] <= 0:
        raise ValueError("Adapter checkpoint profile differs")
    for name, expected_sha in info["input_sha256"].items():
        if sha(inside(name)) != expected_sha:
            raise ValueError("Converted adapter provenance changed")
    run = inside(info["run"])
    training, summary, _ = validate_adapter(run)
    if training["mode"] != "train" or training["profile"] != expected:
        raise ValueError("Adapter training provenance/profile differs")
    for name in ("manifest.json", "summary.json"):
        relative = str((run / name).relative_to(ROOT))
        if info["input_sha256"].get(relative) != sha(run / name):
            raise ValueError("Conversion does not bind this training run")
    path = inside(info["file"])
    if path.stat().st_size != info["bytes"] or sha(path) != info["sha256"]:
        raise ValueError("Converted adapter file integrity differs")
    return {"role": role, "profile": expected, "file": str(path.relative_to(ROOT)),
            "sha256": info["sha256"], "scale": 1.0, "training_run": str(run.relative_to(ROOT)),
            "conversion_manifest": str(converted.relative_to(ROOT)), "conversion_manifest_sha256": sha(converted),
            "optimizer_updates": summary["optimizer_updates"]}
