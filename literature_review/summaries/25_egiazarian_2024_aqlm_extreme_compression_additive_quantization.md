# 25. AQLM: Extreme Compression of Large Language Models via Additive Quantization

> **Authors:** Vage Egiazarian et al.  
> **Affiliation & Venue:** ICML 2024  
> **Publication Year:** 2024  
> **Local PDF Source:** [`25_Egiazarian_2024_AQLM_Extreme_Compression_Additive_Quantization.pdf`](../../sources/25_Egiazarian_2024_AQLM_Extreme_Compression_Additive_Quantization.pdf)  
> **Role in Our Study:** **Extreme 2-Bit / 3-Bit Quantization Baseline**

---

## 1. Executive Summary & Core Premise
Published at ICML 2024, AQLM is the first Pareto-optimal quantization scheme for extreme compression regimes below 3 bits per parameter, generalizing Additive Quantization to LLMs via joint codebook optimization across transformer blocks.

---

## 2. Research Motivation & Problem Formulation
Standard quantization schemes collapse into incoherent gibberish below 3 bits. AQLM breaks this barrier to fit massive models into consumer GPUs.

---

## 3. Technical Architecture & Methodology
- Multi-codebook vector quantization representing weight vectors as the sum of learned codewords ($W \approx \sum C_m[i_m]$).
- Block-wise joint fine-tuning via beam search codebook assignment.
- Targets 2-bit, 2.5-bit, and 3-bit regimes.

---

## 4. Experimental Framework & Setup
- Models: LLaMA-2 (7B to 70B), Mistral-7B.
- Perplexity and zero-shot accuracy evaluation.

---

## 5. Key Quantitative Findings & Breakthroughs
- First scheme where 2-bit and 3-bit models retain non-trivial reasoning capability.
- Compresses 70B models into under 16 GB of memory with viable perplexity.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Slower decoding latency due to vector codebook lookups.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Enables our **Extreme Scale experiment**: testing whether a massive 70B model compressed to 2-bit/3-bit beats an MAS of small models in a 16 GB budget.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 and Section 4 when exploring extreme parameter scaling boundaries.
