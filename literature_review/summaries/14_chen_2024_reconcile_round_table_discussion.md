# 14. ReConcile: Round-Table Discussion Improves Reasoning via Consensus

> **Authors:** Chen et al.  
> **Affiliation & Venue:** ACL 2024 (Main Conference)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`14_Chen_2024_ReConcile_Round_Table_Discussion.pdf`](../../sources/14_Chen_2024_ReConcile_Round_Table_Discussion.pdf)  
> **Role in Our Study:** **Heterogeneous Model Consensus & Round-Table Discussion**

---

## 1. Executive Summary & Core Premise
Accepted at ACL 2024, ReConcile introduces a round-table discussion protocol where heterogeneous LLM agents present reasoning paths, debate counterarguments, and adjust confidence levels to converge on an accurate consensus on complex reasoning problems.

---

## 2. Research Motivation & Problem Formulation
Single models often suffer from stubborn blind spots. ReConcile explores whether convening a 'round-table' of diverse models with different pre-training lineages can eliminate individual errors through calibrated consensus.

---

## 3. Technical Architecture & Methodology
- Multi-turn round-table protocol with confidence estimation.
- Agents attempt to convince peers using deductive arguments.
- Consensus mechanism: terminates when confidence-weighted unanimous agreement or stable majority is reached.

---

## 4. Experimental Framework & Setup
- Benchmarks: Mathematical reasoning (GSM8K, MATH), StrategyQA, CommonsenseQA.
- Compares homogeneous agent teams (same model) vs. heterogeneous agent teams (different model families).

---

## 5. Key Quantitative Findings & Breakthroughs
- Heterogeneous agent teams significantly outperform homogeneous teams, proving that model diversity is the key driver of consensus gains.
- Confidence-weighted voting prevents dominant but hallucinating models from misleading weaker peers.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Simultaneous deployment of multiple diverse model weights multiplies GPU VRAM residency requirements.
- Multi-round debates lead to quadratic context window expansion.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Provides a strong consensus baseline for reasoning tasks, highlighting why heterogeneous model deployment is difficult under single-GPU VRAM constraints.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 as a peer-reviewed ACL 2024 benchmark for multi-model consensus.
