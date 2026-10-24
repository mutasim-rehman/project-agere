"""Fetch hash-verified LoRA conversion sources matching llama-cpp-python 0.3.16."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "4227c9be4268ac844921b90f31595f81236bd317"


def main():
    output = ROOT / "research/tier8_v2/evidence/adapter-converter-source-01.json"
    if output.exists():
        raise ValueError("Converter source evidence already exists")
    with urllib.request.urlopen("https://api.github.com/repos/abetlen/llama-cpp-python/contents/vendor/llama.cpp?ref=v0.3.16", timeout=60) as response:
        submodule = json.load(response)
    if submodule["sha"] != COMMIT:
        raise ValueError("Version-tagged llama.cpp submodule differs")
    with urllib.request.urlopen(f"https://api.github.com/repos/ggml-org/llama.cpp/git/trees/{COMMIT}", timeout=60) as response:
        tree = json.load(response)
    if tree["sha"] != COMMIT or tree.get("truncated"):
        raise ValueError("Incomplete converter source tree")
    subtree_sha = next(r["sha"] for r in tree["tree"] if r["path"] == "gguf-py" and r["type"] == "tree")
    with urllib.request.urlopen(f"https://api.github.com/repos/ggml-org/llama.cpp/git/trees/{subtree_sha}?recursive=1", timeout=60) as response:
        subtree = json.load(response)
    if subtree["sha"] != subtree_sha or subtree.get("truncated"):
        raise ValueError("Incomplete GGUF Python source tree")
    entries = tree["tree"] + [{**r, "path": "gguf-py/" + r["path"]} for r in subtree["tree"]]
    exact = {"convert_hf_to_gguf.py", "convert_lora_to_gguf.py", "gguf-py/pyproject.toml", "gguf-py/README.md", "LICENSE"}
    selected = [r for r in entries if r["type"] == "blob" and
                (r["path"] in exact or (r["path"].startswith("gguf-py/gguf/") and r["path"].endswith(".py")))]
    if not exact <= {r["path"] for r in selected}:
        raise ValueError("Required conversion sources absent")
    folder = ROOT / ".local/llama-adapter-converter" / COMMIT
    def fetch(entry):
        path = folder / entry["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with urllib.request.urlopen(f"https://raw.githubusercontent.com/ggml-org/llama.cpp/{COMMIT}/{entry['path']}", timeout=60) as response:
                path.write_bytes(response.read())
        data = path.read_bytes()
        if len(data) != entry["size"] or hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != entry["sha"]:
            raise ValueError("Converter Git blob integrity differs")
        return {"file": entry["path"], "bytes": len(data), "git_blob": entry["sha"], "sha256": hashlib.sha256(data).hexdigest()}
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, selected))
    report = {"repo": "ggml-org/llama.cpp", "revision": COMMIT, "python_runtime_version": "0.3.16",
              "submodule_source": "abetlen/llama-cpp-python v0.3.16 vendor/llama.cpp",
              "folder": str(folder.relative_to(ROOT)), "files": records,
              "source_hashes_verified": True, "conversion_executed": False,
              "adapter_applied": False, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({**report, "files": len(records)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
