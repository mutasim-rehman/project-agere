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

## 2. Formal Experimental Design Matrix

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

### D. Benchmarks & Task Taxonomies
1. **Multi-Hop Reasoning:** MuSiQue, HotpotQA, or GSM8K / MATH-500.
2. **Tool-Use & Interactive Planning:** GAIA (subsets), ToolBench, or BFCL.
3. **Parametric Knowledge & Comprehension:** MMLU-Pro / ARC-Challenge.

### E. Measurement Metrics
- **Primary:** Task Accuracy / Success Rate.
- **Secondary (Efficiency & Profiling):**
  - Peak Resident VRAM (measured via `torch.cuda.max_memory_allocated()` or `pynvml`).
  - Total Token Footprint (Input, Output, Intermediate Agent Communication Tokens).
  - Wall-Clock Latency (TTFT: Time To First Token, end-to-end task completion time).
  - Quantization degradation curve vs. Coordination overhead cost.

---

## 3. Proposed Repository Architecture (`project-agere`)

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

## 4. Next Steps & Implementation Choices

Before we initialize the repository and build the experimental pipeline, please share your preferences on:

1. **Hardware Setup:** What GPU(s) or compute environment will you run experiments on (e.g., local RTX 3090/4090, 16 GB laptop GPU, cloud A100/H100, or RunPod/Colab)?
2. **Target Model Family:** Would you prefer **Qwen 2.5** (versatile, 0.5B to 72B), **Llama 3.1/3.2** (1B to 70B), or both?
3. **Inference Backend:** Would you prefer **vLLM** (best for serving multiple concurrent models/workers with paged KV cache) or standard **PyTorch + Hugging Face / bitsandbytes / AWQ** (simplest for exact VRAM allocation monitoring)?
4. **Primary Benchmark Focus:** Should we start prototyping the evaluation pipeline on **multi-hop reasoning** (e.g., GSM8K / MuSiQue) or **tool-agent benchmarks** (e.g., GAIA / ToolBench)?
