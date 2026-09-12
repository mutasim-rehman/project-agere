# Research Papers Dictionary & Context Guide

> **Overarching Research Question:**  
> *Given a fixed, non-negotiable resident GPU memory budget (VRAM $M$), do the choice of architecture (Single-Agent monolithic vs. Multi-Agent modular orchestration) and the choice of compression strategy (native FP16 vs. quantized scaling) act independently, or do they interact — such that the optimal compression strategy depends on which architecture is chosen, and vice versa?*
> 
> *Examined via a 2×2 Factorial Design across 15 memory tiers (4 GB to 32 GB): Cell A (SAS-FP16), Cell B (SAS-Quant), Cell C (MAS-FP16), and Cell D (MAS-Quant).*

This dictionary catalogs all **35 primary research papers** stored in [`sources/`](./). For each paper, it defines **what the paper is** and **how it directly connects to our research** in concise, one-sentence explanations.

---

## Table of Contents
1. [Pillar 1: Multi-Agent Systems vs. Single-Agent Baselines (01–14)](#pillar-1-multi-agent-systems-vs-single-agent-baselines)
2. [Pillar 2: Budget-Constrained & Memory-Aware Inference (15–21)](#pillar-2-budget-constrained--memory-aware-inference)
3. [Pillar 3: Quantization, Memory Scaling & On-Device Models (22–30)](#pillar-3-quantization-memory-scaling--on-device-models)
4. [Pillar 4: Benchmarks & Empirical Evaluation Infrastructure (31–35)](#pillar-4-benchmarks--empirical-evaluation-infrastructure)
5. [Quick Reference Matrix](#quick-reference-matrix)

---

## Pillar 1: Multi-Agent Systems vs. Single-Agent Baselines

### 01. Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets
* **File:** [`01_Tran_2026_Single_Agent_LLMs_Outperform_Multi_Agent.pdf`](./01_Tran_2026_Single_Agent_LLMs_Outperform_Multi_Agent.pdf)  
* **Authors & Venue:** Dat Tran, Douwe Kiela (Stanford University) — *arXiv:2604.02460 (April 2026)*  
* **Role:** **Primary Base Paper Candidate** (Multi-Hop Reasoning Focus)  
* **What it is:** Proves that single-agent LLMs consistently match or outperform multi-agent architectures (debate, ensemble, sequential) when computational test-time thinking token budgets are held equal.  
* **How it relates to our research:** Serves as our primary structural template, where we adopt their comparative agent topologies but replace their equalized token budget with a physical resident VRAM budget ($M$) and introduce quantized SAS baselines.

---

### 02. Can Small Agent Collaboration Beat a Single Big LLM?
* **File:** [`02_Zywot_2026_Can_Small_Agent_Collaboration_Beat_Single_Big_LLM.pdf`](./02_Zywot_2026_Can_Small_Agent_Collaboration_Beat_Single_Big_LLM.pdf)  
* **Authors & Venue:** Agata Zywot, Xinyi Chen, Maarten de Rijke (University of Amsterdam) — *arXiv:2601.11327 (Jan 2026)*  
* **Role:** **Primary Base Paper Candidate** (Tool-Use & Agentic Focus)  
* **What it is:** Demonstrates that small models (4B–32B Qwen3) equipped with tool-use and collaborative orchestration can outperform significantly larger monolithic models that lack tools on the GAIA benchmark.  
* **How it relates to our research:** Serves as our alternative base paper and provides the small-agent tool-orchestration architecture to test whether multi-agent systems win specifically on tool-augmented tasks under equal memory.

---

### 03. Towards a Science of Scaling Agent Systems
* **File:** [`03_Kim_2025_Towards_a_Science_of_Scaling_Agent_Systems.pdf`](./03_Kim_2025_Towards_a_Science_of_Scaling_Agent_Systems.pdf)  
* **Authors & Venue:** Kim et al. (Google Research, Google DeepMind, MIT) — *arXiv:2512.08296 (Dec 2025 / 2026)*  
* **Role:** Theoretical Agent Scaling Laws & Topology Selection  
* **What it is:** Establishes formal empirical scaling laws and predictive models showing when adding agents benefits vs. degrades performance based on coordination topology and task parallelism.  
* **How it relates to our research:** Provides the theoretical backing to explain why dividing a fixed memory budget among multiple small agents hits diminishing returns due to inter-agent communication overhead.

---

### 04. Mixture-of-Agents Enhances Large Language Model Capabilities
* **File:** [`04_Wang_2024_Mixture_of_Agents_Enhances_LLM.pdf`](./04_Wang_2024_Mixture_of_Agents_Enhances_LLM.pdf)  
* **Authors & Venue:** Junlin Wang et al. (Together AI, Duke, Stanford) — *arXiv:2406.04692 (June 2024)*  
* **Role:** Layered MAS Architecture Baseline  
* **What it is:** Proposes a feed-forward layered architecture where multiple agent models iteratively integrate and refine the collective outputs of the previous layer to beat frontier models.  
* **How it relates to our research:** Serves as a prominent multi-agent baseline topology to test whether layered multi-model collaboration remains advantageous when all sub-agents must fit within one GPU's VRAM.

---

### 05. Rethinking the Bounds of LLM Reasoning: Are Multi-Agent Discussions the Key?
* **File:** [`05_Wang_2024_Rethinking_Bounds_LLM_Reasoning_MultiAgent_Discussions.pdf`](./05_Wang_2024_Rethinking_Bounds_LLM_Reasoning_MultiAgent_Discussions.pdf)  
* **Authors & Venue:** Qineng Wang et al. — *ACL 2024 (Long Papers)*  
* **Role:** Single-Agent vs. Debate Baseline  
* **What it is:** Shows that a well-prompted single agent achieves reasoning performance equal to multi-agent debate systems, with debate only helping in zero-shot settings without demonstrations.  
* **How it relates to our research:** Establishes the rigorous single-agent prompting baseline needed to ensure our single quantized model is not artificially crippled during evaluation.

---

### 06. More Agents Is All You Need
* **File:** [`06_Li_2024_More_Agents_Is_All_You_Need.pdf`](./06_Li_2024_More_Agents_Is_All_You_Need.pdf)  
* **Authors & Venue:** Junyou Li et al. (Tencent) — *TMLR 2024 / arXiv:2402.05120*  
* **Role:** Sampling-and-Voting Ensemble Baseline  
* **What it is:** Discovers that scaling the number of instantiated agents via simple sampling-and-voting consistently improves performance across models, with gains scaling with task difficulty.  
* **How it relates to our research:** Represents the simplest peer-ensemble baseline to determine whether voting across small models outperforms a single large quantized model.

---

### 07. Why Do Multi-Agent LLM Systems Fail?
* **File:** [`07_Cemri_2025_Why_Do_Multi_Agent_LLM_Systems_Fail.pdf`](./07_Cemri_2025_Why_Do_Multi_Agent_LLM_Systems_Fail.pdf)  
* **Authors & Venue:** Mert Cemri et al. — *arXiv:2503.13657 (March 2025)*  
* **Role:** Multi-Agent Failure Mode Taxonomy (MAST)  
* **What it is:** Analyzes 1,600 interaction traces across 7 MAS frameworks to identify 14 failure modes, demonstrating how context collapse and cascading misunderstandings cripple multi-agent systems.  
* **How it relates to our research:** Provides the analytical lens and vocabulary to diagnose why smaller agents in our MAS configurations fail on multi-step reasoning tasks under memory constraints.

---

### 08. MAS-Orchestra: Benchmarking Holistic Multi-Agent Orchestration
* **File:** [`08_Ke_2026_MAS_Orchestra_Holistic_Multi_Agent_Orchestration.pdf`](./08_Ke_2026_MAS_Orchestra_Holistic_Multi_Agent_Orchestration.pdf)  
* **Authors & Venue:** Ke et al. — *arXiv:2601.14652 (Jan 2026)*  
* **Role:** Multi-Agent Orchestration Benchmark  
* **What it is:** Introduces an evaluation benchmark specifically designed to test dynamic role allocation, message routing, and coordination efficiency in multi-agent orchestration.  
* **How it relates to our research:** Informs how we design and quantify communication overhead and routing mechanics among our small sub-agents.

---

### 09. AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors
* **File:** [`09_Chen_2024_AgentVerse_Multi_Agent_Collaboration.pdf`](./09_Chen_2024_AgentVerse_Multi_Agent_Collaboration.pdf)  
* **Authors & Venue:** Weize Chen et al. (Tsinghua University) — *ICLR 2024*  
* **Role:** Multi-Agent Collaboration Framework  
* **What it is:** Introduces a modular multi-agent platform supporting autonomous dynamic group composition, debate, and problem-solving phases.  
* **How it relates to our research:** Provides the foundational software architecture and prompt templates for executing collaborative problem-solving across multiple small models.

---

### 10. ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate
* **File:** [`10_Chan_2024_ChatEval_Multi_Agent_Debate.pdf`](./10_Chan_2024_ChatEval_Multi_Agent_Debate.pdf)  
* **Authors & Venue:** Chi-Min Chan et al. — *ICLR 2024*  
* **Role:** Multi-Agent Debate Protocol  
* **What it is:** Develops a multi-agent debate framework where diverse referee agents critique each other's assessments to achieve reliable consensus evaluation.  
* **How it relates to our research:** Supplies the multi-round peer-debate protocol tested in our multi-agent debate configurations.

---

### 11. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework
* **File:** [`11_Hong_2024_MetaGPT_Multi_Agent_Collaborative_Framework.pdf`](./11_Hong_2024_MetaGPT_Multi_Agent_Collaborative_Framework.pdf)  
* **Authors & Venue:** Sirui Hong et al. — *ICLR 2024 (Oral)*  
* **Role:** SOP-Based Hierarchical Architecture  
* **What it is:** Encodes Standardized Operating Procedures (SOPs) into agent prompts to establish clear division of labor (Product Manager, Architect, Coder) and prevent cascading logic drift.  
* **How it relates to our research:** Provides the blueprint for our hierarchical MAS architecture, ensuring small sub-agents operate within strict, bounded roles.

---

### 12. ChatDev: Communicative Agents for Software Development
* **File:** [`12_Qian_2024_ChatDev_Communicative_Agents_Software_Development.pdf`](./12_Qian_2024_ChatDev_Communicative_Agents_Software_Development.pdf)  
* **Authors & Venue:** Chen Qian et al. (Tsinghua University) — *ACL 2024 (Long Papers)*  
* **Role:** Sequential Pipeline MAS Architecture  
* **What it is:** Implements a virtual software company where specialized LLM agents interact through a structured "chat chain" across design, coding, testing, and documentation stages.  
* **How it relates to our research:** Serves as the canonical sequential pipeline topology (planner $\to$ worker $\to$ verifier) tested against our single-agent baseline.

---

### 13. Dynamic LLM-Agent Network: An LLM-Agent Collaboration Framework with Dynamic Architecture (DyLAN)
* **File:** [`13_Liu_2024_Dynamic_LLM_Agent_Network_DyLAN.pdf`](./13_Liu_2024_Dynamic_LLM_Agent_Network_DyLAN.pdf)  
* **Authors & Venue:** Liu et al. — *ICLR 2024*  
* **Role:** Communication-Efficient Dynamic Agent Pruning  
* **What it is:** Proposes a dynamic multi-agent network that measures agent contribution in each round and deactivates low-performing agents to conserve compute.  
* **How it relates to our research:** Demonstrates how to minimize inter-agent token communication overhead so multi-agent systems do not waste VRAM on unnecessary context passing.

---

### 14. ReConcile: Round-Table Discussion Improves Reasoning via Consensus
* **File:** [`14_Chen_2024_ReConcile_Round_Table_Discussion.pdf`](./14_Chen_2024_ReConcile_Round_Table_Discussion.pdf)  
* **Authors & Venue:** Chen et al. — *ACL 2024*  
* **Role:** Multi-Model Round-Table Consensus  
* **What it is:** Introduces a round-table discussion protocol where multiple agents convince each other through multi-turn debate to reach a consensus on math and reasoning tasks.  
* **How it relates to our research:** Serves as a high-performing peer-debate baseline for our multi-hop reasoning evaluation suite.

---

## Pillar 2: Budget-Constrained & Memory-Aware Inference

### 15. Reasoning in Token Economies: Budget-Aware Evaluation of LLM Reasoning Strategies
* **File:** [`15_Wang_2024_Reasoning_in_Token_Economies_Budget_Aware.pdf`](./15_Wang_2024_Reasoning_in_Token_Economies_Budget_Aware.pdf)  
* **Authors & Venue:** Junlin Wang et al. — *EMNLP 2024 (Main Conference)*  
* **Role:** **Budget-Normalization Methodological Template**  
* **What it is:** Demonstrates that complex reasoning and agent strategies frequently look superior only because they consume more tokens, proving the necessity of budget-normalized evaluations.  
* **How it relates to our research:** Provides the methodological justification for our entire experimental design: holding resource constraints constant to uncover true architectural efficiency.

---

### 16. Bench360: Benchmarking Local LLM Inference from 360 Degrees
* **File:** [`16_Lin_2025_Bench360_Benchmarking_Local_LLM_Inference.pdf`](./16_Lin_2025_Bench360_Benchmarking_Local_LLM_Inference.pdf)  
* **Authors & Venue:** Lin et al. — *arXiv:2511.16682 (Late 2025)*  
* **Role:** **Replication Baseline (Cell B vs. Cell A) & VRAM Profiling Protocol**  
* **What it is:** A comprehensive benchmarking suite that evaluates local LLMs across resident VRAM usage, latency, throughput, energy consumption, and task accuracy.  
* **How it relates to our research:** Establishes the single-agent winner baseline (Cell B quantized beats Cell A unquantized) which we replicate as our internal control, while providing the profiling protocol for our 15 VRAM tiers (4 GB to 32 GB).

---

### 17. Large Language Monkeys: Scaling Inference Compute with Repeated Sampling
* **File:** [`17_Brown_2024_Large_Language_Monkeys_Scaling_Inference_Compute.pdf`](./17_Brown_2024_Large_Language_Monkeys_Scaling_Inference_Compute.pdf)  
* **Authors & Venue:** Bradley Brown et al. — *arXiv:2407.21787 (July 2024)*  
* **Role:** Inference-Time Compute Scaling Baseline  
* **What it is:** Shows that scaling coverage via repeated sampling on a single model often yields steeper performance improvements than complex prompting or multi-agent structures.  
* **How it relates to our research:** Acts as a strong single-agent baseline: testing whether repeated sampling on a large quantized model beats multi-agent coordination.

---

### 18. ToolOrchestra: Collaborative and Cost-Aware Tool Orchestration for Language Agents
* **File:** [`18_Su_2024_ToolOrchestra_Cost_Aware_Tool_Orchestration.pdf`](./18_Su_2024_ToolOrchestra_Cost_Aware_Tool_Orchestration.pdf)  
* **Authors & Venue:** Su et al. — *arXiv:2411.08573 (Nov 2024)*  
* **Role:** Cost-Constrained Multi-Agent Tool Orchestration  
* **What it is:** Optimizes multi-agent tool execution by balancing performance gains against latency and token costs under strict budgets.  
* **How it relates to our research:** Highlights how small agents in a collaborative setup must budget their tool invocations when operating under hardware resource limits.

---

### 19. The $q_s$ Inequality: Quantifying the Double Penalty of Mixture-of-Experts at Inference
* **File:** [`19_Chen_2026_The_qs_Inequality_MoE_Inference_Penalty.pdf`](./19_Chen_2026_The_qs_Inequality_MoE_Inference_Penalty.pdf)  
* **Authors & Venue:** Chen et al. — *arXiv:2603.08960 (March 2026)*  
* **Role:** **Theoretical Bridge for $\Delta_{\text{interaction}}$ (Double Penalty Hypothesis)**  
* **What it is:** Derives a mathematical quality-equivalence formula proving that distributing capacity into sub-networks incurs a memory and inference penalty compared to dense monolithic networks.  
* **How it relates to our research:** Provides the theoretical foundation for our Compounding Error / Double Penalty Hypothesis ($\Delta_{\text{interaction}} < 0$) in Cell D (MAS-Quant): testing whether quantizing sub-agents and routing across natural language boundaries multiplies noise across stages, mirroring the $q_s$ MoE capacity penalty at the macro-orchestration layer.

---

### 20. Efficient Memory Management for Large Language Model Serving with PagedAttention (vLLM)
* **File:** [`20_Kwon_2023_vLLM_PagedAttention_Memory_Management.pdf`](./20_Kwon_2023_vLLM_PagedAttention_Memory_Management.pdf)  
* **Authors & Venue:** Woosuk Kwon et al. (UC Berkeley) — *SOSP 2023 / MLSys*  
* **Role:** Serving Infrastructure & KV-Cache Management  
* **What it is:** Introduces PagedAttention to eliminate memory fragmentation in the KV-cache, allowing near-zero memory waste during concurrent LLM inference.  
* **How it relates to our research:** Underpins our inference runtime to ensure concurrent multi-agent models do not crash from KV-cache memory spikes inside fixed VRAM budgets.

---

### 21. Frugal-MoE: Cost-Effective Mixture of Experts via Activation-Guided Routing
* **File:** [`21_Yao_2024_Frugal_MoE_Cost_Effective_MoE_Routing.pdf`](./21_Yao_2024_Frugal_MoE_Cost_Effective_MoE_Routing.pdf)  
* **Authors & Venue:** Yao et al. — *ACL 2024 (Findings)*  
* **Role:** Dynamic Capacity-Budgeted Routing  
* **What it is:** Selectively activates sub-networks based on query complexity to reduce memory and computation during inference.  
* **How it relates to our research:** Demonstrates how adaptive capacity allocation saves resources, contrasting with static multi-agent allocation under memory constraints.

---

## Pillar 3: Quantization, Memory Scaling & On-Device Models

### 22. AWQ: Activation-aware Weight Quantization for On-Device LLM Compression and Acceleration
* **File:** [`22_Lin_2024_AWQ_Activation_Aware_Weight_Quantization.pdf`](./22_Lin_2024_AWQ_Activation_Aware_Weight_Quantization.pdf)  
* **Authors & Venue:** Ji Lin, Song Han et al. (MIT HAN Lab) — *MLSys 2024 (Best Paper Award)*  
* **Role:** **Quantization Engine for Cell B (SAS-Quant) & Cell D (MAS-Quant)**  
* **What it is:** Protects salient weight channels by observing activation distributions, delivering accurate 4-bit weight-only quantization without backpropagation.  
* **How it relates to our research:** Serves as the primary quantization technique used to compress models in both Cell B (large monolithic generalist) and Cell D (large sub-agents in an orchestrated MAS) across our 15 VRAM tiers.

---

### 23. QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs
* **File:** [`23_Ashkboos_2024_QuaRot_Outlier_Free_4Bit_Inference.pdf`](./23_Ashkboos_2024_QuaRot_Outlier_Free_4Bit_Inference.pdf)  
* **Authors & Venue:** Saleh Ashkboos et al. (ETH Zurich) — *NeurIPS 2024*  
* **Role:** End-to-End 4-Bit Weight + KV-Cache Quantization  
* **What it is:** Uses randomized Hadamard rotations to eliminate activation outliers, achieving end-to-end 4-bit inference across weights, activations, and the KV cache with 99% accuracy retention.  
* **How it relates to our research:** Enables our single-agent baseline to compress both weights and KV cache to 4 bits, maximizing the parameter size that fits within a strict memory ceiling.

---

### 24. SpinQuant: LLM Quantization with Learned Rotations
* **File:** [`24_Liu_2025_SpinQuant_LLM_Quantization_Learned_Rotations.pdf`](./24_Liu_2025_SpinQuant_LLM_Quantization_Learned_Rotations.pdf)  
* **Authors & Venue:** Zechun Liu et al. (Meta) — *ICLR 2025*  
* **Role:** SOTA Learned Rotation Quantization  
* **What it is:** Optimizes rotation matrices to eliminate outliers in weights and activations, outperforming QuaRot and narrowing the 4-bit accuracy gap with FP16 models.  
* **How it relates to our research:** Provides a state-of-the-art quantized baseline to ensure our single-agent arm is not penalized by sub-optimal quantization artifacts.

---

### 25. AQLM: Extreme Compression of Large Language Models via Additive Quantization
* **File:** [`25_Egiazarian_2024_AQLM_Extreme_Compression_Additive_Quantization.pdf`](./25_Egiazarian_2024_AQLM_Extreme_Compression_Additive_Quantization.pdf)  
* **Authors & Venue:** Vage Egiazarian et al. — *ICML 2024*  
* **Role:** Extreme 2-Bit / 3-Bit Quantization Baseline  
* **What it is:** Introduces learned additive quantization across transformer blocks, achieving Pareto-optimal accuracy in extreme 2-bit to 3-bit parameter regimes.  
* **How it relates to our research:** Allows us to test the extreme scaling boundary: compressing a massive 70B model down into a 16 GB budget to test if extreme parameter scale outperforms multi-agent systems.

---

### 26. Optimize Weight-Only Quantization of Large Language Models with an Advanced Rounding Technique (AutoRound)
* **File:** [`26_Cheng_2024_AutoRound_Advanced_Weight_Only_Quantization.pdf`](./26_Cheng_2024_AutoRound_Advanced_Weight_Only_Quantization.pdf)  
* **Authors & Venue:** Weiwei Cheng et al. (Intel Labs) — *EMNLP 2024*  
* **Role:** Advanced INT4 Rounding  
* **What it is:** Optimizes weight rounding values via sign gradient descent, outperforming GPTQ and standard RTN on 4-bit and 2-bit models.  
* **How it relates to our research:** Provides an easy-to-run, high-accuracy alternative quantization method for our large single-agent models.

---

### 27. MobileLLM: Optimizing Sub-billion Parameter Language Models for On-Device Use Cases
* **File:** [`27_Liu_2024_MobileLLM_Sub_Billion_Parameter_LLMs.pdf`](./27_Liu_2024_MobileLLM_Sub_Billion_Parameter_LLMs.pdf)  
* **Authors & Venue:** Zechun Liu et al. (Meta) — *ICML 2024*  
* **Role:** Sub-Billion Model Architecture Principles  
* **What it is:** Proves that deep-and-thin architectures with embedding sharing and block weight-sharing yield significantly superior accuracy for sub-billion parameter models on edge devices.  
* **How it relates to our research:** Informs how to select and configure small sub-agents (e.g., 1B–3B models) in our tightest memory tier (8 GB).

---

### 28. The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits (BitNet b1.58)
* **File:** [`28_Ma_2024_The_Era_of_1Bit_LLMs_BitNet_b158.pdf`](./28_Ma_2024_The_Era_of_1Bit_LLMs_BitNet_b158.pdf)  
* **Authors & Venue:** Shuming Ma et al. (Microsoft Research) — *arXiv:2402.17764 (Feb 2024)*  
* **Role:** Extreme Quantization Scaling Laws  
* **What it is:** Introduces 1.58-bit ternary {-1, 0, 1} architectures that match full-precision performance while drastically reducing memory bandwidth and latency.  
* **How it relates to our research:** Establishes the theoretical lower bound of parameter storage, demonstrating how far single-model memory compression can be pushed.

---

### 29. QuIP#: Even Better LLM Quantization with Hadamard Incoherence and Lattice Codebooks
* **File:** [`29_Tseng_2024_QuIP_Hadamard_Incoherence_Lattice_Codebooks.pdf`](./29_Tseng_2024_QuIP_Hadamard_Incoherence_Lattice_Codebooks.pdf)  
* **Authors & Venue:** Albert Tseng et al. (Cornell University) — *ICML 2024*  
* **Role:** Theoretical Error Bounds in Quantization  
* **What it is:** Combines randomized Hadamard transforms with $E_8$ lattice codebooks to achieve state-of-the-art 2-bit and 4-bit quantization with minimal loss.  
* **How it relates to our research:** Provides empirical validation that aggressively quantized models retain high reasoning capacity, strengthening the single-agent competitor arm.

---

### 30. SGLang: Efficient Execution of Structured Language Model Programs
* **File:** [`30_Sheng_2024_SGLang_Efficient_Execution_Structured_LM.pdf`](./30_Sheng_2024_SGLang_Efficient_Execution_Structured_LM.pdf)  
* **Authors & Venue:** Lianmin Sheng et al. (LMSYS, UC Berkeley) — *NeurIPS 2024*  
* **Role:** Multi-Agent KV-Cache Sharing Runtime  
* **What it is:** Introduces RadixAttention, which retains and shares KV-cache radix trees across multiple agent calls, branches, and multi-turn workflows.  
* **How it relates to our research:** Directly reduces the memory footprint of our multi-agent system by preventing redundant KV-cache allocations across cooperating sub-agents.

---

## Pillar 4: Benchmarks & Empirical Evaluation Infrastructure

### 31. GAIA: A Benchmark for General AI Assistants
* **File:** [`31_Mialon_2024_GAIA_Benchmark_for_General_AI_Assistants.pdf`](./31_Mialon_2024_GAIA_Benchmark_for_General_AI_Assistants.pdf)  
* **Authors & Venue:** Gregoire Mialon et al. (Meta, Hugging Face, AutoGPT) — *ICLR 2024*  
* **Role:** **Primary Tool-Use & Multi-Step Benchmark**  
* **What it is:** Curates 466 real-world assistant questions requiring multi-step planning, multimodal handling, web search, and tool execution.  
* **How it relates to our research:** Serves as our primary benchmark to test the hypothesis that multi-agent division of labor beats a single quantized model on tool-heavy tasks.

---

### 32. SWE-bench: Can Language Models Resolve Real-World GitHub Issues?
* **File:** [`32_Jimenez_2024_SWE_bench_Real_World_GitHub_Issues.pdf`](./32_Jimenez_2024_SWE_bench_Real_World_GitHub_Issues.pdf)  
* **Authors & Venue:** Carlos E. Jimenez et al. (Princeton University) — *ICLR 2024 (Oral)*  
* **Role:** Complex Real-World Engineering Benchmark  
* **What it is:** Evaluates language models on solving end-to-end GitHub issues across real codebases requiring multi-file navigation, code modification, and testing.  
* **How it relates to our research:** Used as a multi-step execution benchmark to test whether agent specialization (planner + coder + tester) outperforms a single monolithic model under memory budgets.

---

### 33. FRAMES: Factuality, Retrieval, And Multi-hop Evaluation with Structured Knowledge
* **File:** [`33_Krishna_2024_FRAMES_Factuality_Retrieval_Multihop.pdf`](./33_Krishna_2024_FRAMES_Factuality_Retrieval_Multihop.pdf)  
* **Authors & Venue:** Satyapriya Krishna et al. (Google) — *arXiv:2409.05591 / EMNLP 2024*  
* **Role:** **Primary Multi-Hop Reasoning Benchmark**  
* **What it is:** Evaluates LLMs on multi-hop retrieval and multi-step reasoning requiring synthesis of 2 to 15 distinct sources.  
* **How it relates to our research:** Directly replicates and extends the multi-hop reasoning benchmark suite used in Tran & Kiela (2026) to test reasoning retention under memory constraints.

---

### 34. The Berkeley Function-Calling Leaderboard (BFCL)
* **File:** [`34_Patil_2024_Berkeley_Function_Calling_Leaderboard_Gorilla.pdf`](./34_Patil_2024_Berkeley_Function_Calling_Leaderboard_Gorilla.pdf)  
* **Authors & Venue:** Shishir G. Patil et al. (UC Berkeley) — *arXiv:2403.01374 / ICML 2024*  
* **Role:** Standardized Function/Tool Calling Evaluation  
* **What it is:** Evaluates language models on function-calling accuracy across multiple languages, nested parameters, and multi-turn tool execution.  
* **How it relates to our research:** Validates whether smaller sub-agents can call tools with high parameter precision compared to large quantized models.

---

### 35. MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark
* **File:** [`35_Wang_2024_MMLU_Pro_Robust_Challenging_Benchmark.pdf`](./35_Wang_2024_MMLU_Pro_Robust_Challenging_Benchmark.pdf)  
* **Authors & Venue:** Yubo Wang et al. (Tsinghua, Waterloo) — *NeurIPS 2024 (Datasets Track)*  
* **Role:** Parametric World Knowledge Benchmark  
* **What it is:** An expanded benchmark with 10-choice questions and deeper reasoning problems designed to filter out lucky guesses and test deep parametric knowledge.  
* **How it relates to our research:** Tests our counter-hypothesis: that a single large model (even at 4-bit) preserves superior world knowledge that smaller multi-agent models cannot recover.

---

## Quick Reference Matrix

| # | Paper | Core Topic | Role in Your Study |
|---|---|---|---|
| **01** | **Tran & Kiela (2026)** | SAS vs. MAS under equal token budgets | **Base Paper Template** (Swap token budget $\to$ VRAM budget) |
| **02** | **Żywot et al. (2026)** | Small agent collaboration beats big LLM | **Alternative Base Paper** (Tool-use & small agent baseline) |
| **03** | **Kim et al. (2025)** | Scaling laws for agent systems | Theoretical agent scaling & topology baseline |
| **04** | **Wang et al. (MoA, 2024)** | Mixture-of-Agents layered architecture | Multi-agent layered baseline |
| **05** | **Wang et al. (ACL 2024)** | Bounds of multi-agent debate | Rigorous single-agent prompting baseline |
| **06** | **Li et al. (TMLR 2024)** | "More Agents Is All You Need" | Multi-agent voting/sampling ensemble baseline |
| **07** | **Cemri et al. (2025)** | Why multi-agent systems fail (MAST) | Failure mode & context collapse taxonomy |
| **08** | **Ke et al. (2026)** | MAS-Orchestra orchestration benchmark | Multi-agent coordination testbed |
| **09** | **AgentVerse (ICLR 2024)** | Multi-agent collaboration framework | Open-source multi-agent simulation framework |
| **10** | **ChatEval (ICLR 2024)** | Multi-agent debate evaluators | Multi-agent peer debate protocol |
| **11** | **MetaGPT (ICLR 2024)** | SOP-driven agent role assignment | Hierarchical orchestrator-worker architecture |
| **12** | **ChatDev (ACL 2024)** | Communicative software agents | Sequential pipeline (decompose-execute-verify) topology |
| **13** | **DyLAN (ICLR 2024)** | Dynamic agent pruning | Communication token minimization strategy |
| **14** | **ReConcile (ACL 2024)** | Round-table consensus discussion | Multi-agent consensus protocol |
| **15** | **Wang et al. (EMNLP 2024)** | Reasoning in token economies | **Methodology Template** for budget normalization |
| **16** | **Bench360 (2025)** | Local LLM inference benchmarking | **VRAM & Hardware Profiling Protocol** |
| **17** | **Monkeys (2024)** | Inference compute via repeated sampling | Strong single-agent compute-matched baseline |
| **18** | **ToolOrchestra (2024)** | Cost-aware tool orchestration | Budgeted tool invocation protocol |
| **19** | **Chen et al. ($q_s$, 2026)** | MoE double memory penalty | Mathematical capacity vs. memory penalty theory |
| **20** | **vLLM (SOSP 2023)** | PagedAttention KV-cache management | Inference engine for concurrent agent residency |
| **21** | **Frugal-MoE (ACL 2024)** | Dynamic subnetwork activation | Adaptive memory allocation comparison |
| **22** | **AWQ (MLSys 2024)** | Activation-aware weight quantization | **Core 4-bit Quantization Method** for SAS models |
| **23** | **QuaRot (NeurIPS 2024)** | 4-bit weights + activations + KV-cache | End-to-end 4-bit SAS compression method |
| **24** | **SpinQuant (ICLR 2025)** | Learned rotation quantization | SOTA 4-bit quantization baseline |
| **25** | **AQLM (ICML 2024)** | Additive 2-bit/3-bit quantization | Extreme compression for 70B models in 16/24GB |
| **26** | **AutoRound (EMNLP 2024)** | Advanced sign gradient rounding | High-accuracy INT4 quantization baseline |
| **27** | **MobileLLM (ICML 2024)** | Sub-billion on-device architectures | Architecture rules for sub-agents in 8GB tier |
| **28** | **BitNet b1.58 (2024)** | 1.58-bit ternary language models | Theoretical memory-efficiency lower bound |
| **29** | **QuIP# (ICML 2024)** | Incoherence + lattice codebooks | Quantization distortion error bounds |
| **30** | **SGLang (NeurIPS 2024)** | RadixAttention KV-cache reuse | Multi-agent KV-cache sharing to save VRAM |
| **31** | **GAIA (ICLR 2024)** | General AI assistant benchmark | **Primary Tool-Use Benchmark** |
| **32** | **SWE-bench (ICLR 2024)** | Real-world GitHub software issues | Complex multi-step task benchmark |
| **33** | **FRAMES (2024)** | Factuality & multi-hop evaluation | **Primary Multi-Hop Reasoning Benchmark** |
| **34** | **BFCL (ICML 2024)** | Berkeley function-calling leaderboard | Tool-calling parameter precision evaluation |
| **35** | **MMLU-Pro (NeurIPS 2024)**| Robust multi-task language understanding| **Parametric World Knowledge Benchmark** |
