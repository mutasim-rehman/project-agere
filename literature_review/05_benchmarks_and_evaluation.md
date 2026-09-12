# Literature Review: Pillar 4 — Benchmarks & Empirical Evaluation Infrastructure (Papers 31–35)

This document provides a comprehensive, rigorous literature review of Papers 31 through 35, covering the official **benchmark datasets, evaluation protocols, and leaderboards** used to measure reasoning depth, tool usage, and parametric knowledge.

---

## 31. GAIA: A Benchmark for General AI Assistants

* **File:** [`../sources/31_Mialon_2024_GAIA_Benchmark_for_General_AI_Assistants.pdf`](../sources/31_Mialon_2024_GAIA_Benchmark_for_General_AI_Assistants.pdf)
* **Authors:** Grégoire Mialon, Clémentine Fourrier, Craig Swift, Thomas Wolf, Yann LeCun, et al.
* **Affiliation & Venue:** Meta AI, Hugging Face, AutoGPT — **ICLR 2024**

### 1. What It Is
The gold-standard evaluation benchmark for general AI assistants, comprising 466 meticulously curated, real-world questions designed to test multimodal handling, complex multi-step reasoning, web navigation, and tool execution—tasks that are conceptually trivial for humans but notoriously challenging for LLMs.

### 2. How It Relates to Our Research
Serves as our **primary benchmark for testing whether tool-augmented environments buffer against quantization noise in multi-agent systems ($\Delta_{\text{interaction}} > 0$)**. While sequential multi-hop reasoning (FRAMES) is hypothesized to cause error cascade compounding ($\Delta_{\text{interaction}} < 0$), parallel tool-augmented tasks on GAIA allow specialized sub-agents (Planner, Searcher, Coder) to isolate quantization perturbations, testing whether orchestration acts as a protective noise buffer under equal resident VRAM.

### 3. Detailed Methodology
* **Task Structure:** 466 questions categorized into 3 difficulty levels:
  - *Level 1:* 1–3 steps, no tools or single simple tool.
  - *Level 2:* 4–8 steps, multi-modal files, search, and calculation.
  - *Level 3:* Complex multi-modal, multi-step research requiring robust error recovery.
* **Ground Truth Verification:** Unambiguous, short string or numeric answers ensuring 100% objective programmatic evaluation.
* **Baselines:** Human baseline (92%) vs. GPT-4 + plugins baseline (~15%).

### 4. Key Novelty & Theoretical Contributions
* **Conceptually Simple, Computationally Hard:** Reverses the traditional benchmark paradigm (which tested esoteric trivia or advanced mathematics) to focus on everyday operational competence and tool proficiency.
* **Immunity to Memorization:** Questions require interacting with arbitrary dynamic attachments (spreadsheets, audio files, web pages), making pure parametric memorization useless.

### 5. Critical Limitations & Caveats
* Small test set size (466 questions), meaning variance across small sample subsets can be noisy.
* Heavy reliance on external tools (web browsing APIs, Python sandboxes) introduces environmental latency.

### 6. Why We SHOULD Include It as a Source
* **ICLR 2024 paper.** It is the universally recognized gold standard for agentic evaluation. Citing and using GAIA is essential for demonstrating that our agent evaluations meet top-tier community standards.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Cannot be excluded if our paper evaluates tool-use agents.

---

## 32. SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

* **File:** [`../sources/32_Jimenez_2024_SWE_bench_Real_World_GitHub_Issues.pdf`](../sources/32_Jimenez_2024_SWE_bench_Real_World_GitHub_Issues.pdf)
* **Authors:** Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik R. Narasimhan
* **Affiliation & Venue:** Princeton University — **ICLR 2024 (Oral Presentation)**

### 1. What It Is
The definitive software engineering agent benchmark, testing LLMs on resolving 2,294 real-world GitHub issues collected from 12 popular Python repositories, requiring models to ingest full codebases, localize bugs across multiple files, write patches, and pass existing unit test suites.

### 2. How It Relates to Our Research
Serves as our **complex multi-step code execution benchmark**. It allows us to test whether a multi-agent software development pipeline (e.g., File Locator + Bug Reproducer + Patch Generator) built with smaller models can outperform a single large quantized model struggling to maintain context across huge codebases.

### 3. Detailed Methodology
* **Dataset:** 2,294 issue-pull request pairs from active Python repositories (e.g., django, sympy, scikit-learn, matplotlib).
* **Evaluation Harness:** Dockerized unit test execution. A patch is considered correct *if and only if* it passes both the pre-existing unit tests and the newly introduced test cases for the bug.
* **Metrics:** Pass@1 resolution rate, Patch syntax validity, Localization accuracy.

### 4. Key Novelty & Theoretical Contributions
* **True Real-World Scale:** Replaces synthetic coding puzzles (HumanEval) with actual open-source software engineering problems spanning hundreds of thousands of lines of context.
* **ICLR 2024 Oral:** Catalyzed the entire sub-field of software engineering agents (SWE-agent, Devin, etc.).

### 5. Critical Limitations & Caveats
* Extremely compute-heavy to evaluate: running the full 2,294 task instances requires thousands of Docker container executions, making SWE-bench Lite (300 instances) the standard alternative.

### 6. Why We SHOULD Include It as a Source
* **ICLR 2024 Oral.** High academic prestige. Citing SWE-bench Lite demonstrates that our evaluation suite tests real-world multi-step execution rather than toy synthetic benchmarks.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If our hardware environment lacks the compute to run Dockerized software execution sandboxes, SWE-bench can be replaced with lighter benchmarks like GAIA and FRAMES.

---

## 33. FRAMES: Factuality, Retrieval, And Multi-hop Evaluation with Structured Knowledge

* **File:** [`../sources/33_Krishna_2024_FRAMES_Factuality_Retrieval_Multihop.pdf`](../sources/33_Krishna_2024_FRAMES_Factuality_Retrieval_Multihop.pdf)
* **Authors:** Satyapriya Krishna et al.
* **Affiliation & Venue:** Google — *arXiv:2409.05591 / EMNLP 2024*

### 1. What It Is
A dedicated multi-hop evaluation benchmark designed to rigorously assess LLM factual accuracy and multi-hop reasoning by requiring models to retrieve, cross-reference, and synthesize information across 2 to 15 distinct sources and structured knowledge representations.

### 2. How It Relates to Our Research
Serves as our **primary multi-hop reasoning benchmark for testing the Compounding Noise / Double Penalty Hypothesis ($\Delta_{\text{interaction}} < 0$)**. It is the exact dataset used by Tran & Kiela (2026). In our 2×2 Factorial Design, FRAMES provides the acid test for whether quantization noise compounds multiplicatively across sequential inter-agent reasoning handoffs in Cell D compared to Cells C, B, and A under strict resident memory parity.

### 3. Detailed Methodology
* **Dataset Characteristics:** Questions requiring up to 15 reasoning hops across multiple articles and structured tables.
* **Evaluation Protocol:** Strict exact match and factual constraint checking to eliminate ambiguous answers.
* **Metrics:** Multi-hop Accuracy, Retrieval Precision, Context Hallucination Rate.

### 4. Key Novelty & Theoretical Contributions
* **High-Hop Complexity:** Dramatically increases hop complexity beyond older benchmarks (e.g., HotpotQA, which rarely requires $>2$ hops), exposing severe context degradation in multi-agent dialogue handoffs.

### 5. Critical Limitations & Caveats
* Primarily retrieval- and reasoning-focused; does not assess interactive environment actions or executable code tools.

### 6. Why We SHOULD Include It as a Source
* **Essential for baseline continuity.** Because Tran & Kiela anchored their study on FRAMES, using FRAMES allows us to directly test our hypothesis against their findings with zero benchmark divergence.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Cannot be excluded if Tran & Kiela is our primary base paper.

---

## 34. The Berkeley Function-Calling Leaderboard (BFCL)

* **File:** [`../sources/34_Patil_2024_Berkeley_Function_Calling_Leaderboard_Gorilla.pdf`](../sources/34_Patil_2024_Berkeley_Function_Calling_Leaderboard_Gorilla.pdf)
* **Authors:** Shishir G. Patil, Tianjun Zhang, Xin Wang, Joseph E. Gonzalez
* **Affiliation & Venue:** UC Berkeley Gorilla Team — *arXiv:2403.01374 / ICML 2024*

### 1. What It Is
A comprehensive, live-evaluated benchmarking platform designed to measure the function-calling (tool-invocation) accuracy of LLMs across simple, multiple, parallel, and parallel-multiple function calls in diverse programming languages and schema types.

### 2. How It Relates to Our Research
Provides the **micro-level validation for our tool-using sub-agents**. Before small sub-agents can succeed in an MAS on GAIA, they must be able to generate syntactically valid JSON tool calls. BFCL allows us to measure whether small models (e.g., 1B–3B) experience a collapse in function-calling precision compared to a large quantized 14B/32B model.

### 3. Detailed Methodology
* **Test Categories:** Simple function calling, Multiple function calls, Parallel calls, and Multi-turn stateful function calling.
* **Execution Validation:** Compares generated function call ASTs (Abstract Syntax Trees) directly against reference schemas and live API execution environments.
* **Metrics:** AST match accuracy, Parameter value accuracy, Syntax error rate.

### 4. Key Novelty & Theoretical Contributions
* **Fine-Grained Tool Calling Taxonomy:** Separates function selection (which tool to call) from parameter generation (what arguments to pass), identifying that small models often select the correct tool but hallucinate nested parameter types.

### 5. Critical Limitations & Caveats
* Evaluates individual tool-call turns rather than long-horizon, autonomous multi-turn agent planning.

### 6. Why We SHOULD Include It as a Source
* Standard reference in modern tool-use literature; explains the mechanistic limits of small agents when delegating subtasks to external tools.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If GAIA already tests end-to-end tool execution, BFCL can be cited in passing as a diagnostic baseline rather than evaluated as a primary benchmark.

---

## 35. MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark

* **File:** [`../sources/35_Wang_2024_MMLU_Pro_Robust_Challenging_Benchmark.pdf`](../sources/35_Wang_2024_MMLU_Pro_Robust_Challenging_Benchmark.pdf)
* **Authors:** Yubo Wang et al.
* **Affiliation & Venue:** Tsinghua University, University of Waterloo — **NeurIPS 2024 (Datasets Track)**

### 1. What It Is
A rigorous redesign of the ubiquitous MMLU benchmark, expanding options from 4 choices to 10 choices, integrating more advanced multi-step reasoning problems across 14 academic domains, and eliminating noisy questions to separate true parametric world knowledge from statistical guessing.

### 2. How It Relates to Our Research
Serves as our **parametric world knowledge benchmark**. It directly tests our counter-hypothesis: that a single large model (even when quantized to 4-bit) retains a significantly richer parametric knowledge base that smaller models in a multi-agent system cannot recover, regardless of collaborative prompting.

### 3. Detailed Methodology
* **Dataset:** 12,000+ complex questions spanning STEM, humanities, medicine, law, and business.
* **Option Expansion:** 10 answer options per question (reducing random guess probability from 25% down to 10%).
* **Reasoning Requirement:** Emphasizes multi-step derivation rather than simple factual lookup.
* **Metrics:** Accuracy (5-shot CoT), Cross-domain knowledge degradation.

### 4. Key Novelty & Theoretical Contributions
* **Restoring Benchmark Discriminative Power:** Demonstrates that standard MMLU had become saturated due to prompt sensitivity and 4-choice guessing; MMLU-Pro lowers scores across all frontier models by 15–30%, providing a much clearer signal of true model intelligence.

### 5. Critical Limitations & Caveats
* Multiple-choice format; does not assess interactive dialogue, tool usage, or long-horizon agent execution.

### 6. Why We SHOULD Include It as a Source
* **NeurIPS 2024 Datasets Track.** Unimpeachable academic pedigree. Essential for proving that on knowledge-dense domains, model parameter scale (even when quantized) is fundamentally superior to small-model collaboration.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* None. It is the gold-standard benchmark for parametric knowledge depth.
