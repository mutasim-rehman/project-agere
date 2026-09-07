# 15. Reasoning in Token Economies: Budget-Aware Evaluation of LLM Reasoning Strategies

> **Authors:** Junlin Wang, Siddhartha Jain, Dejiao Zhang, Baishakhi Ray, Varun Kumar, Ben Athiwaratkun  
> **Affiliation & Venue:** EMNLP 2024 (Main Conference)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`15_Wang_2024_Reasoning_in_Token_Economies_Budget_Aware.pdf`](../../sources/15_Wang_2024_Reasoning_in_Token_Economies_Budget_Aware.pdf)  
> **Role in Our Study:** **Methodological Template for Budget-Normalized Evaluation**

---

## 1. Executive Summary & Core Premise
A landmark EMNLP 2024 paper proving that many complex reasoning and agent strategies (multi-agent debate, Reflexion, Tree-of-Thoughts) do not outperform simpler baselines due to algorithmic superiority, but simply because they consume far more inference tokens. It establishes the paradigm of budget-aware evaluation.

---

## 2. Research Motivation & Problem Formulation
Traditional NLP evaluations measure accuracy while ignoring inference compute. Complex agent architectures spend 5× to 20× more tokens per query and claim superiority over simple single-turn prompts. The authors argue that this comparison is methodologically broken.

---

## 3. Technical Architecture & Methodology
- Normalizes all evaluation against fixed token budgets ($T \in [512, 8192]$).
- Evaluates Zero-shot, Few-shot CoT, Self-Consistency, Multi-Agent Debate, Reflexion, Tree-of-Thoughts.
- Measures accuracy as a function of total tokens spent per query.

---

## 4. Experimental Framework & Setup
- Models: Llama-2-70B, GPT-3.5-Turbo, Claude-2.
- Benchmarks: GSM8K, SVAMP, StrategyQA, ARC-Challenge.

---

## 5. Key Quantitative Findings & Breakthroughs
- When a single agent with self-consistency (repeated sampling) is given the same token budget as multi-agent debate, the single agent wins decisively.
- Complex strategies exhibit negative scaling beyond a certain token threshold, degrading performance.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Normalizes tokens only; does not consider physical GPU memory, VRAM residency, or model parameter scale.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Our **primary methodological inspiration**. We adopt Wang et al.'s exact principle—*'fair evaluation requires budget normalization'*—and apply it to physical GPU VRAM memory ($M$) instead of token count.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 1 and Section 3 as the definitive academic precedent for budget-normalized evaluation.
