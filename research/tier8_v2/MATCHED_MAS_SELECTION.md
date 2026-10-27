# First matched natural MAS comparison

Both52-case runs completed on15 reports excluded from fitting. Exact initial
actor responses, prompts, usage and plans match. The same critic initializer,
optimizer, update count and positive/rehearsal/validation exposure were used;
negative examples differ under the frozen recipe. All prompts, execution,
review/repair, delivery, scores, token ledgers and memory samples independently
replay. No new generations were made by the auditor.

| Metric | Control | Crossed |
|---|---:|---:|
| Correct delivered, reported metric |3|3|
| Wrong delivered, reported metric |19|15|
| Correct delivered, raw metric |5|5|
| Wrong delivered, raw metric |17|13|
| Withheld |30|34|
| Prompt tokens |162851|170007|
| Generated tokens |4662|4900|
| Recorded inference seconds |2050.7|2136.1|
| Sampled peak RSS, GB |5.060|5.067|

Five wrong deliveries become withheld; one withheld case becomes a new wrong
delivery. Every observed correct delivery remains delivered. Thus the predeclared
exploratory rule passes under both metrics: net four fewer wrong deliveries and
no loss of correct deliveries. Correct answer generation itself does not improve.
Absolute task performance remains weak.

Across15 whole-report clusters, the95% bootstrap interval for change in wrong
deliveries per case is[-0.1739,+0.0204]. It includes zero and slight harm. The
zero-width correct-delivery interval reflects no observed changes, not population
equivalence. One seed and public training-source report holdouts do not establish
confirmation, pretraining cleanliness or financial semantics.

Control30 repairs changed11 programs; crossed34 changed12. In BOTH conditions,
every case's delivery and both correctness indicators equal its no-repair prefix.
The measured improvement comes from initial gating, with no observed correction
gain. Prefixes are measured trajectory ablations, not fresh standalone runs.
Crossed repair overhead71181 prompt/1793 generated tokens and875.0 seconds yields
no measured outcome change here. Both full policies stay below6.4GB sampled RSS.

The strong ORIGINAL critic with this same actor has now completed. The crossed
condition loses one correct delivery against it, so it fails the no-loss rule;
see the full comparison below. Beating the matched continuation alone does not
establish overall superiority or novelty. The49-case reserved diagnostic audit and SAS study
remain required. No recipe, threshold, case, prompt or scoring changes are made
from this result. Existing contrastive/bundle-training literature remains relevant.

[Paired full audit](evidence/matched-mas-selection-paired-01.json) ·
[Control replay](evidence/matched-control-natural-complete-01.json) ·
[Crossed replay](evidence/matched-crossed-natural-complete-01.json).


## Strong-original result: adoption requirement fails

Same52 cases, same actor; initial plans/responses/prompts/usage verified exactly
identical across all THREE critic conditions. Original critic reported4 correct
/22 wrong/26 withheld, raw6/20/26. Crossed reported3/15/34, raw5/13/34.
Ten original wrong deliveries become withheld, THREE new wrong deliveries appear,
and one previously correct delivery becomes withheld. Net7 fewer wrong deliveries
comes with one fewer correct delivery under both metrics. The predeclared sample
Pareto/no-correct-loss rule therefore FAILS against the original.

Report-cluster95% wrong-rate delta interval[-0.2549,-0.0185]; correct-delivery delta
interval[-0.0588,0]. These are exploratory15-report intervals, not a license to
choose a post-hoc error penalty or claim population equivalence/safety. One seed.
Original full inference153639 prompt/4492 generated tokens,1929.1 seconds versus
crossed170007/4900/2136.1. Both run under6.4GB sampled tree RSS.

Do not adopt the crossed method or call it a new best system from these results.
Absolute correct generation remains4 reported/6 raw out of52 for the common actor.
SAS training and the fixed reserved audit continue. Strengthening actor generation,
reference fidelity and critic calibration remain future controlled research;
selection cases must not become training examples or ad-hoc rules.

[Full original comparison](evidence/matched-mas-original-selection-01.json).

## Post-hoc reference-coverage stratification

All52 cases remain in the full metrics. Reference-dependent categories are only
exploratory diagnostics, unavailable at deployment; they cannot become routing
features, exclusions or selection-case training labels.

| Existing-parser category | N | Control correct/wrong/withheld | Crossed | Original |
|---|---:|---|---|---|
| Directly mappable reference |23|3 /6 /14|3 /6 /14|4 /9 /10|
| Missing annotated operand in catalog |16|0 /6 /10|0 /2 /14|0 /7 /9|
| Numeric literal parser failure |9|0 /4 /5|0 /4 /5|0 /4 /5|
| Unsupported annotated operation |4|0 /3 /1|0 /3 /1|0 /2 /2|

Table uses the unchanged reported-answer metric. All net four wrong-delivery
reductions versus matched control lie in the missing-operand category. Within
directly mappable cases, one wrong delivery is prevented and one introduced,
leaving aggregate outcomes unchanged. This does NOT establish a general semantic
verification improvement or a causal explanation of the learned mechanism.

All four initial reported-correct candidates occur in the directly mappable23,
but19/23 are still initially wrong. Representation coverage alone is insufficient.
One initial raw-reference match also occurs in the unsupported-operation group:
exact reference-program mapping is not a task-solvability ceiling. Numeric matches
are not independent financial semantic adjudication.

The stronger-original adoption rule still fails. No metrics, criteria, thresholds
or cases changed; report groups overlap across strata and no post-hoc significance
tests are claimed. [Verified stratification](evidence/mas-representation-strata-01.json).


## Later reserved diagnostic audit — 49 cases / 15 reports

Full-trace paired analysis completed: reported control4/17/28 versus crossed4/9/36
(correct/wrong/withheld), raw8/13/28 versus7/6/36. Crossed reduces wrong deliveries
but loses one raw-correct delivery and withholds eight more. It FAILS the existing
both-metric adoption criterion. Do not choose only the favorable reported metric
or describe this as a general quality improvement. This is a reserved diagnostic
from public training-source reports, not clean publication confirmation.
[Direction review evidence](evidence/research-direction-audit-20261027-01.json).
