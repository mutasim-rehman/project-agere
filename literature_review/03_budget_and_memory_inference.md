# Literature Review: Pillar 2 — Budget-Constrained & Memory-Aware Inference (Papers 15–21)

This document provides a comprehensive, rigorous literature review of Papers 15 through 21, covering **budget-normalized evaluation methodologies, local hardware memory profiling, inference compute scaling, and resource-bounded serving**.

---

## 15. Reasoning in Token Economies: Budget-Aware Evaluation of LLM Reasoning Strategies

* **File:** [`../sources/15_Wang_2024_Reasoning_in_Token_Economies_Budget_Aware.pdf`](../sources/15_Wang_2024_Reasoning_in_Token_Economies_Budget_Aware.pdf)
* **Authors:** Junlin Wang, Siddhartha Jain, Dejiao Zhang, Baishakhi Ray, Varun Kumar, Ben Athiwaratkun
* **Affiliation & Venue:** AWS AI Labs — **EMNLP 2024 (Main Conference)**

### 1. What It Is
A groundbreaking empirical paper proving that many complex LLM reasoning and agent strategies (e.g., multi-agent debate, Reflexion, Tree-of-Thoughts) do not outperform simple baselines because of superior algorithmic design, but simply because they **consume vastly more tokens**. It introduces a formal framework for **budget-aware evaluation** that normalizes performance against token expenditure.

### 2. How It Relates to Our Research
This is our **primary methodological inspiration for budget normalization**. Wang et al. established that comparing reasoning methods without equalizing computational budget is scientifically flawed. Our research takes their exact principle—*"you must hold resources equal to evaluate architectural superiority"*—and translates it from the soft variable of **token count** to the hard hardware reality of **resident GPU VRAM memory ($M$)**.

### 3. Detailed Methodology
* **Strategies Evaluated:** Zero-shot CoT, Few-shot CoT, Self-Consistency (majority voting), Multi-Agent Debate, Reflexion, Tree-of-Thoughts.
* **Controlled Axis:** Fixed token budget (sampling budget ranging from 512 to 8,192 tokens per query).
* **Models:** Llama-2-70B, GPT-3.5-Turbo, Claude-2.
* **Benchmarks:** GSM8K, SVAMP, StrategyQA, ARC-Challenge.
* **Metrics:** Accuracy-per-token efficiency curves, Negative scaling threshold, Pareto-frontier analysis.

### 4. Key Novelty & Theoretical Contributions
* **The "Compute-Performance Equivalence":** Shows that providing a standard single agent with self-consistency (repeated sampling) equal to the token budget of a multi-agent debate system results in the single agent outperforming the multi-agent system on 80%+ of tasks.
* **Negative Scaling in MAS:** Uncovers that for strategies like multi-agent debate, expanding the token budget beyond an optimal threshold actually degrades accuracy due to conversational derailment.

### 5. Critical Limitations & Caveats
* Strictly token-budgeted; ignores physical hardware parameters such as GPU memory bandwidth, VRAM residency, and weight quantization.

### 6. Why We SHOULD Include It as a Source
* **Top-tier EMNLP 2024 Main Conference.** Essential for our Methodology section to justify why unconstrained evaluations are scientifically invalid and why our memory-budgeted framework is a mandatory next step in the literature.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Cannot be excluded: it is the primary methodological precedent for budget-normalized evaluation in modern NLP.

---

## 16. Bench360: Benchmarking Local LLM Inference from 360 Degrees

* **File:** [`../sources/16_Lin_2025_Bench360_Benchmarking_Local_LLM_Inference.pdf`](../sources/16_Lin_2025_Bench360_Benchmarking_Local_LLM_Inference.pdf)
* **Authors:** Lin et al.
* **Affiliation & Venue:** *arXiv:2511.16682 (Late 2025 / 2026)*

### 1. What It Is
A unified benchmarking suite that provides a 360-degree evaluation of local LLM inference across model architectures, precision quantization levels, serving runtimes, hardware memory constraints, latency, and energy consumption.

### 2. How It Relates to Our Research
Serves as our **hardware and memory profiling protocol and our internal replication control baseline**. Bench360 demonstrated at the single-agent level that larger quantized models consistently beat smaller unquantized models under fixed VRAM. In our 2×2 Factorial Design, this establishes Cell B vs. Cell A as our internal replication control baseline, while providing the empirical measurement protocol for verifying our 15 VRAM hardware tiers (4 GB to 32 GB) under the Memory Utilization Parity Protocol (MUPP).

### 3. Detailed Methodology
* **Dimensions Profiled:**
  1. *Hardware Resources:* Peak VRAM (GB), memory bandwidth saturation, energy (Joules/query).
  2. *Inference Engines:* vLLM, SGLang, TGI, LMDeploy, llama.cpp.
  3. *Quantization Schemes:* FP16, INT8, INT4 (AWQ, GPTQ), 2-bit/3-bit.
  4. *Workloads:* Single-stream local desktop, multi-turn dialogue, high-concurrency batching.
* **Metrics:** TTFT (Time to First Token), End-to-End Latency, GPU Memory Watermark, Per-task functional accuracy (F1, Executability).

### 4. Key Novelty & Theoretical Contributions
* **Exposing the "No Universal Best" Rule:** Proves that inference configurations are Pareto-distributed: a model setup that maximizes throughput under server batching performs poorly under single-user latency or strict VRAM caps.
* **Quantization vs. Latency Trade-Off:** Quantifies the compute dequantization overhead on consumer GPUs, showing that 4-bit models save VRAM but can suffer latency penalties if memory bandwidth is not the bottleneck.

### 5. Critical Limitations & Caveats
* Focused primarily on single-model serving pipelines rather than multi-agent collaborative workflows.

### 6. Why We SHOULD Include It as a Source
* Directly gives us the empirical blueprint for defining our 8 GB, 16 GB, and 24 GB hardware tiers, ensuring our VRAM accounting is scientifically standard and reproducible.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If our paper focuses purely on accuracy and algorithmic theory rather than hardware metrics (watts, latency, memory profiling), this paper plays a supporting rather than foundational role.

---

## 17. Large Language Monkeys: Scaling Inference Compute with Repeated Sampling

* **File:** [`../sources/17_Brown_2024_Large_Language_Monkeys_Scaling_Inference_Compute.pdf`](../sources/17_Brown_2024_Large_Language_Monkeys_Scaling_Inference_Compute.pdf)
* **Authors:** Bradley Brown, Jordan Juravsky, Anthony Ryan, et al.
* **Affiliation & Venue:** University of Waterloo, Stanford University — *arXiv:2407.21787 (July 2024)*

### 1. What It Is
A foundational study on test-time inference compute scaling, showing that scaling repeated independent sampling (coverage and majority voting) across small and medium models can match or exceed the performance of models that are 10× to 100× larger.

### 2. How It Relates to Our Research
Represents a vital **single-agent scaling baseline**. In our trade-off study, a key competitor to multi-agent systems is giving the single quantized model additional inference compute via repeated sampling (self-consistency) within the memory limit. Brown et al. provides the scaling laws for this comparison.

### 3. Detailed Methodology
* **Sampling Regime:** Generates up to thousands of candidate solutions ($k = 1$ to $10,000$) per prompt.
* **Aggregation Strategies:** Best-of-$N$, Majority Voting, Verifier/Reward Model reranking.
* **Models:** Llama-3-8B, Llama-3-70B, DeepSeek-Coder.
* **Benchmarks:** SWE-bench Lite, HumanEval, GSM8K, MATH.
* **Metrics:** Pass@$k$, Compute Cost ($k \times \text{tokens}$), Accuracy vs. Compute Scaling Curves.

### 4. Key Novelty & Theoretical Contributions
* **Power-Law Coverage Scaling:** Demonstrates that repeated sampling on an 8B model achieves performance parity with frontier models on coding benchmarks like SWE-bench Lite when sampled sufficiently.
* **Inference-Time vs. Pre-Training Trade-off:** Formulates how test-time compute can substitute for parameter scale.

### 5. Critical Limitations & Caveats
* Relies on external verifiers or deterministic execution environments (e.g., Python test cases) to select the best answer at high $k$, which is impossible for open-ended QA.
* Massive cumulative token and latency costs at high $k$.

### 6. Why We SHOULD Include It as a Source
* Crucial for defending our single-agent baseline. A reviewer might ask: *"Did you test whether the single quantized model could simply sample multiple times?"* Citing Brown et al. allows us to address this directly.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Focuses on extreme repeated sampling ($k > 100$) rather than architectural multi-agent interaction.

---

## 18. ToolOrchestra: Collaborative and Cost-Aware Tool Orchestration for Language Agents

* **File:** [`../sources/18_Su_2024_ToolOrchestra_Cost_Aware_Tool_Orchestration.pdf`](../sources/18_Su_2024_ToolOrchestra_Cost_Aware_Tool_Orchestration.pdf)
* **Authors:** Su et al.
* **Affiliation & Venue:** *arXiv:2411.08573 (November 2024)*

### 1. What It Is
A framework that optimizes multi-agent tool execution by dynamically scheduling and routing tool calls under explicit constraints on financial cost, API rate limits, and latency budgets.

### 2. How It Relates to Our Research
Demonstrates how **multi-agent systems behave under explicit resource boundaries**. While our primary constraint is resident memory rather than per-call monetary budget, ToolOrchestra provides precedence for designing multi-agent orchestration that actively respects deployment constraints.

### 3. Detailed Methodology
* **Mechanism:** Cost-aware routing module that estimates expected utility vs. execution cost before invoking sub-agent tool calls.
* **Benchmarks:** ToolBench, API-Bank, GAIA.
* **Metrics:** Task Accuracy, Cost Efficiency (Accuracy / Dollar), Tool Selection Precision.

### 4. Key Novelty & Theoretical Contributions
* **Budget-Constrained Tool Scheduling:** Proves that unconstrained multi-agent tool calling introduces massive redundancy, and that enforcing cost budgets forces agents to generate more focused, higher-quality queries.

### 5. Critical Limitations & Caveats
* Focuses on cloud API dollar costs rather than on-device GPU memory residency.

### 6. Why We SHOULD Include It as a Source
* Valuable citation when framing the literature on "constrained agent systems," reinforcing that modern agent research is shifting toward resource-aware deployment.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Highly specialized for tool-API economies; can be omitted if selecting the top 15 core papers.

---

## 19. The $q_s$ Inequality: Quantifying the Double Penalty of Mixture-of-Experts at Inference

* **File:** [`../sources/19_Chen_2026_The_qs_Inequality_MoE_Inference_Penalty.pdf`](../sources/19_Chen_2026_The_qs_Inequality_MoE_Inference_Penalty.pdf)
* **Authors:** Chen et al.
* **Affiliation & Venue:** *arXiv:2603.08960 (March 2026)*

### 1. What It Is
A theoretical and mathematical paper that derives the **$q_s$ inequality**, formalizing the dual penalty incurred by sparse Mixture-of-Experts (MoE) architectures at inference: memory capacity overhead and routing inefficiencies compared to compute-matched dense models.

### 2. How It Relates to Our Research
Provides the **formal mathematical foundation for the Compounding Error / Double Penalty Hypothesis ($\Delta_{\text{interaction}} < 0$) in our 2×2 Factorial Design**. Chen et al. proved that sparse MoEs incur an inherent inference double penalty under total parameter parity compared to dense models. In our 2×2 grid, Cell D (MAS-Quant) combines both post-training quantization and multi-agent routing. If quantization noise compounds across lossy natural language handoffs, Cell D will underperform both Cell C (MAS-FP16) and Cell B (SAS-Quant) by more than predicted from each effect alone—a direct macro-level confirmation of the $q_s$ inequality operating at the agent orchestration layer.

### 3. Detailed Methodology
* **Theoretical Framework:** Quality-equivalence multiplier ($q_s$) bounding the parameter gap between routed architectures and dense monolithic models.
* **Empirical Validation:** Tested across dense and MoE architectures under matched total parameters vs. matched active parameters.
* **Metrics:** Quality loss multiplier, Memory residency ratio, Effective parameter utilization.

### 4. Key Novelty & Theoretical Contributions
* **The Total Parameter Parity Inversion:** Proves that while MoEs win when matching *active* compute (FLOPs), dense models win decisively when matching *total stored resident parameters* (memory). This directly mirrors our hypothesis at the agent orchestration layer!

### 5. Critical Limitations & Caveats
* Evaluates internal transformer layers (sub-network routing inside one model) rather than whole orchestrated agent systems.

### 6. Why We SHOULD Include It as a Source
* **Critical theoretical weapon in our Introduction.** Allows us to state: *"At the micro-architecture level, the $q_s$ inequality proved that distributed capacity loses under equal total memory; we test whether this fundamental law also holds at the macro-level of multi-agent orchestration."*

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Very recent 2026 preprint; mathematical rigor is high, but application to agents is analogical rather than direct.

---

## 20. Efficient Memory Management for Large Language Model Serving with PagedAttention (vLLM)

* **File:** [`../sources/20_Kwon_2023_vLLM_PagedAttention_Memory_Management.pdf`](../sources/20_Kwon_2023_vLLM_PagedAttention_Memory_Management.pdf)
* **Authors:** Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, Ying Sheng, Lianmin Zheng, Cody Hao Yu, Joseph E. Gonzalez, Hao Zhang, Ion Stoica
* **Affiliation & Venue:** UC Berkeley — **SOSP 2023 / MLSys**

### 1. What It Is
The foundational systems paper that introduced **PagedAttention** and the **vLLM** serving engine, solving the problem of dynamic KV-cache memory fragmentation and waste in GPU VRAM through virtual memory paging.

### 2. How It Relates to Our Research
Supplies the **core serving infrastructure** for our experimental harness. When running multiple concurrent sub-agents in an MAS configuration, KV-cache fragmentation can easily trigger premature Out-Of-Memory (OOM) crashes. vLLM allows us to run both our single-agent and multi-agent systems with near-zero KV memory waste.

### 3. Detailed Methodology
* **Core Mechanism:** PagedAttention divides contiguous KV-cache tensors into fixed-size physical memory pages, dynamic non-contiguous allocation, copy-on-write sharing for parallel branches.
* **Metrics:** Throughput (tokens/sec), KV-cache memory fragmentation percentage, Maximum concurrent request capacity.

### 4. Key Novelty & Theoretical Contributions
* **Near-Zero Memory Waste:** Reduces KV-cache memory waste from 60–80% in standard Hugging Face implementations down to under 4%.
* **Parallel Sampling Efficiency:** Enables instantaneous branching and copy-on-write KV sharing, crucial for multi-agent discussions.

### 5. Critical Limitations & Caveats
* Does not examine multi-agent prompt scheduling or reasoning accuracy; purely a low-level systems paper.

### 6. Why We SHOULD Include It as a Source
* **Mandatory systems citation.** Reviewers evaluating our memory accounting will demand to know how KV caches were managed; citing vLLM proves our memory bounds were rigorously controlled.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* None. It is the universally accepted standard citation for local LLM memory management.

---

## 21. Frugal-MoE: Cost-Effective Mixture of Experts via Activation-Guided Routing

* **File:** [`../sources/21_Yao_2024_Frugal_MoE_Cost_Effective_MoE_Routing.pdf`](../sources/21_Yao_2024_Frugal_MoE_Cost_Effective_MoE_Routing.pdf)
* **Authors:** Yao et al.
* **Affiliation & Venue:** **ACL 2024 (Findings)**

### 1. What It Is
An inference-optimization paper that introduces activation-guided dynamic routing for Mixture-of-Experts models, selectively skipping expert loading and activation for simpler tokens to minimize runtime memory and computational demands.

### 2. How It Relates to Our Research
Represents an **adaptive memory-budgeting baseline**. In contrast to our static multi-agent setups where all agent models are resident, Frugal-MoE illustrates the benefits of dynamic subnetwork activation under resource constraints.

### 3. Detailed Methodology
* **Routing Mechanism:** Predicts token difficulty and routes easy tokens to a minimal expert subset while reserving full expert capacity for hard tokens.
* **Benchmarks:** MMLU, GSM8K, CommonSenseQA.
* **Metrics:** FLOP reduction, Memory bandwidth savings, Task accuracy retention.

### 4. Key Novelty & Theoretical Contributions
* **Input-Adaptive Capacity Allocation:** Proves that uniform allocation of model capacity across all tokens wastes significant compute, establishing that dynamic routing preserves 98%+ of accuracy while cutting compute by up to 40%.

### 5. Critical Limitations & Caveats
* Requires MoE architecture; does not directly apply to dense model multi-agent systems.

### 6. Why We SHOULD Include It as a Source
* Useful in our Discussion section when contrasting static agent memory allocation with adaptive routing strategies.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Secondary to our main question; can be filtered out when compiling the final 15 core papers.

---

## 40. PolyKV: A Shared Asymmetrically-Compressed KV Cache Pool for Multi-Agent LLM Inference

* **File:** [`../sources/40_Patel_2026_PolyKV_Shared_Asymmetrically_Compressed_KV_Cache_MAS.pdf`](../sources/40_Patel_2026_PolyKV_Shared_Asymmetrically_Compressed_KV_Cache_MAS.pdf)
* **Authors:** Ishan Patel, Ishan Joshi
* **Affiliation & Venue:** *arXiv:2604.24971 (April 2026)*

### 1. What It Is
A systems architecture for multi-agent LLM inference in which multiple concurrent agents share a single, asymmetrically-compressed KV-cache pool instead of maintaining redundant per-agent KV allocations.

### 2. How It Relates to Our Research
Directly addresses our **Memory Utilization Parity Protocol (MUPP)** and serving infrastructure for **Cell C (MAS-FP16)** and **Cell D (MAS-Quant)**. PolyKV demonstrates how concurrent multi-agent teams can scale to high agent counts without exceeding strict hardware VRAM limits.

### 3. Detailed Methodology
* **Asymmetric Compression:** Keys quantized at INT8 (`q8_0`) to preserve attention softmax stability; Values compressed using TurboQuant MSE (Fast Walsh-Hadamard Transform + 3-bit Lloyd-Max quantization).
* **Evaluation:** SmolLM2-1.7B-Instruct and LLaMA-3-8B-Instruct up to 15 concurrent agents across 4K context.
* **Metrics:** KV Cache VRAM Footprint, Perplexity Degradation, BERTScore F1.

### 4. Key Findings & Theoretical Contributions
* **97.7% KV Memory Reduction:** On LLaMA-3-8B with 15 agents sharing a 4K context, reduces KV cache memory from 19.8 GB to 0.45 GB.
* **Negligible Quality Degradation:** Maintains an average of only +0.57% perplexity change and 0.928 BERTScore F1, with PPL delta actually improving as context length increases.

---

## 41. QKVShare: Quantized KV-Cache Handoff for Multi-Agent On-Device LLMs

* **File:** [`../sources/41_Honavar_2026_QKVShare_Quantized_KV_Cache_Handoff_Multi_Agent_OnDevice.pdf`](../sources/41_Honavar_2026_QKVShare_Quantized_KV_Cache_Handoff_Multi_Agent_OnDevice.pdf)
* **Authors:** Pratik Honavar, Tejpratap GVSL
* **Affiliation & Venue:** *arXiv:2605.03884 (May 2026)*

### 1. What It Is
A framework for quantized KV-cache handoff between on-device agents, combining token-level mixed-precision allocation and a self-contained CacheCard representation.

### 2. How It Relates to Our Research
Informs the on-device execution path of **Cell D (MAS-Quant)** on constrained memory tiers (4 GB to 12 GB), eliminating costly full context re-prefill penalties during sequential inter-agent handoffs.

### 3. Key Findings & Theoretical Contributions
* **Latency Reduction:** Cuts Time-to-First-Token (TTFT) compared to full re-prefill across all contexts (130.7 ms vs. 150.2 ms at 1K; 397.1 ms vs. 1029.7 ms at 8K context — a 61.4% reduction).
* **Multi-Hop Resilience:** Adaptive quantization maintains competitive accuracy under repeated handoff, showing greatest advantages in deep multi-hop workflows.

---

## 43. Warp-Cortex: An Asynchronous, Memory-Efficient Architecture for Million-Agent Cognitive Scaling on Consumer Hardware

* **File:** [`../sources/43_Ruiz_Williams_2026_Warp_Cortex_Memory_Efficient_Architecture_Million_Agent.pdf`](../sources/43_Ruiz_Williams_2026_Warp_Cortex_Memory_Efficient_Architecture_Million_Agent.pdf)
* **Authors:** Jorge L. Ruiz Williams
* **Affiliation & Venue:** *arXiv:2601.01298 (January 2026)*

### 1. What It Is
An asynchronous multi-agent architecture that decouples agent logic from physical GPU memory through Singleton Weight Sharing and Topological Synapse KV-cache manifold sparsification.

### 2. How It Relates to Our Research
Establishes the theoretical lower bound for physical memory consumption in multi-agent systems on consumer hardware. It proves that homogeneous agent teams can share a single resident model instance ($O(1)$ weight footprint) while maintaining isolated execution streams.

### 3. Key Findings & Theoretical Contributions
* **Massive Concurrency on Consumer GPUs:** Empirically demonstrates 100 concurrent agents running within 2.2 GB total VRAM on an RTX 4090.
* **Topological KV Sparsification:** Uses witness-complex techniques from Topological Data Analysis (TDA) to compress context from $O(N \cdot L)$ to $O(N \cdot k)$, preserving persistent homological features of the latent reasoning manifold.
