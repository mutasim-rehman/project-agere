# METHODOLOGY: Project Agere
## Spend It Together or Spend It Big?
### Multi-Agent Full-Precision Teams vs. Quantized Monoliths on Analyst Workstation RAM for Regulated Finance

**Document Version:** 1.1  
**Date:** 25 September 2026  
**Status:** Specification  
**Project Repository:** Project Agere (`/workspace`)  
**Related Documents:** [`APPLICATION.md`](./APPLICATION.md) · [`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md) · [`SYSTEM_GAPS_AND_IMPROVEMENTS.md`](./SYSTEM_GAPS_AND_IMPROVEMENTS.md) · [`FINANCE_DOMAIN_CONTEXT.md`](./FINANCE_DOMAIN_CONTEXT.md) · [`sources/INDEX.md`](./sources/INDEX.md)

**Where to look**

| Question | Section |
| :--- | :--- |
| Coding lock if this file and the configs disagree | [`DEVELOPMENT_START.md`](./DEVELOPMENT_START.md) |
| Which phase to run next | [`ROADMAP.md`](./ROADMAP.md) |
| Which model on each RAM tier, and on what hardware | [§10](#10-models-quantization-and-hardware-by-tier) |
| Which quantization method, and how fine-tuning works | [§11](#11-quantization-method-and-fine-tuning-procedure) |
| Which datasets, and what is forbidden in training | [§12](#12-datasets-train-dev-and-test) |
| Which datasets are the final evaluation | [§14](#14-judgement-basis) |
| Which MAS failures we fix, and how | [§13](#13-mas-failure-modes-and-the-fix-for-each) |
| On what basis both systems are judged | [§14](#14-judgement-basis) |
| How both arms are made as strong as this lab can make them | [§15](#15-making-both-systems-as-strong-as-they-can-be) |
| External SSD stores only datasets and model artifacts; code and results stay in repo | [§16](#16-external-ssd-and-repository-storage) |
| Synthetic data and the human sign-off rule | [§17](#17-ethical-compliance-considerations) |

---

## 1. Executive Summary & Research Motivation

### 1.1 The Core Research Question
> **Can a Multi-Agent System consisting of smaller, full-precision LLMs (MAS-FP16) outperform a single larger, quantized LLM (SAS-Quant) when both systems operate under the same host-adjusted process-tree RSS ceiling and thinking-token budget on regulated financial document workflows?**

### 1.2 The Real-World Deployment Dilemma
In commercial banks, asset managers, and financial institutions operating under strict regulatory regimes (e.g., FINRA Notice 24-09, SEC 17a-4, GDPR, DORA, and State Bank of Pakistan AML/CFT directives):
- **Cloud APIs are Legally Prohibited:** Customer Personally Identifiable Information (PII), confidential credit packs, tax records, and sanctions screening hits cannot be transmitted across corporate perimeters or national borders to public cloud endpoints (OpenAI, Anthropic, Google).
- **Workstation Compute Realities:** Compliance officers and credit underwriters execute local CPU-first inference (via `llama.cpp` or `Ollama`) on standard **16 GB RAM** corporate workstations without enterprise datacenter GPUs.
- **The Prevailing Industry Default:** IT departments default to downloading the largest open-weights model that can fit into RAM when aggressively quantized (e.g., 14B parameter model compressed to 4-bit integer weights like GGUF `Q4_K_M`).
- **The Core Scientific Hypothesis:** Rather than spending the effective 16 GB-tier job budget on one compressed generalist, allocating the same capped process memory across an orchestrated team of smaller, native full-precision (FP16/BF16) specialized agents (e.g., 3B Orchestrator/Drafter + 1.5B Extractor + 0.5B Verifier) may improve grounding or reduce invented values. This remains a testable hypothesis, not an assumed result.

---

## 2. Theoretical Foundation & Literature Synthesis

Our methodology directly operationalizes and extends key breakthroughs from the recent (2024–2026) peer-reviewed and foundational literature:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Methodological Pillars                          │
├───────────────────────────────────┬────────────────────────────────────┤
│ 1. Token Budget Parity            │ 2. Tool-Equalized Architecture     │
│    Tran & Kiela (2026)            │    Żywot et al. (2026)             │
│    Equalize test-time tokens      │    Equalize tools across arms;     │
│    to eliminate compute bias.     │    asymmetric orchestrator sizing. │
├───────────────────────────────────┼────────────────────────────────────┤
│ 3. Quantized Agent Vulnerability  │ 4. Cascades & Boundary Gates       │
│    Jang et al. (2026)             │    Singh & Pawar (2026); Cemri     │
│    Quantization amplifies tool    │    Independent verifier boundary   │
│    failures; requires grounding.  │    gates stop Markov snowballs.    │
├───────────────────────────────────┼────────────────────────────────────┤
│ 5. Structured SOP Contracts       │ 6. Hardware Memory Profiling       │
│    Hong et al. (2024, MetaGPT)    │    Lin et al. (2025, Bench360)     │
│    Strict JSON artifacts over     │    Strict peak RSS profiling under │
│    free-form natural language.    │    RAM Utilization Parity (RUPP).  │
└───────────────────────────────────┴────────────────────────────────────┘
```

1. **Test-Time Compute Parity (Tran & Kiela, 2026; Wang et al., EMNLP 2024):** Prior multi-agent benchmarks reported illusory gains by allowing multi-agent teams to burn $3\times\text{--}5\times$ more output tokens than single agents. We enforce strict thinking-token parity ($T_{\text{think}}$) across all arms.
2. **Data Processing Inequality & Information Loss (Tran & Kiela, 2026):** Natural language dialogue between agents is strictly lossy ($I(X; Z) \le I(X; Y)$). Unstructured chat degrades context. Inter-agent communication must therefore be strictly serialized through typed schemas and external deterministic tools.
3. **Tool Equalization & Asymmetry (Żywot et al., 2026):** Multi-agent gains disappear when monolithic baselines are given identical tools. Furthermore, orchestrator parameter capacity matters significantly more than worker capacity.
4. **Quantization Failure Amplification (Jang et al., 2026; Lin et al., MLSys 2024):** Post-training 4-bit quantization (AWQ/GGUF) degrades tool-argument formatting and causes catastrophic hallucinations under missing data.
5. **Hallucination Cascades & Boundary Verification (Singh & Pawar, 2026; Jamshidi et al., 2026):** Unchecked multi-agent handoffs exhibit a Markovian error snowball. We introduce dedicated deterministic and model-based verifier boundary gates to arrest error propagation.
6. **SOPs over Chat (Hong et al., ICLR 2024, MetaGPT):** Human standard operating procedures (SOPs) eliminate over 60% of cascading agent errors.
7. **Local Financial Document Reasoning (MortarBench, 2026; Financial QA SME, 2026):** Proves that architecture beats raw scale on local ~8B models in regulated finance document examination.

---

## 3. Beyond Naive Benchmarking: The "Improve-Then-Compare" Loop

Benchmarking off-the-shelf models (e.g., standard Q4 generalist vs. naive multi-agent chat) yields **no scientific novelty**. A generic quantized model fails due to lack of domain adaptation, while a generic multi-agent system fails from unstructured chatter and error snowballs.

To achieve academic novelty and valid deployment guidance, our methodology adopts an **"Improve-Then-Compare"** loop:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Phase 0: System Specification & Parity Invariants                           │
│ - Hardware tier: 16 GB physical RAM; 12.8 GB nominal job RSS cap            │
│ - Shared invariants: $T_{\text{think}}$ token budget cap, identical tools   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Naive Baseline Evaluation (Freeze Raw State)                       │
│ - Off-the-shelf SAS-Quant (vanilla instruct model at Q4_K_M)                │
│ - Off-the-shelf MAS (naive prompt pipeline, unstructured chat handoffs)     │
│ - Record baseline error rates and establish the performance floor           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Phase 2: Systematic Error Triage & Gap Categorization                       │
│ - Diagnose SAS gaps (S1–S12): invention under missing data, citation drift  │
│ - Diagnose MAS gaps (M1–M14): context collapse, lossy handoffs, loops       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Phase 3: Domain Adaptation & Engineering (Novel Contributions)             │
│                                                                             │
│ ┌────────────────────────────────────┐  ┌─────────────────────────────────┐ │
│ │ SAS-Quant Hardening                │  │ MAS-FP16 Engineering            │ │
│ │ • Domain QLoRA fine-tuning         │  │ • Strict typed JSON schemas     │ │
│ │ • Refusal under missing data       │  │ • Independent Verifier gate     │ │
│ │ • Staged pseudo-pipeline prompts   │  │ • Asymmetric orchestrator sizing│ │
│ │ • Deterministic calculator calls   │  │ • Dynamic budget scheduler      │ │
│ └────────────────────────────────────┘  └─────────────────────────────────┘ │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Phase 4: Head-to-Head Evaluation (Hardened MAS vs. Hardened SAS)            │
│ - Tasks: MortarBench (Origination), Synthetic KYC/CDD, Credit Memos         │
│ - Negative Control: Multi-hop reasoning without documents (FRAMES)          │
│ - Primary Metrics: Grounding Accuracy, Invention Rate, Mismatch Recall      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Phase 5: Ablation Decomposition & Deployment Rule Formulation               │
│ - Measure marginal contribution of QLoRA vs. Verifier gates                 │
│ - Formulate decision rule for compliance IT engineering                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Domain Adaptation & System Engineering

### 4.1 Arm 1: Hardened SAS-Quant (Quantized Monolith)
To overcome the documented failure modes of 4-bit generalists (S1–S12), the single-agent arm is upgraded as follows:

1. **Domain Fine-Tuning via QLoRA / QA-LoRA:**
   - **Base Model:** Qwen2.5-14B-Instruct or Llama-3.1-8B/14B quantized to 4-bit integer weights.
   - **Adaptation Technique:** Quantization-Aware Low-Rank Adaptation (QA-LoRA / QLoRA) applied directly over the quantized weights, avoiding catastrophic representational collapse.
   - **Curated 3-Task Fine-Tuning Dataset:**
     - *Task A (Refusal Discipline):* Explicit training on document packs with intentionally missing fields (e.g., omitted CNIC issue date, unstated turnover). The model is optimized to output `"field_status": "MISSING"` or `"UNVERIFIED_IN_SOURCE"` rather than hallucinating plausible values.
     - *Task B (Strict Tool Invocation):* Training on deterministic function-calling pairs for calculator tools (DBR, DSCR, Current Ratio), forcing the model to emit clean JSON tool calls rather than attempting arithmetic in autoregressive tokens.
     - *Task C (Span-Grounded Citations):* Training on document-to-memo pairs where every factual predicate requires an exact document span pointer `[Doc: Page X, Line Y: "..."]`.
2. **Staged Prompts (Pseudo-Pipeline):**
   - The monolithic model's prompt execution is broken into deterministic, checkpointed phases:
     - Stage 1: Document Entity Extraction (structured JSON).
     - Stage 2: Policy & Regulatory Check (reconciliation against SBP/PR rules).
     - Stage 3: Narrative Memo Synthesis (citing only Stage 1 and Stage 2 outputs).

### 4.2 Arm 2: Hardened MAS-FP16 (Specialist Team)
To eliminate multi-agent failures (M1–M14) without quantizing weights, the multi-agent system implements the **Adaptive Hierarchical with Dynamic Pruning & Structured Communication (AHDS)** framework:

1. **Zero Conversational Dialogue (Strict JSON Contracts):**
   - Agents are prohibited from communicating via conversational prose. All inter-agent handoffs use strictly typed JSON schemas (validated via Pydantic).
   - If the Extractor encounters an unreadable scan or omitted record, it serializes `"status": "MISSING"`. Downstream agents are programmatically restricted from drafting narrative assertions for fields marked missing.
2. **Independent Verifier Boundary Gate (Markov Snowball Breaker):**
   - A dedicated Verifier Agent (FP16) operates between drafting and human delivery:
     - Programmatically parses all currency amounts, dates, entity names, and debt ratios from the drafted memo.
     - Performs exact and fuzzy string matches against the Extractor's source document cache.
     - If an unverified assertion or hallucinated figure is detected, the draft is rejected and routed back for regeneration with an explicit error packet, or escalated with a warning banner to the compliance officer.
3. **Asymmetric Parameter Sizing:**
   - Following Żywot et al. (2026), orchestrator capacity is prioritized. The 16 GB layout below is the primary tier. The 8 GB and 32 GB layouts are in [§10](#10-models-quantization-and-hardware-by-tier).
     - **Orchestrator / Drafter:** Qwen2.5-3B-Instruct (FP16, ~6.2 GB).
     - **Extractor:** Qwen2.5-1.5B-Instruct (FP16, ~3.1 GB).
     - **Verifier:** Qwen2.5-0.5B-Instruct (FP16, ~1.0 GB).
     - **Retriever:** shared embedding index, not a fourth generative model.
     - **KV cache and runtime:** fit within the measured effective 16 GB-tier job cap after reserving OS/background RAM.
4. **Dynamic Token Budget Scheduler ($T_{\text{think}}$):**
   - An immutable token quota is apportioned across pipeline stages (e.g., Extractor: 30%, Drafter: 40%, Verifier: 30%), preventing token starvation and eliminating infinite debate loops.

---

## 5. Experimental Invariants & Parity Protocols

To ensure scientific validity and eliminate confounding variables, three strict invariants are maintained across all experiments:

### 5.1 RAM Utilization Parity Protocol (RUPP)
- **Primary Hardware Tier:** **16 GB System RAM** (standard compliance workstation).
- **Secondary Sensitivity Tiers:** **8 GB** (legacy laptops) and **32 GB** (power workstations).
- **Physical-memory reserve:** Do not treat the whole physical RAM tier as model memory. Reserve at least 20% for the OS and background tasks. Nominal aggregate process-tree RSS caps are 6.4 GB (8 GB tier), 12.8 GB (16 GB tier), and 25.6 GB (32 GB tier).
- **Host-adjusted cap:** Before runs, record idle non-job memory on the actual host. The effective process cap is $M_{\text{job}} = \min(0.8 M_{\text{tier}}, M_{\text{host}} - M_{\text{idle}} - 1\text{ GB})$. If this is lower than the nominal cap, both arms use that lower cap. Never increase it to fit a model.
- **Peak RSS invariant:**
  $$\text{RSS}_{\text{peak, process tree}} = M_{\text{weights}} + M_{\text{KV-cache}} + M_{\text{runtime}} \le M_{\text{job}}$$
- Record host-wide available memory before and during every run and stop if the reserved OS/background headroom is breached. The cap is an upper bound; there is no target utilization percentage.
- **Residency Modes:** Primary analysis mandates **concurrent resident memory** (all sub-models remain loaded simultaneously in RAM). A secondary **sequential swap mode** (loading/unloading models per stage) is reported separately to reflect memory-constrained consumer laptops.

### 5.2 Thinking-Token Parity ($T_{\text{think}}$)
- In accordance with Tran & Kiela (2026), the cumulative generation and reasoning tokens per task instance are capped at an identical budget:
  $$T_{\text{think}}(\text{SAS}) = \sum_{k=1}^K T_{\text{think}}(\text{Agent}_k) = T_{\text{budget}}$$
- Budget tiers evaluated: $T \in \{1024, 2048, 4096\}$ tokens.

### 5.3 Tool & Environment Parity
Both arms interact with the exact same mocked local deterministic tools via Berkeley Function-Calling (BFCL) compliant JSON interfaces:
1. `document_extractor(doc_id, field_list)`: Extracts text chunks and bounding tables.
2. `policy_retriever(query, jurisdiction)`: Returns permissioned regulatory clauses (SBP PRs, AML Act, FATF).
3. `financial_calculator(operation, **kwargs)`: Deterministically computes financial ratios (e.g., DBR, DSCR, Leverage). LLMs are strictly forbidden from performing free-form arithmetic.
4. `citation_verifier(claim_span, source_doc_id)`: Validates text substring alignment.

---

## 6. Benchmark Datasets & Task Tracks

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Benchmark Task Tracks                           │
├───────────────────────────────────┬────────────────────────────────────┤
│ Track A: Mortgage Origination     │ Track B: KYC / CDD Onboarding      │
│ MortarBench (2026)                │ Synthetic Customer Packs           │
│ Underwriting Q&A over bank        │ Discrepancy detection between      │
│ statements, ULAD, and payroll.    │ CNIC/ID, tax filings, and company  │
│                                   │ registry disclosures.              │
├───────────────────────────────────┼────────────────────────────────────┤
│ Track C: Credit Approval Memos    │ Track D: Negative Control          │
│ Corporate Credit Spread Sheets    │ FRAMES / MuSiQue Slice             │
│ Financial spreading, covenant     │ Multi-hop factual reasoning        │
│ checking, and narrative drafting. │ without external documents;        │
│                                   │ monolith hypothesized to win.      │
└───────────────────────────────────┴────────────────────────────────────┘
```

1. **Track A — Mortgage Origination Reasoning (MortarBench, 2026):**
   - Complex document Q&A over synthetic, distribution-faithful borrower files: bank account statements, payroll stubs, and Uniform Loan Application Dataset (ULAD) forms.
   - Target: Accurate boolean underwriting decisions, account lists, and income reconciliation.
2. **Track B — KYC / CDD Onboarding & Entity Resolution:**
   - 100 held-out synthetic case packs (the test slice). A further 500 packs from different generator seeds are train and dev only. Counts and the leakage rule are in [§12](#12-datasets-train-dev-and-test). Packs represent individual and corporate accounts under Pakistan SBP AML/CFT rules as the worked example:
     - CNIC/SNIC national identity documents.
     - FBR Active Taxpayer List (ATL) filings and NTN certificates.
     - SECP Form 29 / Form A corporate shareholding and Ultimate Beneficial Owner (UBO) structures.
   - Intentionally injected discrepancies: name mismatches, expired documents, undisclosed PEP relationships, and sanctions watchlist matches.
3. **Track C — Commercial Credit Approval Memo Drafting:**
   - 75 synthetic small-and-medium enterprise (SME) loan applications:
     - Audited balance sheets, profit and loss statements, and cash flows.
     - Central credit bureau reports (e-CIB).
   - Target: Synthesizing an audit-ready credit memorandum with cited financial covenants.
4. **Track D — Negative Control Track (FRAMES Multi-Hop Slice):**
   - 100 multi-hop reasoning questions without document grounding.
   - Scientific Purpose: Serves as an essential control to confirm the boundary conditions. Under pure parametric multi-hop reasoning, SAS-Quant is expected to outperform MAS-FP16 due to the Data Processing Inequality.

---

## 7. Metrics & Statistical Evaluation Framework

Standard NLP benchmarks (e.g., MMLU-Pro, BLEU, ROUGE) are poorly correlated with compliance risk. Project Agere evaluates systems using **grounding-centric, compliance-aligned metrics**:

| Metric | Formal Definition | Target Compliance Risk |
| :--- | :--- | :--- |
| **Grounding Accuracy** | $\frac{\text{Number of Claims with Verified Source Spans}}{\text{Total Factual Claims Drafted}} \times 100\%$ | Eliminates unsubstantiated narrative claims in credit and KYC files. |
| **Invention Rate** | $\frac{\text{Cases with Hallucinated Figures, Dates, or Names}}{\text{Total Cases Evaluated}} \times 100\%$ | Zero tolerance for fabricated financial numbers, tax IDs, or clearance statuses. |
| **Mismatch Recall** | $\frac{\text{Planted Discrepancies Correctly Flagged}}{\text{Total Planted Document Discrepancies}} \times 100\%$ | Prevents compliance oversight (e.g., missed PEP, altered ID, e-CIB default). |
| **Refusal Correctness** | $\frac{\text{Omitted Fields Correctly Refused / Flagged UNKNOWN}}{\text{Total Intentionally Omitted Document Fields}} \times 100\%$ | Enforces compliance refusal discipline under incomplete documentation. |
| **Token Efficiency** | $\frac{\text{Task Accuracy Score}}{T_{\text{think}} / 1000}$ | Quantifies reasoning efficiency per unit of test-time compute. |
| **Wall-Clock Latency** | End-to-end seconds per case file on CPU runtime | Measures analyst throughput on corporate workstations. |

### Statistical Testing Protocol:
- **Repetitions:** All experiments are conducted across 3 fixed random seeds ($42, 123, 999$).
- **Significance Testing:** Paired binary case outcomes (MAS vs. SAS) evaluated using **McNemar's test** ($\chi^2$).
- **Continuous Metrics:** Bootstrap 95% confidence intervals (1,000 resamples) computed for Grounding Accuracy and Invention Rate.
- **Factorial Interaction Analysis:** When the full 2×2 factorial (Cells A, B, C, D) is evaluated, two-way ANOVA is utilized to test the significance of the interaction term:
  $$\Delta_{\text{interaction}} = [\text{Score}(D) - \text{Score}(C)] - [\text{Score}(B) - \text{Score}(A)]$$

---

## 8. Experimental Execution Roadmap

```
Phase 1: Environment & Tooling Setup
├── Install CPU-first inference runtime (llama.cpp / Ollama / PyTorch)
├── Implement unified tool wrappers (Pydantic schema definitions)
└── Validate peak RSS memory profiler (psutil / system monitor)

Phase 2: Baseline Execution (Unadapted)
├── Execute SAS-Quant (Vanilla Q4_K_M) across Tracks A, B, C, D
├── Execute MAS-FP16 (Naive chat pipeline) across Tracks A, B, C, D
└── Freeze baseline scores; perform error triage (S1–S12, M1–M14)

Phase 3: Domain Adaptation & Hardening
├── Fine-tune SAS-Quant with QLoRA on refusal/tool/citation dataset
├── Implement AHDS structured JSON contracts for MAS-FP16
└── Integrate independent Verifier boundary gate in MAS-FP16

Phase 4: Primary Comparative Evaluation
├── Run hardened SAS-Quant vs. hardened MAS-FP16 on 16 GB tier
├── Measure Grounding Accuracy, Invention Rate, and Mismatch Recall
└── Run Track D negative control to test boundary hypotheses

Phase 5: Ablation Studies & Final Synthesis
├── Ablate Verifier gate, QLoRA adapter, and schema contracts
├── Compile statistical significance tests and confidence intervals
└── Formulate concrete IT deployment decision framework for publication
```

---

## 10. Models, Quantization, and Hardware by Tier

One model family is used on both arms so the comparison is architecture and precision, not “Qwen versus Llama.” The family is **Qwen2.5-Instruct**. A second family is out of scope unless the primary 16 GB result is already in hand.

Sizes below are llama.cpp GGUF footprints (weights only). KV cache and the process runtime sit on top. Physical RAM is not the inference budget: reserve 20% of the tier for the OS/background baseline, then lower the nominal cap if the actual host's idle use plus a 1 GB safety margin needs more. Before a tier is locked, a one-case smoke test records process-tree peak RSS and host-wide available memory. If peak RSS exceeds the effective cap, lower context or shrink the smallest worker. The orchestrator is not the first model to shrink.

The **tier** describes physical RAM on the analyst machine we claim to represent. The **job cap** is at most 80% of that RAM and may be lower after measuring the lab host's idle use. The **lab host** may be larger; `systemd` / `ulimit` / a cgroup holds the aggregate job process tree to the effective cap so extra RAM cannot become an unreported advantage. Both arms use the same effective cap.

| | **T1 — 8 GB** | **T2 — 16 GB (primary)** | **T3 — 32 GB** |
| :--- | :--- | :--- | :--- |
| **What it represents** | Legacy analyst laptop | Standard bank workstation | Team-lead / power desktop |
| **SAS-Quant model** | Qwen2.5-**7B**-Instruct | Qwen2.5-**14B**-Instruct | Qwen2.5-**32B**-Instruct |
| **SAS quant** | GGUF **Q4_K_M** (~4.7 GB) | GGUF **Q4_K_M** (~9.0 GB) | GGUF **Q4_K_M** (~20 GB) |
| **Nominal aggregate job RSS cap** | **6.4 GB** (lower if host-adjusted cap requires) | **12.8 GB** (lower if host-adjusted cap requires) | **25.6 GB** (lower if host-adjusted cap requires) |
| **MAS-FP16 resident team** | Orchestrator **1.5B** FP16 (~3.1 GB); Extractor **0.5B** FP16 (~1.0 GB); Verifier **0.5B** FP16 (~1.0 GB) | Orchestrator/Drafter **3B** FP16 (~6.2 GB); Extractor **1.5B** FP16 (~3.1 GB); Verifier **0.5B** FP16 (~1.0 GB) | Orchestrator **7B** FP16 (~15 GB); Extractor **3B** FP16 (~6.2 GB); Verifier **0.5B** FP16 (~1.0 GB) |
| **Retriever (both arms)** | `bge-small` embedding, same index, counted inside the RSS cap | same | same |
| **Rough weight sum, MAS** | ~5.1 GB | ~10.3 GB | ~22.2 GB |
| **Context at eval** | 4,096 tokens | 8,192 tokens | 8,192 tokens |
| **Primary token cap** | 2,048 thinking tokens | 2,048 thinking tokens | 2,048 thinking tokens |

Q4_K_M is the quant on every SAS tier. We do not switch the 8 GB machine to Q2 or the 32 GB machine to Q8 for the headline table. Q5_K_M on the same SAS checkpoint is a sensitivity run only, and only when the smoke test shows the Q4 peak RSS is far under the cap. Q3 and below are not a competing system (gap S12).

### Hardware required to run each tier

| | **T1 — 8 GB** | **T2 — 16 GB** | **T3 — 32 GB** |
| :--- | :--- | :--- | :--- |
| **Deployment machine the paper talks about** | 8 GB RAM, 4 CPU cores, no discrete GPU, HDD or SATA SSD | 16 GB RAM, 4–8 cores (Core i5/i7 class), integrated graphics, SATA SSD | 32 GB RAM, 8+ cores, SSD |
| **Lab host we prefer** | 16 GB RAM PC, job capped at ≤6.4 GB RSS (possibly lower) | 32 GB RAM PC, job capped at ≤12.8 GB RSS (possibly lower) | 64 GB RAM PC, job capped at ≤25.6 GB RSS (possibly lower) |
| **Minimum lab host if nothing larger exists** | The 8 GB PC itself, text-only Linux, browser closed; lower cap if idle use requires | The 16 GB PC itself, text-only session, browser closed; lower cap if idle use requires | The 32 GB PC itself; lower cap if idle use requires |
| **CPU** | x86-64 with AVX2 | AVX2; AVX-512 helpful, not required | AVX2 |
| **GPU for inference** | None. Inference is CPU, llama.cpp | None | None |
| **GPU for fine-tuning this tier’s SAS** | ≥12 GB VRAM for 7B QLoRA | ≥24 GB VRAM for 14B QLoRA | ≥48 GB VRAM for 32B QLoRA |
| **If that GPU does not exist** | Train the 7B QLoRA with CPU offload and accept a long run, or train on any lab GPU that can hold 7B NF4 | Do not pretend to QLoRA a 14B on a 16 GB CPU. Use the lab’s best GPU, or fine-tune a 7B Q4 stand-in and label it as such. The 14B Q4 baseline still runs | 32B QLoRA is optional. The required 32 GB result is the Q4_K_M base plus the same prompt, schema, and tool gates as 16 GB. A LoRA is added only if a large GPU is actually available |

MAS FP16 models at 0.5B–3B can be LoRA-tuned on a 12 GB GPU, or slowly on CPU. Their adapters, if trained, are role-specific (see [§13](#13-mas-failure-modes-and-the-fix-for-each), M12). The verifier’s pass/fail decision is a checklist plus string match; it is not a free-form “looks good” sample.

---

## 11. Quantization Method and Fine-Tuning Procedure

### 11.1 Method under test

**Inference quant: GGUF Q4_K_M (llama.cpp).** This is the file a bank actually downloads in Ollama. AWQ (Lin et al., MLSys 2024) is the paper that justifies 4-bit by protecting salient channels. AWQ’s fast kernels are for GPUs. This study’s machines are CPU workstations, so the deployed object is Q4_K_M, not an AWQ GPU checkpoint.

**Training quant: QLoRA NF4** (Dettmers et al., 2023) with double quantization, LoRA rank 16, alpha 32, dropout 0.05, on `q,k,v,o,gate,up,down`. Compute dtype is BF16 on a GPU that supports it, otherwise FP16. Optimizer is 8-bit AdamW, learning rate `2e-4`, cosine schedule, 3% warmup, 2–3 epochs, early stop on the **dev invention rate**, not on training loss. Sequence length 2,048 for field and tool examples; 4,096 for memo examples only if the GPU still has headroom. Effective batch size 16 via gradient accumulation.

### 11.2 Why the fine-tune is re-quantized

The adapter is trained on NF4, merged into a 16-bit model, then **converted back to GGUF Q4_K_M**. The evaluated SAS is never the merged 16-bit model. Otherwise the “quantized” arm would quietly spend more RAM than the tier and the comparison would be void.

```
HF 16-bit base
    → QLoRA (NF4 + LoRA) on the training mixture
    → merge adapter into 16-bit weights
    → llama.cpp convert → GGUF Q4_K_M
    → smoke-test peak RSS inside the tier
    → only then enter Phase 4
```

### 11.3 What the fine-tune teaches

The mixture is the use case, not generic finance prose. Shares are by example count:

| Share | Skill | Target behaviour |
| :--- | :--- | :--- |
| 40% | Missing data | Emit `MISSING` or `UNVERIFIED_IN_SOURCE`. Do not invent a CNIC date, an NTN, a deposit, or an e-CIB status. |
| 30% | Tools | Emit a schema-valid call to `financial_calculator` or `document_extractor`. No arithmetic in prose. |
| 30% | Citations | Every amount, date, and name in the draft carries a span id that exists in the packet. |

A staged prompt (extract JSON → policy check → memo) is applied to SAS as well, so MAS does not win only because it was given a pipeline and SAS was given one blob of instructions.

### 11.4 MAS adapters

Role LoRAs are optional and small:

- **Extractor:** field JSON only.
- **Drafter:** memo text that may cite only ids already in the JSON packet.
- **Verifier:** trained, if at all, on binary `PASS`/`FAIL` with hard negatives (a fluent memo that changes one digit). It is not trained to rewrite the memo.
- **Orchestrator:** prompt and schema only, unless the dev set shows it drops stages.

If a role LoRA does not improve the dev set, it is discarded and the base FP16 checkpoint stays. Dead adapters are not kept to make the system look more “fine-tuned.”

---

## 12. Datasets: Train, Dev, and Test

No real customer file is used. Training and test are split by generator seed and then frozen. The test manifest (file names and SHA-256) is written to the repository **before** the first training step. Dataset files stay on the external SSD. Anything hashed as test is never in a training batch.

The first deterministic implementation is `scripts/prepare_project_datasets.py` (`agere-synth-v1`). It writes the specified KYC/credit counts plus a 600-row train SFT mixture and 60-row dev SFT set beneath `AGERE_SSD_ROOT/datasets/`; their hashes and split counts are stored in repository manifests. The SFT rows are generated from train cases only, and dev rows come from dev cases only. This is a starter corpus and must pass the dataset-quality review in `ROADMAP.md` §0.5 before it supports paper results or a model fine-tune.

| Corpus | What it is | Train | Dev (hardening) | Test (judgement) |
| :--- | :--- | :--- | :--- | :--- |
| **Agere-KYC-Synth** | CNIC/SNIC, NTN, ATL line, SECP-style shareholding, sanctions hit or clean bill. Planted mismatches and blank fields. | 400 cases | 100 | 100 (Track B) |
| **Agere-Credit-Synth** | SME statements, e-CIB lines, memo template. Ratios come from the calculator, not from the labeler’s head. | 200 cases | 50 | 75 (Track C) |
| **MortarBench** | Mortgage origination questions over statements, payroll, ULAD-style fields (paper 45). | **none** | small slice only if the authors allow a dev cut | Track A, the rest |
| **MortarBench-style pack** | Built only if the official set cannot be obtained. Same question types as the paper. Disclosed as style-alike, not as the official score. | none | 20 | 80 |
| **FRAMES or MuSiQue slice** | Multi-hop questions, no case documents (paper 33, or MuSiQue). | **none** | none | 100 (Track D) |
| **Tool-format supplement** | A few hundred BFCL-style calls rewritten to our four tools. Teaches JSON shape. | yes | yes | not a reported finance score |
| **Policy index** | Public SBP prudential excerpts, FATF recommendation text, a synthetic bank SOP. Same index mounted for both arms. | index only | index only | index only |

Dev is where we stop training, tune the verifier threshold, and decide whether an adapter stays. Test is touched once per frozen system, three seeds, and not used to pick prompts.

MortarBench and FRAMES are pinned external datasets staged beneath `AGERE_SSD_ROOT/datasets/external/`; MortarBench's complete test JSONL is secondary, and a deterministic 100-question FRAMES slice is frozen separately. The fine-tuning mixture is project-generated, not downloaded from a public data host. Public SBP/FATF policy sources used to build the retriever index are separate input artifacts and must be versioned on the SSD before policy-grounded runs.

---

## 13. MAS Failure Modes and the Fix for Each

These are the MAST-aligned gaps in [`SYSTEM_GAPS_AND_IMPROVEMENTS.md`](./SYSTEM_GAPS_AND_IMPROVEMENTS.md). Each P0 item is in the system that reaches Phase 4. A P1 item can be deferred only with a one-line reason in the run log.

| ID | Problem on a KYC or credit file | Fix |
| :--- | :--- | :--- |
| **M1** | Agents disagree on what “case complete” means | One written SOP and one JSON schema of done-ness, held by the orchestrator. |
| **M2** | Extractor softens “unknown”; drafter invents the field | JSON only between stages. `MISSING` is a value. The drafter template has no slot that can be filled from thin air. |
| **M3** | One bad amount is copied into every later agent | Verifier between stages. A failed quote-check rejects the draft. |
| **M4** | Downstream agent forgets “cite or refuse” | Workers are stateless. The constraint packet is reattached on every call. Chat history is not the memory. |
| **M5** | Retriever returns another product’s policy | The packet carries product, jurisdiction, and document ids. Retrieval filters on those fields. |
| **M6** | Agents debate until the token budget is gone | No debate topology. One forward pass per role, plus at most one repair pass if the verifier fails. |
| **M7** | Critic rewrites prose and never checks the quote | Verifier does deterministic span match. Fuzzy match is logged separately from exact match. |
| **M8** | Team spends the budget before verify | Scheduler: extractor 30%, retriever 10%, drafter 40%, verifier 20% of \(T_{\text{think}}\). Verify is reserved first, not last. |
| **M9** | All agents resident causes swap, or sequential mode is quieter than it looks | Primary number is resident peak RSS. Sequential load/unload is a second table, labelled as such. |
| **M10** | Orchestrator skips the mismatch check | Orchestrator is the largest model in the team. The stage list is code, not a suggestion in the prompt. |
| **M11** | Two agents extract the same PDF differently | One case store. Only the extractor calls `document_extractor`. |
| **M12** | Roles are names on a general chat model | Role prompts plus the optional role LoRAs in [§11.4](#114-mas-adapters). |
| **M13** | Verifier always says the draft is fine | Binary checklist, hard negatives, and a rule that `PASS` requires every amount to match a span. |
| **M14** | Hard to debug | One JSON log line per stage in the repository, including token counts and RSS. |

SAS receives the matching hardening so the team is not compared with a crippled monolith: domain QLoRA (S1, S2), staged prompts (S3), calculator-only amounts (S4), schema-limited tools (S5), span ids (S6), a deterministic mismatch diff (S7), chunked extract when the pack is long (S8), a fixed memo template (S9, S10), and a client-scoped index (S11). Quant level stays Q4_K_M (S12).

---

## 14. Judgement Basis

**Final evaluation datasets.** The score that decides the paper is the frozen test split of **Agere-KYC-Synth** (Track B, 100 cases) and **Agere-Credit-Synth** (Track C, 75 cases), pooled. Primary metric: invention rate. Co-primary: mismatch recall on planted conflicts. **MortarBench** (Track A) is secondary. **FRAMES or a MuSiQue slice** (Track D, 100 questions) is a control and does not pick the winner. Dev is not the final evaluation. Test is one shot per frozen system.

Both systems see the same cases, the same tools, the same \(T_{\text{think}}\), and the same RSS cap. The primary tier is **16 GB, resident mode, 2,048 thinking tokens, hardened systems**. 8 GB and 32 GB say whether the 16 GB result moves when the machine changes. Latency is reported and does not pick the winner.

| Priority | Measure | Direction | Where |
| :--- | :--- | :--- | :--- |
| **Primary** | Invention rate | Lower is better | Tracks B and C, pooled |
| **Co-primary** | Mismatch recall | Higher is better | Planted conflicts in B and C |
| **Secondary** | Grounding accuracy | Higher is better | A, B, C |
| **Secondary** | Refusal correctness | Higher is better | Blank fields in B and C |
| **Secondary** | Per-type F1 | Higher is better | Track A (MortarBench question types) |
| **Control** | Exact match | Reported, not the claim | Track D. A large MAS win here is treated as a bug until explained. |
| **Reported, not decisive** | Tokens used, peak RSS, wall-clock | Parity checks | All tracks |

A case is paired. The same case id is run on SAS and on MAS. Binary outcomes use McNemar’s test. Invention rate and grounding accuracy get a bootstrap 95% interval, 1,000 resamples, seeds 42, 123, and 999. The paper states the 16 GB primary result first. A win on one secondary metric does not override a loss on invention rate.

Naive scores stay in the paper as the floor. They are not the headline comparison.

---

## 15. Making Both Systems as Strong as They Can Be

“As strong as they can be” means as strong as this protocol allows, not an open-ended prompt search on the test set.

1. **Freeze the naive run first.** Off-the-shelf Q4_K_M and the chatty MAS are scored on dev and then left alone. Later gains have to beat that floor.
2. **Equal hardening budget.** Each arm gets the same number of engineering passes on dev (three passes). A pass is one change set: an adapter, a schema, or a gate. The pass is kept only if dev invention rate or mismatch recall improves and the other does not collapse.
3. **P0 gaps are attempted on both arms** before Phase 4 (SAS S1–S7, MAS M1–M8). A skipped P0 item needs a written reason.
4. **Early stop on dev.** Training stops when dev invention rate has not improved for one epoch. Prompt edits stop when a pass does not move dev.
5. **Test is one-shot** per frozen configuration. If a test result tempts a change, that change is a new system and the old one stays in the table.
6. **Shared bugs are shared fixes.** A bad calculator or a bad parser is patched for both arms in the same commit.
7. **Parity is measured, not assumed.** Every case log stores thinking tokens and peak RSS. A run outside the cap is discarded, not averaged in.
8. **Ablations after the headline.** Turn the QLoRA off, turn the verifier off, turn JSON contracts off. The kept pieces are the ones that moved dev. This is how the paper shows the work was necessary.
9. **Stop condition for Phase 4.** Dev metrics exist for both arms, three seeds agree in direction, Track D has been run, and the checklist in [`SYSTEM_GAPS_AND_IMPROVEMENTS.md`](./SYSTEM_GAPS_AND_IMPROVEMENTS.md) §5 is ticked.

---

## 16. External SSD and Repository Storage

The external SSD is an artifact drive, not a project drive. It stores only the large inputs and model artifacts: datasets and their derived data indexes/caches, downloaded source weights, converted/quantized weights, trained adapters, and merged weight files. **No source code, runtime/build files, logs, manifests, evaluation outputs, or reports belong on the SSD.** All of those stay under the repository checkout on the laptop/PC/lab machine and are committed or backed up with the repository as appropriate.

### Per-run path requirement

- Before starting any phase, dataset operation, training job, evaluation, or other run, set `AGERE_SSD_ROOT` to the correct absolute mount path for the external SSD on that machine.
- The runner prints the resolved repository root and SSD root, verifies the SSD is mounted and contains the expected `weights/` and/or `datasets/` inputs, and refuses to run if the path is unset, stale, or invalid.
- Point model-hub/download caches (such as `HF_HOME` and `HF_HUB_CACHE`) under `AGERE_SSD_ROOT/weights/` and dataset loaders under `AGERE_SSD_ROOT/datasets/`; do not let libraries silently cache these large artifacts on the machine's system drive.
- Never silently fall back to a same-named folder on the local disk. Model and dataset inputs must resolve beneath `AGERE_SSD_ROOT`; code and every output must resolve beneath the repository root.
- The exact mount point may differ across computers, so pass the current machine's path rather than assuming `/mnt/agere` or a particular Windows drive letter.

### SSD layout

```
AGERE_SSD_ROOT/
  weights/
    hf/                 # downloaded official model snapshots
    gguf/               # converted and quantized model weights
    adapters/           # trained adapter weights and merged model weights
  datasets/
    train/
    dev/
    test/               # immutable after the test manifest is committed
    derived/            # dataset-derived indexes/caches only
```

### Repository layout for code and results

```
<repository>/
  src/                  # all project source code
  third_party/          # local source/build for runtime tools when needed
  configs/              # configs refer to artifacts beneath AGERE_SSD_ROOT
  manifests/            # artifact hashes, dataset/test hashes, runtime versions
  runs/                 # per-run JSON logs, traces, memory/token records
  experiments/          # scored evaluations and analysis inputs
  results/              # summaries, figures, and reports
```

Each source or processed weight file gets a SHA-256 entry in the repository's `manifests/weights.sha256`. The frozen test dataset manifest lives in the repository's `manifests/test.sha256` before training starts. Logs and evaluation outputs are written under the repository throughout; do not stage them on the SSD and copy them later.

The SSD must be mounted and its path checked at the start of every phase/run. Unmount before unplugging it. Keep a backup copy of the datasets and weights; repository backups cover code, manifests, logs, and evaluation results.

---

## 17. Ethical & Compliance Considerations

1. **Synthetic Data Integrity:** All KYC records, tax forms, CNICs, financial statements, and company documents used in this study are 100% synthetically generated. No genuine customer Personally Identifiable Information (PII) or proprietary bank data is contained in the repository.
2. **Human-in-the-Loop Principle:** In accordance with financial supervisory standards, AI outputs generated by both SAS and MAS architectures are strictly treated as **draft work-in-progress**. The system includes explicit disclaimers: AI models must never autonomously approve credit facilities, assign final AML risk ratings, or file regulatory Suspicious Transaction Reports (STRs). Sole decision-making authority remains with licensed human compliance officers and underwriters.
