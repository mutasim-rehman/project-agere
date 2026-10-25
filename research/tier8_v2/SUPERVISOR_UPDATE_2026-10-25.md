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
