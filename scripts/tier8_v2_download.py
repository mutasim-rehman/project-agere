"""Fetch revision-pinned official GGUFs within the checkout, verifying LFS hashes."""
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "weights" / "tier8_v2"
SPECS = [
    ("Qwen/Qwen2.5-0.5B-Instruct-GGUF", "9217f5db79a29953eb74d5343926648285ec7e67", "fp16"),
    ("Qwen/Qwen2.5-1.5B-Instruct-GGUF", "91cad51170dc346986eccefdc2dd33a9da36ead9", "fp16"),
    ("Qwen/Qwen2.5-7B-Instruct-GGUF", "bb5d59e06d9551d752d08b292a50eb208b07ab1f", "q4_k_m"),
]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = []
    for repo, revision, precision in SPECS:
        with urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true", timeout=60) as response:
            metadata = json.load(response)
        for entry in metadata["siblings"]:
            name = entry["rfilename"]
            if not name.endswith(".gguf") or f"-{precision}" not in name:
                continue
            expected = entry["lfs"]["sha256"]
            size = entry["lfs"]["size"]
            target = DEST / name
            if not target.exists() or target.stat().st_size != size or digest(target) != expected:
                partial = target.with_suffix(".partial")
                if shutil.disk_usage(DEST).free < size + 500_000_000:
                    raise RuntimeError("Insufficient disk headroom")
                url = f"https://huggingface.co/{repo}/resolve/{revision}/{name}"
                print(f"Downloading {name}: {size} bytes", flush=True)
                # Retry the process on network failure; completed verified files are reused.
                with urllib.request.urlopen(url, timeout=120) as source, partial.open("wb") as out:
                    shutil.copyfileobj(source, out, length=8 * 1024 * 1024)
                if partial.stat().st_size != size or digest(partial) != expected:
                    raise RuntimeError(f"Integrity failure: {name}")
                partial.replace(target)
            print(f"Verified {name}", flush=True)
            manifest.append({"repo": repo, "revision": revision, "file": str(target.relative_to(ROOT)),
                             "bytes": size, "sha256": expected})
            (ROOT / "research/tier8_v2/evidence/models.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
