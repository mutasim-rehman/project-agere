# 02. Can Small Agent Collaboration Beat a Single Big LLM?

> **Authors:** Agata Zywot, Xinyi Chen, Maarten de Rijke  
> **Affiliation & Venue:** arXiv:2601.11327 (University of Amsterdam, Preprint Under Review)  
> **Publication Year:** 2026  
> **Local PDF Source:** [`02_Zywot_2026_Can_Small_Agent_Collaboration_Beat_Single_Big_LLM.pdf`](../../sources/02_Zywot_2026_Can_Small_Agent_Collaboration_Beat_Single_Big_LLM.pdf)  
> **Role in Our Study:** **Primary Base Paper Candidate (Tool-Use & Small vs. Large Agent Architecture)**

---

## 1. Executive Summary & Core Premise
This paper evaluates whether collaborative multi-agent teams of smaller language models (4B–32B parameters) can surpass a single, substantially larger model on complex, real-world tasks requiring external tool use. Benchmarking on GAIA, the authors find that small agents equipped with external tools (web search, Python code interpreter, mind-mapping) and orchestrated hierarchically routinely outperform monolithic models that are up to 8× larger but lack tool augmentation.

---

## 2. Research Motivation & Problem Formulation
Deploying frontier monolithic models (32B–70B+) incurs prohibitive hardware costs, high inference latency, and severe environmental footprints. The authors explore whether task decomposition across specialized small models can democratize agentic AI, challenging the 'bigger is always better' dogma in practical deployment settings.

---

## 3. Technical Architecture & Methodology
The authors build an orchestrator-subagent architecture using the Qwen3 family (4B, 8B, 14B, 32B):
1. **Central Orchestrator:** Decomposes complex user goals, assigns tasks, schedules tool invocations, and synthesizes intermediate outputs.
2. **Specialized Worker Agents:** Equipped with dedicated toolkits—Searcher (web browsing), Coder (code sandbox), and Reasoner (logical planning).
3. **Monolithic Baselines:** Standalone single models operating at larger parameter scales.

The architecture tests asymmetrical scaling: varying the orchestrator size independently of worker sizes to measure where parameter capacity is most critical.

---

## 4. Experimental Framework & Setup
- **Benchmark:** GAIA (General AI Assistants benchmark, Levels 1, 2, and 3).
- **Model Family:** Qwen3 models across 4B, 8B, 14B, and 32B scales.
- **Ablation Studies:** Tool access on vs. off, orchestration topology (flat peer vs. hierarchical central), and sub-agent parameter variations.

---

## 5. Key Quantitative Findings & Breakthroughs
- A 4B agent team with tools outperforms a standalone 32B monolithic model without tools on GAIA Levels 1 and 2.
- Tool access is the dominant equalizing factor: small models with code execution and search bridge the reasoning gap against models 8× their size.
- Orchestrator capacity matters significantly more than worker capacity: upgrading the orchestrator from 4B to 14B produces a dramatic jump in success rate, whereas scaling workers yields marginal gains.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Does not control for concurrent resident VRAM: the multi-agent systems instantiate multiple distinct models without bounding total GPU memory.
- Does not test post-training quantization on the single large model baseline (e.g., comparing 4B MAS against 32B 4-bit in identical memory).
- GAIA evaluation relies heavily on external API reliability, introducing non-deterministic execution noise.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Provides our **alternative base architecture** for the tool-augmented arm. It proves that MAS superiority depends heavily on tool integration. Our research directly fills their missing gap by holding total resident VRAM constant and comparing their small-agent team against a quantized large model.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 and Section 4 to justify our hierarchical orchestrator-worker topology and to support our hypothesis that task type (tool-use vs. pure reasoning) acts as a moderator.
