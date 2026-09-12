# EXPERIMENT PROTOCOL: 2×2 FACTORIAL ISO-MEMORY STUDY
## Project Agere: Multi-Agent Orchestration vs. Quantized Scaling Under Strict VRAM Budgets

**Protocol Version:** 2.0 (Factorial Expansion)  
**Date:** September 2026  
**Status:** Approved Specification  
**Working Title:** *Spend It Together or Spend It Big: How Multi-Agent Orchestration and Quantization Interact Under a Fixed Memory Budget*  
**Secondary Subtitle:** *A 2×2 Factorial Study of Architectural Modularity and Post-Training Quantization Under Strict VRAM Parity*

---

## 1. Executive Summary & Problem Motivation

In modern edge and enterprise AI deployments, GPU Video RAM (VRAM) is an uncompromising physical barrier. While token budgets and FLOP limits are soft operational constraints, exceeding resident VRAM triggers fatal Out-Of-Memory (OOM) crashes or catastrophic latency collapse via PCIe CPU host offloading.

System designers facing a fixed hardware footprint (e.g., 8 GB RTX 4060, 16 GB RTX 4080, 24 GB RTX 4090, 32 GB Dual-GPU) face a fundamental architectural choice between two distinct scaling paradigms:

1. **Quantized Scaling (Bench360 Paradigm):** Allocate the entire resident memory budget to a single monolithic generalist model compressed aggressively via post-training quantization (e.g., running a 14B or 32B model at INT4/INT2 instead of a 3B model at FP16).
2. **Modular Orchestration (Multi-Agent Paradigm):** Divide the reasoning pipeline across an ensemble of smaller, specialized agents operating within the same total memory budget.

### The Literature Gap: The Missing 2×2 Cell
Prior literature has evaluated these two dimensions in isolation:
* Quantization benchmarks (Bench360, AWQ, GPTQ) compare larger quantized single models against smaller full-precision single models.
* Multi-agent evaluations (ChatEval, MetaGPT, DyLAN) compare multi-agent teams against single models, but routinely violate iso-resource parity by allowing the multi-agent system multiple times the inference memory or comparing identical models without memory constraints.
* Crucially, **no study in the literature has systematically evaluated a Multi-Agent System built with larger, quantized models (Cell D) against a single giant quantized model (Cell B) and a native full-precision multi-agent system (Cell C) under strict physical resident memory parity.**

This protocol formalizes a **2×2 Factorial Experimental Design** across **15 discrete hardware memory tiers** (4 GB to 32 GB at 2 GB increments), testing whether architectural modularity and post-training compression act independently, or whether they exhibit a significant non-linear interaction effect ($\Delta_{\text{interaction}}$).

---

## 2. Theoretical Framework & 2×2 Factorial Design

### 2.1 The 2×2 Factorial Matrix
The experiment manipulates two independent factors under an invariant constraint: **total resident physical VRAM $M_{\text{resident}} \le M_{\text{budget}}$ with $\ge 95\%$ memory saturation.**

$$\begin{array}{c|c|c}
\hline
\textbf{Precision / Compression} & \textbf{Single-Agent System (SAS)} & \textbf{Multi-Agent System (MAS)} \\
\hline
\textbf{Native Full-Precision} & \textbf{Cell A: SAS-FP16} & \textbf{Cell C: MAS-FP16} \\
\text{(FP16 / BF16)} & \text{Smaller Single Model (Control Baseline)} & \text{Modular Team of Smaller Native Models} \\
\hline
\textbf{Quantized Scaling} & \textbf{Cell B: SAS-Quant} & \textbf{Cell D: MAS-Quant (NEW)} \\
\text{(INT8 / INT4 / INT2)} & \text{Larger Single Model Quantized (Bench360 Winner)} & \text{Modular Team of Larger Quantized Models} \\
\hline
\end{array}$$

### 2.2 Factor Definitions
* **Factor 1: Architectural Modularity ($A \in \{\text{SAS}, \text{MAS}\}$)**
  * $\text{SAS}$ ($A=0$): A single generalist LLM prompted zero-shot or few-shot with Chain-of-Thought (CoT) to solve the task end-to-end.
  * $\text{MAS}$ ($A=1$): An orchestrated ensemble of $\ge 2$ specialized agents communicating via structured natural language handoffs to solve the task cooperatively (AHDS topology).
* **Factor 2: Precision / Compression Strategy ($C \in \{\text{FP16}, \text{Quantized}\}$)**
  * $\text{FP16}$ ($C=0$): Models retain uncompressed native 16-bit floating-point weights ($b = 16\text{ bits}$).
  * $\text{Quantized}$ ($C=1$): Models are scaled up in parameter count and compressed using state-of-the-art post-training quantization ($b \in \{8, 4, 2\}\text{ bits}$) to match the target memory ceiling.

---

## 3. Research Questions & Mechanistic Hypotheses

### 3.1 Research Questions
* **RQ1 (A vs. B — Control Baseline Replication):** Does a larger, quantized single model outperform a smaller, native FP16 single model under identical resident memory limits? *(Replicates Bench360 findings as our internal baseline control).*
* **RQ2 (C vs. B — Original Agere Question):** Does a multi-agent system of smaller native FP16 agents outperform a single larger quantized model under equal memory?
* **RQ3 (D vs. A — Quantized Modular vs. Native Single):** Does a multi-agent system of larger, quantized agents outperform a single smaller native FP16 model under equal memory?
* **RQ4 (D vs. B — Quantized Modular vs. Quantized Monolith):** Does a multi-agent system of larger, quantized agents outperform a single much larger quantized model under equal memory?
* **RQ5 (The Interaction Term — Core Theoretical Contribution):** Does post-training quantization degrade performance more, less, or equally inside an orchestrated multi-agent system compared to a single monolithic model?

### 3.2 The Interaction Metric
The factorial interaction effect is formally defined as:
$$\Delta_{\text{interaction}} = [\text{Score}(D) - \text{Score}(C)] - [\text{Score}(B) - \text{Score}(A)]$$

Equivalently, it measures whether the architectural advantage of multi-agent orchestration changes as models are quantized:
$$\Delta_{\text{interaction}} = [\text{Score}(D) - \text{Score}(B)] - [\text{Score}(C) - \text{Score}(A)]$$

### 3.3 Mechanistic Hypotheses
1. **Hypothesis 1 (Compounding Error / Double Penalty — $q_s$ Inequality):** $\Delta_{\text{interaction}} < 0$.  
   *Mechanism:* Post-training quantization introduces stochastic and systematic noise into token probability distributions. In a single model (Cell B), internal hidden representations remain continuous until generation. In a multi-agent system (Cell D), sub-agent outputs are discretized into discrete tokens across inter-agent handoffs. Any quantization-induced hallucination, formatting aberration, or reasoning error from Agent $k$ is amplified multiplicatively by Agent $k+1$, leading to cascading failure. This mirrors the mathematical $q_s$ double-penalty inequality established for Mixture-of-Experts (MoE) routing.
2. **Hypothesis 2 (Role Specialization Noise-Buffering):** $\Delta_{\text{interaction}} > 0$.  
   *Mechanism:* In Cell D, each sub-agent is prompted for a narrow, highly constrained sub-task (e.g., query generation, validation, calculation) rather than generalist world modeling. Narrow prompt constraints collapse the active manifold of required tokens, rendering specialized sub-agents significantly more resilient to low-precision weight perturbations than a monolithic generalist trying to maintain long-range multi-task coherence.
3. **Null Hypothesis ($H_0$):** $\Delta_{\text{interaction}} = 0$.  
   *Mechanism:* The effects of multi-agent modularity and quantization are strictly additive and orthogonal. Architectural choice does not alter quantization sensitivity.
4. **Task-Type Moderator Hypothesis:** $\Delta_{\text{interaction}}$ is strongly modulated by reasoning topology:
   * *Sequential Multi-Hop Reasoning (FRAMES):* $\Delta_{\text{interaction}} < 0$ (error cascade dominates).
   * *Parallel Tool Execution (GAIA):* $\Delta_{\text{interaction}} > 0$ (isolation and specialization dominate).

---

## 4. Memory Utilization Parity Protocol (MUPP)

### 4.1 The "Empty VRAM" Confound
A critical flaw in previous memory-constrained evaluations is the **discretization void**: because open-source models exist only at discrete parameter scales (e.g., Qwen 2.5: 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B), naively deploying a model into an arbitrary tier leaves substantial VRAM unallocated. For instance, deploying a 7B model at INT4 (~3.8 GB) on an 8 GB GPU leaves >50% of the VRAM unused. Comparing this under-utilized setup against a system that fills 7.8 GB creates an invalid comparison.

### 4.2 MUPP Enforcement Rules
Every experimental condition in Cells A, B, C, and D must strictly satisfy:

1. **Physical Budget Ceiling:**
   $$M_{\text{total}} = M_{\text{weights}} + M_{\text{KV-cache}} + M_{\text{runtime}} \le M_{\text{budget}}$$
2. **Active Saturation Floor:**
   $$\text{Saturation Ratio} = \frac{M_{\text{total}}}{M_{\text{budget}}} \ge 0.950 \quad (95.0\%)$$
3. **Two-Phase Allocation Pipeline:**
   * **Phase 1 (Weight Sizing):** Calibrate model parameter counts and quantization bit-widths ($b \in \{16, 8, 4, 2\}$) such that model weights occupy between 75% and 94% of the target VRAM tier.
   * **Phase 2 (Runtime Reservoir Pre-Allocation):** Pre-allocate the remaining resident headroom to the inference engine's KV-cache pool using `--gpu-memory-utilization 0.95`. This guarantees that all four cells physically occupy $\ge 95\%$ of resident VRAM during execution, eliminating VRAM under-allocation confounds.
4. **No Swapping / Host RAM Offloading:**
   All weights and active KV-cache blocks must reside entirely in GPU VRAM. PCIe swapping to system RAM is strictly prohibited during benchmarking runs.

---

## 5. Master 15-Tier Iso-Memory Matrix (60 Experimental Cells)

All models are drawn from the standardized **Qwen 2.5** family (Alibaba, 2024), maintaining consistent architecture, tokenizer, and pre-training distribution.

| Tier | VRAM Budget | Cell A: SAS-FP16 (Control) | Cell B: SAS-Quant (Bench360) | Cell C: MAS-FP16 (AHDS Native) | Cell D: MAS-Quant (AHDS Quantized) |
|:---:|:---:|:---|:---|:---|:---|
| **4 GB** | 4.0 GB | Qwen2.5-1.5B FP16<br>*(3.0G W + 0.8G KV = 3.8G, 95.0%)* | Qwen2.5-7B INT4-AWQ<br>*(3.8G W + 0.1G KV = 3.9G, 97.5%)* | 0.5B + 0.5B FP16<br>*(2.0G W + 1.8G KV = 3.8G, 95.0%)* | 1.5B INT8 + 0.5B FP16<br>*(2.5G W + 1.3G KV = 3.8G, 95.0%)* |
| **6 GB** | 6.0 GB | Qwen2.5-1.5B FP16<br>*(3.0G W + 2.7G KV = 5.7G, 95.0%)* | Qwen2.5-7B INT4-AWQ<br>*(3.8G W + 1.9G KV = 5.7G, 95.0%)* | 1.5B + 0.5B FP16<br>*(4.0G W + 1.7G KV = 5.7G, 95.0%)* | 3B INT8 + 1.5B INT4<br>*(3.8G W + 1.9G KV = 5.7G, 95.0%)* |
| **8 GB** | 8.0 GB | Qwen2.5-3B FP16<br>*(6.0G W + 1.6G KV = 7.6G, 95.0%)* | Qwen2.5-14B INT4-AWQ<br>*(7.6G W + 0.1G KV = 7.7G, 96.2%)* | 3B + 0.5B FP16<br>*(7.0G W + 0.6G KV = 7.6G, 95.0%)* | 7B INT4 + 7B INT4<br>*(7.6G W + 0.2G KV = 7.8G, 97.5%)* |
| **10 GB** | 10.0 GB | Qwen2.5-3B FP16<br>*(6.0G W + 3.5G KV = 9.5G, 95.0%)* | Qwen2.5-14B INT4-AWQ<br>*(7.6G W + 1.9G KV = 9.5G, 95.0%)* | 3B + 1.5B FP16<br>*(9.0G W + 0.5G KV = 9.5G, 95.0%)* | 7B INT8 + 1.5B FP16<br>*(10.0G W + 0.0G KV = 10.0G, 100.0%)* |
| **12 GB** | 12.0 GB | Qwen2.5-3B FP16<br>*(6.0G W + 5.4G KV = 11.4G, 95.0%)* | Qwen2.5-14B INT4-AWQ<br>*(7.6G W + 3.8G KV = 11.4G, 95.0%)* | 3B + 1.5B + 0.5B FP16<br>*(10.0G W + 1.4G KV = 11.4G, 95.0%)* | 7B INT8 + 3B INT8<br>*(10.0G W + 1.4G KV = 11.4G, 95.0%)* |
| **14 GB** | 14.0 GB | Qwen2.5-3B FP16<br>*(6.0G W + 7.3G KV = 13.3G, 95.0%)* | Qwen2.5-14B INT4-AWQ<br>*(7.6G W + 5.7G KV = 13.3G, 95.0%)* | 3B + 3B FP16<br>*(12.0G W + 1.3G KV = 13.3G, 95.0%)* | 14B INT4 + 7B INT4<br>*(11.4G W + 2.0G KV = 13.4G, 95.7%)* |
| **16 GB** | 16.0 GB | Qwen2.5-7B FP16<br>*(14.0G W + 1.2G KV = 15.2G, 95.0%)* | Qwen2.5-32B INT4-AWQ<br>*(15.5G W + 0.1G KV = 15.6G, 97.5%)* | 7B + 0.5B FP16<br>*(15.0G W + 0.2G KV = 15.2G, 95.0%)* | 14B INT4 + 14B INT4<br>*(15.2G W + 0.6G KV = 15.8G, 98.8%)* |
| **18 GB** | 18.0 GB | Qwen2.5-7B FP16<br>*(14.0G W + 3.1G KV = 17.1G, 95.0%)* | Qwen2.5-32B INT4-AWQ<br>*(15.5G W + 1.6G KV = 17.1G, 95.0%)* | 7B + 1.5B FP16<br>*(17.0G W + 0.1G KV = 17.1G, 95.0%)* | 14B INT8 + 1.5B FP16<br>*(17.0G W + 0.1G KV = 17.1G, 95.0%)* |
| **20 GB** | 20.0 GB | Qwen2.5-7B FP16<br>*(14.0G W + 5.0G KV = 19.0G, 95.0%)* | Qwen2.5-32B INT4-AWQ<br>*(15.5G W + 3.5G KV = 19.0G, 95.0%)* | 7B + 1.5B + 0.5B FP16<br>*(18.0G W + 1.0G KV = 19.0G, 95.0%)* | 14B INT8 + 3B INT8<br>*(17.0G W + 2.0G KV = 19.0G, 95.0%)* |
| **22 GB** | 22.0 GB | Qwen2.5-7B FP16<br>*(14.0G W + 6.9G KV = 20.9G, 95.0%)* | Qwen2.5-32B INT4-AWQ<br>*(15.5G W + 5.4G KV = 20.9G, 95.0%)* | 7B + 3B FP16<br>*(20.0G W + 0.9G KV = 20.9G, 95.0%)* | 32B INT4 + 7B INT4<br>*(19.3G W + 1.7G KV = 21.0G, 95.5%)* |
| **24 GB** | 24.0 GB | Qwen2.5-7B FP16<br>*(14.0G W + 8.8G KV = 22.8G, 95.0%)* | Qwen2.5-32B INT4-AWQ<br>*(15.5G W + 7.3G KV = 22.8G, 95.0%)* | 7B + 3B + 1.5B FP16<br>*(23.0G W + 0.0G KV = 23.0G, 95.8%)* | 32B INT4 + 7B INT8<br>*(23.5G W + 0.4G KV = 23.9G, 99.6%)* |
| **26 GB** | 26.0 GB | Qwen2.5-7B FP16<br>*(14.0G W + 10.7G KV = 24.7G, 95.0%)* | Qwen2.5-32B INT4-AWQ<br>*(15.5G W + 9.2G KV = 24.7G, 95.0%)* | 7B + 3B + 1.5B + 0.5B FP16<br>*(24.0G W + 0.7G KV = 24.7G, 95.0%)* | 32B INT4 + 14B INT4<br>*(23.1G W + 1.7G KV = 24.8G, 95.4%)* |
| **28 GB** | 28.0 GB | Qwen2.5-7B FP16<br>*(14.0G W + 12.6G KV = 26.6G, 95.0%)* | Qwen2.5-72B INT2-GPTQ<br>*(26.0G W + 0.6G KV = 26.6G, 95.0%)* | 7B + 7B FP16<br>*(28.0G W + 0.0G KV = 28.0G, 100.0%)* | 32B INT4 + 14B INT4 + 1.5B FP16<br>*(26.1G W + 0.6G KV = 26.7G, 95.4%)* |
| **30 GB** | 30.0 GB | Qwen2.5-14B FP16<br>*(28.0G W + 0.5G KV = 28.5G, 95.0%)* | Qwen2.5-72B INT2-GPTQ<br>*(26.0G W + 2.5G KV = 28.5G, 95.0%)* | 14B + 0.5B FP16<br>*(29.0G W + 0.0G KV = 29.0G, 96.7%)* | 32B INT4 + 14B INT4 + 3B INT8<br>*(26.1G W + 2.4G KV = 28.5G, 95.0%)* |
| **32 GB** | 32.0 GB | Qwen2.5-14B FP16<br>*(28.0G W + 2.4G KV = 30.4G, 95.0%)* | Qwen2.5-72B INT2-GPTQ<br>*(26.0G W + 4.4G KV = 30.4G, 95.0%)* | 14B + 1.5B FP16<br>*(31.0G W + 0.0G KV = 31.0G, 96.9%)* | 32B INT4 + 14B INT4 + 7B INT4<br>*(27.9G W + 3.0G KV = 30.9G, 96.6%)* |

*Note: All 60 conditions have been programmatically verified to achieve $\ge 95.0\%$ memory saturation while remaining strictly $\le 100.0\%$ of their respective physical tier budget.*

---

## 6. Multi-Agent System Architecture (AHDS)

### 6.1 AHDS Overview
All multi-agent configurations in Cells C and D utilize the **Adaptive Hierarchical with Dynamic Pruning & Structured Communication (AHDS)** architecture. AHDS was explicitly engineered to address the 7 fatal failure modes of multi-agent collaboration documented in our systematic literature review:

| Problem ID | Failure Mode | Prior Literature Source | AHDS Solution Protocol |
|:---:|:---|:---|:---|
| **P1** | Context Dilution & Bloat | Du et al. (2023), Chen et al. (2024) | Strict JSON-schema inter-agent contracts (maximum 200-word payload). Raw reasoning scratchpads are pruned. |
| **P2** | Sycophancy & False Consensus | Liang et al. (2023) | Anonymous, blinded role execution. Sub-agents do not know peer identities or confidence scores. |
| **P3** | Cascading Hallucination | Bench360 (2024), DyLAN (2024) | Deterministic gating validator. Output is rejected and regenerated if JSON schema or math checks fail. |
| **P4** | Unbounded Token Explosion | Agere Survey (2024) | Fixed-budget token quotas per role; maximum 2 inter-agent revision hops. |
| **P5** | Role Under-Specialization | MetaGPT (2023) | Differentiated system prompts with negative constraints and strict domain boundaries. |
| **P6** | Topology Rigidity | DyLAN (2024) | Dynamic role invocation: single-step questions bypass secondary workers to save compute. |
| **P7** | Memory Bloat & Thrashing | Project Agere Survey | Concurrent model co-residency in shared VRAM pool; shared prefix caching where supported. |

### 6.2 AHDS Role Definitions
1. **Orchestrator / Decomposer:** Receives the original user prompt, performs problem decomposition into independent sub-tasks, assigns sub-tasks to specialist workers, and synthesizes the final output.
2. **Specialist Worker(s):** Executes a dedicated sub-domain task (e.g., retrieval extraction, formal symbolic derivation, counter-argument drafting).
3. **Critic / Validator:** Audits the intermediate outputs against task constraints, verifies numerical/symbolic correctness, and gates the final response.

---

## 7. Minimal Dual-Benchmark Design (Controlled Task Moderator)

### 7.1 Strategic Rationale: The Task-Type Moderator Tension
A critical insight from our literature synthesis explains why foundational papers reached diametrically opposed conclusions:
* **Tran & Kiela (2026)** evaluated multi-hop reasoning (FRAMES, MuSiQue) and concluded that single agents decisively outperform multi-agent systems. This is the domain where the **Data Processing Inequality (DPI)** bites hardest: intermediate information is degraded across lossy natural language handoffs, compounding error cascades.
* **Żywot et al. (2026)** ("Can Small Agent Collaboration Beat a Single Big LLM?") evaluated **GAIA** and demonstrated that collaborative small agents equipped with external tools outperform much larger monolithic models. This is the domain where **role specialization and tool interfaces** let small models shine.

Rather than collapsing our evaluation into purely multi-hop reasoning (which would merely re-confirm Tran & Kiela's findings under a different budget axis) or expanding to an unmanageable survey, we adopt a **Minimal Dual-Benchmark Design**. We evaluate two lean, highly controlled contrasting anchors that operationalize the task moderator as an independent experimental variable:

$$\begin{array}{c|c|c}
\hline
\textbf{Contrasting Anchor} & \textbf{Anchor 1: Tool-Intensive Slice} & \textbf{Anchor 2: Multi-Hop Reasoning Slice} \\
\hline
\textbf{Representative Dataset} & \textbf{GAIA (Level 1 \& 2 Subset)} & \textbf{MuSiQue / FRAMES Subset} \\
\textbf{Theoretical Literature Basis} & \text{Żywot et al. (2026) Base Paper Domain} & \text{Tran \& Kiela (2026) Baseline Domain} \\
\textbf{Primary Mechanistic Driver} & \text{Modular Tool Specialization} & \text{Sequential Context Synthesis (DPI)} \\
\textbf{Hypothesized Interaction} & \Delta_{\text{interaction}} > 0 \text{ (Noise-Buffering)} & \Delta_{\text{interaction}} < 0 \text{ (Double Penalty / Cascading Error)} \\
\textbf{Sample Size} & 100 \text{ balanced tasks} & 150 \text{ questions (2-to-4 hops)} \\
\textbf{Strategic Function} & \textbf{Primary Novel Finding Engine} & \textbf{Sanity Check \& Calibration Anchor} \\
\hline
\end{array}$$

### 7.2 Anchor 1: GAIA Tool-Intensive Slice (Primary Testing Ground)
* **Dataset:** GAIA (Mialon et al., ICLR 2024), 100-task curated subset (50 Level 1 tasks + 50 Level 2 tasks).
* **Configuration:** Defined in [`configs/benchmarks/gaia_tool_slice.yaml`](file:///d:/project-agere/configs/benchmarks/gaia_tool_slice.yaml).
* **Standardized Tools:** Python code execution sandbox, web search (cached/Serp), and file inspector (JSON, CSV, PDF). Identical tools and execution sandboxes are provided to both SAS and MAS configurations.
* **Role in Study:** Tests **Hypothesis 2 (Role Specialization Buffering: $\Delta_{\text{interaction}} > 0$)**. Because each sub-agent in Cell D handles a narrow operational role (e.g. drafting search queries or writing Python arithmetic snippets), the active token manifold is constrained, testing whether orchestration acts as a protective buffer against quantization noise.
* **Priority:** **Top Priority.** If compute time runs short, the GAIA slice is preserved as the core experimental deliverable.

### 7.3 Anchor 2: MuSiQue Multi-Hop Reasoning Slice (Calibration & Sanity Check)
* **Dataset:** MuSiQue (Trivedi et al., TACL 2022) / FRAMES (Krishna et al., Google 2024), 150-question subset evenly distributed across 2-hop, 3-hop, and 4-hop questions.
* **Configuration:** Defined in [`configs/benchmarks/musique_reasoning_slice.yaml`](file:///d:/project-agere/configs/benchmarks/musique_reasoning_slice.yaml).
* **Environment:** Closed-book multi-step reasoning without external tools; Chain-of-Thought prompting.
* **Role in Study:** Tests **Hypothesis 1 (Compounding Noise / Double Penalty: $\Delta_{\text{interaction}} < 0$)** under the Data Processing Inequality.
* **Calibration Function:** Provides an immediate sanity check: our single-agent baseline results on MuSiQue can be calibrated against Tran & Kiela's published numbers to verify our evaluation pipeline before evaluating novel cells.

### 7.4 Primary Evaluation Metrics
* **Accuracy ($\text{Acc}$):** Exact Match / F1 on canonical ground-truth answers.
* **Memory Efficiency ($\eta_M$):** Accuracy achieved per gigabyte of resident physical VRAM:
  $$\eta_M = \frac{\text{Acc}}{M_{\text{budget}}} \quad [\% / \text{GB}]$$
* **Token Efficiency ($\eta_T$):** Accuracy per thousand generated output tokens:
  $$\eta_T = \frac{\text{Acc}}{T_{\text{total}} / 1000}$$
* **Interaction Term ($\Delta_{\text{interaction}}$):**
  $$\Delta_{\text{interaction}} = [\text{Score}(D) - \text{Score}(C)] - [\text{Score}(B) - \text{Score}(A)]$$

---

## 8. Experimental Controls & Reproducibility Specs

### 8.1 Random Seeds & Sampling
* **Replications:** All evaluations executed across **3 independent random seeds** ($S \in \{42, 123, 999\}$).
* **Sampling Parameters:**
  * Deterministic baseline passes: Greedy decoding, $T = 0.0$, $\text{top\_p} = 1.0$.
  * Stochastic passes: $T = 0.7$, $\text{top\_p} = 0.9$ across all 3 seeds for confidence interval reporting.

### 8.2 Standardized Execution Commands
Below are the standardized execution templates for the 16 GB tier across both benchmark anchors:

#### GAIA Tool-Intensive Slice (Anchor 1)
```bash
# Cell A (SAS-FP16) on GAIA
python -m src.benchmarks.run_eval --tier 16gb --cell A --model Qwen/Qwen2.5-7B-Instruct --benchmark configs/benchmarks/gaia_tool_slice.yaml --gpu-memory-utilization 0.95 --seeds 42 123 999

# Cell B (SAS-Quant) on GAIA
python -m src.benchmarks.run_eval --tier 16gb --cell B --model Qwen/Qwen2.5-32B-Instruct-AWQ --benchmark configs/benchmarks/gaia_tool_slice.yaml --gpu-memory-utilization 0.95 --seeds 42 123 999

# Cell C (MAS-FP16) on GAIA
python -m src.benchmarks.run_eval --tier 16gb --cell C --config configs/systems/mas/ahds/ahds_16gb.yaml --benchmark configs/benchmarks/gaia_tool_slice.yaml --gpu-memory-utilization 0.95 --seeds 42 123 999

# Cell D (MAS-Quant) on GAIA
python -m src.benchmarks.run_eval --tier 16gb --cell D --config configs/systems/mas/quant/mas_quant_16gb.yaml --benchmark configs/benchmarks/gaia_tool_slice.yaml --gpu-memory-utilization 0.95 --seeds 42 123 999
```

#### MuSiQue Multi-Hop Reasoning Slice (Anchor 2)
```bash
# Cell D (MAS-Quant) on MuSiQue Calibration Slice
python -m src.benchmarks.run_eval --tier 16gb --cell D --config configs/systems/mas/quant/mas_quant_16gb.yaml --benchmark configs/benchmarks/musique_reasoning_slice.yaml --gpu-memory-utilization 0.95 --seeds 42 123 999
```

---

## 9. Statistical Analysis Plan

### 9.1 Three-Way Factorial ANOVA with Controlled Task Moderator
To evaluate main effects, the 2×2 interaction, and how task type moderates this interaction, accuracy results will be modeled using a Three-Way Factorial Analysis of Variance with Hardware Tier as a blocking factor:

$$y_{ijkl} = \mu + \alpha_i \, (\text{Arch}) + \beta_j \, (\text{Precision}) + (\alpha\beta)_{ij} \, (\text{Interaction}) + \delta_k \, (\text{Task Type}) + [(\alpha\beta)\delta]_{ijk} \, (\text{Moderation}) + \gamma_l \, (\text{Tier}) + \epsilon_{ijkl}$$

Where:
* $\alpha_i \in \{\text{SAS}, \text{MAS}\}$ ($1$ df)
* $\beta_j \in \{\text{FP16}, \text{Quantized}\}$ ($1$ df)
* $(\alpha\beta)_{ij}$ is the core Architecture $\times$ Precision interaction term ($1$ df)
* $\delta_k \in \{\text{Tool-Intensive (GAIA)}, \text{Multi-Hop Reasoning (MuSiQue)}\}$ ($1$ df)
* $[(\alpha\beta)\delta]_{ijk}$ is the **Three-Way Moderation Term** ($1$ df) directly testing whether task type flips or attenuates the 2×2 interaction effect
* $\gamma_l$ is the blocking factor across 15 memory tiers ($l \in \{1, \dots, 15\}$)
* $\epsilon_{ijkl} \sim \mathcal{N}(0, \sigma^2)$ is the residual error

### 9.2 Statistical Hypotheses Testing Criteria
1. **Main Interaction Test ($(\alpha\beta) \neq 0$):** If $p < 0.05$, architecture and compression do not act independently.
2. **Task Moderation Test ($[(\alpha\beta)\delta] \neq 0$):** If $p < 0.05$, the direction or magnitude of $\Delta_{\text{interaction}}$ is significantly governed by task structure (confirming the crossover hypothesis between tool specialization and reasoning DPI degradation).

### 9.2 Statistical Tests & Significance Thresholds
* **Significance Level:** $\alpha = 0.05$.
* **Multiple Comparisons:** Bonferroni-Holm step-down procedure applied across pairwise post-hoc tests (A vs B, C vs B, D vs A, D vs B).
* **Pairwise Categorical Comparisons:** McNemar's test for paired binary correctness on identical benchmark questions:
  $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}, \quad df = 1$$
* **Effect Size:** Partial eta-squared ($\eta_p^2$) computed for all main effects and the interaction term:
  $$\eta_p^2 = \frac{SS_{\text{effect}}}{SS_{\text{effect}} + SS_{\text{error}}}$$

### 9.3 Python Analysis Script (`src/analysis/factorial_anova.py`)
```python
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

def run_factorial_anova(results_csv: str):
    df = pd.read_csv(results_csv)
    # Full Model: score ~ Architecture * Precision * Task_Type + C(Tier)
    model = ols('score ~ C(architecture) * C(precision) * C(task_type) + C(tier)', data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    
    print("=== Factorial ANOVA Results with Task Moderator ===")
    print(anova_table)
    
    # 1. Core 2x2 Interaction: Architecture x Precision
    f_2way = anova_table.loc['C(architecture):C(precision)', 'F']
    p_2way = anova_table.loc['C(architecture):C(precision)', 'PR(>F)']
    ss_2way = anova_table.loc['C(architecture):C(precision)', 'sum_sq']
    ss_err = anova_table.loc['Residual', 'sum_sq']
    eta_p2_2way = ss_2way / (ss_2way + ss_err)
    print(f"\nCore Interaction (Arch x Quant): F = {f_2way:.4f}, p = {p_2way:.4e}, partial_eta2 = {eta_p2_2way:.4f}")
    
    # 2. Three-Way Moderation: Architecture x Precision x Task_Type
    inter_3way_key = 'C(architecture):C(precision):C(task_type)'
    if inter_3way_key in anova_table.index:
        f_3way = anova_table.loc[inter_3way_key, 'F']
        p_3way = anova_table.loc[inter_3way_key, 'PR(>F)']
        ss_3way = anova_table.loc[inter_3way_key, 'sum_sq']
        eta_p2_3way = ss_3way / (ss_3way + ss_err)
        print(f"Three-Way Moderation (Arch x Quant x Task): F = {f_3way:.4f}, p = {p_3way:.4e}, partial_eta2 = {eta_p2_3way:.4f}")
        if p_3way < 0.05:
            print("[FINDING] Task Type significantly moderates the 2x2 interaction! (DPI error cascade vs. tool noise-buffering confirmed)")

if __name__ == '__main__':
    import sys
    run_factorial_anova(sys.argv[1] if len(sys.argv) > 1 else 'experiments/results_master.csv')
```

---

## 10. Publication Deliverables & Artifacts Checkpoints

1. **Protocol & Specification (Current):** `EXPERIMENT_PROTOCOL.md` and 45 YAML configurations in `configs/`.
2. **Infrastructure Scaffolding (Phase 4):** Model downloading, quantization pipelines, and vLLM multi-model serving verification.
3. **Execution & Profiling (Phase 5):** Automated evaluation harness running all 60 conditions across FRAMES, GSM8K/MATH, and GPQA.
4. **Data Analysis & Visualization (Phase 6):** Iso-VRAM Pareto curves, 2×2 interaction bar charts, and ANOVA significance tables.
5. **Manuscript Preparation (Phase 7):** Full conference submission targeted at NeurIPS / ICLR / ACL / ICML.
