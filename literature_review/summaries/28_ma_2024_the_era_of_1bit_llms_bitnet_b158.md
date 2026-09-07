# 28. The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits (BitNet b1.58)

> **Authors:** Shuming Ma et al. (Microsoft Research)  
> **Affiliation & Venue:** arXiv:2402.17764 (February 2024)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`28_Ma_2024_The_Era_of_1Bit_LLMs_BitNet_b158.pdf`](../../sources/28_Ma_2024_The_Era_of_1Bit_LLMs_BitNet_b158.pdf)  
> **Role in Our Study:** **Theoretical Boundary: Extreme 1.58-Bit Ternary Quantization**

---

## 1. Executive Summary & Core Premise
Introduces BitNet b1.58, where every transformer weight is constrained to ternary values {-1, 0, 1}, matching full-precision 16-bit LLM performance while eliminating matrix multiplication in favor of integer addition.

---

## 2. Research Motivation & Problem Formulation
Floating-point matrix multiplication is the dominant bottleneck in LLM memory and energy consumption. BitNet b1.58 redefines neural computing with ternary weights.

---

## 3. Technical Architecture & Methodology
- Absmean quantization scaling weights to {-1, 0, 1} and activations to 8-bit integers.
- Replaces FP16 matrix multiplications with pure integer addition kernels.

---

## 4. Experimental Framework & Setup
- Evaluated from 700M to 3B parameters across perplexity and commonsense QA.

---

## 5. Key Quantitative Findings & Breakthroughs
- Matches FP16 performance starting at 3B parameters while saving up to 3.55× memory and 71× matrix multiplication energy.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Requires full pre-training from scratch; cannot be applied as PTQ.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Establishes the theoretical lower bound of single-model parameter storage cost.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 1 and Section 2 as the ultimate horizon of single-model compression.
