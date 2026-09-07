# 10. ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate

> **Authors:** Chi-Min Chan, Weize Chen, Yusheng Su, et al.  
> **Affiliation & Venue:** ICLR 2024  
> **Publication Year:** 2024  
> **Local PDF Source:** [`10_Chan_2024_ChatEval_Multi_Agent_Debate.pdf`](../../sources/10_Chan_2024_ChatEval_Multi_Agent_Debate.pdf)  
> **Role in Our Study:** **Multi-Agent Peer Debate Protocol & Bias Mitigation**

---

## 1. Executive Summary & Core Premise
ChatEval introduces a multi-agent debate framework where diverse referee agents critique each other's assessments to achieve objective, human-aligned evaluations, effectively eliminating the position and verbosity biases inherent in single LLM evaluators.

---

## 2. Research Motivation & Problem Formulation
Using a single LLM as an evaluator ('LLM-as-a-judge') suffers from egocentric bias, verbosity bias, and prompt sensitivity. ChatEval hypothesizes that structured debate among specialized personas can triangulate objective ground truth.

---

## 3. Technical Architecture & Methodology
- Defines distinct critic personas (e.g., factual precision, fluency, completeness).
- Multi-turn debate rounds where agents present scores, justify critiques, and challenge peers.
- Consensus aggregation mechanism calculating final calibrated ratings.

---

## 4. Experimental Framework & Setup
- Benchmarks: Text summarization (CNN/DailyMail), Dialogue generation, Translation.
- Evaluates correlation against human expert rankings (Spearman $\rho$, Pearson $r$).

---

## 5. Key Quantitative Findings & Breakthroughs
- Multi-agent debate achieves significantly higher correlation with human judgment than single-model evaluators.
- Committees of smaller, cheaper models debating each other frequently match or exceed a single frontier model judge.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Multiplies token costs linearly with agent count and debate rounds.
- Risk of groupthink cascades when multiple models share common pre-training biases.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Supplies the specific prompt structure and critique-revision loops used in our Peer Debate MAS arm.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 3 to justify our multi-agent peer debate protocol.
