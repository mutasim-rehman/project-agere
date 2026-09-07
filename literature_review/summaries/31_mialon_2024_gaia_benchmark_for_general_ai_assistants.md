# 31. GAIA: A Benchmark for General AI Assistants

> **Authors:** Gregoire Mialon et al. (Meta AI, Hugging Face, AutoGPT)  
> **Affiliation & Venue:** ICLR 2024  
> **Publication Year:** 2024  
> **Local PDF Source:** [`31_Mialon_2024_GAIA_Benchmark_for_General_AI_Assistants.pdf`](../../sources/31_Mialon_2024_GAIA_Benchmark_for_General_AI_Assistants.pdf)  
> **Role in Our Study:** **Primary Tool-Use & Multi-Step Agent Benchmark**

---

## 1. Executive Summary & Core Premise
Introduced at ICLR 2024, GAIA is the gold-standard benchmark for general AI assistants, comprising 466 real-world questions requiring multimodal handling, multi-step planning, web navigation, and tool execution—tasks simple for humans (92%) but difficult for AI (15%).

---

## 2. Research Motivation & Problem Formulation
Existing benchmarks saturated on esoteric trivia and standardized tests while failing to measure real-world operational assistant capabilities.

---

## 3. Technical Architecture & Methodology
- 466 questions across Levels 1, 2, and 3 based on step complexity.
- Objective string/numeric ground truth verification.
- Requires multimodal parsing, web search, and Python code execution.

---

## 4. Experimental Framework & Setup
- Evaluated across GPT-4 with plugins, AutoGPT, and open-source models.

---

## 5. Key Quantitative Findings & Breakthroughs
- Revealed massive gap between human baseline (92%) and GPT-4 with plugins (15%).
- Resistant to statistical guessing and dataset memorization.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Small test set (466 items); relies on external web environment stability.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Our **primary tool-use benchmark** to test whether multi-agent tool specialization outperforms a single large quantized model.

---

## 8. Citation Utility & Key Takeaways
Mandatory benchmark citation in Section 3 and Section 4.
