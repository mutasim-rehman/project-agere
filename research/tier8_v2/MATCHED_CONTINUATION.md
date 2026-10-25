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

## Fixed optimizer and worker, before baseline-probe outcomes

The new `scripts/tier8_v2_continue.py` supports both original3B NF4 loading and the
successful compact-CPU7B loading policy, without editing either live source set.
Recipe: seed42, AdamW reset, learning rate1e-4, weight decay0, clip norm1,
accumulation8, exactly one epoch. This learning rate is half the original2e-4:
a fixed moderate continuation rate intended to allow learning new negatives while
limiting forgetting. It is a judgment, not an optimized or empirically proven rate.
No rate sweep or outcome-dependent checkpoint choice is planned.

Preparation requires the declared discovery queue to complete and replays its
results. It rejects continuation if BOTH target policies meet the ceiling rule.
It requires a complete compatible full-epoch initializer with finite validation;
all saved LoRA tensors are loaded and compared for exact dtype/value/key equality
before any update. A fresh adapter with zero B matrices is rejected. Model/data/
tokenizer/source/runtime identities are pinned. The fit covers the longest complete
input and longest supervised target; its two updates are discarded. Full training
requires that same measured fit, reloads the original full checkpoint, and resets
AdamW. Losses are reported by validation family/task. Training keeps the10.5GB
complete-tree cap,1GB host reserve and serial hardware lock, separately from6.4GB
deployment. No retries/resume. Conversion and actual deployment effect proof remain
required after training, and neither is implemented by this worker itself.

Three checks pass, including a real tiny CPU PEFT save/restore and rejection of an
untrained state. This is worker integrity testing, not a real3B/7B fit or result.
No continuation plan or worker has been launched; baseline inputs remain frozen.

[Prepared data/audit evidence](evidence/matched-continuation-prepared-01.json).
Raw data, manifests, source snapshots and logs stay on SSD at
`datasets/tier8_v2_continuation/matched_01` and `runs/continuation-matched-*`.


Deployment provenance correction before any real continuation: the monitored
training plan/controller/worker still stream-check every HF source weight file.
The saved manifest retains those hashes in training_base_artifact_sha256 rather
than asking the legacy deployment input validator to read_bytes whole multi-GB
shards. Configs, data, scripts, runtime and initializer-adapter inputs remain
rehash-checked. Actual deployment weights are separately pinned GGUF files, not
the NF4/BF16 training source. Four focused checks now pass. This is an allocation/
provenance correction; no model recipe, data or method changed and no actual fit
has run. Canonical natural evaluation preparation is now02;01 and changed-source
snapshots are preserved as superseded, with zero study NN calls.
