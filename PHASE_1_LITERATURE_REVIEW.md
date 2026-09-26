# PHASE 1 — LITERATURE REVIEW AND RESEARCH GAP IDENTIFICATION

**Project Title:** Spend It Together or Spend It Big? Multi-Agent Full-Precision Teams vs. Quantized Monoliths on Analyst Workstation RAM for Regulated Finance  
**Repository:** Project Agere (`/workspace`)  
**Document Type:** Phase 1 Required Deliverable  
**Date:** September 2026  
**Status:** Complete  

---

## Part 1: Literature Section & Critical Synthesis (Two-Page Narrative)

### 1.1 Context and Problem Formulation
In regulated financial institutions (commercial banks, investment funds, and lending institutions), deployment of generative Large Language Models (LLMs) on high-liability documentation tasks—such as Know Your Customer (KYC) onboarding, Customer Due Diligence (CDD), credit approval memo drafting, and mortgage underwriting—faces strict data privacy and regulatory constraints (e.g., FINRA Notice 24-09, SEC 17a-4, GDPR, DORA, and State Bank of Pakistan AML/CFT directives). Transmission of customer Personally Identifiable Information (PII), confidential financial statements, or suspicious activity traces to public cloud LLM endpoints is strictly prohibited. Consequently, institutions rely on local, on-premise execution using runtimes such as `llama.cpp` and `Ollama` on standard corporate workstations (typically equipped with 16 GB system RAM and commodity CPUs, without datacenter GPUs).

The default operational paradigm adopted by industry practitioners is to maximize parameter scale within the workstation's memory envelope by deploying a single, heavily quantized monolithic model—typically a 14B parameter generalist compressed to 4-bit integer weights (e.g., GGUF `Q4_K_M`). Project Agere investigates an alternative architectural hypothesis: partitioning that identical 16 GB RAM envelope and an invariant thinking-token budget across an orchestrated team of smaller, native full-precision (FP16/BF16) specialized agents (e.g., 3B Orchestrator/Drafter, 1.5B Extractor, 1.5B Verifier).

To establish the academic foundation and identify unexplored gaps, we conducted a critical analysis of 9 peer-reviewed and pre-print research studies published in 2025 and 2026 spanning top venues (ICLR, EMNLP, MLSys, IEEE, Stanford, Amsterdam, Google Research).

---

### 1.2 Critical Thematic Analysis Across the Literature

#### Theme 1: Test-Time Compute Confound & Token Parity
A prominent cluster of literature has historically claimed that Multi-Agent Systems (MAS) inherently out-reason Single-Agent Systems (SAS). However, **Tran & Kiela (2026)** rigorously demonstrated that this reported superiority is primarily an artifact of unconstrained test-time compute. When intermediate reasoning and inter-agent dialogue tokens are held strictly invariant under an equal thinking-token budget ($T_{\text{think}}$), single-agent extended Chain-of-Thought (CoT) matches or outperforms multi-agent debate and sequential setups on over 82% of multi-hop evaluation splits (FRAMES, MuSiQue, HotpotQA). Grounding their findings in information theory, Tran & Kiela proved via the Data Processing Inequality (DPI), $I(X; Z) \le I(X; Y)$, that each natural language handoff between agents without external ground-truth tool injection represents a lossy compression step that erodes factual context.

*Critical Evaluation & Identified Limitations:* While Tran & Kiela successfully exposed the token-budget confound, their methodology has major limitations:
- *Dataset Scope:* Restricted entirely to synthetic, closed-book multi-hop question answering benchmarks; it omits document-grounded, tool-augmented environments.
- *Hardware Omission:* They model compute purely as abstract token counts, ignoring physical hardware memory (resident RAM/VRAM) ceilings.
- *Homogeneous Scale:* All agents utilized identical model sizes (homogeneous teams), leaving unexamined whether heterogeneous, specialized sub-agent teams or quantized monoliths alter the trade-off under memory parity.

#### Theme 2: Tool-Augmentation as an Equalizer & Orchestrator Asymmetry
Addressing the tool deficit in prior studies, **Żywot et al. (2026)** investigated whether collaborative teams of small language models (4B–32B) could beat single models up to 8× larger on GAIA. Their findings established that small agents equipped with external tools (Python execution, web search) decisively outperform un-augmented large models. Crucially, they revealed an asymmetric scaling law: orchestrator parameter capacity dictates system-level success far more than worker capacity—upgrading the central planner yields non-linear gains, whereas scaling worker agents produces marginal improvements.

*Critical Evaluation & Identified Limitations:*
- *Uncontrolled Confound:* Żywot et al. compared tool-augmented small models against tool-deprived monolithic baselines. When monolithic models are granted identical tool execution, the architectural advantage substantially narrows.
- *Memory Ceiling Unenforced:* The multi-agent configurations instantiated multiple independent models without bounding cumulative resident VRAM or host RAM.
- *Zero Quantization Comparison:* They evaluated full-precision small models against full-precision large models across disparate hardware envelopes, failing to test whether a single 4-bit quantized model fitting into the same memory footprint wins.

#### Theme 3: Multi-Agent Failure Modes & Coordination Bottlenecks
Why do multi-agent systems fail in production? **Cemri et al. (2025)** presented the MAST taxonomy based on forensic analysis of 1,600+ multi-agent traces across 7 frameworks. They classified failures into three primary clusters: System Specification (41.8%), Inter-Agent Misalignment (36.9%), and Verification Breakdown (21.3%). Key failure mechanisms included "context collapse" (instruction dilution over long histories) and "error amplification" (unverified early hallucinations cascading exponentially). Complementing this, **Kim et al. (2025)** formalized predictive agent scaling laws across thousands of runs, demonstrating mathematically and empirically that tasks with high sequential dependencies exhibit *negative scaling*: adding agents degrades performance due to compounded handoff noise.

*Critical Evaluation & Identified Limitations:*
- *Observational Diagnostics Only:* Cemri et al. cataloged failure modes retrospectively without providing a formal, runtime-enforced mitigation framework.
- *Cloud Elasticity Assumption:* Kim et al. assumed zero-cost infrastructure scaling via cloud APIs, ignoring workstation RAM residency where loading $N$ concurrent models incurs direct physical memory penalties.

#### Theme 4: Quantization-Induced Vulnerabilities in Autonomous Agents
While post-training quantization methods like AWQ (**Lin et al., MLSys 2024**) preserve low perplexity and general knowledge on single models, **Jang et al. (2026)** revealed a critical vulnerability: 4-bit quantization dramatically amplifies agentic and tool-calling failures. While high-level benchmark scores remain flat, quantized models suffer an explosion in tool syntax errors, invalid JSON argument formatting, and ungrounded hallucinations under incomplete information. Furthermore, **Singh & Pawar (2026)** modeled multi-agent hallucination propagation as a Markov chain ("hallucination snowball"), demonstrating that once a compressed or hallucinating agent injects an inaccurate claim, downstream agents treat it as established ground truth unless halted by external boundary verification.

*Critical Evaluation & Identified Limitations:*
- *Missing Mitigation:* Jang et al. documented the degradation of quantized agents but did not evaluate domain-specific fine-tuning (e.g., QLoRA for refusal discipline and strict tool formatting) to rescue the quantized monolith.
- *Lack of Hardware Parity:* Singh & Pawar analyzed error snowballs theoretically without grounding their agent topologies in resident workstation memory constraints.

#### Theme 5: Hardware-Aware Local Inference & Financial Document Reasoning
**Lin et al. (2025, Bench360)** benchmarked local LLM inference across 360 degrees (VRAM, latency, energy, throughput, and accuracy across llama.cpp, vLLM, and SGLang). They proved that under rigid memory caps, a single quantized larger model (e.g., 14B Q4) routinely Pareto-dominates small native models (e.g., 3B FP16) on general NLP benchmarks. However, Bench360 evaluated only single-model execution, entirely omitting multi-agent collaboration.

In the financial domain, **Financial QA SME (2026)** proved that within strict SME compute envelopes (a single local 8B model), architectural innovations (retrieval and structured memory) outperform raw model scale. Finally, **MortarBench (2026)** established the first formal agent benchmark for mortgage loan origination, evaluating document reasoning over underwriting files, payroll records, and bank statements.

*Critical Evaluation & Identified Limitations:*
- *The Unbridged Gap:* Bench360 proved that single quantized models win under local memory caps, but never tested multi-agent architectures. Financial QA SME tested architectures on a single 8B model without evaluating quantization or multi-agent teams. MortarBench evaluated agent workflows but enforced neither RAM parity nor thinking-token budget controls.

---

### 1.3 Detailed Synthesis of Limitations Across the 2025–2026 Literature

1. **Limitations Explicitly Mentioned by Authors:**
   - *Tran & Kiela (2026):* Evaluated exclusively on closed-book QA (FRAMES, MuSiQue); explicit absence of tool use or multimodal document inputs; compute defined as tokens rather than physical memory.
   - *Żywot et al. (2026):* Total concurrently loaded model weights were unconstrained; API latency and non-deterministic web tool noise impacted reproducibility.
   - *Cemri et al. (2025):* Purely observational and forensic; proposed no architectural mitigation or runtime enforcement mechanism.
   - *Jang et al. (2026):* Evaluated off-the-shelf quantized generalists; did not test whether domain fine-tuning restores function-calling reliability.
   - *Lin et al. (2025, Bench360):* Limited strictly to single-model serving; multi-agent coordination was out of scope.
   - *MortarBench (2026):* Unbounded hardware compute; does not control for resident RAM footprint or test-time token budgets.

2. **Limitations Identified by Project Agere:**
   - *The Memory-Compute Disconnect:* Across all 9 papers, studies either control token budgets while ignoring physical hardware RAM (Tran & Kiela, Wang), or profile hardware memory while evaluating only single models on general benchmarks (Lin et al. Bench360). No published study bridges both axes simultaneously.
   - *Tool Parity Confound:* Prior MAS victories over monoliths (Żywot et al.) failed to provide identical tool interfaces to the single-agent baseline.
   - *Unadapted "Naive Baseline" Fallacy:* Existing agent studies compare off-the-shelf models, failing to acknowledge that generic quantized models fail from lack of domain adaptation, while generic agent teams fail from unconstrained natural language chatter.

3. **Dataset Limitations:**
   - Dominance of synthetic trivia puzzles (HotpotQA, GSM8K) or software codebases (SWE-bench).
   - Severe lack of high-liability, document-grounded financial compliance corpora featuring intentional discrepancies, missing fields, and regulatory verification constraints.

4. **Methodological & Evaluation Limitations:**
   - Reliance on general accuracy, ROUGE, or MMLU scores rather than compliance-aligned grounding metrics: **Invention Rate** (hallucinated amounts/dates), **Mismatch Recall** (flagging planted document conflicts), and **Refusal Correctness** (refusing to invent missing data).

5. **Generalizability Issues:**
   - Cloud API assumptions (unlimited burst concurrency) fail completely in air-gapped financial institutions operating under local workstation hardware constraints.

6. **Missing Experiments Across Prior Work:**
   - A controlled head-to-head evaluation between a **domain-fine-tuned quantized monolithic model (SAS-Quant)** and a **structured, verifier-gated multi-agent full-precision system (MAS-FP16)** where:
     - Peak resident system RAM is strictly matched ($M_{\text{peak}} \le 16\text{ GB}$).
     - Thinking-token budgets ($T_{\text{think}}$) are identical.
     - Available tools and execution environments are identical.

---

## Part 2: Cross-Paper Comparison Table

The following table provides a rigorous, comparative synthesis of the 9 foundational 2025–2026 studies directly informing Project Agere. Information is deeply synthesized to highlight critical differences in methodologies, datasets, models, metrics, findings, and gaps.

| # | Title | Year | Dataset Used | Preprocessing & Invariants | Models / Architectures | Evaluation Metrics | Key Findings & Results | Critical Limitations & Research Gaps |
| :-: | :--- | :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Single-Agent LLMs Outperform Multi-Agent Systems Under Equal Thinking Token Budgets** *(Tran & Kiela, Stanford)* | 2026 | FRAMES, MuSiQue, HotpotQA (multi-hop QA) | Strict thinking-token budgets $T \in [512, 8192]$; context truncation normalization | Qwen3, DeepSeek-R1-Distill, Gemini 2.5; SAS vs Sequential vs Debate vs Ensemble | Exact Match (EM), F1, Information Retention rate | SAS matches/beats MAS on >82% of splits; DPI proves conversational handoffs are lossy ($I(X;Z) \le I(X;Y)$) | Closed-book QA only; no tool use; models homogeneous; ignores hardware RAM/VRAM constraints entirely. |
| **2** | **Can Small Agent Collaboration Beat a Single Big LLM?** *(Żywot et al., Univ. of Amsterdam)* | 2026 | GAIA (Levels 1–3, real-world multimodal agent tasks) | Tool sandboxes (Python execution, web search); prompt decomposition | Qwen3 family (4B, 8B, 14B, 32B); Central Orchestrator + Specialized Tool Workers vs Monoliths | Task Completion Rate, Tool Selection Precision, Latency | 4B MAS + tools beats un-augmented 32B monolith; orchestrator capacity scales non-linearly over worker size | Monolithic baseline lacked equal tools (confound); total resident VRAM unconstrained; no post-training quantization tested. |
| **3** | **Towards a Science of Scaling Agent Systems** *(Kim et al., Google Research / DeepMind / MIT)* | 2025 | Multi-domain reasoning & synthetic dependency graphs | Formal classification by parallel ($P$) vs sequential ($S$) dependencies | Varying proprietary & open models; Independent, Centralized, Decentralized, Hybrid topologies ($N=1\text{ to }16$) | Predictive accuracy ($R^2 \approx 0.41$), Scaling exponents, Error cascade rate | Parallel tasks scale positively with agent count; high sequential dependency produces negative scaling (error compounding) | Elastic cloud API assumption; ignores concurrent GPU/CPU memory residency limits; no quantization analysis. |
| **4** | **Why Do Multi-Agent LLM Systems Fail? (MAST Taxonomy)** *(Cemri et al.)* | 2025 | MAST-Data (1,600+ multi-turn interaction traces across 7 frameworks) | Trace parsing into multi-step execution graphs; human & automated failure labeling | AutoGen, MetaGPT, ChatDev, CrewAI, CAMEL, custom agent topologies | Error frequency across 14 failure modes, correlation with team size and dialogue depth | 41.8% Specification, 36.9% Misalignment, 21.3% Verification; early hallucinations amplify exponentially downstream | Observational only; provides no algorithmic mitigation or runtime memory constraint protocol. |
| **5** | **Bench360: Benchmarking Local LLM Inference from 360 Degrees** *(Lin et al.)* | 2025 | Summarization, QA, Code execution benchmarks | Single-stream desktop, multi-turn chat, batched serving profiling | Open weights (7B–70B); llama.cpp, vLLM, SGLang; FP16, INT8, INT4 (AWQ, GPTQ), 2/3-bit | Peak VRAM (GB), TTFT, Latency, Throughput, Energy (Joules), Task F1 | Larger quantized models (14B Q4) Pareto-dominate small native models (3B FP16) on general benchmarks under fixed RAM | Evaluates only single-model inference pipelines; completely omits multi-agent collaborative systems. |
| **6** | **Flat Score, Amplified Failures: Sensitivity of Quantized LLM Agents** *(Jang et al.)* | 2026 | AgentBench, ToolBench, function-calling datasets | Calibration sets for PTQ; prompt-response trace logging | Llama-3, Qwen2.5; FP16 vs INT8 vs INT4-AWQ vs GGUF | Task Success, Tool Call Argument Validity, Syntax Error Rate, Invention Rate | Benchmark scores mask severe tool syntax degradation; 4-bit quant sharply amplifies tool argument & grounding failures | Did not evaluate domain fine-tuning (QLoRA) to repair tool calling; did not test multi-agent boundary verifiers. |
| **7** | **The Hallucination Snowball: Markov Modeling of Multi-Agent Propagation** *(Singh & Pawar)* | 2026 | Multi-agent sequential dialogue and drafting traces | State-transition matrix construction across sequential agent handoffs | Heterogeneous and homogeneous open-weight agent chains | Hallucination Survival Probability, Propagation Decay Rate, Boundary Catch Rate | Unchecked agent handoffs follow a Markov snowball: step 1 errors become step 3 facts; verifier gates collapse error survival | Theoretical modeling; lacks evaluation on standardized domain benchmarks or workstation hardware tiers. |
| **8** | **Architecture Matters More Than Scale: Financial QA under SME Compute** *(Anonymous / Financial QA SME)* | 2026 | Financial QA, earnings reports, regulatory disclosures | Retrieval chunking, memory structuring, credit spreading | Single local ~8B open-weight LLMs with symbolic memory & RAG | F1, Numerical Accuracy, Grounding Precision, Computational Cost | Retrieval and structured symbolic memory beat raw parameter scale under strict SME workstation constraints | Evaluated only a single 8B model; no multi-agent comparison; did not test quantization scaling (14B Q4 vs 3B FP16). |
| **9** | **MortarBench: Evaluating Mortgage Loan Origination Agents** *(Anonymous / MortarBench)* | 2026 | Synthetic distribution-faithful mortgage files (ULAD, bank statements, payroll) | SME expert filtering, document parsing into structured underwriting cases | Frontier & open LLMs configured as loan origination assistants | Boolean Underwriting F1, Account List Extraction, Income Reconciliation Precision | Baseline models achieve ~81% F1; document-grounded policy verification poses severe factual challenges | Does not enforce hardware RAM parity or token budgets; does not compare MAS vs quantized monolith architectures. |

---

## Part 3: Research Gap Synthesis

Based on the critical analysis and comparative cross-paper synthesis, we identify **four fundamental, unaddressed research gaps** in the contemporary literature:

### Research Gap 1: The Memory-Compute Hardware Parity Void
- *The Gap:* Existing research on agent architectures operates in two disconnected silos:
  1. *Token-Budget Camp (Tran & Kiela, 2026; Wang et al., EMNLP 2024):* Controls test-time token compute ($T_{\text{think}}$) but assumes identical model weights in unconstrained memory, completely overlooking hardware resident RAM/VRAM constraints.
  2. *Hardware Profiling Camp (Lin et al. Bench360, 2025):* Enforces hardware memory constraints (GB RAM/VRAM) but evaluates strictly single-model inference on general NLP tasks, never testing multi-agent systems.
- *Why It Matters:* In local, on-premise deployments (compliance analyst workstations), **system RAM is the binding physical ceiling**. No published study has compared a single quantized model against a multi-agent team where **both peak resident RAM (RUPP protocol) and thinking-token budgets ($T_{\text{think}}$) are simultaneously held invariant**.

### Research Gap 2: The Confounded Tool & Naive Baseline Fallacy
- *The Gap:* Literature evaluating small-agent collaboration (Żywot et al., 2026) claims multi-agent superiority by equipping small models with tools while comparing them against un-augmented monoliths. Conversely, literature declaring single-agent dominance (Tran & Kiela, 2026) compares off-the-shelf models on closed-book QA where agents suffer from unconstrained conversational drift.
- *Why It Matters:* Off-the-shelf comparisons are unscientific: a generic quantized model fails due to lack of domain adaptation (gaps S1–S12), while a generic multi-agent team fails from unstructured chatter and error cascades (gaps M1–M14). Prior work lacks an **"Improve-Then-Compare"** methodology where both arms are hardened with equal tools, domain adaptation, and strict communication contracts before final evaluation.

### Research Gap 3: Domain-Adapted Quantization vs. Verifier-Gated Multi-Agent Architecture
- *The Gap:* Jang et al. (2026) demonstrated that 4-bit quantization amplifies agent tool and grounding failures, while Singh & Pawar (2026) proved that multi-agent handoffs suffer from Markovian hallucination snowballs. However, neither work evaluated whether:
  - Targeted **domain fine-tuning (QLoRA)** on refusal discipline and strict tool calling can eliminate quantization vulnerabilities in the monolithic model.
  - An **independent, deterministic verifier boundary gate** (AHDS framework) can arrest hallucination snowballs in full-precision multi-agent teams.
- *Why It Matters:* The open scientific question is: *Does domain adaptation rescue the quantized monolith, or does architectural role specialization with boundary verification provide a superior buffer against factual errors under identical RAM?*

### Research Gap 4: Absence of Compliance-Aligned Grounding Evaluation in Regulated Document Workflows
- *The Gap:* Benchmark suites evaluate models on generic reasoning (MMLU-Pro, GSM8K) or software engineering (SWE-bench). Even recent financial benchmarks (MortarBench, 2026; Financial QA SME, 2026) report standard F1 accuracy without isolating compliance-critical failure modes under hardware constraints.
- *Why It Matters:* Regulated financial workflows (KYC/CDD entity verification, credit memo narrative drafting) have zero tolerance for ungrounded assertions. Prior work fails to evaluate systems along compliance-first dimensions: **Invention Rate** (fabrication of amounts/dates), **Mismatch Recall** (detecting document discrepancies), and **Refusal Correctness** (explicitly refusing to invent missing data).

---

## Part 4: Dataset Specifications for Fine-Tuning and Evaluation

To support the "Improve-Then-Compare" methodology and address the research gaps, Project Agere establishes a rigorous, leakage-free data pipeline:

### 4.1 Fine-Tuning Dataset for the Quantized Monolith (SAS-Quant)
The quantized monolithic baseline (Qwen2.5-14B-Instruct @ GGUF Q4_K_M on 16 GB RAM) is fine-tuned using **QLoRA (NF4)** on a curated 3-task domain adaptation mixture. After training, the LoRA adapter is merged into the 16-bit weights and **re-quantized to GGUF Q4_K_M** to strictly enforce the RAM ceiling:

1. **Task A: Refusal Under Missing Data (40% of mixture):**
   - *Target Problem:* Solves Gap **S2** (hallucinating missing information to be helpful).
   - *Data Construction:* Synthetic KYC document packs and credit files with intentionally omitted fields (e.g., missing CNIC issue date, unstated turnover, absent tax filing).
   - *Supervision Target:* The model is trained to output `"field_status": "MISSING"` or `"UNVERIFIED_IN_SOURCE"`. Any generated text that invents plausible dates or amounts is penalized with infinite loss.
2. **Task B: Deterministic Calculator & Extractor Tool Invocations (30% of mixture):**
   - *Target Problem:* Solves Gaps **S4 & S5** (arithmetic errors in prose, tool-call syntax brittleness under 4-bit quantization).
   - *Data Construction:* Input prompts paired with exact, schema-valid JSON tool calls to `financial_calculator` (for Debt Burden Ratio, DSCR, Current Ratio) and `document_extractor`.
   - *Supervision Target:* Forces the model to emit clean JSON tool calls without free-form arithmetic in autoregressive tokens.
3. **Task C: Verifiable Span Citation (30% of mixture):**
   - *Target Problem:* Solves Gap **S6** ("citation theatre" where models assert facts without valid document spans).
   - *Data Construction:* Document-to-memo drafting pairs where every factual predicate requires an exact document span pointer: `[Doc: Page X, Line Y: "Turnover: PKR 45.2M"]`.
   - *Supervision Target:* Strict alignment between cited span IDs and source document text.

### 4.2 Data Splits and Leakage Prevention Invariant
To ensure complete evaluation integrity:
- **Generation Seed Partitioning:** Training, dev, and test sets are generated using disjoint pseudo-random generator seeds.
- **Pre-Training Test Manifest Hashing:** Before any training step or adapter optimization begins, the complete test dataset is hashed (SHA-256) and stored in an immutable manifest (`AGERE_ROOT/manifests/test_manifest.sha256`) on the external NVMe storage.
- **Zero Evaluation Leakage:**
  - `Agere-KYC-Synth`: 400 cases Train, 100 cases Dev, 100 cases Test.
  - `Agere-Credit-Synth`: 200 cases Train, 50 cases Dev, 75 cases Test.
  - `MortarBench` (Track A) & `FRAMES/MuSiQue Slice` (Track D): **Zero training cases**; reserved strictly for evaluation.

---

## Part 5: Multi-Agent System (MAS) Engineering & Failure Mitigations

To eliminate the 14 documented multi-agent failure modes (Cemri et al. MAST, M1–M14) without quantizing weights, our full-precision team (MAS-FP16) implements the **Adaptive Hierarchical with Dynamic Pruning & Structured Communication (AHDS)** framework:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AHDS Architectural Pipeline                     │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   Case Documents (PDF / Text)                                          │
│         │                                                              │
│         ▼                                                              │
│   [Extractor Agent] ──────► Strict Pydantic JSON Schema (M1, M2)       │
│   (Qwen2.5-1.5B FP16)       - Passes UNKNOWN explicitly                │
│         │                   - Zero conversational prose                │
│         ▼                                                              │
│   [Policy Retriever] ─────► Permissioned Regulatory Snippets (M5)      │
│   (bge-small index)         - Filtered by product & jurisdiction       │
│         │                                                              │
│         ▼                                                              │
│   [Drafter Agent] ────────► Draft Memo with Span Citations (M4, M8)    │
│   (Qwen2.5-3B FP16)         - Stateless execution; bounded budget      │
│         │                   - Cites only Extractor JSON IDs            │
│         ▼                                                              │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │ Independent Verifier Boundary Gate (M3, M7, M13)             │     │
│   │ (Qwen2.5-1.5B FP16 + Deterministic String Matcher)           │     │
│   │ - Programmatic regex extraction of amounts, dates, names     │     │
│   │ - Substring verification against Extractor Document Cache    │     │
│   └──────────────────────────────┬───────────────────────────────┘     │
│                                  │                                     │
│                ┌─────────────────┴─────────────────┐                   │
│                │ PASS                              │ FAIL (Reject)     │
│                ▼                                   ▼                   │
│      [Human Compliance Officer]       [Regeneration / Error Packet]    │
│      (Sole Approval Authority)        (Max 1 retry pass; no loops)     │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### Specific Problem-to-Fix Mappings (Gaps M1–M14):
1. **M1 (Specification Drift):** Controlled via an explicit Standard Operating Procedure (SOP) embedded in the central Orchestrator with a deterministic Pydantic schema defining case completeness.
2. **M2 (Lossy Handoffs & DPI):** Eliminated by enforcing **JSON-only contracts**. Agents communicate exclusively via structured schemas. Missing fields are serialized as `"field_status": "MISSING"`; downstream drafters are programmatically barred from generating narrative text for missing values.
3. **M3 & M7 (Hallucination Snowball & Missing Verifier):** Mitigated by an **Independent Verifier Boundary Gate**. The verifier executes a deterministic substring match between drafted claims and source documents. If an amount or date cannot be grounded, the draft is rejected before reaching the human officer.
4. **M4 (Context Collapse):** Sub-agents are completely **stateless**. The active task constraint packet is injected fresh into each invocation, eliminating instruction dilution across chat histories.
5. **M5 (Inter-Agent Misalignment):** Policy retrieval queries are strictly scoped with case metadata (jurisdiction, product type, document IDs).
6. **M6 (Endless Debate Loops):** The topology enforces a **directed acyclic graph (DAG)**: one forward extraction pass, one drafting pass, and at most one repair pass upon verifier rejection. Multi-round open debate is structurally barred.
7. **M8 (Token Budget Fragmentation):** A dynamic scheduler allocates the thinking-token budget ($T_{\text{think}} = 2048$): Extractor 30% (~614 tokens), Retriever 10% (~205 tokens), Drafter 40% (~819 tokens), and Verifier 20% (~410 tokens). Verification tokens are reserved upfront.
8. **M9 (RAM Residency):** All sub-models remain concurrently resident in RAM. On the primary 16 GB tier: Orchestrator/Drafter (3B FP16, ~6.2 GB) + Extractor (1.5B FP16, ~3.1 GB) + Verifier (1.5B FP16, ~3.1 GB) + KV/runtime buffer (~3.4 GB) = 15.8 GB peak RSS.
9. **M10 (Weak Orchestrator):** Solved via **asymmetric parameter allocation** (Żywot et al., 2026): the orchestrator/drafter is assigned the largest model (3B FP16), while workers receive smaller, task-specialized checkpoints (1.5B FP16).
10. **M11 (Tool Call Races):** All document ingest is mediated through a single unified case store. Only the Extractor agent possesses tool permissions for `document_extractor`.
11. **M12 (No Domain Specialization):** Role prompts are enforced with specialized system schemas and optional role-specific LoRA adapters.
12. **M13 (Verification Theatre):** The verifier is constrained to a binary pass/fail checklist combined with hard-coded string matching, preventing sycophantic approval.
13. **M14 (Operational Latency & Debuggability):** Every inter-agent exchange emits a structured JSON log line recording elapsed time, token consumption, and peak RSS directly to the NVMe storage.

---

## 6. Execution Roadmap for Phase 2 & Beyond

Following the approval of Phase 1, the research group proceeds along the established roadmap:
- **Phase 2 (Baseline Freeze):** Deploy off-the-shelf Q4_K_M monolith and naive MAS pipeline; record baseline error rates across Tracks A–D.
- **Phase 3 (Hardening):** Execute QLoRA fine-tuning for SAS-Quant (with re-quantization to Q4_K_M) and deploy AHDS JSON contracts and Verifier gates for MAS-FP16.
- **Phase 4 (Head-to-Head Evaluation):** Benchmark hardened systems under 16 GB RAM and 2,048 thinking-token parity across 3 random seeds.
- **Phase 5 (Ablations & Deployment Guidance):** Deconstruct individual contribution of fine-tuning vs. architectural verifiers; submit findings for peer review.
