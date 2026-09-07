# Master Literature Review & Research Synthesis

> **Core Research Question:**  
> *Under a fixed resident VRAM memory budget $M$, can a Multi-Agent System (MAS) composed of smaller, high-precision language models outperform a Single-Agent System (SAS) utilizing a larger, aggressively quantized language model?*

This folder contains a complete, in-depth academic literature review of **35 primary research papers** published between **2024 and 2026** (excluding all surveys, SLRs, and informal benchmarks). Every paper is analyzed across its problem statement, methodology, theoretical novelty, empirical findings, critical limitations, and exact role in our research study.

---

## Structure of the Literature Review

The review is organized into five thematic documents plus this master synthesis:

| Document | Covered Papers | Core Themes |
| :--- | :--- | :--- |
| [**`01_mas_vs_sas_collaboration.md`**](./01_mas_vs_sas_collaboration.md) | **01 – 08** | Core SAS vs. MAS baselines (Tran & Kiela, Żywot et al.), agent scaling theory (Kim et al., Li et al.), and failure taxonomy (Cemri et al. MAST). |
| [**`02_mas_topologies_and_frameworks.md`**](./02_mas_topologies_and_frameworks.md) | **09 – 14** | Concrete multi-agent topologies: dynamic groups (AgentVerse), debate (ChatEval, ReConcile), hierarchical SOPs (MetaGPT), pipelines (ChatDev), and dynamic pruning (DyLAN). |
| [**`03_budget_and_memory_inference.md`**](./03_budget_and_memory_inference.md) | **15 – 21** | Budget-aware evaluation (Wang et al. EMNLP), hardware VRAM profiling (Bench360), inference compute scaling (Monkeys), tool budgets, MoE capacity penalty ($q_s$ inequality), and vLLM PagedAttention. |
| [**`04_quantization_and_ondevice.md`**](./04_quantization_and_ondevice.md) | **22 – 30** | Quantization algorithms for large SAS models (AWQ, QuaRot, SpinQuant, AQLM, AutoRound), sub-billion on-device design (MobileLLM), ternary BitNet, and multi-agent KV sharing (SGLang). |
| [**`05_benchmarks_and_evaluation.md`**](./05_benchmarks_and_evaluation.md) | **31 – 35** | Standardized evaluation infrastructure: tool-use (GAIA, BFCL), multi-step engineering (SWE-bench), multi-hop reasoning (FRAMES), and parametric world knowledge (MMLU-Pro). |

---

## The Core Scientific Tension & Research Gap

Prior literature on scaling agent systems and post-training model compression has operated in isolated silos:

```
                  ┌────────────────────────────────────────┐
                  │    The Core Architectural Dilemma      │
                  │        Fixed VRAM Budget (M)           │
                  └──────────────────┬─────────────────────┘
                                     │
            ┌────────────────────────┴────────────────────────┐
            ▼                                                 ▼
┌───────────────────────┐                         ┌───────────────────────┐
│  Single-Agent (SAS)   │                         │   Multi-Agent (MAS)   │
│  Large + Quantized    │                         │  Multiple Small Models│
├───────────────────────┤                         ├───────────────────────┤
│ • 1× 32B @ INT4/AWQ   │                         │ • 2× 8B @ INT8 or     │
│ • Deeper pre-trained  │                         │   1× 8B + 2× 3B FP16  │
│   reasoning & world   │                         │ • Intact precision    │
│   knowledge           │                         │ • Specialization      │
│ • Suffers from        │                         │ • Context collapse,   │
│   quantization noise  │                         │   coordination drift  │
│   on sensitive heads  │                         │   & inter-agent token │
│                       │                         │   inflation           │
└───────────┬───────────┘                         └───────────┬───────────┘
            │                                                 │
            └────────────────────────┬────────────────────────┘
                                     ▼
                  ┌─────────────────────────────────────┐
                  │      Moderator: Task Complexity     │
                  │  • Tool-Use / Step Decomposition    │
                  │    --> MAS Favored?                 │
                  │  • Multi-Hop / Knowledge-Dense      │
                  │    --> SAS Favored?                 │
                  └─────────────────────────────────────┘
```

1. **The Flaw in Prior SAS-vs-MAS Work (e.g., Tran & Kiela 2026):**  
   Equalized computational thinking token budgets while holding model size constant. This treats compute as a soft operational cost, ignoring the physical hardware reality that **VRAM is a hard ceiling**. In edge or single-GPU deployments, exceeding VRAM causes an immediate Out-of-Memory (OOM) crash.
2. **The Flaw in Prior Quantization Work (e.g., AWQ, QuaRot, Bench360):**  
   Quantization benchmarks evaluate models as monolithic silos. They establish that a 4-bit 32B model beats a 4-bit 14B model, but never ask whether the 16 GB VRAM used by that 32B model would be better spent running an orchestrated team of smaller, higher-precision models with specialized tools.
3. **The Micro-to-Macro Analogy ($q_s$ Inequality):**  
   At the internal architecture level, Chen et al. (2026) proved that splitting parameter capacity into routed sub-networks (MoEs) incurs a double penalty under total parameter parity compared to dense models. Our research investigates whether this same degradation occurs at the coarser, macro-orchestration level of multi-agent systems.

---

## The Filtered 15-Paper Core Bibliography

To focus your manuscript for top-tier conference submission, here is the recommended **15-paper core subset**, mapped to their precise sections in your research paper:

| # | Selected Paper | Venue | Exact Function in Your Paper |
| :---: | :--- | :--- | :--- |
| **1** | **Tran & Kiela (2026)** | arXiv:2604.02460 | **Primary Base Paper:** The direct structural template our work modifies by swapping token budgets for VRAM budgets. |
| **2** | **Żywot, Chen, & de Rijke (2026)** | arXiv:2601.11327 | **Secondary Base Paper (Tool-Use):** Justification for the hypothesis that small agent teams with tools beat monolithic models. |
| **3** | **Kim et al. (2025/2026)** | arXiv:2512.08296 | **Theoretical Scaling Foundation:** Predictive scaling laws explaining coordination bottlenecks across topologies. |
| **4** | **Wang et al. (MoA, 2024)** | arXiv:2406.04692 | **MAS Baseline 1:** Layered Mixture-of-Agents baseline representing multi-model collaborative generation. |
| **5** | **Hong et al. (MetaGPT, 2024)** | ICLR 2024 (Oral) | **MAS Baseline 2:** Canonical Hierarchical Orchestrator-Worker architecture using structured SOP schemas. |
| **6** | **Wang et al. (ACL 2024)** | ACL 2024 | **Single-Agent Prompting Baseline:** Guarantees our single quantized model is benchmarked with fair, state-of-the-art prompting. |
| **7** | **Cemri et al. (MAST, 2025)** | arXiv:2503.13657 | **Error Analysis Framework:** Taxonomy used in the Discussion to classify multi-agent failure modes and context collapse. |
| **8** | **Wang et al. (EMNLP 2024)** | EMNLP 2024 | **Budget-Aware Methodology:** The core methodological precedent for holding resource consumption constant during evaluation. |
| **9** | **Lin et al. (Bench360, 2025)** | arXiv:2511.16682 | **Hardware Profiling Standard:** Protocol for measuring and reporting resident VRAM, latency, and throughput on consumer GPUs. |
| **10** | **Chen et al. ($q_s$ Inequality, 2026)** | arXiv:2603.08960 | **Theoretical Bridge:** Formal mathematics establishing capacity penalties when dividing stored weights into sub-units. |
| **11** | **Lin et al. (AWQ, 2024)** | MLSys 2024 (Best Paper) | **SAS Quantization Engine:** The primary 4-bit weight quantization method used to compress our large single models. |
| **12** | **Ashkboos et al. (QuaRot, 2024)** | NeurIPS 2024 | **Advanced Quantization Baseline:** End-to-end 4-bit weights + activations + KV-cache compression for extreme memory efficiency. |
| **13** | **Kwon et al. (vLLM, 2023)** | SOSP 2023 / MLSys | **Serving Infrastructure:** PagedAttention runtime ensuring multi-agent KV caches do not cause memory fragmentation. |
| **14** | **Mialon et al. (GAIA, 2024)** | ICLR 2024 | **Primary Benchmark (Tool-Use):** Real-world multi-step assistant tasks testing whether MAS tool specialization beats monolithic scale. |
| **15** | **Krishna et al. (FRAMES, 2024)** | EMNLP 2024 / arXiv | **Primary Benchmark (Reasoning):** High-hop reasoning benchmark directly replicating Tran & Kiela's evaluation suite. |

---

## Why the Remaining 20 Papers Were Filtered Out

When consolidating your bibliography, the remaining 20 papers serve as valuable supporting citations but are secondary to the core argument:

* **ChatDev (12), AgentVerse (09), ReConcile (14):** Functionally redundant with MetaGPT (11) and MoA (04); MetaGPT represents structured pipelines with higher citation prestige (ICLR Oral).
* **Li et al. (06) & Monkeys (17):** Focus on pure repeated sampling and voting rather than collaborative multi-agent orchestration.
* **Ke et al. (08) & Su et al. (18):** Benchmarking frameworks specifically for orchestration or API cost, superseded by Bench360 (16) and GAIA (31).
* **SpinQuant (24), AutoRound (26), QuIP# (29), AQLM (25):** Advanced quantization variations; keeping AWQ (22) and QuaRot (23) provides sufficient coverage of weight-only and end-to-end 4-bit compression.
* **BitNet b1.58 (28) & MobileLLM (27):** Require training from scratch; our experimental design uses pre-trained open-weight models.
* **SWE-bench (32) & BFCL (34):** Computationally heavy or narrow tool benchmarks; GAIA (31) and FRAMES (33) provide cleaner coverage of tools and multi-hop reasoning.
* **MMLU-Pro (35):** Closed-book multiple choice; secondary if your empirical focus is on agentic execution and multi-hop derivation.
* **SGLang (30) & Frugal-MoE (21):** Systems optimizations that can be cited in a single sentence alongside vLLM (20).

---

## Writing Guide: How to Frame This in Your Paper

### In Section 1: Introduction
> *"While recent work has vigorously debated whether Multi-Agent Systems (MAS) outperform Single-Agent Systems (SAS) [Wang et al., 2024; Tran & Kiela, 2026], existing comparisons have almost exclusively normalized compute along the axis of thinking token budgets or active FLOPs. However, in real-world on-device and local workstation deployments, computational cost is secondary to physical hardware boundaries: resident GPU memory (VRAM) is a hard ceiling that cannot be exceeded [Lin et al., 2025]. 
> 
> In this paper, we bridge this fundamental gap by investigating the trade-off between architectural distribution and parameter precision under a strict total resident VRAM budget $M$. Given a fixed memory allocation, a practitioner faces a critical design dilemma: should they deploy a Single-Agent System powered by a larger model compressed via post-training quantization [Lin et al., 2024; Ashkboos et al., 2024], or an orchestrated Multi-Agent System composed of smaller, higher-precision models with specialized division of labor [Hong et al., 2024; Zywot et al., 2026]? Drawing upon theoretical capacity penalties established in sparse MoE architectures [Chen et al., 2026], we hypothesize that..."*

### In Section 2: Related Work
> *"**Budget-Normalized Agent Evaluation:** Prior investigations into agentic scaling laws have demonstrated that complex multi-agent reasoning often gains an unfair advantage simply by consuming more inference tokens [Wang et al., 2024]. When tokens are strictly equalized, Tran & Kiela (2026) demonstrated that single agents consistently surpass multi-agent debate and ensemble configurations on multi-hop benchmarks [Krishna et al., 2024]. Concurrently, however, Zywot et al. (2026) demonstrated on GAIA [Mialon et al., 2024] that small models can decisively surpass monolithic models when augmented with external tools. We synthesize these diverging observations by recognizing that memory residency, rather than token generation, represents the decisive deployment bottleneck..."*
