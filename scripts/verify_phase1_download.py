"""Verify every Phase 1 model/tokenizer file against the repository manifests."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPOSITORIES = {
    "Qwen/Qwen2.5-14B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct",
    "BAAI/bge-small-en-v1.5",
}


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    root_value = os.environ.get("AGERE_SSD_ROOT")
    if not root_value:
        raise SystemExit("ERROR: Set AGERE_SSD_ROOT to the mounted external SSD path first.")
    ssd_root = Path(root_value).expanduser().resolve()
    if not ssd_root.is_dir():
        raise SystemExit(f"ERROR: AGERE_SSD_ROOT is not an existing directory: {ssd_root}")

    weights_manifest = REPO_ROOT / "manifests" / "weights.sha256"
    snapshots_manifest = REPO_ROOT / "manifests" / "hf_snapshots.json"
    if not weights_manifest.is_file() or not snapshots_manifest.is_file():
        raise SystemExit("ERROR: Phase 1 manifests are missing from the repository.")

    snapshot_data = json.loads(snapshots_manifest.read_text(encoding="utf-8"))
    artifacts = snapshot_data.get("artifacts", [])
    repositories = {artifact.get("repo_id") for artifact in artifacts}
    if repositories != EXPECTED_REPOSITORIES:
        raise SystemExit(f"ERROR: Expected five model snapshots; manifest contains {len(repositories)}.")

    manifest_rows: list[tuple[str, str, Path]] = []
    for line_number, raw_line in enumerate(weights_manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip() or raw_line.startswith("#"):
            continue
        expected_hash, separator, relative_path = raw_line.partition("  ")
        if not separator or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            raise SystemExit(f"ERROR: Invalid SHA-256 manifest line {line_number}.")
        target = (ssd_root / PurePosixPath(relative_path)).resolve()
        if not target.is_relative_to(ssd_root):
            raise SystemExit(f"ERROR: Manifest path escapes the SSD root on line {line_number}.")
        manifest_rows.append((expected_hash, relative_path, target))

    if not manifest_rows:
        raise SystemExit("ERROR: No weight hashes found in the repository manifest.")
    artifact_paths = {artifact.get("path") for artifact in artifacts}
    manifest_paths = {relative_path for _, relative_path, _ in manifest_rows}
    if manifest_paths != artifact_paths or len(manifest_rows) != len(artifacts):
        raise SystemExit("ERROR: SHA-256 and snapshot manifests do not contain the same file set.")

    for index, (expected_hash, relative_path, target) in enumerate(manifest_rows, 1):
        if not target.is_file():
            raise SystemExit(f"ERROR: Missing artifact {index}/{len(manifest_rows)}: {relative_path}")
        actual_hash = hash_file(target)
        if actual_hash != expected_hash:
            raise SystemExit(f"ERROR: SHA-256 mismatch for {relative_path}")
        print(f"[{index}/{len(manifest_rows)}] OK {relative_path}", flush=True)

    print(
        f"Verified {len(manifest_rows)} files across {len(repositories)} snapshots "
        f"at {ssd_root}.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
