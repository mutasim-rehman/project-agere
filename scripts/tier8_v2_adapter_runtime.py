"""Validate a fully trained, converted adapter before CPU inference loads it."""
import hashlib
import json
import math
from pathlib import Path

from tier8_v2_adapter_convert import validate_adapter

ROOT = Path(__file__).resolve().parents[1]


def inside(value):
    from tier8_artifact_paths import artifact_path
    return artifact_path(ROOT / value)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_adapter(directory, arm, drafter_model):
    role = "sas" if arm == "sas" else "drafter"
    expected = "7b" if arm == "sas" else "3b"
    if arm not in ("sas", "mas") or (arm == "mas" and drafter_model != "3b-q4"):
        raise ValueError("Adapter profile requires SAS 7B or MAS 3B Q4 drafter")
    return _validated_adapter(directory, expected, role, "drafter")


def load_critic_adapter(directory, verifier_model="3b"):
    if verifier_model != "3b":
        raise ValueError("Critic adapter requires a 3B Q4 verifier")
    return _validated_adapter(directory, "3b", "verifier", "critic")


def _validated_adapter(directory, expected, role, purpose):
    converted = inside(directory) / "manifest.json"
    info = json.loads(converted.read_text())
    if info.get("purpose", "drafter") != purpose:
        raise ValueError("A critic adapter cannot be loaded as a drafter, or a drafter as a critic")
    if info["status"] != "complete" or info["training_mode"] != "train" or info["diagnostic_only"]:
        raise ValueError("Require full trained adapter; fit diagnostics are not QA systems")
    if info["profile"] != expected or info["tensor_count"] <= 0:
        raise ValueError("Adapter checkpoint profile differs")
    for name, expected_sha in info["input_sha256"].items():
        if sha(inside(name)) != expected_sha:
            raise ValueError("Converted adapter provenance changed")
    run = inside(info["run"])
    training, summary, _ = validate_adapter(run)
    if training.get("purpose", "drafter") != info.get("purpose", "drafter"):
        raise ValueError("Adapter training purpose differs from conversion metadata")
    if purpose == "critic":
        n = training.get("training_n", 0)
        validation_loss = summary.get("validation_teacher_forced_loss")
        if (n <= 0 or training.get("validation_n", 0) <= 0
                or summary.get("examples_processed") != n
                or summary["optimizer_updates"] != (n + 7) // 8
                or not isinstance(validation_loss, (int, float))
                or not math.isfinite(validation_loss)):
            raise ValueError("Require a complete critic epoch and finite validation result")
    inputs = training.get("input_sha256", {})
    if purpose == "critic" and not inputs:
        raise ValueError("Critic training input provenance is missing")
    for name, expected_sha in inputs.items():
        if sha(inside(name)) != expected_sha:
            raise ValueError("Training input provenance changed")
    if training["mode"] != "train" or training["profile"] != expected:
        raise ValueError("Adapter training provenance/profile differs")
    for name in ("manifest.json", "summary.json"):
        relative = str((run / name).relative_to(ROOT)) if run.is_relative_to(ROOT) else str(run / name)
        if info["input_sha256"].get(relative) != sha(run / name):
            raise ValueError("Conversion does not bind this training run")
    path = inside(info["file"])
    if path.stat().st_size != info["bytes"] or sha(path) != info["sha256"]:
        raise ValueError("Converted adapter file integrity differs")
    return {"role": role, "purpose": purpose, "profile": expected, "file": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            "sha256": info["sha256"], "scale": 1.0, "training_run": str(run.relative_to(ROOT)) if run.is_relative_to(ROOT) else str(run),
            "conversion_manifest": str(converted.relative_to(ROOT)) if converted.is_relative_to(ROOT) else str(converted), "conversion_manifest_sha256": sha(converted),
            "optimizer_updates": summary["optimizer_updates"]}
