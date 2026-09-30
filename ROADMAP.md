# Build roadmap

> Ubuntu lab update: Phase 2 is still incomplete. The September 30 runs stopped during 1.5B conversion after source verification. Use the bounded launcher for Phase 2, checkpoint diagnostics, and Phase 3. See [lab recovery and commands](LAB_RECOVERY.md). Its default 4 GiB host reserve and whole-job cap may lower the nominal tier budgets further.

**Project:** Agere  
**Use this file to drive an agent one stage at a time.**  
Decisions (which model, which quant, which test set) stay in [`DEVELOPMENT_START.md`](./DEVELOPMENT_START.md). This file is only the order of work.

**Co-equal outcomes:** this roadmap delivers both a reproducible research result and a working local-first analyst product. Each phase has a research deliverable and a product deliverable; neither track is complete if only the other is usable.

**Storage rule from Phase 2 onward:** code, tools, Python environments, and runtime builds stay in the repository checkout on the laptop/PC/lab machine. The external SSD holds datasets, model artifacts, logs, manifests, evaluation outputs, and reports. The existing Phase 0/1 manifests in git remain as input records; new run products go to the SSD. Before every phase or run, set and validate the actual external-drive path in `AGERE_SSD_ROOT`; never assume a path or fall back to another drive.

Start at **Phase 0**. Finish a phase before opening the next one. The **16 GB** tier is the primary research comparison. Phase 2 prepares and smoke checks all three tiers; Phase 3 records untouched dev floors for all three tiers on the lab PC. The held-out 8 GB and 32 GB comparisons remain in Phase 8 after the 16 GB system is frozen.

## How to hand a phase to an agent

Paste this, with the phase number filled in:

> Do **only Phase N** of [`ROADMAP.md`](./ROADMAP.md). Follow [`DEVELOPMENT_START.md`](./DEVELOPMENT_START.md) for models, quantization, and data. Stop when that phase’s “Done when” is true. Do not start the next phase.

## Order

| Phase | What happens | Where the files go |
| :---: | :--- | :--- |
| **0** | Validate SSD path, repository checkout, llama.cpp, 16 GB physical tier / 12.8 GB nominal job cap | Historical manifests in repo; datasets/weights on SSD |
| **1** | Download the 16 GB models | External SSD |
| **2** | Convert and smoke all three tiers' GGUF files | External SSD |
| **3** | Score the **untouched** single model and team at all three tiers | Dev cases only |
| **4** | Fine-tune the single model, merge, quantize **again** | Code on host; adapters, weights, logs, results on SSD |
| **5** | Build the real multi-agent team (JSON, verifier, budget) | Code |
| **6** | Final evaluation, once | Test cases |
| **7** | Loop: tag failures, change one thing on dev, or ablate | Dev cases |
| **8** | Score the 8 GB and 32 GB tier comparisons | After Phase 6 |

Fine-tuning is **after** the untouched scores are frozen. The team is scored once in its simple form in Phase 3, then rebuilt in Phase 5. Phase 6 does not get a second look.

```
0 SSD → 1 Download → 2 Quantize → 3 Score untouched SAS, then untouched MAS
                                      ↓
                               7 Loop on dev ← 4 Fine-tune SAS → 5 Harden MAS
                                      ↓
                               6 Final test (once) → 8 Other RAM tiers
```

---

## Phase 0 — SSD and runtime

**Goal:** Every job uses an explicitly supplied external SSD path. Code and build tools run from the computer; phase outputs travel with the SSD.

**Steps**

0.1 Mount the external NVMe and set `AGERE_SSD_ROOT` to its actual absolute mount path for this machine (for example `/mnt/AGERE` on Linux or the assigned drive path on Windows). Do not hard-code an assumed drive letter or mount point. The volume label is `AGERE`.

0.2 Keep this layout on the external SSD. Source code and runtime binaries stay on the computer. Phase outputs, including logs and manifests, are stored on the SSD.

```
AGERE_SSD_ROOT/
  weights/
    hf/                 # original model snapshots
    gguf/               # converted and quantized model weights
    adapters/           # trained adapters and merged model weights
  datasets/
    train/
    dev/
    test/               # immutable after the test manifest is committed
    derived/            # dataset-derived indexes/caches only
  phase2/               # Phase 2 logs, manifests, smoke results, summary
  runs/                 # later evaluation and training logs
  results/              # later reports and figures
```

0.3 Keep the repository checkout, llama.cpp source/build, and all dependencies on the laptop/PC/lab machine. Record Phase 2 runtime versions on the SSD at `phase2/manifests/runtime.json`. Inference is CPU. A GPU is for fine-tuning only.

0.4 Before starting **every phase or run**, supply the current machine's correct `AGERE_SSD_ROOT`. The runner must print the resolved repo root and SSD root, validate that the SSD is mounted and contains the required input directories, and refuse to start if the variable is missing, stale, or invalid. Set model-hub/cache paths (including `HF_HOME`/`HF_HUB_CACHE`) beneath `$AGERE_SSD_ROOT/weights/` so large model downloads never default to the local disk. Never silently substitute a local path.

0.5 **Stage datasets before evaluation or training.** On Windows, set `$env:AGERE_SSD_ROOT='H:\AGERE'` (or the current machine's actual mount), then run `scripts\download_project_datasets.ps1` and `scripts\prepare_project_datasets.py`. The downloader puts the pinned MortarBench snapshot and the Google FRAMES source TSV under `datasets/external/`; the preparation script writes Agere-KYC-Synth (400/100/100), Agere-Credit-Synth (200/50/75), the 600-example QLoRA train mixture, its 60-example dev set, and a deterministic 100-question FRAMES slice under `datasets/`. The existing Phase 0 dataset metadata and held-out SHA-256 manifest were written under repository `manifests/` and remain frozen there as input records.

**Data-quality gate:** `agere-synth-v1` is a deterministic synthetic starter corpus generated from fabricated records, not a validated research benchmark. Phase 3 may record a clearly labelled **provisional dev floor** on it, but before paper-grade Phase 3 claims or Phase 4 training, inspect and improve case diversity, labels, source evidence, financial edge cases, and KYC policy coverage; record the reviewed dataset version and freeze its tests. The 600 SFT rows are project-generated, not a publicly downloadable corpus. MortarBench is a secondary official benchmark; FRAMES is only the 100-question negative-control slice. The SBP/FATF policy corpus and synthetic bank SOP still need to be acquired/created and versioned before the retriever can be evaluated.

0.6 From Phase 2 onward, write manifests, logs, traces, metrics, evaluation outputs, and reports beneath `AGERE_SSD_ROOT`. Nominal aggregate process-tree RSS caps are 6.4 / 12.8 / 25.6 GB for the 8 / 16 / 32 GB tiers. Lower them for measured host use and runner overhead. On Ubuntu, use `scripts/lab_run.py`, whose default outer-service headroom reserves 4 GiB for the host, 1 GiB for launch variation, and 1 GiB for its control process, and whose evaluations retain another 0.5 GiB fluctuation margin. See `LAB_RECOVERY.md` for attached-SSD incident evidence, commands, and diagnostics. Never raise a cap to force a model to fit.

**Do not:** Download models. Write training code.

**Done when:** A process exits with a clear error if `AGERE_SSD_ROOT` is missing or incorrect; it reports the resolved paths; subsequent smoke runs write logs on the SSD; and the effective RSS cap plus host-wide memory monitor preserve the OS/background reserve.

---

## Phase 1 — Download models onto the SSD

**Goal:** The 16 GB checkpoints are on the SSD, their hashes are recorded in the repository, and weights are not in git.

**Status: Complete (2026-09-29).** Five pinned snapshots totaling about 37.3 GiB are stored under `H:\AGERE\weights\hf\`; all 49 model/tokenizer files passed SHA-256 verification against the repository manifests. The 7B and 32B source snapshots were staged on 2026-09-30 (35 files, 75.2 GiB) and recorded with SHA-256 in the same manifests; their conversion is part of Phase 2.

**Steps**

1.1 Before downloading, set and validate this machine's `AGERE_SSD_ROOT`. Install the downloader dependency on the computer (not the SSD) with `python -m pip install -r requirements-phase1.txt`, then run `python scripts/download_hf_snapshots.py`. The downloader pins each snapshot to its resolved Hub revision, preflights available space, resumes partial files, and writes only model/tokenizer assets under `$AGERE_SSD_ROOT/weights/hf/`:

To stage the 8 GB and 32 GB tier sources early as well, run `python scripts/download_hf_snapshots.py --include-tier-checkpoints`. This adds the 7B and 32B snapshots and reports file-level transfer progress. It still writes only to the SSD weights directory; SHA-256 manifests are written in the repository.

| Role | Hugging Face id |
| :--- | :--- |
| Single model (SAS) | `Qwen/Qwen2.5-14B-Instruct` |
| Orchestrator and drafter | `Qwen/Qwen2.5-3B-Instruct` |
| Extractor | `Qwen/Qwen2.5-1.5B-Instruct` |
| Verifier | `Qwen/Qwen2.5-0.5B-Instruct` |
| Retriever | `BAAI/bge-small-en-v1.5` |

1.2 Write a SHA-256 line for each snapshot to the repository's `manifests/weights.sha256` before any config points at the files. Include the SSD-relative artifact path and checksum.

1.3 The 7B and 32B checkpoints are required for the 8 GB and 32 GB tiers. Stage their source snapshots by adding `--include-tier-checkpoints` to the download command. Phase 2 converts, quantizes, and smoke checks all three tiers; Phase 3 runs their provisional dev floors; Phase 8 runs the later held-out 8 GB and 32 GB comparisons. The 0.5B checkpoint is shared across all three teams.

**Do not:** Quantize yet. Download Llama. Commit weights.

**Done when:** All five snapshots load from `AGERE_SSD_ROOT`, their immutable Hub revisions and per-file SHA-256 hashes are recorded in repository manifests, and every recorded hash matches a recompute.

---

## Phase 2 — Convert, quantize, and smoke all tiers

**Goal:** Runnable GGUF files for all three tiers' untouched baselines. Each SAS is Q4_K_M and every MAS model instance stays F16. This preparation does not score datasets.

**Lab PC runbook:** [`PHASE_2_LAB_RUN.md`](./PHASE_2_LAB_RUN.md) gives the exact commands. The runner pins llama.cpp `v0.5.0`, checks the Phase 1 source hashes, converts with CPU tools, and puts every Phase 2 output and log on the mounted SSD. It prints the resolved SSD and repository paths on every invocation.

- **SSD space:** Budget about **123 GiB** peak additional space across all tiers and keep at least **133 GiB free** before a fresh conversion, including 10 GiB safety room. The 14B and 32B F16 intermediates are deleted after each Q4 checksum. The runner computes a smaller remaining requirement when resuming. The last check on the development SSD found 149.4 GiB free, so this is feasible but leaves limited margin for unrelated files.
- **Local PC space:** Keep the repository checkout, Python environment, llama.cpp source/build, and installed packages on the lab PC. Its memory and available local disk must be checked there; the development laptop's earlier measurements do not describe the lab PC.
- **RAM:** Before each smoke arm, measure the lab PC's idle OS/background use. Cap the aggregate model process tree at the lower of that tier's nominal **6.4 / 12.8 / 25.6 GB** cap and the host's available memory minus its configured safety reserve and runtime headroom. Monitor host-wide available memory while the arm is loaded. On Ubuntu, use the bounded launcher in `LAB_RECOVERY.md`. Never raise the cap to force a model to fit.
- **Elapsed time:** Conversion and quantization may take hours; the exact time depends on the lab PC CPU and SSD throughput. The per-step SSD logs and session log show progress and any failure.

**Steps**

2.1 Convert the 7B, 3B, 1.5B, and 0.5B Qwen snapshots to GGUF **F16**. The 7B F16 file is retained for the 32 GB team.

2.2 Convert 14B and 32B to temporary F16 GGUF, then quantize 7B, 14B, and 32B to **Q4_K_M**. Keep 7B F16 for the 32 GB team. Delete the 14B and 32B F16 intermediates only after each Q4 checksum is recorded. Do not produce Q3, Q2, or AWQ for the headline.

2.3 Save all seven final GGUF files under `AGERE_SSD_ROOT/weights/gguf/`: Q4_K_M for 7B, 14B, and 32B; F16 for 0.5B, 1.5B, 3B, and 7B. Hash each file into `AGERE_SSD_ROOT/phase2/manifests/weights.sha256` and `gguf_artifacts.json`.

2.4 Smoke-load each tier's SAS Q4_K_M under its effective process cap and generate a few tokens. Record process-tree peak RSS, host-wide available memory, idle baseline, effective cap, and llama.cpp version in `AGERE_SSD_ROOT/phase2/runs/smoke_sas_<tier>gb.json`.

2.5 Smoke-load each tier's three MAS model **instances together** (resident), including two distinct 0.5B instances on the 8 GB tier. Record the same memory fields in `AGERE_SSD_ROOT/phase2/runs/smoke_mas_<tier>gb.json`. If the effective cap is exceeded, lower context or shrink the smallest worker first; do not raise the cap. Record the actual context so later scoring uses the same configuration.

**Do not:** Fine-tune. Score a dataset. Turn the team into a fourth model.

**Done when:** All six SSD smoke JSON files report `passed`, SAS and MAS use the same context within each tier, every process-tree peak is within its effective cap with OS/background headroom intact, all seven final GGUF hashes are recorded on the SSD, and `AGERE_SSD_ROOT/phase2/phase2_summary.json` reports `complete`.

**Optional checkpoint diagnostic after conversion:** [`CHECKPOINT_EVAL_LAB_RUN.md`](./CHECKPOINT_EVAL_LAB_RUN.md) compares each original HF checkpoint with its Phase 2 GGUF output on the synthetic **dev** tasks and stores every result under `AGERE_SSD_ROOT/runs/checkpoint_diagnostics/`. This is a format/quantization progress check, not the Phase 3 system floor or the held-out Phase 6 evaluation. It does not change the locked phase order or consume the test split.

---

## Phase 3 — Score the untouched models

**Goal:** A separate untouched Q4 SAS versus simple resident F16 MAS floor for **each** 8 GB, 16 GB, and 32 GB tier, on **dev** only. The 16 GB tier remains the preregistered primary comparison.

**Lab PC runbook:** [`PHASE_3_LAB_RUN.md`](./PHASE_3_LAB_RUN.md) gives the all-tier CLI. The runner verifies the Phase 2 GGUF hashes and smoke contexts, checks the committed dev dataset hashes, copies frozen test filenames and hashes into the SSD run manifest without reading those test files, and writes every trace, log, summary, and model-memory record to the SSD. It resumes completed cases.

**Steps**

3.1 Check the frozen test-set manifest (`manifests/test.sha256` from Phase 0); copy its names and SHA-256 values into the SSD run manifest before training or scoring. Dataset files remain on the SSD. Anything in that manifest is off limits here.

3.2 Implement the four tools, same schemas for both arms: `document_extractor`, `policy_retriever`, `financial_calculator`, `citation_verifier`. Amounts come from the calculator. The citation tool is a string match.

3.3 Implement the scorer: invention rate, mismatch recall, grounding accuracy, refusal correctness. Tag each failed case with one id from [`configs/locked/problems.yaml`](./configs/locked/problems.yaml).

3.4 Run **untouched SAS** in each tier: 7B, 14B, or 32B Q4_K_M, no adapter, 2,048 generated-token ceiling, the same tool packet, and the tier's host-adjusted process cap. Score the **dev** slices of Agere-KYC-Synth and Agere-Credit-Synth read from `AGERE_SSD_ROOT`. Save outputs under `AGERE_SSD_ROOT/runs/phase3/<run-id>/tier<tier>/naive_sas/`.

3.5 Run each tier's three locked **untouched MAS** instances, all F16 and resident, under the same effective cap, cases, 2,048-token ceiling, and deterministic tools as SAS. One forward pass per extractor, drafter, and verifier; no debate, verifier gate, or LoRA. Save outputs under `AGERE_SSD_ROOT/runs/phase3/<run-id>/tier<tier>/naive_mas/`.

3.6 Write one immutable `AGERE_SSD_ROOT/runs/phase3/<run-id>/tier<tier>/naive_floor.json` per tier only when both arms finish all 150 dev cases within the cap. Do not edit a floor after it is written. An all-tier summary lives at `AGERE_SSD_ROOT/runs/phase3/<run-id>/all_tiers_summary.json`.

The staged synthetic corpus has not passed the data-quality gate in Phase 0, and the versioned policy index is not staged. The Phase 3 runner marks these floors **provisional**, reports policy retrieval as `UNAVAILABLE`, and labels its invention metric as structured-claim only. Do not present this output as a complete policy-grounded paper result until those inputs and a human review of free-text drafts are added.

**Do not:** Call the test split. Start QLoRA. Add a verifier gate and then call the result “naive”.

**Done when:** All three tier floors contain both arms, every run log has generated tokens and peak RSS, all caps and OS reserves were preserved, and no test file was opened. The scientific Phase 3 gate additionally requires the dataset-quality and policy-corpus limitations above to be resolved or explicitly reported.

---

## Phase 4 — Fine-tune, then quantize again

**Goal:** A domain-adapted single model that still fits the effective 16 GB-tier process cap as Q4_K_M, with OS/background headroom preserved.

**Steps**

4.1 Build the training mixture from **train** only: 40% missing-field refusal, 30% tool calls, 30% span citations. Hyperparameters are [`configs/locked/finetune.yaml`](./configs/locked/finetune.yaml): QLoRA NF4, rank 16, alpha 32, dropout 0.05, 8-bit AdamW, learning rate `2e-4`. Stop on **dev invention rate**, not on training loss.

4.2 GPU: ≥24 GB VRAM for the 14B. If that GPU does not exist, fine-tune a **7B** stand-in and label every run `7b-stand-in`. The untouched 14B Q4 from Phase 3 still stays in the table.

4.3 Merge the adapter into 16-bit weights. Save the merged and converted/quantized weight artifacts on the SSD under `weights/`; hash each artifact in an SSD manifest. The merged 16-bit model is not what gets scored.

4.4 Smoke-test process-tree RSS and host-wide available memory under the effective 16 GB-tier cap. Save both to the SSD run log.

4.5 Score it on **dev**. Keep the adapter only if dev invention rate or mismatch recall improves and the other does not collapse. Otherwise discard it from the SSD and record that in the SSD run log.

**Do not:** Train on test. Compare against the team yet. Replace `naive_floor.json`.

**Done when:** The evaluated file on the SSD is a hashed Q4_K_M within the effective 16 GB-tier process cap, OS/background headroom is intact, and the dev delta is written to `AGERE_SSD_ROOT/runs/sas_qlora_dev.json`.

---

## Phase 5 — Multi-agent system

**Goal:** The team that will be compared, still three F16 models, with the failure fixes that are P0.

**Steps**

5.1 Stage list is code, in this order: extractor → retriever → drafter → verifier. The drafter is the 3B checkpoint, not a fourth model. The retriever is `bge-small`.

5.2 JSON only between stages. `MISSING` is a real value. Workers are stateless; reattach the constraint packet on every call.

5.3 Verifier does a deterministic span match. `PASS` requires every amount to match a span. At most one repair if it fails. No debate.

5.4 Token split of the 2,048 cap: extractor 30%, retriever 10%, drafter 40%, verifier 20%. Reserve the verifier share first.

5.5 Optional role LoRAs (extractor, drafter, verifier) only if a 12 GB-class GPU exists. Keep one only if **dev** invention rate or mismatch recall improves. Otherwise ship the base F16 file.

5.6 Score the hardened team on **dev**. This is one engineering pass. Each arm gets at most three passes total (Phase 7).

**Do not:** Quantize the team. Add a second 3B. Touch the test split.

**Done when:** A dev run finishes resident within the effective 16 GB-tier cap, preserves OS/background headroom, writes one JSON line per stage (tokens, RSS, gap id) to the SSD, and `AGERE_SSD_ROOT/runs/mas_hardened_dev.json` records the delta versus the naive MAS floor.

---

## Phase 6 — Final evaluation

**Goal:** The number that goes in the paper. One shot per frozen system.

**Steps**

6.1 Confirm both arms are frozen: naive floors exist, dev metrics exist, and the P0 items in [`SYSTEM_GAPS_AND_IMPROVEMENTS.md`](./SYSTEM_GAPS_AND_IMPROVEMENTS.md) §5 were attempted or explicitly skipped with a reason.

6.2 Run hardened SAS and hardened MAS on the **test** split only:

| Set | n | Role |
| :--- | ---: | :--- |
| Agere-KYC-Synth | 100 | Headline, pooled |
| Agere-Credit-Synth | 75 | Headline, pooled |
| MortarBench, or a labelled 80-case style-alike | rest, or 80 | Secondary |
| FRAMES or a MuSiQue slice | 100 | Control |

6.3 Three seeds: 42, 123, 999. Same case id on both arms. 16 GB physical RAM tier, same effective process cap (12.8 GB nominal maximum), resident, 2,048 thinking tokens.

6.4 Report invention rate (primary) and mismatch recall (co-primary) on the pooled 175 KYC and credit cases. A win on MortarBench or on the control does not override a loss on invention rate.

**Do not:** Change a prompt because of a test result. Average in a run that broke the RAM cap or the token cap.

**Done when:** `AGERE_SSD_ROOT/runs/final/` has both arms, three seeds, and a short `results.md` that states the 16 GB pooled invention rate first. Inputs and outputs use the validated SSD path.

---

## Phase 7 — Loop

**Goal:** Show which change moved the dev score. This is the only phase that repeats.

**Steps**

7.1 Read the failure tags from the latest dev run. Pick **one** primary gap id (S* or M*).

7.2 Change one thing on that arm: an adapter, a schema, or a gate. Score **dev** again.

7.3 Keep the change only if invention rate or mismatch recall improves and the other does not collapse. A pass that does not move dev is reverted.

7.4 Stop an arm after three kept-or-reverted passes, or after one epoch of no dev-invention improvement for training.

7.5 Ablations, after the headline systems exist: turn QLoRA off, turn the verifier off, turn JSON contracts off. Each ablation is a dev run. The pieces that moved dev are the ones the paper keeps.

7.6 If a **test** result makes you want a change, that change is a new system. The old test number stays. Go back to step 7.2. Do not edit against the test set.

**Do not:** Open Phase 6 again for the same frozen system. Loop on test.

**Done when:** The run log lists each pass, whether it was kept, and the dev delta. Ablations have the same shape.

---

## Phase 8 — 8 GB and 32 GB

**Goal:** Run the later held-out and hardened 8 GB and 32 GB comparisons after Phase 6, using the earlier Phase 3 dev floors as reference.

**Steps**

8.1 Recheck the Phase 2 hashes and smoke results for the 8 GB and 32 GB checkpoints from [`configs/locked/tiers/`](./configs/locked/tiers/). Reconvert and re-smoke only if the earlier preparation failed or the frozen model/runtime changed.

8.2 The nominal process caps are **6.4 GB on 8 GB physical RAM** and **25.6 GB on 32 GB physical RAM**, reduced further for measured host use and runtime headroom. On the 32 GB Ubuntu host the 4 GiB host reserve can make the 32 GB MAS tier infeasible; test its SAS and MAS smoke separately and record a blocked/unavailable result rather than raising caps. 8 GB SAS is 7B Q4_K_M; the team is 1.5B + 0.5B + 0.5B F16 (5.1 GB of weights). 32 GB SAS is 32B Q4_K_M; the team is 7B + 3B + 0.5B F16 (22.2 GB of weights). Use the contexts established by the Phase 2 smoke runs; lower context or shrink the smallest model if the actual scored workload cannot fit.

8.3 Cap the aggregate process tree at the effective budget, monitor host-wide available memory, and preserve OS/background reserve. Review the existing Phase 3 dev floor, then score the frozen hardened systems on the held-out tier comparison. If a GPU exists, a matching fine-tune is optional; 32B QLoRA needs ≥48 GB VRAM. The required 32 GB result is the Q4 base plus the same prompts, schemas, and tools as 16 GB.

8.4 Report these tables separately from the 16 GB headline.

**Do not:** Let a 32 GB result replace the 16 GB number.

**Done when:** Each tier has a smoke log with physical RAM, idle baseline, reserve, effective process cap, peak process-tree RSS, minimum host-wide available memory, and a dev or test table labelled with tier and residency mode.

---

## Co-equal product track

Complete these product deliverables alongside the numbered research/build phases. The final product is a demonstrable analyst workflow, and the paper reports how that workflow performs under the locked study conditions. Use synthetic or explicitly licensed data only.

### Alongside Phase 0 — Define the analyst workflow

- [ ] Write the product brief: target analyst, buyer, local deployment boundary, first job-to-be-done, and limits of use.
- [ ] Map the KYC/CDD flow: create/open case → inspect source documents → review extracted fields and evidence → resolve missing/conflicting facts → review cited summary → approve/export.
- [ ] Specify the review states (`MISSING`, `UNVERIFIED_IN_SOURCE`, conflict, verified) and the human approval boundary.
- [ ] Define what gets stored in the local case record and audit trail; keep real customer PII out of the demo.

### Alongside Phases 1–2 — Make local setup and evidence visible

- [ ] Create a simple local case browser and document viewer using the synthetic demo pack.
- [ ] Show which pinned model, quantization, tokenizer/template, and runtime are loaded; include license/source information.
- [ ] Surface model-load failures and RAM-cap failures with actionable messages; never silently fall back to another model or quantization.
- [ ] Make extracted facts open the exact source document and page/span supporting them.

### Alongside Phases 3–5 — Build the reviewable casework experience

- [ ] Present the same case result shape for SAS and MAS: structured facts, source citations, missing fields, discrepancy flags, draft summary, and verifier status.
- [ ] Give the analyst controls to inspect evidence, correct fields, mark a discrepancy resolved/unresolved, and approve or reject the draft.
- [ ] Keep generated claims traceable to case evidence and policy snippets; visibly flag claims with no supporting span.
- [ ] Keep financial calculations deterministic and show the inputs and result used in the draft.
- [ ] Save a case-level audit record with input-document hashes, model/config revision, tool results, generated draft, analyst edits, and approval/export event. Avoid retaining private chain-of-thought.
- [ ] Provide an exportable review package with the final draft, cited evidence, discrepancy register, and run metadata.

### Alongside Phase 6 — Prepare a truthful product demonstration

- [ ] Build a scripted demonstration using held-out demo cases that are separate from the research test split.
- [ ] Demonstrate clean, incomplete, and conflicting case packs, including at least one case where the assistant abstains or marks information missing.
- [ ] Report research metrics and product/usability feedback separately; do not use the research test set for product iteration or user-facing claims.
- [ ] State model, data, hardware, local-processing, and human-review limitations in the demo materials. Do not claim compliance certification or autonomous decision capability.

### Alongside Phases 7–8 — Iterate and document deployment fit

- [ ] Gather structured feedback on task completion, citation discoverability, discrepancy comprehension, correction effort, and confidence in the review trail.
- [ ] Fix product usability issues using dev/demo cases; record changes and do not alter frozen research test results.
- [ ] Show measured RAM use, latency, and any model swap/loading behavior for each tier actually demonstrated.
- [ ] Document setup, supported hardware, local data handling, known limitations, and a repeatable demo path.

### Product done when

- [ ] An analyst can take a synthetic KYC case from local documents through evidence review, discrepancy handling, draft correction, approval, and export.
- [ ] Every material extracted fact or draft claim has a visible source or is explicitly flagged as unsupported/missing.
- [ ] The case record explains which system ran and what tools/evidence/analyst actions shaped the exported result.
- [ ] Product usability findings and research performance results are reported as distinct evidence for the two project outcomes.

---

## Status

Update this table when a phase finishes.

| Phase | Status |
| :---: | :--- |
| 0 SSD and runtime | Not started |
| 1 Download | Not started |
| 2 Quantize | Not started |
| 3 Untouched scores | Not started |
| 4 Fine-tune | Not started |
| 5 Multi-agent system | Not started |
| 6 Final evaluation | Not started |
| 7 Loop | Not started |
| 8 Other RAM tiers | Not started |
