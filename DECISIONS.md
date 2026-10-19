# 8 GB tier study decisions

**Study:** `tier8-8gb-v1`  
**SSD:** `H:\AGERE` (`AGERE_SSD_ROOT`)  
**Repo:** `D:\project-agere`  
**Date:** 18 October 2026

This file records choices and blockers for the overnight 8 GB run. It does not replace `DEVELOPMENT_START.md`. Where this file narrows the study, the narrowing is the 8 GB-only scope the user requested.

## Scope

- Only the 8 GB tier.
- SAS: `Qwen2.5-7B-Instruct` GGUF `Q4_K_M`.
- MAS: 1.5B F16 orchestrator/drafter, 0.5B F16 extractor, 0.5B F16 verifier.
- Resident loading is attempted first. If the combined weights do not fit the cap, the team is sequential load/unload and is labeled as such.
- Inference is CPU (`n_gpu_layers=0`). The GPU is only for QLoRA.
- Dev is 150 cases (100 KYC + 50 credit). The frozen test split is KYC 100 + credit 75 and is not opened until `frozen_systems.json` exists.
- Seed 42, temperature 0, one greedy run. Extra seeds would repeat the same outputs.
- FRAMES is a control after the headline, if time remains. MortarBench is not the headline.
- Headline metrics: invention rate (lower is better) and mismatch recall (higher is better), plus grounding and refusal. Scoring is `scripts/phase3.py` through `scripts/tier8_study.py`.
- A hardened change is kept only if dev invention falls or mismatch recall rises and the other does not collapse (`better()` in `scripts/tier8_study.py`).

## RAM cap

The cap is `min(6.4 GB, available RAM minus 1 GB safety)`. It is not raised to force a model to fit.

On 18 October 2026 the host had 16.39 GB total and about 6.7 GB available. The effective cap was about 5.68 GB. Loading `qwen2.5-7b-instruct-q4_k_m.gguf` crossed that cap in about 20 seconds. The runner stopped the process. No dev case was scored. ChatGPT, Spotify, and Cursor were left running.

A later measurement the same night showed 6.8 GB available, so the cap was 5.8 GB. One retry was run. At 6.85 GB available the cap was 5.85 GB. The 7B Q4 load reached 6.40 GB RSS and the runner stopped it. No dev case was scored.

The host was then measured at 7.60 GB available, so the cap was the full nominal ceiling of 6.40 GB. `qwen2.5-7b-instruct-q4_k_m.gguf` was loaded once at context 4096. The resident constructor crossed the cap. The runner then loaded that same single file once more under the sequential path, which is the same load for a one-model arm. That second constructor returned at **6.59 GB** RSS. The process stopped. Context 4096 was not loaded again. ChatGPT, Spotify, and Cursor were not closed. The cap was not raised.

The locked protocol lowers context when the scored workload does not fit. Both arms would have used the same context. With 7.72 GB available the cap stayed 6.40 GB. One load at context **2048** returned at **6,466,244,608 bytes (6.466 GB)**. With 7.85 GB available the cap stayed 6.40 GB. One load at context **1024** returned at **6,407,192,576 bytes (6.407 GB)**. Both are above the 6,400,000,000 byte cap. No lower context was tried. No dev case was scored.

The 1024-token load was 7,192,576 bytes over the cap. That is a compute-buffer fit adjustment, not a cap change. `Llama()` now uses `n_batch=64` and `n_ubatch=64` instead of `n_batch=256`. Context stays 1024. Contexts 4096 and 2048 were not retried. The cap stays 6,400,000,000 bytes. With 7.67 GB available, that one load returned at **6,406,934,528 bytes (6.407 GB)**, still 6,934,528 bytes over the cap. It was not loaded again.

## Packages

Installed into `D:\project-agere\.venv` on 18 October 2026:

- `torch==2.6.0+cu124` from `H:\AGERE\tmp\torch-2.6.0+cu124-cp312-cp312-win_amd64.whl`. CUDA is available on the RTX 4050.
- `transformers==5.20.1`, `peft==0.21.2`, `accelerate==1.15.0`, `bitsandbytes==0.50.2`.

QLoRA was not started. The order runs training only after the naive dev floor exists, and that floor does not exist.

## Result

There is no invention rate and no mismatch recall. The untouched comparison, the fine-tune, the hardened team, and the held-out test did not run.

The 7B Q4 load does not fit the 6.40 GB cap at any locked context. Peaks, one load each:

| Context | Process RSS |
| --- | --- |
| 4096 | 6.59 GB (runner print, two decimal places) |
| 2048 | 6,466,244,608 bytes (6.466 GB) |
| 1024 | 6,407,192,576 bytes (6.407 GB) |

The cap is 6,400,000,000 bytes. These peaks are not scored runs.

One later load kept context 1024 and used `n_batch=64` and `n_ubatch=64`. Process RSS was **6,406,934,528 bytes (6.407 GB)**. That is still over the cap. It is not a scored run.

A fit measurement on the same night found the overrun was Windows counting a memory-mapped weight file on top of a private allocation. With `use_mmap=False` and context 2048, a long prompt stays near **4.92 GB** RSS. The three team models together stayed near **5.31 GB**. The cap was not raised.

Q4_0 KV cache plus flash attention also fit, at 4.83 GB, and a full 150-case naive run was completed under that setting. Every case was invalid JSON. A direct check showed the cause: `2+2` came back as `The023.` with Q4 KV and flash attention, and as `4` with the default F16 KV cache and flash attention off. The F16 setting used **4.92 GB** on a 1,601-token prompt. That 150-case run is not a result. It is stored aside as `dev_invalid_q4kv`. The rerun uses F16 KV, no flash attention, and no memory map.

## Policy corpus

Both hardened arms share the synthetic SOP at `H:\AGERE\datasets\policy\agere-policy-v1\sop.jsonl`. It is original project text. Official SBP wording is not invented. Naive runs still see policy retrieval as unavailable, matching the Phase 3 floor.

## QLoRA

The RTX 4050 has 6 GB of VRAM. The locked sequence length is 2048. If that step does not fit, training uses 512 tokens and the deviation is labeled. The SFT rows are short JSON tasks and are not truncated by 512 in any material way. Training reads only the finetune train and finetune-dev files. The test split is not used.

The scored SAS remains the Q4 GGUF under the RAM cap. A GGUF LoRA is applied only if conversion succeeds. Otherwise the frozen SAS is the base Q4 with the staged prompt, and the adapter status is written as such.

The torch wheel is `H:\AGERE\tmp\torch-2.6.0+cu124-cp312-cp312-win_amd64.whl` (download completed). If `bitsandbytes` fails on Windows, QLoRA is skipped and the comparison continues with the base Q4 file.

## Sequential team

If more than one model is resident and the combined weight files plus the measured 1.72 GB runtime overhead exceed the cap, the team is sequential load/unload and is labeled as such. That path was not reached. The single 7B Q4 model itself exceeded 6.40 GB.

## Runs that break the cap

A run whose peak RSS exceeds the cap is invalid. It is not averaged into the result.
