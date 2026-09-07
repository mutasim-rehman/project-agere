# 19. The qs Inequality: Quantifying the Double Penalty of Mixture-of-Experts at Inference

> **Authors:** Chen et al.  
> **Affiliation & Venue:** arXiv:2603.08960 (March 2026)  
> **Publication Year:** 2026  
> **Local PDF Source:** [`19_Chen_2026_The_qs_Inequality_MoE_Inference_Penalty.pdf`](../../sources/19_Chen_2026_The_qs_Inequality_MoE_Inference_Penalty.pdf)  
> **Role in Our Study:** **Mathematical Theory: Capacity vs. Memory Parity Penalty**

---

## 1. Executive Summary & Core Premise
A formal theoretical paper deriving the $q_s$ inequality, proving mathematically that sparse Mixture-of-Experts (MoE) architectures incur a double penalty at inference: when total resident memory is held equal, dense monolithic networks decisively outperform sparse networks.

---

## 2. Research Motivation & Problem Formulation
While MoEs achieve superior performance when matching *active* parameters (compute FLOPs), practitioners noticed that dense models win when matching *total stored parameters* (VRAM). The authors set out to prove this mathematical quality-equivalence boundary.

---

## 3. Technical Architecture & Methodology
- Derives the quality-equivalence multiplier $q_s$ bounding parameter efficiency.
- Compares MoE vs. Dense under matched FLOPs vs. matched resident memory.
- Validates theoretical bounds empirically across open transformer checkpoints.

---

## 4. Experimental Framework & Setup
- Comprehensive scaling experiments holding total parameter memory constant.

---

## 5. Key Quantitative Findings & Breakthroughs
- Proves that distributing parameters across routed sub-networks incurs an inherent representation penalty under total memory parity.
- The total parameter parity inversion: dense models consistently surpass MoEs when resident hardware memory is the binding constraint.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Evaluates internal layer routing inside single models rather than multi-agent macro-orchestration.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Provides our **core theoretical analogy**: just as the $q_s$ inequality proved that distributing capacity into sub-networks loses under total memory parity, we test whether distributing capacity into whole orchestrated agents loses to a monolithic model under equal VRAM.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 1 (Introduction) and Section 2 (Theory) as the formal mathematical foundation for our hypothesis.
