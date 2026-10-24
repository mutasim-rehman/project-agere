"""Small-model runtime diagnostic, explicitly not the SAS/MAS comparison."""
import hashlib
import json
import os
from pathlib import Path
import threading
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    import psutil
    from llama_cpp import Llama, LlamaGrammar, __version__
    out = ROOT / "research/tier8_v2/evidence/capacity-05"
    out.mkdir(exist_ok=False)
    weights = ROOT / "weights/tier8_v2/qwen2.5-0.5b-instruct-fp16.gguf"
    manifest = json.loads((ROOT / "research/tier8_v2/evidence/models.json").read_text())
    expected = next(e for e in manifest if Path(e["file"]).name == weights.name)
    sha = hashlib.sha256()
    with weights.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            sha.update(block)
    if sha.hexdigest() != expected["sha256"]:
        raise ValueError("Weight checksum mismatch")
    cap = min(6_400_000_000, psutil.virtual_memory().available - 1_000_000_000)
    stop = threading.Event()
    peak = [0]
    def watch():
        with (out / "memory.jsonl").open("w") as stream:
            while not stop.is_set():
                process = psutil.Process()
                rss = sum(p.memory_info().rss for p in [process, *process.children(recursive=True)])
                peak[0] = max(peak[0], rss)
                stream.write(json.dumps({"time": time.time(), "rss_bytes": rss}) + "\n")
                stream.flush()
                if rss > cap:
                    (out / "summary.json").write_text(json.dumps({"status": "invalid_memory", "rss_bytes": rss, "cap_bytes": cap}))
                    os._exit(2)
                stop.wait(0.1)
    thread = threading.Thread(target=watch, daemon=True)
    thread.start()
    records = []
    try:
        model = Llama(model_path=str(weights), n_ctx=2048, n_gpu_layers=0,
                      n_threads=8, n_threads_batch=8, n_batch=64, n_ubatch=64,
                      use_mmap=False, seed=42, verbose=False)
        probes = [("arithmetic", "What is 2+2? Reply with the digit only.", "4"),
                  ("copy_name", "Source: The beneficial owner is Amina Cedar. Return a JSON object with key value containing the owner name.", "Amina Cedar"),
                  ("missing", "Source: The identity expiry date was not supplied. Return a JSON object with key value containing MISSING if the expiry date is absent.", "MISSING")]
        for name, task, expected_value in probes:
            prompt = f"<|im_start|>user\n{task}<|im_end|>\n<|im_start|>assistant\n"
            schema = {"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"], "additionalProperties": False}
            kwargs = {} if name == "arithmetic" else {"grammar": LlamaGrammar.from_json_schema(json.dumps(schema), verbose=False)}
            started = time.monotonic()
            result = model.create_completion(prompt, max_tokens=96, temperature=0, top_k=1,
                                             seed=42, repeat_penalty=1, stop=["<|im_end|>"], **kwargs)
            response = result["choices"][0]["text"].strip()
            try:
                predicted = response if name == "arithmetic" else json.loads(response)["value"]
            except (ValueError, KeyError, TypeError):
                predicted = None
            record = {"probe": name, "prompt": task, "response": response,
                      "correct": predicted == expected_value, "seconds": time.monotonic() - started,
                      "usage": result["usage"], "finish_reason": result["choices"][0]["finish_reason"]}
            records.append(record)
            with (out / "probes.jsonl").open("a") as stream:
                stream.write(json.dumps(record) + "\n")
            print(json.dumps(record), flush=True)
        model.close()
    finally:
        stop.set()
        thread.join()
    summary = {"status": "complete", "scope": "0.5B primitive diagnostic; not an architecture comparison",
               "n": len(records), "correct": sum(r["correct"] for r in records),
               "runtime": __version__, "weights_sha256": sha.hexdigest(), "peak_rss_bytes": peak[0], "cap_bytes": cap}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
