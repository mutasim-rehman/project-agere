# 01. Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets

> **Authors:** Dat Tran, Douwe Kiela  
> **Affiliation & Venue:** arXiv:2604.02460 (Stanford University)  
> **Publication Year:** 2026  
> **Local PDF Source:** [`01_Tran_2026_Single_Agent_LLMs_Outperform_Multi_Agent.pdf`](../../sources/01_Tran_2026_Single_Agent_LLMs_Outperform_Multi_Agent.pdf)  
> **Role in Our Study:** **Primary Base Paper Candidate (Thinking Token Normalization Template)**

---

## 1. Executive Summary & Core Premise
This paper provides a rigorous empirical and information-theoretic challenge to the prevailing belief that Multi-Agent Systems (MAS) naturally surpass Single-Agent Systems (SAS) on complex reasoning. By strictly controlling the computational thinking token budget—measuring combined internal reasoning and dialogue tokens—the authors demonstrate across Qwen3, DeepSeek-R1-Distill, and Gemini 2.5 that a single agent consistently matches or outperforms multi-agent debate, ensemble, and sequential setups on multi-hop QA.

---

## 2. Research Motivation & Problem Formulation
Prior literature celebrated massive gains from multi-agent collaboration (e.g., Mixture-of-Agents, AgentVerse), but these studies conflated multi-agent architectural synergy with increased test-time compute. When an MAS generates thousands of intermediate communication tokens, it spends more inference compute than a zero-shot or short-chain single agent. The authors ask: Does multi-agent interaction provide inherent algorithmic synergy, or is it merely an expensive way to spend more test-time tokens?

---

## 3. Technical Architecture & Methodology
The study investigates three dominant MAS topologies alongside SAS:
1. **Single-Agent System (SAS):** Standard autoregressive generation using extended Chain-of-Thought (CoT) reasoning budgets.
2. **Sequential MAS:** Linear pipeline where Agent A generates intermediate rationales that are passed to Agent B.
3. **Debate MAS:** Multi-round iterative peer review where multiple agent personas critique peer answers and revise conclusions.
4. **Ensemble MAS:** Parallel independent generations aggregated via majority consensus.

**The Equal Budget Control Mechanism:**
Total test-time thinking budget $T$ is fixed. For SAS, $T$ tokens are allocated to the single model's reasoning trace. For MAS with $N$ agents over $R$ rounds, the per-agent generation is capped such that $\sum_{i=1}^N \sum_{r=1}^R t_{i,r} = T$. Experiments are run across model families (Qwen3, DeepSeek-R1-Distill-Llama, Gemini 2.5) on multi-hop reasoning benchmarks.

---

## 4. Experimental Framework & Setup
- **Benchmarks:** FRAMES (Factuality, Retrieval, and Multi-hop Evaluation), MuSiQue, and HotpotQA.
- **Controlled Parameter:** Thinking token budget $T \in [512, 1024, 2048, 4096, 8192]$.
- **Ablations:** Context truncation thresholds, API budget enforcement quirks (revealing Gemini 2.5 token artifacts), and prompt formatting variance.

---

## 5. Key Quantitative Findings & Breakthroughs
- Under equal thinking token budgets, SAS matches or outperforms MAS on over 82% of multi-hop evaluation splits.
- Multi-agent debate exhibits severe diminishing returns: as debate rounds increase, error cascading and consensus drift cause accuracy degradation.
- Information-theoretic proof: via the Data Processing Inequality ($I(X; Z) \le I(X; Y)$), every inter-agent conversational handoff without external tool injection is lossy, progressively eroding context fidelity.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Exclusively restricted to closed-book and retrieved-context multi-hop QA; does not examine tool execution (e.g., code sandboxes, web browsing).
- Holds base model parameter size constant across agents; does not evaluate whether heterogeneous model teams or quantized scale shifts the outcome.
- Treats compute (tokens) as the only resource axis, ignoring physical GPU resident VRAM constraints.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Tran & Kiela is our **direct structural foundation**. We adopt their SAS vs. MAS comparative topology (sequential, debate, ensemble) and evaluation methodology, but swap their controlled resource from **thinking token budget** to **physical GPU VRAM memory ($M$)**. Where they tested equal tokens with identical model sizes, we test equal VRAM where the single agent spends freed memory on larger model scale via quantization (e.g., 1× 32B @ 4-bit vs. 2× 8B @ INT8 or 1× 8B + 2× 3B @ FP16).

---

## 8. Citation Utility & Key Takeaways
Cite in Section 1 (Introduction) and Section 2 (Related Work) as the definitive baseline establishing that compute-matched MAS does not beat SAS, framing our paper as extending this inquiry to the physical hardware memory boundary.
