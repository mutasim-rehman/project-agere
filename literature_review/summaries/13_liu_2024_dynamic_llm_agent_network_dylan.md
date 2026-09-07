# 13. Dynamic LLM-Agent Network: An LLM-Agent Collaboration Framework with Dynamic Architecture (DyLAN)

> **Authors:** Liu et al.  
> **Affiliation & Venue:** ICLR 2024  
> **Publication Year:** 2024  
> **Local PDF Source:** [`13_Liu_2024_Dynamic_LLM_Agent_Network_DyLAN.pdf`](../../sources/13_Liu_2024_Dynamic_LLM_Agent_Network_DyLAN.pdf)  
> **Role in Our Study:** **Dynamic Agent Pruning & Communication Token Efficiency**

---

## 1. Executive Summary & Core Premise
DyLAN introduces a dynamic multi-agent framework that measures agent contributions at each execution round and prunes inactive or redundant agents. It demonstrates that dynamic agent pruning reduces token consumption while improving overall task accuracy.

---

## 2. Research Motivation & Problem Formulation
Static multi-agent systems suffer from token explosion and distracting chatter because all agents participate in all rounds regardless of utility. DyLAN addresses this by dynamically adjusting the collaboration network at runtime.

---

## 3. Technical Architecture & Methodology
- Formulates an Agent Importance Score based on contribution to state advancement.
- Dynamically prunes lowest-ranked agents after each discussion round.
- Features an early stopping algorithm when agent consensus converges.

---

## 4. Experimental Framework & Setup
- Benchmarks: Arithmetic reasoning (GSM8K, SVAMP), Code generation (HumanEval), Multi-hop QA (HotpotQA).
- Measures accuracy versus token consumption Pareto efficiency.

---

## 5. Key Quantitative Findings & Breakthroughs
- Pruning ineffective agents cuts token overhead by 30–50% while improving reasoning accuracy by eliminating noisy distractions.
- Outperforms static multi-agent debate frameworks across all tested benchmarks.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Calculating agent importance requires additional evaluation passes.
- Assumes cloud API execution rather than local GPU memory scheduling.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Guides our strategies for trimming inter-agent communication overhead so our small-agent MAS configurations do not waste GPU memory on uninformative tokens.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 and Section 5 to discuss how communication pruning mitigates multi-agent coordination costs.
