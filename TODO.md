# Project Agere — Research Roadmap & TODO

> **Core RQ:** Under a fixed resident VRAM memory budget $M$, can a MAS of smaller high-precision models outperform a SAS using a larger, aggressively quantized model?

---

## Phase 1: Problem Definition & Motivation
*Establish what you're studying, why it matters, and scope the contribution.*

- [x] Identify the core architectural dilemma (SAS vs. MAS under memory parity)
- [x] Articulate why VRAM is a hard ceiling vs. soft token/FLOP budgets
- [x] Define the 5 research gaps from prior work
  - [x] Gap 1: Compute-budget vs. physical memory disconnect
  - [x] Gap 2: Cross-silo disconnect (quantization ↔ agent collaboration)
  - [x] Gap 3: Confounded baselines in small-agent tool research
  - [x] Gap 4: Micro-to-macro capacity penalty analogy ($q_s$ inequality)
  - [x] Gap 5: Task-type moderator spectrum (no universal winner)
- [x] Frame the real-world application gap (local deployment dilemma: RTX 4090 / M-series / RTX 4060)
- [x] Define the 4 core scientific contributions
- [ ] Finalize and commit the formal research questions (RQ1, RQ2, RQ3) as a standalone document
  - [ ] RQ1: Memory-equated accuracy comparison (SAS vs. MAS)
  - [ ] RQ2: Task-type phase boundary & crossover threshold $\theta^*$
  - [ ] RQ3: Memory allocation strategy (concentrated vs. distributed)
- [ ] Write explicit hypotheses (H1, H2, H3) with null hypotheses for each RQ

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

### 3.1 — Formalize Research Questions
- [ ] Write RQ1 precisely (memory-equated accuracy: SAS vs. MAS across tiers)
- [ ] Write RQ2 precisely (task-type phase boundary: at what task complexity $\theta^*$ does MAS overtake SAS?)
- [ ] Write RQ3 precisely (memory allocation: concentrated single model vs. orchestrator + workers vs. peer debate)
- [ ] Review RQs for testability — each must be answerable with a single experiment and a clear metric

### 3.2 — Formulate Hypotheses
- [ ] H1: Under memory parity, SAS (quantized large) outperforms MAS on knowledge-dense, multi-hop reasoning tasks (FRAMES, GPQA Diamond)
- [ ] H2: Under memory parity, MAS outperforms SAS on tool-intensive, step-decomposable tasks (GAIA)
- [ ] H3: The crossover threshold $\theta^*$ shifts toward MAS as tool reliance increases, and toward SAS as reasoning depth increases
- [ ] Write null hypotheses for each (H0₁, H0₂, H0₃)

### 3.3 — Experimental Design Matrix
- [x] Define the 3 VRAM budget tiers (8 GB, 16 GB, 24 GB)
- [x] Define the residency formula: $M_{\text{total}} = M_{\text{weights}} + M_{\text{KV-cache}} + M_{\text{runtime}} \le M_{\text{budget}}$
- [x] Design the SAS configurations per tier (model + quant level)
- [x] Design the MAS configurations per tier (topology + model mix)
- [x] Select MAS topologies to test (Hierarchical, Peer Debate, Sequential Pipeline)
- [x] Select primary benchmarks (FRAMES, GSM8K/MATH-500, GPQA Diamond)
- [ ] Decide secondary/stretch benchmarks (GAIA for tool-use, MMLU-Pro for breadth)
- [x] Define all evaluation metrics ($\text{Acc}$, $\eta_M$, $\eta_T$, McNemar's $\chi^2$, Pareto dominance)
- [ ] Determine the number of seeds / repetitions per experiment (recommend ≥ 3 seeds for significance)
- [ ] Design control experiments
  - [ ] Control 1: Same model, same quant, SAS vs. MAS (isolate collaboration effect from model size)
  - [ ] Control 2: Same model count, different topologies (isolate topology effect)
  - [ ] Control 3: Tool-equipped SAS vs. tool-equipped MAS (eliminate tool confound from Żywot et al.)
- [ ] Write the full experimental protocol as a standalone `EXPERIMENT_PROTOCOL.md` document
- [ ] Finalize the hardware you'll run on (local GPU? cloud? RunPod?)

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
- [ ] Download target model weights for each tier:
  - [ ] **8 GB tier**: 14B-INT4 (or 7B-INT8) for SAS; 3B-FP16 × 2 for MAS
  - [ ] **16 GB tier**: 32B-INT4 (or 14B-INT8) for SAS; 7B-INT8 × 2 (or 7B + 3B × 2) for MAS
  - [ ] **24 GB tier**: 70B-INT4/3-bit (or 32B-INT8) for SAS; 8B-INT8 × 3 (or 14B + 7B × 2) for MAS
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
*Run all planned experiment conditions systematically.*

### 7.1 — Full SAS Baseline Runs
- [ ] **8 GB tier SAS** on all benchmarks (FRAMES, GSM8K, MATH-500, GPQA Diamond)
  - [ ] Run with ≥ 3 random seeds
  - [ ] Record: accuracy, VRAM peak, token counts, latency, raw outputs
- [ ] **16 GB tier SAS** on all benchmarks
  - [ ] Run with ≥ 3 random seeds
  - [ ] Record all metrics
- [ ] **24 GB tier SAS** on all benchmarks
  - [ ] Run with ≥ 3 random seeds
  - [ ] Record all metrics

### 7.2 — Full MAS Runs (Hierarchical Topology)
- [ ] **8 GB tier Hierarchical MAS** on all benchmarks
- [ ] **16 GB tier Hierarchical MAS** on all benchmarks
- [ ] **24 GB tier Hierarchical MAS** on all benchmarks

### 7.3 — Full MAS Runs (Peer Debate Topology)
- [ ] **8 GB tier Debate MAS** on all benchmarks
- [ ] **16 GB tier Debate MAS** on all benchmarks
- [ ] **24 GB tier Debate MAS** on all benchmarks

### 7.4 — Full MAS Runs (Sequential Pipeline Topology)
- [ ] **8 GB tier Pipeline MAS** on all benchmarks
- [ ] **16 GB tier Pipeline MAS** on all benchmarks
- [ ] **24 GB tier Pipeline MAS** on all benchmarks

### 7.5 — Control Experiments
- [ ] Control 1: Same model, same quant, SAS vs. MAS (isolate collaboration effect)
- [ ] Control 2: Same model count, different topologies (isolate topology effect)
- [ ] Control 3: Tool-equipped SAS vs. tool-equipped MAS (eliminate tool confound)

### 7.6 — Ablation Studies
- [ ] Ablation: MAS without the verification/critic agent — does quality drop?
- [ ] Ablation: MAS with 2 agents vs. 3 agents vs. 4 agents (at same VRAM)
- [ ] Ablation: SAS at INT4 vs. INT8 vs. 3-bit (quantization severity sweep)
- [ ] Ablation: MAS debate rounds (1 round vs. 2 vs. 3 vs. 5) — diminishing returns?
- [ ] Ablation: Orchestrator model size (small orchestrator + big workers vs. big orchestrator + small workers)

### 7.7 — Data Management
- [ ] Back up all raw experiment outputs to a secondary location
- [ ] Create an experiment manifest (CSV/JSON) cataloging every run with config hash, date, seed, and result summary
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

### 8.2 — Statistical Significance Testing
- [ ] Compute McNemar's $\chi^2$ test for every SAS-vs-MAS pair on the same benchmark and tier
- [ ] Compute paired bootstrap 95% confidence intervals ($B = 1000$ iterations)
- [ ] Flag which comparisons achieve $p < 0.05$ and which do not
- [ ] Build a summary significance table

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
| 3. Experimental Design | 🟡 ~60% | Design matrix drafted in README; needs formal protocol doc |
| 4. Environment Setup | ⬜ Not Started | Repository scaffolding, deps, model downloads |
| 5. Core Implementation | ⬜ Not Started | Agent code, inference engine, profiling, eval harness |
| 6. Pilot Experiments | ⬜ Not Started | Smoke tests on 10–50 samples |
| 7. Full Experiments | ⬜ Not Started | All tiers × topologies × benchmarks × seeds |
| 8. Analysis & Figures | ⬜ Not Started | Statistics, plots, error analysis |
| 9. Paper Writing | ⬜ Not Started | Full manuscript for venue submission |
