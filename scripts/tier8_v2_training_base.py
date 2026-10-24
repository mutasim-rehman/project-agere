"""Download a pinned prequantized training base, separately from GGUF inference."""
import argparse
import json
from pathlib import Path
import shutil
import urllib.request

from tier8_v2_download import digest, transfer

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    "3b": ("unsloth/Qwen2.5-3B-Instruct-bnb-4bit", "2672b588848527e456d320c11926c794539f47d5", 2054625552),
    "7b": ("unsloth/Qwen2.5-7B-Instruct-bnb-4bit", "bdd404162d94997f390efbfa660eb3f21cbbc81d", 5547254622),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=tuple(SPECS), default="3b")
    parser.add_argument("--metadata-only", action="store_true")
    args = parser.parse_args()
    repo, revision, size = SPECS[args.profile]
    base = ROOT / "research/tier8_v2"
    output = base / "evidence" / f"training-base-{args.profile}-01.json"
    if output.exists() and json.loads(output.read_text()).get("weights_verified"):
        raise ValueError("Training snapshot already verified; do not overwrite evidence")
    with urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true", timeout=60) as response:
        metadata = json.load(response)
    if metadata["sha"] != revision:
        raise ValueError("Training base revision differs")
    files = {r["rfilename"]: r for r in metadata["siblings"]}
    weight = files["model.safetensors"]
    if weight["size"] != size or weight["lfs"]["size"] != size:
        raise ValueError("Training base size differs from specification")
    folder = ROOT / "weights/hf-training" / args.profile
    folder.mkdir(parents=True, exist_ok=True)
    config_records = []
    import hashlib
    for name in ("config.json", "generation_config.json"):
        path = folder / name
        if not path.exists():
            with urllib.request.urlopen(f"https://huggingface.co/{repo}/resolve/{revision}/{name}", timeout=60) as response:
                path.write_bytes(response.read())
        data = path.read_bytes()
        expected = files[name]
        if len(data) != expected["size"] or hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != expected["blobId"]:
            raise ValueError("Training config integrity differs")
        config_records.append({"file": name, "bytes": len(data), "sha256": digest(path)})
    config = json.loads((folder / "config.json").read_text())
    if config["model_type"] != "qwen2" or config["quantization_config"]["quant_method"] != "bitsandbytes":
        raise ValueError("Unsupported prequantized training architecture")
    target = folder / "model.safetensors"
    report = {"repo": repo, "revision": revision, "folder": str(folder.relative_to(ROOT)),
              "weight_file": target.name, "bytes": size, "sha256": weight["lfs"]["sha256"],
              "config_files": config_records, "quantization_config": config["quantization_config"],
              "weights_verified": False, "script_sha256": digest(Path(__file__)),
              "deployment_quantization": "Q4_K_M GGUF (different from this NF4 training base)",
              "exact_original_fp16_equivalence_asserted": False, "model_trained": False}
    output.write_text(json.dumps(report, indent=2) + "\n")
    if not args.metadata_only:
        if not target.exists() or target.stat().st_size != size or digest(target) != report["sha256"]:
            partial = target.with_suffix(".partial")
            offset = partial.stat().st_size if partial.exists() else 0
            if shutil.disk_usage(folder).free < size - offset + 500_000_000:
                raise ValueError("Insufficient disk for training base plus headroom")
            transfer(f"https://huggingface.co/{repo}/resolve/{revision}/{target.name}", partial, size)
            if partial.stat().st_size != size or digest(partial) != report["sha256"]:
                raise ValueError("Training base integrity failure; partial retained")
            partial.replace(target)
        report["weights_verified"] = True
        output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
