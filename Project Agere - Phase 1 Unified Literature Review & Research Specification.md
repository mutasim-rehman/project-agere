# Project Agere Phase 1 Literature Review and Research Specification

**Project title:** *Spend It Together or Spend It Big? Multi-Agent Full-Precision Teams vs. Quantized Monoliths on Analyst Workstation RAM for Regulated Finance*  
**Document:** Initial literature review and research specification  
**Date:** October 2026  
**Status:** Working draft for supervisor review

## Executive summary

Project Agere studies whether a small team of full-precision language-model agents can produce more grounded financial-document analyses than a single, larger quantized model when both systems run under the same workstation memory ceiling and reasoning-token budget. The intended tasks include KYC/CDD case-file review, credit memo drafting, and mortgage-document checks. The systems are decision-support tools: a qualified human remains responsible for final decisions.

Recent research offers evidence about agent coordination, orchestration, factual refinement, failure analysis, and local inference. Eight selected 2025 conference papers provide the peer-reviewed foundation in this draft. Six additional 2025–2026 preprints are treated as provisional supporting evidence, not as qualifying peer-reviewed publications. None of the reviewed work establishes the complete combination of financial documents, matched process memory, equal token budgets, equal tool access, and a quantized single-model baseline. That combination defines the proposed research gap.

## 1. Research context and question

Financial institutions may restrict or prohibit sending customer records to public cloud services, depending on jurisdiction, contract, data type, and internal policy. Local inference can reduce exposure to third-party services, but it does not by itself satisfy privacy, security, recordkeeping, or regulatory obligations. The project therefore focuses on on-premise or offline assistance over synthetic or otherwise approved data, with human review and auditable outputs.

The practical baseline is a single open-weight model quantized to fit available workstation memory. The alternative is a small orchestrated team with roles such as extraction, drafting, and verification. Project Agere compares these approaches on the same tasks and under the same resource and tool constraints.

> **Research question:** Can a multi-agent system of smaller full-precision models outperform a single larger quantized model on regulated-finance document workflows when both have the same effective process-tree RSS ceiling, reasoning-token budget, and tool access?

For the primary 16 GB tier, the nominal job RSS ceiling is 12.8 GB, reserving 20% of physical RAM for the operating system and background processes. The actual ceiling must be recalculated from host use before each run and may be lower. The locked resident MAS configuration is a 3B orchestrator/drafter, a 1.5B extractor, and a 0.5B verifier. These sizes are an experimental configuration, not a claim that every workstation can run them within the cap; measure peak RSS and reduce the smallest worker or context if required.

## 2. Literature synthesis

### 2.1 Token budgets and single-agent comparisons

Tran and Kiela’s 2026 preprint compares single-agent and multi-agent reasoning under matched thinking-token budgets on multi-hop question answering. Its central methodological contribution for this project is the need to control test-time computation. Its benchmark setting does not establish performance on document-grounded finance tasks, local CPU inference, or a shared physical-memory ceiling. The paper’s information-theoretic discussion motivates testing structured handoffs, but does not prove that every multi-agent handoff is necessarily harmful in every workflow.

### 2.2 Orchestration and specialization

Peer-reviewed work at NeurIPS, ICLR, and ACL studies dynamic agent scheduling, actor–critic collaboration, learned role differentiation, and decentralized retrieval-based networks. Collectively, these methods show that topology and role design are meaningful variables. They also introduce training, coordination, and runtime costs that need to be counted in a local deployment comparison. The studies do not establish which architecture is best under the project’s RAM and token parity controls.

### 2.3 Failure modes and task dependence

Cemri et al.’s NeurIPS 2025 MAST study builds a taxonomy of 14 multi-agent failure modes from execution traces and groups them into system-design, inter-agent-misalignment, and task-verification categories. It provides a useful vocabulary for error analysis, but it is not itself a resource-matched intervention study. MedAgentBoard finds that the value of collaboration depends on the task: multi-agent systems can help in some clinical workflows without consistently outperforming single-model or conventional methods. Collab-Overcooked likewise reports that strong goal interpretation does not guarantee sustained coordination or adaptation. These findings support task-specific comparisons instead of assuming that additional agents always help.

### 2.4 Factuality and iterative review

MAMM-Refine evaluates collaborative error detection, critique, and correction for summarization and long-form question answering. It reports that reranking candidate critiques and revisions can improve results compared with unconstrained revision generation. This is relevant to drafting and verification, but its tasks do not measure financial claim grounding, numerical discrepancy detection, or justified refusal when source documents are incomplete.

### 2.5 Quantization, local inference, and finance benchmarks

Bench360 (2025 preprint) proposes measuring both task quality and system characteristics such as inference performance, resource use, and deployment behavior across local configurations. It does not evaluate multi-agent systems or establish that a particular quantized model universally dominates a smaller full-precision model. Jang et al. (2026 preprint) investigate tool-calling behavior under quantization and show why aggregate task scores can hide process errors. MortarBench (2026 preprint) contributes a mortgage-origination benchmark with document-grounded questions, while Singh and Pawar (2026 preprint) analyze error propagation in a financial multi-agent pipeline. These are directly relevant research leads, but their preprint status should remain explicit until peer-reviewed publication is confirmed.

## 3. Cross-paper comparison matrix

The matrix separates peer-reviewed conference papers from preprints. Findings are summarized rather than copied. Check each full paper for exact preprocessing and metric definitions before submitting a final version; this draft does not infer details that are not established by the paper record or source notes.

### Peer-reviewed conference papers

| # | Paper and task/method | Evaluation and reported finding | Limitation or gap for Project Agere |
|---:|---|---|---|
| 1 | **Cemri et al. (2025), MAST — NeurIPS Datasets and Benchmarks.** Builds a taxonomy from 150 expert-analyzed traces and scales annotation across 1,600+ traces from seven frameworks. | Reports inter-annotator agreement and analyzes 14 failure modes grouped around system design, inter-agent misalignment, and task verification. | Diagnostic corpus, not a RAM-matched finance intervention; does not compare MAS-FP16 with SAS-Quant. |
| 2 | **Zhu et al. (2025), MedAgentBoard — NeurIPS Datasets and Benchmarks.** Compares multi-agent, single-LLM, and conventional approaches across medical QA/VQA, summaries, EHR prediction, and clinical workflows. | Task-specific performance across four medical task families; MAS helps in some workflows but has no consistent advantage. | Medical domain and modalities differ from finance; no local RAM or reasoning-token parity. |
| 3 | **Dang et al. (2025), Multi-Agent Collaboration via Evolving Orchestration — NeurIPS.** Uses an RL-trained centralized orchestrator to schedule agents for closed- and open-domain scenarios. | Evaluates task performance and computational cost; reports improved performance with reduced cost and compact reasoning structures. | Does not establish equal peak RSS or compare against a quantized monolith on financial documents. |
| 4 | **Estornell et al. (2025), ACC-Collab — ICLR.** Trains an actor–critic two-agent team on collaboration benchmarks. | Reports performance against existing multi-agent methods across benchmarks. | Does not establish local deployment cost or an equal-resource single-model comparison. |
| 5 | **Wan et al. (2025), MAMM-Refine — NAACL.** Studies multi-agent error detection, critique, and revision on three summarization datasets and long-form QA. | Intrinsic refinement and end-task quality/faithfulness measures; reranking candidate critiques improves results over unconstrained revision generation. | No financial documents, monetary grounding measures, or RSS parity. |
| 6 | **Li et al. (2025), Advancing Collaborative Debates with Role Differentiation — ACL.** Learns role embeddings and turn-aware role differentiation across seven datasets. | Task-specific performance; authors report improved collaboration and expertise. | Training cost, financial auditability, and workstation resource parity remain untested. |
| 7 | **Sun et al. (2025), Collab-Overcooked — EMNLP.** Evaluates 13 LLMs on Overcooked-AI and 30 open-ended interactive tasks. | Outcome and process-oriented collaboration measures; finds weaknesses in active collaboration and continuous adaptation. | Game tasks do not test document evidence, financial rules, or compliance decisions. |
| 8 | **Yang et al. (2025), AgentNet — NeurIPS.** Uses decentralized retrieval-based agents arranged as a directed acyclic graph. | Evaluates task performance and collaboration; proposes decentralized capability evolution. | Distributed setting differs from a single analyst workstation; no matched-RAM quantized baseline. |

### Provisional preprints

| # | Paper and task/method | Evaluation and reported finding | Limitation or gap for Project Agere |
|---:|---|---|---|
| 9 | **Tran and Kiela (2026), equal thinking-token budgets.** Compares single-agent and multi-agent topologies on FRAMES, MuSiQue, and HotpotQA. | Reports Exact Match, F1, and reasoning behavior; SAS can match or outperform MAS on the tested tasks. | Preprint; not finance-document evaluation and does not measure physical RAM parity. |
| 10 | **Kim et al. (2025), Towards a Science of Scaling Agent Systems.** Compares five topologies across 180 configurations and three model families on Finance-Agent, BrowseComp-Plus, PlanCraft, and Workbench. | Predictive scaling analysis finds task dependency structure moderates whether adding agents helps. | Preprint; does not answer local memory-constrained deployment. |
| 11 | **Stuhlmann et al. (2025), Bench360.** Benchmarks four task families across three hardware platforms and four inference engines. | Measures task and system outcomes, including accuracy/F1, latency, throughput, energy, and deployment behavior. | Preprint; does not evaluate multi-agent finance workflows or matched MAS/SAS under one RSS cap. |
| 12 | **Jang et al. (2026), Flat Score, Amplified Failures.** Compares 16-, 8-, and 4-bit quantization on τ²-Bench tool-calling episodes across two model families and two domains. | Compares aggregate task reward with logged process-level tool/entity errors; shows aggregate scores can mask error increases. | Preprint; does not evaluate financial documents or whether domain adaptation changes the result. |
| 13 | **Singh and Pawar (2026), The Hallucination Snowball.** Injects hallucinations into a four-agent financial-analysis pipeline using FinanceBench and tests boundary verification. | Measures stage-level detection and hallucination survival; reports boundary checks can reduce propagation. | Preprint; results require independent replication and do not compare equal-memory SAS-Quant. |
| 14 | **Toles et al. (2026), MortarBench.** Creates synthetic mortgage-origination questions and document packs and proposes confidence calibration. | Reports exact-match accuracy and calibration; finds errors in current systems and gains from calibration. | Preprint; no workstation RAM or token parity and no direct MAS-FP16 vs. SAS-Quant comparison. |

## 4. Research-gap synthesis

### Gap 1: Memory and compute parity

Token-budget studies do not measure process memory, while local-inference benchmarks generally do not compare a team of resident full-precision agents against a quantized monolith. A controlled experiment should match the effective process-tree RSS ceiling and reasoning-token budget, and report actual peak RSS for each case.

### Gap 2: Equal tools and fair baselines

An apparent architecture advantage can be confounded if only one system has access to retrieval, calculators, or document-extraction tools. The SAS and MAS arms should receive the same tools, source material, and output schema. Compare both unadapted baselines and improved systems so results do not depend on a deliberately weak baseline.

### Gap 3: Domain adaptation and verifier value

The selected studies do not settle whether domain adaptation can improve a quantized monolith’s performance on structured finance tasks, or whether a specialized full-precision team offers an advantage under the same constraints. Evaluate domain-adapted SAS-Quant and verifier-gated MAS-FP16 under a common protocol, and use ablations to isolate the contribution of adaptation and verification.

### Gap 4: Compliance-aligned grounding measures

General task success alone does not capture the errors that matter in document review. In addition to task completion, evaluate:

- **Invention rate:** unsupported amounts, dates, entities, or other claims.
- **Planted mismatch recall:** deliberately introduced discrepancies correctly identified across documents.
- **Refusal correctness:** appropriate abstention when required evidence is missing or contradictory.
- **Citation accuracy:** claims linked to the correct source document and span.
- **Operational outcomes:** latency, token use, and peak process-tree RSS.

## 5. Dataset design and leakage controls

The evaluation should use synthetic KYC/CDD, credit, and mortgage document packs with known ground truth. Include missing fields, contradictory records, numeric edge cases, and policy-relevant scenarios. Any public benchmark or template documents must be checked for license and permitted use before inclusion.

The adapted SAS-Quant training data should cover three behaviors:

1. **Missing-data handling (40%):** produce an explicit missing or unverified status instead of inventing a value.
2. **Structured tool invocation (30%):** call deterministic calculators with schema-valid arguments for ratios such as DTI/DBR, DSCR, and current ratio.
3. **Span-grounded citations (30%):** attach every factual statement to an exact document and span identifier.

Generate train, development, and test packs from disjoint synthetic seeds. Freeze and hash the evaluation manifest before fine-tuning. Do not use evaluation cases, labels, or near-duplicates in adaptation. Record generation scripts, seed values, document mutations, and manifest hashes so the benchmark can be reproduced.

## 6. System specification

### 6.1 SAS-Quant

- **Locked primary model:** Qwen2.5-14B-Instruct, converted to GGUF Q4_K_M, subject to the effective RSS ceiling.
- **Adapted condition:** QLoRA NF4 fine-tuning on the training split, merge, then re-quantize to Q4_K_M for evaluation.
- **Staged prompting:** extraction, policy retrieval/checking, then memo drafting. The stages are deterministic prompt stages on the same model, not separate resident model instances.
- **Tools:** the same local extractor, policy retriever, calculator, and citation checker available to MAS-FP16.

### 6.2 MAS-FP16

The locked 16 GB resident configuration has three generative models: Qwen2.5-3B-Instruct for orchestration and drafting, Qwen2.5-1.5B-Instruct for extraction, and Qwen2.5-0.5B-Instruct for verification. A shared local embedding retriever is not counted as a generative agent, but its memory is included in the job RSS measurement.

Inter-agent messages use validated structured data rather than unconstrained conversational prose. The extractor records missing or unreadable fields explicitly. The drafter cites extracted field or source-span identifiers. A verifier checks claims against source material and routes failures to a bounded retry. A deterministic calculator handles financial arithmetic. These are proposed controls to evaluate, not assumed guarantees of correctness.

### 6.3 Project risk-and-control mapping

The controls below are Project Agere design choices informed by the literature; they are not the official MAST failure-mode codes.

| Project risk | Proposed control |
|---|---|
| Requirement or output drift | Stable task instructions and schema validation |
| Lossy or ambiguous handoffs | Typed JSON fields, source identifiers, and explicit missing-value states |
| Unsupported claims or propagated errors | Independent evidence checks at the draft boundary; deterministic matching where appropriate |
| Citation mismatch | Verify each citation against the original document span |
| Retrieval contamination | Filter local policy materials by jurisdiction and product type; record the retrieved source |
| Premature agreement | Independent extraction before narrative synthesis |
| Token exhaustion or repeated loops | Per-stage quotas, bounded retries, and a fixed global reasoning-token cap |
| Memory overrun | Enforce and log the effective process-tree RSS ceiling; shrink the smallest worker or context if needed |
| Untraceable behavior | Log model/config versions, prompt stages, tool calls, token usage, latency, and peak RSS |

## 7. Experimental protocol and primary measures

### 7.1 Resource and task controls

- **Primary machine tier:** 16 GB physical RAM, CPU-first inference using llama.cpp.
- **Nominal RSS ceiling:** 12.8 GB, or a lower host-adjusted cap when idle use and required safety headroom demand it.
- **Memory protocol:** apply the same cap to the complete process tree for each arm; include model weights, KV cache, retriever, runtime, and tools. Report resident MAS as the primary mode and sequential load/unload as a supplementary deployment mode.
- **Reasoning budget:** use the locked per-case cap of 2,048 thinking tokens, and report the token accounting method. The cap is shared across the stages of each system.
- **Tool parity:** provide equivalent extraction, policy retrieval, deterministic calculation, and citation checking to both systems.
- **Human review:** outputs are drafts and flags only. No automated credit approval, risk rating, or regulatory filing.
- **Negative control:** include a no-document multi-hop QA slice such as FRAMES or MuSiQue to test whether results depend on the finance-document setting.

The 20% reserve and 12.8 GB cap are nominal starting values, not guarantees that a particular host can sustain that limit. Before each run, record total and idle host memory, compute the effective cap, and apply it equally to both arms. Record actual peak process-tree RSS and latency for every case.

### 7.2 Primary measures

| Measure | Definition |
|---|---|
| Invention rate | Frequency of unsupported facts, amounts, dates, or entities in outputs |
| Planted mismatch recall | Share of deliberate cross-document conflicts correctly flagged |
| Refusal correctness | Correct abstention when required evidence is absent or inconsistent |
| Citation accuracy | Share of factual claims linked to a correct source span |
| Task completion | Correct completion of the task-specific extraction, reconciliation, or drafting objective |
| Resource use | Peak process-tree RSS, reasoning tokens, and wall-clock latency per case |

Use paired cases for MAS/SAS comparison. Report confidence intervals and per-task breakdowns; do not collapse safety-relevant errors into a single score without showing their individual rates. Statistical tests and sample sizes should be finalized before running the confirmatory evaluation.

## 8. References and publication status

### Peer-reviewed conference papers selected for the 2025 literature review

- Cemri, M. et al. (2025). “Why Do Multi-Agent LLM Systems Fail?” *NeurIPS 2025, Datasets and Benchmarks Track.* [Proceedings record](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html)
- Dang, Y. et al. (2025). “Multi-Agent Collaboration via Evolving Orchestration.” *NeurIPS 2025.* [Proceedings record](https://proceedings.neurips.cc/paper_files/paper/2025/hash/f1320d2e2842169c6fc89dcbd80e94d0-Abstract-Conference.html)
- Estornell, A. et al. (2025). “ACC-Collab: An Actor-Critic Approach to Multi-Agent LLM Collaboration.” *ICLR 2025.* [Proceedings record](https://proceedings.iclr.cc/paper_files/paper/2025/hash/e187897ed7780a579a0d76fd4a35d107-Abstract-Conference.html)
- Li, H. et al. (2025). “Advancing Collaborative Debates with Role Differentiation through Multi-Agent Reinforcement Learning.” *ACL 2025.* [ACL Anthology](https://aclanthology.org/2025.acl-long.1105/)
- Sun, H. et al. (2025). “Collab-Overcooked: Benchmarking and Evaluating Large Language Models as Collaborative Agents.” *EMNLP 2025.* [ACL Anthology](https://aclanthology.org/2025.emnlp-main.249/)
- Wan, D. et al. (2025). “MAMM-Refine: A Recipe for Improving Faithfulness in Generation with Multi-Agent Collaboration.” *NAACL 2025.* [ACL Anthology](https://aclanthology.org/2025.naacl-long.498/)
- Yang, Y. et al. (2025). “AgentNet: Decentralized Evolutionary Coordination for LLM-based Multi-Agent Systems.” *NeurIPS 2025.* [Proceedings record](https://proceedings.neurips.cc/paper_files/paper/2025/hash/9a379c1b05793d1c42dc832269834515-Abstract-Conference.html)
- Zhu, Y. et al. (2025). “MedAgentBoard: Benchmarking Multi-Agent Collaboration with Conventional Methods for Diverse Medical Tasks.” *NeurIPS 2025, Datasets and Benchmarks Track.* [Proceedings record](https://proceedings.neurips.cc/paper_files/paper/2025/hash/d59aa09699530c00d4b875a883876641-Abstract-Datasets_and_Benchmarks_Track.html)

### Provisional preprints used as supporting evidence

These are not counted among the eight peer-reviewed conference papers above. Confirm publication status and venue before presenting them as qualified studies.

- Jang, J. et al. (2026). “Flat Score, Amplified Failures: How the Error Budget Masks Damage in Quantized LLM Agents.” [arXiv:2607.27275](https://arxiv.org/abs/2607.27275)
- Kim, Y. et al. (2025). “Towards a Science of Scaling Agent Systems.” [arXiv:2512.08296](https://arxiv.org/abs/2512.08296)
- Singh, P. and Pawar, B. (2026). “The Hallucination Snowball: Modeling Error Propagation as State Transitions in Multi-Agent LLM Pipelines.” [arXiv:2608.14588](https://arxiv.org/abs/2608.14588)
- Stuhlmann, L. et al. (2025). “Bench360: Benchmarking Local LLM Inference from 360°.” [arXiv:2511.16682](https://arxiv.org/abs/2511.16682)
- Toles, M. et al. (2026). “MortarBench: Evaluating Mortgage Loan Origination Agents.” [arXiv:2606.19416](https://arxiv.org/abs/2606.19416)
- Tran, D. and Kiela, D. (2026). “Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets.” [arXiv:2604.02460](https://arxiv.org/abs/2604.02460)
