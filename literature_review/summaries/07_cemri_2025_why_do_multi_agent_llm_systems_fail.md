# 07. Why Do Multi-Agent LLM Systems Fail?

> **Authors:** Mert Cemri et al.  
> **Affiliation & Venue:** arXiv:2503.13657 (March 2025)  
> **Publication Year:** 2025  
> **Local PDF Source:** [`07_Cemri_2025_Why_Do_Multi_Agent_LLM_Systems_Fail.pdf`](../../sources/07_Cemri_2025_Why_Do_Multi_Agent_LLM_Systems_Fail.pdf)  
> **Role in Our Study:** **Multi-Agent System Failure Taxonomy (MAST) & Error Analysis Framework**

---

## 1. Executive Summary & Core Premise
A comprehensive forensic analysis of failure modes in multi-agent LLM systems. The authors examine over 1,600 annotated interaction traces across 7 prominent MAS frameworks, creating the MAST (Multi-Agent System Failure Taxonomy) of 14 failure modes grouped into specification, inter-agent misalignment, and verification breakdowns.

---

## 2. Research Motivation & Problem Formulation
Despite immense hype, multi-agent frameworks often fail unpredictably in real-world deployment or yield negligible gains over single agents. Prior literature lacked a systematic diagnostic framework explaining the root causes of multi-agent failures.

---

## 3. Technical Architecture & Methodology
- Analyzes 7 frameworks: AutoGen, MetaGPT, ChatDev, CrewAI, CAMEL, and custom architectures.
- Curates MAST-Data: 1,600+ multi-turn execution traces annotated by human experts and automated evaluators.
- Categorizes failures into 3 primary clusters:
  1. System Specification & Design (~41.8%)
  2. Inter-Agent Misalignment & Communication (~36.9%)
  3. Task Verification & Termination (~21.3%)

---

## 4. Experimental Framework & Setup
- Traces failure propagation across multi-step execution graphs.
- Measures correlation between team size, dialogue length, and cascading error rates.

---

## 5. Key Quantitative Findings & Breakthroughs
- **Error Amplification:** Hallucinations in early sub-agents compound exponentially in downstream agents because agents lack stable internal state verification.
- **Context Collapse:** Passing long conversational histories causes instruction dilution, leading downstream agents to lose track of original user constraints.
- Over 36% of failures originate from communication breakdowns (withholding info, misinterpreting intent, endless loops).

---

## 6. Critical Limitations, Caveats & Failure Modes
- Purely diagnostic and observational; does not propose a new coordination architecture or runtime fix.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Provides the **exact diagnostic vocabulary** for our Error Analysis and Discussion sections. When our small MAS arm underperforms the large quantized SAS model on multi-hop tasks, MAST allows us to classify whether failure stemmed from context collapse, cascading hallucination, or verification failure.

---

## 8. Citation Utility & Key Takeaways
Cite extensively in Section 5 (Discussion and Error Analysis) to explain why small multi-agent models suffer from coordination overhead.
