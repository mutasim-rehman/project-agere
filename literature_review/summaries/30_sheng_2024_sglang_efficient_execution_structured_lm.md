# 30. SGLang: Efficient Execution of Structured Language Model Programs

> **Authors:** Lianmin Sheng, Cody Hao Yu, Lianmin Zheng, et al.  
> **Affiliation & Venue:** NeurIPS 2024  
> **Publication Year:** 2024  
> **Local PDF Source:** [`30_Sheng_2024_SGLang_Efficient_Execution_Structured_LM.pdf`](../../sources/30_Sheng_2024_SGLang_Efficient_Execution_Structured_LM.pdf)  
> **Role in Our Study:** **Multi-Agent KV-Cache Sharing & High-Throughput Runtime**

---

## 1. Executive Summary & Core Premise
Accepted at NeurIPS 2024, SGLang introduces RadixAttention, which manages KV-caches as reusable radix trees, enabling automatic prefix caching and KV-cache sharing across multi-turn agent interactions and multi-agent workflows.

---

## 2. Research Motivation & Problem Formulation
Multi-agent workflows pass identical prompt prefixes, system instructions, and history across multiple calls, causing massive redundant KV-cache memory consumption and recomputation.

---

## 3. Technical Architecture & Methodology
- RadixAttention: treats KV-cache as dynamic search tree, matching and reusing cached prefix blocks automatically.
- Structured decoding compiler optimizing branching agent execution.

---

## 4. Experimental Framework & Setup
- Evaluated across multi-turn chat, agent tool execution, and Tree-of-Thoughts reasoning.

---

## 5. Key Quantitative Findings & Breakthroughs
- Delivers up to 5× throughput improvement over standard runtimes by eliminating redundant KV recomputations.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Focused on runtime systems execution rather than reasoning algorithms.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Directly reduces the memory footprint of our multi-agent system by sharing prompt KV-cache across cooperating sub-agents.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 3 (Systems Implementation) to validate how multi-agent KV memory was managed.
