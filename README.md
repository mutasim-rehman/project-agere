# Spend It Together or Spend It Big: How Multi-Agent Orchestration and Quantization Interact Under a Fixed Memory Budget
*(Project Agere — A 2×2 Factorial Study of Architectural Modularity and Post-Training Quantization Under Strict VRAM Parity)*

## Research Framing & Problem Formulation

Your research addresses a fundamental, unanswered dilemma in practical AI deployment:

### Overarching Research Question
> **Given a fixed, non-negotiable physical hardware memory budget (resident GPU VRAM $M$), do the choice of architecture (Single-Agent monolithic vs. Multi-Agent modular orchestration) and the choice of compression strategy (retain smaller models at native FP16 precision vs. scale parameter count up and quantize) act independently, or do they interact — such that the optimal compression strategy depends on which architecture is chosen, and vice versa?**

### The 2×2 Factorial Experimental Grid
To isolate the main effects and evaluate their interaction, we lay out a rigorous **2×2 Factorial Experimental Design**, where all four cells are strictly equated to the exact same resident memory budget ($M_{\text{peak}} \approx 0.95 \times M_{\text{budget}}$):

| Architecture \ Precision | **Full-Precision (Native FP16/BF16)** | **Quantized (Scaled up to fit budget)** |
| :--- | :--- | :--- |
| **Single-Agent System (SAS)** | **Cell A:** Smaller single model, FP16 *(The Control: Bench360 losing baseline)* | **Cell B:** Larger single model, Quantized *(Bench360 established winner at single-model level)* |
| **Multi-Agent System (MAS)** | **Cell C:** Small sub-agents, native FP16 *(Original Agere hypothesis: native precision team)* | **Cell D (NEW):** Larger sub-agents, Quantized, Orchestrated *(The missing cell in prior literature)* |

### The Four Base Research Questions & The Core Interaction Term
1. **RQ1 (Cell A vs. Cell B — Replication Baseline):** Does a larger, quantized single model outperform a smaller, full-precision single model at equal memory? *(Replication control of Bench360).*
2. **RQ2 (Cell C vs. Cell B — Original Agere Question):** Does a multi-agent system composed of smaller, full-precision sub-agents outperform a single larger, quantized model at equal memory?
3. **RQ3 (Cell D vs. Cell A — Quantized MAS vs. Small Generalist):** Does a multi-agent system composed of larger, quantized agents outperform a single smaller, full-precision model at equal memory?
4. **RQ4 (Cell D vs. Cell B — Quantized MAS vs. Giant Generalist):** Does a multi-agent system composed of larger, quantized agents outperform a single, much larger quantized model at equal memory?
5. **RQ5 (The Headline Interaction Term — $\Delta_{\text{interaction}}$):** Does post-training quantization degrade reasoning performance **more, less, or the same amount** when applied inside an orchestrated multi-agent system ($D$ vs. $C$) compared to inside a single monolithic model ($B$ vs. $A$)?

$$\Delta_{\text{interaction}} = [ \text{Score}(D) - \text{Score}(C) ] - [ \text{Score}(B) - \text{Score}(A) ]$$

- **Hypothesis 1 (Compounding Error / "Double Penalty" — $q_s$ Inequality):** Quantization noise compounds across agent communication handoffs (Data Processing Inequality). In this case, **$\Delta_{\text{interaction}} < 0$**, meaning quantization imposes a super-additive penalty on multi-agent teams.
- **Hypothesis 2 (Role Specialization Noise-Buffering):** Constrained, role-specialized sub-agents are inherently more tolerant to quantization noise than a single generalist holding an entire multi-step reasoning context. In this case, **$\Delta_{\text{interaction}} > 0$**, meaning orchestration acts as a protective buffer against quantization loss.

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
- **What We Do (Our Contribution):** We establish the first systematic evaluation that equalizes **physical resident hardware VRAM ($M$)** across 15 fine-grained tiers (4 GB to 32 GB). We investigate whether the single-agent advantage holds when the freed memory is used to deploy a larger, post-training quantized model (Cell B) against an intact multi-agent team (Cell C) and a quantized multi-agent team of larger sub-agents (Cell D).

### Gap 2: The Cross-Silo Disconnect Between Quantization and Agent Collaboration (The Missing 2×2 Cell)
- **Prior Work:**
  - *Quantization Literature (AWQ, QuaRot, SpinQuant, Bench360):* Compresses monolithic models in isolation to minimize perplexity loss, never testing whether that memory would be better allocated to an orchestrated team of smaller models.
  - *Agent Literature (Mixture-of-Agents, AgentVerse, MetaGPT, ChatDev):* Explores multi-agent synergy under the assumption of unconstrained cloud API memory, never profiling concurrent resident GPU footprints or quantizing sub-agents.
- **The Blind Spot / Limitation:** Neither literature speaks to the other. Crucially, **no prior study has evaluated an orchestrated multi-agent system composed of larger, quantized models (Cell D)** against a single giant quantized model (Cell B) and a native full-precision multi-agent system (Cell C) under strict physical resident memory parity.
- **What We Do (Our Contribution):** We directly bridge these two literatures through a **2×2 Factorial Experimental Design**, simultaneously evaluating Architectural Modularity (Single-Agent vs. Multi-Agent) and Compression Strategy (Native FP16 vs. Quantized Scaling) across 15 standardized hardware tiers (4 GB to 32 GB).

### Gap 3: Confounded Baselines in Small-Agent Tool Research
- **Prior Work:** Żywot, Chen, & de Rijke (2026).  
  Claimed that small collaborative agents (4B) beat a large monolithic model (32B) on the GAIA benchmark.
- **The Blind Spot / Limitation:** The comparison was confounded by tool access. Small agents were equipped with external tools (Python interpreters, web search, calculators) while the large model was evaluated without tools or without equalized memory.
- **What We Do (Our Contribution):** We conduct the first unconfounded test by giving **both** the single agent and the multi-agent system identical toolkits, prompting formats (ReAct/CoT), and runtime environments under an identical resident memory envelope.

### Gap 4: The Micro-to-Macro "Capacity Penalty" Analogy & The Interaction Term
- **Prior Work:** Chen et al. (2026, the $q_s$ inequality), Cemri et al. (2025, MAST).  
  At the micro-architectural layer inside a single model, Chen et al. proved mathematically that sparse Mixture-of-Experts (MoEs) lose to dense monolithic models when total stored resident parameters are held equal.
- **The Blind Spot / Limitation:** Nobody has evaluated whether this law also governs the macro-orchestration level when models are quantized. Does quantizing sub-agents in a multi-agent system (Cell D) cause quantization noise to compound multiplicatively across lossy inter-agent handoffs, manifesting an MoE-style double penalty at the macro-orchestration layer ($\Delta_{\text{interaction}} < 0$)? Or does narrow role specialization buffer against quantization loss ($\Delta_{\text{interaction}} > 0$)?
- **What We Do (Our Contribution):** We empirically evaluate the **Architecture $\times$ Quantization Interaction Term ($\Delta_{\text{interaction}}$)**, measuring whether quantization degrades performance more, less, or equally inside an orchestrated multi-agent system compared to a monolithic model.

### Gap 5: The Task-Type Moderator Spectrum
- **Prior Work:** Flat, contradictory claims in prior literature: Tran & Kiela claimed "SAS universally wins," while MoA and Żywot et al. claimed "MAS universally wins."
- **The Blind Spot / Limitation:** Neither claim holds universally. The winner is governed by the underlying task dependency structure (Kim et al., 2025):
  - *Knowledge-Dense & Deep Logical Reasoning (MMLU-Pro, MuSiQue, FRAMES):* Small models lack the parametric depth to derive answers, and inter-agent communication is lossy (Data Processing Inequality).
  - *Tool-Intensive & Step-Decomposable Workflows (GAIA, SWE-bench Lite):* Specialized agents with dedicated tool interfaces divide and conquer effectively.
- **What We Do (Our Contribution):** We map the exact phase boundary and crossover threshold where the advantage flips between SAS and MAS across all four factorial cells based on task complexity, reasoning depth, and tool reliance.

---

### The Real-World Application Gap (The Local Deployment Dilemma)
In local workstation, on-device, and private enterprise deployments, engineers face a concrete architectural choice across hardware tiers spanning from an **RTX 3050 (4 GB)** up to an **RTX 5090 / A100 fraction (32 GB)**:
1. **Option A (SAS-FP16):** Host a smaller, native uncompressed model (e.g., 7B at FP16 on 16 GB).
2. **Option B (SAS-Quant):** Host a single giant model quantized to 4-bit (e.g., 32B at INT4 on 16 GB).
3. **Option C (MAS-FP16):** Host an orchestrated team of smaller native models (e.g., 7B + 0.5B at FP16 on 16 GB).
4. **Option D (MAS-Quant):** Host an orchestrated team of larger quantized models (e.g., two 14B at INT4 on 16 GB).

Currently, zero scientific literature exists to inform this four-way deployment decision under memory parity. Our research directly provides the definitive benchmark, latency trade-offs, and Pareto-optimal guidelines for local practitioners.

---

### Summary of Core Scientific Contributions Claimed by This Project
1. **First 2×2 Factorial Iso-Memory Evaluation:** First benchmark crossing Architectural Modularity (Single-Agent vs. Multi-Agent) with Model Compression (Native FP16 vs. Quantized Scaling) across 15 fine-grained hardware tiers (4 GB to 32 GB in 2 GB steps).
2. **Measuring the Architecture × Compression Interaction ($\Delta_{\text{interaction}}$):** First formal determination of whether post-training quantization degrades performance more, less, or equally inside multi-agent orchestration compared to single generalists, testing the macro-level $q_s$ MoE capacity penalty against the role-specialization buffering hypothesis.
3. **Memory Utilization Parity Protocol (MUPP):** Methodological standard mandating $\ge 95\%$ resident VRAM saturation across all 60 experimental conditions, eliminating the "empty VRAM" experimental confound.
4. **Dense 15-Tier Hardware Phase Boundary Resolution:** Dense 2 GB spacing mapping non-linear crossover thresholds, capability cliffs, and Pareto frontiers across real-world edge-to-workstation GPUs.

---

## 3. Formal Experimental Design Matrix

To make this rigorous enough for top-tier venues (NeurIPS, ICLR, ACL, EMNLP), the experiment needs clean isolation of variables.

### A. The Controlled Axis: Memory Budget ($M$)

We define **15 fine-grained memory tiers** spanning the full consumer-to-professional hardware spectrum. The dense 2 GB spacing (from 4 GB to 32 GB) ensures we can detect **performance dips, crossover points, and phase boundaries** with high resolution rather than interpolating across wide gaps.

| Tier | VRAM | Category | Example Hardware |
| :--- | :--- | :--- | :--- |
| 1 | **4 GB** | Ultra-Edge / Mobile | RTX 3050 Mobile, Intel Arc A380 |
| 2 | **6 GB** | Entry Mobile / Legacy | RTX 4050 Mobile, RTX 2060 |
| 3 | **8 GB** | Consumer / Edge | RTX 4060, Apple M2 8 GB |
| 4 | **10 GB** | Apple Unified / Cloud Fractional | Apple M-series 10 GB, fractional cloud GPU |
| 5 | **12 GB** | Mainstream Workstation | RTX 4070, Tesla T4 |
| 6 | **14 GB** | Mid-Range Workstation | RTX 4060 Ti (16 GB variant), Intel Arc A770 |
| 7 | **16 GB** | Prosumer Workstation | RTX 4080, Apple M-series 16 GB |
| 8 | **18 GB** | Extended Prosumer | RTX 5070, fractional A100 |
| 9 | **20 GB** | High-End Workstation | RTX 3080 20 GB, A30 (partial) |
| 10 | **22 GB** | Near-Flagship | Cloud fractional A100, multi-GPU partial |
| 11 | **24 GB** | Flagship Single-GPU | RTX 3090, RTX 4090, A10G |
| 12 | **26 GB** | Extended Flagship | Partial A100, fractional H100 |
| 13 | **28 GB** | Professional Entry | A100-40GB (partial), RTX 5090 |
| 14 | **30 GB** | Professional Mid | V100-32GB (partial), A100 fractional |
| 15 | **32 GB** | Professional / Multi-GPU | V100-32GB, A100-40GB partial, RTX 5090 |

> **Residency Definition:**  
> Total allocated memory $M_{\text{total}} = M_{\text{weights}} + M_{\text{KV-cache}} + M_{\text{runtime-overhead}} \le M_{\text{budget}}$.  
> *(Both systems must be able to reside and infer concurrently within the target VRAM without host RAM offloading).*  
> Assuming ~0.5–1 GB for CUDA runtime overhead and KV-cache at 2048-token context length.

### B. The Competing Paradigms

> **Fundamental Design Constraint:** Quantization is permitted **only** in SAS configurations. All MAS agents must run at **native precision (FP16/BF16)** — no INT8, INT4, or lower-bit quantization. This ensures the comparison directly tests the core research question: *Can teams of small, full-precision models outperform a single large, aggressively quantized model?*

#### B.0 FP16 Model Weight Reference Table (Qwen 2.5 Family)

All MAS VRAM estimates are based on this reference. SAS models are quantized and use proportionally less.

| Model | FP16 Weight Size | INT8 Size | INT4 (AWQ) Size | 2-bit Size | 1-bit Size |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Qwen2.5-0.5B | ~1.0 GB | ~0.5 GB | ~0.3 GB | ~0.15 GB | ~0.08 GB |
| Qwen2.5-1.5B | ~3.0 GB | ~1.5 GB | ~0.9 GB | ~0.45 GB | ~0.23 GB |
| Qwen2.5-3B | ~6.0 GB | ~3.0 GB | ~1.8 GB | ~0.9 GB | ~0.45 GB |
| Qwen2.5-7B | ~14.0 GB | ~7.0 GB | ~4.0 GB | ~2.0 GB | ~1.0 GB |
| Qwen2.5-14B | ~28.0 GB | ~14.0 GB | ~7.0 GB | ~3.5 GB | ~1.75 GB |
| Qwen2.5-32B | ~64.0 GB | ~32.0 GB | ~17.0 GB | ~8.0 GB | ~4.0 GB |
| Qwen2.5-72B | ~144.0 GB | ~72.0 GB | ~38.0 GB | ~18.0 GB | ~9.0 GB |

#### B.0.1 Memory Utilization Parity Protocol (MUPP)

> **Core Methodological Mandate:** In every comparison between a Single-Agent System (quantized at bit-width $b$) and a Multi-Agent System (native FP16 team), **both architectures must actually saturate the entire memory budget allotted to that tier ($\ge 95\%$ resident VRAM utilization)**.
> 
> Under strict memory parity, evaluating a system that leaves 30–50% of the hardware capacity unallocated introduces a fatal experimental confound (under-allocation bias). To guarantee rigorous fairness, Project Agere implements a **two-level memory saturation mechanism**:
> 1. **Model & Quantization Calibration (Weight Saturation):** For each tier, the Single-Agent model and its quantization bit-width $b$ are specifically chosen to fill 75–90% of the hardware budget in model weights (e.g., Qwen2.5-14B @ INT4 on 8 GB, Qwen2.5-14B @ INT8 on 16 GB, Qwen2.5-72B @ 2.5-bit on 24 GB). Likewise, MAS agent teams are packed to occupy 80–95% of the tier budget at native FP16.
> 2. **Runtime KV-Cache Reservoir Allocation (`gpu_memory_utilization = 0.95`):** At inference runtime (via vLLM / SGLang / PyTorch memory pool), any remaining headroom between model weights and 95% of total budget is pre-allocated into the active KV-cache buffer. Thus, **every test condition physically resides at $\ge 95\%$ of the physical VRAM budget throughout execution**.

##### Master Iso-Memory Head-to-Head Comparison Matrix

The table below defines the primary **Iso-Memory Direct Comparison** for each of the 15 hardware tiers, demonstrating that both SAS and MAS achieve $\ge 95\%$ memory saturation:

| Tier | VRAM | Saturating SAS (Quantized) | SAS VRAM (Util) | Saturating MAS (FP16 Only) | MAS VRAM (Util) | AHDS Architecture (FP16) | AHDS VRAM (Util) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **4 GB** | 4 GB | 3B-Instruct @ INT8 | 3.8 GB (95.0%) | MAS-4G-A: 1× 0.5B (orch) + 2× 0.5B (workers) | 3.8 GB (95.0%) | 0.5B orch + 0.5B worker + 0.5B verif | 3.8 GB (95.0%) |
| **6 GB** | 6 GB | 7B-Instruct @ INT6 (Q6_K) | 5.8 GB (96.7%) | MAS-6G-A: 1× 1.5B (orch) + 2× 0.5B (workers) | 5.8 GB (96.7%) | 1.5B orch + 0.5B worker + 0.5B verif | 5.8 GB (96.7%) |
| **8 GB** | 8 GB | 14B-Instruct @ INT4-AWQ | 7.8 GB (97.5%) | MAS-8G-A: 1× 3B (orch) + 1× 0.5B (worker) | 7.8 GB (97.5%) | 1.5B orch + 1.5B worker + 0.5B verif | 7.8 GB (97.5%) |
| **10 GB** | 10 GB | 14B-Instruct @ INT5 (Q5_K) | 9.6 GB (96.0%) | MAS-10G-A: 1× 3B (orch) + 1× 1.5B (worker) | 9.8 GB (98.0%) | 3B orch + 1.5B worker | 9.8 GB (98.0%) |
| **12 GB** | 12 GB | 14B-Instruct @ INT6 (Q6_K) | 11.7 GB (97.5%) | MAS-12G-A: 1× 3B (orch) + 1× 1.5B (worker 1) + 2× 0.5B (workers) | 11.8 GB (98.3%) | 3B orch + 1.5B worker + 0.5B verif | 11.5 GB (95.8%) |
| **14 GB** | 14 GB | 32B-Instruct @ INT3 (Q3_K) | 13.5 GB (96.4%) | MAS-14G-A: 1× 3B (orch) + 1× 3B (worker) | 13.5 GB (96.4%) | 3B orch + 3B worker + 0.5B verif | 13.8 GB (98.6%) |
| **16 GB** | 16 GB | 14B-Instruct @ INT8 | 15.5 GB (96.9%) | MAS-16G-A: 1× 7B (orch) + 1× 0.5B (worker) | 15.8 GB (98.8%) | 3B orch + 3B worker + 1.5B verif | 15.8 GB (98.8%) |
| **18 GB** | 18 GB | 32B-Instruct @ INT4-AWQ | 17.4 GB (96.7%) | MAS-18G-A: 1× 7B (orch) + 1× 1.5B (worker) + 1× 0.5B (worker) | 18.0 GB (100.0%) | 7B orch + 0.5B worker + 0.5B verif | 17.5 GB (97.2%) |
| **20 GB** | 20 GB | 72B-Instruct @ 2-bit (AQLM) | 19.2 GB (96.0%) | MAS-20G-A: 1× 7B (orch) + 1× 3B (worker) | 20.0 GB (100.0%) | 7B orch + 1.5B worker + 0.5B verif | 19.5 GB (97.5%) |
| **22 GB** | 22 GB | 32B-Instruct @ INT5 (Q5_K) | 21.2 GB (96.4%) | MAS-22G-A: 1× 7B (orch) + 1× 3B (worker) | 21.5 GB (97.7%) | 7B orch + 3B worker + 0.5B verif | 21.8 GB (99.1%) |
| **24 GB** | 24 GB | 72B-Instruct @ 2.5-bit (AQLM/EXL2) | 23.5 GB (97.9%) | MAS-24G-A: 1× 7B (orch) + 1× 3B (worker 1) + 1× 1.5B (worker 2) | 23.8 GB (99.2%) | 7B orch + 3B worker + 1.5B verif | 23.8 GB (99.2%) |
| **26 GB** | 26 GB | 32B-Instruct @ INT6 (Q6_K) | 25.5 GB (98.1%) | MAS-26G-A: 1× 7B (orch) + 1× 3B (worker 1) + 1× 3B (worker 2) | 26.0 GB (100.0%) | 7B orch + 3B worker + 1.5B verif | 25.5 GB (98.1%) |
| **28 GB** | 28 GB | 72B-Instruct @ 3-bit (Q3_K) | 27.5 GB (98.2%) | MAS-28G-A: 1× 7B (orch) + 1× 3B (worker 1) + 1× 3B (worker 2) | 27.5 GB (98.2%) | 7B orch + 3B worker + 3B verif | 27.5 GB (98.2%) |
| **30 GB** | 30 GB | 14B-Instruct @ FP16 | 29.5 GB (98.3%) | MAS-30G-A: 1× 7B (orch) + 1× 7B (worker) | 29.5 GB (98.3%) | 7B orch + 7B worker + 0.5B verif | 29.5 GB (98.3%) |
| **32 GB** | 32 GB | 72B-Instruct @ 3.5-bit (AWQ/GGUF) | 31.0 GB (96.9%) | MAS-32G-A: 1× 14B (orch) + 1× 1.5B (worker) | 31.8 GB (99.4%) | 7B orch + 7B worker + 0.5B verif | 31.0 GB (96.9%) |

#### B.0.2 Master 2×2 Factorial Iso-Memory Comparison Table

The table below details the complete 2×2 factorial matrix across all 15 memory tiers (4 GB to 32 GB). Every cell is strictly matched to $\ge 95\%$ resident VRAM utilization under the Memory Utilization Parity Protocol:

| Tier | VRAM | Cell A: SAS-FP16 (Control) | Cell B: SAS-Quant (Scaled) | Cell C: MAS-FP16 (Original) | Cell D: MAS-Quant (NEW!) | VRAM Saturation |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **4 GB** | 4 GB | 1.5B-Instruct @ FP16 | 3B-Instruct @ INT8 | MAS-4G-C: 3× 0.5B FP16 | MAS-Q-4G: 1× 3B @ INT4 (orch) + 1× 1.5B @ INT8 (worker) | **>= 95.0%** |
| **6 GB** | 6 GB | 1.5B-Instruct @ FP16 | 7B-Instruct @ INT6 (Q6_K) | MAS-6G-A: 1× 1.5B (orch) + 2× 0.5B (workers) FP16 | MAS-Q-6G: 1× 7B @ INT4 (orch) + 1× 1.5B @ INT8 (worker) | **>= 95.0%** |
| **8 GB** | 8 GB | 3B-Instruct @ FP16 | 14B-Instruct @ INT4-AWQ | MAS-8G-A: 1× 3B (orch) + 1× 0.5B (worker) FP16 | MAS-Q-8G: 1× 7B @ INT4 (orch) + 1× 7B @ INT4 (worker) | **>= 95.0%** |
| **10 GB** | 10 GB | 3B-Instruct @ FP16 | 14B-Instruct @ INT5 (Q5_K) | MAS-10G-A: 1× 3B (orch) + 1× 1.5B (worker) FP16 | MAS-Q-10G: 1× 14B @ INT4 (orch) + 1× 1.5B @ INT8 (worker) | **>= 95.0%** |
| **12 GB** | 12 GB | 3B-Instruct @ FP16 | 14B-Instruct @ INT6 (Q6_K) | MAS-12G-A: 1× 3B (orch) + 1× 1.5B + 2× 0.5B FP16 | MAS-Q-12G: 1× 14B @ INT4 (orch) + 1× 3B @ INT8 (worker) | **>= 95.0%** |
| **14 GB** | 14 GB | 3B-Instruct @ FP16 | 32B-Instruct @ INT3 (Q3_K) | MAS-14G-D: 1× 3B (orch) + 1× 3B (worker) + 1× 0.5B (verifier) FP16 | MAS-Q-14G: 1× 14B @ INT4 (orch) + 1× 7B @ INT4 (worker) + 1× 1.5B @ INT8 (verifier) | **>= 95.0%** |
| **16 GB** | 16 GB | 7B-Instruct @ FP16 | 14B-Instruct @ INT8 | MAS-16G-A: 1× 7B (orch) + 1× 0.5B (worker) FP16 | MAS-Q-16G: 1× 14B @ INT4 (orch) + 1× 14B @ INT4 (worker) | **>= 95.0%** |
| **18 GB** | 18 GB | 7B-Instruct @ FP16 | 32B-Instruct @ INT4-AWQ | MAS-18G-D: 1× 7B (orch) + 1× 0.5B + 1× 0.5B FP16 | MAS-Q-18G: 1× 14B @ INT8 (orch) + 1× 3B @ INT8 (worker) | **>= 95.0%** |
| **20 GB** | 20 GB | 7B-Instruct @ FP16 | 72B-Instruct @ 2-bit (AQLM) | MAS-20G-D: 1× 7B (orch) + 1× 1.5B + 1× 0.5B FP16 | MAS-Q-20G: 1× 14B @ INT8 (orch) + 1× 7B @ INT4 (worker) + 1× 1.5B @ INT8 (verifier) | **>= 95.0%** |
| **22 GB** | 22 GB | 7B-Instruct @ FP16 | 32B-Instruct @ INT5 (Q5_K) | MAS-22G-D: 1× 7B (orch) + 1× 3B + 1× 0.5B FP16 | MAS-Q-22G: 1× 14B @ INT8 (orch) + 1× 7B @ INT8 (worker) | **>= 95.0%** |
| **24 GB** | 24 GB | 7B-Instruct @ FP16 | 72B-Instruct @ 2.5-bit (AQLM) | MAS-24G-D: 1× 7B (orch) + 1× 3B + 1× 1.5B FP16 | MAS-Q-24G: 1× 32B @ INT4 (orch) + 1× 7B @ INT8 (worker) | **>= 95.0%** |
| **26 GB** | 26 GB | 7B-Instruct @ FP16 | 32B-Instruct @ INT6 (Q6_K) | MAS-26G-C: 1× 7B + 1× 3B + 1× 1.5B FP16 | MAS-Q-26G: 1× 32B @ INT4 (orch) + 1× 7B @ INT8 (worker) + 1× 1.5B @ INT8 (verifier) | **>= 95.0%** |
| **28 GB** | 28 GB | 7B-Instruct @ FP16 | 72B-Instruct @ 3-bit (Q3_K) | MAS-28G-C: 1× 7B + 1× 3B + 1× 3B FP16 | MAS-Q-28G: 1× 32B @ INT4 (orch) + 1× 7B @ INT8 (worker) + 1× 3B @ INT8 (verifier) | **>= 95.0%** |
| **30 GB** | 30 GB | 14B-Instruct @ FP16 | 14B-Instruct @ FP16 | MAS-30G-A: 1× 7B (orch) + 1× 7B (worker) FP16 | MAS-Q-30G: 1× 14B @ INT8 (orch) + 1× 14B @ INT8 (worker) | **>= 95.0%** |
| **32 GB** | 32 GB | 14B-Instruct @ FP16 | 72B-Instruct @ 3.5-bit (AWQ) | MAS-32G-A: 1× 14B (orch) + 1× 1.5B (worker) FP16 | MAS-Q-32G: 1× 32B @ INT4 (orch) + 1× 14B @ INT4 (worker) + 1× 7B @ INT4 (verifier) | **>= 95.0%** |

#### B.1 Single-Agent System (SAS) Configurations

For each tier, we test the **largest model that fits** at **every feasible quantization level** (FP16, INT8, INT4, 2-bit, 1-bit). This ensures no quantization level is hidden and we can plot the full quantization-accuracy degradation curve.

| Tier | VRAM | SAS-FP16 (Baseline) | SAS-INT8 | SAS-INT4 (AWQ) | SAS-2bit | SAS-1bit |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **4 GB** | 4 GB | 1.5B | 3B | 3B | 7B | 14B |
| **6 GB** | 6 GB | 1.5B | 3B | 7B | 14B | 32B |
| **8 GB** | 8 GB | 3B | 7B | 7B | 14B | 32B |
| **10 GB** | 10 GB | 3B | 7B | 14B | 32B | 32B |
| **12 GB** | 12 GB | 3B | 7B | 14B | 32B | 72B |
| **14 GB** | 14 GB | 3B | 7B | 14B | 32B | 72B |
| **16 GB** | 16 GB | 7B | 14B | 14B | 32B | 72B |
| **18 GB** | 18 GB | 7B | 14B | 14B | 32B | 72B |
| **20 GB** | 20 GB | 7B | 14B | 32B | 72B | 72B |
| **22 GB** | 22 GB | 7B | 14B | 32B | 72B | 72B |
| **24 GB** | 24 GB | 7B | 14B | 32B | 72B | 72B |
| **26 GB** | 26 GB | 7B | 14B | 32B | 72B | 72B |
| **28 GB** | 28 GB | 7B | 14B | 32B | 72B | 72B |
| **30 GB** | 30 GB | 14B | 14B | 32B | 72B | 72B |
| **32 GB** | 32 GB | 14B | 14B | 32B | 72B | 72B |

> *Each cell shows the **largest model** that fits at that quantization level. Smaller models at the same quant level may also be tested as additional data points. At every tier, all 5 quantization levels are tested to produce a complete accuracy-vs-compression curve.*

#### B.2 Multi-Agent System (MAS) Configurations

> **Constraint: All MAS agents run at FP16/BF16 (native precision). No quantization permitted in MAS.**

For each tier, we design **3–5 MAS topologies**. All agents must fit **simultaneously** in VRAM at FP16 precision.

**Tier 1 — 4 GB** (Hardware Budget: 4 GB | Target Resident VRAM: 3.8 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-4G-A | Hierarchical | 1× 0.5B (orch) + 2× 0.5B (workers) | ~3.0 GB | ~0.8 GB | ~3.8 GB | **95.0%** |
| MAS-4G-B | Peer Debate | 2× 0.5B + 1× 0.5B (judge) | ~3.0 GB | ~0.8 GB | ~3.8 GB | **95.0%** |
| MAS-4G-C | Sequential Pipeline | 3× 0.5B (Decompose → Execute → Verify) | ~3.0 GB | ~0.8 GB | ~3.8 GB | **95.0%** |
| MAS-4G-D | Hierarchical With Verifier | 1× 0.5B (orch) + 1× 0.5B (worker) + 1× 0.5B (verifier) | ~3.0 GB | ~0.8 GB | ~3.8 GB | **95.0%** |

**Tier 2 — 6 GB** (Hardware Budget: 6 GB | Target Resident VRAM: 5.7 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-6G-A | Hierarchical | 1× 1.5B (orch) + 2× 0.5B (workers) | ~5.0 GB | ~0.8 GB | ~5.8 GB | **96.7%** |
| MAS-6G-B | Peer Debate | 2× 0.5B + 1× 1.5B (judge) | ~5.0 GB | ~0.8 GB | ~5.8 GB | **96.7%** |
| MAS-6G-C | Sequential Pipeline | 1× 1.5B + 2× 0.5B | ~5.0 GB | ~0.8 GB | ~5.8 GB | **96.7%** |
| MAS-6G-D | Hierarchical With Verifier | 1× 1.5B (orch) + 1× 0.5B (worker) + 1× 0.5B (verifier) | ~5.0 GB | ~0.8 GB | ~5.8 GB | **96.7%** |

**Tier 3 — 8 GB** (Hardware Budget: 8 GB | Target Resident VRAM: 7.6 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-8G-A | Hierarchical | 1× 3B (orch) + 1× 0.5B (worker) | ~7.0 GB | ~0.8 GB | ~7.8 GB | **97.5%** |
| MAS-8G-B | Peer Debate | 2× 1.5B + 1× 0.5B (judge) | ~7.0 GB | ~0.8 GB | ~7.8 GB | **97.5%** |
| MAS-8G-C | Sequential Pipeline | 2× 1.5B + 1× 0.5B | ~7.0 GB | ~0.8 GB | ~7.8 GB | **97.5%** |
| MAS-8G-D | Hierarchical With Verifier | 1× 1.5B (orch) + 1× 1.5B (worker) + 1× 0.5B (verifier) | ~7.0 GB | ~0.8 GB | ~7.8 GB | **97.5%** |

**Tier 4 — 10 GB** (Hardware Budget: 10 GB | Target Resident VRAM: 9.5 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-10G-A | Hierarchical | 1× 3B (orch) + 1× 1.5B (worker) | ~9.0 GB | ~0.8 GB | ~9.8 GB | **98.0%** |
| MAS-10G-B | Peer Debate | 3× 1.5B | ~9.0 GB | ~0.8 GB | ~9.8 GB | **98.0%** |
| MAS-10G-C | Sequential Pipeline | 3× 1.5B (Decompose → Execute → Verify) | ~9.0 GB | ~0.8 GB | ~9.8 GB | **98.0%** |
| MAS-10G-D | Hierarchical With Verifier | 1× 3B (orch) + 2× 0.5B (workers) + 1× 0.5B (verifier) | ~9.0 GB | ~0.8 GB | ~9.8 GB | **98.0%** |

**Tier 5 — 12 GB** (Hardware Budget: 12 GB | Target Resident VRAM: 11.4 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-12G-A | Hierarchical | 1× 3B (orch) + 1× 1.5B (worker 1) + 2× 0.5B (workers) | ~11.0 GB | ~0.8 GB | ~11.8 GB | **98.3%** |
| MAS-12G-B | Peer Debate | 3× 1.5B + 1× 1.5B (judge) | ~12.0 GB | ~0.0 GB | ~12.0 GB | **100.0%** |
| MAS-12G-C | Sequential Pipeline | 1× 3B + 1× 1.5B + 2× 0.5B | ~11.0 GB | ~0.8 GB | ~11.8 GB | **98.3%** |
| MAS-12G-D | Hierarchical With Verifier | 1× 3B (orch) + 1× 1.5B (worker) + 1× 0.5B (verifier) | ~10.0 GB | ~1.5 GB | ~11.5 GB | **95.8%** |

**Tier 6 — 14 GB** (Hardware Budget: 14 GB | Target Resident VRAM: 13.3 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-14G-A | Hierarchical | 1× 3B (orch) + 1× 3B (worker) | ~12.0 GB | ~1.5 GB | ~13.5 GB | **96.4%** |
| MAS-14G-B | Peer Debate | 2× 3B + 1× 0.5B (judge) | ~13.0 GB | ~0.8 GB | ~13.8 GB | **98.6%** |
| MAS-14G-C | Sequential Pipeline | 1× 3B + 1× 3B + 1× 0.5B | ~13.0 GB | ~0.8 GB | ~13.8 GB | **98.6%** |
| MAS-14G-D | Hierarchical With Verifier | 1× 3B (orch) + 1× 3B (worker) + 1× 0.5B (verifier) | ~13.0 GB | ~0.8 GB | ~13.8 GB | **98.6%** |

**Tier 7 — 16 GB** (Hardware Budget: 16 GB | Target Resident VRAM: 15.2 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-16G-A | Hierarchical | 1× 7B (orch) + 1× 0.5B (worker) | ~15.0 GB | ~0.8 GB | ~15.8 GB | **98.8%** |
| MAS-16G-B | Peer Debate | 2× 3B + 1× 1.5B (judge) | ~15.0 GB | ~0.8 GB | ~15.8 GB | **98.8%** |
| MAS-16G-C | Sequential Pipeline | 2× 3B + 1× 1.5B | ~15.0 GB | ~0.8 GB | ~15.8 GB | **98.8%** |
| MAS-16G-D | Hierarchical With Verifier | 1× 3B (orch) + 1× 3B (worker) + 1× 1.5B (verifier) | ~15.0 GB | ~0.8 GB | ~15.8 GB | **98.8%** |

**Tier 8 — 18 GB** (Hardware Budget: 18 GB | Target Resident VRAM: 17.1 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-18G-A | Hierarchical | 1× 7B (orch) + 1× 1.5B (worker) + 1× 0.5B (worker) | ~18.0 GB | ~0.0 GB | ~18.0 GB | **100.0%** |
| MAS-18G-B | Peer Debate | 2× 3B + 1× 1.5B (critic) | ~15.0 GB | ~2.5 GB | ~17.5 GB | **97.2%** |
| MAS-18G-C | Sequential Pipeline | 1× 7B + 1× 1.5B + 1× 0.5B | ~18.0 GB | ~0.0 GB | ~18.0 GB | **100.0%** |
| MAS-18G-D | Hierarchical With Verifier | 1× 7B (orch) + 1× 0.5B (worker) + 1× 0.5B (verifier) | ~16.0 GB | ~1.5 GB | ~17.5 GB | **97.2%** |

**Tier 9 — 20 GB** (Hardware Budget: 20 GB | Target Resident VRAM: 19.0 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-20G-A | Hierarchical | 1× 7B (orch) + 1× 3B (worker) | ~20.0 GB | ~0.0 GB | ~20.0 GB | **100.0%** |
| MAS-20G-B | Peer Debate | 3× 3B | ~18.0 GB | ~1.5 GB | ~19.5 GB | **97.5%** |
| MAS-20G-C | Sequential Pipeline | 1× 7B + 1× 1.5B + 1× 0.5B | ~18.0 GB | ~1.5 GB | ~19.5 GB | **97.5%** |
| MAS-20G-D | Hierarchical With Verifier | 1× 7B (orch) + 1× 1.5B (worker) + 1× 0.5B (verifier) | ~18.5 GB | ~1.0 GB | ~19.5 GB | **97.5%** |

**Tier 10 — 22 GB** (Hardware Budget: 22 GB | Target Resident VRAM: 20.9 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-22G-A | Hierarchical | 1× 7B (orch) + 1× 3B (worker) | ~20.0 GB | ~1.5 GB | ~21.5 GB | **97.7%** |
| MAS-22G-B | Peer Debate | 3× 3B + 1× 1.5B (judge) | ~21.0 GB | ~0.8 GB | ~21.8 GB | **99.1%** |
| MAS-22G-C | Sequential Pipeline | 1× 7B + 1× 1.5B + 1× 1.5B | ~20.0 GB | ~1.5 GB | ~21.5 GB | **97.7%** |
| MAS-22G-D | Hierarchical With Verifier | 1× 7B (orch) + 1× 3B (worker) + 1× 0.5B (verifier) | ~21.0 GB | ~0.8 GB | ~21.8 GB | **99.1%** |

**Tier 11 — 24 GB** (Hardware Budget: 24 GB | Target Resident VRAM: 22.8 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-24G-A | Hierarchical | 1× 7B (orch) + 1× 3B (worker 1) + 1× 1.5B (worker 2) | ~23.0 GB | ~0.8 GB | ~23.8 GB | **99.2%** |
| MAS-24G-B | Peer Debate | 3× 3B + 1× 1.5B (judge) | ~21.0 GB | ~2.5 GB | ~23.5 GB | **97.9%** |
| MAS-24G-C | Sequential Pipeline | 1× 7B + 1× 3B + 1× 1.5B | ~23.0 GB | ~0.8 GB | ~23.8 GB | **99.2%** |
| MAS-24G-D | Hierarchical With Verifier | 1× 7B (orch) + 1× 3B (worker) + 1× 1.5B (verifier) | ~23.0 GB | ~0.8 GB | ~23.8 GB | **99.2%** |

**Tier 12 — 26 GB** (Hardware Budget: 26 GB | Target Resident VRAM: 24.7 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-26G-A | Hierarchical | 1× 7B (orch) + 1× 3B (worker 1) + 1× 3B (worker 2) | ~26.0 GB | ~0.0 GB | ~26.0 GB | **100.0%** |
| MAS-26G-B | Peer Debate | 3× 3B + 1× 3B (judge) | ~24.0 GB | ~1.5 GB | ~25.5 GB | **98.1%** |
| MAS-26G-C | Sequential Pipeline | 1× 7B + 1× 3B + 1× 1.5B | ~23.0 GB | ~2.5 GB | ~25.5 GB | **98.1%** |
| MAS-26G-D | Hierarchical With Verifier | 1× 7B (orch) + 1× 3B (worker) + 1× 1.5B (verifier) | ~23.0 GB | ~2.5 GB | ~25.5 GB | **98.1%** |

**Tier 13 — 28 GB** (Hardware Budget: 28 GB | Target Resident VRAM: 26.6 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-28G-A | Hierarchical | 1× 7B (orch) + 1× 3B (worker 1) + 1× 3B (worker 2) | ~26.0 GB | ~1.5 GB | ~27.5 GB | **98.2%** |
| MAS-28G-B | Peer Debate | 2× 7B | ~28.0 GB | ~0.0 GB | ~28.0 GB | **100.0%** |
| MAS-28G-C | Sequential Pipeline | 1× 7B + 1× 3B + 1× 3B | ~26.0 GB | ~1.5 GB | ~27.5 GB | **98.2%** |
| MAS-28G-D | Hierarchical With Verifier | 1× 7B (orch) + 1× 3B (worker) + 1× 3B (verifier) | ~26.0 GB | ~1.5 GB | ~27.5 GB | **98.2%** |

**Tier 14 — 30 GB** (Hardware Budget: 30 GB | Target Resident VRAM: 28.5 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-30G-A | Hierarchical | 1× 7B (orch) + 1× 7B (worker) | ~28.0 GB | ~1.5 GB | ~29.5 GB | **98.3%** |
| MAS-30G-B | Peer Debate | 2× 7B | ~28.0 GB | ~1.5 GB | ~29.5 GB | **98.3%** |
| MAS-30G-C | Sequential Pipeline | 1× 7B + 1× 3B + 1× 3B | ~26.0 GB | ~3.5 GB | ~29.5 GB | **98.3%** |
| MAS-30G-D | Hierarchical With Verifier | 1× 7B (orch) + 1× 7B (worker) + 1× 0.5B (verifier) | ~29.0 GB | ~0.5 GB | ~29.5 GB | **98.3%** |

**Tier 15 — 32 GB** (Hardware Budget: 32 GB | Target Resident VRAM: 30.4 GB [95%]):

| Config | Topology | Agent Layout (all FP16) | Total Weight | Active KV-Cache | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MAS-32G-A | Hierarchical | 1× 14B (orch) + 1× 1.5B (worker) | ~31.0 GB | ~0.8 GB | ~31.8 GB | **99.4%** |
| MAS-32G-B | Peer Debate | 2× 7B + 1× 0.5B (judge) | ~29.0 GB | ~2.0 GB | ~31.0 GB | **96.9%** |
| MAS-32G-C | Sequential Pipeline | 1× 7B + 1× 7B + 1× 0.5B | ~29.0 GB | ~2.0 GB | ~31.0 GB | **96.9%** |
| MAS-32G-D | Hierarchical With Verifier | 1× 7B (orch) + 1× 7B (worker) + 1× 0.5B (verifier) | ~29.0 GB | ~2.0 GB | ~31.0 GB | **96.9%** |

*(All MAS models use **Qwen 2.5** at **FP16/BF16 native precision** — no quantization. Alternative runs with **Llama 3.1 / 3.2** may be conducted at key tiers for generalizability analysis.)*

### C. MAS Topologies Under Budget
1. **Hierarchical (Orchestrator-Worker):** A larger orchestrator delegates subtasks to specialized smaller workers. Inspired by MetaGPT (Hong et al., ICLR 2024) and Żywot et al. (2026). Allocates 40–60% of VRAM to the orchestrator.
2. **Peer Review / Debate (Reflection):** Equal-sized or near-equal small models cross-verify and debate answers. Protocol derived from ChatEval (Chan et al., ICLR 2024) and ReConcile (Chen et al., ACL 2024).
3. **Sequential Pipeline (Decompose $\to$ Execute $\to$ Verify):** Dedicated modular sub-agents handling stages sequentially. Based on ChatDev's (Qian et al., ACL 2024) conversational chain architecture.
4. **AHDS — Adaptive Hierarchical with Dynamic Pruning & Structured Communication:** Our proposed "best" MAS architecture that systematically addresses 7 documented failure modes of standard MAS topologies. *(See Section 3E below.)*

### E. AHDS: Proposed Optimal MAS Architecture

The standard MAS topologies (Hierarchical, Debate, Pipeline) each suffer from well-documented failure modes identified in our literature review. We propose **AHDS (Adaptive Hierarchical with Dynamic Pruning & Structured Communication)** — a composite architecture designed to address all 7 problems simultaneously.

#### E.1 Documented MAS Failure Modes

| # | Problem | Source | Impact Under Memory Constraint |
| :-- | :--- | :--- | :--- |
| P1 | **Inter-agent context decay** (Data Processing Inequality) | Tran & Kiela (2026) | Worse at low memory — smaller agents have shorter contexts, increasing information loss per handoff |
| P2 | **Token overhead explosion** | Wang et al. (EMNLP 2024) | MAS debate/reflection can consume 3–10× more tokens than SAS, eating KV-cache VRAM |
| P3 | **Peer cascade / hallucination amplification** | ChatEval (ICLR 2024), MAST (Cemri et al., 2025) | Two weak agents can mutually reinforce errors, especially with sub-3B models |
| P4 | **Orchestrator bottleneck** | MetaGPT (ICLR 2024), Żywot et al. (2026) | If the orchestrator is too small, it fails at decomposition; if too large, workers starve for VRAM |
| P5 | **Latency compounding** | ChatDev (ACL 2024) | Sequential chains multiply wall-clock time, unacceptable in interactive settings |
| P6 | **KV-cache fragmentation** | vLLM / PagedAttention (SOSP 2023) | Multiple concurrent models create fragmented memory pools without paged management |
| P7 | **No dynamic adaptation** | DyLAN (ICLR 2024) | Static agent topologies waste resources on easy tasks that a single agent could solve |

#### E.2 AHDS Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                       AHDS Architecture                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────┐                          │
│  │      ORCHESTRATOR (Largest Model)     │  ← 40–60% of VRAM      │
│  │  - Task analysis & difficulty scoring │                          │
│  │  - Structured decomposition (JSON)    │                          │
│  │  - Confidence-gated dispatch (τ)      │                          │
│  │  - Self-solve if confidence ≥ τ       │                          │
│  └──────────┬───────────────────────────┘                          │
│             │ (dispatch only if confidence < τ)                    │
│     ┌───────┼───────┐                                              │
│     ▼       ▼       ▼                                              │
│  ┌──────┐┌──────┐┌──────┐                                          │
│  │ W₁   ││ W₂   ││ W₃   │  ← Dynamically activated workers       │
│  │Reason││Tool  ││Verify│     (only instantiated when needed)      │
│  └──┬───┘└──┬───┘└──┬───┘                                          │
│     └───────┼───────┘                                              │
│             ▼                                                      │
│  ┌──────────────────────────────────┐                              │
│  │     STRUCTURED AGGREGATOR        │                              │
│  │  (JSON schema, not free-form NL) │                              │
│  │  + Consistency verification       │                              │
│  └──────────────────────────────────┘                              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

#### E.3 Design Principles & Problem–Solution Mapping

| Principle | Solves | Mechanism |
| :--- | :--- | :--- |
| **Asymmetric VRAM allocation** | P4 | Allocate 40–60% of VRAM to orchestrator; remainder split among workers. Non-linear gains per Żywot et al. |
| **Structured communication (JSON schemas)** | P1, P2 | Replace natural language chatter with MetaGPT-style structured schemas. ~60% fewer tokens per handoff. |
| **Confidence-gated dispatch** | P7, P3 | Orchestrator attempts self-solve first. Only dispatches to workers if self-assessed confidence $< \tau$. Avoids unnecessary overhead on easy tasks. |
| **Dedicated verifier agent** | P3 | A small, cheap verification agent checks worker outputs for self-consistency before returning to orchestrator. |
| **PagedAttention KV-cache sharing** | P6 | Uses vLLM's PagedAttention to share prefix KV-cache across agents, reducing redundant allocation by ~40%. |
| **Early termination & token budgets** | P5, P2 | Workers have strict per-turn token budgets. Consensus detection halts debate early (ReConcile protocol). |

#### E.4 Per-Tier AHDS Instantiation

| Tier | Orchestrator (FP16) | Workers (FP16) | Verifier (FP16) | Strategy | Total Weight | Active KV | Total Resident | VRAM Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **4 GB** | 0.5B | 1× 0.5B | 1× 0.5B | 3-agent, full AHDS | ~3.0 GB | ~0.8 GB | ~3.8 GB | **95.0%** |
| **6 GB** | 1.5B | 1× 0.5B | 1× 0.5B | 3-agent, full AHDS | ~5.0 GB | ~0.8 GB | ~5.8 GB | **96.7%** |
| **8 GB** | 1.5B | 1× 1.5B | 1× 0.5B | 3-agent, full AHDS | ~7.0 GB | ~0.8 GB | ~7.8 GB | **97.5%** |
| **10 GB** | 3B | 1× 1.5B | — (orch self-verifies) | 2-agent, confidence-gated (orch self-verifies) | ~9.0 GB | ~0.8 GB | ~9.8 GB | **98.0%** |
| **12 GB** | 3B | 1× 1.5B | 1× 0.5B | 3-agent, full AHDS | ~10.0 GB | ~1.5 GB | ~11.5 GB | **95.8%** |
| **14 GB** | 3B | 1× 3B | 1× 0.5B | 3-agent, full AHDS | ~13.0 GB | ~0.8 GB | ~13.8 GB | **98.6%** |
| **16 GB** | 3B | 1× 3B | 1× 1.5B | 3-agent, full AHDS | ~15.0 GB | ~0.8 GB | ~15.8 GB | **98.8%** |
| **18 GB** | 7B | 1× 0.5B | 1× 0.5B | 3-agent, full AHDS | ~16.0 GB | ~1.5 GB | ~17.5 GB | **97.2%** |
| **20 GB** | 7B | 1× 1.5B | 1× 0.5B | 3-agent, full AHDS | ~18.5 GB | ~1.0 GB | ~19.5 GB | **97.5%** |
| **22 GB** | 7B | 1× 3B | 1× 0.5B | 3-agent, full AHDS | ~21.0 GB | ~0.8 GB | ~21.8 GB | **99.1%** |
| **24 GB** | 7B | 1× 3B | 1× 1.5B | 3-agent, full AHDS | ~23.0 GB | ~0.8 GB | ~23.8 GB | **99.2%** |
| **26 GB** | 7B | 1× 3B | 1× 1.5B | 3-agent, full AHDS | ~23.0 GB | ~2.5 GB | ~25.5 GB | **98.1%** |
| **28 GB** | 7B | 1× 3B | 1× 3B | 3-agent, full AHDS | ~26.0 GB | ~1.5 GB | ~27.5 GB | **98.2%** |
| **30 GB** | 7B | 1× 7B | 1× 0.5B | 3-agent, full AHDS | ~29.0 GB | ~0.5 GB | ~29.5 GB | **98.3%** |
| **32 GB** | 7B | 1× 7B | 1× 0.5B | 3-agent, full AHDS | ~29.0 GB | ~2.0 GB | ~31.0 GB | **96.9%** |

> *All AHDS agents run at FP16/BF16 native precision — no quantization. The orchestrator receives asymmetric VRAM allocation (40–60% of the budget).*

### D. Minimal Dual-Benchmark Design (Controlled Task Moderator)

A central strategic insight from our literature review is that foundational papers arrived at opposite conclusions because they tested opposite ends of the task-type spectrum:
* **Tran & Kiela (2026)** evaluated multi-hop reasoning (FRAMES, MuSiQue) and showed single agents beat multi-agent systems because the **Data Processing Inequality (DPI)** causes information to dilute across agent communication handoffs.
* **Żywot et al. (2026)** ("Can Small Agent Collaboration Beat a Single Big LLM?") evaluated **GAIA** and showed that small collaborative agents with tools beat a large monolithic model because **role specialization and tool interfaces** let small models conquer multi-step workflows.

Narrowing to multi-hop reasoning alone would simply confirm Tran & Kiela's findings under a different budget axis. Instead, we operationalize task type as an independent controlled variable through a **Minimal Dual-Benchmark Design**:

1. **Anchor 1: Tool-Intensive Slice (GAIA Subset — Primary Testing Ground):**
   - *Dataset:* 100-question curated subset of GAIA (50 Level 1 + 50 Level 2 tasks).
   - *Config:* [`configs/benchmarks/gaia_tool_slice.yaml`](file:///d:/project-agere/configs/benchmarks/gaia_tool_slice.yaml).
   - *Standardized Tools:* Python code sandbox, web search (cached/Serp), and file inspector (JSON, CSV, PDF) provided equally to both SAS and MAS.
   - *Target Hypothesis:* **Role Specialization Buffering ($\Delta_{\text{interaction}} > 0$)**. Tests whether narrow sub-agent roles collapse active token manifolds, protecting quantized sub-agents (Cell D) from precision loss.
   - *Priority:* Top experimental priority (preserves our base paper's domain and novel interaction findings).

2. **Anchor 2: Multi-Hop Reasoning Slice (MuSiQue / FRAMES Subset — Calibration & Sanity Check):**
   - *Dataset:* 150-question curated subset of MuSiQue / FRAMES (50 2-hop + 50 3-hop + 50 4-hop questions).
   - *Config:* [`configs/benchmarks/musique_reasoning_slice.yaml`](file:///d:/project-agere/configs/benchmarks/musique_reasoning_slice.yaml).
   - *Environment:* Closed-book reasoning with standardized Chain-of-Thought prompting (no tools).
   - *Target Hypothesis:* **Compounding Noise / Double Penalty ($\Delta_{\text{interaction}} < 0$)**. Tests whether quantization errors compound across sequential inter-agent handoffs under DPI.
   - *Strategic Function:* Provides a direct calibration anchor against Tran & Kiela's published baselines to verify setup normality before interpreting novel factorial cells.

*(Optional secondary probe for symbolic derivation: MATH-500 / GPQA Diamond if compute budget permits).*

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


### 5. Two-Way Factorial ANOVA & The Interaction Effect ($\Delta_{\text{interaction}}$)

Because our experimental matrix forms a balanced $2 \times 2$ factorial design along the factors of **Architecture** ($i \in \{\text{SAS}, \text{MAS}\}$) and **Precision** ($j \in \{\text{Full-Precision (FP16)}, \text{Quantized}\}$), we analyze task performance using a two-factor linear model:

$$y_{ijk} = \mu + \alpha_i + \beta_j + (\alpha\beta)_{ij} + \epsilon_{ijk}$$

where:
- $\mu$ is the grand mean benchmark accuracy across all conditions.
- $\alpha_i$ is the main effect of **Architecture** (Single-Agent vs. Multi-Agent Orchestration).
- $\beta_j$ is the main effect of **Compression** (Native FP16 vs. Quantized Scaling).
- $(\alpha\beta)_{ij}$ is the **Interaction Effect**, quantifying whether the performance impact of quantization is modulated by the multi-agent architecture.
- $\epsilon_{ijk} \sim \mathcal{N}(0, \sigma^2)$ represents random residual variance across $K$ evaluation trials/seeds.

#### Statistical Hypothesis Testing on the Interaction:
- **Null Hypothesis ($H_0$):** $(\alpha\beta)_{ij} = 0$. The effects of architecture and quantization are strictly additive and independent. Quantization degrades multi-agent teams by the exact same margin as single agents.
- **Alternative Hypothesis 1 ($H_{1,\text{double}}$):** $(\alpha\beta)_{\text{MAS},\text{Quant}} < 0$. Quantization noise compounds super-additively across agent communication hops (the multi-agent "double penalty" / $q_s$ inequality).
- **Alternative Hypothesis 2 ($H_{1,\text{buffer}}$):** $(\alpha\beta)_{\text{MAS},\text{Quant}} > 0$. Role specialization buffers against quantization noise, making multi-agent systems more noise-resilient than single-agent generalists.

We report the ANOVA $F$-statistic and associated $p$-value for the interaction term, complemented by non-parametric paired bootstrap resampling ($B = 10,000$) on the empirical difference-in-differences estimator:

$$\widehat{\Delta}_{\text{interaction}} = (\bar{y}_{D} - \bar{y}_{C}) - (\bar{y}_{B} - \bar{y}_{A})$$

