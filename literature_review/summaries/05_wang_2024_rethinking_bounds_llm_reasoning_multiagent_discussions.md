# 05. Rethinking the Bounds of LLM Reasoning: Are Multi-Agent Discussions the Key?

> **Authors:** Qineng Wang, Zihao Wang, Ying Su, Hanghang Tong, Yangqiu Song  
> **Affiliation & Venue:** ACL 2024 (62nd Annual Meeting of the ACL, Long Papers)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`05_Wang_2024_Rethinking_Bounds_LLM_Reasoning_MultiAgent_Discussions.pdf`](../../sources/05_Wang_2024_Rethinking_Bounds_LLM_Reasoning_MultiAgent_Discussions.pdf)  
> **Role in Our Study:** **Single-Agent vs. Multi-Agent Debate Baseline & Prompting Rigor**

---

## 1. Executive Summary & Core Premise
A peer-reviewed ACL 2024 paper that critically evaluates multi-agent discussion and debate frameworks across a battery of reasoning tasks. The authors find that when single-agent systems are provided with standard prompt engineering (such as Chain-of-Thought and few-shot demonstrations), they match the performance of multi-agent discussions, with multi-agent debate only helping in unprompted, zero-shot scenarios.

---

## 2. Research Motivation & Problem Formulation
Multiple 2023 papers claimed multi-agent debate revolutionized reasoning. The authors questioned whether these improvements were genuine or merely an artifact of comparing rich multi-turn discussion prompts against severely under-prompted, zero-shot single-agent baselines.

---

## 3. Technical Architecture & Methodology
Systematic empirical comparison between:
- Single-Agent: Zero-shot CoT, Few-shot CoT, Self-Consistency.
- Multi-Agent Discussion: Round-robin discussion, simultaneous debate, hierarchical debate.
Investigates the internal communicative dynamics between agents: persuasion success rate, answer flipping rate, and confidence calibration.

---

## 4. Experimental Framework & Setup
- Models: ChatGPT (GPT-3.5-Turbo), GPT-4, Llama-2-70B.
- Benchmarks: GSM8K, MATH, StrategyQA, ARC-Challenge.
- Analysis of conformity: measuring how frequently agents abandon correct answers to conform with an incorrect majority.

---

## 5. Key Quantitative Findings & Breakthroughs
- In few-shot settings, single agents match multi-agent debate on almost all mathematical and logical tasks.
- Multi-agent debate provides a 5–10% boost *only* in zero-shot settings where the single agent lacks guidance.
- Identified the 'Conformity Trap': agents frequently exhibit sycophancy, agreeing with hallucinated peer claims.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Does not test tool-augmented agents.
- Evaluates closed-source proprietary APIs (GPT-4) and unquantized open models; does not explore physical memory or quantization.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Guarantees that our single-agent baseline is properly prompted with CoT and demonstrations, preventing our experiments from falling into the 'zero-shot baseline' trap that artificially inflated early MAS papers.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 and Section 3 to justify our Single-Agent baseline prompt design using fully peer-reviewed ACL 2024 evidence.
