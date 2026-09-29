# EXPERIMENT PROTOCOL: RAM- and Token-Matched Finance LLM Deployment Study

**Project:** Agere  
**Version:** 3.0 (Regulated finance / analyst RAM)  
**Status:** Specification  
**Application:** [`APPLICATION.md`](./APPLICATION.md)

---

## 1. Executive summary

**Primary comparison:** **MAS-FP16** (orchestrated specialists) vs **SAS-Quant** (single larger GGUF/Q4 model)—the default on-prem install in banks and funds.

**Invariants:**

1. **Memory ceiling:** Both arms use the same host-adjusted process-tree RSS cap per tier after reserving RAM for OS/background tasks (RUPP); measure and report each arm's actual peak RSS.
2. **Thinking-token budget** $T_{\text{think}}$ matched per task ([Tran & Kiela, 2026](./sources/papers/01_Tran_2026_Single_Agent_LLMs_Outperform_Multi_Agent.pdf)).  
3. **Identical tools** (extract, search policy corpus, calculator, citation checker).  
4. **Human-in-the-loop:** systems produce drafts only; no automated approval.

**Runtime:** llama.cpp or Ollama on **CPU** (optional GPU noted as sensitivity analysis, not primary).

---

## 2. Research questions

| ID | Question |
| :--- | :--- |
| **RQ0 (headline)** | Does **MAS-FP16** outperform **SAS-Quant** on finance document workflows under the same host-adjusted RSS ceiling and $T_{\text{think}}$? |
| **RQ1** | Replication: does **SAS-Quant** beat **SAS-FP16** under the same host-adjusted process RSS ceiling? (Bench360 control) |
| **RQ2** | Optional factorial: $\Delta_{\text{interaction}}$ if Cells A and D are run |
| **RQ3** | Does advantage flip on **negative-control** multi-hop (no documents)? |

---

## 3. RAM tiers

| Tier | Physical RAM | Nominal process-tree RSS cap | Example | Primary? |
| :--- | :--- | :--- | :--- | :---: |
| T1 | 8 GB | **6.4 GB** | Legacy laptop | |
| T2 | **16 GB** | **12.8 GB** | Standard analyst PC | **Yes** |
| T3 | 32 GB | **25.6 GB** | Power workstation | |

**RUPP (RAM Utilization Parity Protocol):**

- Reserve at least 20% of tier physical RAM for OS/background tasks. The nominal aggregate process-tree RSS caps are 6.4 / 12.8 / 25.6 GB for the 8 / 16 / 32 GB tiers.
- Before each run, record actual host RAM, idle non-job use, and available memory. Effective cap is the smaller of 80% of tier RAM and host RAM minus idle non-job use and a 1 GB safety margin. If this reduces the nominal cap, use the lower cap for both arms; never raise the cap to make a model fit.
- Report **process-tree peak RSS** during a full case (weights + KV + runtime), host-wide available memory before/during the case, and the effective cap. Do not force either arm to use a target fraction of RAM.
- **MAS modes:** (a) *resident*—all agents loaded; (b) *sequential*—load/unload per stage (document real laptops). Both arms must declare mode; primary analysis uses **resident** for fairness, **sequential** as supplementary.

---

## 4. Systems under test

### 4.1 SAS-Quant (industry default)

- One instruct model at **Q4_K_M** sized to fit the effective process-tree RSS cap after reserving memory for the OS/background tasks. Q5_K_M is sensitivity only. No utilization target.
- Same system prompt + ReAct tool loop as MAS.

### 4.2 MAS-FP16 (specialist team)

Suggested topology (MetaGPT-style):

| Role | Responsibility |
| :--- | :--- |
| Orchestrator | Plan stages, enforce token budget |
| Extractor | Structured fields from PDFs/images |
| Retriever | Policy/regulation snippets (permissioned RAG) |
| Drafter | Case narrative with citations |
| Verifier | Quote match; flag invention |

Sub-models: Qwen2.5 at **FP16** for the locked comparison; the resident team is sized to fit under the same effective process-tree RSS cap as SAS-Quant. The cap is a ceiling applied to both arms, not a requirement that both consume equal memory. Start with the tier-specific team in the locked config, measure full-case process-tree RSS including KV cache and runtime, and reduce context or the smallest worker if the effective cap is exceeded.

### 4.3 Controls

- **Tool parity:** BFCL-validated schemas for both arms.  
- **Deterministic numerics:** credit ratios computed in Python; never LLM-generated.  
- **Seeds:** 42, 123, 999; report mean ± CI.

---

## 5. Tasks & datasets

| Track | Source | n (target) | Metrics |
| :--- | :--- | :--- | :--- |
| **A — Origination** | MortarBench-style Q&A | Full dev subset | Accuracy / F1 per category |
| **B — KYC pack** | Synthetic + public template docs | 100–200 cases | Field F1, mismatch recall |
| **C — Credit memo** | Synthetic financials + memo template | 50–100 | Citation accuracy, invention rate |
| **D — Negative control** | FRAMES or MuSiQue slice | 100 | Accuracy (expect SAS-Quant ↑) |

---

## 6. Metrics (finance-first)

| Metric | Definition |
| :--- | :--- |
| **Grounding accuracy** | % claims with correct source span |
| **Invention rate** | % cases with hallucinated amount/date/name |
| **Mismatch recall** | % injected ID/registry conflicts flagged |
| **Token efficiency** | Task success / $T_{\text{think}}$ |
| **Latency** | Wall-clock per case (report separately) |

---

## 7. Statistical analysis

- McNemar per case for paired binary outcomes (MAS vs SAS).  
- Bootstrap CIs on invention rate.  
- ANOVA for optional 2×2 if Cells A–D completed.  
- Pre-register **16 GB** as primary tier.

---

## 8. Ethics & compliance (study conduct)

- No real customer PII in repo; synthetic KYC only.  
- Human subjects: analyst time studies optional with IRB if needed.  
- Paper states clearly: **not** a compliance certification.

---

## 9. Deliverables

1. RAM–token deployment matrix for compliance IT.  
2. Open configs under `configs/` (to be aligned to RUPP).  
3. Error taxonomy tagged with MAST categories.
