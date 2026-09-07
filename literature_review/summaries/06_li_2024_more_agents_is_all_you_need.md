# 06. More Agents Is All You Need

> **Authors:** Junyou Li, Qin Zhang, Yangbin Yu, Qiang Fu, Deheng Ye  
> **Affiliation & Venue:** TMLR 2024 (Transactions on Machine Learning Research)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`06_Li_2024_More_Agents_Is_All_You_Need.pdf`](../../sources/06_Li_2024_More_Agents_Is_All_You_Need.pdf)  
> **Role in Our Study:** **Agent Ensemble Scaling Laws via Sampling-and-Voting**

---

## 1. Executive Summary & Core Premise
Published in TMLR 2024, this paper demonstrates that simply scaling the number of instantiated LLM agents via a sampling-and-voting methodology consistently improves reasoning accuracy across diverse tasks, with the magnitude of improvement strongly correlated with task difficulty.

---

## 2. Research Motivation & Problem Formulation
Complex multi-agent collaboration frameworks require bespoke prompt engineering, complex communication graphs, and prone-to-failure parsing logic. The authors investigate whether an extremely simple, uncoordinated ensemble scaling method (instantiating $N$ independent agents and taking a majority vote) can deliver competitive scaling behavior.

---

## 3. Technical Architecture & Methodology
- Instantiates $N$ identical or heterogeneous agents with query $q$.
- Agents independently generate reasoning paths and terminal answers.
- A consensus module aggregates votes to determine the winner.
- Explores hierarchical voting: using smaller models to filter and generate candidate sets, followed by higher-capacity models for final verification.

---

## 4. Experimental Framework & Setup
- Models: Llama-2-13B, Llama-2-70B, GPT-3.5-Turbo.
- Benchmarks: GSM8K, SVAMP, HumanEval, MMLU.
- Evaluates scaling behavior as $N$ increases from 1 to 20+.

---

## 5. Key Quantitative Findings & Breakthroughs
- Performance scales monotonically with the number of agents, exhibiting power-law improvements on complex problems.
- The benefit of adding agents is orthogonal to prompt strategy: stacking voting on top of CoT or Reflexion yields additive gains.
- Simple tasks saturate quickly (diminishing returns at $N=3$), while hard tasks continue improving up to $N=15+$.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Multiplying agent count multiplies inference compute and memory linear in $N$.
- Lacks collaborative specialization: all agents perform identical tasks rather than decomposing problems into specialized sub-roles.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Represents our **peer-ensemble baseline**. Under an equal memory budget (e.g., 16 GB), can 3 identical 7B models with voting beat a 32B 4-bit model? Li et al. provides the reference scaling law for this comparison.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 and Section 3 as the definitive reference for sampling-and-voting multi-agent scaling.
