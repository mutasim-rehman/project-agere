"""Report overlap at question, page, company-year report, and company levels."""
import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path


def identities(path):
    raw = path.read_bytes()
    cases = {row["id"] for row in json.loads(raw)}
    groups = {"question": cases,
              "page": {case.rsplit(".pdf-", 1)[0] + ".pdf" for case in cases},
              "report": {case.rsplit("/", 1)[0] for case in cases},
              "company": {case.split("/", 1)[0] for case in cases}}
    return groups, hashlib.sha256(raw).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("train", "development", "test"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    inputs = {name: identities(getattr(args, name)) for name in ("train", "development", "test")}
    levels = tuple(inputs["test"][0])
    print(json.dumps({
        "sources": {name: {"sha256": sha, "distinct": {level: len(groups[level]) for level in levels}}
                    for name, (groups, sha) in inputs.items()},
        "overlaps": {f"{first}_{second}": {
            level: len(inputs[first][0][level] & inputs[second][0][level]) for level in levels}
            for first, second in combinations(inputs, 2)}
    }, indent=2))
