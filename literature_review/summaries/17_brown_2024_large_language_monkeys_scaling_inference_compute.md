# 17. Large Language Monkeys: Scaling Inference Compute with Repeated Sampling

> **Authors:** Bradley Brown, Jordan Juravsky, Anthony Ryan, et al.  
> **Affiliation & Venue:** arXiv:2407.21787 (July 2024)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`17_Brown_2024_Large_Language_Monkeys_Scaling_Inference_Compute.pdf`](../../sources/17_Brown_2024_Large_Language_Monkeys_Scaling_Inference_Compute.pdf)  
> **Role in Our Study:** **Inference-Time Compute Scaling Baseline**

---

## 1. Executive Summary & Core Premise
Demonstrates that scaling coverage via repeated independent sampling ($k = 1$ to $10,000$) on small-to-medium models enables them to match or surpass models 10× to 100× larger on complex coding and reasoning benchmarks.

---

## 2. Research Motivation & Problem Formulation
Investigates whether test-time inference compute can substitute for parameter scale: can a smaller model with extensive sampling outperform a monolithic frontier model?

---

## 3. Technical Architecture & Methodology
- Generates thousands of samples per query using varying temperatures.
- Evaluates Pass@$k$ coverage and majority voting.
- Analyzes compute-scaling curves across Llama-3-8B and Llama-3-70B.

---

## 4. Experimental Framework & Setup
- Benchmarks: SWE-bench Lite, HumanEval, GSM8K, MATH.
- Compares Pass@$k$ scaling against pre-training compute scaling.

---

## 5. Key Quantitative Findings & Breakthroughs
- Repeated sampling exhibits consistent power-law scaling on tasks with verifiable test cases.
- An 8B model with sufficient sampling coverage solves problems that standard 70B models fail on.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Requires automated verifiers or unit tests to select correct solutions at high $k$.
- Extremely high cumulative token cost.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Serves as a strong compute-matched baseline for our Single-Agent arm, testing whether repeated sampling on a quantized model beats multi-agent coordination.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 and Section 3 when defending our single-agent test-time compute baselines.
