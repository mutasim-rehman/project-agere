# 33. FRAMES: Factuality, Retrieval, And Multi-hop Evaluation with Structured Knowledge

> **Authors:** Satyapriya Krishna et al. (Google)  
> **Affiliation & Venue:** arXiv:2409.05591 / EMNLP 2024  
> **Publication Year:** 2024  
> **Local PDF Source:** [`33_Krishna_2024_FRAMES_Factuality_Retrieval_Multihop.pdf`](../../sources/33_Krishna_2024_FRAMES_Factuality_Retrieval_Multihop.pdf)  
> **Role in Our Study:** **Primary Multi-Hop Reasoning Benchmark**

---

## 1. Executive Summary & Core Premise
Introduces FRAMES, a benchmark designed to evaluate multi-hop retrieval and reasoning requiring models to synthesize information across 2 to 15 distinct sources and structured knowledge representations.

---

## 2. Research Motivation & Problem Formulation
Prior multi-hop benchmarks rarely required more than 2 hops, allowing single models to succeed via statistical shortcuts. FRAMES tests high-hop reasoning.

---

## 3. Technical Architecture & Methodology
- Questions requiring up to 15 reasoning hops across multiple articles.
- Exact match and factual constraint verification.

---

## 4. Experimental Framework & Setup
- Evaluated across state-of-the-art models and retrieval-augmented systems.

---

## 5. Key Quantitative Findings & Breakthroughs
- Exposes severe context degradation in multi-agent dialogue handoffs as hop count increases.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Focused on retrieval and reasoning; does not evaluate tool execution.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Our **primary multi-hop benchmark**, directly replicating and extending the evaluation suite used in Tran & Kiela (2026).

---

## 8. Citation Utility & Key Takeaways
Mandatory benchmark citation in Section 3 and Section 4.
