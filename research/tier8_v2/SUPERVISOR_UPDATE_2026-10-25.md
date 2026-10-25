# Supervisor update — 25 October 2026

The project has progressed from an unconvincing comparison into an instrumented
systems-development study with one real adaptation gain. A useful original method
and publication-quality validation have not yet been demonstrated.

## What improved

On the same repeatedly used 24 FinQA development questions:

| Experiment | Correct answers | Interpretation |
|---|---:|---|
| SAS7B Q4, two demos, direct answer | 7/24 | Earlier strong control |
| Same SAS with 128-token analysis | 13/24 | Measured reasoning-prompt improvement |
| MAS3B Q4, no analysis/demos, unadapted | 0/24 | Matched protocol control; all abstained |
| Same MAS with trained drafter adapter | 11/24 | Genuine matched adaptation gain |

The adapter was trained on 661 fitting training examples, with 100 train-only
validation examples and report-group exclusion from development. It was converted
to GGUF and verified to alter inference reversibly, rather than merely existing
on disk. Training used approximately 4.05GB peak allocated GPU memory; adapted
inference used approximately 3.90GB process-tree RSS. These are different memory
measurements. The host has more than8GB RAM; deployment is a simulated tier.

The adapted MAS delivered 10 correct and11 incorrect answers and withheld3.
Therefore, 11 correct candidate answers does not mean11 reliable deliveries.
Best SAS delivered13 correct and5 incorrect answers, withholding6. These best
conditions differ in prompts/training and are not a clean architecture-effect
estimate. SAS7B has not yet received equivalent adaptation.

## MAS weaknesses addressed and remaining

- Small-specialist capability: tried a 3B Q4 drafter and genuine task adaptation.
  Adaptation helped under the cap; pure MAS-FP16 and this quantized extension
  must remain separately labelled.
- Correlated errors and misleading handoffs: source-visible/independent checks,
  fallible handoffs and deterministic arithmetic reduce reliance on narratives.
  Lexically supported programs can still select the wrong measure, year or unit.
- Weak verification: the0.5B critic allowed11 incorrect deliveries after adaptation.
  A separately resident3B critic fit at4.82GB but withheld all24 cases. It failed
  to provide useful coverage; zero wrong deliveries alone is not success.
- Repair damage: implemented atomic field patches, preservation of unrelated
  claims, source-cell identities and arithmetic dependency/influence checks.
  The financial proof-feedback pilot corrected no answers beyond plain retry.
- Coordination cost: token ledgers, verified prompt accounting and sampled full
  process-tree memory expose costs. They measure overhead; they do not establish
  that MAS has become more efficient.

## Insights and novelty status

All24 adapted programs passed source-support/execution checks, but only11 were
answer-correct: syntactic grounding and executability do not establish semantic
correctness. A larger critic can collapse coverage. More reasoning is not monotonic:
128→256 analysis tokens changed SAS13→11 and left MAS at4; more table coverage
left SAS at13. These are local development observations, not new universal findings.
The original150 synthetic tasks were solved by deterministic rules, which showed
that the old benchmark could not establish a need for multi-agent reasoning.

No feature can currently be defended as both previously unused in research and
responsible for a validated gain. SFT/QLoRA, role decomposition, verification,
calculators, demonstrations and local repair all have close prior work recorded
in RELATED_WORK_MATRIX.md. The candidate remains a repair contract that preserves
unaffected evidence-dependent computations under joint memory/token limits.
It needs a distinction from prior methods and a useful controlled result.
The current negative repair pilot does not support that claim.

## External evaluation status

The SSD queue planned90 MortarBench and100 FRAMES questions for each original arm
(380 case–arm evaluations). At this check26 MortarBench SAS cases were saved,
with14 local exact matches; no arm completed and MAS/FRAMES had not started.
No evaluation controller or worker remained alive, and no terminal summary was
written. The cause is unknown. The stale running manifest was backed up and
marked interrupted with a separate observation. Raw outputs remain on the SSD.
Do not report the earlier5–8h estimate as a current completion promise.

This external run uses original unadapted systems, partial JSON/XML retrieval and
local exploratory scoring. It is not the official complete MortarBench protocol,
an adapted-system comparison, or a pristine held-out confirmation.

## Next research decisions

Recover the interrupted queue with explicit provenance and validated resume;
finish external paired baselines. Strengthen SAS comparably, train/evaluate the
verifier on naturally correct and incorrect programs, and measure wrong deliveries
and coverage together. Test a specific repair hypothesis against strong plain-retry,
independent-solving and full-regeneration controls at comparable expenditure.
Freeze systems before fresh report-disjoint confirmation and assess prior art
before claiming publication novelty.

## Subsequent verified diagnosis

A matched audit confirms identical initial plans and verifier prompts on all24
cases. The0.5B critic returns unanimousPASS on21; the3B critic rejects every case
and requests repairNONE on all24 despite failing checks. Thus the control exposes
an uncalibrated/protocol-inconsistent verifier, not a validated strong-verifier
baseline. Before further comparisons, assess balanced program discrimination on
training-only validation examples. This is an informative local result, not a
claim of new prior-art-free methodology.

Recovery code now preserves and validates completed prefixes in separate segments.
Its first launch was refused before model loading because available RAM was below
7.4GB; inference remains stopped. Boot metadata confirms a host reboot after the
last original sample, although the initial termination mechanism is unknown.

## Completed follow-up: critic discrimination, not just acceptance

A new96-review controlled probe used12 train-validation report groups, each with
an annotation-consistent reference and an executable, source-supported but
numerically incorrect operation mutation. Both0.5B and3B critics reviewed both
members using the existing rich protocol and a simpler verdict-only protocol.
Neither critic/protocol accepted the reference while rejecting its mutation for
any of the12 pairs.0.5B binary accepted11/12 of each class;3B returnedFAIL for every
rich review andUNKNOWN for every binary review. Simplifying the review protocol
did not fix useful discrimination. This supports strengthening role-specific
verification rather than assuming a bigger critic or easier format solves it.

These are controlled training-validation probes, not natural errors, independently
adjudicated semantic labels, or publication confirmation. Judge calibration,
contrastive negatives and framing controls have prior work added to the audit.
The probe is an informative negative result, not a new method. Both runs fit the
component cap; raw evidence stays on SSD. Full external recovery remains stopped
pending original7.4GB available-memory requirement.

## Critic baseline strengthening now underway

Constructed3522 balanced training/validation examples from training-only annotated
programs and valid-source executable single-edit negatives;3140 train and382
validation across414/49 disjoint report groups. Mutations cover operations and
source-operand substitution. All token sequences pass actual HF/GGUF parity;
weights/data/new logs live on SSD. These are weak numerical annotation labels,
not independently adjudicated semantic judgments or natural model errors.

The real2-update fit passed with504 changed adapter tensors and3.861GB peak GPU
allocation. Full one-epoch critic training is now live (393 planned optimizer
updates); subsequent conversion, applied-adapter proof and QA evaluation remain
required. No new correctness/novelty result follows from training progress. SAS
still needs comparable adaptation before an architecture comparison is defensible.

## Completed role-critic result

Full critic training completed393 updates over3140 examples. Conversion and actual
reversible application proof passed. On the matched controlled training-validation
probe, the trained critic accepted11/12 annotation-consistent references and0/12
wrong mutations;11/12 pairs separated, versus0/12 for the plain critic, which
returnedUNKNOWN throughout. This is23/24 gate decisions on constructed controls,
not95.8% financial-QA accuracy. Fine-tuning is established; novelty remains unproven.
The next running experiment measures whether this transfers to natural drafter
errors with identical actor outputs and verifier prompts. That result is pending.

## Latest authoritative result — natural-error transfer completed

Matched24-case no-repair comparison passed strict identical draft/prompt/actor
and separate critic-application guards. Plain binary3B:3 correct delivered,
0 wrong,21 withheld. Trained binary3B:11 correct,4 wrong,9 withheld (reported-answer
metric). Raw execution:2/1/21 versus9/6/9. Candidate accuracy remains11/24 reported
and9/24 raw; this is a gate effect, not answer generation improvement. Correct
coverage gains8/24 but wrong deliveries rise4/24; no Pareto dominance. Report-
cluster95% intervals for those deltas:[.167,.52] and[.04,.333]. Illustrative error
penalty break-even2, not a validated financial cost. Unit sidecar changes no cases.
Complete inner process-tree peaks:plain4.842GB,trained4.908GB under6.4GB decimal.
Evidence: `evidence/critic3b-natural24-delivery-results-01.json`.

Manual error hypotheses: missing future-period evidence (one case lacks annotated
row), missing net-of-allowance subtraction, inconsistent percent scaling, and wrong
pension measure/entity. These guide training-only natural-error controls; they are
not adjudicated semantic labels or license for gold-specific patches. Constructed
single-edit validation performance does not establish reliable natural verification.

External recovery02 is now genuinely running (controller40968/worker41022 observed),
preserving original26 cases. All FinQA queue stages1–9 passed. Broad100-report
inference, comparable SAS adaptation, useful novelty and publication confirmation
remain outstanding.212 tests pass. Earlier running/stopped statements are dated
history; LIVE_STATUS.md carries the latest snapshot.
