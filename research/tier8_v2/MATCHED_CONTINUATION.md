# Conditional matched continuation study

Prepared26October2026, before the fixed32-review NN probe. No continuation has
been launched; the baseline-probe stop rule remains in force. These are training
data and controls, not a trained method or useful novelty result.

The question is whether crossed-question negatives help beyond additional ordinary
fine-tuning. Compare two conditions initialized from the SAME proven full adapter:
current extended-corpus mutation negatives versus crossed-question negatives. Both
use the same selected questions, common union evidence, positive programs, labels,
task examples, rehearsal and validation. Only new negative program inputs differ.
This avoids attributing extra optimization alone to the candidate curriculum.

## Frozen data recipe and actual counts

Select64 jointly eligible TRAINING quartets by existing SHA, one per report. Both
conditions must fit all four records under BOTH3B/7B tokenizers before inclusion;
no partial quartet filtering. Eight training candidates and one validation quartet
failed that joint length criterion. Source selection never uses neural outcomes.
128 new negatives exist;127 actually differ from the current-mutation control.
The one coincident negative remains, rather than being filtered to enlarge effects.

Add64 old critic source pairs (128 rows) and128 actor rows as fixed rehearsal.
Exclude new training source cases from rehearsal; prefer distinct reports by fixed
hash, then fill by the same hash if needed. Inherit original report splits.

| Policy dataset, each condition | Train rows | Validation rows | Planned updates, accumulation8 |
|---|---:|---:|---:|
| Joint SAS |512|448|64|
| MAS critic |384|416|48|
| Common MAS actor |128|32|16|

SAS receives exactly the same critic and actor rows as the separate MAS adapters.
Its task weights2.0 drafter and2/3 critic give equal total training-loss mass256
per task, retaining the established shared-policy balancing convention. Separate
MAS parameter/optimizer states differ; this does not isolate architecture alone.
The MAS actor data is identical across conditions, so one common actor continuation
can serve both. Any shared training cost must be disclosed rather than counted twice.

The common validation contains192 crossed-family rows,192 matched mutation-family
rows,32 old critic-replay rows and32 actor rows. Positive inputs repeat between
the two new families, so448 observations are not448 independent cases. SAS covers
190 training/38 validation reports, with no overlap. MAS critic covers115/33 and
actor128/32. Report losses/behavior by family and task; do not turn the combined
teacher-forced loss into financial QA accuracy.

## Matched controls and remaining differences

All positives, rehearsal and validation records are byte-identical between the
conditions. Actual training tokens under either tokenizer:

| Dataset | Current-mutation control | Crossed candidate |
|---|---:|---:|
| Joint SAS |409558|408376|
| MAS critic |296262|295080|
| Common actor |113296|113296|

The crossed condition has1182 fewer tokens:0.289% for SAS,0.399% for the critic.
Equal steps are not perfectly equal compute. Gradient/dropout paths and SAS/MAS
parameter sharing are not identical. These limitations remain even if outcomes
look favorable.

The new256 crossed training rows have exact evidence+program and evidence+question
label balance. The full rehearsal mixture does NOT retain exact50% marginal balance;
do not transfer the pure-quartet guarantee to the whole training corpus.

Independent audit verifies all five dataset hashes and source identities, numerical
labels/execution/model-prompt bindings, unchanged positive/rehearsal/validation
records, exact SAS/MAS task-row equality, no train/validation report overlap or
contradictory identical full inputs, response-to-target binding, and complete
HF/GGUF sequence parity for BOTH profiles. No target cropping or truncation.
Three targeted construction checks and full real-data replay pass.

## Before any actual continuation

Wait for the frozen baseline discovery jobs. If both current target policies meet
the predeclared30/32 exact-label and6/8 exact-quartet ceiling rule, do not train
solely to manufacture a gain on this small family. Otherwise freeze the actual
continuation plan, including optimizer reset, learning rate/epoch, checkpoint
hashes, source/runtime hashes and memory policy before looking at its outcomes.
Load the real trained LoRA state; an independently initialized adapter is not a
continuation. Preserve all baseline checkpoints. Require a new measured fit,
actual updates, conversion and deployment application proof for every new policy.

Use the same plan in control and candidate. Do not select a checkpoint, learning
rate, classifier, validation subset or scalar risk penalty to improve the reported
story. Rehearsal is intended to limit forgetting, not assumed to succeed. Measure
generative and critic behavior, correct/wrong deliveries and withholding under BOTH
existing numerical metrics on report-disjoint natural errors, with actual work
and full resident memory. Any adoption must happen at8GB before cross-tier freeze.
Contrastive bundles and rehearsal are established methods; measured usefulness
and a defensible distinction from closest priors still remain unproven.

[Prepared data/audit evidence](evidence/matched-continuation-prepared-01.json).
Raw data, manifests, source snapshots and logs stay on SSD at
`datasets/tier8_v2_continuation/matched_01` and `runs/continuation-matched-*`.
