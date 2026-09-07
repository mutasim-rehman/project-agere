# 18. ToolOrchestra: Collaborative and Cost-Aware Tool Orchestration for Language Agents

> **Authors:** Su et al.  
> **Affiliation & Venue:** arXiv:2411.08573 (November 2024)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`18_Su_2024_ToolOrchestra_Cost_Aware_Tool_Orchestration.pdf`](../../sources/18_Su_2024_ToolOrchestra_Cost_Aware_Tool_Orchestration.pdf)  
> **Role in Our Study:** **Cost-Constrained Multi-Agent Tool Orchestration**

---

## 1. Executive Summary & Core Premise
ToolOrchestra proposes an orchestration framework that dynamically schedules and routes tool calls under explicit constraints on monetary cost and latency budgets, proving that budget constraints eliminate redundant tool calls and improve accuracy.

---

## 2. Research Motivation & Problem Formulation
Language agents invoking external tools often issue redundant, expensive API calls. ToolOrchestra models tool calling under strict resource economics.

---

## 3. Technical Architecture & Methodology
- Cost-aware routing module estimating expected information gain against API invocation cost.
- Dynamically selects between cheap internal heuristics and expensive external tool calls.
- Benchmarked on ToolBench, API-Bank, and GAIA.

---

## 4. Experimental Framework & Setup
- Measures accuracy under varying per-query cost budgets.
- Evaluates tool selection precision and latency reduction.

---

## 5. Key Quantitative Findings & Breakthroughs
- Enforcing explicit budgets reduces API costs by up to 60% with zero loss in task success rate.
- Prevents agents from entering infinite tool-calling loops.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Focuses on monetary API costs rather than physical GPU VRAM.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Highlights how multi-agent tool execution must be budgeted, reinforcing our resource-constrained research paradigm.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 as precedent for resource-constrained agent tool orchestration.
