"""Download the locked Phase 1 model snapshots to the validated external SSD."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPOSITORIES = (
    "Qwen/Qwen2.5-14B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct",
    "BAAI/bge-small-en-v1.5",
)
ALLOW_PATTERNS = (
    "*.safetensors",
    "*.bin",
    "*.json",
    "*.model",
    "*.tiktoken",
    "*.txt",
    "*.vocab",
    "*.merges",
    "*.jinja",
)
MIN_FREE_GB = 80
HF_TOKEN_KEYS = {"HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_HUB_TOKEN"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_hf_token_from_dotenv() -> bool:
    """Expose an existing .env token only to this process; never print or persist it."""
    if os.environ.get("HF_TOKEN"):
        return True

    env_file = REPO_ROOT / ".env"
    if not env_file.is_file():
        return False

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, separator, value = line.partition("=")
        if not separator or key.strip() not in HF_TOKEN_KEYS:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        else:
            value = value.split(" #", 1)[0].strip()
        if value:
            os.environ["HF_TOKEN"] = value
            return True
    return False


def main() -> int:
    root_value = os.environ.get("AGERE_SSD_ROOT")
    if not root_value:
        raise SystemExit("ERROR: Set AGERE_SSD_ROOT to the mounted external SSD path first.")

    ssd_root = Path(root_value).expanduser().resolve()
    if not ssd_root.is_dir():
        raise SystemExit(f"ERROR: AGERE_SSD_ROOT is not an existing directory: {ssd_root}")
    if not (REPO_ROOT / "ROADMAP.md").is_file():
        raise SystemExit(f"ERROR: Repository root could not be confirmed: {REPO_ROOT}")

    authenticated = load_hf_token_from_dotenv()

    weights_root = ssd_root / "weights"
    snapshots_root = weights_root / "hf"
    snapshots_root.mkdir(parents=True, exist_ok=True)
    free_gb = shutil.disk_usage(ssd_root).free / (1024**3)
    if free_gb < MIN_FREE_GB:
        raise SystemExit(
            f"ERROR: Only {free_gb:.1f} GiB free on {ssd_root}; "
            f"Phase 1 requires at least {MIN_FREE_GB} GiB free before starting."
        )

    # local_dir stores only model files plus Hub resume metadata under weights/hf.
    # Keep any Hugging Face auth token on this computer's default user config,
    # never move credentials to the external model/data drive.
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")
    # The Xet transfer backend stalled on this host; use the resumable HTTPS path.
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as exc:
        raise SystemExit(
            "ERROR: Install the Phase 1 downloader dependency on this computer with: "
            "python -m pip install -r requirements-phase1.txt"
        ) from exc

    api = HfApi()
    plan: list[tuple[str, str, Path, list[object]]] = []
    required_bytes = 0
    for repo_id in REPOSITORIES:
        info = api.model_info(repo_id, files_metadata=True)
        if not info.sha:
            raise SystemExit(f"ERROR: Hub did not return an immutable revision for {repo_id}")
        local_dir = snapshots_root / repo_id.replace("/", "--")
        files = snapshot_download(
            repo_id,
            revision=info.sha,
            allow_patterns=list(ALLOW_PATTERNS),
            local_dir=local_dir,
            dry_run=True,
        )
        bytes_to_download = sum(
            item.file_size or 0 for item in files if item.will_download
        )
        required_bytes += bytes_to_download
        plan.append((repo_id, info.sha, local_dir, files))
        print(f"PLAN {repo_id}@{info.sha[:12]}: {bytes_to_download / (1024**3):.2f} GiB")

    free_bytes = shutil.disk_usage(ssd_root).free
    required_with_margin = int(required_bytes * 1.15)
    if free_bytes < required_with_margin:
        raise SystemExit(
            f"ERROR: The selected snapshots need about {required_bytes / (1024**3):.1f} GiB "
            f"plus 15% headroom, but only {free_bytes / (1024**3):.1f} GiB is free."
        )
    print(
        f"SSD: {ssd_root} | free: {free_bytes / (1024**3):.1f} GiB | "
        f"planned: {required_bytes / (1024**3):.1f} GiB | "
        f"Hugging Face auth: {'enabled' if authenticated else 'not configured'}"
    )

    for repo_id, revision, local_dir, _ in plan:
        print(f"\nDownloading {repo_id}@{revision} -> {local_dir}", flush=True)
        snapshot_download(
            repo_id,
            revision=revision,
            local_dir=local_dir,
            allow_patterns=list(ALLOW_PATTERNS),
            max_workers=8,
        )

    generated_at = datetime.now(timezone.utc).isoformat()
    entries: list[dict[str, str | int]] = []
    for repo_id, revision, local_dir, _ in plan:
        files = sorted(
            path for path in local_dir.rglob("*")
            if path.is_file() and ".cache" not in path.relative_to(local_dir).parts
        )
        if not files:
            raise SystemExit(f"ERROR: No snapshot files found after download: {repo_id}")
        for path in files:
            entries.append(
                {
                    "repo_id": repo_id,
                    "revision": revision,
                    "path": path.relative_to(ssd_root).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )

    manifests = REPO_ROOT / "manifests"
    manifests.mkdir(exist_ok=True)
    (manifests / "weights.sha256").write_text(
        "".join(f"{item['sha256']}  {item['path']}\n" for item in entries),
        encoding="utf-8",
    )
    (manifests / "hf_snapshots.json").write_text(
        json.dumps(
            {
                "generated_at_utc": generated_at,
                "ssd_root_at_download": str(ssd_root),
                "artifacts": entries,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nVerified and recorded {len(entries)} files from {len(plan)} snapshots.")
    print(f"Repository manifests: {manifests}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
