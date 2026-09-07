# 24. SpinQuant: LLM Quantization with Learned Rotations

> **Authors:** Zechun Liu et al.  
> **Affiliation & Venue:** ICLR 2025  
> **Publication Year:** 2025  
> **Local PDF Source:** [`24_Liu_2025_SpinQuant_LLM_Quantization_Learned_Rotations.pdf`](../../sources/24_Liu_2025_SpinQuant_LLM_Quantization_Learned_Rotations.pdf)  
> **Role in Our Study:** **State-of-the-Art Learned Rotation Quantization Baseline**

---

## 1. Executive Summary & Core Premise
Accepted at ICLR 2025, SpinQuant optimizes rotation matrices via Cayley optimization on the Stiefel manifold to suppress outliers, outperforming QuaRot and narrowing the accuracy gap between 4-bit quantized models and full-precision FP16 baselines.

---

## 2. Research Motivation & Problem Formulation
Random Hadamard rotations (QuaRot) reduce outliers but do not exploit the specific weight geometry of a given model checkpoint. SpinQuant learns the optimal rotation angles directly.

---

## 3. Technical Architecture & Methodology
- Optimizes rotation matrices constrained to the orthogonal group $O(n)$ using Cayley transforms.
- End-to-end W4A4KV4 coverage.
- Outperforms SmoothQuant and QuaRot on challenging reasoning tasks.

---

## 4. Experimental Framework & Setup
- Benchmarks: MMLU, GSM8K, HumanEval, WikiText perplexity.

---

## 5. Key Quantitative Findings & Breakthroughs
- Recovers 1.5–3.0% higher accuracy than QuaRot on complex reasoning.
- Closes over 95% of the perplexity gap with full-precision FP16.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Requires an offline optimization phase (several GPU hours) before deployment.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Provides an uncompromised, cutting-edge quantized single-agent baseline to guarantee that our SAS model is not handicapped by quantization artifacts.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 3 to establish that our study uses latest ICLR 2025 quantization standards.
