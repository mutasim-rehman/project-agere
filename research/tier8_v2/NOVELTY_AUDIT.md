# Candidate novelty audit — 24 October 2026

This is a working research assessment, not a novelty certificate.

## Current falsification and next diagnostic

A further close prior, [VeriFin](https://arxiv.org/html/2608.10213v1), independently
grounds financial facts and authorized formulas, then uses symbolic constraint
feedback for repair. Read its method/setup; do not claim that formal financial
verification or targeted solver feedback is new. Its XBRL-backed authority is
stronger than our source-span membership checks; no replication has been run.


The controlled real-model proof pilot is now complete. On the stronger SAS output,
plain retry and symbolic feedback both made zero corrections and withheld the same
one wrong answer. Proof has no demonstrated accuracy benefit over retry. Only two
cases triggered; lower output tokens alongside higher prompt tokens cannot support
a general efficiency claim. Table-complete retrieval also left aggregate accuracy
unchanged (13/24). These are negative development findings, not contributions.


Endpoint repair has zero oracle gains on the stronger SAS analysis baseline;
its apparent headroom on weaker generation does not establish a useful method.
Exact functional-influence diagnostics now identify two wrong deliveries in that
stronger baseline whose cited quantities cancel algebraically. Standard symbolic
algebra is not novel, and cancellation can be legitimate. Four training sketches
also reveal ambiguous equal-value cell binding. Any proof-informed repair must
resolve this distinction, improve actual answers against a matched retry baseline,
and survive broader/frozen evaluation before becoming a contribution claim.

The closer-prior review now includes [BudgetVerify](https://arxiv.org/html/2609.33052v1),
whose method routes financial answers between no verification, local revision and
independent re-solving using offline correctness/cost supervision. Adaptive token
allocation across these options cannot be our originality claim. Strict dependency
preservation under a measured RAM ceiling is still only a hypothesis; its useful
distinction from existing local repair and routing has not been demonstrated.

| Prior work | Inspected scope | Consequence for Agere |
|---|---|---|
| [Self-Refine](https://arxiv.org/abs/2303.17651) | Abstract | Iterative self-feedback is established. |
| [CRITIC](https://arxiv.org/html/2305.11738v4) | Framework and introduction | External-tool verification followed by correction is established. |
| [CLR](https://arxiv.org/html/2608.11994v1) | Method, budget and scope | Critical-claim falsification and reliability-weighted candidate selection are established. CLR selects among generated candidates rather than constructing repaired answers. |
| [BRA-Audit](https://arxiv.org/html/2608.14668v1) | Algorithm 1 and system/method formulation | Trusted audit points, selective rollback, and re-auditing already exist. Localized recovery by itself is not a credible new contribution. |
| [Chain-of-Verification](https://aclanthology.org/2024.findings-acl.212/) | Published abstract and method summary | Independent verification questions that avoid conditioning on earlier answers are established. Blind re-extraction must be treated as a baseline, not claimed as a new idea. |

The remaining candidate is an empirically useful **transactional field-repair
contract under simultaneous RAM and token constraints**, evaluated in both SAS
and MAS. It must be distinguished from graph-localized recovery through its
field-level preservation rules, rejection behavior, and treatment of derived
dependencies. The KYC implementation preserves unrelated fact entries and
recomputes name mismatch. The financial implementation now audits arithmetic
dependencies and enumerates bounded single-edge reconnections, preserving
operations, quantities, units and other edges. This is a candidate mechanism,
not demonstrated novelty.

## Falsifiable hypotheses

1. Field patches reduce correct-to-incorrect transitions relative to full-answer
   regeneration at matched resource ceilings.
2. The benefit survives verifier false positives and false negatives; false locks
   do not offset preservation gains.
3. The effect remains on unfamiliar source layouts and independently sourced data,
   rather than only the synthetic generator used to develop the controller.
4. Under a memory ceiling, changing verification/repair allocation can outperform
   fixed allocation without merely moving errors into withheld answers.

Report correct delivered coverage, incorrect deliveries, withheld answers, field
accuracy, total tokens, prompt processing, latency, and memory. Accuracy restricted
to delivered cases cannot be the sole outcome.

## Evidence so far

- Original structured v1 development tasks are completely solved by rule-only
  parsing (150/150). That benchmark cannot establish the need for an LLM.
- Unit tests establish patch isolation and delivery-gate behavior only.
- Shared-weight MAS now fits with about 5.14 GB observed peak RSS. A four-case
  pilot improved correct delivered coverage from 0/4 to 1/4 but did not improve
  complete-answer correctness (1/4). Patch repair added tokens with no gains on
  those four cases. No architecture winner or novelty claim is established.
- The new 24-case KYC diagnostic is deliberately a pilot. It is still templated,
  lacks credit coverage, and requires stronger baselines and external validation.
- A generator-aware rule control also solves all 24 temporal KYC probes. Use them
  for mechanism regression, not as the sole evidence of a useful LLM contribution.
- Non-oracle lexical retrieval on the fixed first 24 FinQA development records
  retrieves all annotated evidence for 19/24. This is a retrieval diagnostic, not
  question-answering accuracy. Public benchmark contamination is unassessed.
- The 24-case MAS demonstration baseline has now completed: all 24 programs passed
  source-support/execution checks, but only one answer matched either numerical
  reference metric. Thirteen wrong answers passed the neural verifier. Stronger
  reasoning and verification baselines remain necessary before claiming a useful
  repair contribution. See RELATED_WORK_MATRIX.md for closer financial-QA priors.

## Next decisions depend on measurements

If a compact deterministic baseline also solves the new tasks, improve task
coverage rather than claim a model contribution. If both strong systems already
solve them, add realistic ambiguity and longer evidence; do not inject arbitrary
errors solely to produce gains. Fault injection may measure mechanisms separately,
but must be labeled and accompanied by naturally occurring error results.
