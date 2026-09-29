# Build roadmap

**Project:** Agere  
**Use this file to drive an agent one stage at a time.**  
Decisions (which model, which quant, which test set) stay in [`DEVELOPMENT_START.md`](./DEVELOPMENT_START.md). This file is only the order of work.

**Co-equal outcomes:** this roadmap delivers both a reproducible research result and a working local-first analyst product. Each phase has a research deliverable and a product deliverable; neither track is complete if only the other is usable.

**Storage rule:** the external SSD holds only datasets and model artifacts (source weights, converted/quantized weights, and adapters). Code, tools, dependencies, manifests, logs, evaluation outputs, and reports stay in the repository checkout on the laptop/PC/lab machine. Before every phase, dataset access, training job, evaluation, or other run, set and validate the actual external-drive path in `AGERE_SSD_ROOT`; never assume a path or fall back to another drive.

Start at **Phase 0**. Finish a phase before opening the next one. The first machine is **16 GB**. 8 GB and 32 GB wait until Phase 8.

## How to hand a phase to an agent

Paste this, with the phase number filled in:

> Do **only Phase N** of [`ROADMAP.md`](./ROADMAP.md). Follow [`DEVELOPMENT_START.md`](./DEVELOPMENT_START.md) for models, quantization, and data. Stop when that phase’s “Done when” is true. Do not start the next phase.

## Order

| Phase | What happens | Where the files go |
| :---: | :--- | :--- |
| **0** | Validate SSD path, repository checkout, llama.cpp, 16 GB physical tier / 12.8 GB nominal job cap | Code/manifests in repo; datasets/weights on SSD |
| **1** | Download the 16 GB models | External SSD |
| **2** | Convert to GGUF and quantize the single model | External SSD |
| **3** | Score the **untouched** single model, then the **untouched** team | Dev cases only |
| **4** | Fine-tune the single model, merge, quantize **again** | Adapter/weight artifacts on SSD; code/logs in repo |
| **5** | Build the real multi-agent team (JSON, verifier, budget) | Code |
| **6** | Final evaluation, once | Test cases |
| **7** | Loop: tag failures, change one thing on dev, or ablate | Dev cases |
| **8** | Repeat the smoke test at 8 GB and 32 GB | After Phase 6 |

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

**Goal:** Every job reads only dataset/model artifacts from the explicitly supplied external SSD path; all code and run products stay in the repository checkout.

**Steps**

0.1 Mount the external NVMe and set `AGERE_SSD_ROOT` to its actual absolute mount path for this machine (for example `/mnt/AGERE` on Linux or the assigned drive path on Windows). Do not hard-code an assumed drive letter or mount point. The volume label is `AGERE`.

0.2 Keep this layout on the external SSD. It contains only datasets and model artifacts; source code, runtime binaries, logs, manifests, and evaluation results do not go here.

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
```

0.3 Keep the repository checkout, llama.cpp source/build, and all dependencies on the laptop/PC/lab machine, not on the external SSD. Record runtime versions in the repository at `manifests/runtime.txt`. Inference is CPU. A GPU is for fine-tuning only.

0.4 Before starting **every phase or run**, supply the current machine's correct `AGERE_SSD_ROOT`. The runner must print the resolved repo root and SSD root, validate that the SSD is mounted and contains the required input directories, and refuse to start if the variable is missing, stale, or invalid. Set model-hub/cache paths (including `HF_HOME`/`HF_HUB_CACHE`) beneath `$AGERE_SSD_ROOT/weights/` so large model downloads never default to the local disk. Never silently substitute a local path.

0.5 Write manifests, logs, traces, metrics, checkpoints of evaluation outputs, and reports under the repository (`manifests/`, `runs/`, `experiments/`, or `results/`). For the 16 GB physical tier, set a nominal 12.8 GB aggregate process-tree RSS cap; lower it if the actual host's idle OS/background use plus a 1 GB safety margin requires less. On larger lab PCs, cap to the 16 GB tier's effective budget. A lab PC with more RAM does not get to use it.

**Do not:** Download models. Write training code.

**Done when:** A process exits with a clear error if `AGERE_SSD_ROOT` is missing or incorrect; it reports the resolved paths; a smoke run writes its log under the repo; and the effective RSS cap plus host-wide memory monitor preserve the OS/background reserve.

---

## Phase 1 — Download models onto the SSD

**Goal:** The 16 GB checkpoints are on the SSD, their hashes are recorded in the repository, and weights are not in git.

**Status: Complete (2026-09-29).** Five pinned snapshots totaling about 37.3 GiB are stored under `H:\AGERE\weights\hf\`; all 49 model/tokenizer files passed SHA-256 verification against the repository manifests.

**Steps**

1.1 Before downloading, set and validate this machine's `AGERE_SSD_ROOT`. Install the downloader dependency on the computer (not the SSD) with `python -m pip install -r requirements-phase1.txt`, then run `python scripts/download_hf_snapshots.py`. The downloader pins each snapshot to its resolved Hub revision, preflights available space, resumes partial files, and writes only model/tokenizer assets under `$AGERE_SSD_ROOT/weights/hf/`:

| Role | Hugging Face id |
| :--- | :--- |
| Single model (SAS) | `Qwen/Qwen2.5-14B-Instruct` |
| Orchestrator and drafter | `Qwen/Qwen2.5-3B-Instruct` |
| Extractor | `Qwen/Qwen2.5-1.5B-Instruct` |
| Verifier | `Qwen/Qwen2.5-0.5B-Instruct` |
| Retriever | `BAAI/bge-small-en-v1.5` |

1.2 Write a SHA-256 line for each snapshot to the repository's `manifests/weights.sha256` before any config points at the files. Include the SSD-relative artifact path and checksum.

1.3 Defer the 7B and 32B checkpoints until Phase 8. Download the 0.5B checkpoint now; it is required by the primary 16 GB team and reused by the 8 GB tier.

**Do not:** Quantize yet. Download Llama. Commit weights.

**Done when:** All five snapshots load from `AGERE_SSD_ROOT`, their immutable Hub revisions and per-file SHA-256 hashes are recorded in repository manifests, and every recorded hash matches a recompute.

---

## Phase 2 — Quantize

**Goal:** Runnable GGUF files for the untouched baseline. The single model is Q4_K_M. The team stays full precision.

**Planning estimate for the current development laptop (2026-09-29):** Ryzen 5 8645HS (6 cores / 12 threads), 15.3 GiB physical RAM, RTX 4050 Laptop GPU with 6 GiB VRAM; H: has 110.1 GiB free. Use the CPU conversion/quantization path to match the locked CPU experiment; the GPU is not required for Phase 2. The official llama.cpp flow converts Hugging Face weights to GGUF, then quantizes the GGUF file.

- **SSD space:** Budget about **49 GB (45 GiB)** peak additional space: ~29.5 GB for temporary 14B F16 GGUF, ~10.3 GB for the three retained MAS F16 GGUFs, and ~9 GB for 14B Q4_K_M. The current H: free space is sufficient; keep at least 55 GiB free before starting. Delete the temporary 14B F16 GGUF only after Q4 output and its checksum verify.
- **Local PC space:** Keep all source/build code, Python environment, logs, and smoke results on the PC/repository. The current D: checkout drive has 8.6 GiB free and C: has 1.6 GiB free, which is tight for build tools, Python packages, and Windows temporary files. Free at least 15 GiB on the chosen internal working drive; if Windows/Python caches use C:, free more space there or redirect those caches to D:. Keep package/build caches off H:.
- **RAM:** A recent interactive-session reading was 3.9 GiB available. With 15.3 GiB physical RAM and the required 1 GiB safety margin, that live host state would allow only about a 2.9 GiB job cap and cannot smoke-load either arm. Close memory-heavy apps, record a fresh idle baseline, and recalculate the effective cap before the Phase 2 smoke tests. Never raise the cap to force a model to fit.
- **Elapsed time:** Plan on **3–6 hours** on this CPU, including environment/build setup, conversion of the three smaller F16 GGUFs, 14B F16 conversion and Q4_K_M quantization, and smoke checks. Keep a **half day** free in case the 14B conversion/quantization is memory- or thermally limited. This is a planning estimate, not a benchmark from this host.

**Steps**

2.1 Convert the 3B, 1.5B, and 0.5B Qwen snapshots to GGUF **F16**.

2.2 Quantize **only** the 14B F16 file to **Q4_K_M**. Leave the 3B, 1.5B, and 0.5B team files at F16. Do not produce Q3, Q2, or AWQ for the headline.

2.3 Save converted and quantized weight files under `AGERE_SSD_ROOT/weights/gguf/`. Name them `qwen2.5-14b-instruct-q4_k_m.gguf`, `qwen2.5-3b-instruct-f16.gguf`, `qwen2.5-1.5b-instruct-f16.gguf`, and `qwen2.5-0.5b-instruct-f16.gguf`. Hash each file into the repository's `manifests/weights.sha256`.

2.4 Smoke-load the 14B Q4_K_M under the effective 16 GB-tier process cap (12.8 GB nominal maximum). Generate a few tokens. Record process-tree peak RSS, host-wide available memory, idle baseline, effective cap, and llama.cpp version in the repository's `runs/smoke_sas_16gb.json`.

2.5 Smoke-load the 3B, 1.5B, and 0.5B **together** (resident). Record the same memory fields in the repository's `runs/smoke_mas_16gb.json`. If the effective cap is exceeded, lower context or shrink the smallest worker first; do not raise the cap.

**Do not:** Fine-tune. Score a dataset. Turn the team into a fourth model.

**Done when:** Both smoke JSON files exist in the repo, both process-tree peaks are within the effective cap with OS/background headroom intact, and the Q4 file on the SSD is the one that will be scored in Phase 3.

---

## Phase 3 — Score the untouched models

**Goal:** A frozen floor for the off-the-shelf Q4 model and for a simple team, on **dev** only.

**Steps**

3.1 Write the test-set manifest (names and SHA-256) to the repository's `manifests/test.sha256` **before** any training and before this scoring run if the test files already exist. Dataset files remain on the SSD. Anything in that manifest is off limits here.

3.2 Implement the four tools, same schemas for both arms: `document_extractor`, `policy_retriever`, `financial_calculator`, `citation_verifier`. Amounts come from the calculator. The citation tool is a string match.

3.3 Implement the scorer: invention rate, mismatch recall, grounding accuracy, refusal correctness. Tag each failed case with one id from [`configs/locked/problems.yaml`](./configs/locked/problems.yaml).

3.4 Run **untouched SAS**: 14B Q4_K_M, no adapter, 2,048 thinking tokens, effective 16 GB-tier process cap (12.8 GB nominal maximum), on the **dev** slices of Agere-KYC-Synth and Agere-Credit-Synth read from `AGERE_SSD_ROOT`. Seeds later; one seed is enough to freeze a floor. Save outputs under repository `runs/naive_sas/`.

3.5 Run **untouched MAS**: 3B orchestrator/drafter, 1.5B extractor, 0.5B verifier, all F16, resident, same effective cap, cases, token cap, and tools as SAS. One forward pass per role. No debate and no LoRA. Read weights and cases from the validated SSD root; save outputs under repository `runs/naive_mas/`.

3.6 Write `runs/naive_floor.json` in the repository with both scores. Do not edit this file after it is written.

**Do not:** Call the test split. Start QLoRA. Add a verifier gate and then call the result “naive”.

**Done when:** `naive_floor.json` exists for both arms, every run log has thinking tokens and peak RSS, and no test-manifest hash appears in the inputs.

---

## Phase 4 — Fine-tune, then quantize again

**Goal:** A domain-adapted single model that still fits the effective 16 GB-tier process cap as Q4_K_M, with OS/background headroom preserved.

**Steps**

4.1 Build the training mixture from **train** only: 40% missing-field refusal, 30% tool calls, 30% span citations. Hyperparameters are [`configs/locked/finetune.yaml`](./configs/locked/finetune.yaml): QLoRA NF4, rank 16, alpha 32, dropout 0.05, 8-bit AdamW, learning rate `2e-4`. Stop on **dev invention rate**, not on training loss.

4.2 GPU: ≥24 GB VRAM for the 14B. If that GPU does not exist, fine-tune a **7B** stand-in and label every run `7b-stand-in`. The untouched 14B Q4 from Phase 3 still stays in the table.

4.3 Merge the adapter into 16-bit weights. Save the merged and converted/quantized weight artifacts on the SSD under `weights/`; hash each artifact in the repository manifest. The merged 16-bit model is not what gets scored.

4.4 Smoke-test process-tree RSS and host-wide available memory under the effective 16 GB-tier cap. Save both to the repo run log.

4.5 Score it on **dev**. Keep the adapter only if dev invention rate or mismatch recall improves and the other does not collapse. Otherwise discard it from the SSD and record that in the repository run log.

**Do not:** Train on test. Compare against the team yet. Replace `naive_floor.json`.

**Done when:** The evaluated file on the SSD is a hashed Q4_K_M within the effective 16 GB-tier process cap, OS/background headroom is intact, and the dev delta is written to repository `runs/sas_qlora_dev.json`.

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

**Done when:** A dev run finishes resident within the effective 16 GB-tier cap, preserves OS/background headroom, writes one JSON line per stage (tokens, RSS, gap id) to the repository, and `runs/mas_hardened_dev.json` records the delta versus the naive MAS floor.

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

**Done when:** Repository `runs/final/` has both arms, three seeds, and a short `results.md` that states the 16 GB pooled invention rate first. Inputs were read from the validated SSD path; outputs remain in the repo.

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

**Goal:** See whether the 16 GB result moves when the machine changes. Only after Phase 6.

**Steps**

8.1 Download and convert the extra checkpoints from [`configs/locked/tiers/`](./configs/locked/tiers/): 7B and 0.5B for 8 GB; 7B and 32B for 32 GB. Hash them.

8.2 The nominal process caps are **6.4 GB on 8 GB physical RAM** and **25.6 GB on 32 GB physical RAM**, reduced further if measured idle host use plus 1 GB safety margin requires it. 8 GB SAS is 7B Q4_K_M; the team is 1.5B + 0.5B + 0.5B F16 (5.1 GB of weights). 32 GB SAS is 32B Q4_K_M; the team is 7B + 3B + 0.5B F16 (22.2 GB of weights). Smoke-test each against its effective cap; lower context or shrink the smallest model if runtime/KV memory does not fit.

8.3 Cap the aggregate process tree at the effective budget, monitor host-wide available memory, and preserve OS/background reserve. Then repeat Phase 3 and, if a GPU exists for it, the matching fine-tune. 32B QLoRA is optional (needs ≥48 GB VRAM). The required 32 GB result is the Q4 base plus the same prompts, schemas, and tools as 16 GB.

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
