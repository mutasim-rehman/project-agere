# Thematic Synthesis: Regulated Finance & Local LLM Deployment

*Papers: 16, 22, 34, 36–38, 42, 44–45 + regulatory sources in [`../sources/regulatory/README.md`](../sources/regulatory/README.md)*

---

## 1. Why finance blocks cloud LLMs

**Data classes:** KYC identity documents, beneficial-ownership graphs, borrower financials, screening hits, draft SAR narratives, and (for advisers) MNPI-adjacent research—all are **high-sensitivity** and often **contractually restricted**.

**Regulatory pressure (U.S.):** FINRA Notice 24-09 applies existing supervision and recordkeeping to GenAI; firms remain responsible when using **third-party** models. Books-and-records rules imply **retention and audit** of prompts/outputs where communications are business-related.

**Control failure mode:** Skadden (2026) frames MNPI risk as **system design**: shared vector stores and permissive retrieval can contaminate strategies even without a “trade” by the model. Analogously, a KYC assistant that indexes multiple client folders without hard segregation is an exam finding.

**Deployment response:** Behind-the-firewall agents, on-prem RAG, and laptop Ollama/llama.cpp stacks—**inference stays inside the perimeter**.

---

## 2. Where LLMs are used in finance (our scope)

| Function | LLM role | Human gate |
| :--- | :--- | :--- |
| **KYC/CDD/EDD** | Extract fields, reconcile registry vs. CRM, summarise hits | Analyst approves onboarding |
| **AML case support** | Evidence summary, discrepancy list | MLRO; no auto SAR filing |
| **Credit memo** | Draft narrative from **pre-computed ratios** | Credit officer signs |
| **Mortgage origination** | Answer document questions (deposits, employment match) | Underwriter |

**Out of scope:** autonomous credit decisioning, execution/trading agents, high-frequency workflows.

---

## 3. The local deployment gap

**Industry default:** Fit the **largest quantized model** in RAM (Q4_K_M 7B–14B on 16 GB).

**Known failures:**

- **Hallucination under missing data** (JurisTech 2026 finance benchmark; industry guides ~80% reasoning accuracy compounding at scale).
- **Quantized agents amplify tool failures** (Jang et al. 2026).
- **Multi-agent handoffs** compound factual error unless bounded by verification (Jamshidi; Singh snowball).

**What prior finance LLM research did:**

- **Paper 44:** On **one local 8B**, retrieval/memory architecture beats naive scale for financial QA under SME constraints—it does **not** compare **MAS-FP16 vs SAS-Quant** at equal RAM.
- **MortarBench:** Origination **agent** tasks with SME expert filtering—it does **not** test RAM-matched team vs monolith.
- **Bench360:** Quantized **single** local models win vs small FP16—**no multi-agent arm**.

→ **Agere fills:** RAM + token parity, **MAS-FP16 specialist pipeline vs SAS-Quant monolith**, metrics = **grounding/invention**, domain = **KYC + MortarBench-style origination**.

---

## 4. Recommended system pattern (from literature)

```
Documents → [Extractor agent, FP16] → structured JSON
         → [Policy RAG, deterministic] → cited snippets
         → [Drafter agent, FP16] → case narrative
         → [Verifier agent, FP16] → quote-check / refuse
         → Human analyst (mandatory)
```

**SAS-Quant arm:** Same pipeline prompts in **one** Q4 generalist with equal tools and token cap.

**Design choices from excluded-but-cited practice:** Ratios and sanctions screening stay **deterministic** (credit-memo best practice); LLM never owns numeric truth.

---

## 5. Hypotheses (finance-specific)

| ID | Hypothesis |
| :--- | :--- |
| **H1** | On **tool-like extraction + verification** (KYC packs, MortarBench), **MAS-FP16** beats **SAS-Quant** at equal RAM/tokens (role buffering). |
| **H2** | On **closed-book multi-hop** negative control, **SAS-Quant** wins (parametric depth; DPI on handoffs). |
| **H3** | **Invented field rate** is lower for MAS-FP16 when verifier is separate (Singh boundary gates). |
| **H0** | No difference after parity—architecture and quantization are independent. |

---

## 6. Links to other thematic docs

- MAS vs SAS (general): [`01_mas_vs_sas_collaboration.md`](./01_mas_vs_sas_collaboration.md) — **read 01, 02, 07 only**; ignore GPU-centric claims.  
- Quantization: [`04_quantization_and_ondevice.md`](./04_quantization_and_ondevice.md) — **read AWQ + Bench360 sections**.  
- Benchmarks: [`05_benchmarks_and_evaluation.md`](./05_benchmarks_and_evaluation.md) — **BFCL + replace GAIA with MortarBench** in your head.
