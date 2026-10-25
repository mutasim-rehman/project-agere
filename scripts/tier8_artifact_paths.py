"""Resolve research artifacts inside the checkout or explicitly mounted SSD."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def artifact_path(value):
    path = (ROOT / value).resolve()
    if path.is_relative_to(ROOT):
        return path
    configured = os.environ.get("AGERE_SSD_ROOT")
    if configured:
        ssd = Path(configured).resolve()
        if (ssd.is_dir() and (ssd / "datasets").is_dir()
                and (ssd / "weights").is_dir() and path.is_relative_to(ssd)):
            return path
    raise ValueError("Artifact must resolve inside repository or configured mounted AGERE SSD")
