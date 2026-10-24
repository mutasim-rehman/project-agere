"""Capture actual deployment draft prompts without model calls or mock outcomes.

The capture deliberately stops at the draft call, before verification. Target
programs are training annotations, never supplied to the prompt-building path.
Tokenization is vocab-only; exported rows must pass HF/GGUF parity before SFT.
"""
import argparse
import hashlib
import json

from tier8_v2_financial_pipeline import run_financial
from tier8_v2_run import Models, WEIGHTS
from tier8_v2_sequence import inside
from tier8_v2_adaptation_data import validate_prepared


class DraftCaptured(Exception):
    def __init__(self, role, content, schema, requested):
        super().__init__("draft captured without generation")
        self.role, self.content, self.schema, self.requested = role, content, schema, requested


class CaptureModels:
    context = 4096

    def call(self, role, content, schema, budget, requested, stage):
        if stage != "program":
            raise ValueError("Capture configuration made an unexpected model call")
        raise DraftCaptured(role, content, schema, requested)


def capture(public, arm):
    try:
        run_financial(public, CaptureModels(), arm, "none", representation="reference",
                      unit_mode="question", selector="none", causal_mode="grammar",
                      catalog_style="compact", demonstrations=(), analysis_tokens=0)
    except DraftCaptured as result:
        return {"role": result.role, "content": result.content,
                "prompt": Models.prompt(result.content), "schema": result.schema,
                "requested_output_tokens": result.requested}
    raise ValueError("Pipeline never reached the deployment draft call")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokenized_target(tokenizer, prompt, target, max_length):
    response = json.dumps(target) + "<|im_end|>"
    # Matches _create_completion for the pinned Qwen GGUFs (no automatic BOS/EOS).
    prefix = tokenizer.tokenize(prompt.encode(), add_bos=False, special=True)
    full = tokenizer.tokenize((prompt + response).encode(), add_bos=False, special=True)
    if full[:len(prefix)] != prefix:
        raise ValueError("tokenization_boundary_mismatch")
    if len(full) > max_length:
        raise ValueError("training_length_overflow")
    if len(full) - len(prefix) > 768:
        raise ValueError("target_exceeds_deployment_output_allowance")
    if len(prefix) + 768 + 8 > 4096:
        raise ValueError("deployment_reserve_overflow")
    return {"prompt_tokens": len(prefix), "completion_tokens": len(full) - len(prefix),
            "total_tokens": len(full), "label_mask_prefix_tokens": len(prefix),
            "input_ids_sha256": hashlib.sha256(json.dumps(full).encode()).hexdigest(),
            "response": response}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-length", type=int, choices=(1024, 2048), default=1024)
    args = parser.parse_args()
    base = inside("research/tier8_v2")
    tag = f"deployment-sft-{args.max_length}-02"
    out = base / "data" / f"{tag}.jsonl"
    audit_path = base / "evidence" / f"{tag}.json"
    if out.exists() or audit_path.exists():
        raise ValueError("Use a new corpus; refusing overwrite")
    audit = json.loads((base / "evidence/cell-adaptation-data-02.json").read_text())
    rows, source_hashes = [], {}
    for split, entry in audit["splits"].items():
        path = inside(entry["file"])
        if sha(path) != entry["sha256"]:
            raise ValueError("Adaptation input changed")
        source_hashes[str(path.relative_to(inside(".")))] = sha(path)
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row["split"] != split:
                raise ValueError("Adaptation split mismatch")
            validate_prepared(row)
            draft = capture(row["public"], "mas")
            sas = capture(row["public"], "sas")
            if draft["prompt"] != sas["prompt"] or draft["schema"] != sas["schema"]:
                raise ValueError("SAS/MAS deployment prompt or schema differs")
            rows.append({"source_id": row["source_id"], "report_group": row["report_group"],
                         "split": split, "prompt": draft["prompt"], "target": row["target"],
                         "prompt_sha256": hashlib.sha256(draft["prompt"].encode()).hexdigest(),
                         "schema_sha256": hashlib.sha256(json.dumps(draft["schema"], sort_keys=True).encode()).hexdigest()})
    from llama_cpp import Llama
    profiles = {"mas-3b-q4": "qwen2.5-3b-instruct-q4_k_m.gguf",
                "sas-7b-q4": "qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf"}
    rejected, vocab_profiles = {}, {}
    for profile, filename in profiles.items():
        tokenizer = Llama(model_path=str(WEIGHTS / filename), vocab_only=True, n_ctx=4096,
                          n_gpu_layers=0, use_mmap=True, verbose=False)
        try:
            special_config = {"add_bos": tokenizer._model.add_bos_token(),
                              "add_eos": tokenizer._model.add_eos_token(),
                              "cls": tokenizer._model.token_cls(), "sep": tokenizer._model.token_sep()}
            if special_config["add_bos"] or special_config["add_eos"] or special_config["sep"] != -1:
                raise ValueError("Unsupported completion BOS/EOS policy; inspect runtime before exporting")
            for row in rows:
                try:
                    metadata = tokenized_target(tokenizer, row["prompt"], row["target"], args.max_length)
                    metadata["legacy_manual_prompt_tokens"] = len(tokenizer.tokenize(row["prompt"].encode(), add_bos=True))
                    row.setdefault("tokenization", {})[profile] = metadata
                except ValueError as exc:
                    rejected.setdefault(row["source_id"], {})[profile] = str(exc)
            vocab_profiles[profile] = {"gguf_file": filename, "vocab_only": True,
                                       "n_vocab": tokenizer.n_vocab(), "special_config": special_config}
        finally:
            tokenizer.close()
    kept = [r for r in rows if r["source_id"] not in rejected]
    if not kept or {r["split"] for r in kept} != {"train", "validation"}:
        raise ValueError("Empty training/validation after token fitting")
    with out.open("x") as stream:
        for row in kept:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
    report = {"input_sha256": source_hashes, "max_training_tokens": args.max_length,
              "deployment_context": 4096, "target_budget": 768, "model_calls": 0,
              "tokenization_policy": "add_bos=False, special=True; pinned Qwen no-auto-BOS/EOS/CLS/SEP policy verified against llama-cpp-python completion source",
              "input_n": len(rows), "kept_n": len(kept), "rejected": rejected,
              "split_n": {s: sum(r["split"] == s for r in kept) for s in ("train", "validation")},
              "profiles": vocab_profiles, "output_file": str(out.relative_to(inside("."))), "output_sha256": sha(out),
              "code_sha256": {name: sha(inside("scripts/" + name)) for name in
                   ("tier8_v2_adaptation_prompts.py", "tier8_v2_adaptation_data.py", "evidence_cells.py",
                    "tier8_v2_financial_pipeline.py", "tier8_v2_run.py", "evidence_atoms.py")},
              "configuration": "Actual reference/compact/question-unit/causal deployment draft; no analysis, demos, selector or repair.",
              "limitations": ["Not the stronger 128/256-analysis configuration; evaluate adapted no-analysis arms explicitly.",
                  "Cell metadata is retained in source corpus but absent from this unchanged deployment prompt.",
                  "Teacher reasoning and verifier labels were not synthesized.",
                  "Require exact HF tokenizer parity with recorded input IDs before training.",
                  "No model training, adapter application or measured inference gain yet."]}
    audit_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "rejected"}, indent=2))


if __name__ == "__main__":
    main()
