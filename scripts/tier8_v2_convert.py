"""Convert official mixed F32/F16 embeddings to native F16 GGUFs locally.

No quantized tensors are introduced. Preserve original hashes and transformation
parameters; conversion is preprocessing, not a scored inference experiment.
"""
import ctypes
import hashlib
import json
from pathlib import Path
import time

from gguf_integrity import inspect_gguf

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main():
    import llama_cpp as runtime
    source_manifest = json.loads((ROOT / "research/tier8_v2/evidence/models.json").read_text())
    out_manifest = ROOT / "research/tier8_v2/evidence/native-models.json"
    existing = json.loads(out_manifest.read_text()) if out_manifest.exists() else []
    for size in ("0.5b", "1.5b"):
        filename = f"qwen2.5-{size}-instruct-fp16.gguf"
        source = ROOT / "weights/tier8_v2" / filename
        target = source.with_name(f"qwen2.5-{size}-instruct-native-f16.gguf")
        metadata = next(e for e in source_manifest if Path(e["file"]).name == filename)
        if digest(source) != metadata["sha256"]:
            raise ValueError(f"Source hash mismatch: {filename}")
        previous = next((e for e in existing if e["file"] == str(target.relative_to(ROOT))), None)
        if previous and target.exists() and digest(target) == previous["sha256"]:
            print(f"Verified existing {target.name}", flush=True)
            continue
        partial = target.with_suffix(".partial")
        params = runtime.llama_model_quantize_default_params()
        params.nthread = 4
        params.ftype = runtime.LLAMA_FTYPE_MOSTLY_F16
        params.output_tensor_type = runtime.GGML_TYPE_F16
        params.token_embedding_type = runtime.GGML_TYPE_F16
        params.allow_requantize = False
        params.quantize_output_tensor = True
        started = time.monotonic()
        code = runtime.llama_model_quantize(str(source).encode(), str(partial).encode(), ctypes.byref(params))
        if code:
            raise RuntimeError(f"F16 conversion returned {code}")
        integrity = inspect_gguf(partial)
        partial.replace(target)
        entry = {"file": str(target.relative_to(ROOT)), "bytes": target.stat().st_size,
                 "sha256": digest(target), "source_sha256": metadata["sha256"],
                 "source_file": metadata["file"], "runtime": runtime.__version__,
                 "transform": {"ftype": "MOSTLY_F16", "token_embedding_type": "F16", "output_tensor_type": "F16", "allow_requantize": False},
                 "seconds": time.monotonic() - started, "integrity": integrity}
        existing = [e for e in existing if e["file"] != entry["file"]] + [entry]
        out_manifest.write_text(json.dumps(existing, indent=2) + "\n")
        print(json.dumps(entry), flush=True)


if __name__ == "__main__":
    main()
