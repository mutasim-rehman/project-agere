# 35. MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark

> **Authors:** Yubo Wang et al.  
> **Affiliation & Venue:** NeurIPS 2024 (Datasets Track)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`35_Wang_2024_MMLU_Pro_Robust_Challenging_Benchmark.pdf`](../../sources/35_Wang_2024_MMLU_Pro_Robust_Challenging_Benchmark.pdf)  
> **Role in Our Study:** **Parametric World Knowledge Benchmark**

---

## 1. Executive Summary & Core Premise
Published at NeurIPS 2024, MMLU-Pro redesigns MMLU by expanding to 10 choices, integrating harder multi-step reasoning, and filtering out lucky guesses to accurately measure true parametric world knowledge.

---

## 2. Research Motivation & Problem Formulation
Standard MMLU had become saturated due to prompt sensitivity and 4-choice random guessing.

---

## 3. Technical Architecture & Methodology
- 12,000+ complex questions across 14 academic domains.
- 10 answer choices per question.
- Emphasizes multi-step reasoning over simple trivia recall.

---

## 4. Experimental Framework & Setup
- Evaluated across all leading frontier and open-source models.

---

## 5. Key Quantitative Findings & Breakthroughs
- Lowers scores across all models by 15–30%, restoring clear separation between model capability tiers.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Multiple-choice format; does not assess interactive agent workflows.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Our **parametric world knowledge benchmark**, testing whether a single large model (even at 4-bit) retains superior world knowledge over small models.

---

## 8. Citation Utility & Key Takeaways
Mandatory benchmark citation in Section 3 and Section 4.
