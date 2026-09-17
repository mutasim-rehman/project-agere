# Literature Review — Project Agere (Finance / Local RAM)

**Title alignment:** *Spend It Together or Spend It Big?* — multi-agent full-precision teams vs. quantized monoliths on **analyst RAM**, applied to **regulated finance document workflows**.

**Application:** [`../APPLICATION.md`](../APPLICATION.md)  
**Active sources (16 PDFs):** [`../sources/INDEX.md`](../sources/INDEX.md)  
**Excluded corpus (27 papers):** [`../sources/EXCLUDED_PAPERS.md`](../sources/EXCLUDED_PAPERS.md)

---

## Overarching research question

> Can a **multi-agent system of smaller, full-precision LLMs** outperform a **single larger, quantized LLM** when both use the **same peak resident system RAM** and the **same thinking-token budget**, on **KYC/credit/mortgage document tasks** where cloud APIs are prohibited?

---

## What changed (Sept 2026 pivot)

| Before | After |
| :--- | :--- |
| GPU VRAM, 15 tiers, 2×2 factorial headline | **System RAM**, 3 tiers (8/16/32 GB), **C vs B** headline |
| GAIA, SWE-bench, MMLU-Pro | **MortarBench**, synthetic KYC packs, grounding metrics |
| 43 papers | **16 active** + regulatory refs |
| “Interaction term” as main story | Optional 2×2; **practitioner install decision** as main story |

Legacy per-paper summaries (`summaries/*.md`) describe the **old** VRAM factorial mapping—they remain for reference but **override with** [`06_regulated_finance_local_llm.md`](./06_regulated_finance_local_llm.md) and [`../sources/PAPERS_DICTIONARY.md`](../sources/PAPERS_DICTIONARY.md).

---

## Reading order

1. **[`06_regulated_finance_local_llm.md`](./06_regulated_finance_local_llm.md)** — application, gaps, hypotheses *(start here)*  
2. **[`01_mas_vs_sas_collaboration.md`](./01_mas_vs_sas_collaboration.md)** — papers 01, 02, 03, 07 (token parity, tools, failures)  
3. **[`03_budget_and_memory_inference.md`](./03_budget_and_memory_inference.md)** — papers 15, 16 (budget + local quant monolith)  
4. **[`04_quantization_and_ondevice.md`](./04_quantization_and_ondevice.md)** — papers 22, 27, 36–38 (quantize + agent failure)  
5. **[`05_benchmarks_and_evaluation.md`](./05_benchmarks_and_evaluation.md)** — papers 34, 44, 45 (tools + finance eval)  

**Deprioritized (archival only):** `02_mas_topologies_and_frameworks.md` (MetaGPT content duplicated in paper 11).

---

## Core bibliography (16)

| # | Paper | Finance / RAM role |
| :---: | :--- | :--- |
| 01 | Tran & Kiela 2026 | Token budget parity |
| 02 | Żywot et al. 2026 | Tool-equalized MAS |
| 03 | Kim et al. 2025 | Agent scaling laws |
| 07 | Cemri MAST 2025 | Failure taxonomy |
| 11 | MetaGPT 2024 | Role orchestration |
| 15 | Wang EMNLP 2024 | Budget-aware eval |
| 16 | Bench360 2025 | Local SAS-Quant baseline |
| 22 | AWQ 2024 | Quantization |
| 27 | MobileLLM 2024 | Small agents |
| 34 | BFCL 2024 | Tool calling |
| 36–38 | Jang, Jamshidi, Singh 2026 | Quant + cascade + verifier theory |
| 42 | Quantigence 2025 | Commodity MAS |
| 44 | Financial QA SME 2026 | Local finance architecture gap |
| 45 | MortarBench 2026 | Mortgage agent benchmark |

---

## Abstract draft (≤250 words, finance framing)

Financial institutions increasingly deploy large language models **on analyst workstations** because customer and borrower data cannot be sent to public cloud APIs under privacy, MNPI, and supervisory expectations. The prevailing local pattern is to **quantize the largest single model** that fits in available RAM. An alternative is to **partition RAM across a team of smaller, full-precision models** with specialised roles (extract, retrieve, draft, verify) under human approval—yet no study has compared these options under **matched peak memory and matched thinking-token budgets** on regulated document workflows.

We evaluate **MAS-FP16** against **SAS-Quant** on mortgage origination agent tasks (MortarBench) and synthetic KYC/credit case-file generation, using CPU-first inference (llama.cpp/Ollama) at 8, 16, and 32 GB RAM tiers. Tools, prompts, and per-case token caps are identical across arms. Beyond task accuracy, we report **grounding-specific metrics**: invented amounts, uncited claims, and missed field mismatches—failure modes compliance reviewers care about.

We situate results against local single-model quantization benchmarks (Bench360), token-parity agent studies (Tran & Kiela), and recent work on quantised agent failure amplification and multi-agent error cascades. Our goal is a **deployment rule** for compliance IT: when to spend RAM on one quantized generalist versus a full-precision specialist team for on-prem KYC and credit documentation.
