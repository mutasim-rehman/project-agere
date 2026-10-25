"""Convert a proven updated PEFT adapter using verified runtime-paired sources.

Conversion is not proof of application or reasoning gain. Fit diagnostics retain
their diagnostic label. Full measured inference still requires loading this file.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ARCH_KEYS = ("model_type", "hidden_size", "intermediate_size", "num_attention_heads",
             "num_key_value_heads", "num_hidden_layers", "vocab_size", "tie_word_embeddings",
             "rope_theta", "rope_scaling", "rms_norm_eps", "hidden_act")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(path):
    from tier8_artifact_paths import artifact_path
    return artifact_path(ROOT / path)


def check_architecture(training, deployment):
    required = ("hidden_size", "intermediate_size", "num_attention_heads", "num_key_value_heads", "num_hidden_layers", "vocab_size")
    if training.get("model_type") != "qwen2" or any(not isinstance(training.get(k), int) or training[k] <= 0 for k in required):
        raise ValueError("Require complete Qwen2 architecture dimensions")
    differences = {k: [training.get(k), deployment.get(k)] for k in ARCH_KEYS
                   if training.get(k) != deployment.get(k)}
    if differences:
        raise ValueError(f"Training/deployment model architecture differs: {differences}")


def validate_adapter(run):
    manifest = json.loads((run / "manifest.json").read_text())
    summary = json.loads((run / "summary.json").read_text())
    if summary["status"] != "complete" or summary["changed_adapter_tensors"] <= 0 or summary["optimizer_updates"] < 2:
        raise ValueError("Require complete real adapter updates, not an initialized adapter")
    if summary["mode"] not in ("fit", "train") or summary["mode"] != manifest["mode"]:
        raise ValueError("Adapter training mode differs")
    adapter = run / "adapter"
    if not {"adapter_config.json", "adapter_model.safetensors"} <= set(summary["adapter_files"]):
        raise ValueError("Adapter config or safe tensor weights missing")
    for name, expected in summary["adapter_files"].items():
        if Path(name).name != name or sha(adapter / name) != expected:
            raise ValueError("Saved adapter integrity differs")
    return manifest, summary, adapter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run, out = inside(args.run), inside(args.out)
    if out.exists():
        raise ValueError("Use a new conversion output directory")
    manifest, summary, adapter = validate_adapter(run)
    profile = "mas-3b-q4" if manifest["profile"] == "3b" else "sas-7b-q4"
    tokenizer_dir = ROOT / "weights/hf-tokenizers" / profile
    model_config_path = tokenizer_dir / "config.json"
    training_config = inside(manifest["training_base"]["folder"]) / "config.json"
    check_architecture(json.loads(training_config.read_text()), json.loads(model_config_path.read_text()))
    source_manifest_path = ROOT / "research/tier8_v2/evidence/adapter-converter-source-01.json"
    source = json.loads(source_manifest_path.read_text())
    folder = inside(source["folder"])
    for item in source["files"]:
        path = (folder / item["file"]).resolve()
        if not path.is_relative_to(folder) or sha(path) != item["sha256"]:
            raise ValueError("Pinned converter source differs")
    out.mkdir(parents=True)
    target = out / "adapter-f16.gguf"
    command = [sys.executable, str(folder / "convert_lora_to_gguf.py"), "--base", str(tokenizer_dir),
               "--outfile", str(target), "--outtype", "f16", str(adapter)]
    environment = {**os.environ, "HF_HOME": str(ROOT / ".local/hf-training"),
                   "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "TMPDIR": str(ROOT / ".local/tmp")}
    with (out / "conversion.log").open("x") as log:
        subprocess.run(command, cwd=ROOT, env=environment, stdout=log, stderr=log, check=True)
    sys.path.insert(0, str(folder / "gguf-py"))
    import gguf
    import numpy as np
    reader = gguf.GGUFReader(str(target))
    def field(name):
        value = reader.get_field(name)
        return value.contents() if value is not None else None
    config = json.loads((adapter / "adapter_config.json").read_text())
    if field("general.type") != "adapter" or field("adapter.type") != "lora" or field("adapter.lora.alpha") != config["lora_alpha"]:
        raise ValueError("Converted GGUF adapter metadata differs")
    tensors = {t.name: t for t in reader.tensors}
    if not tensors or len(tensors) % 2 or any(not np.isfinite(t.data).all() for t in tensors.values()):
        raise ValueError("Invalid or nonfinite converted adapter tensors")
    for name in tensors:
        if name.endswith(".lora_a"):
            if name[:-7] + ".lora_b" not in tensors:
                raise ValueError("Unpaired adapter matrix")
        elif not name.endswith(".lora_b") or name[:-7] + ".lora_a" not in tensors:
            raise ValueError("Unexpected or unpaired adapter tensor")
    report = {"status": "complete", "training_mode": manifest["mode"],
              "diagnostic_only": manifest["mode"] == "fit", "profile": manifest["profile"],
              "purpose": manifest.get("purpose", "drafter"),
              "run": str(run.relative_to(ROOT)) if run.is_relative_to(ROOT) else str(run), "command": command,
              "input_sha256": {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p) for p in
                    (run / "manifest.json", run / "summary.json", source_manifest_path, model_config_path, training_config)},
              "script_sha256": sha(Path(__file__)), "file": str(target.relative_to(ROOT)) if target.is_relative_to(ROOT) else str(target), "sha256": sha(target),
              "bytes": target.stat().st_size, "tensor_count": len(tensors), "outtype": "f16",
              "runtime_adapter_applied": False, "measured_reasoning_gain": False}
    (out / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
