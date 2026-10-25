# Closest prior work — 24 October 2026

These records constrain novelty claims. A remaining gap is a hypothesis, not proof
of being first. Source scope is stated to distinguish methods read from abstracts.

| Work | Inspected scope and overlap | Consequence |
|---|---|---|
| [LRAgent](https://arxiv.org/abs/2602.01053v2) | Abstract v2: role-specific LoRA agents share a backbone; proposed base/low-rank KV sharing includes a shared-A variant. | Shared role adapters and memory-efficient multi-agent serving are established. Our KV resets preserve isolation; neither role adapters nor switching alone can be an originality claim. No replication or full-method review yet. |
| [MapCoder-Lite](https://arxiv.org/abs/2509.17489v2) | Abstract v2: agent-wise LoRA over a small coding model, trajectory distillation and supervisor-guided correction. | Role-specific low-rank adaptation is a useful stronger baseline, not itself a new contribution. Coding-domain results are not our financial results. |
| [DAC](https://arxiv.org/abs/2606.10684v2) | Abstract v2, revised title Cross-Agent Learning Signals Enable Coordinated Role-Decomposed LLM Training: role-specific cross-verification rewards and hard-positive evidence for abstention control. | Training distinct roles and controlling over-abstention have close priors. A future learned critic needs a measured distinction and appropriate data/credit controls. Full method not inspected. |
| [VeriFin](https://arxiv.org/html/2608.10213v1) | Method §§3.1–3.6 and setup §§4.1–4.2: independent XBRL concept/period/unit binding, external formula authority, Z3 checks and named-constraint feedback. Code/data link is present. | Source-grounded formal verification and targeted financial repair are close prior work. Our current span support and algebraic cancellation checks do not establish those semantic guarantees. No replication performed; paper-reported outcomes are not our results. |
| [Encore](https://aclanthology.org/2024.acl-long.582/) | Published abstract only: formula-derived reasoning targets and synthetic pretraining for numerical reasoning. | Generating executable training traces from annotated formulas is established. Full method not yet inspected. |
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
| [DCRC](https://arxiv.org/html/2605.31064v1) | Main method/setup: adversarial training data, structure-aware SFT and GRPO; shared source-labelled evidence, task routing, symbol binding with conflict/missing states and deterministic operators. Uses Qwen2.5 1.5B/3B/7B. | Financial source auditing, compilation and auditable execution are established. Our untuned systems do not establish small-model capacity ceilings. Functional-influence feedback needs a useful distinction and stronger training/protocol controls; no DCRC replication has been performed. |
| [VerityMath](https://openreview.net/notes/edits/attachment?id=LxmHG5LQy1&name=pdf) | Abstract and method sections: unit-annotated programs with assertion checks, generated training targets and fine-tuned 7B models; reported variants slightly underperform plain program baselines. | Formal checks inside reasoning programs are established and need not improve accuracy. Unit consistency differs from value-influence analysis, but adding a checker does not by itself establish utility or originality. |
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

## Critic-calibration screening — 25 October 2026

Primary abstracts inspected via web during the train-only critic probe:

| Work | Inspected scope | Consequence |
|---|---|---|
| [Mitigating the Bias of Large Language Model Evaluation](https://aclanthology.org/2024.ccl-1.101/) | Published abstract: probability/prompt calibration and contrastive training with curated negatives for judge bias. | Calibrating a critic or training on negatives is established; our probe is baseline diagnosis, not an original method. Full method not yet inspected. |
| [Don’t Judge Code by Its Cover](https://aclanthology.org/2026.findings-eacl.70/) | Published abstract: correctness judgments shift with superficial code variations; positive and negative judge biases persist across models. | Finding an unreliable program critic alone is not new. Financial counterfactuals and memory constraints still require a useful methodological distinction. Full method not yet inspected. |
| [The yes-no bias of large language models reflects answer order and wording, not shifts in moral judgment](https://arxiv.org/abs/2607.05552) | arXivv1 abstract: balanced framing/label-order controls separate verdict, lexical label and option-order effects in moral judgments. | Label remapping, format robustness and balanced calibration batteries have close priors. Different domain; do not transfer reported results to our finance critics. Full method not yet inspected. |

Our rich-versus-binary experiment changes instruction content as well as output
format. It cannot identify a pure grammar, label-order or lexical-bias mechanism.
Do not promote a protocol improvement into a first-use or novelty claim.

## Role-cache optimization screen — 25 October 2026

| Work | Inspected scope | Consequence |
|---|---|---|
| [LRAgent v2](https://arxiv.org/html/2602.01053v2) | Method§3.2 and AppendixC.2, extending the earlier abstract-only read: shared base/low-rank caches, approximate cross-role states, and shared-A training. | Backbone sharing, low-rank cache decomposition and shared-A role adapters are close priors. We have not replicated them; cached states across different adapters cannot simply be treated as exact. |
| [ForkKV](https://arxiv.org/abs/2604.06370) | Primary abstract: copy-on-write disaggregated shared/agent-specific caches and specialized reconstruction kernel. | Copy-on-write multi-LoRA cache storage is established; no first-use claim for a shared-role runtime. Full method not inspected. |
| [PReCache v2](https://arxiv.org/abs/2609.34054) | Primary abstract: precomputed role-specific low-rank states and adapter-neutral reconstruction; direct cross-role reuse can weaken specialization. | Role-specific cache correction/neutralization is close prior work. Full method not inspected. |
| [Shared-Prefix KV Reuse Across Standard LoRA Adapters](https://arxiv.org/abs/2609.17109) | Primary abstract: takeover-boundary quality/cost sweep; reported latency benefit does not imply physically shared storage or quality equivalence. | Reuse boundaries and quality/serving tradeoffs already have direct investigation. Full method not inspected; no transfer of paper-reported gains to our models. |

Current frozen runs retain KV reset on every model call. No cross-role cache reuse
or shared-backbone implementation was added during this screen. Exact same-policy
prefix reuse may be a useful future baseline optimization; it is not automatically
novel and needs measured output/cost controls. Keep active evaluation sources fixed.

## 25 October2026 — Risk-selection prior-art screen (abstracts only)

| Primary source | Relevant overlap | Consequence for this project |
|---|---|---|
| [SHIP](https://arxiv.org/abs/2608.21748),22Aug2026 | Replays complete verifier-guided image-generation policy on held-out prompts; candidate calibration need not control released-output risk | Whole-policy risk/coverage calibration alone is not a new principle; different image domain does not erase overlap |
| [SAFER](https://arxiv.org/abs/2510.10193),v3,16Feb2026 | LLM sampling cap calibrated with held-out exact intervals, abstention and conformal filtering | Budget-aware sampling/filtering with risk control is established prior art |
| [Audit-First VAPO](https://arxiv.org/abs/2609.33662),v2,16Oct2026 | Selective learning updates under imperfect verification; freeze action traces before labels, finite verification budgets and simultaneous risk/coverage/call bounds | Accept/appeal/abstain plus bounded secondary verification is not enough to claim originality |

Primary abstracts read; full methods and assumptions have not been audited.
These constrain novelty claims, not establish direct task equivalence or validate
our weak numerical labels. Natural-error adaptation and risk/coverage accounting
are useful baseline strengthening, not claimed new algorithms. Any proposed
bounded repair mechanism needs a concrete distinction and a measured gain.
