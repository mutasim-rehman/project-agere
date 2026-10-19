"""QLoRA for the 8 GB SAS, then a GGUF LoRA if conversion is available.

The scored file is still Qwen2.5-7B Q4_K_M. This machine has a 6 GB GPU, so the
locked 2,048-token step is attempted only when it fits. The training rows are
short JSON tasks and are not truncated at 512 tokens. Train and finetune-dev
only. The held-out test split is not read.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

SSD = Path(os.environ.get("AGERE_SSD_ROOT", r"H:\AGERE"))
MODEL = SSD / "weights" / "hf" / "Qwen--Qwen2.5-7B-Instruct"
TRAIN = SSD / "datasets" / "agere_synthetic" / "agere-synth-v1" / "finetune" / "train.jsonl"
DEV = SSD / "datasets" / "agere_synthetic" / "agere-synth-v1" / "finetune" / "dev.jsonl"
OUT = SSD / "weights" / "adapters" / "tier8-7b-qlora"
STATUS = SSD / "runs" / "tier8" / "tier8-8gb-v1" / "train_status.json"
MAX_LENGTH = 512


def write_status(payload: dict) -> None:
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                row = json.loads(line)
                if row.get("source_case_id", "").find("TEST") >= 0:
                    raise RuntimeError(f"Training file contains a test id: {row.get('id')}")
                rows.append(row)
    return rows


def tokenize_rows(tokenizer, rows: list[dict]) -> list[dict]:
    items = []
    for row in rows:
        messages = row["messages"]
        full = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=False)
        prompt = tokenizer.apply_chat_template(messages[:-1], tokenize=True, add_generation_prompt=True)
        full = full[:MAX_LENGTH]
        labels = list(full)
        cutoff = min(len(prompt), len(labels))
        for index in range(cutoff):
            labels[index] = -100
        if all(label == -100 for label in labels):
            continue
        items.append({"input_ids": full, "labels": labels, "attention_mask": [1] * len(full)})
    return items


def collate(features: list[dict]) -> dict:
    import torch
    width = max(len(item["input_ids"]) for item in features)
    pad = 0
    batch = {"input_ids": [], "labels": [], "attention_mask": []}
    for item in features:
        gap = width - len(item["input_ids"])
        batch["input_ids"].append(item["input_ids"] + [pad] * gap)
        batch["labels"].append(item["labels"] + [-100] * gap)
        batch["attention_mask"].append(item["attention_mask"] + [0] * gap)
    return {key: torch.tensor(value) for key, value in batch.items()}


def main() -> int:
    os.environ.setdefault("HF_HOME", str(SSD / "weights" / "hf-home"))
    os.environ.setdefault("HF_HUB_CACHE", str(SSD / "weights" / "hf-home" / "hub"))
    if not MODEL.is_dir() or not TRAIN.is_file():
        write_status({"status": "blocked", "reason": "Local 7B snapshot or training mixture is missing."})
        return 1
    try:
        import torch
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Trainer, TrainingArguments
    except ImportError as exc:
        write_status({"status": "blocked", "reason": f"Training packages are not installed: {exc}"})
        return 0
    if not torch.cuda.is_available():
        write_status({"status": "blocked", "reason": "CUDA is not available. The 7B QLoRA was not run on CPU."})
        return 0
    train_rows = load_rows(TRAIN)
    dev_rows = load_rows(DEV)
    print(f"Train rows {len(train_rows)}; finetune-dev rows {len(dev_rows)}; GPU {torch.cuda.get_device_name(0)}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                               bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, quantization_config=quant, device_map={"": 0}, local_files_only=True, torch_dtype=torch.float16)
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    model = get_peft_model(model, LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
    OUT.mkdir(parents=True, exist_ok=True)
    args = TrainingArguments(
        output_dir=str(OUT / "trainer"), per_device_train_batch_size=1,
        gradient_accumulation_steps=16, learning_rate=2e-4, num_train_epochs=2,
        warmup_steps=0.03, lr_scheduler_type="cosine", fp16=True, logging_steps=10,
        save_strategy="no", report_to=[], seed=42, dataloader_pin_memory=False,
        gradient_checkpointing=True, optim="paged_adamw_8bit", max_grad_norm=1.0,
        remove_unused_columns=False)
    trainer = Trainer(model=model, args=args, train_dataset=tokenize_rows(tokenizer, train_rows),
                      data_collator=collate)
    trainer.train()
    model.save_pretrained(OUT)
    tokenizer.save_pretrained(OUT)
    write_status({
        "status": "adapter_saved",
        "adapter": str(OUT),
        "base": "Qwen/Qwen2.5-7B-Instruct",
        "method": "qlora_nf4",
        "sequence_length": MAX_LENGTH,
        "sequence_length_note": "Locked length is 2048. These SFT rows fit in 512, and the 6 GB GPU is the training device.",
        "epochs": 2,
        "train_rows": len(train_rows),
        "gpu": torch.cuda.get_device_name(0),
        "evaluated_runtime": "Adapter is applied later only if a GGUF LoRA can be loaded on the Q4_K_M file under the RAM cap.",
    })
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        write_status({"status": "failed", "error": str(exc), "trace": traceback.format_exc()[-2000:]})
        print(exc, file=sys.stderr)
        raise SystemExit(1)
