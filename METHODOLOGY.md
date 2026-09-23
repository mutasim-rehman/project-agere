# METHODOLOGY: Project Agere
## Spend It Together or Spend It Big?
### Multi-Agent Full-Precision Teams vs. Quantized Monoliths on Analyst Workstation RAM for Regulated Finance

**Document Version:** 1.0  
**Date:** September 2026  
**Status:** Approved Specification  
**Project Repository:** Project Agere (`/workspace`)  
**Related Documents:** [`APPLICATION.md`](./APPLICATION.md) · [`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md) · [`SYSTEM_GAPS_AND_IMPROVEMENTS.md`](./SYSTEM_GAPS_AND_IMPROVEMENTS.md) · [`FINANCE_DOMAIN_CONTEXT.md`](./FINANCE_DOMAIN_CONTEXT.md) · [`sources/INDEX.md`](./sources/INDEX.md)

---

## 1. Executive Summary & Research Motivation

### 1.1 The Core Research Question
> **Can a Multi-Agent System consisting of smaller, full-precision LLMs (MAS-FP16) outperform a single larger, quantized LLM (SAS-Quant) when both systems are strictly constrained to the same peak resident system RAM and the same thinking-token budget on regulated financial document workflows?**

### 1.2 The Real-World Deployment Dilemma
In commercial banks, asset managers, and financial institutions operating under strict regulatory regimes (e.g., FINRA Notice 24-09, SEC 17a-4, GDPR, DORA, and State Bank of Pakistan AML/CFT directives):
- **Cloud APIs are Legally Prohibited:** Customer Personally Identifiable Information (PII), confidential credit packs, tax records, and sanctions screening hits cannot be transmitted across corporate perimeters or national borders to public cloud endpoints (OpenAI, Anthropic, Google).
- **Workstation Compute Realities:** Compliance officers and credit underwriters execute local CPU-first inference (via `llama.cpp` or `Ollama`) on standard **16 GB RAM** corporate workstations without enterprise datacenter GPUs.
- **The Prevailing Industry Default:** IT departments default to downloading the largest open-weights model that can fit into RAM when aggressively quantized (e.g., 14B parameter model compressed to 4-bit integer weights like GGUF `Q4_K_M`).
- **The Core Scientific Hypothesis:** Rather than spending the 16 GB memory budget on one compressed generalist, allocating the same RAM across an orchestrated team of smaller, native full-precision (FP16/BF16) specialized agents (e.g., 3B Orchestrator/Drafter + 1.5B Extractor + 1.5B Verifier) yields higher grounding accuracy, lower hallucinated amount rates, and superior regulatory compliance.

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
│ - Hardware limits: 16 GB Peak RAM (RUPP), CPU-first execution               │
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
   - Following Żywot et al. (2026), orchestrator capacity is prioritized:
     - **Orchestrator / Drafter:** Qwen2.5-3B-Instruct (FP16, ~6.0 GB RAM).
     - **Extractor:** Qwen2.5-1.5B-Instruct (FP16, ~3.0 GB RAM).
     - **Verifier:** Qwen2.5-1.5B-Instruct (FP16, ~3.0 GB RAM).
     - **Runtime & KV-Cache Buffer:** ~3.0–4.0 GB RAM allocated to KV-cache and system overhead.
4. **Dynamic Token Budget Scheduler ($T_{\text{think}}$):**
   - An immutable token quota is apportioned across pipeline stages (e.g., Extractor: 30%, Drafter: 40%, Verifier: 30%), preventing token starvation and eliminating infinite debate loops.

---

## 5. Experimental Invariants & Parity Protocols

To ensure scientific validity and eliminate confounding variables, three strict invariants are maintained across all experiments:

### 5.1 RAM Utilization Parity Protocol (RUPP)
- **Primary Hardware Tier:** **16 GB System RAM** (standard compliance workstation).
- **Secondary Sensitivity Tiers:** **8 GB** (legacy laptops) and **32 GB** (power workstations).
- **Peak RSS Invariant:**
  $$\text{RSS}_{\text{peak}} = M_{\text{weights}} + M_{\text{KV-cache}} + M_{\text{runtime}} \le M_{\text{budget}}$$
- Both arms must utilize $\ge 85\%$ of the target hardware tier at peak execution to ensure fair resource saturation.
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
   - 150 synthetic, multi-document case packs representing individual and corporate accounts (incorporating Pakistan SBP AML/CFT regulations as a representative emerging-market framework):
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

## 9. Ethical & Compliance Considerations

1. **Synthetic Data Integrity:** All KYC records, tax forms, CNICs, financial statements, and company documents used in this study are 100% synthetically generated. No genuine customer Personally Identifiable Information (PII) or proprietary bank data is contained in the repository.
2. **Human-in-the-Loop Principle:** In accordance with financial supervisory standards, AI outputs generated by both SAS and MAS architectures are strictly treated as **draft work-in-progress**. The system includes explicit disclaimers: AI models must never autonomously approve credit facilities, assign final AML risk ratings, or file regulatory Suspicious Transaction Reports (STRs). Sole decision-making authority remains with licensed human compliance officers and underwriters.
