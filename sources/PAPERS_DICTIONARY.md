# Active Papers Dictionary (16-Paper Corpus)

> **RQ:** Under equal **peak system RAM** and equal **thinking-token budget**, does **MAS-FP16** outperform **SAS-Quant** on regulated finance document workflows (KYC case files, credit memo drafts, mortgage origination Q&A)?

See [`INDEX.md`](./INDEX.md) for PDF paths. Excluded former papers: [`EXCLUDED_PAPERS.md`](./EXCLUDED_PAPERS.md).

---

## Agent parity & orchestration

| # | Paper | One-line role |
| :---: | :--- | :--- |
| **01** | Tran & Kiela 2026 | **Method template:** equal thinking tokens; MAS often loses on multi-hop—use as protocol, swap cloud for RAM parity. |
| **02** | Żywot et al. 2026 | Small tool-using teams can beat big models—**must equalize tools** for SAS vs MAS. |
| **03** | Kim et al. 2025 | Predicts when coordination overhead dominates (serial handoffs in KYC). |
| **07** | Cemri et al. 2025 (MAST) | Labels failure modes (context collapse, hallucination propagation) for diagnostics. |
| **11** | Hong et al. 2024 (MetaGPT) | Structured orchestrator–worker roles → KYC extract/draft/verify topology. |

## Budget & local hardware

| # | Paper | One-line role |
| :---: | :--- | :--- |
| **15** | Wang et al. 2024 (EMNLP) | Precedent for holding resource budgets invariant across conditions. |
| **16** | Lin et al. 2025 (Bench360) | **SAS-Quant wins vs small FP16** on local hardware—replicate as Cell B baseline. |
| **27** | Liu et al. 2024 (MobileLLM) | Design of sub-1B–3B agents in tight RAM. |
| **42** | Alquwayfili 2025 (Quantigence) | 4-bit MAS on commodity hardware—closest prior art to MAS under resource caps. |

## Quantization & agent failure

| # | Paper | One-line role |
| :---: | :--- | :--- |
| **22** | Lin et al. 2024 (AWQ) | Default PTQ for SAS-Quant monolith (GGUF/Q4 ecosystem). |
| **36** | Jang et al. 2026 | Quantization **amplifies tool/agent failures**—motivates grounding metrics. |
| **37** | Jamshidi et al. 2026 | Claim-level decay across agent cascades. |
| **38** | Singh & Pawar 2026 | Markov snowball; **verifier gates** reduce survival of hallucinations. |

## Finance application & evaluation

| # | Paper | One-line role |
| :---: | :--- | :--- |
| **34** | Patil et al. 2024 (BFCL) | Standardize tool/API calls for extraction agents. |
| **44** | Architecture Matters More Than Scale 2026 | **SME local 8B** financial QA: architecture > raw scale; **missing MAS vs quant monolith**. |
| **45** | MortarBench 2026 | **Mortgage origination agent** benchmark—document reasoning under policy. |

---

## Gap statement (for Related Work)

1. **Tran (tokens)** and **Bench360 (local quant monolith)** never intersect on **finance workflows + RAM parity + MAS-FP16**.  
2. **Paper 44** studies retrieval/memory on one 8B model—not multi-agent vs quantized scale-up.  
3. **MortarBench** evaluates agents but not **iso-RAM MAS-FP16 vs SAS-Quant**.  
4. Industry practice (on-prem KYC agents, TCAML-style human gates) assumes local LLMs without **systematic architecture comparison**.
