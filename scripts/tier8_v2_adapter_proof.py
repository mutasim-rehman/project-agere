"""Memory-monitored 0 -> 1 -> 0 adapter effect check, not a QA accuracy run."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from completion_tokenization import completion_tokens
from tier8_v2_adapter_runtime import load_adapter
from tier8_v2_run import MODEL_FILES, WEIGHTS, inside, verified_models

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def worker(args, out):
    from llama_cpp import Llama, llama_cpp as api
    info = load_adapter(args.adapter, args.arm, "3b-q4")
    dataset = inside("research/tier8_v2/data/deployment-sft-1024-02.jsonl")
    row = next(r for r in map(json.loads, dataset.read_text().splitlines()) if r["split"] == "validation")
    filename = "qwen2.5-3b-instruct-q4_k_m.gguf" if args.arm == "mas" else MODEL_FILES["sas"]["sas"]
    model = Llama(model_path=str(WEIGHTS / filename), n_ctx=4096, n_gpu_layers=0,
        n_threads=8, n_threads_batch=8, n_batch=64, n_ubatch=64, seed=42,
        use_mmap=False, verbose=False, logits_all=True,
        lora_path=str(ROOT / info["file"]), lora_scale=0.0)
    try:
        if not model._lora_adapter:
            raise ValueError("Runtime has no adapter handle")
        phases = []
        for scale in (0.0, 1.0, 0.0):
            if api.llama_set_adapter_lora(model._ctx.ctx, model._lora_adapter, scale):
                raise ValueError("Runtime rejected adapter scale")
            model.reset()
            result = model.create_completion(row["prompt"], max_tokens=1, logprobs=20,
                temperature=0, top_k=1, seed=42, repeat_penalty=1, stop=["<|im_end|>"])
            if result["usage"]["prompt_tokens"] != len(completion_tokens(model, row["prompt"])):
                raise ValueError("Real generation token accounting mismatch")
            choice = result["choices"][0]
            tops = choice["logprobs"]["top_logprobs"]
            if len(tops) != 1 or result["usage"]["completion_tokens"] != 1:
                raise ValueError("Expected exactly one diagnostic output token")
            phases.append({"scale": scale, "text": choice["text"],
                           "top_logprobs": {key: float(value) for key, value in tops[0].items()},
                           "usage": result["usage"]})
        zero, one, repeated = [p["top_logprobs"] for p in phases]
        if set(zero) != set(repeated):
            raise ValueError("Repeated zero-scale token set differs")
        drift = max(abs(zero[k] - repeated[k]) for k in zero)
        common = set(zero) & set(one)
        effect = max((abs(zero[k] - one[k]) for k in common), default=0)
        if drift > 1e-5 or effect <= max(1e-5, 10 * drift):
            raise ValueError("No reproducible reversible adapter effect established")
        proof = {"pass": True, "adapter": info, "source_id": row["source_id"],
                 "prompt_sha256": hashlib.sha256(row["prompt"].encode()).hexdigest(),
                 "dataset_sha256": sha(dataset), "phases": phases, "zero_repeat_max_logprob_drift": drift,
                 "common_tokens": len(common), "max_common_token_logprob_effect": effect,
                 "scope": "One validation prompt, three next-token calls with KV reset; proves application/effect only, not QA gain or full MAS memory."}
        (out / "proof.json").write_text(json.dumps(proof, indent=2) + "\n")
    finally:
        model.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--arm", choices=("mas", "sas"), default="mas")
    parser.add_argument("--out", required=True)
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    out = inside(args.out)
    if args.worker:
        worker(args, out)
        return
    import psutil
    for p in psutil.process_iter(["cmdline"]):
        if p.pid == os.getpid():
            continue
        names = {Path(x).name for x in p.info["cmdline"] or []}
        if names & {"tier8_v2_adapt.py", "tier8_v2_run.py", "tier8_v2_replay.py", "tier8_v2_adapter_proof.py"}:
            raise ValueError("Another model workload is active")
    if out.exists():
        raise ValueError("Use a new proof directory")
    info = load_adapter(args.adapter, args.arm, "3b-q4")
    models = verified_models(args.arm, use_selector=False, drafter_model="3b-q4")
    out.mkdir(parents=True)
    cap = min(6_400_000_000, psutil.virtual_memory().available - 1_000_000_000)
    manifest = {"adapter": info, "verified_models": models, "cap_bytes": cap,
                "code_sha256": {name: sha(ROOT / "scripts" / name) for name in
                    (Path(__file__).name, "tier8_v2_run.py", "tier8_v2_adapter_runtime.py", "completion_tokenization.py")}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    peak, breached = 0, False
    start = time.monotonic()
    with (out / "worker.log").open("x") as log, (out / "memory.jsonl").open("x") as memory:
        process = subprocess.Popen([sys.executable, str(Path(__file__)), *sys.argv[1:], "--worker"], cwd=ROOT, stdout=log, stderr=log)
        child = psutil.Process(process.pid)
        while process.poll() is None:
            try:
                rss = psutil.Process().memory_info().rss + sum(p.memory_info().rss for p in [child, *child.children(recursive=True)] if p.is_running())
            except psutil.Error:
                continue
            peak = max(peak, rss)
            memory.write(json.dumps({"time": time.time(), "tree_rss_bytes": rss}) + "\n"); memory.flush()
            if rss > cap:
                breached = True
                process.kill()
                break
            time.sleep(.1)
        code = process.wait()
    proof = out / "proof.json"
    passed = code == 0 and not breached and proof.exists() and json.loads(proof.read_text())["pass"]
    summary = {"status": "complete" if passed else "failed", "exit_code": code,
               "peak_tree_rss_bytes": peak, "cap_bytes": cap, "memory_breached": breached,
               "wall_seconds": time.monotonic() - start, "adapter_effect_proven": bool(passed), "qa_gain_measured": False}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)
    if not passed:raise RuntimeError("Adapter application proof failed; inspect retained logs")


if __name__ == "__main__":
    main()
