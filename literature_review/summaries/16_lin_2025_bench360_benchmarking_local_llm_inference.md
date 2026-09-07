# 16. Bench360: Benchmarking Local LLM Inference from 360 Degrees

> **Authors:** Lin et al.  
> **Affiliation & Venue:** arXiv:2511.16682 (Late 2025 / 2026)  
> **Publication Year:** 2025  
> **Local PDF Source:** [`16_Lin_2025_Bench360_Benchmarking_Local_LLM_Inference.pdf`](../../sources/16_Lin_2025_Bench360_Benchmarking_Local_LLM_Inference.pdf)  
> **Role in Our Study:** **Hardware & VRAM Memory Profiling Protocol**

---

## 1. Executive Summary & Core Premise
Bench360 provides a unified benchmarking platform that measures local LLM inference across hardware memory footprint (VRAM in GB), latency, throughput, energy consumption, and downstream task quality across multiple inference engines and quantization formats.

---

## 2. Research Motivation & Problem Formulation
Local inference research is fragmented: quantization papers report perplexity, systems papers report throughput, and NLP papers report accuracy. Bench360 bridges this divide with a standardized 360-degree profiling suite.

---

## 3. Technical Architecture & Methodology
- Profiles hardware metrics: Peak resident VRAM (GB), memory bandwidth, energy (Joules/query).
- Evaluates runtimes: vLLM, SGLang, TGI, LMDeploy, llama.cpp.
- Tests precision levels: FP16, INT8, INT4 (AWQ, GPTQ), 2-bit/3-bit across consumer and workstation GPUs.

---

## 4. Experimental Framework & Setup
- Workloads: Single-stream desktop, multi-turn chat, high-throughput batching.
- Evaluates functional accuracy across summarization, QA, and code.

---

## 5. Key Quantitative Findings & Breakthroughs
- Proves that no single model configuration is optimal across all hardware constraints.
- Shows that 4-bit quantization drastically reduces VRAM but introduces dequantization compute latency on memory-bandwidth-unconstrained GPUs.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Focuses on single-model serving rather than multi-agent collaborative workflows.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Provides our **exact VRAM measurement and hardware profiling protocol**, establishing how we enforce and report our 8 GB, 16 GB, and 24 GB hardware tiers.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 3 (Experimental Setup) to validate our hardware memory accounting methodology.
