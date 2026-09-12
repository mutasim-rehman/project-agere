# Spend It Together or Spend It Big: Research Roadmap & TODO
*(Project Agere — A 2×2 Factorial Study of Architectural Modularity and Post-Training Quantization Under Strict VRAM Parity)*

> **Overarching RQ:** Given a fixed physical resident VRAM budget $M$, do the choice of architecture (Single-Agent vs. Multi-Agent) and the choice of compression strategy (native FP16 vs. quantized scaling) act independently, or do they interact — such that the optimal compression strategy depends on which architecture is chosen?

---

## Phase 1: Problem Definition & Motivation
*Establish what you're studying, why it matters, and scope the 2×2 factorial contribution.*

- [x] Identify the core architectural dilemma (Single-Agent vs. Multi-Agent under memory parity)
- [x] Formulate the **2×2 Factorial Experimental Design**:
  - Cell A: Single-Agent FP16 (Control baseline / Bench360 losing baseline)
  - Cell B: Single-Agent Quantized (Scaled-up generalist / Bench360 winning baseline)
  - Cell C: Multi-Agent FP16 (Original Agere hypothesis: native precision sub-agents)
  - Cell D: Multi-Agent Quantized (New proposal: larger sub-agents, quantized & orchestrated)
- [x] Articulate why VRAM is a hard physical ceiling vs. soft token/FLOP budgets
- [x] Define the 5 research gaps from prior work (Compute-vs-Memory, Cross-Silo, Tool Confound, $q_s$ Inequality, Task Moderator)
- [x] Frame the real-world application gap (local deployment dilemma across 15 hardware tiers)
- [x] Formulate the 5 Core Research Questions:
  - [x] **RQ1 (A vs. B):** Does larger quantized single model beat smaller FP16 single model? (Replication control)
  - [x] **RQ2 (C vs. B):** Does native FP16 MAS beat single larger quantized model? (Original RQ)
  - [x] **RQ3 (D vs. A):** Does quantized MAS of larger models beat single smaller FP16 model?
  - [x] **RQ4 (D vs. B):** Does quantized MAS of larger models beat single giant quantized model?
  - [x] **RQ5 (Interaction Term):** Does quantization degrade performance more, less, or equally inside MAS vs. SAS?
- [x] Formulate explicit hypotheses for the 2×2 Factorial Interaction:
  - [x] **Hypothesis 1 (Compounding Error / Double Penalty — $q_s$ Inequality):** $\Delta_{\text{interaction}} < 0$. Quantization noise stacks across agent handoffs.
  - [x] **Hypothesis 2 (Role Specialization Noise-Buffering):** $\Delta_{\text{interaction}} > 0$. Role specialization buffers against quantization noise.
  - [x] **Null Hypothesis ($H_0$):** $\Delta_{\text{interaction}} = 0$. Architecture and compression choices are strictly additive and independent.

---

## Phase 2: Literature Review & Gap Analysis
*Survey, synthesize, and identify what's missing.*

### 2.1 — Source Collection
- [x] Identify and curate the 35 primary research papers
- [x] Download all 35 PDFs to `sources/`
- [x] Build `sources/INDEX.md` with full bibliographic entries
- [x] Build `sources/PAPERS_DICTIONARY.md` with paper-level metadata

### 2.2 — Individual Paper Analysis
- [x] Write individual study summaries for all 35 papers (`literature_review/summaries/`)
  - [x] Papers 01–08 (MAS vs. SAS & collaboration)
  - [x] Papers 09–14 (MAS topologies & frameworks)
  - [x] Papers 15–21 (Budget, memory, inference)
  - [x] Papers 22–30 (Quantization & on-device)
  - [x] Papers 31–35 (Benchmarks & evaluation)

### 2.3 — Thematic Synthesis
- [x] Write `01_mas_vs_sas_collaboration.md` (Papers 01–08)
- [x] Write `02_mas_topologies_and_frameworks.md` (Papers 09–14)
- [x] Write `03_budget_and_memory_inference.md` (Papers 15–21)
- [x] Write `04_quantization_and_ondevice.md` (Papers 22–30)
- [x] Write `05_benchmarks_and_evaluation.md` (Papers 31–35)

### 2.4 — Master Synthesis & Bibliography Curation
- [x] Write `literature_review/README.md` master synthesis document
- [x] Filter 35 papers down to the 15-paper core bibliography
- [x] Justify why each of the remaining 20 papers was excluded
- [x] Write paper-framing templates (Introduction & Related Work paragraphs)

### 2.5 — Final Literature Review Polishing
- [ ] Cross-check every claim in thematic docs against the actual paper summaries for accuracy
- [ ] Add missing cross-references between thematic documents (e.g., link quantization findings to MAS evaluation gaps)
- [ ] Verify no relevant 2025–2026 papers were missed (do a final arXiv sweep for "multi-agent VRAM", "quantized agent", "memory-constrained LLM")
- [ ] Add a "Limitations of This Review" sub-section to the master README

---

## Phase 3: Research Questions, Hypotheses & Experimental Design
*Turn gaps into testable questions with a rigorous experimental protocol.*

### 3.1 — Formalize Research Questions (2×2 Factorial Framework)
- [x] Write RQ1 precisely (A vs. B: Does a larger, quantized single model outperform a smaller FP16 single model under equal VRAM? Replication control)
- [x] Write RQ2 precisely (C vs. B: Does native FP16 MAS outperform a single larger quantized model under equal VRAM? Core Agere RQ)
- [x] Write RQ3 precisely (D vs. A: Does a quantized MAS of larger models outperform a single smaller FP16 model under equal VRAM?)
- [x] Write RQ4 precisely (D vs. B: Does a quantized MAS of larger models outperform a single much larger quantized model under equal VRAM?)
- [x] Write RQ5 precisely (Interaction Term $\Delta_{\text{interaction}}$: Does quantization degrade performance more, less, or equally inside MAS vs. SAS?)
- [x] Formalize the interaction metric: $\Delta_{\text{interaction}} = [\text{Score}(D) - \text{Score}(C)] - [\text{Score}(B) - \text{Score}(A)]$
- [x] Review RQs for testability — each cell mapped to standardized VRAM tiers, identical benchmark prompts, and deterministic evaluation

### 3.2 — Formulate Hypotheses & Mechanistic Models
- [x] **Hypothesis 1 (Compounding Error / Double Penalty — $q_s$ Inequality):** $\Delta_{\text{interaction}} < 0$. Quantization noise compounds multiplicatively across agent handoffs; quantized MAS suffers an extra penalty not present in single-agent state.
- [x] **Hypothesis 2 (Role Specialization Noise-Buffering):** $\Delta_{\text{interaction}} > 0$. Decomposed sub-agent prompts narrow the token distribution; specialized agents tolerate lower precision better than a monolithic generalist.
- [x] **Null Hypothesis ($H_0$):** $\Delta_{\text{interaction}} = 0$. Architecture and quantization are orthogonal, strictly additive design decisions.
- [x] Task-Moderator Hypothesis: $\Delta_{\text{interaction}}$ is negative on multi-hop sequential reasoning (FRAMES) where errors cascade, but positive on parallel tool-augmented tasks (GAIA) where sub-agents act independently.

### 3.3 — Experimental Design Matrix
- [x] Define the 15 VRAM budget tiers (4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32 GB) with 2 GB spacing
- [x] Define the residency formula: $M_{\text{total}} = M_{\text{weights}} + M_{\text{KV-cache}} + M_{\text{runtime}} \le M_{\text{budget}}$
- [x] Establish the **Memory Utilization Parity Protocol (MUPP)** — mandate $\ge 95\%$ actual resident VRAM utilization across all 4 cells (calibrated model/quantization selection + runtime KV-cache reservoir pre-allocation)
- [x] Design **Cell A (SAS-FP16)** across all 15 tiers (native FP16 control baseline)
- [x] Design **Cell B (SAS-Quant)** across all 15 tiers (saturating quantized single model, plus 5-level quant sweep)
- [x] Design **Cell C (MAS-FP16)** across all 15 tiers (native FP16 sub-agents across 4 topologies: Hierarchical, Debate, Pipeline, AHDS)
- [x] Design **Cell D (MAS-Quant)** across all 15 tiers (larger sub-agents, quantized to fit budget; 15 YAML configs in `configs/systems/mas/quant/`)
- [x] Design the AHDS (Adaptive Hierarchical with Dynamic Pruning & Structured Communication) architecture
  - [x] Document 7 MAS failure modes from literature review (P1–P7)
  - [x] Define 6 AHDS design principles solving P1–P7
  - [x] Specify per-tier AHDS instantiations across all 15 tiers (both FP16 and Quantized variants)
- [x] Generate machine-readable YAML configs (15 in `configs/hardware_tiers/`, 15 in `configs/systems/mas/quant/`, 15 in `configs/systems/mas/ahds/` — 45 total)
- [x] Establish the **Minimal Dual-Benchmark Design (Controlled Task Moderator)**:
  - [x] Anchor 1: GAIA Lean Tool-Intensive Slice (`configs/benchmarks/gaia_tool_slice.yaml` — 100 tasks, primary finding engine for noise-buffering $\Delta > 0$)
  - [x] Anchor 2: MuSiQue Multi-Hop Reasoning Slice (`configs/benchmarks/musique_reasoning_slice.yaml` — 150 tasks, calibration & DPI error cascade $\Delta < 0$)
- [x] Optional secondary STEM probes (MATH-500 / GPQA Diamond for symbolic depth)
- [x] Define all evaluation metrics ($\text{Acc}$, $\eta_M$, $\eta_T$, McNemar's $\chi^2$, Two-Way ANOVA $\Delta_{\text{interaction}}$, Pareto dominance)
- [x] Determine the number of seeds / repetitions per experiment (3 seeds: 42, 123, 999; $T=0.0$ greedy, $T=0.7$ stochastic)
- [x] Design control experiments (isolate collaboration, topology, and tool confounds via AHDS vs Peer Debate vs Pipeline)
- [x] Write the full experimental protocol as a standalone `EXPERIMENT_PROTOCOL.md` document

---

## Phase 4: Environment Setup & Infrastructure
*Build the codebase, install dependencies, and get models running.*

### 4.1 — Repository Scaffolding
- [ ] Create the directory structure per the README architecture
  ```
  configs/hardware_tiers/, configs/models/, configs/systems/sas/, configs/systems/mas/, configs/benchmarks/
  src/agents/, src/inference/, src/profiling/, src/benchmarks/, src/analysis/
  experiments/, paper/
  ```
- [ ] Initialize `pyproject.toml` or `requirements.txt` with core dependencies
- [ ] Set up Python virtual environment (venv / conda)
- [ ] Set up version control conventions (`.gitignore`, commit message format)

### 4.2 — Dependency Installation & Validation
- [ ] Install PyTorch with CUDA support (verify `torch.cuda.is_available()`)
- [ ] Install inference backend
  - [ ] Option A: vLLM (`pip install vllm`) — verify multi-model serving
  - [ ] Option B: HuggingFace Transformers + bitsandbytes / auto-gptq / autoawq
  - [ ] Option C: SGLang (if KV-cache sharing is needed for MAS)
- [ ] Install quantization libraries (autoawq, auto-gptq, bitsandbytes)
- [ ] Install evaluation libraries (datasets, sympy for math parsing, rouge/bleu if needed)
- [ ] Install profiling tools (nvidia-smi, pynvml, torch.cuda.memory_stats)
- [ ] Install statistical analysis libraries (scipy, statsmodels, bootstrapped)
- [ ] Install visualization libraries (matplotlib, seaborn, plotly)

### 4.3 — Model Acquisition & Validation
- [ ] Download target model weights across the Qwen 2.5 family:
  - [ ] **Native FP16 weights** (for all MAS agents and SAS FP16 baseline):
    - [ ] Qwen2.5-0.5B-Instruct (~1.0 GB)
    - [ ] Qwen2.5-1.5B-Instruct (~3.0 GB)
    - [ ] Qwen2.5-3B-Instruct (~6.0 GB)
    - [ ] Qwen2.5-7B-Instruct (~14.0 GB)
    - [ ] Qwen2.5-14B-Instruct (~28.0 GB)
    - [ ] Qwen2.5-32B-Instruct (~64.0 GB, for high-tier SAS)
    - [ ] Qwen2.5-72B-Instruct (~144.0 GB, for high-tier SAS)
  - [ ] **Quantized weights for SAS evaluations** (INT8, INT4-AWQ, 2-bit, 1-bit per tier config)
- [ ] Verify each model loads and runs a simple generation (smoke test)
- [ ] Measure and record the actual VRAM footprint of each model configuration
- [ ] Confirm all configurations fit within their target VRAM tier **without** host RAM offloading
- [ ] Choose final model family (Qwen 2.5 or Llama 3.1/3.2 or both)
- [ ] Document exact model versions and HuggingFace repo IDs in `configs/models/`

### 4.4 — Benchmark Dataset Preparation
- [ ] Download and preprocess FRAMES dataset
  - [ ] Verify data format, question structure, and ground-truth labels
  - [ ] Create a standardized data loader in `src/benchmarks/datasets/`
- [ ] Download and preprocess GSM8K
  - [ ] Parse ground-truth numerical answers
  - [ ] Implement symbolic answer extraction (regex for `####` format)
- [ ] Download and preprocess MATH-500
  - [ ] Implement `sympy`-based symbolic equivalence checker
- [ ] Download and preprocess GPQA Diamond
  - [ ] Verify multiple-choice format and answer parsing
- [ ] (Optional) Download and preprocess GAIA
  - [ ] Set up tool sandboxes (Python interpreter, web search stub)
- [ ] Create a unified `BenchmarkRunner` class that takes a config and runs any dataset
- [ ] Write a validation script that loads each dataset and prints sample counts, format checks

---

## Phase 5: Core Implementation
*Build the agent systems, inference engines, and measurement instrumentation.*

### 5.1 — Inference Engine
- [ ] Implement `src/inference/engine.py` — unified interface for model loading & generation
  - [ ] Support loading models with different quantization levels (FP16, INT8, INT4, 3-bit)
  - [ ] Support multiple concurrent models in the same GPU (for MAS)
  - [ ] Expose generation parameters (temperature, top-p, max tokens, stop tokens)
  - [ ] Handle batched vs. sequential inference
- [ ] Implement `src/inference/quantization.py` — quantization config loaders
  - [ ] AWQ loader (autoawq)
  - [ ] GPTQ loader (auto-gptq)
  - [ ] bitsandbytes INT8/INT4 loader
  - [ ] Record quantization metadata (bit-width, group size, calibration dataset)

### 5.2 — Agent Implementations
- [ ] Implement `src/agents/base.py` — Agent abstract base class
  - [ ] Define interface: `__init__(model, tools, system_prompt)`, `step(observation) → action`, `run(task) → result`
  - [ ] Built-in conversation history management
  - [ ] Token counting per turn
- [ ] Implement `src/agents/single_agent.py` — SAS implementation
  - [ ] Chain-of-Thought (CoT) prompting strategy
  - [ ] ReAct prompting strategy (for tool-use tasks)
  - [ ] Self-consistency / majority voting option
- [ ] Implement `src/agents/orchestrator.py` — Hierarchical MAS orchestrator
  - [ ] Task decomposition logic (break task into sub-tasks)
  - [ ] Worker dispatch and result aggregation
  - [ ] Error handling and retry logic
- [ ] Implement `src/agents/worker.py` — Specialized MAS worker
  - [ ] Tool-use worker (executes tools on behalf of orchestrator)
  - [ ] Reasoning worker (answers sub-questions)
  - [ ] Verification worker (checks answers for correctness)
- [ ] Implement `src/agents/debate.py` — Peer debate / reflection protocol
  - [ ] Round-robin debate with configurable rounds
  - [ ] Convergence detection (agents agree → stop early)
  - [ ] Final answer extraction after debate
- [ ] Implement sequential pipeline topology (Decompose → Execute → Verify)

### 5.3 — Profiling & Measurement Instrumentation
- [ ] Implement `src/profiling/memory_tracker.py`
  - [ ] Track peak resident VRAM via `torch.cuda.max_memory_allocated()`
  - [ ] Track allocated vs. reserved memory at each agent step
  - [ ] Log memory snapshots at configurable intervals
  - [ ] Verify VRAM residency stays within budget tier (raise alert if exceeded)
- [ ] Implement `src/profiling/token_tracker.py`
  - [ ] Count prompt tokens, completion tokens, and inter-agent communication tokens separately
  - [ ] Track total tokens per query, per agent, per turn
  - [ ] Compute token overhead ratio (communication tokens / total tokens)
- [ ] Implement latency tracking
  - [ ] Wall-clock time per query (end-to-end)
  - [ ] Time-to-first-token (TTFT)
  - [ ] Per-agent step latency

### 5.4 — Evaluation Harness
- [ ] Implement `src/benchmarks/runner.py` — unified evaluation harness
  - [ ] Accept a system config (SAS or MAS) + benchmark config → run all samples
  - [ ] Save raw outputs (model responses, intermediate agent traces, token counts, memory logs)
  - [ ] Compute Exact Match accuracy
  - [ ] Handle edge cases (timeouts, OOM, malformed outputs)
- [ ] Implement answer extraction and normalization
  - [ ] Numerical answer extraction for GSM8K
  - [ ] Symbolic equivalence for MATH-500 (via sympy)
  - [ ] Multiple-choice answer extraction for GPQA Diamond
  - [ ] Multi-hop answer matching for FRAMES
- [ ] Implement logging and experiment tracking
  - [ ] Save configs, git commit hash, random seeds, and all hyperparameters per run
  - [ ] Output structured JSON results files to `experiments/`
  - [ ] Create a run index / manifest for all completed experiments

---

## Phase 6: Pilot Experiments & Smoke Tests
*Validate the pipeline end-to-end on small subsets before committing to full runs.*

### 6.1 — Single-Model Smoke Tests
- [ ] Run SAS (e.g., 7B @ INT8) on 10 samples of GSM8K — verify answer extraction works
- [ ] Run SAS on 10 samples of FRAMES — verify multi-hop output parsing
- [ ] Run SAS on 10 samples of GPQA Diamond — verify MCQ answer extraction
- [ ] Confirm VRAM measurements are recording correctly
- [ ] Confirm token counts match expectations

### 6.2 — Multi-Agent Smoke Tests
- [ ] Run Hierarchical MAS (orchestrator + 2 workers) on 10 GSM8K samples
  - [ ] Verify orchestrator correctly decomposes and dispatches
  - [ ] Verify workers return structured answers
  - [ ] Verify aggregation produces a final answer
- [ ] Run Peer Debate MAS on 10 GSM8K samples
  - [ ] Verify debate rounds proceed correctly
  - [ ] Verify convergence detection works
- [ ] Confirm all agents fit in target VRAM simultaneously
- [ ] Inspect inter-agent communication traces for sanity

### 6.3 — Pipeline Validation
- [ ] Run a mini-experiment: 1 SAS config vs. 1 MAS config on 50 samples of 1 benchmark
- [ ] Verify end-to-end: config loading → model loading → inference → answer extraction → metric computation → results file saved
- [ ] Verify McNemar's test computation on the paired results
- [ ] Verify memory and token efficiency metrics ($\eta_M$, $\eta_T$) compute correctly
- [ ] Fix any bugs, edge cases, or crashes discovered during pilot

---

## Phase 7: Full Experimentation & Data Collection
*Run all planned 2×2 factorial conditions systematically across all 15 memory tiers under MUPP ($\ge 95\%$ memory saturation).*

### 7.1 — Cell A: Full SAS-FP16 Baseline Runs (Control Anchor)
- [ ] Evaluate SAS-FP16 across all 15 tiers on FRAMES, GSM8K, MATH-500, GPQA Diamond (≥ 3 seeds)
- [ ] Record: Accuracy, peak VRAM, token counts, latency, raw traces

### 7.2 — Cell B: Full SAS-Quant Runs (Scaled Quantized Generalist)
- [ ] Evaluate Saturating SAS-Quant across all 15 tiers on all benchmarks (≥ 3 seeds)
- [ ] Evaluate 5-level quantization sweep (FP16, INT8, INT4-AWQ, 2-bit, 1-bit) for degradation curve analysis

### 7.3 — Cell C: Full MAS-FP16 Runs (Original Native Precision MAS)
- [ ] **Hierarchical MAS (FP16)** across all 15 tiers
- [ ] **Peer Debate MAS (FP16)** across all 15 tiers
- [ ] **Sequential Pipeline MAS (FP16)** across all 15 tiers
- [ ] **AHDS MAS (FP16)** across all 15 tiers

### 7.4 — Cell D: Full MAS-Quant Runs (NEW: Larger Quantized Sub-Agents)
- [ ] **Tier 1 (4 GB)**: MAS-Q-4G (3B @ INT4 orch + 1.5B @ INT8 worker) on all benchmarks
- [ ] **Tier 2 (6 GB)**: MAS-Q-6G (7B @ INT4 orch + 1.5B @ INT8 worker) on all benchmarks
- [ ] **Tier 3 (8 GB)**: MAS-Q-8G (7B @ INT4 orch + 7B @ INT4 worker) on all benchmarks
- [ ] **Tier 4 (10 GB)**: MAS-Q-10G (14B @ INT4 orch + 1.5B @ INT8 worker) on all benchmarks
- [ ] **Tier 5 (12 GB)**: MAS-Q-12G (14B @ INT4 orch + 3B @ INT8 worker) on all benchmarks
- [ ] **Tier 6 (14 GB)**: MAS-Q-14G (14B @ INT4 orch + 7B @ INT4 worker + 1.5B @ INT8 verifier) on all benchmarks
- [ ] **Tier 7 (16 GB)**: MAS-Q-16G (two 14B @ INT4 models) on all benchmarks
- [ ] **Tier 8 (18 GB)**: MAS-Q-18G (14B @ INT8 orch + 3B @ INT8 worker) on all benchmarks
- [ ] **Tier 9 (20 GB)**: MAS-Q-20G (14B @ INT8 orch + 7B @ INT4 worker + 1.5B @ INT8 verifier) on all benchmarks
- [ ] **Tier 10 (22 GB)**: MAS-Q-22G (14B @ INT8 orch + 7B @ INT8 worker) on all benchmarks
- [ ] **Tier 11 (24 GB)**: MAS-Q-24G (32B @ INT4 orch + 7B @ INT8 worker) on all benchmarks
- [ ] **Tier 12 (26 GB)**: MAS-Q-26G (32B @ INT4 orch + 7B @ INT8 worker + 1.5B @ INT8 verifier) on all benchmarks
- [ ] **Tier 13 (28 GB)**: MAS-Q-28G (32B @ INT4 orch + 7B @ INT8 worker + 3B @ INT8 verifier) on all benchmarks
- [ ] **Tier 14 (30 GB)**: MAS-Q-30G (two 14B @ INT8 models) on all benchmarks
- [ ] **Tier 15 (32 GB)**: MAS-Q-32G (32B @ INT4 orch + 14B @ INT4 worker + 7B @ INT4 verifier) on all benchmarks

### 7.5 — Factorial Control Experiments & Ablations
- [ ] Control 1 (A vs. B): Quantization gain in single models (Bench360 replication)
- [ ] Control 2 (C vs. B): Native MAS vs. Quantized SAS (Original Agere hypothesis)
- [ ] Control 3 (D vs. A): Quantized MAS vs. Native SAS
- [ ] Control 4 (D vs. B): Quantized MAS vs. Quantized SAS
- [ ] Control 5 (D vs. C): Quantization effect inside MAS vs. inside SAS (The Interaction Test)
- [ ] Ablation: AHDS with/without structured JSON schemas (P1, P2)
- [ ] Ablation: AHDS confidence threshold $\tau$ sensitivity (0.3, 0.5, 0.7, 0.9)
- [ ] Ablation: AHDS with/without PagedAttention prefix KV sharing (P6)

### 7.6 — Data Management
- [ ] Back up all raw experiment outputs to secondary storage
- [ ] Create an experiment manifest cataloging every run with config hash, date, seed, and results
- [ ] Verify no runs are missing or incomplete

---

## Phase 8: Analysis, Visualization & Interpretation
*Process raw data into insights, statistical tests, and publication-ready figures.*

### 8.1 — Metric Aggregation
- [ ] Implement `src/analysis/parse_results.py`
  - [ ] Parse all raw result JSON files from `experiments/`
  - [ ] Compute per-condition: mean accuracy, std, 95% CI (bootstrap)
  - [ ] Compute $\eta_M$ and $\eta_T$ for every configuration
  - [ ] Output a master results table (CSV and LaTeX-formatted)

### 8.2 — Statistical Significance Testing & Factorial ANOVA
- [ ] Compute **Two-Way Factorial ANOVA** for the $2 \times 2$ design (Architecture $\times$ Compression):
  - [ ] Test main effect of Architecture ($F_{\text{arch}}$, $p$-value)
  - [ ] Test main effect of Compression ($F_{\text{comp}}$, $p$-value)
  - [ ] **Test Interaction Term ($F_{\text{inter}}$, $p$-value)**: determine whether $(\alpha\beta)_{ij} \neq 0$
  - [ ] Compute empirical difference-in-differences estimator $\widehat{\Delta}_{\text{interaction}} = (\bar{y}_D - \bar{y}_C) - (\bar{y}_B - \bar{y}_A)$
  - [ ] Compute paired bootstrap 95% confidence interval on $\Delta_{\text{interaction}}$ ($B = 10,000$ iterations)
- [ ] Compute McNemar's $\chi^2$ test with continuity correction for all pairwise cell comparisons (A vs B, C vs B, D vs A, D vs B, D vs C)
- [ ] Flag statistically significant transitions ($p < 0.05$) across the 15 tiers
- [ ] Build master statistical significance table

### 8.3 — Phase Boundary & Crossover Analysis
- [ ] Compute $\Delta(\theta) = \text{Score}_{\text{MAS}}(\theta) - \text{Score}_{\text{SAS}}(\theta)$ across task complexity bins
- [ ] Estimate the crossover point $\theta^*$ where $\Delta(\theta^*) = 0$
- [ ] Test whether $\theta^*$ shifts predictably with VRAM tier

### 8.4 — Pareto Frontier Analysis
- [ ] Plot Pareto frontiers: Accuracy vs. VRAM for each benchmark
- [ ] Plot Pareto frontiers: Accuracy vs. Total Tokens for each benchmark
- [ ] Plot Pareto frontiers: Accuracy vs. Latency for each benchmark
- [ ] Identify which systems are Pareto-dominated and which are Pareto-optimal

### 8.5 — Publication-Ready Visualizations
- [ ] Implement `src/analysis/plot_tradeoffs.py`
- [ ] **Table 1**: Main results table (Accuracy across all tiers × benchmarks × systems)
- [ ] **Figure 1**: Bar chart / grouped bar — SAS vs. MAS accuracy per benchmark per tier
- [ ] **Figure 2**: Pareto frontier plot (Accuracy vs. VRAM)
- [ ] **Figure 3**: Phase boundary / crossover plot ($\Delta(\theta)$ vs. task complexity)
- [ ] **Figure 4**: Token efficiency comparison ($\eta_T$) across systems
- [ ] **Figure 5**: Memory breakdown (weights + KV-cache + runtime) stacked bar per system
- [ ] **Figure 6**: Ablation summary (radar chart or small multiples)
- [ ] Export all figures as PDF/SVG for LaTeX inclusion
- [ ] Ensure all plots use consistent styling, fonts, and color palettes

### 8.6 — Qualitative Error Analysis
- [ ] Sample 20–30 failure cases from each system (SAS and MAS)
- [ ] Categorize failures using Cemri et al.'s MAST taxonomy:
  - [ ] Specification & Planning failures
  - [ ] Inter-agent misalignment / context collapse
  - [ ] Quantization-induced errors (attention head noise, perplexity spikes)
  - [ ] Tool misuse or hallucinated tool calls
  - [ ] Reasoning chain breaks (arithmetic errors, logic gaps)
- [ ] Write up 3–5 illustrative case studies with full agent traces
- [ ] Identify systematic failure patterns (e.g., "MAS always fails on questions requiring > 5 reasoning hops")

---

## Phase 9: Paper Writing & Submission
*Turn findings into a publication-quality manuscript.*

### 9.1 — Paper Skeleton
- [ ] Create `paper/` directory with LaTeX project structure
  - [ ] `main.tex`, `references.bib`, `figures/`, `tables/`
- [ ] Choose target venue and format (NeurIPS / ICLR / ACL / EMNLP)
- [ ] Set up LaTeX template for the target venue
- [ ] Write the section skeleton (all section headers, no content yet)

### 9.2 — Abstract (write last, but draft early)
- [ ] Draft v1 abstract (problem → gap → method → key result → implication, ≤ 250 words)

### 9.3 — Section 1: Introduction
- [ ] Paragraph 1: The general problem (MAS vs. SAS debate)
- [ ] Paragraph 2: The specific gap (VRAM as hard ceiling, not tokens/FLOPs)
- [ ] Paragraph 3: What we do (first memory-equated evaluation)
- [ ] Paragraph 4: Summary of key findings and contributions
- [ ] Contributions bullet list (4 items, matching README claims)

### 9.4 — Section 2: Related Work
- [ ] Subsection: Multi-Agent vs. Single-Agent Scaling (Tran & Kiela, Żywot, Kim, MoA, MAST)
- [ ] Subsection: Budget-Normalized LLM Evaluation (Wang EMNLP 2024, Bench360, Token Economies)
- [ ] Subsection: Post-Training Quantization (AWQ, QuaRot, AQLM, bitsandbytes)
- [ ] Subsection: MAS Topologies & Frameworks (MetaGPT, AgentVerse, ChatEval, DyLAN)
- [ ] Position our work clearly relative to all baselines — what we do that nobody else did

### 9.5 — Section 3: Methodology
- [ ] Formalize the memory-equated evaluation framework ($M_{\text{budget}}$)
- [ ] Describe each system configuration (SAS variants, MAS topologies) with architecture diagrams
- [ ] Describe benchmark selection rationale
- [ ] Describe evaluation metrics with mathematical definitions
- [ ] Describe the statistical testing protocol (McNemar, bootstrap CIs)

### 9.6 — Section 4: Experimental Setup
- [ ] Hardware and software specifications
- [ ] Exact model versions, quantization configs, and HuggingFace model IDs
- [ ] Dataset sizes, splits, and preprocessing steps
- [ ] Hyperparameters (temperature, top-p, max tokens, number of debate rounds, etc.)
- [ ] Number of seeds and total compute used

### 9.7 — Section 5: Results
- [ ] Main results table and discussion
- [ ] Per-benchmark analysis (where SAS wins, where MAS wins, and why)
- [ ] Phase boundary and crossover findings
- [ ] Efficiency analysis ($\eta_M$, $\eta_T$, latency)
- [ ] Ablation findings
- [ ] Statistical significance reporting

### 9.8 — Section 6: Discussion
- [ ] Interpret the crossover threshold — practical deployment guidance
- [ ] Connect findings back to the $q_s$ inequality (does the macro-capacity hypothesis hold?)
- [ ] Address when practitioners should choose SAS vs. MAS
- [ ] Discuss surprising or counter-intuitive findings

### 9.9 — Section 7: Limitations & Future Work
- [ ] Model family scope (only Qwen / only Llama — does it generalize?)
- [ ] Benchmark scope (only 3–4 benchmarks — broader coverage needed?)
- [ ] Hardware scope (only tested on specific VRAM tiers)
- [ ] No training-time interventions (only post-training quantization)
- [ ] Future: dynamic VRAM allocation, model swapping, heterogeneous agent teams

### 9.10 — Section 8: Conclusion
- [ ] Restate the research question
- [ ] Summarize the answer with the most compelling quantitative evidence
- [ ] End with the practical takeaway for practitioners

### 9.11 — Supplementary Material & Reproducibility
- [ ] Full per-question results tables
- [ ] All agent conversation traces for case studies
- [ ] Complete hyperparameter tables
- [ ] Code and data availability statement
- [ ] Open-source the repository with README, configs, and evaluation scripts

### 9.12 — Review & Submission
- [ ] Internal review: re-read the entire paper for logical coherence
- [ ] Proofread for grammar, spelling, and formatting
- [ ] Verify all numbers in tables match the raw experiment data
- [ ] Verify all figures render correctly in the compiled PDF
- [ ] Check reference formatting and completeness
- [ ] Submit to target venue
- [ ] Prepare a 1-page rebuttal template for reviewer responses

---

## Progress Summary

| Phase | Status | Key Deliverable |
| :--- | :---: | :--- |
| 1. Problem Definition | ✅ Done | `README.md` with RQs, gaps, contributions |
| 2. Literature Review | 🟡 ~95% | 35 summaries + 5 thematic docs + master synthesis |
| 3. Experimental Design | 🟡 ~95% | 2×2 Factorial Design across 15 tiers (Cells A, B, C, D) + 45 YAML configs (15 hardware tiers, 15 Cell D quant MAS, 15 AHDS) + Interaction Term (Two-Way ANOVA); needs protocol doc |
| 4. Environment Setup | ⬜ Not Started | Repository scaffolding, deps, model downloads |
| 5. Core Implementation | ⬜ Not Started | Agent code, inference engine, profiling, eval harness |
| 6. Pilot Experiments | ⬜ Not Started | Smoke tests on 10–50 samples |
| 7. Full Experiments | ⬜ Not Started | All tiers × topologies × benchmarks × seeds |
| 8. Analysis & Figures | ⬜ Not Started | Statistics, plots, error analysis |
| 9. Paper Writing | ⬜ Not Started | Full manuscript for venue submission |
