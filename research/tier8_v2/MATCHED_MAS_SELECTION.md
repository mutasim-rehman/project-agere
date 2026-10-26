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

The strong ORIGINAL critic with this same actor is now evaluating. Beating a
matched continuation of the regressed extension does not establish superiority
to that original, or novelty. The49-case reserved diagnostic audit and SAS study
remain required. No recipe, threshold, case, prompt or scoring changes are made
from this result. Existing contrastive/bundle-training literature remains relevant.

[Paired full audit](evidence/matched-mas-selection-paired-01.json) ·
[Control replay](evidence/matched-control-natural-complete-01.json) ·
[Crossed replay](evidence/matched-crossed-natural-complete-01.json).
