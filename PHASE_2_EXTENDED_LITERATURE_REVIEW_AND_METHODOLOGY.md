# PHASE 2 — EXTENDED LITERATURE REVIEW AND RESEARCH METHODOLOGY DEVELOPMENT

**Project Title:** Spend It Together or Spend It Big? Multi-Agent Full-Precision Teams vs. Quantized Monoliths on Analyst Workstation RAM for Regulated Finance  
**Repository:** Project Agere (`/workspace`)  
**Document Type:** Phase 2 / Milestone 02 Required Deliverable  
**Project members:** Mutasim ur Rehman and Ahmad Raza  
**Date:** October 2026  
**Status:** Complete  

---

## Executive Summary

Phase 2 moves Project Agere from foundational research gap identification into an extended, in-depth literature review, critical synthesis, and comprehensive, technically sound research methodology. Operating under strict banking secrecy, Personally Identifiable Information (PII) protection, and regulatory mandates (e.g., FINRA Notice 24-09, SEC Rule 17a-4, EU AI Act, DORA, and State Bank of Pakistan AML/CFT regulations), financial institutions are legally prohibited from transmitting client KYC portfolios, credit memo dossiers, or suspicious transaction data to public cloud APIs. Analyst workstations—typically constrained to 16 GB of physical system RAM without datacenter GPUs—represent the binding physical deployment envelope.

This document fulfills the four required deliverables of Milestone 02:
1. **Deliverable 1 — Extended Literature Review:** Identification, critical synthesis, and structured comparison of 10 additional peer-reviewed research papers published in 2025–2026 from top-tier Q1/Q2 venues (NeurIPS, ICLR, ACL, NAACL, EMNLP, IEEE).
2. **Deliverable 2 — Refined Research Gap:** Rigorous synthesis of four potential research gaps grounded in empirical evidence across the literature and justified across six structural questions (what exists, what are the limitations, what domains remain uninvestigated, why the gap is significant, what interventions are proposed, and how the research addresses them).
3. **Deliverable 3 — Proposed Step-by-Step Research Methodology:** A reproducible, 12-step pipeline spanning research inputs, synthetic generation, preprocessing, representation, model architectures, baseline protocols, experimental design, compliance-first grounding metrics, statistical testing, ablations, failure forensics, and final deployment outputs.
4. **Deliverable 4 — Research Methodology Architecture Diagram:** An exhaustive, multi-tier ASCII/Unicode architectural schematic illustrating data flows, process-tree memory caps, thinking-token budgets, deterministic tool interfaces, and human-in-the-loop compliance sign-off.

---

## Deliverable 1: Extended Literature Review (2025–2026 Corpus)

### 1.1 Context and Selection Criteria for the Extended Corpus
Phase 1 examined 9 foundational studies (Tran & Kiela 2026; Żywot et al. 2026; Kim et al. 2025; Cemri et al. MAST 2025; Lin et al. Bench360 2025; Jang et al. 2026; Singh & Pawar 2026; Financial QA SME 2026; MortarBench 2026). These studies confirmed that token budgets can confound multi-agent evaluations and that quantization reduces tool-calling reliability, but they left open critical methodological issues involving dynamic orchestration, actor-critic coordination, role differentiation, multi-agent critique and revision, and hardware-constrained local deployment.

To establish the most rigorous academic grounding possible, we identified 10 additional peer-reviewed research papers published exclusively in 2025 and 2026. Each selected paper satisfies the following strict criteria:
- **Publication Venue:** Published in recognized top-tier conferences or journals (NeurIPS, ICLR, ACL, NAACL, EMNLP, IEEE Access).
- **Recency:** Published exclusively in 2025 or 2026.
- **Methodological Depth:** Provides reproducible experimental designs, clear baseline comparisons, explicit dataset specifications, and rigorous evaluation measures.
- **Direct Domain Relevance:** Proactively explores multi-agent coordination, orchestration topology, error cascading, refinement/verification, extreme quantization, or high-liability domain applications.

---

### 1.2 Critical Thematic Analysis Across the Extended Corpus

```
┌────────────────────────────────────────────────────────────────────────┐
│             Five Thematic Pillars of the Extended Literature           │
├───────────────────────────────────┬────────────────────────────────────┤
│ 1. Dynamic Orchestration & DAGs   │ 2. Role Differentiation & MARL     │
│    Dang et al. (NeurIPS 2025)     │    Li et al. (ACL 2025)            │
│    Yang et al. (NeurIPS 2025)     │    Sun et al. (EMNLP 2025)         │
│    Estornell et al. (ICLR 2025)   │    Coordination collapse & debate  │
├───────────────────────────────────┼────────────────────────────────────┤
│ 3. Multi-Agent Critique & Faith   │ 4. Regulated Domain Evaluation     │
│    Wan et al. (NAACL 2025)        │    Zhu et al. (NeurIPS 2025)       │
│    Jamshidi et al. (EMNLP 2026)   │    High-liability task bounds;     │
│    Iterative refinement & decay   │    SAS parity in clinical texts    │
├───────────────────────────────────┴────────────────────────────────────┤
│ 5. Resource-Constrained Quantization & Local MAS Execution             │
│    Alquwayfili et al. (IEEE 2025, Quantigence)                         │
│    Liu et al. (ICLR 2025, SpinQuant)                                   │
│    Hardware-aware inference under workstation memory ceilings          │
└────────────────────────────────────────────────────────────────────────┘
```

#### Theme 1: Dynamic Orchestration, Adaptive Topologies, and Directed Execution Graphs
Multi-agent pipelines often suffer from excessive token consumption and rigid coordination overhead, particularly in static sequential chains or fixed round-robin debates. **Dang et al. (NeurIPS 2025)** proposed a reinforcement learning-based method to train a centralized orchestrator that dynamically schedules sub-agents and constructs compact, instance-specific reasoning topologies. Their framework demonstrated that eliminating unnecessary communication hops saves 34% of token expenditure while improving task accuracy on complex multi-domain benchmarks. In parallel, **Yang et al. (NeurIPS 2025)** introduced *AgentNet*, a decentralized framework where agents coordinate through Directed Acyclic Graphs (DAGs) without a central bottleneck. Meanwhile, **Estornell et al. (ICLR 2025)** presented *ACC-Collab*, an actor-critic framework that optimizes multi-agent collaboration and credit assignment across sequential decision steps.

*Critical Evaluation & Identified Limitations for Local Deployments:* While dynamic graph scheduling and actor-critic coordination improve theoretical task efficiency, these systems were evaluated on unconstrained cloud clusters. They introduce non-trivial meta-orchestration models and gradient computation overheads that are simply not viable on a 16 GB workstation. Furthermore, they fail to constrain peak resident process RAM ($M_{\text{job}}$), nor do they investigate whether a single quantized generalist model operating under staged prompt scheduling can outperform distributed agent graphs under the same physical hardware ceiling.

#### Theme 2: Turn-Aware Role Differentiation and Coordination Overhead
Semantic homogenisation is one of the most common failure modes in multi-agent systems, where collaborative agents converge toward a false consensus and compound intermediate errors. To overcome this, **Li et al. (ACL 2025)** employed learned role embeddings and Multi-Agent Reinforcement Learning (MARL) for turn-aware role differentiation. Their approach succeeded in enforcing orthogonal functional roles during inter-agent debates, avoiding consensus collapse, and increasing reasoning diversity across 7 reasoning benchmarks. Concurrently, **Sun et al. (EMNLP 2025, Collab-Overcooked)** critically examined the causes of collaboration failure across 13 contemporary LLMs, demonstrating that while role prompting works in early conversational turns, models suffer severe performance drops in continuous adaptation, spatial coordination, and long-horizon planning, frequently resulting in communication deadlocks.

*Critical Evaluation & Identified Limitations for Regulated Finance:* Li et al.'s debate frameworks require multiple forward passes and round-robin dialogues ($N \ge 3$ turns), which directly contravenes the Data Processing Inequality (DPI) and rapidly depletes workstation token budgets ($T_{\text{think}} \le 2048$). In financial compliance (such as checking a corporate share register or computing a debt-service coverage ratio), open discussion promotes hallucination snowballs. What is required is not open-ended natural language argumentation, but deterministic role specialization governed by strictly typed schemas.

#### Theme 3: Multi-Agent Error Detection, Critique Reranking, and Claim Degradation
To improve factual reliability, **Wan et al. (NAACL 2025)** developed *MAMM-Refine*, an architecture that leverages feedback from specialist critique agents to rerank candidate revisions in generated drafts based on factual alignment scores. Their results demonstrated that reranking candidate revisions with structured critique tokens is substantially more effective than unconstrained autoregressive revision generation. However, **Jamshidi et al. (EMNLP 2026)** rigorously modeled inter-agent factual decay, demonstrating that across sequential multi-agent handoffs, unsupported factual claims decay following an exponential decay function unless anchored by deterministic external retrieval or formal verification boundaries.

*Critical Evaluation & Identified Limitations:* MAMM-Refine focused on open-domain summarization and question answering, leaving domain-specific compliance risks unmeasured—such as numerical discrepancy detection, missing statutory tax identifiers, or citation span precision. Jamshidi et al.'s analysis was primarily observational and synthetic. Neither study enforced a physical memory ceiling or evaluated whether multi-model critique loops could be eliminated entirely by using a fine-tuned quantized monolith paired with staged prompts.

#### Theme 4: High-Liability Domain Benchmarking and the Single-Agent Parity Reality
In high-liability regulated domains, the assumption that multi-agent collaboration is inherently superior to single-model execution has been forcefully challenged. **Zhu et al. (NeurIPS 2025, MedAgentBoard)** established a comprehensive benchmark across four clinical task families (medical QA, diagnostic summarization, EHR trajectory prediction, and treatment planning). Their empirical findings revealed that while multi-agent teams achieve marginal improvements in multimodal diagnostic aggregation, strong single-agent models with extended Chain-of-Thought match or outperform multi-agent teams across more than 70% of clinical document workflows, exhibiting dramatically lower latency and eliminating coordination-related failure modes.

*Critical Evaluation & Identified Limitations:* While MedAgentBoard represents a milestone in high-liability domain evaluation, its focus is strictly biomedical. Regulated banking and compliance workflows possess fundamentally distinct characteristics: statutory compliance thresholds are strictly codified by law (e.g., FATF beneficial ownership thresholds, SBP Prudential Regulations); cross-document reconciliations are highly complex (bank statements vs. audited balance sheets); and there is zero tolerance for numerical fabrication. Moreover, Zhu et al. evaluated models exclusively via commercial cloud API endpoints without hardware memory caps or quantization parity.

#### Theme 5: Hardware-Aware Quantization and Multi-Agent Inference on Commodity RAM
Bridging the gap between multi-agent theory and physical hardware, **Alquwayfili et al. (IEEE Access 2025, Quantigence)** developed a framework to orchestrate 4-bit quantized multi-agent systems on consumer-grade hardware envelopes. By optimizing weight residency and offloading dormant agents to system RAM, they demonstrated the feasibility of deploying multi-agent teams on commodity devices. On the single-model compression front, **Liu et al. (ICLR 2025, SpinQuant)** demonstrated that learned orthogonal rotations eliminate outlier activation dimensions, enabling 4-bit weight and activation quantization (W4A4) without significant loss of perplexity on standard LLMs.

*Critical Evaluation & Identified Limitations:* Alquwayfili et al. evaluated multi-agent teams where *all* sub-agents were quantized to 4 bits, which—as demonstrated by Jang et al. (2026)—causes a severe compounding of tool-syntax failures and JSON truncation. They did not explore the alternative architectural paradigm: deploying native full-precision (FP16) small specialist agents instead of a single quantized monolith (SAS-Quant) under the same peak process RAM. Liu et al. focused exclusively on perplexity preservation for single models on GPU tensor cores, omitting CPU-first workstation execution and agentic tool invocation.

---

### 1.3 Cross-Paper Comparison Table (10 Extended Papers)

The following table provides a rigorous, deeply synthesized comparison of the 10 extended 2025–2026 peer-reviewed studies. In accordance with Milestone 02 requirements, details are synthesized to highlight concrete datasets, preprocessing methods, architectures, evaluation metrics, empirical results, and identified research limitations.

| # | Title & Venue | Year | Dataset Used | Preprocessing & Invariants | Models / Techniques Used | Evaluation Metrics Used | Key Empirical Results | Critical Limitations & Research Gaps |
| :-: | :--- | :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Multi-Agent Collaboration via Evolving Orchestration** *(Dang et al., NeurIPS)* | 2025 | GSM8K, MATH, HumanEval, HotpotQA | Dynamic prompt decomposition; token history truncation; task-state graph serialization | Llama-3-70B, GPT-4o; RL-trained centralized meta-orchestrator + specialized sub-agents | Pass@1, Token Efficiency (Tokens/Problem), Orchestration Overhead (sec) | Reduces communication token overhead by 34.2%; achieves +4.8% accuracy gain over static round-robin agent chains | Evaluated on cloud GPUs; ignores physical workstation RAM limits; orchestrator adds computational overhead impractical for local CPUs. |
| **2** | **ACC-Collab: Actor-Critic Multi-Agent Collaboration** *(Estornell et al., ICLR)* | 2025 | ALFWorld, WebShop, InterCode (interactive decision benchmarks) | State-action trajectory logging; reward signal normalization; centralized critic state encoding | Llama-3-8B/70B; Decentralized Actor agents + Centralized Critic for multi-agent policy gradients | Task Success Rate, Average Steps to Goal, Reward Accumulation, Variance | Actor-critic credit assignment boosts success by 18.5% over vanilla prompt-based debate; prevents premature convergence | High training and memory cost for centralized critic; tested exclusively on synthetic web/game sandboxes, not high-liability compliance. |
| **3** | **Advancing Debates with Role Differentiation** *(Li et al., ACL)* | 2025 | MMLU, GSM8K, ARC-Challenge, StrategyQA | Turn-aware prompt formatting; orthogonal role embedding projection; debate history pruning | Mistral-7B, Llama-2-13B; MARL-optimized role differentiators (Devil's Advocate, Fact-Checker, Synthesizer) | Accuracy (%), Semantic Diversity Score, Consensus Convergence Rate | Orthogonal role differentiation prevents premature consensus; reduces groupthink failure modes by 41% across debate turns | Multi-round debate consumes $3\times\text{--}5\times$ more tokens than single-agent CoT; unconstrained dialogue induces error snowballs in tabular data. |
| **4** | **MAMM-Refine: Faithfulness via Multi-Agent Collaboration** *(Wan et al., NAACL)* | 2025 | CNN/DailyMail, XSum, QAGS, FRANK (factual consistency splits) | Entity extraction masking; claim dependency parsing; critique candidate generation | Llama-3-8B, Qwen1.5-14B; Generator Agent + Critique Agent + Revision Reranker | FactCC, QAGS-Score, Rouge-1/2/L, Human Faithfulness Rating | Structured critique reranking improves factual consistency by +8.4% over single-pass generation; outperforms self-reflection | Focuses on open-domain summarization; lacks numerical reconciliation or compliance discrepancy metrics; compute budgets unconstrained. |
| **5** | **AgentNet: Decentralized Coordination via DAGs** *(Yang et al., NeurIPS)* | 2025 | GAIA, SWE-bench Lite, WebArena | Dependency graph compilation; message serialization via typed key-value pairs; dead-end pruning | DeepSeek-V2, Qwen2.5-72B; Decentralized directed acyclic graph (DAG) routing without central master | Task Completion Rate, End-to-End Latency, Communication Redundancy | DAG routing achieves parity with centralized topologies while cutting latency by 28%; prevents single-point master failure | Evaluated exclusively on massive cloud models; concurrent RAM footprint of multiple DAG nodes violates local workstation hardware caps. |
| **6** | **MedAgentBoard: Multi-Agent vs Single-Agent Benchmarking** *(Zhu et al., NeurIPS D&B)* | 2025 | MedQA, PubMedQA, MIMIC-IV Clinical Summaries, EHR Trajectories | Clinical entity anonymization; temporal event extraction; standardized physician prompt templates | GPT-4o, Claude-3.5-Sonnet, Med-PaLM 2; MAS vs SAS-CoT vs Specialist Baselines | Clinical Diagnostic Accuracy, Rouge-L, Hallucination Rate, Physician Score | Strong single-agent models with CoT match or exceed multi-agent teams on >70% of clinical tasks; MAS adds latency without accuracy | Domain restricted to medicine; models evaluated via commercial APIs; no hardware memory parity, local CPU profiling, or quantization comparison. |
| **7** | **Collab-Overcooked: Evaluating Collaborative Agents** *(Sun et al., EMNLP)* | 2025 | Overcooked-AI (5 layout environments) + 30 open-ended interactive tasks | Multi-modal frame encoding; action-space token mapping; partner behavior profiling | 13 LLMs (Llama-3, Qwen, Claude-3, GPT-4o); Zero-shot coordination & Few-shot adaptation | Partner Score, Collision Rate, Coordination Efficiency, Stuck Rate | Contemporary LLMs fail in active real-time collaboration; frequent communication deadlocks and catastrophic coordination collapse | Game-theoretic coordination environment; lacks document-grounded verification, regulatory policy compliance, and RAM-constrained execution. |
| **8** | **Quantigence: 4-Bit MAS on Commodity Hardware** *(Alquwayfili et al., IEEE Access)* | 2025 | HotpotQA, GSM8K, CodeXGlue | 4-bit weight packing; dynamic model eviction from host RAM to disk swap; prompt context sharding | Llama-3-8B @ INT4, Mistral-7B @ INT4; Commodity RAM/GPU Multi-Agent Pipeline | Task Accuracy (%), Peak Host RAM (GB), Swapping Latency, Throughput (tok/s) | Confirms feasibility of running multi-agent workflows under tight 8–16 GB hardware envelopes via aggressive quant and paging | All agents were quantized to 4-bit, compounding tool-calling syntax errors; did not evaluate native FP16 specialist teams vs. quantized monoliths. |
| **9** | **Hallucination Cascade in Multi-Agent Systems** *(Jamshidi et al., EMNLP)* | 2026 | Multi-turn dialogue traces, Collaborative reasoning graphs | Injected factual perturbation; claim-level token dependency tracking; transition probability estimation | Llama-3-8B/70B, Qwen2.5-7B/32B; Sequential agent chains ($N=2\text{ to }6$) | Factual Survival Probability ($S_t$), Cumulative Error Rate, Cascade Decay | Factual claims decay exponentially across ungrounded agent handoffs ($S_t \propto e^{-\lambda t}$); errors cascade irreversibly without external tools | Observational study; did not formulate a deterministic runtime verification gate; omitted memory-bounded local workstation constraints. |
| **10** | **SpinQuant: LLM Quantization with Learned Rotations** *(Liu et al., ICLR)* | 2025 | WikiText-2, C4, PTB, Zero-shot reasoning splits | Random Hadamard transform; learned orthogonal rotation optimization; activation outlier smoothing | Llama-2/3 (7B–70B), Mistral-7B; W4A4 and W4A8 quantization via learned rotation matrices | Perplexity (PPL), Zero-shot Accuracy (ARC, HellaSwag, MMLU), Kernel Speedup | Closes 85% of the accuracy gap between INT4 and FP16; effectively eliminates activation outliers across transformer blocks | Evaluated exclusively on GPU tensor cores; ignores CPU-first integer execution (GGUF/llama.cpp); does not test agent tool invocation stability. |

---

## Deliverable 2: Refined Research Gap Synthesis

### 2.1 Extended Cross-Paper Research Gap Synthesis Table

Guided by the combined Phase 1 and Phase 2 literature base, we synthesize **four fundamental, unaddressed research gaps**. The table below establishes explicit empirical evidence across the literature and defines the corresponding research opportunity addressed by Project Agere.

| Research Gap | Evidence from Study 1 | Evidence from Study 2 | Evidence from Study 3 | Proposed Research Opportunity |
| :--- | :--- | :--- | :--- | :--- |
| **Gap 1: The Memory-Bounded Multi-Agent vs. Quantized Monolith Parity Void** | **Tran & Kiela (2026):** Enforces strict thinking-token parity ($T_{\text{think}}$) across agent setups, but assumes unlimited cloud memory, omitting physical host RAM constraints. | **Lin et al. (Bench360, 2025):** Evaluates local LLM execution under hardware RAM/VRAM caps, proving 14B Q4 beats 3B FP16, but evaluates *only single-model pipelines*. | **Alquwayfili et al. (IEEE 2025):** Profiles multi-agent execution on commodity hardware, but quantizes *all* models to 4-bit, ignoring full-precision specialist teams. | Execute the first controlled evaluation comparing a **quantized monolith (SAS-Quant, Q4_K_M)** against a **full-precision specialist team (MAS-FP16)** where both peak process RAM (RUPP protocol) and thinking tokens ($T_{\text{think}}$) are simultaneously held invariant. |
| **Gap 2: The Confounded Tool Baseline & Naive Evaluation Fallacy** | **Żywot et al. (2026):** Claims small-model MAS beats large models, but grants tools (Python/search) *exclusively to the MAS*, confounding architecture with tool access. | **Zhu et al. (MedAgentBoard, 2025):** Demonstrates that when strong single models are given equal reasoning scaffolds, multi-agent superiority vanishes in 70% of tasks. | **Dang et al. (NeurIPS 2025):** Demonstrates that naive unpruned multi-agent pipelines waste >34% of compute in redundant coordination dialogue. | Establish the **"Improve-Then-Compare"** paradigm: harden *both* arms with identical local deterministic tools (extractor, calculator, retriever) and structured prompting before comparative evaluation, eliminating naive baseline bias. |
| **Gap 3: Domain-Adapted Quantization (QLoRA) vs. Architectural Boundary Verification** | **Jang et al. (2026):** Demonstrates that 4-bit quantization causes an explosion in agent tool-calling syntax errors and invalid JSON structures. | **Singh & Pawar (2026) / Jamshidi et al. (2026):** Proves unchecked agent handoffs suffer exponential hallucination cascades without boundary verification. | **Liu et al. (SpinQuant, 2025):** Shows that post-training quantization preserves perplexity but leaves agent refusal discipline and function syntax unaddressed. | Formulate a direct empirical comparison between **QLoRA domain fine-tuning** (rescuing the 4-bit monolith's refusal and tool discipline) and an **independent deterministic verifier gate** (halting Markov snowballs in the FP16 team). |
| **Gap 4: Absence of Compliance-Aligned Grounding Metrics in Regulated Workflows** | **MortarBench (2026):** Establishes an origination agent benchmark, but evaluates only standard Boolean F1, ignoring uncited claims and hardware RAM limits. | **Wan et al. (MAMM-Refine, 2025):** Evaluates factual refinement on generic summarization, ignoring financial balance sheet reconciliations and statutory rules. | **Cemri et al. (MAST, 2025):** Categorizes 1,600+ multi-agent failures retrospectively, but provides no quantitative grounding or mismatch-detection metrics. | Design and deploy a compliance-grounded evaluation framework reporting **Structured Invention Rate**, **Planted Mismatch Recall**, **Refusal Correctness**, and **Citation Accuracy** on realistic KYC and credit dossiers. |

---

### 2.2 Refinement and Formal Justification of the Research Gap

To satisfy the core Milestone 02 research criteria, we answer the six mandatory analytical questions:

#### 1. What has already been done?
Prior research has rigorously explored several individual dimensions of LLM deployment:
- **Test-Time Compute Control:** Tran & Kiela (2026) and Wang et al. (EMNLP 2024) demonstrated that unconstrained multi-agent dialogue creates an illusory performance advantage, proving that holding thinking tokens ($T_{\text{think}}$) invariant often enables single-agent Chain-of-Thought to match or exceed multi-agent systems.
- **Local Inference Profiling:** Lin et al. (Bench360, 2025) profiled local LLM inference engines—`llama.cpp`, `vLLM`, and `SGLang`—with respect to latency, throughput, energy, and VRAM, establishing that larger quantized models frequently Pareto-dominate smaller native models on general language benchmarks.
- **Multi-Agent Coordination & Failure Taxonomies:** Cemri et al. (MAST, 2025) categorized 1,600+ multi-agent execution traces into 14 distinct failure modes. Dang et al. (2025), Yang et al. (2025), and Li et al. (2025) proposed dynamic DAG orchestration and learned role differentiation to prevent coordination collapse.
- **Agentic Quantization Vulnerabilities:** Jang et al. (2026) demonstrated that 4-bit quantization exerts a disproportionate negative impact on tool-calling precision, syntax stability, and entity extraction tasks in agentic workflows.

#### 2. What approaches currently exist?
Two dominant paradigms currently exist in industry and academia:
1. **The Quantized Monolith Paradigm (SAS-Quant):** When deploying on local hardware, IT practitioners default to selecting the largest open-weights model capable of fitting into workstation RAM when aggressively compressed to 4 bits (such as Qwen2.5-14B @ GGUF Q4_K_M on 16 GB RAM). In this configuration, all task phases are executed autoregressively by the single compressed model.
2. **The Cloud-Elastic Multi-Agent Paradigm:** Academic multi-agent systems instantiate multiple instances of frontier models (e.g., GPT-4o, Claude-3.5) operating within unconstrained cloud APIs, communicating through open natural language dialogue, debate loops, or dynamic DAG schedulers (MetaGPT, ChatDev, AgentNet).

#### 3. What are their limitations?
Both existing approaches suffer from profound technical and functional limitations:
- *Limitations of the Quantized Monolith:* While 4-bit compression largely preserves general semantic knowledge, it severely degrades **refusal discipline** (causing models to invent plausible missing data rather than acknowledging omission) and **tool-syntax stability** (producing malformed JSON arguments and arithmetic hallucinations).
- *Limitations of Cloud-Elastic Multi-Agent Systems:* Cloud multi-agent systems are legally impermissible in regulated finance due to strict data residency requirements (GDPR, DORA, SEC Rule 17a-4, SBP AML/CFT). Furthermore, porting multiple independent LLMs to local hardware results in catastrophic memory overruns, while unconstrained natural language handoffs suffer from the Data Processing Inequality ($I(X; Z) \le I(X; Y)$) and Markovian hallucination snowballs.

#### 4. What remains insufficiently investigated?
The literature reveals an absence of research at the intersection of:
- **Workstation Process Memory Parity:** No published study has matched the aggregate process-tree Resident Set Size (RSS) of a multi-agent team against a quantized monolith under identical hardware envelopes.
- **Full-Precision Specialists vs. Compressed Generalist:** No research investigates whether allocating a 12.8 GB process memory cap across an orchestrated team of native, uncompressed (FP16/BF16) small specialist models (e.g., 3B Orchestrator + 1.5B Extractor + 0.5B Verifier) provides superior factual grounding compared to concentrating the entire memory budget on a single 14B Q4_K_M monolith.
- **Document-Grounded Compliance Evaluation:** No benchmark evaluates local models on high-liability financial documentation tasks that incorporate planted cross-document discrepancies, missing statutory disclosures, and strict citation requirements.

#### 5. Why is this gap important?
This gap directly impacts compliance safety and real-world IT procurement for thousands of banking institutions:
- **Statutory Penalties for Regulated Institutions:** Financial institutions are exposed to severe statutory penalties for fraudulent or hallucinated compliance filings and for failing to detect AML/PEP red flags. Deploying quantized monoliths introduces systemic legal liability if 4-bit quantization causes silent grounding failures.
- **Capital & Hardware Efficiency:** Financial institutions cannot provision \$30,000 datacenter GPUs for every compliance analyst. If full-precision specialist teams demonstrate superior verification performance to quantized monoliths on existing 16 GB workstations, institutions can achieve enterprise-grade compliance automation without substantial capital expenditure.

#### 6. How will your research address it?
Project Agere resolves this dilemma through a controlled, leakage-free empirical investigation:
- We formulate and enforce the **RAM Utilization Parity Protocol (RUPP)**, locking both systems to the exact same host-adjusted process RSS ceiling (12.8 GB nominal on 16 GB workstations) and identical thinking-token budgets ($T_{\text{think}} = 2048$).
- Rather than testing naive baselines, we implement an **"Improve-Then-Compare"** loop: we harden the quantized monolith through QLoRA domain fine-tuning (refusal discipline, deterministic calculator calls, and span citation) and harden the multi-agent team through the AHDS framework (strictly typed Pydantic JSON contracts and an independent deterministic verifier boundary gate).
- We benchmark both hardened systems on realistic financial compliance tasks (MortarBench, synthetic KYC/CDD dossiers, SME credit memos) using specialized, compliance-aligned grounding metrics.

---

## Deliverable 3: Proposed Step-by-Step Research Methodology

Project Agere's research methodology is structured into 12 sequential, fully reproducible steps:

```
┌────────────────────────────────────────────────────────────────────────┐
│               12-Step Research Methodology Pipeline                     │
├────────────────────────────────────────────────────────────────────────┤
│ Step 1: Research Input Definition  ──► KYC, Credit Memos, MortarBench  │
│ Step 2: Data Collection Pipeline   ──► Statutory Packs & Discrepancies │
│ Step 3: Data Preprocessing         ──► Parsing, Masking, Injection     │
│ Step 4: Feature & State Rep.       ──► Pydantic Schemas, Span Pointers │
│ Step 5: Proposed MAS-FP16 Method   ──► AHDS Topology & Verifier Gate   │
│ Step 6: Baseline SAS-Quant Method  ──► QLoRA Q4_K_M Monolith           │
│ Step 7: Experimental Design        ──► RUPP RAM & Token Parity         │
│ Step 8: Evaluation Metrics         ──► Grounding, Invention, Mismatch  │
│ Step 9: Statistical Analysis       ──► McNemar, Bootstrap CIs, ANOVA  │
│ Step 10: Ablation Decomposition    ──► Gate, Adapter, & Schema Cuts    │
│ Step 11: Error & Failure Forensics ──► MAST & S1–S12 Forensic Triage   │
│ Step 12: Final Research Deliverable──► Audit Dossier & Decision Rule   │
└────────────────────────────────────────────────────────────────────────┘
```

### Step 1 — Define the Research Input
The research inputs represent high-liability corporate banking documentation where automated extraction and narrative synthesis are subjected to mandatory human oversight:
1. **Multi-Document Customer Dossiers (KYC / CDD):** Customer packets comprising national identity records (CNIC/SNIC), utility verification bills, tax authority filings (FBR Active Taxpayer List / NTN verification certificates), and corporate registrar documents (SECP Form 29 / Form A beneficial ownership schedules).
2. **Commercial SME Credit Approval Files:** Corporate loan application files including three consecutive years of audited balance sheets, profit-and-loss statements, cash-flow reconciliations, and central credit bureau debt summaries (e-CIB reports).
3. **Mortgage Loan Origination Packages (MortarBench):** Synthetic, distribution-faithful borrower packages that include Uniform Residential Loan Applications (FNMA Form 1003 / ULAD), W-2 wage statements, paystubs, and consecutive monthly checking/savings bank statements.
4. **Negative Control Input Slice:** Multi-hop question-answering cases from FRAMES and MuSiQue with no document context, evaluated to verify theoretical boundary conditions and confirm whether multi-agent performance advantages depend strictly on external document grounding.

### Step 2 — Data Collection and Synthetic Generation
Due to banking confidentiality laws and GDPR restrictions, real customer dossiers cannot be publicly published. We construct synthetic, legally compliant, distribution-faithful corpora:
- **`Agere-KYC-Synth`:** 600 synthetic customer onboarding cases created using rule-based stochastic templates aligned with Pakistan State Bank AML/CFT regulations and FATF 40 Recommendations (400 Train, 100 Dev, 100 Held-Out Test).
- **`Agere-Credit-Synth`:** 325 synthetic SME corporate credit dossiers featuring realistic financial ratios, debt obligations, and credit histories (200 Train, 50 Dev, 75 Held-Out Test).
- **`MortarBench Track A`:** 200 standardized mortgage underwriting cases from the published benchmark corpus (strictly held-out; 0 training instances).
- **Test Manifest Integrity:** To ensure complete prevention of evaluation data leakage, all evaluation splits are generated using disjoint pseudo-random seeds, cryptographically hashed with SHA-256 (`manifests/test_manifest.sha256`), and locked on an external drive prior to model fine-tuning.

### Step 3 — Data Preprocessing
Inputs are systematically mutated and parsed into verified ground-truth targets:
- **Structured OCR & Text Chunking:** `pdfplumber` and `pydantic` are utilized to convert PDF files into clean plain-text formats, preserving tabular markdown alignments and coordinate bounding boxes.
- **Systematic Error & Discrepancy Injection:**
  - *Planted Inconsistencies (30% of cases):* Name spelling variations, mismatched CNIC numbers between registry records and ID cards, expired tax certificates, undisclosed Politically Exposed Persons (PEPs), and unlisted bank loans.
  - *Omitted Data Fields (25% of cases):* Intentionally redacted or absent fields (e.g., omitted director CNIC issue dates, unstated operating turnover) to evaluate refusal discipline.
  - *Numerical Incompatibilities (20% of cases):* Conflicting cash figures between balance sheet cash assets and closing balances on bank statements.

### Step 4 — Feature Engineering and Representation
To remove conversational noise and establish strict grounding objectives from the ground up:
- **Typed Pydantic Schemas:** All entity representations are defined as strict schemas (e.g., `KYCEntitySchema`, `CreditRatioSchema`). Fields require explicit status flags: `VERIFIED`, `DISCREPANCY`, or `MISSING`.
- **Verifiable Citation Span Pointers:** Extracted facts are directly linked to source document coordinates: `[DocID: Page P, Lines L1-L2: "exact substring"]`.
- **Deterministic Ratio Computation:** Financial metrics (Debt Burden Ratio, Current Ratio, Debt Service Coverage Ratio) are engineered as programmatic tool targets computed deterministically, preventing the LLM from attempting free-form arithmetic in autoregressive tokens.

### Step 5 — Proposed Model / Method (Hardened MAS-FP16)
The primary proposed architecture is the **Adaptive Hierarchical with Dynamic Pruning & Structured Communication (AHDS)** full-precision team. Operating under concurrent RAM residency on the 16 GB tier (nominal job cap: 12.8 GB):
1. **Model Checkpoints:**
   - **Orchestrator & Memo Drafter:** Qwen2.5-3B-Instruct (native FP16, ~6.2 GB RSS).
   - **Entity Extractor Agent:** Qwen2.5-1.5B-Instruct (native FP16, ~3.1 GB RSS).
   - **Independent Verifier Agent:** Qwen2.5-0.5B-Instruct (native FP16, ~1.0 GB RSS).
   - **Shared Local Embedding Retriever:** `bge-small` (~0.4 GB RSS).
   - **KV-Cache & Runtime Footprint:** ~1.8 GB RSS (Total peak process RSS: ~12.5 GB $\le 12.8\text{ GB}$).
2. **Architectural Guardrails (Mitigating Gaps M1–M14):**
   - *Strict JSON Contracts (M2, DPI):* All inter-agent communication is exclusively serialized through validated Pydantic JSON formats; natural language conversational chatter is programmatically prohibited.
   - *Stateless Execution (M4):* On every turn, fresh task-constraint packets are injected into sub-agents, preventing instruction dilution across chat histories.
   - *Independent Verifier Boundary Gate (M3, M7, M13):* An automated boundary gate intercepts drafted narratives before delivery to the compliance officer. It programmatically extracts all monetary figures, dates, and entity claims, executing regex and exact substring checks against the Extractor cache. If unsubstantiated claims are detected, they trigger an automated single-pass repair routing.

### Step 6 — Baseline Methods
Multiple baseline configurations are evaluated to ensure a fair, rigorous, and scientifically valid comparison:
1. **Hardened SAS-Quant (Primary Competing Arm):** Qwen2.5-14B-Instruct compressed to 4-bit integer weights via GGUF `Q4_K_M` (~9.0 GB weights + ~2.2 GB KV/runtime $\approx 11.2\text{ GB}$ peak RSS). Trained on a curated 3-task domain adaptation mixture using QLoRA (NF4):
   - *Task A (Refusal Discipline, 40%):* Trained to output `"field_status": "MISSING"` when data is incomplete, penalized with infinite loss if plausible figures are fabricated.
   - *Task B (Strict Function Calling, 30%):* Trained on schema-valid JSON calculator tool calls.
   - *Task C (Span Citation, 30%):* Trained to link all factual assertions to specific spans in the source documents.
   - Operates via a deterministic staged prompting approach (Stage 1: Extract, Stage 2: Policy Check, Stage 3: Draft).
2. **Naive SAS-Quant Baseline:** Vanilla off-the-shelf Qwen2.5-14B-Instruct @ GGUF Q4_K_M without domain fine-tuning.
3. **Naive MAS-FP16 Baseline:** Multi-agent team baseline communicating through unstructured, open-ended conversational prompts without JSON schemas or verifier gates.
4. **Small Single-Model Baseline (SAS-FP16):** Single Qwen2.5-3B-Instruct native FP16 model, representing the baseline performance of small uncompressed models without multi-agent role decomposition.

### Step 7 — Experimental Design & Parity Invariants
Experiments are executed according to three strict parity protocols:
1. **RAM Utilization Parity Protocol (RUPP):**
   - Evaluated on a standard corporate workstation (16 GB physical memory).
   - A mandatory 20% reserve ($3.2\text{ GB}$) is allocated for the operating system and background processes.
   - The nominal aggregate process-tree RSS cap is locked to $12.8\text{ GB}$, adjusted downwards if host idle memory demands ($M_{\text{job}} = \min(0.8 M_{\text{tier}}, M_{\text{host}} - M_{\text{idle}} - 1\text{ GB})$).
   - Peak RSS is continuously profiled at 100 ms intervals using `psutil`.
2. **Thinking-Token Parity ($T_{\text{think}}$):**
   - The total number of test-time generation and intermediate reasoning tokens for each task instance is locked to an identical shared budget across both arms:
     $$T_{\text{think}}(\text{SAS}) = \sum_{k=1}^K T_{\text{think}}(\text{Agent}_k) = 2,048\text{ tokens}$$
3. **Tool and Runtime Parity:**
   - Both arms access the exact same deterministic Python tools (`document_extractor`, `policy_retriever`, `financial_calculator`, `citation_verifier`) via Berkeley Function-Calling Leaderboard (BFCL) compatible interfaces.
   - Both arms execute inference CPU-only using `llama.cpp` on identical hardware cores.
   - All evaluations are performed across 3 fixed random seeds ($42, 123, 999$).

### Step 8 — Evaluation Metrics
Systems are assessed using grounding metrics aligned with regulatory compliance rather than generic NLP text similarity:
1. **Grounding Accuracy ($GA$):** Proportion of factual narrative claims supported by verified document span pointers:
   $$GA = \frac{\sum_{i=1}^N \mathbb{I}(\text{Claim}_i \in \text{Source Spans})}{\text{Total Factual Claims Drafted}} \times 100\%$$
2. **Structured Invention Rate ($IR$, Primary Safety Metric - Lower is Better):** Percentage of evaluated cases containing fabricated financial figures, dates, or legal entities:
   $$IR = \frac{\text{Cases with Hallucinated Figures or Names}}{\text{Total Cases Evaluated}} \times 100\%$$
3. **Planted Mismatch Recall ($MR$):** Rate of correctly flagging deliberately injected cross-document discrepancies:
   $$MR = \frac{\text{Planted Discrepancies Correctly Flagged}}{\text{Total Planted Document Discrepancies}} \times 100\%$$
4. **Refusal Correctness ($RC$):** Percentage of intentionally omitted fields correctly refused as `MISSING` or `UNKNOWN`:
   $$RC = \frac{\text{Omitted Fields Correctly Refused}}{\text{Total Intentionally Omitted Fields}} \times 100\%$$
5. **Token Efficiency:** Accuracy score achieved per 1,000 thinking tokens consumed.
6. **Wall-Clock Latency:** Total execution time in seconds per case file on CPU runtime.

### Step 9 — Statistical and Comparative Analysis
To apply scientific rigor and evaluate the null hypothesis ($H_0$):
- **Hypothesis Testing for Binary Outcomes:** Case-level binary outcomes (e.g., case-level invention occurrences and mismatch detections) are compared using **paired McNemar's tests** ($\chi^2$ with continuity correction) across matched test instances.
- **Continuous Metric Testing:** The non-parametric **Wilcoxon signed-rank test** for paired samples is used for comparing Grounding Accuracy and Refusal Correctness distributions.
- **Confidence Intervals:** 95% bootstrap confidence intervals are computed using 1,000 resamples per evaluation track.
- **Factorial Interaction Analysis:** A two-way ANOVA is utilized to evaluate whether full-precision multi-agent teams interact synergistically with workstation memory constraints across the $2 \times 2$ factorial space (Architecture: SAS vs. MAS; Precision: Q4 vs. FP16):
  $$\Delta_{\text{interaction}} = [S(\text{MAS-FP16}) - S(\text{MAS-Q4})] - [S(\text{SAS-FP16}) - S(\text{SAS-Q4})]$$

### Step 10 — Ablation and Component Analysis
We perform systematic ablation experiments to isolate the causal drivers of performance:
1. **Ablation Arm 1 (MAS without Verifier Gate):** Remove the verifier agent from MAS-FP16 and route drafted narratives directly to output to measure the exact contribution of the boundary gate to hallucination reduction.
2. **Ablation Arm 2 (MAS without Typed JSON Schemas):** Replace structured Pydantic handoffs with free-form conversational dialogue to measure context collapse and information erosion under the Data Processing Inequality.
3. **Ablation Arm 3 (SAS without QLoRA Hardening):** Evaluate SAS-Quant without domain fine-tuning to measure the performance delta attributable solely to refusal and tool adaptation.
4. **Token Budget Sensitivity Analysis:** Evaluate both systems across scaled thinking-token budgets: $T_{\text{think}} \in \{1024, 2048, 4096\}$.
5. **Hardware Memory Tier Sensitivity:** Execute secondary evaluations on the held-out **8 GB tier** (6.4 GB job cap; 7B Q4 vs. 1.5B+0.5B+0.5B FP16) and **32 GB tier** (25.6 GB job cap; 32B Q4 vs. 7B+3B+0.5B FP16).

### Step 11 — Error and Failure Forensics
All failed cases are automatically logged in structured JSON format (`runs/`) and mapped to established failure taxonomies:
- **MAS Failure Modes (Cemri et al. MAST, M1–M14):** Forensic tagging of Specification Drift (M1), Lossy Handoff Information Decay (M2), Markov Hallucination Cascades (M3), Context Collapse (M4), Tool Race Conditions (M11), and Verification Theatre (M13).
- **SAS Quantization Failure Modes (S1–S12):** Forensic tagging of Refusal Failure / Eager Fabrication (S2), Arithmetic Drift in Prose (S4), Tool Syntax Brittleness (S5), and Citation Theatre (S6).
- **Confusion Matrix Construction:** Factual claims are categorized into True Grounded Assertions, False Fabrications, Correct Refusals, and Erroneous Rejections.

### Step 12 — Final Research Output and Decision Guidance
The research produces two practical deliverables:
1. **The Compliance Decision Framework:** An empirical decision matrix and decision tree providing IT compliance architects with definitive guidance regarding the memory threshold, task complexity, and token budget required to deploy a quantized monolith versus a full-precision multi-agent team.
2. **Audit-Ready Compliance Artifacts:** Standardized, machine-readable JSON compliance dossiers complete with exact span citations, reconciliation logs, planted discrepancy flags, and mandatory human sign-off blocks.

---

## Deliverable 4: Research Methodology Architecture Diagram

The schematic below provides an end-to-end architectural blueprint of Project Agere, detailing input ingestion, invariant enforcement, dual competing pipelines, deterministic tool execution, compliance-aligned evaluation, and human-in-the-loop oversight.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       PROJECT AGERE ARCHITECTURE                                       │
│          Multi-Agent Full-Precision Teams vs. Quantized Monoliths on Analyst Workstation RAM           │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       1. RESEARCH INPUT LAYER                                          │
├───────────────────────────────────┬────────────────────────────────────┬───────────────────────────────┤
│ Track A: Mortgage Origination     │ Track B: KYC / CDD Onboarding      │ Track C: SME Credit Memos     │
│ - MortarBench Benchmark Files     │ - CNIC / SNIC National IDs         │ - Audited Balance Sheets      │
│ - ULAD (FNMA Form 1003)           │ - FBR Tax Records & NTN Certs      │ - Profit & Loss Statements    │
│ - Monthly Bank Statements & W-2s  │ - SECP Form 29 Beneficial Owners   │ - Central Credit Bureau (e-CIB│
├───────────────────────────────────┴────────────────────────────────────┴───────────────────────────────┤
│ Track D: Negative Control Slice — Multi-hop closed-book QA without documents (FRAMES / MuSiQue)        │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              2. PREPROCESSING & PARITY ENFORCEMENT ENGINE                              │
├───────────────────────────────────────────────────┬────────────────────────────────────────────────────┤
│ • Preprocessing: OCR Parsing, Tabular Markdown    │ • Cryptographic Hashing: SHA-256 Test Manifest     │
│ • Mutation: Planted Discrepancies & Omitted Fields│ • Leakage Guard: Strict Disjoint Pseudo-Random Seed│
├───────────────────────────────────────────────────┴────────────────────────────────────────────────────┤
│                                  INVIOLABLE PARITY INVARIANTS                                          │
│  [RAM Utilization Parity Protocol (RUPP)]          [Thinking-Token Budget Parity ($T_{\text{think}}$)] │
│  - 16 GB Workstation Physical RAM Envelope         - Fixed Quota: $T_{\text{think}} = 2,048$ tokens    │
│  - 20% Mandatory OS/Headroom Reserve ($3.2\text{ GB}$) - Token Exhaustion Guard & Accounting Tracker   │
│  - Nominal Process RSS Ceiling: $M_{\text{job}} \le 12.8\text{ GB}$                                    │
└─────────────────────────┬────────────────────────────────────────────────────────────┬─────────────────┘
                          │                                                            │
                          ▼                                                            ▼
┌───────────────────────────────────────────────────┐        ┌───────────────────────────────────────────┐
│       ARM 1: COMPETING SAS-QUANT MONOLITH         │        │         ARM 2: PROPOSED MAS-FP16 TEAM     │
│   (Domain-Adapted Qwen2.5-14B-Instruct Q4_K_M)    │        │       (AHDS Full-Precision Specialist Team│
├───────────────────────────────────────────────────┤        ├───────────────────────────────────────────┤
│ • Model File: `qwen2.5-14b-instruct-q4_k_m.gguf`  │        │ • Weight Residency: Concurrent FP16 Team  │
│ • Weight Footprint: ~9.0 GB (In-Memory)           │        │ • Total Weight Sum: ~10.3 GB (In-Memory)  │
│ • Fine-Tuning: QLoRA (NF4) Domain Adapted         │        │ • Zero Dialogue: Strict Pydantic JSONs    │
│   - 40% Refusal Discipline on Missing Data        │        │                                           │
│   - 30% Deterministic Tool Function Calling       │        │ ┌───────────────────────────────────────┐ │
│   - 30% Exact Verifiable Span Citations           │        │ │ Extractor Agent (Qwen2.5-1.5B FP16)   │ │
│ • Execution Mode: Staged Deterministic Prompts    │        │ │ - Parses documents to structured JSON │ │
│                                                   │        │ │ - Emits explicit UNKNOWN for missing  │ │
│ ┌───────────────────────────────────────────────┐ │        │ └───────────────────┬───────────────────┘ │
│ │ Stage 1: Entity Extraction (JSON-bounded)     │ │        │                     │ [Typed JSON]        │
│ └───────────────────────┬───────────────────────┘ │        │                     ▼                     │
│                         ▼                         │        │ ┌───────────────────────────────────────┐ │
│ ┌───────────────────────────────────────────────┐ │        │ │ Policy Retriever (bge-small Index)    │ │
│ │ Stage 2: Regulatory & Policy Reconciliation   │ │        │ │ - Injects scoped SBP/FATF clauses     │ │
│ └───────────────────────┬───────────────────────┘ │        │ └───────────────────┬───────────────────┘ │
│                         ▼                         │        │                     │ [Scoped Rules]      │
│ ┌───────────────────────────────────────────────┐ │        │                     ▼                     │
│ │ Stage 3: Narrative Memo Synthesis & Spans     │ │        │ ┌───────────────────────────────────────┐ │
│ └───────────────────────┬───────────────────────┘ │        │ │ Drafter / Lead (Qwen2.5-3B FP16)      │ │
│                         │                         │        │ │ - Synthesizes narrative credit memo   │ │
│                         │                         │        │ │ - Attaches strict span citations      │ │
│                         │                         │        │ └───────────────────┬───────────────────┘ │
│                         │                         │        │                     │ [Draft Memo]        │
│                         │                         │        │                     ▼                     │
│                         │                         │        │ ┌───────────────────────────────────────┐ │
│                         │                         │        │ │ Verifier Gate (Qwen2.5-0.5B + String) │ │
│                         │                         │        │ │ - Deterministic substring matching    │ │
│                         │                         │        │ │ - Halts Markov hallucination snowball │ │
│                         │                         │        │ └───────────────────┬───────────────────┘ │
│                         │                         │        │                     │                     │
│                         │                         │        │       [Pass] ───────┴─────── [Reject]     │
│                         │                         │        │         │                       │         │
│                         │                         │        │         │                (Max 1 Repair)   │
│                         │                         │        │         │                       ▼         │
│                         │                         │        │         │            [Regeneration Packet]│
└─────────────────────────┼─────────────────────────┘        └─────────┼─────────────────────────────────┘
                          │                                            │
                          ▼                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               3. SHARED DETERMINISTIC LOCAL TOOLS (BFCL)                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • `document_extractor`: Extracts verified text chunks & coordinate tables                              │
│ • `financial_calculator`: Computes financial ratios (DBR, DSCR, Leverage) deterministically           │
│ • `policy_retriever`: Fetches permissioned regulatory clauses (SBP Prudential Regs, FATF)              │
│ • `citation_verifier`: Programmatically validates text substring alignment against source spans        │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              4. GROUNDING & COMPLIANCE EVALUATION ENGINE                               │
├───────────────────────────────────┬────────────────────────────────────┬───────────────────────────────┤
│ Grounding Accuracy (%)            │ Structured Invention Rate (%)      │ Planted Mismatch Recall (%)   │
│ - Verified span pointer ratio     │ - Fabricated figures or names (Min)│ - Caught planted discrepancies│
├───────────────────────────────────┼────────────────────────────────────┼───────────────────────────────┤
│ Refusal Correctness (%)           │ Token Efficiency (Score/1k Tokens) │ Peak Process RSS Profiling    │
│ - Abstention under missing fields │ - Compute efficiency per token     │ - Continuous psutil logging   │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 5. HUMAN COMPLIANCE OFFICER APPROVAL GATE                              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Sole Authorized Decision Authority: Mandated Human-in-the-Loop Sign-Off                             │
│ • Outputs are STRICTLY ADVISORY: System produces draft memos and discrepancy red-flag alerts           │
│ • Zero Autonomous Execution: Automated credit approval, account blocking, or SAR filings PROHIBITED    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Execution Timeline and Next Milestones

Following the formal approval of Phase 2, Project Agere executes along the established laboratory roadmap:
- **Phase 3 (Baseline Freeze & Untouched Dev Scoring):** Score the unadapted SAS-Quant generalist and naive MAS pipeline across Tracks A–D on development splits, establishing the empirical floor.
- **Phase 4 (Domain Adaptation & System Hardening):** Perform QLoRA fine-tuning for SAS-Quant (with GGUF re-quantization) and deploy AHDS JSON contracts and verifier boundary gates for MAS-FP16.
- **Phase 5 (Confirmatory Head-to-Head Evaluation):** Benchmark hardened systems on the 16 GB workstation tier under strict RUPP RAM and 2,048 token parity across 3 random seeds on the locked test manifest.
- **Phase 6 (Statistical Synthesis & Deployment Framework):** Execute paired McNemar tests, bootstrap confidence intervals, and ablation analyses; publish the final empirical decision guidance for banking IT deployment.
