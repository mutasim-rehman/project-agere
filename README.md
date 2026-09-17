# Project Agere: Local LLM Deployment for Regulated Finance

**Working title:** *Spend It Together or Spend It Big? Multi-Agent Full-Precision Teams vs. Quantized Monoliths on Analyst RAM*

## One-sentence pitch

Banks and funds that **cannot use cloud LLMs** on KYC and credit files default to **one large quantized model on the analyst PC**; we test whether a **team of smaller full-precision agents** is a better use of the **same RAM and thinking-token budget**.

→ Full application framing: [`APPLICATION.md`](./APPLICATION.md)  
→ Domain glossary & workflows: [`FINANCE_DOMAIN_CONTEXT.md`](./FINANCE_DOMAIN_CONTEXT.md)  
→ SAS vs MAS gap list & improve-then-compare loop: [`SYSTEM_GAPS_AND_IMPROVEMENTS.md`](./SYSTEM_GAPS_AND_IMPROVEMENTS.md)

---

## Core research question

> **Can a multi-agent system consisting of smaller, full-precision LLMs outperform a single larger, quantized LLM when both systems use the same peak resident system RAM and the same thinking-token budget?**

### Competing deployments (primary comparison)

| | **MAS-FP16** (team) | **SAS-Quant** (industry default) |
| :--- | :--- | :--- |
| **Architecture** | Orchestrated specialists (extract → retrieve → draft → verify) | One generalist model |
| **Precision** | Native FP16/BF16 sub-models | Post-training quant (GGUF Q4_K_M, etc.) |
| **RAM** | Peak RSS matched to tier | Peak RSS matched to tier |
| **Tokens** | Equal thinking-token cap per case ([Tran & Kiela, 2026](./sources/papers/01_Tran_2026_Single_Agent_LLMs_Outperform_Multi_Agent.pdf)) | Same cap |

### Optional extension (2×2 for reviewers)

Cells **A** (SAS-FP16) and **D** (MAS-Quant) complete a factorial to measure $\Delta_{\text{interaction}}$; the **headline claim** remains **C vs. B** under finance workflows—not a GPU benchmark tournament.

---

## Application area

| Field | Workflow | Why local |
| :--- | :--- | :--- |
| **KYC / CDD / EDD** | Case-file assembly, screening summary, discrepancy register | Customer PII must not leave the bank |
| **Credit memo drafting** | Spread + cite + narrative (human approves) | Borrower financials are confidential |
| **Mortgage origination checks** | Document Q&A (payroll match, large deposits) | Same + examinable tool traces |

**Beneficiary:** compliance-minded IT deploying **Ollama/llama.cpp on 16 GB analyst workstations**, not cloud agent vendors.

---

## Method (summary)

1. **RAM tiers:** 8 GB, 16 GB (primary), 32 GB — CPU-first inference.  
2. **RAM Utilization Parity Protocol (RUPP):** match **peak RSS** (weights + KV + runtime); report **resident** vs **sequential swap** MAS separately.  
3. **Token parity:** fixed thinking-token budget per task instance.  
4. **Tools:** identical extractors, policy RAG, and calculators for both arms.  
5. **Metrics:** grounding (citation accuracy), invented amounts, missed mismatches—not MMLU.  
6. **Benchmarks:** MortarBench-style origination Q&A + synthetic KYC/credit packs; FRAMES slice as **negative control** (monolith expected to win).

Protocol detail: [`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md)

---

## Literature review (curated)

| Doc | Content |
| :--- | :--- |
| [`literature_review/README.md`](./literature_review/README.md) | Master synthesis (finance-local focus) |
| [`literature_review/06_regulated_finance_local_llm.md`](./literature_review/06_regulated_finance_local_llm.md) | Application + regulatory + finance LLM gaps |
| [`sources/INDEX.md`](./sources/INDEX.md) | **16 active papers** (PDFs in `sources/papers/`) |
| [`sources/EXCLUDED_PAPERS.md`](./sources/EXCLUDED_PAPERS.md) | Former 43-paper set—dropped with rationale |

---

## Repository layout

```
APPLICATION.md                  # Who benefits (supervisor-facing)
FINANCE_DOMAIN_CONTEXT.md       # KYC/credit/mortgage + compliance glossary
SYSTEM_GAPS_AND_IMPROVEMENTS.md # Where SAS-Quant / MAS fail; fix backlog; compare loop
README.md                       # This file
EXPERIMENT_PROTOCOL.md          # RAM + token parity study spec
configs/                        # Hardware + system YAML (to be aligned to RAM tiers)
literature_review/              # Thematic synthesis + per-paper summaries (legacy summaries retained)
sources/
  papers/                       # Downloaded PDFs
  INDEX.md
  PAPERS_DICTIONARY.md
  regulatory/                   # FINRA/SEC pointers (non-PDF)
```

---

## Contributions (target)

1. First **RAM- and token-matched** comparison of **MAS-FP16 vs. SAS-Quant** on **regulated finance document workflows**.  
2. **Grounding-centric metrics** aligned with analyst review burden, not generic leaderboards.  
3. **Deployment guidance** for on-prem compliance teams: when to quantize-up vs. split RAM across roles.  
4. Optional: $\Delta_{\text{interaction}}$ if full 2×2 is run.
