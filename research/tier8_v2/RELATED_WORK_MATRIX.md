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
