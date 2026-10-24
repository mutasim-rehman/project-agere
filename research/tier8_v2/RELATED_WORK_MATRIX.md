# Closest prior work — 24 October 2026

These records constrain novelty claims. A remaining gap is a hypothesis, not proof
of being first. Source scope is stated to distinguish methods read from abstracts.

| Work | Inspected scope and overlap | Consequence |
|---|---|---|
| [FinMAN / David vs. Goliath](https://aclanthology.org/2025.findings-emnlp.225.pdf) | Main method and evaluation: formula planning with MCTS, quantity retrieval/extraction, code execution, and stage-wise checking. The paper also examines thinking-token scaling and runtime. | Financial specialist decomposition, calculation tools, staged verification, and financial token-cost analysis are established. A host-RSS cap was not located in the inspected sections; inspect the code/appendix before asserting a gap. This is an important adapted baseline, not background to omit. |
| [The Hidden Cost of Structure](https://aclanthology.org/2025.ranlp-1.124/) | Published abstract: constrained generation can degrade instruction-tuned models; prompt adaptation and demonstrations matter. | Our protocol failures motivate stronger baselines, not a claim that small models inherently cannot reason. Full method review remains pending. |
| [Fine-tuning Smaller Language Models for Financial Documents](https://aclanthology.org/2024.findings-emnlp.617/) | Published abstract: program-oriented financial reasoning can improve through targeted small-model training. | Role adaptation and financial program fine-tuning are not novel by themselves. Our current models are untuned; optimality is not established. |
| [FinQA](https://aclanthology.org/2021.emnlp-main.300/) and [TAGOP/TAT-QA](https://aclanthology.org/2021.acl-long.254/) | Published task/method descriptions establish annotated reasoning programs and symbolic aggregation over selected evidence. | Source-quantity copying, arithmetic graphs, and deterministic calculation are strong baseline components. |
| [FinLFQA](https://aclanthology.org/2025.findings-emnlp.908/) | Published abstract includes evidence, numerical steps, and financial-knowledge attribution. | Finance attribution is broader than checking whether a quoted number appears in a line. |
| [FinChain](https://aclanthology.org/2026.acl-long.662.pdf) | Dataset and metric sections, PDF pp. 3–5: parameterized financial templates; semantic-embedding and numeric-result gating with DTW alignment; final-answer correctness uses 5% relative tolerance. | Verifiable financial traces and step-level evaluation are established. Useful supplementary controlled reasoning evaluation, not a replacement for real-document evidence. Do not transfer its 5% tolerance to our main answer metric; wrong financial measures can yield nearby numbers. Code/data adaptation pending; no data downloaded or held-out split opened. |
| [BudgetVerify](https://arxiv.org/html/2609.33052v1) | Introduction, methodology and experimental setup: train-only cost-aware router selects no verification, candidate-centered local revision, or independent solve-first/tool-grounded comparison. Uses pre-verification features; oracle correctness/cost appear only in offline training labels. | Adaptive financial verification depth, local-vs-full correction and token-cost routing are close established ideas. Our sampled RAM constraint and strict change contracts need a useful demonstrated distinction; adding a RAM cap to this router is insufficient as a novelty claim. No explicit host-RSS constraint found in the inspected sections; do not assert absence throughout paper/code. |
| [CIFQA](https://arxiv.org/abs/2608.26114) | Abstract only: specialized interpretation, routing, extraction, planning and response agents with deterministic financial tools, evaluated on fixed-deposit queries. | Financial role decomposition and deterministic rule execution are established. Full-method comparison pending; do not generalize its reported task results to our document QA setting. |
| [ThinkBrake](https://aclanthology.org/2026.findings-acl.1095/) | Published abstract: oracle stopping exposes correct intermediate solutions overwritten by later reasoning; log-probability margin stopping controls reasoning length. | Correct-intermediate recovery and overthinking are established. A selector over executable financial-program endpoints differs in representation, but requires useful evidence and full-method comparison before any originality claim. |
| [Diagnosing Numerical Capabilities](https://aclanthology.org/2022.emnlp-main.542.pdf) | Abstract/introduction: targeted numerical perturbations diagnose robustness and spurious correlations in numerical QA. | Numerical perturbation diagnostics are established. Exact symbolic value-influence checks use a different representation, but neither ordinary algebra nor a new perturbation suite alone establishes a useful original method. |
| [Towards Effectively Leveraging Execution Traces for Program Repair with Code LLMs](https://aclanthology.org/2025.knowledgenlp-1.17.pdf) | Introduction and setup, PDF pp. 1–3: failing-test and execution-trace prompts for complete function generation; includes alternative trace representations and confidence-conditioned representation selection. | Execution-guided repair and adaptive trace presentation are established. Their failing-test feedback differs from our financial setting without a known deployment answer; this difference is not itself a new algorithm. Trace inclusion alone cannot be the novelty. |

## Candidate contribution still requiring evidence

Bounded repair of an evidence-dependent computation graph, with explicit preservation
of unaffected components and allocation of a shared token budget under a measured
host-memory ceiling. Compare whole-program regeneration, local patches, independent
re-extraction, and stronger staged baselines. Measure false locks, wrong deliveries,
repair-induced regressions, token costs, context pressure, and memory.

Current pilots do not establish a useful repair gain. The proposed contribution must
survive comparison with FinMAN-style staging, CoVe-style independent checks, and
BRA-Audit-style localized recovery. Merely combining known components is insufficient.

## Development decisions

- Use training-only demonstrations and a formula/measure-identification stage as
  baseline controls for constrained-output failures.
- Expand evaluation beyond the two debug questions before interpreting accuracy.
- Keep both reported-answer and raw executable-reference metrics: the selected
  FinQA development slice contains mixed percentage conventions and disagreements.
- Do not promote synthetic parser success, valid JSON, source support, or a verifier
  PASS into evidence of financial correctness.
