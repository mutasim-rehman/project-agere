"""Train-only QLoRA baseline with exact deployment tokens and applied-weight proof.

`fit` performs two real updates on the longest training sequence, exercising
optimizer state as well as forward/backward memory. It is not a trained-system
result. `train` uses one epoch, grouped accumulation, and train-only validation.
All model work refuses to overlap the frozen CPU inference sequence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time

from supervised_logits import supervised_window

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def encode_example(tokenizer, row, profile):
    expected = row["tokenization"][profile]
    full = tokenizer.encode(row["prompt"] + expected["response"], add_special_tokens=False)
    prefix = tokenizer.encode(row["prompt"], add_special_tokens=False)
    if hashlib.sha256(json.dumps(full).encode()).hexdigest() != expected["input_ids_sha256"]:
        raise ValueError("Training tokenizer differs from deployment IDs")
    if full[:len(prefix)] != prefix or len(prefix) != expected["label_mask_prefix_tokens"] or len(full) > 1024 or len(full) <= len(prefix):
        raise ValueError("Invalid token boundary/length for labels")
    return {"input_ids": full, "labels": [-100] * len(prefix) + full[len(prefix):],
            "source_id": row["source_id"], "split": row["split"]}


def guard_no_inference():
    import psutil
    names = {"tier8_v2_run.py", "tier8_v2_replay.py", "tier8_v2_adapt.py"}
    for process in psutil.process_iter(["pid", "cmdline"]):
        if process.pid != os.getpid() and any(Path(x).name in names for x in (process.info["cmdline"] or [])):
            raise ValueError(f"Another inference/training process is active: {process.pid}")
    from tier8_v2_sequence import require_complete
    require_complete("research/tier8_v2/runs/finqa-sas-analysis256-dev24-01")
    journal = ROOT / "research/tier8_v2/logs/analysis256-sequence-01.jsonl"
    if json.loads(journal.read_text().splitlines()[-1])["state"] != "complete":
        raise ValueError("Frozen CPU sequence has not completed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("3b", "7b"), default="3b")
    parser.add_argument("--mode", choices=("fit", "train"), required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        raise ValueError("Require a new output directory inside the project")
    guard_no_inference()
    for key, value in {"HF_HOME": ".local/hf-training", "HF_HUB_CACHE": ".local/hf-training/hub",
                       "TRITON_CACHE_DIR": ".local/triton-cache", "CUDA_CACHE_PATH": ".local/cuda-cache",
                       "TORCHINDUCTOR_CACHE_DIR": ".local/torchinductor-cache", "TMPDIR": ".local/tmp"}.items():
        os.environ[key] = str(ROOT / value)
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", TOKENIZERS_PARALLELISM="false")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import torch
    import peft
    import transformers
    import bitsandbytes
    import psutil
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise ValueError("CUDA BF16 training is unavailable")
    torch.set_num_threads(2)
    random.seed(42)
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    base = ROOT / "research/tier8_v2"
    parity_path = base / "evidence/hf-tokenizer-parity-02.json"
    parity = json.loads(parity_path.read_text())
    if not parity["pass"] or parity["transformers_version"] != transformers.__version__:
        raise ValueError("Successful parity under the current tokenizer runtime required")
    data_manifest_path = base / "evidence/deployment-sft-1024-02.json"
    data_manifest = json.loads(data_manifest_path.read_text())
    data_path = (ROOT / data_manifest["output_file"]).resolve()
    if not data_path.is_relative_to(ROOT) or sha(data_path) != data_manifest["output_sha256"] or sha(data_path) != parity["dataset_sha256"]:
        raise ValueError("Training corpus identity differs")
    training_base_path = base / "evidence" / f"training-base-{args.profile}-01.json"
    training_base = json.loads(training_base_path.read_text())
    folder = (ROOT / training_base["folder"]).resolve()
    if not folder.is_relative_to(ROOT) or not training_base["weights_verified"] or sha(folder / training_base["weight_file"]) != training_base["sha256"]:
        raise ValueError("Pinned training base is not verified")
    for file in training_base["config_files"]:
        if sha(folder / file["file"]) != file["sha256"]:
            raise ValueError("Training model config changed")
    profile = "mas-3b-q4" if args.profile == "3b" else "sas-7b-q4"
    tokenizer_folder = ROOT / "weights/hf-tokenizers" / profile
    from tier8_v2_adapter_convert import check_architecture
    check_architecture(json.loads((folder / "config.json").read_text()),
                       json.loads((tokenizer_folder / "config.json").read_text()))
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_folder), local_files_only=True, trust_remote_code=False)
    rows = [json.loads(line) for line in data_path.read_text().splitlines()]
    examples = [encode_example(tokenizer, row, profile) for row in rows]
    training = [r for r in examples if r["split"] == "train"]
    validation = [r for r in examples if r["split"] == "validation"]
    if len(training) != 661 or len(validation) != 100:
        raise ValueError("Training corpus/split changed")
    out.mkdir(parents=True)
    def event(state, **fields):
        with (out / "events.jsonl").open("a") as stream:
            stream.write(json.dumps({"state": state, "time": time.time(), **fields}) + "\n")
            stream.flush()
    manifest = {"mode": args.mode, "profile": args.profile, "seed": 42,
        "input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in
                         (parity_path, data_manifest_path, data_path, training_base_path)},
        "script_sha256": sha(Path(__file__)), "training_base": training_base,
        "lora": {"r": 8, "lora_alpha": 16, "lora_dropout": .05, "target_modules": "all-linear"},
        "optimizer": "AdamW lr=2e-4 weight_decay=0; clip_norm=1; accumulation=8; one epoch",
        "runtime": {"torch": torch.__version__, "transformers": transformers.__version__,
                    "peft": peft.__version__, "bitsandbytes": bitsandbytes.__version__},
        "gpu": {"name": torch.cuda.get_device_name(), "total_bytes": torch.cuda.get_device_properties(0).total_memory},
        "training_n": len(training), "validation_n": len(validation),
        "loss_policy": "Complete input; logits/shifted labels only for last prefix position plus all supervised target tokens",
        "loss_helper_sha256": sha(ROOT / "scripts/supervised_logits.py"),
        "cuda_allocator_policy": os.environ["PYTORCH_CUDA_ALLOC_CONF"],
        "scope": "Adaptation baseline; training resource use is separate from the 8 GB deployment study. No novelty claim."}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    model = None
    started = time.monotonic()
    try:
        event("loading")
        torch.cuda.reset_peak_memory_stats()
        model = AutoModelForCausalLM.from_pretrained(str(folder), local_files_only=True,
            trust_remote_code=False, use_safetensors=True, device_map={"": 0},
            torch_dtype=torch.bfloat16, attn_implementation="sdpa")
        model.config.use_cache = False
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
            gradient_checkpointing_kwargs={"use_reentrant": False})
        model = get_peft_model(model, LoraConfig(**manifest["lora"], bias="none", task_type="CAUSAL_LM"))
        trainable = [(name, p) for name, p in model.named_parameters() if p.requires_grad]
        if any("lora_" not in name for name, _ in trainable):
            raise ValueError("Unexpected trainable base-model parameter")
        params = [p for _, p in trainable]
        if not params or any(not torch.isfinite(p).all().item() for p in params):
            raise ValueError("Invalid trainable adapter parameters")
        before = [p.detach().cpu().clone() for p in params]
        optimizer = torch.optim.AdamW(params, lr=2e-4, weight_decay=0)
        model.train()
        def batch(row):
            window = supervised_window(row)
            return {"input_ids": torch.tensor([window["input_ids"]], dtype=torch.long, device="cuda"),
                    "labels": torch.tensor([window["labels"]], dtype=torch.long, device="cuda"),
                    "logits_to_keep": window["logits_to_keep"]}
        if args.mode == "fit":
            longest = max(training, key=lambda r: (len(r["input_ids"]), r["source_id"]))
            groups = [[longest], [longest]]
            event("fit_case", source_id=longest["source_id"], tokens=len(longest["input_ids"]))
        else:
            random.Random(42).shuffle(training)
            groups = [training[i:i + 8] for i in range(0, len(training), 8)]
        losses = []
        for step, group in enumerate(groups, 1):
            optimizer.zero_grad(set_to_none=True)
            group_loss = 0
            for row in group:
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    loss = model(**batch(row)).loss
                if not torch.isfinite(loss).item():
                    raise ValueError("Nonfinite training loss")
                group_loss += loss.detach().item() / len(group)
                (loss / len(group)).backward()
            gradient_norm = torch.nn.utils.clip_grad_norm_(params, 1.0)
            if not torch.isfinite(gradient_norm).item() or gradient_norm.item() <= 0:
                raise ValueError("No finite nonzero adapter gradient")
            optimizer.step()
            losses.append(group_loss)
            event("update", step=step, examples=len(group), loss=group_loss,
                  gradient_norm=gradient_norm.item(), gpu_peak_allocated=torch.cuda.max_memory_allocated(),
                  gpu_peak_reserved=torch.cuda.max_memory_reserved(), host_rss=psutil.Process().memory_info().rss)
        changed = sum(not torch.equal(old, new.detach().cpu()) for old, new in zip(before, params))
        if not changed:
            raise ValueError("Optimizer did not change adapter tensors")
        model.save_pretrained(str(out / "adapter"), safe_serialization=True)
        validation_loss = None
        if args.mode == "train":
            model.eval()
            measured = []
            with torch.no_grad():
                for row in validation:
                    with torch.autocast("cuda", dtype=torch.bfloat16):
                        measured.append(model(**batch(row)).loss.item())
            validation_loss = sum(measured) / len(measured)
        result = {"status": "complete", "mode": args.mode, "optimizer_updates": len(groups),
            "examples_processed": sum(map(len, groups)), "changed_adapter_tensors": changed,
            "trainable_parameters": sum(p.numel() for p in params), "last_training_loss": losses[-1],
            "validation_teacher_forced_loss": validation_loss, "wall_seconds": time.monotonic() - started,
            "gpu_peak_allocated": torch.cuda.max_memory_allocated(), "gpu_peak_reserved": torch.cuda.max_memory_reserved(),
            "adapter_files": {p.name: sha(p) for p in (out / "adapter").iterdir() if p.is_file()},
            "deployment_adapter_applied": False, "measured_reasoning_gain": False}
        (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
        event("complete", **result)
    except Exception as exc:
        result = {"status": "failed", "error": type(exc).__name__, "reason": str(exc),
                  "wall_seconds": time.monotonic() - started, "model_training_result_valid": False}
        (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
        event("failed", **result)
        raise


if __name__ == "__main__":
    main()
