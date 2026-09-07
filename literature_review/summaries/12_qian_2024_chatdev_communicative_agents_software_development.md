# 12. ChatDev: Communicative Agents for Software Development

> **Authors:** Chen Qian, Wei Liu, Hongzhang Liu, et al.  
> **Affiliation & Venue:** ACL 2024 (Long Papers)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`12_Qian_2024_ChatDev_Communicative_Agents_Software_Development.pdf`](../../sources/12_Qian_2024_ChatDev_Communicative_Agents_Software_Development.pdf)  
> **Role in Our Study:** **Sequential Pipeline MAS Architecture Baseline**

---

## 1. Executive Summary & Core Premise
Published in ACL 2024, ChatDev models a virtual software company that operates through a sequential chat chain. By decomposing the development lifecycle into Designing, Coding, Testing, and Documenting, pairs of specialized agents interact via multi-turn dialogue to complete granular tasks for under $1 in API costs.

---

## 2. Research Motivation & Problem Formulation
Monolithic LLMs struggle to maintain long-range coherence when asked to generate complex, multi-component programs from a single prompt. ChatDev tests whether sequential communicative decomposition across paired agents solves this limitation.

---

## 3. Technical Architecture & Methodology
- Sequential multi-stage pipeline: Designing $\to$ Coding $\to$ Testing $\to$ Documenting.
- 'Chat Chain' mechanism: Each phase contains paired communicative agents (e.g., CEO $\leftrightarrow$ CPO, Programmer $\leftrightarrow$ Reviewer).
- Incorporates self-reflection and peer-review loops at each stage.

---

## 4. Experimental Framework & Setup
- Evaluated across 70 custom software development scenarios.
- Measures software completeness, code executability, vulnerability rates, and manufacturing costs.

---

## 5. Key Quantitative Findings & Breakthroughs
- Successfully generates complete software applications in under 7 minutes for less than $1.00.
- Peer testing and review loops catch and fix over 70% of potential syntax and runtime bugs before final output.

---

## 6. Critical Limitations, Caveats & Failure Modes
- High wall-clock latency caused by sequential round-trip dialogues.
- Prone to context accumulation overhead across consecutive pipeline nodes.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Represents our **Sequential Pipeline MAS baseline** (Decompose $\to$ Execute $\to$ Verify), showing how sequential stages reduce single-agent context load.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 and Section 3 to establish peer-reviewed ACL 2024 precedence for sequential agent pipelines.
