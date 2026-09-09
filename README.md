# Project Agere: Multi-Agent Systems vs. Quantized Single Agents Under Equal Memory Budgets

## Research Framing & Problem Formulation

Your research addresses a fundamental, unanswered dilemma in practical AI deployment:

### Core Research Question
> **Under a fixed, hard memory constraint (resident VRAM budget $M$), can a Multi-Agent System (MAS) composed of smaller, higher-precision language models outperform a Single-Agent System (SAS) utilizing a larger, aggressively quantized language model?**

---

## 1. Why This Problem is Methodologically Groundbreaking

Prior agentic scaling literature almost exclusively equalizes compute (FLOPs, thinking token budgets, or active parameter counts). However:

1. **Memory is a hard physical ceiling, not a soft operational cost:** In edge, local workstation, or single-GPU deployments (e.g., 8 GB, 16 GB, or 24 GB VRAM), exceeding VRAM results in Out-Of-Memory (OOM) fatal crashes or massive offloading latency penalties. You cannot simply "spend more tokens" if the model weights do not fit in hardware.
2. **The Tension Between Scale vs. Precision vs. Multi-Agent Synergy:**
   - **Large + Quantized (SAS):** Benefits from higher pre-trained world knowledge, deeper reasoning depth, and instruction-following scale, but suffers from quantization noise (e.g., 4-bit/3-bit degradation on sensitive attention heads and perplexity spikes).
   - **Smaller + Coordinated (MAS):** Preserves higher numeric precision (FP16/BF16 or INT8) and gains task decomposition, self-correction, role specialization, and verification—but individual sub-agents possess strictly bounded reasoning ceilings and smaller parametric knowledge stores.
3. **Task Type as the Critical Moderator:** The winner will not be universal:
   - **Tool & Step-Decomposition Heavy:** Smaller agents with division of labor (e.g., Planner + Searcher + Verifier) often beat a single monolithic model.
   - **Deep Interleaved Logic & Knowledge-Dense:** A single larger model (even at 4-bit) may preserve relational knowledge and long-range coherence that smaller models cannot recover regardless of prompting.

---

## 2. Research Gaps, Prior Work Limitations & What We Can Do

A systematic analysis of the 35 foundational papers across multi-agent systems, budget normalization, and quantization reveals **5 critical research gaps** and **1 major real-world application void**:

### Gap 1: The "Compute-Budget" vs. "Physical Memory" Disconnect
- **Prior Work:** Tran & Kiela (2026), Wang et al. (EMNLP 2024).  
  Equalized resources along the axis of "thinking tokens" or "inference FLOPs" to conclude that single agents consistently match or outperform multi-agent systems on reasoning.
- **The Blind Spot / Limitation:** Tokens and FLOPs are *soft operational costs* that can be relaxed by spending more budget or waiting longer. In contrast, physical hardware memory (resident GPU VRAM) is a *rigid, non-negotiable physical wall*. Exceeding VRAM triggers an immediate, fatal CUDA Out-of-Memory (OOM) crash or massive offloading latency penalties.
- **What We Do (Our Contribution):** We establish the first systematic evaluation that equalizes **physical resident hardware VRAM ($M$)**. We investigate whether the single-agent advantage holds when the freed memory is used to deploy a larger, post-training quantized model (e.g., 32B @ 4-bit) against an intact multi-agent team (e.g., 2× 7B @ INT8 or 1× 7B + 2× 3B @ FP16).

### Gap 2: The Cross-Silo Disconnect Between Quantization and Agent Collaboration
- **Prior Work:**
  - *Quantization Literature (AWQ, QuaRot, SpinQuant, Bench360):* Compresses monolithic models in isolation to minimize perplexity loss, never testing whether that memory would be better allocated to an orchestrated team of smaller models.
  - *Agent Literature (Mixture-of-Agents, AgentVerse, MetaGPT, ChatDev):* Explores multi-agent synergy under the assumption of unconstrained cloud API memory, never profiling concurrent resident GPU footprints.
- **The Blind Spot / Limitation:** Neither literature speaks to the other. Quantization researchers ignore collaborative agent specialization; agent researchers ignore model quantization and hardware memory limits.
- **What We Do (Our Contribution):** We directly bridge these two literatures, pitting post-training quantized large models (SAS) against high-precision multi-agent teams (MAS) at identical VRAM residency tiers (8 GB, 16 GB, 24 GB).

### Gap 3: Confounded Baselines in Small-Agent Tool Research
- **Prior Work:** Żywot, Chen, & de Rijke (2026).  
  Claimed that small collaborative agents (4B) beat a large monolithic model (32B) on the GAIA benchmark.
- **The Blind Spot / Limitation:** The comparison was confounded by tool access. Small agents were equipped with external tools (Python interpreters, web search, calculators) while the large model was evaluated without tools or without equalized memory.
- **What We Do (Our Contribution):** We conduct the first unconfounded test by giving **both** the single agent and the multi-agent system identical toolkits, prompting formats (ReAct/CoT), and runtime environments under an identical resident memory envelope.

### Gap 4: The Micro-to-Macro "Capacity Penalty" Analogy
- **Prior Work:** Chen et al. (2026, the $q_s$ inequality), Cemri et al. (2025, MAST).  
  At the micro-architectural layer inside a single model, Chen et al. proved mathematically that sparse Mixture-of-Experts (MoEs) lose to dense monolithic models when total stored resident parameters are held equal.
- **The Blind Spot / Limitation:** Nobody has evaluated whether this law also governs the macro-orchestration level. An MAS is conceptually an external, coarsely-routed MoE. Does partitioning a 16 GB memory budget across multiple small agents incur an identical (or worse) capacity penalty due to inter-agent communication overhead and context collapse?
- **What We Do (Our Contribution):** We empirically test the "Macro-Capacity Hypothesis" at the agent coordination layer, determining whether multi-agent systems suffer an irreversible capacity fragmentation penalty under total memory parity.

### Gap 5: The Task-Type Moderator Spectrum
- **Prior Work:** Flat, contradictory claims in prior literature: Tran & Kiela claimed "SAS universally wins," while MoA and Żywot et al. claimed "MAS universally wins."
- **The Blind Spot / Limitation:** Neither claim holds universally. The winner is governed by the underlying task dependency structure (Kim et al., 2025):
  - *Knowledge-Dense & Deep Logical Reasoning (MMLU-Pro, MuSiQue, FRAMES):* Small models lack the parametric depth to derive answers, and inter-agent communication is lossy (Data Processing Inequality).
  - *Tool-Intensive & Step-Decomposable Workflows (GAIA, SWE-bench Lite):* Specialized agents with dedicated tool interfaces divide and conquer effectively.
- **What We Do (Our Contribution):** We map the exact phase boundary and crossover threshold where the advantage flips from the quantized single agent to the multi-agent system based on task complexity, reasoning depth, and tool reliance.

---

### The Real-World Application Gap (The Local Deployment Dilemma)
In local workstation, on-device, and private enterprise deployments, engineers face a concrete dilemma on hardware such as an **RTX 4090 (24 GB)**, an **Apple M-series unified memory laptop (16 GB)**, or an **RTX 4060 (8 GB)**:
1. **Option A:** Host a single large model quantized to 4-bit (e.g., Qwen-2.5-32B at INT4 via AWQ).
2. **Option B:** Host an orchestrated multi-agent team of smaller models (e.g., 1× 7B orchestrator + 2× 3B tool agents via vLLM/Ollama).

Currently, zero scientific literature exists to inform this deployment decision. Our research directly provides the definitive benchmark, latency trade-offs, and accuracy guidelines for local edge practitioners.

---

### Summary of Core Scientific Contributions Claimed by This Project
1. **First Memory-Equated Evaluation:** First benchmark strictly holding physical resident VRAM ($M$) constant across single-agent and multi-agent systems.
2. **The Scale-vs-Precision Frontier:** First empirical characterization of whether aggressive quantization of large models outperforms multi-agent collaboration of smaller, higher-precision models.
3. **Task-Type Phase Boundary:** Formal mapping of when SAS dominates (closed-book multi-hop reasoning & parametric recall) versus when MAS dominates (tool-augmented decomposition).
4. **Memory Allocation Breakdown:** Empirical guidance on how to partition a fixed memory budget: concentrated in one model, allocated to an orchestrator, or distributed among peer debate agents.

---

## 3. Formal Experimental Design Matrix

To make this rigorous enough for top-tier venues (NeurIPS, ICLR, ACL, EMNLP), the experiment needs clean isolation of variables.

### A. The Controlled Axis: Memory Budget ($M$)
Define exact resident memory tiers reflecting standard hardware boundaries:

- **Tier 1 (Consumer / Edge):** **8 GB VRAM** (e.g., RTX 4060, Apple unified memory base)
- **Tier 2 (Prosumer Workstation):** **16 GB VRAM** (e.g., RTX 4080, T4, V100)
- **Tier 3 (Flagship Single-GPU):** **24 GB VRAM** (e.g., RTX 3090, RTX 4090, A10G)

> **Residency Definition:**  
> Total allocated memory $M_{\text{total}} = M_{\text{weights}} + M_{\text{KV-cache}} + M_{\text{runtime-overhead}} \le M_{\text{budget}}$.  
> *(Both systems must be able to reside and infer concurrently within the target VRAM without host RAM offloading).*

### B. The Competing Paradigms

| Budget Tier | Single-Agent Baseline (SAS - Big & Quantized) | Multi-Agent Baseline (MAS - Small & High-Precision) |
| :--- | :--- | :--- |
| **8 GB** | 14B @ 4-bit (or 7B/8B @ 8-bit) | 2× 3B @ FP16/INT8 or 1× 3B (Orchestrator) + 2× 1B (Workers) |
| **16 GB** | 32B @ 4-bit (or 14B @ 8-bit) | 2× 7B/8B @ INT8 or 1× 7B + 2× 3B @ FP16 |
| **24 GB** | 70B/72B @ 3-bit/4-bit (or 32B @ 8-bit) | 3× 8B @ INT8 or 1× 14B + 2× 7B @ INT8 |

*(Using uniform model families such as **Qwen 2.5** or **Llama 3.1 / 3.2** to prevent confounding cross-architecture inductive biases).*

### C. MAS Topologies Under Budget
1. **Hierarchical (Orchestrator-Worker):** A slightly larger orchestrator delegates subtasks to specialized smaller workers.
2. **Peer Review / Debate (Reflection):** Two equal-sized small models cross-verify and debate answers.
3. **Sequential Pipeline (Decompose $\to$ Execute $\to$ Verify):** Dedicated modular sub-agents handling stages sequentially.

### D. Primary Reasoning Benchmarks & Dataset Selection
To prevent benchmark fatigue and cherry-picking accusations, we focus on **3 gold-standard datasets** representing 3 distinct modes of reasoning:

1. **Multi-Hop Relational Synthesis:** [**FRAMES**](https://arxiv.org/abs/2409.05591) (Factuality, Retrieval, and Multi-hop Evaluation, 2–15 hops).
   - *Purpose:* Replicates Tran & Kiela (2026) to test if inter-agent handoffs suffer context decay under memory constraints.
2. **Formal Symbolic & Quantitative Deduction:** **GSM8K** (grade-school arithmetic) and **MATH-500** (high-school/Olympiad derivation).
   - *Purpose:* Tests step-by-step logical derivation where a single arithmetic error ruins the reasoning chain.
3. **Deep Conceptual STEM & Anti-Memorization:** **GPQA Diamond** (graduate-level physics, chemistry, biology).
   - *Purpose:* Tests parametric knowledge depth where web search is useless and only deep model representations succeed.

---

## 4. Mathematical Evaluation Framework & Decision Metrics

To scientifically declare whether SAS or MAS is "better," we formulate a multi-dimensional evaluation methodology incorporating accuracy, statistical significance, efficiency ratios, and Pareto dominance.

```
                              Decision Triad
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
  [1. Accuracy & EM]     [2. Significance (p < 0.05)]   [3. Pareto ROI (η_M, η_T)]
  Task success rate         McNemar's χ² test &            Accuracy per VRAM GB &
    on identical splits      Bootstrap 95% CIs              Accuracy per 1k tokens
```

### 1. Primary Task Accuracy: Exact Match (EM)
For ground-truth reference $y_i^*$ and model output $\hat{y}_i$:
$$\text{Acc} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\hat{y}_i = y_i^*)$$
*(For mathematical datasets like MATH-500, symbolic parsing via `sympy` verifies exact numerical and algebraic equivalence).*

### 2. Statistical Significance Testing: McNemar's Test
A simple percentage difference (e.g., $71.2\%$ vs. $68.5\%$) is insufficient without proving statistical significance. Because both architectures are evaluated on the **exact same test questions**, we compute **McNemar's Chi-Square Test** with continuity correction on the $2 \times 2$ contingency matrix:

$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}$$

* Where $b$ is the count of items where SAS is correct and MAS is incorrect, and $c$ is the count where MAS is correct and SAS is incorrect.
* **Decision Rule:** A performance margin is statistically valid *if and only if* **$p\text{-value} < 0.05$** ($\chi^2 > 3.841$ at 1 degree of freedom).
* **Paired Bootstrap Resampling:** We also compute **95% Confidence Intervals** across $B = 1,000$ bootstrap iterations to verify non-overlapping error margins.

### 3. Pareto Dominance Condition
Holding peak resident memory within budget ($M_{\text{peak}} \le M_{\text{budget}}$), System $A$ strictly **Pareto-dominates** System $B$ ($A \succ B$) if:

$$\text{Acc}(A) \ge \text{Acc}(B) \quad \land \quad L(A) \le L(B) \quad \land \quad T(A) \le T(B)$$

with at least one strict inequality, where $L$ is end-to-end wall-clock latency and $T$ is total tokens consumed per query.

### 4. Memory-Efficiency ROI Ratio ($\eta_M$)
Quantifies the accuracy return-on-investment per gigabyte of resident GPU memory:
$$\eta_M = \frac{\text{Accuracy (\%)}}{\text{Peak Resident VRAM (GB)}}$$

*Higher $\eta_M$ indicates superior memory density.*

### 5. Token Economy Efficiency Ratio ($\eta_T$)
*(Inspired by Wang et al., EMNLP 2024)*  
Quantifies how efficiently the system converts token generation into correct reasoning answers:
$$\eta_T = \frac{\text{Accuracy (\%)}}{\mathbb{E}[\text{Total Generated Tokens}] / 1000}$$

*An architecture that spends 3,500 tokens in multi-agent debate to achieve 70% accuracy is 5× less token-efficient than a single agent achieving 69% with 700 tokens.*

### 6. Phase Boundary & Crossover Threshold ($\theta^*$)
To discover the exact task conditions that favor one paradigm over the other, we model the performance gap $\Delta$ as a function of task complexity $\theta$ (reasoning hop count or tool dependencies):

$$\Delta(\theta) = \text{Score}_{\text{MAS}}(\theta) - \text{Score}_{\text{SAS}}(\theta)$$

* $\Delta(\theta) < 0$: Quantized Single Agent dominates (quantization degradation is smaller than multi-agent coordination decay).
* $\Delta(\theta) > 0$: Multi-Agent System dominates (task decomposition and specialization outweigh small model capacity limits).
* **The Crossover Point $\theta^*$:** The mathematical threshold where $\Delta(\theta^*) = 0$ defines the paper's core theoretical contribution.

---

### Architectural Decision Matrix

| Evaluation Dimension | Mathematical Formulation | Proves Single-Agent (SAS) Superiority | Proves Multi-Agent (MAS) Superiority |
| :--- | :--- | :--- | :--- |
| **Reasoning Accuracy** | $\text{Acc} = \frac{1}{N} \sum \mathbb{I}(\hat{y}=y^*)$ | Higher accuracy on multi-hop derivation (FRAMES, MATH). | Higher accuracy on decomposed sub-stages. |
| **Statistical Confidence** | $\chi^2 > 3.841$ ($p < 0.05$) | Performance gap is statistically significant over $N$ runs. | Performance gap is statistically significant over $N$ runs. |
| **Memory Density** | $\eta_M = \text{Acc} / \text{VRAM}_{\text{peak}}$ | Higher accuracy achieved per gigabyte of VRAM. | Higher accuracy achieved per gigabyte of VRAM. |
| **Token Economy** | $\eta_T = \text{Acc} / (\text{Tokens}/1000)$ | Generates fewer intermediate tokens to reach final answer. | Generates fewer intermediate tokens to reach final answer. |
| **Latency** | $T_{\text{wall-clock}}$ & $\text{TTFT}$ | Lower latency due to zero inter-agent round trips. | Lower latency due to parallel worker execution. |

---

## 5. Proposed Repository Architecture (`project-agere`)

To structure this research cleanly from day one, here is the recommended architecture:

```
project-agere/
├── configs/
│   ├── hardware_tiers/         # 8gb.yaml, 16gb.yaml, 24gb.yaml
│   ├── models/                 # Model registry (Qwen2.5, Llama3) with quant configs (AWQ, GPTQ, bnb)
│   ├── systems/
│   │   ├── sas/                # Single-agent configurations
│   │   └── mas/                # Multi-agent topology configurations (hierarchical, debate, pipeline)
│   └── benchmarks/             # Benchmark evaluation configs (dataset paths, few-shot prompts)
├── src/
│   ├── agents/
│   │   ├── base.py             # Agent abstract base class
│   │   ├── single_agent.py     # SAS implementation with standard prompt strategies (CoT, ReAct)
│   │   ├── orchestrator.py     # Hierarchical MAS orchestrator
│   │   ├── worker.py           # Specialized worker agent
│   │   └── debate.py           # Multi-agent debate / reflection protocol
│   ├── inference/
│   │   ├── engine.py           # Uniform inference engine (vLLM / HuggingFace Transformers / SGLang)
│   │   └── quantization.py     # Quantization loaders (4-bit, 8-bit, AWQ, GPTQ)
│   ├── profiling/
│   │   ├── memory_tracker.py   # High-resolution GPU VRAM residency & peak memory profiler
│   │   └── token_tracker.py    # Tracks prompt, completion, and communication overhead tokens
│   ├── benchmarks/
│   │   ├── runner.py           # Unified evaluation harness
│   │   └── datasets/           # Benchmark loaders (GSM8K, MuSiQue, GAIA, etc.)
│   └── analysis/
│       ├── parse_results.py    # Metric aggregation
│       └── plot_tradeoffs.py   # Publication-ready plots (Pareto frontiers, memory vs. accuracy)
├── experiments/                # Raw experiment runs, logs, and outputs
├── literature_review/          # Complete literature reviews, synthesis & 35 article study guides
│   ├── README.md               # Master synthesis & 15-paper filtered bibliography
│   ├── summaries/              # 35 individual article study summaries
│   └── *.md                    # Thematic literature review pillars
├── sources/                    # 35 downloaded primary research PDFs & dictionary
├── paper/                      # LaTeX source, tables, and figures
├── pyproject.toml / requirements.txt
└── README.md
```

---

## 6. Next Steps & Implementation Choices

Before we initialize the repository and build the experimental pipeline, please share your preferences on:

1. **Hardware Setup:** What GPU(s) or compute environment will you run experiments on (e.g., local RTX 3090/4090, 16 GB laptop GPU, cloud A100/H100, or RunPod/Colab)?
2. **Target Model Family:** Would you prefer **Qwen 2.5** (versatile, 0.5B to 72B), **Llama 3.1/3.2** (1B to 70B), or both?
3. **Inference Backend:** Would you prefer **vLLM** (best for serving multiple concurrent models/workers with paged KV cache) or standard **PyTorch + Hugging Face / bitsandbytes / AWQ** (simplest for exact VRAM allocation monitoring)?
4. **Primary Benchmark Focus:** Should we start prototyping the evaluation pipeline on **multi-hop reasoning** (e.g., GSM8K / MuSiQue / FRAMES) or **tool-agent benchmarks** (e.g., GAIA / ToolBench)?
