# 20. Efficient Memory Management for Large Language Model Serving with PagedAttention (vLLM)

> **Authors:** Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, et al.  
> **Affiliation & Venue:** SOSP 2023 / MLSys  
> **Publication Year:** 2023  
> **Local PDF Source:** [`20_Kwon_2023_vLLM_PagedAttention_Memory_Management.pdf`](../../sources/20_Kwon_2023_vLLM_PagedAttention_Memory_Management.pdf)  
> **Role in Our Study:** **Serving Infrastructure & KV-Cache Management**

---

## 1. Executive Summary & Core Premise
The foundational systems paper that introduced PagedAttention and vLLM, eliminating KV-cache memory fragmentation and enabling near-zero memory waste during concurrent LLM inference through virtual memory paging.

---

## 2. Research Motivation & Problem Formulation
Existing LLM serving systems wasted 60–80% of GPU memory due to internal and external KV-cache fragmentation. In memory-constrained settings, this caused premature Out-Of-Memory (OOM) crashes long before physical VRAM was actually filled.

---

## 3. Technical Architecture & Methodology
- PagedAttention divides contiguous KV-caches into fixed-size physical memory blocks.
- Dynamic non-contiguous allocation similar to OS virtual memory paging.
- Supports copy-on-write page sharing for parallel sampling and beam search.

---

## 4. Experimental Framework & Setup
- Evaluates throughput and memory efficiency across diverse model scales and batch workloads.

---

## 5. Key Quantitative Findings & Breakthroughs
- Reduces KV-cache memory waste to under 4%.
- Increases serving throughput by 2× to 4× with zero accuracy degradation.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Pure systems paper; does not explore multi-agent prompting or agent reasoning algorithms.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

The **core serving engine** of our experimental pipeline, ensuring multi-agent models and single-agent models run with near-zero KV memory waste.

---

## 8. Citation Utility & Key Takeaways
Mandatory citation in Section 3 (Implementation Details) to validate our memory accounting.
