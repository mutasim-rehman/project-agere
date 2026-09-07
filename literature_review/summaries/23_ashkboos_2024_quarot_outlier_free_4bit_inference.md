# 23. QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs

> **Authors:** Saleh Ashkboos et al.  
> **Affiliation & Venue:** NeurIPS 2024  
> **Publication Year:** 2024  
> **Local PDF Source:** [`23_Ashkboos_2024_QuaRot_Outlier_Free_4Bit_Inference.pdf`](../../sources/23_Ashkboos_2024_QuaRot_Outlier_Free_4Bit_Inference.pdf)  
> **Role in Our Study:** **End-to-End 4-Bit Weights + Activations + KV-Cache Compression**

---

## 1. Executive Summary & Core Premise
Published at NeurIPS 2024, QuaRot introduces randomized Hadamard rotations to eliminate activation outliers, enabling end-to-end 4-bit inference across weights, activations, and KV-cache simultaneously with 99% accuracy retention.

---

## 2. Research Motivation & Problem Formulation
Weight-only quantization leaves the KV-cache and activations in 16-bit, which causes severe memory bottlenecks at long sequence lengths. Quantizing activations failed previously due to extreme outlier values. QuaRot eliminates outliers mathematically.

---

## 3. Technical Architecture & Methodology
- Applies orthogonal randomized Hadamard matrices $H$ to weights and activations exploiting computational invariance: $(XH)(H^T W) = XW$.
- Rotations spread outlier energy uniformly across all channels, eliminating extreme spikes.
- Enables 4-bit integer GEMM matrix multiplication without dequantization.

---

## 4. Experimental Framework & Setup
- Models: LLaMA-2 (7B, 13B, 70B), LLaMA-3.
- Full W4A4KV4 evaluation across perplexity and zero-shot reasoning.

---

## 5. Key Quantitative Findings & Breakthroughs
- LLaMA-2-70B retains 99% of original zero-shot accuracy under full 4-bit inference.
- Slashes total runtime memory footprint (including KV cache) by nearly 4×.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Online rotation operations add slight arithmetic latency.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Allows our single-agent arm to compress both weights and KV cache to 4-bit, testing whether end-to-end compression maximizes single-agent dominance.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 and Section 3 as the leading NeurIPS 2024 baseline for end-to-end 4-bit inference.
