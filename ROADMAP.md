# Build roadmap

**Project:** Agere  
**Use this file to drive an agent one stage at a time.**  
Decisions (which model, which quant, which test set) stay in [`DEVELOPMENT_START.md`](./DEVELOPMENT_START.md). This file is only the order of work.

Start at **Phase 0**. Finish a phase before opening the next one. The first machine is **16 GB**. 8 GB and 32 GB wait until Phase 8.

## How to hand a phase to an agent

Paste this, with the phase number filled in:

> Do **only Phase N** of [`ROADMAP.md`](./ROADMAP.md). Follow [`DEVELOPMENT_START.md`](./DEVELOPMENT_START.md) for models, quantization, and data. Stop when that phase’s “Done when” is true. Do not start the next phase.

## Order

| Phase | What happens | Where the files go |
| :---: | :--- | :--- |
| **0** | SSD layout, llama.cpp, 16 GB cap | Lab machine |
| **1** | Download the 16 GB models | External SSD |
| **2** | Convert to GGUF and quantize the single model | External SSD |
| **3** | Score the **untouched** single model, then the **untouched** team | Dev cases only |
| **4** | Fine-tune the single model, merge, quantize **again** | SSD `adapters/` |
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

**Goal:** A job can see the external drive and cannot silently use the internal disk.

**Steps**

0.1 Mount the external NVMe at `AGERE_ROOT` (`/mnt/agere` on Linux). The volume label is `AGERE`. 1 TB minimum, 2 TB preferred. ext4 if every machine is Linux; exFAT if Windows must read it.

0.2 Create this layout. Weights never go into git.

```
AGERE_ROOT/
  weights/
  adapters/
  datasets/train/
  datasets/dev/
  datasets/test/
  policy_index/
  runs/
  manifests/
```

0.3 Install llama.cpp and record the version in `manifests/runtime.txt`. Inference is CPU. A GPU is for fine-tuning only.

0.4 Make the runner refuse to start when `AGERE_ROOT` is unset or not a mount.

0.5 Add a 16 GB RSS cap for the process (cgroup or `ulimit`). A lab PC with more RAM does not get to use it.

**Do not:** Download models. Write training code.

**Done when:** The process exits with a clear error if `AGERE_ROOT` is missing, and a hello-process under the cap stays at or below 16 GB RSS.

---

## Phase 1 — Download models onto the SSD

**Goal:** The 16 GB checkpoints are on the SSD, hashed, and not in git.

**Steps**

1.1 Download these official snapshots into `AGERE_ROOT/weights/hf/`:

| Role | Hugging Face id |
| :--- | :--- |
| Single model (SAS) | `Qwen/Qwen2.5-14B-Instruct` |
| Orchestrator and drafter | `Qwen/Qwen2.5-3B-Instruct` |
| Extractor and verifier | `Qwen/Qwen2.5-1.5B-Instruct` |
| Retriever | `BAAI/bge-small-en-v1.5` |

1.2 Write a SHA-256 line for each snapshot to `AGERE_ROOT/manifests/weights.sha256` before any config points at the files.

1.3 Leave 7B, 0.5B, and 32B for Phase 8.

**Do not:** Quantize yet. Download Llama. Commit weights.

**Done when:** All four snapshots load as directories on the SSD and every hash in the manifest matches a recompute.

---

## Phase 2 — Quantize

**Goal:** Runnable GGUF files for the untouched baseline. The single model is Q4_K_M. The team stays full precision.

**Steps**

2.1 Convert each Qwen snapshot to GGUF **F16**.

2.2 Quantize **only** the 14B F16 file to **Q4_K_M**. Leave the 3B and 1.5B files at F16. Do not produce Q3, Q2, or AWQ for the headline.

2.3 Name them `qwen2.5-14b-instruct-q4_k_m.gguf`, `qwen2.5-3b-instruct-f16.gguf`, `qwen2.5-1.5b-instruct-f16.gguf`. Hash each file into `manifests/weights.sha256`.

2.4 Smoke-load the 14B Q4_K_M under the 16 GB cap. Generate a few tokens. Record peak RSS and the llama.cpp version in `runs/smoke_sas_16gb.json`.

2.5 Smoke-load the 3B and the 1.5B **together** (resident). Record peak RSS in `runs/smoke_mas_16gb.json`. If the cap breaks, shrink the 1.5B worker first, not the 3B.

**Do not:** Fine-tune. Score a dataset. Turn the team into a fourth model.

**Done when:** Both smoke JSON files exist, both peak RSS numbers are ≤ 16 GB, and the Q4 file is the one that will be scored in Phase 3.

---

## Phase 3 — Score the untouched models

**Goal:** A frozen floor for the off-the-shelf Q4 model and for a simple team, on **dev** only.

**Steps**

3.1 Write the test-set manifest (names and SHA-256) to `AGERE_ROOT/manifests/test.sha256` **before** any training and before this scoring run if the test files already exist. Anything in that manifest is off limits here.

3.2 Implement the four tools, same schemas for both arms: `document_extractor`, `policy_retriever`, `financial_calculator`, `citation_verifier`. Amounts come from the calculator. The citation tool is a string match.

3.3 Implement the scorer: invention rate, mismatch recall, grounding accuracy, refusal correctness. Tag each failed case with one id from [`configs/locked/problems.yaml`](./configs/locked/problems.yaml).

3.4 Run **untouched SAS**: 14B Q4_K_M, no adapter, 2,048 thinking tokens, 16 GB cap, on the **dev** slices of Agere-KYC-Synth and Agere-Credit-Synth. Seeds later; one seed is enough to freeze a floor. Save outputs under `runs/naive_sas/`.

3.5 Run **untouched MAS**: 3B orchestrator/drafter, 1.5B extractor, 1.5B verifier, all F16, resident, same cases, same token cap, same tools. One forward pass per role. No debate and no LoRA. Save outputs under `runs/naive_mas/`.

3.6 Write `runs/naive_floor.json` with both scores. Do not edit this file after it is written.

**Do not:** Call the test split. Start QLoRA. Add a verifier gate and then call the result “naive”.

**Done when:** `naive_floor.json` exists for both arms, every run log has thinking tokens and peak RSS, and no test-manifest hash appears in the inputs.

---

## Phase 4 — Fine-tune, then quantize again

**Goal:** A domain-adapted single model that still fits the 16 GB tier as Q4_K_M.

**Steps**

4.1 Build the training mixture from **train** only: 40% missing-field refusal, 30% tool calls, 30% span citations. Hyperparameters are [`configs/locked/finetune.yaml`](./configs/locked/finetune.yaml): QLoRA NF4, rank 16, alpha 32, dropout 0.05, 8-bit AdamW, learning rate `2e-4`. Stop on **dev invention rate**, not on training loss.

4.2 GPU: ≥24 GB VRAM for the 14B. If that GPU does not exist, fine-tune a **7B** stand-in and label every run `7b-stand-in`. The untouched 14B Q4 from Phase 3 still stays in the table.

4.3 Merge the adapter into 16-bit weights. Convert to GGUF F16. Quantize to Q4_K_M. Hash the new GGUF. The merged 16-bit model is not what gets scored.

4.4 Smoke-test peak RSS of the new Q4 file under the 16 GB cap.

4.5 Score it on **dev**. Keep the adapter only if dev invention rate or mismatch recall improves and the other does not collapse. Otherwise discard it and record that in the run log.

**Do not:** Train on test. Compare against the team yet. Replace `naive_floor.json`.

**Done when:** The evaluated file is a hashed Q4_K_M under 16 GB RSS, and the dev delta versus the naive floor is written to `runs/sas_qlora_dev.json`.

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

**Done when:** A dev run finishes resident under 16 GB, logs one JSON line per stage (tokens, RSS, gap id), and `runs/mas_hardened_dev.json` records the delta versus the naive MAS floor.

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

6.3 Three seeds: 42, 123, 999. Same case id on both arms. 16 GB, resident, 2,048 thinking tokens.

6.4 Report invention rate (primary) and mismatch recall (co-primary) on the pooled 175 KYC and credit cases. A win on MortarBench or on the control does not override a loss on invention rate.

**Do not:** Change a prompt because of a test result. Average in a run that broke the RAM cap or the token cap.

**Done when:** `runs/final/` has both arms, three seeds, and a short `results.md` that states the 16 GB pooled invention rate first.

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

8.2 8 GB SAS is 7B Q4_K_M. 8 GB team is 1.5B + 0.5B + 0.5B, all F16. 32 GB SAS is 32B Q4_K_M. 32 GB team is 7B + 3B + 1.5B, all F16.

8.3 Cap the job at that tier. Smoke-test RSS. Then repeat Phase 3 and, if a GPU exists for it, the matching fine-tune. 32B QLoRA is optional (needs ≥48 GB VRAM). The required 32 GB result is the Q4 base plus the same prompts, schemas, and tools as 16 GB.

8.4 Report these tables separately from the 16 GB headline.

**Do not:** Let a 32 GB result replace the 16 GB number.

**Done when:** Each tier has a smoke RSS log and a dev or test table labelled with the tier and the residency mode.

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
