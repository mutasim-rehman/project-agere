# 32. SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

> **Authors:** Carlos E. Jimenez, John Yang, Alexander Wettig, et al.  
> **Affiliation & Venue:** ICLR 2024 (Oral Presentation)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`32_Jimenez_2024_SWE_bench_Real_World_GitHub_Issues.pdf`](../../sources/32_Jimenez_2024_SWE_bench_Real_World_GitHub_Issues.pdf)  
> **Role in Our Study:** **Complex Multi-Step Real-World Engineering Benchmark**

---

## 1. Executive Summary & Core Premise
An ICLR 2024 Oral paper introducing SWE-bench, evaluating LLMs on resolving 2,294 real-world GitHub issues from 12 popular Python repositories requiring codebase navigation, bug localization, patch editing, and unit test execution.

---

## 2. Research Motivation & Problem Formulation
Synthetic coding benchmarks (HumanEval) failed to capture the complexity of real-world software engineering across large codebases.

---

## 3. Technical Architecture & Methodology
- Dockerized unit test evaluation harness.
- Patch considered valid if and only if it passes both existing regression tests and newly added bug test cases.

---

## 4. Experimental Framework & Setup
- Evaluated across proprietary and open-source models.

---

## 5. Key Quantitative Findings & Breakthroughs
- Initial models solved under 5% of real-world issues, establishing it as the definitive benchmark for agentic coding.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Compute-heavy to evaluate; requires Docker container execution.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Serves as our complex multi-step execution benchmark testing whether agent division of labor beats monolithic models on massive contexts.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 3 as the gold-standard benchmark for software engineering agents.
