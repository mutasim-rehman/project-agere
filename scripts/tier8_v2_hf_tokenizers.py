"""Pin official HF tokenizer assets and verify exact deployment-token parity."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {
    "mas-3b-q4": ("Qwen/Qwen2.5-3B-Instruct", "aa8e72537993ba99e69dfaafa59ed015b17504d1"),
    "sas-7b-q4": ("Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28"),
}
ASSETS = ("tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt", "config.json", "generation_config.json")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch():
    output = ROOT / "research/tier8_v2/evidence/hf-tokenizer-snapshots-01.json"
    if output.exists():
        raise ValueError("Refusing to overwrite tokenizer snapshot manifest")
    profiles = {}
    for profile, (repo, revision) in PROFILES.items():
        with urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true", timeout=60) as response:
            metadata = json.load(response)
        if metadata["sha"] != revision:
            raise ValueError("HF did not resolve pinned revision")
        files = {r["rfilename"]: r for r in metadata["siblings"]}
        folder = ROOT / "weights/hf-tokenizers" / profile
        folder.mkdir(parents=True, exist_ok=True)
        records = []
        for name in ASSETS:
            entry = files[name]
            destination = folder / name
            if not destination.exists():
                url = f"https://huggingface.co/{repo}/resolve/{revision}/{name}"
                with urllib.request.urlopen(url, timeout=60) as response:
                    data = response.read()
                destination.write_bytes(data)
            data = destination.read_bytes()
            if len(data) != entry["size"]:
                raise ValueError("Tokenizer asset size mismatch")
            lfs = entry.get("lfs")
            if lfs:
                if hashlib.sha256(data).hexdigest() != lfs["sha256"]:
                    raise ValueError("Tokenizer LFS SHA mismatch")
            elif hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != entry["blobId"]:
                raise ValueError("Tokenizer Git blob mismatch")
            records.append({"file": name, "bytes": len(data), "sha256": sha(destination), "git_blob": entry["blobId"]})
        profiles[profile] = {"repo": repo, "revision": revision,
                             "folder": str(folder.relative_to(ROOT)), "files": records}
    report = {"profiles": profiles, "only_tokenizer_config_assets": True,
              "model_weights_downloaded": False, "script_sha256": sha(Path(__file__))}
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


def verify():
    # Prevent HF libraries from consulting caches or downloading outside ROOT.
    os.environ["HF_HOME"] = str(ROOT / ".local/hf-training")
    os.environ["HF_HUB_CACHE"] = str(ROOT / ".local/hf-training/hub")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    from transformers import AutoTokenizer, __version__ as transformers_version
    import tokenizers
    base = ROOT / "research/tier8_v2"
    snapshots = base / "evidence/hf-tokenizer-snapshots-01.json"
    dataset_manifest = base / "evidence/deployment-sft-1024-02.json"
    output = base / "evidence/hf-tokenizer-parity-01.json"
    if output.exists():
        raise ValueError("Refusing to overwrite tokenizer parity evidence")
    manifest = json.loads(dataset_manifest.read_text())
    data_path = (ROOT / manifest["output_file"]).resolve()
    if not data_path.is_relative_to(ROOT) or sha(data_path) != manifest["output_sha256"]:
        raise ValueError("Deployment dataset changed")
    rows = [json.loads(line) for line in data_path.read_text().splitlines()]
    if len(rows) != manifest["kept_n"]:
        raise ValueError("Incomplete deployment dataset")
    results = {}
    for profile, assets in json.loads(snapshots.read_text())["profiles"].items():
        folder = (ROOT / assets["folder"]).resolve()
        if not folder.is_relative_to(ROOT):
            raise ValueError("Tokenizer folder outside project")
        if (assets["repo"], assets["revision"]) != PROFILES[profile]:
            raise ValueError("Tokenizer revision differs from pin")
        for entry in assets["files"]:
            if sha(folder / entry["file"]) != entry["sha256"]:
                raise ValueError("Tokenizer snapshot changed")
        tokenizer = AutoTokenizer.from_pretrained(str(folder), local_files_only=True, trust_remote_code=False)
        failures = []
        for row in rows:
            reference = row["tokenization"][profile]
            prefix = tokenizer.encode(row["prompt"], add_special_tokens=False)
            full = tokenizer.encode(row["prompt"] + reference["response"], add_special_tokens=False)
            checks = {"input_ids": hashlib.sha256(json.dumps(full).encode()).hexdigest() == reference["input_ids_sha256"],
                      "prefix_mask": len(prefix) == reference["label_mask_prefix_tokens"] and full[:len(prefix)] == prefix,
                      "length": len(full) == reference["total_tokens"] <= manifest["max_training_tokens"]}
            if not all(checks.values()):
                failures.append({"source_id": row["source_id"], "checks": checks})
        results[profile] = {"n": len(rows), "mismatches": failures, "pass": not failures,
                             "tokenizer_class": type(tokenizer).__name__, "repo": assets["repo"], "revision": assets["revision"]}
    report = {"profiles": results, "pass": bool(results) and all(r["pass"] for r in results.values()),
              "transformers_version": transformers_version, "tokenizers_version": tokenizers.__version__,
              "snapshots_sha256": sha(snapshots), "dataset_manifest_sha256": sha(dataset_manifest),
              "dataset_sha256": sha(data_path), "script_sha256": sha(Path(__file__)),
              "model_training_performed": False, "model_calls": 0}
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    if not report["pass"]:
        raise ValueError("HF/GGUF tokenizer parity failed; training prohibited")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("fetch", "verify"))
    args = parser.parse_args()
    {"fetch": fetch, "verify": verify}[args.mode]()
