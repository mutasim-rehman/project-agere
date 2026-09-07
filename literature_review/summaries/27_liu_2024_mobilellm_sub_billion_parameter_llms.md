# 27. MobileLLM: Optimizing Sub-billion Parameter Language Models for On-Device Use Cases

> **Authors:** Zechun Liu et al. (Meta AI)  
> **Affiliation & Venue:** ICML 2024  
> **Publication Year:** 2024  
> **Local PDF Source:** [`27_Liu_2024_MobileLLM_Sub_Billion_Parameter_LLMs.pdf`](../../sources/27_Liu_2024_MobileLLM_Sub_Billion_Parameter_LLMs.pdf)  
> **Role in Our Study:** **Sub-Billion Model Architecture Principles for Edge Sub-Agents**

---

## 1. Executive Summary & Core Premise
Published at ICML 2024 by Meta, MobileLLM proves that for sub-billion models (125M–1B), model architecture is far more critical than data scaling, introducing deep-thin topologies, embedding sharing, and block weight-sharing to maximize capability on edge devices.

---

## 2. Research Motivation & Problem Formulation
Deploying LLMs on mobile and edge hardware requires models under 1B parameters. Prior small models simply shrunk width and depth uniformly, causing severe reasoning collapse.

---

## 3. Technical Architecture & Methodology
- Deep-and-thin architecture optimizing memory bandwidth.
- Input/output embedding sharing and Grouped-Query Attention (GQA).
- Immediate block weight-sharing to increase effective depth with zero memory increase.

---

## 4. Experimental Framework & Setup
- Evaluated on commonsense reasoning, chat, and API-calling benchmarks.

---

## 5. Key Quantitative Findings & Breakthroughs
- 125M and 350M models achieve 2.7% to 4.3% accuracy gains over prior state-of-the-art models of identical parameter scale.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Requires pre-training from scratch.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Informs how to select and configure small sub-agents (e.g., 1B models) in our tightest memory tier (8 GB VRAM).

---

## 8. Citation Utility & Key Takeaways
Cite in Section 3 to justify sub-agent architectural selection in edge regimes.
