"""Fetch revision-pinned official GGUFs within the checkout, verifying LFS hashes."""
import hashlib
import json
from pathlib import Path
import shutil
import re
import urllib.request
import urllib.error

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


def transfer(url, partial, expected_size):
    """Resume only range-validated prefixes; reject contradictory HTTP metadata."""
    for attempt in range(12):
        offset = partial.stat().st_size if partial.exists() else 0
        if offset == expected_size:
            return
        if offset > expected_size:
            raise RuntimeError("Partial exceeds expected size")
        request = urllib.request.Request(url + f"?download=true&agere_retry={attempt}",
                                         headers={"Range": f"bytes={offset}-", "Cache-Control": "no-cache"})
        try:
            with urllib.request.urlopen(request, timeout=120) as source:
                if source.status == 206:
                    match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", source.headers.get("Content-Range", ""))
                    if not match or int(match[1]) != offset or int(match[3]) != expected_size:
                        raise RuntimeError("Inconsistent Content-Range")
                elif offset:
                    raise RuntimeError("Server refused a validated resume")
                print(f"Transfer {partial.name}: offset={offset}, status={source.status}, content_length={source.headers.get('Content-Length')}", flush=True)
                with partial.open("ab" if offset else "wb") as out:
                    shutil.copyfileobj(source, out, length=8 * 1024 * 1024)
            actual = partial.stat().st_size
            print(f"Transfer ended at {actual}/{expected_size} bytes", flush=True)
            if actual == offset:
                raise RuntimeError("No download progress")
        except (OSError, urllib.error.URLError) as exc:
            print(f"Transfer interrupted: {type(exc).__name__}; prefix retained", flush=True)
    raise RuntimeError("Transfer did not reach the verified size after 12 requests")


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
                offset = partial.stat().st_size if partial.exists() else 0
                if shutil.disk_usage(DEST).free < size - offset + 500_000_000:
                    raise RuntimeError("Insufficient disk headroom")
                url = f"https://huggingface.co/{repo}/resolve/{revision}/{name}"
                print(f"Downloading {name}: {size} bytes", flush=True)
                transfer(url, partial, size)
                actual_sha = digest(partial)
                if partial.stat().st_size != size or actual_sha != expected:
                    partial.rename(partial.with_name(partial.name + ".rejected-" + actual_sha[:12]))
                    raise RuntimeError(f"Integrity failure: {name}")
                partial.replace(target)
            print(f"Verified {name}", flush=True)
            manifest.append({"repo": repo, "revision": revision, "file": str(target.relative_to(ROOT)),
                             "bytes": size, "sha256": expected})
            (ROOT / "research/tier8_v2/evidence/models.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
