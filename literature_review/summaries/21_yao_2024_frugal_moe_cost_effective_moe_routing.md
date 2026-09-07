# 21. Frugal-MoE: Cost-Effective Mixture of Experts via Activation-Guided Routing

> **Authors:** Yao et al.  
> **Affiliation & Venue:** ACL 2024 (Findings)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`21_Yao_2024_Frugal_MoE_Cost_Effective_MoE_Routing.pdf`](../../sources/21_Yao_2024_Frugal_MoE_Cost_Effective_MoE_Routing.pdf)  
> **Role in Our Study:** **Adaptive Subnetwork Activation Baseline**

---

## 1. Executive Summary & Core Premise
Frugal-MoE introduces activation-guided dynamic routing to selectively skip expert loading and activation for simpler tokens, reducing runtime memory bandwidth and compute demands during inference.

---

## 2. Research Motivation & Problem Formulation
Uniform expert activation wastes significant memory bandwidth on simple, predictable tokens.

---

## 3. Technical Architecture & Methodology
- Predicts token difficulty and routes easy tokens to a minimal expert subset.
- Dynamic capacity budgeting preserving accuracy on complex tokens.

---

## 4. Experimental Framework & Setup
- Benchmarks: MMLU, GSM8K, CommonsenseQA.

---

## 5. Key Quantitative Findings & Breakthroughs
- Preserves 98%+ of accuracy while slashing inference compute by up to 40%.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Restricted to MoE architectures; does not apply directly to dense multi-agent teams.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Serves as an adaptive memory-saving contrast point against static multi-agent allocation.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 when discussing dynamic capacity allocation.
