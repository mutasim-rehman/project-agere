# Master Literature Review & Research Synthesis
## Spend It Together or Spend It Big: How Multi-Agent Orchestration and Quantization Interact Under a Fixed Memory Budget
*(Project Agere — A 2×2 Factorial Study of Architectural Modularity and Post-Training Quantization Under Strict VRAM Parity)*

> **Overarching Research Question:**  
> *Given a fixed, non-negotiable physical hardware memory budget (resident GPU VRAM $M$), do the choice of architecture (Single-Agent monolithic vs. Multi-Agent modular orchestration) and the choice of compression strategy (retain smaller models at native FP16 precision vs. scale parameter count up and quantize) act independently, or do they interact — such that the optimal compression strategy depends on which architecture is chosen, and vice versa?*

This document provides the master synthesis of our in-depth academic literature review of **43 primary research papers** published between **2024 and 2026** (excluding all surveys, SLRs, and informal benchmarks). Every paper is analyzed across its problem statement, methodology, theoretical novelty, empirical findings, critical limitations, and exact role in our **2×2 Factorial Experimental Design**.

---

## 1. The 2×2 Factorial Experimental Framework

Prior literature on agent scaling (e.g., Tran & Kiela, 2026; Zywot et al., 2026) and post-training model compression (e.g., AWQ, QuaRot, Bench360) has operated in separate intellectual silos. Crucially, **no prior study has evaluated an orchestrated multi-agent system composed of larger, quantized models against a giant quantized single model and a native full-precision multi-agent team under identical resident memory limits.**

Holding peak resident physical VRAM strictly equal ($M_{\text{peak}} \approx 0.95 \times M_{\text{budget}}$) across 15 fine-grained hardware tiers (4 GB to 32 GB):

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

### The Four Base Questions & The Headline Interaction Term
1. **RQ1 (Cell A vs. Cell B — Baseline Replication):** Does a larger, quantized single model outperform a smaller, full-precision single model at equal memory? *(Replicates Bench360 as our internal control baseline).*
2. **RQ2 (Cell C vs. Cell B — Original Agere Hypothesis):** Does a multi-agent system of smaller, full-precision agents outperform a single larger, quantized model at equal memory?
3. **RQ3 (Cell D vs. Cell A — Quantized MAS vs. Small Generalist):** Does a multi-agent system of larger, quantized agents outperform a single smaller, full-precision model at equal memory?
4. **RQ4 (Cell D vs. Cell B — Quantized MAS vs. Giant Generalist):** Does a multi-agent system of larger, quantized agents outperform a single, much larger quantized model at equal memory?
5. **RQ5 (The Interaction Term — Core Theoretical Prize):** Does quantization degrade performance **more, less, or the same amount** when applied inside an orchestrated multi-agent system ($D$ vs. $C$) as it does inside a single model ($B$ vs. $A$)?

$$\Delta_{\text{interaction}} = [\text{Score}(D) - \text{Score}(C)] - [\text{Score}(B) - \text{Score}(A)]$$

* **Hypothesis 1 (Compounding Error / "Double Penalty" — $q_s$ Inequality):** $\Delta_{\text{interaction}} < 0$. Quantization noise compounds multiplicatively across inter-agent natural language handoffs. Discretized intermediate outputs amplify errors that remain continuous inside a monolithic model, validating Chen et al.'s $q_s$ MoE capacity penalty at the macro-orchestration layer.
* **Hypothesis 2 (Role Specialization Noise-Buffering):** $\Delta_{\text{interaction}} > 0$. Sub-agents assigned narrow, constrained tasks experience a collapsed active token manifold, rendering specialized roles more resilient to precision loss than a single generalist maintaining long-range multi-task state.
* **Null Hypothesis ($H_0$):** $\Delta_{\text{interaction}} = 0$. Architectural modularity and compression strategy are orthogonal, strictly additive design decisions.

---

## 2. The Core Scientific Tension & Research Gaps

```
                         ┌─────────────────────────────────────────────────────────┐
                         │              The Physical VRAM Ceiling (M)              │
                         │          Strict Memory Utilization Parity (≥95%)        │
                         └────────────────────────────┬────────────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       ▼                                                             ▼
         ┌───────────────────────────┐                                 ┌───────────────────────────┐
         │     Single-Agent (SAS)    │                                 │     Multi-Agent (MAS)     │
         ├───────────────────────────┤                                 ├───────────────────────────┤
         │ Cell A: Smaller FP16      │                                 │ Cell C: Smaller FP16 Team │
         │ • Full precision baseline │                                 │ • Native representation   │
         │ • Limited parameter scale │                                 │ • Role specialization     │
         │                           │                                 │ • Context bloat risk      │
         │ Cell B: Larger Quantized  │                                 │                           │
         │ • SOTA 4-bit / 2-bit AWQ  │                                 │ Cell D: Larger Quantized  │
         │ • Deeper pre-trained scale│                                 │ • Large sub-agents in MAS │
         │ • Quant noise in generalist│                                │ • Specialization vs noise │
         └─────────────┬─────────────┘                                 └─────────────┬─────────────┘
                       │                                                             │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      ▼
                                   ┌────────────────────────────────────┐
                                   │      The Interaction Question      │
                                   │       Δ_interaction = ?            │
                                   │  • Compounding error cascade? (<0) │
                                   │  • Role-specialization buffer? (>0)│
                                   └────────────────────────────────────┘
```

### Gap 1: Compute-Budget vs. Physical Memory Disconnect
* **Prior Work:** Tran & Kiela (2026), Wang et al. (EMNLP 2024).  
  Normalized resources using "thinking token budgets" or FLOPs, finding single models superior on multi-hop reasoning.
* **The Blind Spot:** Tokens and FLOPs are soft operational costs. In local and on-device deployment, **GPU VRAM is a hard physical ceiling**. Exceeding it triggers fatal CUDA Out-of-Memory (OOM) crashes or catastrophic PCIe offloading latency.
* **Our Contribution:** We establish the first benchmark equalizing physical resident VRAM ($M$) across 15 fine-grained tiers (4 GB to 32 GB in 2 GB steps) with $\ge 95\%$ memory saturation.

### Gap 2: The Cross-Silo Disconnect (The Missing 2×2 Cell)
* **Prior Work:**
  * *Quantization Literature (AWQ, QuaRot, Bench360):* Evaluates monolithic models in isolation; never tests whether memory is better spent on an orchestrated multi-agent team.
  * *Agent Literature (MoA, MetaGPT, ChatDev, DyLAN):* Explores multi-agent synergy assuming unconstrained cloud API memory; never profiles resident VRAM or quantizes sub-agents.
* **The Blind Spot:** Neither field evaluates **Quantized Multi-Agent Systems (Cell D)**. Does quantization help or hurt more when models are orchestrated?
* **Our Contribution:** We complete the full 2×2 factorial grid, evaluating Cells A, B, C, and D under identical memory footprints.

### Gap 3: The Micro-to-Macro Capacity Penalty ($q_s$ Inequality)
* **Prior Work:** Chen et al. (2026, the $q_s$ inequality).  
  Proved mathematically that sparse Mixture-of-Experts (MoEs) suffer an inference double penalty under total parameter parity compared to dense models.
* **The Blind Spot:** No prior work has tested whether this capacity penalty operates at the coarser, macro-orchestration level of multi-agent systems where sub-agents communicate via natural language tokens.
* **Our Contribution:** We provide the first empirical test of whether MAS coordination incurs a macro-level $q_s$ capacity penalty under strict memory parity.

### Gap 4: Confounded Tool Access in Small-Agent Studies
* **Prior Work:** Zywot et al. (2026).  
  Reported small agents beating large models on GAIA, but confounded the comparison by giving tools exclusively to small agents.
* **The Blind Spot:** Fails to isolate whether the advantage came from multi-agent orchestration or simply tool access.
* **Our Contribution:** We provide identical tool access, environment sandboxes, and memory budgets to both SAS and MAS configurations.

### Gap 5: The Task-Type Moderator Spectrum & The Dual-Benchmark Design
* **Prior Work:** Contradictory claims in literature: Tran & Kiela (2026) claimed single agents universally match or beat multi-agent systems, while Żywot et al. (2026) claimed small agent teams beat a 32B model.
* **The Blind Spot:** They tested opposite ends of the task spectrum! Tran & Kiela evaluated multi-hop reasoning (FRAMES, MuSiQue) where the **Data Processing Inequality (DPI)** causes information to dilute across sequential handoffs. Żywot et al. evaluated **GAIA** where **role specialization and tool interfaces** allow small models to divide and conquer. Narrowing evaluation to multi-hop reasoning alone would merely confirm Tran & Kiela's findings under a different budget axis.
* **Our Contribution (Minimal Dual-Benchmark Design):** We turn task type into a controlled experimental variable by anchoring evaluation on two contrasting, lean benchmark slices:
  1. **Anchor 1 (Primary / Base Paper Domain):** A curated 100-task slice of **GAIA** (Levels 1 & 2 with standardized Python, search, and file tools), testing the **Role Specialization Buffering Hypothesis ($\Delta_{\text{interaction}} > 0$)**.
  2. **Anchor 2 (Calibration Anchor / DPI Test):** A curated 150-question slice of **MuSiQue / FRAMES** (2-to-4 hops, closed-book), testing the **Compounding Error Double Penalty Hypothesis ($\Delta_{\text{interaction}} < 0$)** and providing a direct sanity check against Tran & Kiela's published baselines.

---

## 3. Structure of the Literature Review

The review is organized into five thematic synthesis documents, 35 dedicated study summaries in [`summaries/`](./summaries/README.md), and our catalog in [`../sources/INDEX.md`](../sources/INDEX.md):

| Document | Covered Papers | Core Themes & 2×2 Relevance |
| :--- | :--- | :--- |
| [**`01_mas_vs_sas_collaboration.md`**](./01_mas_vs_sas_collaboration.md) | **01 – 08** | Core SAS vs. MAS baselines (Tran & Kiela, Zywot et al.), agent scaling theory (Kim et al., Li et al.), and failure taxonomy (Cemri et al. MAST). Direct basis for Cells A, C, and D. |
| [**`02_mas_topologies_and_frameworks.md`**](./02_mas_topologies_and_frameworks.md) | **09 – 14** | Concrete multi-agent topologies: dynamic groups (AgentVerse), debate (ChatEval, ReConcile), hierarchical SOPs (MetaGPT), pipelines (ChatDev), and dynamic pruning (DyLAN). Direct basis for AHDS architecture. |
| [**`03_budget_and_memory_inference.md`**](./03_budget_and_memory_inference.md) | **15 – 21** | Budget-aware evaluation (Wang et al. EMNLP), hardware VRAM profiling (Bench360), inference compute scaling (Monkeys), tool budgets, MoE capacity penalty ($q_s$ inequality), and vLLM PagedAttention. Theoretical foundation for MUPP and $\Delta_{\text{interaction}}$. |
| [**`04_quantization_and_ondevice.md`**](./04_quantization_and_ondevice.md) | **22 – 30** | Quantization algorithms for Cell B and Cell D (AWQ, QuaRot, SpinQuant, AQLM, AutoRound), sub-billion on-device design (MobileLLM), ternary BitNet, and multi-agent KV sharing (SGLang). |
| [**`05_benchmarks_and_evaluation.md`**](./05_benchmarks_and_evaluation.md) | **31 – 35** | Standardized evaluation infrastructure: tool-use (GAIA, BFCL), multi-step engineering (SWE-bench), multi-hop reasoning (FRAMES), and parametric world knowledge (MMLU-Pro). Task moderator suite. |
| [**`../sources/PAPERS_DICTIONARY.md#pillar-5-quantized-multi-agent-systems-error-cascades--shared-memory-architectures`**](../sources/PAPERS_DICTIONARY.md#pillar-5-quantized-multi-agent-systems-error-cascades--shared-memory-architectures) | **36 – 43** | **New 2025–2026 Quantized MAS & Memory Literature:** Quantized agent failure amplification (Jang et al. 2026), dynamic hallucination cascades (Jamshidi et al. 2026), Markov error snowballing (Singh & Pawar 2026), edge error taxonomies (Lin et al. 2025), shared compressed KV pools (PolyKV 2026), quantized KV handoffs (QKVShare 2026), 8 GB quantized MAS on commodity GPUs (Quantigence 2025), and singleton weight sharing (Warp-Cortex 2026). Direct empirical and theoretical foundation for Cells B, C, D, and $\Delta_{\text{interaction}}$. |

---

## 4. The Filtered 15-Paper Core Bibliography

The recommended **15-paper core subset** mapped to their exact roles in the 2×2 Factorial Study:

| # | Selected Paper | Venue | Role in 2×2 Factorial Paper |
| :---: | :--- | :--- | :--- |
| **1** | **Tran & Kiela (2026)** | arXiv:2604.02460 | **Primary Base Paper:** Baseline template; we swap token budgets for VRAM budgets and evaluate Cells A, B, C, D. |
| **2** | **Zywot, Chen, & de Rijke (2026)** | arXiv:2601.11327 | **Secondary Base Paper (Tool-Use):** Empirical basis for small-agent tool specialization; testbed for GAIA benchmark. |
| **3** | **Kim et al. (2025/2026)** | arXiv:2512.08296 | **Theoretical Scaling Foundation:** Topology-dependent coordination bottlenecks explaining SAS vs MAS phase boundaries. |
| **4** | **Wang et al. (MoA, 2024)** | arXiv:2406.04692 | **MAS Baseline 1:** Layered collaborative ensemble baseline for Cells C and D. |
| **5** | **Hong et al. (MetaGPT, 2024)** | ICLR 2024 (Oral) | **MAS Baseline 2:** Canonical Hierarchical Orchestrator-Worker architecture using structured SOP schemas (AHDS foundation). |
| **6** | **Wang et al. (ACL 2024)** | ACL 2024 | **Single-Agent Prompting Baseline:** Ensures Cells A and B are evaluated with rigorous CoT and self-consistency controls. |
| **7** | **Cemri et al. (MAST, 2025)** | arXiv:2503.13657 | **Error Taxonomy:** Classification framework used to analyze why Cell C or D fails (context collapse, hallucination propagation). |
| **8** | **Wang et al. (EMNLP 2024)** | EMNLP 2024 | **Budget-Aware Methodology:** Precedent for holding resource consumption strictly invariant across conditions. |
| **9** | **Lin et al. (Bench360, 2025)** | arXiv:2511.16682 | **Hardware Profiling & Control Baseline:** Replicated in Cell B (quantized single model winner); profiling standard for resident VRAM. |
| **10** | **Chen et al. ($q_s$ Inequality, 2026)** | arXiv:2603.08960 | **Theoretical Bridge for $\Delta_{\text{interaction}}$:** Formal mathematical foundation for the Compounding Noise / Double Penalty hypothesis in Cell D. |
| **11** | **Lin et al. (AWQ, 2024)** | MLSys 2024 (Best Paper) | **Quantization Engine:** Primary 4-bit weight quantization method powering Cell B (SAS-Quant) and Cell D (MAS-Quant). |
| **12** | **Ashkboos et al. (QuaRot, 2024)** | NeurIPS 2024 | **Advanced Quantization Baseline:** End-to-end 4-bit weights + activations + KV compression for extreme memory tiers. |
| **13** | **Kwon et al. (vLLM, 2023)** | SOSP 2023 / MLSys | **Serving Infrastructure:** PagedAttention runtime enforcing `--gpu-memory-utilization 0.95` across all 60 conditions. |
| **14** | **Mialon et al. (GAIA, 2024)** | ICLR 2024 | **Anchor 1 Primary Benchmark (Tool-Use):** Base paper domain testing the Role Specialization Buffering Hypothesis ($\Delta_{\text{interaction}} > 0$). |
| **15** | **Krishna et al. (FRAMES, 2024)** | EMNLP 2024 / arXiv | **Anchor 2 Calibration Benchmark (Reasoning):** Direct replication of Tran & Kiela's multi-hop domain testing the Double Penalty Hypothesis ($\Delta_{\text{interaction}} < 0$). |

---


### Additional Core 2025–2026 Literature (Direct Factorial & Architectural Grounding)
* **Jang et al. (July 2026, arXiv:2607.27275):** *Flat Score, Amplified Failures: How the Error Budget Masks Damage in Quantized LLM Agents.* Proves that 4-bit quantization causes a 2.5× amplification in agent tool failures masked by standard error budgets; establishes diagnostic failure-volume metrics for Cells B and D.
* **Singh & Pawar (June 2026, arXiv:2608.14588):** *The Hallucination Snowball: Modeling Error Propagation as State Transitions in Multi-Agent LLM Pipelines.* Models multi-agent error escalation as a Markov process, proving that inter-agent boundary verification reduces hallucination survival from 58.4% to 16.2%; provides direct mathematical justification for AHDS boundary gating.
* **Jamshidi et al. (June 2026, arXiv:2606.07937):** *Hallucination Cascade: Analyzing Error Propagation in Multi-Agent LLM Systems.* Empirically tracks claim-level error attenuation vs. factual decay across agent cascades, directly informing $\Delta_{\text{interaction}}$.
* **Patel & Joshi (April 2026, arXiv:2604.24971):** *PolyKV: A Shared Asymmetrically-Compressed KV Cache Pool for Multi-Agent LLM Inference.* Shrinks multi-agent KV-cache memory by 97.7% via INT8 keys and 3-bit values, establishing high-density local multi-agent serving.
* **Alquwayfili (Dec 2025, arXiv:2512.12989):** *Quantigence: A Multi-Agent Framework for Post-Quantum Security Analysis on Commodity Hardware.* Demonstrates a 4-bit quantized multi-agent system outperforming single agents on multi-faceted tasks within an 8 GB consumer GPU budget (empirical prototype of Cell D vs. Cell A/B).

---

## 5. Paper Framing Templates

### Abstract Draft
> Deploying Large Language Model (LLM) agents under physical hardware constraints presents a fundamental architectural dilemma: given a fixed resident GPU memory budget (e.g., 8 GB, 16 GB, or 24 GB VRAM), should practitioners allocate memory to a single monolithic model compressed via post-training quantization, or partition it across an orchestrated multi-agent system? Prior literature has evaluated quantization and multi-agent orchestration in isolation, leaving the interaction between architectural modularity and precision unexamined.
> 
> In this paper, we present the first **2×2 Factorial Iso-Memory Study** crossing Architectural Modularity (Single-Agent vs. Multi-Agent) with Model Precision (Native FP16 vs. Quantized Scaling) across 15 fine-grained hardware memory tiers (4 GB to 32 GB at 2 GB intervals). Under our strict **Memory Utilization Parity Protocol (MUPP)**, every experimental condition physically saturates $\ge 95\%$ of resident VRAM, eliminating under-allocation confounds. To resolve the contradiction between prior studies favoring single agents on pure multi-hop reasoning (Tran & Kiela, 2026) and those favoring multi-agent teams on tool-assisted tasks (Żywot et al., 2026), we adopt a **Minimal Dual-Benchmark Design** spanning a tool-intensive slice (GAIA) and a multi-hop reasoning slice (MuSiQue/FRAMES). We measure the interaction term $\Delta_{\text{interaction}} = [\text{Score}(D) - \text{Score}(C)] - [\text{Score}(B) - \text{Score}(A)]$, testing whether quantization noise compounds across agent handoffs (manifesting a macro-level MoE $q_s$ capacity penalty) or whether role specialization buffers against precision loss. Our findings establish the empirical Pareto frontier for memory-constrained agent deployment.

### Section 1: Introduction Draft
> In real-world edge, workstation, and private cloud deployments, GPU Video RAM (VRAM) is an unyielding physical boundary. Unlike software token budgets or compute FLOPs—which can be traded for latency—exceeding resident VRAM triggers immediate CUDA Out-Of-Memory (OOM) crashes or severe PCIe offloading penalties [Lin et al., 2025]. System architects facing a fixed memory envelope (e.g., 16 GB) confront two competing scaling paradigms:
> 
> 1. **Quantized Monolithic Scaling:** Allocate the full budget to a single large model compressed aggressively via post-training quantization [Lin et al., 2024; Ashkboos et al., 2024].
> 2. **Modular Multi-Agent Orchestration:** Partition the budget across an ensemble of smaller models collaborating via structured roles [Hong et al., 2024; Zywot et al., 2026].
> 
> While recent benchmarks establish that quantized large models beat smaller full-precision models at the single-agent level [Lin et al., 2025], and agent literature shows multi-agent ensembles can improve decomposition [Wang et al., 2024], existing work leaves a critical scientific question unanswered: **Do architectural modularity and model quantization act independently, or do they interact?**
> 
> To answer this question, we formulate a 2×2 factorial design comprising four memory-equated cells: (A) Single-Agent FP16, (B) Single-Agent Quantized, (C) Multi-Agent FP16, and (D) Multi-Agent Quantized. By evaluating all four cells across 15 memory tiers, we isolate whether quantization imposes a compounding double penalty across agent communication handoffs [Chen et al., 2026] or whether narrow role specialization buffers against precision loss.

### Section 2: Related Work Draft
> **Budget-Equated Agent Evaluation:** Evaluating LLM reasoning under explicit constraints has emerged as a crucial methodology. Wang et al. (2024) and Tran & Kiela (2026) demonstrated that multi-agent systems often owe their apparent gains to inflated thinking token budgets. However, token normalization treats compute as a fungible operational cost, ignoring the rigid hardware reality that memory residency is the governing constraint in local deployment.
> 
> **Post-Training Quantization & Capacity Penalties:** Quantization techniques such as AWQ [Lin et al., 2024] and QuaRot [Ashkboos et al., 2024] have enabled 4-bit execution with minimal perplexity degradation on monolithic models. In parallel, Chen et al. (2026) derived the $q_s$ inequality, proving that dividing parameter capacity into routed sparse sub-networks (MoEs) incurs an inherent capacity penalty under total memory parity. We bridge these two fields by investigating whether quantized multi-agent orchestration suffers an analogous macro-level capacity penalty or benefits from role-constrained noise resilience.
