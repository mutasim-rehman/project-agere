# 11. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework

> **Authors:** Sirui Hong, Mingchen Zhuge, Jonathan Chen, et al.  
> **Affiliation & Venue:** ICLR 2024 (Oral Presentation)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`11_Hong_2024_MetaGPT_Multi_Agent_Collaborative_Framework.pdf`](../../sources/11_Hong_2024_MetaGPT_Multi_Agent_Collaborative_Framework.pdf)  
> **Role in Our Study:** **SOP-Based Hierarchical Architecture Baseline**

---

## 1. Executive Summary & Core Premise
Accepted as an Oral presentation at ICLR 2024, MetaGPT incorporates human Standardized Operating Procedures (SOPs) into multi-agent systems. By replacing unstructured natural language dialogue with structured engineering documents (PRDs, architecture designs, API specifications), MetaGPT prevents cascading hallucinations and coordinates specialized agents in complex multi-file software creation.

---

## 2. Research Motivation & Problem Formulation
Natural language multi-agent conversations quickly degenerate into hallucination cascades, repetitive loops, and context drift. Human software organizations avoid this by enforcing rigorous SOPs and structured documentation schemas.

---

## 3. Technical Architecture & Methodology
- Models human roles: Product Manager, Architect, Project Manager, Engineer, QA Engineer.
- Replaces conversational chat with structured artifacts (Markdown tables, JSON schemas, UML diagrams).
- Publish-subscribe message bus ensuring agents only receive documents relevant to their role.

---

## 4. Experimental Framework & Setup
- Benchmarks: HumanEval, MBPP, and end-to-end multi-file software synthesis.
- Evaluates task completion rate, code executability, and documentation quality.

---

## 5. Key Quantitative Findings & Breakthroughs
- Achieves state-of-the-art code generation pass rates, generating executable multi-file software projects.
- SOP constraints reduce cascading logic errors by over 60% compared to unconstrained multi-agent dialogue.

---

## 6. Critical Limitations, Caveats & Failure Modes
- High token verbosity due to comprehensive documentation generation at each step.
- Specifically optimized for software engineering rather than generalized reasoning.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Serves as our primary **Hierarchical Orchestrator-Worker baseline**, demonstrating that small sub-agents need rigid role constraints to succeed.

---

## 8. Citation Utility & Key Takeaways
Cite in Section 2 and Section 3 as the gold-standard peer-reviewed (ICLR Oral) hierarchical MAS framework.
