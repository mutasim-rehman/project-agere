# 34. The Berkeley Function-Calling Leaderboard (BFCL)

> **Authors:** Shishir G. Patil, Tianjun Zhang, Xin Wang, Joseph E. Gonzalez  
> **Affiliation & Venue:** arXiv:2403.01374 / ICML 2024 (Gorilla Team)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`34_Patil_2024_Berkeley_Function_Calling_Leaderboard_Gorilla.pdf`](../../sources/34_Patil_2024_Berkeley_Function_Calling_Leaderboard_Gorilla.pdf)  
> **Role in Our Study:** **Standardized Tool/Function-Calling Evaluation**

---

## 1. Executive Summary & Core Premise
A comprehensive benchmarking platform from UC Berkeley measuring function-calling accuracy across simple, multiple, parallel, and multi-turn function calls in diverse programming languages.

---

## 2. Research Motivation & Problem Formulation
Evaluates whether models can accurately generate structured API calls with valid AST parameters.

---

## 3. Technical Architecture & Methodology
- AST parsing and live API execution verification.
- Separates function selection accuracy from argument generation accuracy.

---

## 4. Experimental Framework & Setup
- Evaluates models from 1B to 70B+ parameters.

---

## 5. Key Quantitative Findings & Breakthroughs
- Small models often select the correct function but struggle with nested JSON parameter syntax.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Evaluates single-turn function calling rather than long-horizon autonomous planning.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Validates the tool-calling precision of small sub-agents compared to large quantized models.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 3 to validate tool-calling metrics.
