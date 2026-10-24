"""Prepare one pinned larger-drafter control; does not change frozen profiles."""
import json
from pathlib import Path
import shutil
import urllib.request

from tier8_v2_download import digest, transfer

ROOT = Path(__file__).resolve().parents[1]
REPO = "Qwen/Qwen2.5-3B-Instruct-GGUF"
REVISION = "7dabda4d13d513e3e842b20f0d435c732f172cbe"
NAME = "qwen2.5-3b-instruct-q4_k_m.gguf"
SIZE = 2104932768
SHA256 = "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d"


def main():
    with urllib.request.urlopen(f"https://huggingface.co/api/models/{REPO}/revision/{REVISION}?blobs=true", timeout=60) as response:
        metadata = json.load(response)
    entry = next(item for item in metadata["siblings"] if item["rfilename"] == NAME)
    if metadata["sha"] != REVISION or entry["lfs"]["sha256"] != SHA256 or entry["lfs"]["size"] != SIZE:
        raise ValueError("Official pinned metadata does not match the candidate specification")
    target = ROOT / "weights/tier8_v2" / NAME
    partial = target.with_suffix(".partial")
    if not target.exists() or target.stat().st_size != SIZE or digest(target) != SHA256:
        offset = partial.stat().st_size if partial.exists() else 0
        if shutil.disk_usage(target.parent).free < SIZE - offset + 500_000_000:
            raise RuntimeError("Insufficient disk headroom for candidate weights")
        transfer(f"https://huggingface.co/{REPO}/resolve/{REVISION}/{NAME}", partial, SIZE)
        if partial.stat().st_size != SIZE or digest(partial) != SHA256:
            raise ValueError("Candidate weights failed integrity verification; partial retained")
        partial.replace(target)
    result = {"repo": REPO, "revision": REVISION, "file": str(target.relative_to(ROOT)),
              "bytes": SIZE, "sha256": SHA256, "quantization": "Q4_K_M",
              "license_metadata": metadata.get("cardData", {}).get("license"),
              "status": "download_verified_only", "inference_or_memory_fit_tested": False,
              "scope": "Prospective separately labelled model-allocation control; does not replace original FP16 MAS."}
    (ROOT / "research/tier8_v2/evidence/candidate-model-3b.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
