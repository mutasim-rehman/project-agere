# Paper 44 — Architecture Matters More Than Scale (Financial QA, SME Compute)

- **File:** [`../../sources/papers/44_Financial_QA_SME_Architecture_vs_Scale.pdf`](../../sources/papers/44_Financial_QA_SME_Architecture_vs_Scale.pdf)
- **arXiv:** 2604.17979 (2026)
- **Role:** Finance + **local 8B** constraint; retrieval/memory architecture vs. raw model scale

## Problem

SMEs cannot afford cloud GPU inference or large API spend. Which **LLM architectures** (RAG, memory, symbolic layers) work on a **single locally hosted ~8B** model for financial QA?

## Method

Compare reasoning architectures under explicit **SME compute envelope** (no datacenter GPUs).

## Key finding

**Architecture choices dominate** naive scale-ups within the envelope—directly motivates testing **MAS role decomposition** vs **one quantized larger model** at equal RAM (gap Agere fills).

## Limitation for Agere

Single-model study only; **no MAS-FP16 vs SAS-Quant** comparison.

## Cite in paper

Related Work (regulated finance), Gap paragraph, SME deployment motivation.
