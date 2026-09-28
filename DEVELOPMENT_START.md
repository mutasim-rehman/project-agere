# Development start lock

**Project:** Agere  
**Date locked:** 28 September 2026  
**Status:** Decisions gathered. Application code has not been written.  
**Use this file to start coding.** Research narrative stays in [`METHODOLOGY.md`](./METHODOLOGY.md). If that file and this one disagree on a model, a quant, a tier, or a fine-tune step, **this file wins**, because it resolves the conflicts in [§1](#1-what-was-already-written-and-what-contradicted-it).

Machine-readable copy of the same lock: [`configs/locked/`](./configs/locked/).

---

## 0. Can we start?

| Need | Ready? | Where it lives |
| :--- | :---: | :--- |
| Who the system is for, and which workflows | Yes | [`APPLICATION.md`](./APPLICATION.md), [`FINANCE_DOMAIN_CONTEXT.md`](./FINANCE_DOMAIN_CONTEXT.md) |
| Headline comparison and parity rules | Yes | [`METHODOLOGY.md`](./METHODOLOGY.md) §5, [`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md) |
| Model family, size, and precision **per RAM tier** | Yes, locked here | [§3](#3-models-per-tier) |
| Quantization method | Yes, locked here | [§4](#4-quantization) |
| Fine-tune procedure | Yes, locked here | [§5](#5-fine-tuning) |
| MAS: how many models, which roles, per tier | Yes, locked here | [§3](#3-models-per-tier), [§6](#6-how-the-team-is-wired) |
| Which problems to fix, and how | Yes | [§7](#7-problems-and-the-fix-for-each) |
| Train / dev / test counts | Yes | [`METHODOLOGY.md`](./METHODOLOGY.md) §12 |
| Configs a runner can load for the current study | Yes, as of this lock | [`configs/locked/`](./configs/locked/) |
| Python package, inference code, datasets on disk | No | [§9](#9-what-to-build-first) |

Start on the **16 GB** tier. Build the naive baseline before any fine-tune. The old 15-tier GPU checklist and its YAML have been removed from the tree.

---

## 1. What was already written, and what contradicted it

The decisions below were already made in [`METHODOLOGY.md`](./METHODOLOGY.md) v1.1 (25 September 2026), sections 10–17. An earlier draft described a different study: 15 GPU VRAM tiers, CUDA, vLLM, AWQ, GAIA, and GSM8K. That draft’s checklist and YAML have been **deleted**. Where the remaining prose still disagrees with this file, this file wins.

| Topic | What the older draft said | Lock used for code |
| :--- | :--- | :--- |
| Hardware axis | 15 GPU VRAM tiers, CUDA, vLLM | **3 system-RAM tiers** (8 / 16 / 32 GB), **CPU**, llama.cpp |
| Model family | “Qwen2.5 / Llama 3.x”, family still open. Methodology §4.1 still says “or Llama-3.1” | **Qwen2.5-Instruct only.** Llama stays out of scope until the 16 GB headline result exists. |
| SAS quant | Q5/Q8, INT8, AWQ, 2-bit, 1-bit as the main sweep | **GGUF Q4_K_M on every SAS tier.** Q5_K_M is a sensitivity run only. Q3 and below are not a system we compare. AWQ is the paper that justifies 4-bit. It is not the file we run. |
| MAS at 16 GB | Two 3B FP16 models plus a 1.5B | **One** 3B (orchestrator and drafter), **one** 1.5B extractor, **one** 1.5B verifier |
| MAS at 8 GB | 1.5B + 1.5B + 0.5B | **1.5B + 0.5B + 0.5B** |
| MAS at 32 GB | 7B + 7B + 0.5B | **7B + 3B + 1.5B** |
| How many agents | Five named roles, each a model | **Three generative models** plus one shared embedding retriever. The drafter is the orchestrator checkpoint, not a fourth LLM. |
| Saturation rule | ≥95% of GPU VRAM | **RUPP:** peak RSS ≤ tier, and both arms should reach **≥85%** of the tier on a real case. Measure it. Do not pad memory to fake the percentage. |
| Headline benchmarks | GAIA, GSM8K, MATH-500, GPQA | **Tracks A–D** in [§8](#8-tasks-the-first-code-must-score) |

---

## 2. Stack

| Piece | Choice |
| :--- | :--- |
| Family | Qwen2.5-Instruct. Same family on both arms. |
| SAS runtime file | llama.cpp **GGUF Q4_K_M** |
| MAS runtime file | llama.cpp **GGUF F16** (IEEE FP16). This is the CPU “full precision” file. |
| Retriever | `BAAI/bge-small-en-v1.5`, same index on both arms, counted inside the RSS cap |
| Inference | llama.cpp, CPU, AVX2. No GPU at inference. Ollama is an acceptable wrapper only if it loads these exact GGUF types and we still record peak RSS ourselves. |
| Training | **QLoRA NF4** on a GPU, then merge, then **re-quantize to Q4_K_M**. The evaluated SAS is never the merged 16-bit model. |
| Primary tier | 16 GB peak RSS, resident MAS, 2,048 thinking tokens |
| Seeds | 42, 123, 999 |
| Human rule | Draft, extract, flag, cite. No credit approval, no risk rating, no SAR/STR filing. |

Official Hugging Face ids:

| Checkpoint | Id |
| :--- | :--- |
| 0.5B | `Qwen/Qwen2.5-0.5B-Instruct` |
| 1.5B | `Qwen/Qwen2.5-1.5B-Instruct` |
| 3B | `Qwen/Qwen2.5-3B-Instruct` |
| 7B | `Qwen/Qwen2.5-7B-Instruct` |
| 14B | `Qwen/Qwen2.5-14B-Instruct` |
| 32B | `Qwen/Qwen2.5-32B-Instruct` |
| Embeddings | `BAAI/bge-small-en-v1.5` |

Do not pin a third-party GGUF mirror in git. Convert from the official snapshot (or record the exact file URL **and** SHA-256 in `manifests/` on the lab SSD at download time). Filename pattern: `qwen2.5-<size>-instruct-f16.gguf` and `qwen2.5-<size>-instruct-q4_k_m.gguf`.

Weight figures below are weights only. KV cache and the process sit on top. A one-case smoke test records peak RSS before a tier is treated as runnable. If peak RSS exceeds the cap, shrink the **smallest worker** first. The orchestrator is not the first model to shrink.

The lab PC may have more RAM than the tier. Cap the job (cgroup / `ulimit`) at the tier. A run with no cap is not a result.

---

## 3. Models per tier

Three generative models on every MAS tier. The retriever is not one of them.

| | **T1 — 8 GB** | **T2 — 16 GB (build this first)** | **T3 — 32 GB** |
| :--- | :--- | :--- | :--- |
| Machine the paper means | Legacy analyst laptop, 4 cores, no GPU | Bank workstation, 4–8 cores, no GPU | Team-lead desktop, 8+ cores, no GPU |
| **SAS model** | `Qwen2.5-7B-Instruct` | `Qwen2.5-14B-Instruct` | `Qwen2.5-32B-Instruct` |
| **SAS file** | Q4_K_M, ~4.7 GB | Q4_K_M, ~9.0 GB | Q4_K_M, ~20 GB |
| **SAS fine-tune** | QLoRA on the 7B. Needs a **≥12 GB** GPU, or a slow CPU-offload run | QLoRA on the 14B. Needs a **≥24 GB** GPU. If that GPU does not exist, fine-tune a **7B Q4 stand-in and label it**. Still run the untouched 14B Q4 as the baseline | 32B QLoRA is **optional** and needs **≥48 GB** VRAM. The required 32 GB system is the Q4_K_M base plus the same prompts, schemas, and tools as 16 GB |
| **MAS model 1 — orchestrator and drafter** | 1.5B F16, ~3.1 GB | 3B F16, ~6.2 GB | 7B F16, ~15 GB |
| **MAS model 2 — extractor** | 0.5B F16, ~1.0 GB | 1.5B F16, ~3.1 GB | 3B F16, ~6.2 GB |
| **MAS model 3 — verifier** | 0.5B F16, ~1.0 GB | 1.5B F16, ~3.1 GB | 1.5B F16, ~3.1 GB |
| **MAS generative count** | 3 | 3 | 3 |
| **Retriever** | `bge-small-en-v1.5` | same | same |
| **MAS weight sum** | ~5.1 GB | ~12.4 GB | ~24 GB |
| Eval context | 4,096 | 8,192 | 8,192 |
| Thinking-token cap | 2,048 (also report 1,024 and 4,096) | same | same |
| MAS LoRA | Optional, role-specific, 0.5B–3B fit a 12 GB GPU. Drop the adapter if dev does not improve | same | 7B orchestrator LoRA only if a GPU can hold it; otherwise prompt and schema only |

Q4_K_M stays the SAS quant on all three tiers. We do not move 8 GB to Q2 or 32 GB to Q8 for the headline table.

---

## 4. Quantization

### 4.1 What we run

**GGUF Q4_K_M** (llama.cpp K-quant, 4-bit, medium). Super-blocks of 256 weights, with a mix of 4-bit and 6-bit scales. This is the file a bank downloads for Ollama/llama.cpp.

Why not the others, for the headline:

| Method | Role in this project |
| :--- | :--- |
| **Q4_K_M** | The deployed SAS object on every tier. |
| **Q5_K_M** | Sensitivity only, and only if the Q4 smoke test is far under the RAM cap. Same checkpoint, same prompts. |
| **Q3_K_M and below** | Not a competing system. Gap S12. |
| **AWQ** | Citation for why 4-bit can protect salient channels (Lin et al., 2024). AWQ kernels are GPU kernels. We do not serve AWQ. |
| **GPTQ, bitsandbytes INT4/INT8 at inference, AQLM, QuIP#, SpinQuant, BitNet** | Out of the headline. They answer a different hardware question. |
| **GGUF F16** | MAS weights. Not a quantized SAS. |
| **NF4** | Training-time only, inside QLoRA. Never the file we score. |

### 4.2 How the SAS file is produced after training

```
Hugging Face 16-bit Qwen2.5-*-Instruct
    → QLoRA (NF4 base + LoRA) on the training mixture
    → merge the adapter into 16-bit weights
    → llama.cpp convert to GGUF F16
    → llama-quantize … Q4_K_M
    → smoke-test peak RSS inside the tier
    → only then is this file allowed into the hardened comparison
```

The naive baseline skips the first three arrows: official (or converted) Q4_K_M, no adapter.

---

## 5. Fine-tuning

### 5.1 SAS — required procedure

QLoRA as in Dettmers et al. (2023). Not QA-LoRA. Section 4.1 of the methodology uses both names; the procedure that is locked is QLoRA.

| Hyperparameter | Value |
| :--- | :--- |
| Base quant | NF4, double quantization |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |
| Target modules | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |
| Compute dtype | BF16 if the GPU supports it, else FP16 |
| Optimizer | AdamW 8-bit |
| Learning rate | `2e-4` |
| Schedule | Cosine, 3% warmup |
| Epochs | 2–3, then early stop |
| Early stop | **Dev invention rate**, not training loss. Stop when that rate has not improved for one epoch. |
| Sequence length | 2,048. Memo examples may use 4,096 only if the GPU still has headroom. |
| Effective batch | 16, via gradient accumulation |

Mixture by example count:

| Share | Skill | Target behaviour |
| :--- | :--- | :--- |
| 40% | Missing data | Emit `MISSING` or `UNVERIFIED_IN_SOURCE`. Do not invent a CNIC date, an NTN, a deposit, or an e-CIB status. |
| 30% | Tools | Schema-valid call to `financial_calculator` or `document_extractor`. No arithmetic in prose. |
| 30% | Citations | Every amount, date, and name carries a span id that exists in the packet. |

SAS also gets the staged prompt (extract JSON → policy check → memo) so the team does not win only because it was given a pipeline.

### 5.2 MAS — optional role adapters

Train only if a 12 GB-class GPU exists (0.5B–3B). Keep an adapter only if the **dev** set improves. If it does not, delete it and ship the base F16 checkpoint.

| Role | Adapter, if trained | Not trained to |
| :--- | :--- | :--- |
| Extractor | Field JSON only | Write the memo |
| Drafter | Memo text that may cite only ids already in the JSON packet | Invent fields |
| Verifier | Binary `PASS` / `FAIL`, including fluent memos that change one digit | Rewrite the memo |
| Orchestrator | Prompt and schema only, unless dev shows it drops stages | Free-form planning |

The verifier’s real decision is a checklist plus string match against the case store. The adapter does not replace that check.

### 5.3 Data the fine-tune may see

No real customer file. The test manifest (names and SHA-256) is written to the lab SSD **before** the first training step. Anything hashed as test never enters a batch. Dev is where training stops and where adapters are kept or dropped. Test is one shot per frozen system.

| Corpus | Train | Dev | Test |
| :--- | ---: | ---: | ---: |
| Agere-KYC-Synth (Track B) | 400 | 100 | 100 |
| Agere-Credit-Synth (Track C) | 200 | 50 | 75 |
| MortarBench (Track A) | none | only if the authors allow a cut | the rest |
| MortarBench-style pack, only if the official set cannot be obtained | none | 20 | 80 |
| FRAMES or MuSiQue slice (Track D) | none | none | 100 |
| Tool-format supplement (our four tools, BFCL-shaped) | yes | yes | not a reported finance score |

Full rules: [`METHODOLOGY.md`](./METHODOLOGY.md) §12.

---

## 6. How the team is wired

One forward pass per role, plus **at most one** repair if the verifier fails. No debate topology.

| Order | Who | Model instance | Talks in |
| :--- | :--- | :--- | :--- |
| 1 | Extractor | model 2 | JSON fields. `MISSING` is a value. Only this role calls `document_extractor`. |
| 2 | Retriever | embedding index, query from the orchestrator | Filtered snippets. Filter on product, jurisdiction, document ids. |
| 3 | Drafter | model 1 (same checkpoint as the orchestrator) | Memo. May cite only ids already in the JSON packet. |
| 4 | Verifier | model 3 | `PASS` or `FAIL` plus a checklist. Deterministic span match. Fuzzy matches are logged apart from exact matches. |

The orchestrator does not “decide” the stage list in prose. The stage list is code. Workers are stateless: the constraint packet is reattached on every call.

Thinking-token split of the shared cap (verifier’s share is reserved first):

| Stage | Share |
| :--- | ---: |
| Extractor | 30% |
| Retriever | 10% |
| Drafter | 40% |
| Verifier | 20% |

Tools, identical on both arms:

| Tool | Rule |
| :--- | :--- |
| `document_extractor(doc_id, field_list)` | Text and tables from the case pack. |
| `policy_retriever(query, jurisdiction)` | SBP PR excerpts, FATF text, synthetic bank SOP. |
| `financial_calculator(operation, **kwargs)` | DBR, DSCR, current ratio, leverage. The model must not do this arithmetic in prose. |
| `citation_verifier(claim_span, source_doc_id)` | Substring check against the case store. |

Primary MAS number is **resident** peak RSS (all three LLMs loaded). Sequential load/unload is a second table, labelled as such.

---

## 7. Problems and the fix for each

P0 items are in the system that reaches the hardened comparison. A skipped P0 item needs one written reason in the run log. SAS receives the matching fix so the team is not compared with a weak monolith.

### 7.1 Quantized monolith (SAS)

| ID | Problem | Priority | Fix to build |
| :--- | :--- | :---: | :--- |
| S1 | No domain adaptation (KYC fields, memo shape, SBP wording) | P0 | QLoRA on the synthetic mixture, [§5](#5-fine-tuning) |
| S2 | Invents a value when the document is blank | P0 | Train `MISSING` / `UNVERIFIED_IN_SOURCE`; refusal in the schema |
| S3 | One prompt extracts, judges, and drafts | P0 | Staged prompts with JSON checkpoints between stages |
| S4 | Prose changes DSCR / EBITDA versus the sheet | P0 | Calculator tool only; ban free-form amounts |
| S5 | Quantized tool calls break (bad name, bad args) | P1 | Four tools, strict JSON schema, at most two retries |
| S6 | Citations that do not match a span | P0 | Mandatory span ids; post-hoc string match |
| S7 | ID and registry disagree and nobody flags it | P0 | Deterministic mismatch diff, not “the model noticed” |
| S8 | Long packs push early documents out of context | P1 | Chunked extract into a case store, then retrieve |
| S9 | Free text an examiner cannot sample | P1 | Fixed memo template and a discrepancy table |
| S10 | Reads as if it approved the loan or rated the risk | P1 | System prompt and training: draft only |
| S11 | Retrieval can see another client | P0 | One index scope per case; no shared client collection |
| S12 | Q3/Q2 collapses structured output | P2 | Stay on Q4_K_M. Do not add a low-bit arm to the headline |

### 7.2 Multi-agent team (MAS)

| ID | Problem | Priority | Fix to build |
| :--- | :--- | :---: | :--- |
| M1 | Agents disagree on what “done” means | P0 | One SOP and one JSON done-schema, held by the orchestrator |
| M2 | Extractor softens “unknown”; drafter invents the field | P0 | JSON only between stages. No prose handoff. No empty slot the drafter can fill |
| M3 | One bad amount is copied into every later stage | P0 | Verifier between draft and delivery. Failed quote-check rejects the draft |
| M4 | Downstream role forgets “cite or refuse” | P0 | Stateless workers; constraint packet on every call |
| M5 | Retriever returns another product’s policy | P1 | Packet carries product, jurisdiction, document ids; retrieval filters on them |
| M6 | Debate burns the token budget | P1 | No debate. One pass per role, one repair at most |
| M7 | Critic rewrites prose and never checks the quote | P0 | Verifier is deterministic span match, not a second drafter |
| M8 | Budget is gone before verify | P0 | Scheduler in [§6](#6-how-the-team-is-wired). Reserve the verifier share first |
| M9 | All agents resident causes swap, or sequential mode is reported as if it were resident | P1 | Two tables. Primary = resident peak RSS |
| M10 | Orchestrator skips the mismatch check | P1 | Largest model is the orchestrator. Stage list is code |
| M11 | Two roles extract the same PDF differently | P2 | One case store. Only the extractor calls `document_extractor` |
| M12 | Role names on a general chat model | P0 | Role prompts, schemas, and the optional LoRAs in [§5.2](#52-mas--optional-role-adapters) |
| M13 | Verifier always says the draft is fine | P0 | Binary checklist. `PASS` requires every amount to match a span. Hard negatives if a LoRA is trained |
| M14 | Hard to debug | P2 | One JSON log line per stage: tokens, RSS, gap id |

### 7.3 Both arms

| ID | Problem | Fix |
| :--- | :--- | :--- |
| X1 | Scoring MMLU-style accuracy | Score invention rate, mismatch recall, grounding, refusal |
| X2 | The LLM owns the numbers | Calculator outside the model |
| X3 | No human gate | Draft only |
| X4 | Real customer PII | Synthetic packs only |
| X5 | Unequal tools | The four tools above, same schemas |
| X6 | Unequal RAM or tokens | RUPP and the shared thinking-token cap |

Detail and the fair-comparison checklist: [`SYSTEM_GAPS_AND_IMPROVEMENTS.md`](./SYSTEM_GAPS_AND_IMPROVEMENTS.md).

---

## 8. Tasks the first code must score

| Track | Task | What “good” means | n test |
| :--- | :--- | :--- | ---: |
| A | Mortgage origination Q&A (MortarBench, or a disclosed style-alike) | Per-type F1 | official rest, or 80 |
| B | KYC/CDD pack: CNIC, NTN/ATL, SECP-style ownership, sanctions hit or clean | Invention rate, mismatch recall, refusal | 100 |
| C | SME credit memo with cited ratios | Same, plus grounding | 75 |
| D | Multi-hop questions, **no case documents** (FRAMES or MuSiQue) | Exact match. A large MAS win here is a bug until explained | 100 |

Primary judgement, 16 GB, resident, 2,048 thinking tokens, **hardened** systems: invention rate (lower) and mismatch recall (higher), pooled on B and C. Naive scores stay in the paper as the floor. Latency is reported and does not pick the winner.

---

## 9. What to build first

Follow this order.

1. **Lab layout, not weights in git.** `AGERE_ROOT` on the external SSD (`weights/`, `adapters/`, `datasets/`, `runs/`, `manifests/`). The job refuses to start if `AGERE_ROOT` is unset. SHA-256 every GGUF before a config points at it.
2. **16 GB naive SAS.** Load `Qwen2.5-14B-Instruct` Q4_K_M in llama.cpp. One case. Record peak RSS and tokens. Cap the process at 16 GB.
3. **16 GB naive MAS.** Load the three F16 models in [§3](#3-models-per-tier) resident. JSON handoff, no debate, no LoRA yet. Same case, same token cap, same tools.
4. **Four tools and the case schema** (Pydantic). Calculator and citation check are deterministic.
5. **Scorer** for invention, mismatch recall, grounding, refusal. Tag each failure with one S* or M* id.
6. **Freeze naive scores on dev.** Then harden (QLoRA, staged SAS prompt, MAS gates). Test is one shot after the freeze.
7. **Only then** repeat the smoke test at 8 GB and 32 GB.

Cells A (SAS at F16) and D (quantized MAS) are optional and are not this start path.

Still open, and none of them block step 2:

| Item | Rule already in place |
| :--- | :--- |
| Exact GGUF SHA-256 | Written to `manifests/` at download. Not invented here. |
| Which role LoRAs survive | Dev invention rate or mismatch recall. Else discard. |
| Official MortarBench files vs a style-alike pack | Style-alike is allowed and must be labelled as such. |
| Whether the lab has a 24 GB GPU for 14B QLoRA | Fallback is a labelled 7B stand-in. The 14B Q4 baseline still runs. |
| llama.cpp version pin | Pin the version in the environment when it is installed. |

