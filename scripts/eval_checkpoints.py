"""Run paired, resumable checkpoint diagnostics on the frozen synthetic dev tasks.

This is a model-level pre/post-format diagnostic, not the Phase 3 SAS/MAS system
score or the held-out paper evaluation. All run artifacts live on AGERE_SSD_ROOT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from phase2 import (GB, GIB, F16_SIZES_GIB, HardMemoryCap, MemoryMonitor, Paths, REPO, SOURCE_MODELS,
                    TIERS, binary, capture, free_port, kill_tree, request_json,
                    run_logged, runtime_commit, sha256, validate_paths, verify_locked_tiers,
                    write_json, host_reserve, safe_process_cap, require_lab_guard)


DATASET_VERSION = "agere-synth-v1"
PROMPT_VERSION = "checkpoint-dev-json-v1"
TASKS = {"missing_data": 24, "tool_calls": 18, "citations": 18}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fail(message: str) -> None:
    raise RuntimeError(message)


def jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def manifest_entry(path: Path, expected_relative: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    matches = [item for item in data["files"] if item["path"] == expected_relative]
    if len(matches) != 1:
        fail(f"Dataset manifest lacks exactly one entry for {expected_relative}")
    return matches[0]


def dataset_inputs(paths: Paths, limit: int) -> tuple[list[dict], dict]:
    manifest = REPO / "manifests" / "synthetic_datasets.json"
    frozen_test = REPO / "manifests" / "test.sha256"
    if not manifest.is_file() or not frozen_test.is_file():
        fail("Missing committed synthetic dataset or frozen test manifest")
    root = paths.ssd / "datasets" / "agere_synthetic" / DATASET_VERSION
    test_listing = frozen_test.read_text(encoding="utf-8")
    checks = []
    for relative in (f"datasets/agere_synthetic/{DATASET_VERSION}/finetune/dev.jsonl",
                     f"datasets/agere_synthetic/{DATASET_VERSION}/dev/kyc.jsonl",
                     f"datasets/agere_synthetic/{DATASET_VERSION}/dev/credit.jsonl"):
        if relative in test_listing:
            fail(f"Refusing to evaluate a file present in the frozen test manifest: {relative}")
        item = manifest_entry(manifest, relative)
        path = (paths.ssd / relative).resolve(strict=True)
        if not path.is_relative_to(root):
            fail(f"Dev input escapes the SSD dataset root: {path}")
        actual = sha256(path)
        if actual != item["sha256"]:
            fail(f"Dev dataset hash mismatch: {path}")
        checks.append({"path": relative, "sha256": actual, "rows": item["rows"]})
    cases = {}
    for kind in ("kyc", "credit"):
        for case in jsonl(root / "dev" / f"{kind}.jsonl"):
            if case.get("split") != "dev" or not case.get("synthetic_only"):
                fail(f"Non-dev or non-synthetic case encountered: {case.get('id')}")
            if case["id"] in cases:
                fail(f"Duplicate case id: {case['id']}")
            cases[case["id"]] = case
    rows = jsonl(root / "finetune" / "dev.jsonl")
    if len(rows) != 60 or Counter(row["task"] for row in rows) != TASKS:
        fail("The dev task file no longer has the locked 60 rows and 24/18/18 task mix")
    if limit > len(rows):
        fail(f"--limit {limit} exceeds the {len(rows)} dev tasks")
    selected = []
    for row in rows[:limit]:
        case = cases.get(row.get("source_case_id"))
        if case is None or not row.get("synthetic_only"):
            fail(f"Dev task has no valid dev source case: {row.get('id')}")
        selected.append({"row": row, "case": case})
    return selected, {"manifest_sha256": sha256(manifest),
                      "frozen_test_manifest_sha256": sha256(frozen_test),
                      "inputs": checks, "selected_task_ids": [entry["row"]["id"] for entry in selected]}


def prompt_for(row: dict, case: dict) -> str:
    target = json.loads(row["messages"][1]["content"])
    lines = "\n".join(case["case_documents"][0]["lines"])
    calculator = case.get("calculator_inputs")
    addendum = f"\n\nCase documents (authoritative):\n{lines}"
    if calculator:
        addendum += f"\nCalculator inputs: {json.dumps(calculator, sort_keys=True)}"
    return (row["messages"][0]["content"] + addendum +
            "\n\nReturn only one JSON object, with exactly these top-level keys: " +
            ", ".join(target) + ". Use only the case documents and inputs above. "
            "If a fact is missing, use MISSING; never invent a value.")


def score(row: dict, response: str) -> dict:
    target = json.loads(row["messages"][1]["content"])
    raw = response.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.IGNORECASE)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"valid_json": False, "task_success": False, "exact_json": False}
    if not isinstance(parsed, dict):
        return {"valid_json": False, "task_success": False, "exact_json": False}
    task = row["task"]
    if task == "missing_data":
        success = (parsed.get("field") == target["field"] and
                   parsed.get("status") == "MISSING" and parsed.get("value") is None)
    elif task == "tool_calls":
        success = parsed.get("tool") == target["tool"] and parsed.get("arguments") == target["arguments"]
    else:
        citations = parsed.get("citations")
        success = (isinstance(parsed.get("text"), str) and bool(parsed["text"].strip()) and
                   isinstance(citations, list) and any(
                       isinstance(cite, dict) and
                       cite.get("document_id") == target["citations"][0]["document_id"] and
                       cite.get("span_id") == target["citations"][0]["span_id"] and
                       cite.get("quote") == target["citations"][0]["quote"] for cite in citations))
    return {"valid_json": True, "task_success": bool(success), "exact_json": parsed == target}


def variants(tier: str, arm: str) -> list[tuple[str, str, str]]:
    selected = []
    spec = TIERS[tier]
    if arm in ("sas", "both"):
        selected.append((spec["sas"], "sas", "q4_k_m"))
    if arm in ("mas", "both"):
        for _, size in spec["mas"]:
            if not any(entry[0] == size for entry in selected):
                selected.append((size, "mas", "f16"))
    return [(size, mode, kind) for size, mode, kind in selected]


def model_provenance(paths: Paths, size: str, format_name: str, kind: str) -> dict:
    if format_name == "hf":
        manifest = REPO / "manifests" / "hf_snapshots.json"
        entries = [item for item in json.loads(manifest.read_text(encoding="utf-8"))["artifacts"]
                   if item.get("repo_id") == SOURCE_MODELS[size]]
        if not entries or not any(item["path"].endswith(".safetensors") for item in entries):
            fail(f"Missing frozen HF manifest entries for {size}")
        for item in entries:
            path = (paths.ssd / item["path"]).resolve(strict=True)
            if not path.is_relative_to(paths.source(size)) or path.stat().st_size != item["size_bytes"]:
                fail(f"HF input path or size mismatch: {path}")
            if sha256(path, progress=True) != item["sha256"]:
                fail(f"HF input checksum mismatch: {path}")
        return {"format": "hf-f16", "model": SOURCE_MODELS[size],
                "source_revision": entries[0]["revision"],
                "manifest_sha256": sha256(manifest), "files": entries}
    manifest = paths.manifests / "gguf_artifacts.json"
    if not manifest.is_file():
        fail(f"Phase 2 GGUF manifest missing; finish conversion first: {manifest}")
    expected = paths.output(size, kind).relative_to(paths.ssd).as_posix()
    entries = [item for item in json.loads(manifest.read_text(encoding="utf-8"))["artifacts"]
               if item.get("path") == expected]
    if len(entries) != 1:
        fail(f"No Phase 2 GGUF manifest entry for {expected}")
    item = entries[0]
    path = paths.output(size, kind)
    if not path.is_file() or path.stat().st_size != item["size_bytes"] or sha256(path, progress=True) != item["sha256"]:
        fail(f"Phase 2 GGUF checksum mismatch: {path}")
    return {"format": f"gguf-{kind}", "model": SOURCE_MODELS[size],
            "source_revision": item["source_revision"], "file": item,
            "llama_cpp_commit": json.loads(manifest.read_text(encoding="utf-8"))["llama_cpp_commit"]}


def run_directory(paths: Paths, run_id: str, tier: str) -> Path:
    return paths.ssd / "runs" / "checkpoint_diagnostics" / run_id / f"tier{tier}"


def prepare_run(paths: Paths, run_id: str, tier: str, limit: int,
                max_new_tokens: int, context: int) -> Path:
    entries, dataset = dataset_inputs(paths, limit)
    directory = run_directory(paths, run_id, tier)
    directory.mkdir(parents=True, exist_ok=True)
    expected = {"purpose": "dev_checkpoint_diagnostic_not_paper_score",
                "prompt_version": PROMPT_VERSION, "tier_gb": int(tier),
                "limit": limit, "max_new_tokens": max_new_tokens,
                "context_tokens": context, "dataset": dataset,
                "project_commit": capture(["git", "rev-parse", "HEAD"])}
    manifest = directory / "run_manifest.json"
    if manifest.is_file():
        existing = json.loads(manifest.read_text(encoding="utf-8"))
        if {key: existing.get(key) for key in expected} != expected:
            fail(f"Run settings or inputs changed; choose a new --run-id instead of overwriting {manifest}")
    else:
        write_json(manifest, {**expected, "created_at_utc": now(),
                              "test_file_paths_were_not_opened": True})
    print(f"Dev tasks: {len(entries)}; outputs: {directory}", flush=True)
    return directory


def prior_ids(path: Path, expected_ids: list[str]) -> set[str]:
    if not path.exists():
        return set()
    rows = jsonl(path)
    ids = [row.get("task_id") for row in rows]
    if len(ids) != len(set(ids)) or any(item not in expected_ids for item in ids):
        fail(f"Existing output contains duplicate or unexpected task ids: {path}")
    return set(ids)


def hf_infer(paths: Paths, size: str, prompts: list[str], max_new_tokens: int):
    import torch
    import psutil
    from transformers import AutoModelForCausalLM, AutoTokenizer

    source = paths.source(size)
    available = psutil.virtual_memory().available
    required = int((F16_SIZES_GIB[size] + 2) * GIB)
    budget = safe_process_cap(2**63 - 1)
    if required > budget:
        fail(f"Original HF {size} needs roughly {required / GIB:.1f} GiB free host RAM to load safely; "
             f"safe job budget is {budget / GIB:.1f} GiB (host available {available / GIB:.1f}). "
             "HF reference unavailable on this host; use a larger-memory host. GGUF can run separately.")
    tokenizer = AutoTokenizer.from_pretrained(source, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        source, local_files_only=True, torch_dtype=torch.float16,
        device_map="cpu", low_cpu_mem_usage=True)
    model.eval()
    print(f"Loaded original HF F16 {size} on CPU", flush=True)
    try:
        for prompt in prompts:
            inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
            started = time.monotonic()
            with torch.inference_mode():
                output = model.generate(**inputs, do_sample=False,
                                        max_new_tokens=max_new_tokens,
                                        pad_token_id=tokenizer.eos_token_id)
            completion = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:],
                                          skip_special_tokens=True)
            yield completion, time.monotonic() - started, int(output.shape[1] - inputs["input_ids"].shape[1])
    finally:
        del model


def gguf_infer(paths: Paths, tier: str, size: str, kind: str,
               prompts: list[str], max_new_tokens: int, context: int, log: Path):
    import psutil

    runtime_commit(paths)
    idle = psutil.virtual_memory()
    cap = safe_process_cap(int(TIERS[tier]["cap_gb"] * GB))
    if cap <= 0:
        fail("Insufficient host memory after the 1 GB OS reserve")
    port = free_port()
    command = [str(binary(paths, "llama-server")), "--model", str(paths.output(size, kind)),
               "--host", "127.0.0.1", "--port", str(port), "--ctx-size", str(context),
               "--n-gpu-layers", "0", "--fit", "off", "--parallel", "1", "--threads", "4"]
    hard = HardMemoryCap(cap, f"diag-{tier}-{size}")
    monitor = MemoryMonitor(cap, host_reserve())
    process = None
    monitoring = False
    try:
        with log.open("a", encoding="utf-8") as stream:
            stream.write(f"\n[{now()}] command={subprocess.list2cmdline(command)}\n")
            stream.flush()
            process = hard.spawn(command, cwd=REPO, stdout=stream, stderr=subprocess.STDOUT)
            monitor.processes.append(process)
            monitor.start()
            monitoring = True
            deadline = time.monotonic() + 900
            while time.monotonic() < deadline:
                if monitor.breach:
                    fail(monitor.breach)
                if process.poll() is not None:
                    fail(f"llama-server exited while loading; see {log}")
                try:
                    if request_json(f"http://127.0.0.1:{port}/health", timeout=3).get("status") == "ok":
                        break
                except (urllib.error.URLError, TimeoutError, ValueError):
                    pass
                time.sleep(1)
            else:
                fail(f"llama-server load timed out; see {log}")
            print(f"Loaded GGUF {size} ({kind}); cap {cap / GB:.2f} GB", flush=True)
            for prompt in prompts:
                if monitor.breach:
                    fail(monitor.breach)
                started = time.monotonic()
                response = request_json(f"http://127.0.0.1:{port}/completion",
                                        {"prompt": prompt, "n_predict": max_new_tokens,
                                         "temperature": 0.0, "seed": 42,
                                         "stop": ["<|im_end|>"]}, timeout=1800)
                if monitor.breach:
                    fail(monitor.breach)
                yield str(response.get("content", "")), time.monotonic() - started, response.get("tokens_predicted")
    finally:
        if monitoring:
            monitor.stop()
        if process is not None:
            kill_tree(process)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        hard.close()
        write_json(log.with_suffix(".memory.json"), {
            "measured_at_utc": now(), "tier_gb": int(tier), "model_size": size,
            "host_physical_bytes": idle.total, "idle_host_available_bytes": idle.available,
            "effective_process_cap_bytes": cap,
            "os_safety_reserve_bytes": host_reserve(),
            "peak_process_tree_rss_bytes": monitor.peak_rss_bytes,
            "minimum_host_available_bytes": monitor.minimum_host_available_bytes if monitor.samples else None,
            "breach": monitor.breach,
        })


def worker(paths: Paths, args: argparse.Namespace) -> None:
    import psutil

    directory = run_directory(paths, args.run_id, args.tier)
    settings = json.loads((directory / "run_manifest.json").read_text(encoding="utf-8"))
    entries, _ = dataset_inputs(paths, settings["limit"])
    size, kind = args.size, args.kind
    variant = f"{args.format}_{size}" + (f"_{kind}" if args.format == "gguf" else "")
    output = directory / f"{variant}.jsonl"
    provenance = model_provenance(paths, size, args.format, kind)
    provenance_path = directory / f"{variant}.provenance.json"
    if provenance_path.is_file():
        if json.loads(provenance_path.read_text(encoding="utf-8"))["model"] != provenance:
            fail(f"Model provenance changed; use a new --run-id: {provenance_path}")
    else:
        write_json(provenance_path, {"model": provenance, "recorded_at_utc": now()})
    done = prior_ids(output, settings["dataset"]["selected_task_ids"])
    remaining = [entry for entry in entries if entry["row"]["id"] not in done]
    if not remaining:
        print(f"Already complete: {variant} ({len(done)} tasks)", flush=True)
        return
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(paths.source(size), local_files_only=True)
    prompts = [tokenizer.apply_chat_template(
        [{"role": "system", "content": "You are a careful finance data assistant. Output only the requested JSON."},
         {"role": "user", "content": prompt_for(entry["row"], entry["case"])}],
        tokenize=False, add_generation_prompt=True) for entry in remaining]
    if args.format == "hf":
        generator = hf_infer(paths, size, prompts, settings["max_new_tokens"])
    else:
        generator = gguf_infer(paths, args.tier, size, kind, prompts,
                               settings["max_new_tokens"], settings["context_tokens"],
                               directory / "logs" / f"{variant}.server.log")
    output.parent.mkdir(parents=True, exist_ok=True)
    worker_process = psutil.Process()
    with output.open("a", encoding="utf-8", newline="\n") as stream:
        for index, (entry, (response, elapsed, tokens)) in enumerate(zip(remaining, generator, strict=True), 1):
            row = entry["row"]
            record = {"task_id": row["id"], "source_case_id": row["source_case_id"],
                      "task": row["task"], "model_size": size, "format": args.format,
                      "prompt_sha256": hashlib.sha256(prompts[index - 1].encode()).hexdigest(),
                      "response": response, "target": json.loads(row["messages"][1]["content"]),
                      "score": score(row, response), "elapsed_seconds": elapsed,
                      "generated_tokens": tokens,
                      "sampled_worker_rss_bytes": worker_process.memory_info().rss,
                      "sampled_host_available_bytes": psutil.virtual_memory().available,
                      "completed_at_utc": now()}
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
            print(f"{variant}: {len(done) + index}/{settings['limit']} {row['id']} success={record['score']['task_success']} {elapsed:.1f}s", flush=True)


def summarize(directory: Path) -> None:
    settings = json.loads((directory / "run_manifest.json").read_text(encoding="utf-8"))
    results = {}
    for output in sorted(directory.glob("*.jsonl")):
        records = jsonl(output)
        n = len(records)
        if n == 0:
            continue
        results[output.stem] = {
            "completed": n, "expected": settings["limit"],
            "valid_json_rate": sum(row["score"]["valid_json"] for row in records) / n,
            "task_success_rate": sum(row["score"]["task_success"] for row in records) / n,
            "exact_json_rate": sum(row["score"]["exact_json"] for row in records) / n,
            "task_success_by_type": {
                task: {"correct": sum(row["score"]["task_success"] for row in records if row["task"] == task),
                       "total": sum(row["task"] == task for row in records)}
                for task in TASKS},
            "total_generation_seconds": sum(row["elapsed_seconds"] for row in records),
            "output": output.name,
        }
    pairs = {}
    for name, result in results.items():
        if not name.startswith("hf_") or result["completed"] != settings["limit"]:
            continue
        size = name.removeprefix("hf_")
        gguf_name = next((key for key in results if key.startswith(f"gguf_{size}_") and
                          results[key]["completed"] == settings["limit"]), None)
        if gguf_name:
            pairs[size] = {"hf": name, "gguf": gguf_name,
                           "task_success_delta_gguf_minus_hf":
                           results[gguf_name]["task_success_rate"] - result["task_success_rate"]}
    write_json(directory / "summary.json", {
        "generated_at_utc": now(), "purpose": "dev_checkpoint_diagnostic_not_paper_score",
        "tier_gb": settings["tier_gb"], "results": results, "paired_deltas": pairs,
        "warning": "Strict task proxy on synthetic dev SFT rows; not invention rate, not system-level SAS/MAS, and not held-out test accuracy. HF F16 and GGUF Q4 may have different memory feasibility.",
    })
    print(f"Summary: {directory / 'summary.json'}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=("setup", "run", "summarize", "worker"))
    parser.add_argument("--tier", choices=("8", "16", "32", "all"), default="16")
    parser.add_argument("--arm", choices=("sas", "mas", "both"), default="both")
    parser.add_argument("--format", choices=("hf", "gguf", "both"), default="both")
    parser.add_argument("--run-id", default="dev_sft_v1")
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--max-new-tokens", type=int, default=160)
    parser.add_argument("--context", type=int)
    parser.add_argument("--size", choices=SOURCE_MODELS, help=argparse.SUPPRESS)
    parser.add_argument("--kind", choices=("f16", "q4_k_m"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", args.run_id):
        parser.error("--run-id must be a simple name up to 64 characters")
    if args.limit < 1 or args.limit > 60 or args.max_new_tokens < 1 or (args.context is not None and args.context < 512):
        parser.error("limit must be 1–60, max-new-tokens positive, and context at least 512")
    try:
        paths = validate_paths()
        if args.step in ("run", "worker"):
            require_lab_guard()
        verify_locked_tiers()
        if args.step == "setup":
            run_logged([sys.executable, "-m", "pip", "install", "accelerate>=1,<2"],
                       paths.ssd / "runs" / "checkpoint_diagnostics" / "setup.log")
            print("Checkpoint diagnostic dependencies ready", flush=True)
            return 0
        if args.step == "worker":
            if args.tier == "all" or not args.size or not args.kind or args.format == "both":
                fail("Worker requires one tier, size, kind, and format")
            worker(paths, args)
            return 0
        tiers = ("16", "8", "32") if args.tier == "all" else (args.tier,)
        failures = []
        for tier in tiers:
            tier_failures = []
            directory = run_directory(paths, args.run_id, tier)
            if args.step == "summarize":
                summarize(directory)
                continue
            context = args.context or TIERS[tier]["context"]
            prepare_run(paths, args.run_id, tier, args.limit, args.max_new_tokens, context)
            for size, _, kind in variants(tier, args.arm):
                formats = ("gguf", "hf") if args.format == "both" else (args.format,)
                for format_name in formats:
                    command = [sys.executable, str(Path(__file__).resolve()), "worker",
                               "--tier", tier, "--format", format_name, "--run-id", args.run_id,
                               "--size", size, "--kind", kind]
                    log = directory / "logs" / f"{format_name}_{size}_{kind}.log"
                    try:
                        run_logged(command, log, guarded=True)
                    except RuntimeError as exc:
                        failure = {"tier": tier, "size": size, "format": format_name,
                                   "error": str(exc), "log": str(log), "at_utc": now()}
                        failures.append(failure)
                        tier_failures.append(failure)
                        print(f"Variant failed; continuing with the others: {exc}", file=sys.stderr, flush=True)
                    summarize(directory)
            if tier_failures:
                write_json(directory / "failures.json", {"failures": tier_failures})
        return 1 if failures else 0
    except (RuntimeError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        return 1
    except KeyboardInterrupt:
        print("Interrupted; rerun the same command to resume completed dev tasks.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
