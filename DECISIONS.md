# 8 GB tier study decisions

## Redevelopment — 24 October 2026

- User authorized iterative code changes, 8 GB research and evaluation, milestone
  commits and pushes, and evidence retention. New files and artifacts stay inside
  this directory; this overrides the historical external-SSD storage convention.
- Preserve the historical runner and results. New code uses separate v2 modules.
- Current checkout has no GGUF weights, no llama-cpp runtime, and no old raw traces.
  Host reports 15.44 decimal GB RAM; 8 GB results here are simulated by a cap.
- Runtime bootstrap initially failed: system Python 3.14 lacks ensurepip. Install
  a project-local Python/runtime instead of changing the host installation.
- Targeted repair, claim verification, and budgeted audits already have prior art
  (Self-Refine, CRITIC, CLR, BRA-Audit). Candidate contribution is transactional
  evidence repair and measured repair-induced regression under tight resources;
  originality and effectiveness remain unproven.
- First milestone isolates deployment checks from gold labels. A supported span
  is not necessarily the correct field value. Missing status needs explicit absence
  evidence. Neither limitation will be hidden by a success metric.
- Credentials from .env are used only for Git authentication; never logged or committed.
- Milestone 1: eight contract tests passed; commit 5db7756 pushed to origin/main.
- Rule-only v1 development baseline scored 150/150 fully correct structured cases,
  including 20 mismatch-positive cases and 51 missing fields, using zero generated
  tokens. Deployment prediction was given neither labels nor calculator_inputs.
  The original scorer was used only after prediction. Per-case evidence and a
  SHA-256 summary are retained under research/tier8_v2/evidence/.
- Consequence: v1 is a regression/smoke suite, not sufficient evidence for a useful
  architecture contribution. Next data must include natural-language, multi-document
  evidence selection, temporal precedence, and conflicts. Retain a rule-only baseline
  and measure template/layout generalization; do not equate synthetic success with
  financial deployment readiness.
- Official pinned Qwen GGUF downloads are used for this reconstruction. Their F16
  files may differ in size from the earlier locally converted weights; hashes and
  actual fit must be recorded before claiming a reproduction of the old runtime.
- Milestone 2 (9bb1262) pushed. New development probes now separate source support
  from semantic correctness: a stale registry value passes lexical support but
  fails gold evaluation. Missing values cite explicit absence statements, rather
  than treating a null citation as proof of absence. This changes the v2 contract;
  the historical v1 scorer is unchanged.
- v2 pilot implements source-visible verifier calls, an actual delivery gate,
  constrained JSON, full/patch/no-repair ablations, and process-tree RSS sampling
  throughout load and generation. The nominal cap includes parent-monitor RSS.
  Patch repairs cannot edit unrelated fact entries. Semantic verification is still
  fallible: a supported-but-wrong claim can be locked, which must be measured.
- The first v2 pilot covers temporal KYC reconciliation only; credit expansion,
  role search, adaptive routing, full paired evaluations, new frozen confirmation,
  and full-paper novelty review remain required work.
- CPU wheel 0.3.19 installed but failed import because its shared object requires
  musl on this glibc host. Preserve install evidence; build 0.3.16 locally instead.
- Milestone 3 (70ec680) pushed. Review then found semantic source roles encoded in
  diagnostic document IDs; replace those with opaque randomized IDs before any
  model evaluation and regenerate the development manifest. No model results exist
  for the earlier probe version.
- Added paired analysis that rejects incomplete, memory-invalid, mismatched-data,
  duplicated-ID and unpaired runs. Sixteen tests now pass across contracts, data,
  delivery gates and paired statistics.
- Full method inspection of BRA-Audit Algorithm 1 confirms localized rollback and
  re-auditing are prior art. Do not claim novelty for those concepts. Keep testing
  field-level transactional preservation, false locks and repair regressions as a
  narrower hypothesis; the publication contribution remains unproven.
- Continued from verified progress: five commits were pushed in the previous goal
  turn. The source-runtime installation and model download processes remain live;
  source cache size and weight partial size have increased. Do not restart them
  solely because installation has not printed a progress line.
- Before pilot runs, enforce per-run weight SHA-256 checks (including both 7B
  shards), reject contradictory PASS verdicts, and reserve 192 output tokens for
  post-repair verification. These controls address evidence validity rather than
  implying a research finding.
- Record verifier confusion and wrong fields left locked, not just repair gains.
  Low repair regression alone is insufficient if the controller preserves incorrect
  fields. These metrics use gold only in the independent analysis after generation.
- Download only FinQA development data plus license/documentation from official
  repository commit 0f16e2867befa6840783e58be38c9efb9229d742. This is supplementary
  public financial-report validation, not a replacement for the KYC/credit scope.
  FinQA's test data remains unopened.
- Add a separately labeled 0.5B primitive diagnostic for runtime/token corruption
  checks. It cannot be counted as SAS-versus-MAS evidence.
- The generator-aware rule control solves all 24 temporal KYC probes. Treat them
  as regression tests, not evidence that an LLM is needed. Do not tune synthetic
  complexity merely to defeat a parser. Public-report tasks and broader independent
  sources are needed to establish practical value.
- FinQA first-24 development slice: non-oracle shared lexical retrieval includes
  all annotated evidence in 19/24 cases, and 34/41 annotated evidence units. Missing
  evidence is a measured retrieval limitation, not automatically a generation error.
- Official small-model GGUF files include larger embeddings than the earlier
  conversions. Prepare reproducible native-F16 conversion with F16 output and
  embedding tensors, preserving original hashes. Native F16 remains unquantized;
  actual resident fit and generation behavior must be measured after conversion.

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

## Naive development floor

Rerun with F16 KV, no flash attention, no memory map, context 2048, seed 42. Both arms stayed under the 6.40 GB cap. This replaces the discarded Q4-KV run.

| Arm | Valid JSON | Invention | Mismatch recall | Grounding | Refusal | Peak RSS |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| SAS 7B Q4 | 100% | 78.0% | 0% | 81.8% | 0% | 5.03 GB |
| MAS resident | 62% | 91.4% | 0% | 37.2% | 0% | 5.53 GB |

Invention is among complete claim sets. The team had 93 complete sets. Failure tags: SAS `S6` on 117 of 150; MAS `M2` 57, `M3` 85, `M7` 8. Neither arm flagged a name mismatch or refused a missing field. The untouched team is worse on invention, grounding, and valid JSON.

## Result

The naive floor above is the untouched comparison. The fine-tune, the hardened team, and the held-out test follow it.

The first QLoRA attempt loaded the 7B on the RTX 4050 and then failed before the first step: installed `transformers` 5.20 takes the 3% warmup as `warmup_steps=0.03`, not `warmup_ratio`. The locked ratio is unchanged. The retry uses that argument.

QLoRA then completed: 600 rows, 2 epochs, sequence length 512, train loss 0.2195, about 4.9 hours on the RTX 4050. The adapter is `H:\AGERE\weights\adapters\tier8-7b-qlora`. It is a PEFT adapter, not a GGUF LoRA, so it is not loaded onto the Q4 file. The scored SAS remains the base Q4_K_M with the staged prompt.

The hardened development run died after writing `CR-DEV-0032` (132 of 150 SAS cases). The process was gone and the case file had not been updated for about an hour. The runner resumes completed case ids, so that run was started again rather than repeated.

The resumed hardened dev run finished. It did not beat the untouched floor.

| Arm | Valid JSON | Invention | Mismatch recall | Grounding |
| :--- | ---: | ---: | ---: | ---: |
| Hardened SAS | 19.3% | 100% of 29 complete sets | 20% | 10.7% |
| Hardened MAS | 0% | none scored | 0% | 0% |

Hardened SAS tags: `S3` 121, `S6` 29. Hardened MAS tag: `M2` on all 150. Valid JSON collapsed, so both repairs are reverted. The frozen systems are the untouched 7B Q4 and the untouched team.

## Held-out test

Pooled Agere-KYC-Synth (100) and Agere-Credit-Synth (75). Seed 42, temperature 0, context 2048, F16 KV, no memory map. Both arms stayed under the 6.40 GB cap.

| Arm | Valid JSON | Invention | Mismatch recall | Grounding | Refusal | Peak RSS |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| SAS 7B Q4 | 100% | 71.4% | 0% | 84.4% | 0% | 5.03 GB |
| MAS resident | 63.4% | 80.2% | 0% | 36.3% | 0% | 5.54 GB |

Invention is lower-better, among complete claim sets. The team had 111 complete sets. SAS tags: `S6` on 125 of 175. MAS tags: `M2` 64, `M3` 89, `M7` 22. The single quantized model invented less and grounded more. Neither arm caught a planted name mismatch or refused a missing field.

FRAMES closed-book control, 100 questions: SAS exact match 1%, MAS exact match 2%. That small team edge does not override the KYC and credit invention result.

The 8 GB study is complete. The QLoRA adapter remains on disk and was not part of this scored comparison.

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
