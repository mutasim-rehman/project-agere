# Crossed-question verifier curriculum

26October2026. Prepared and audited candidate training data. No new adapter has
been trained on it, and no natural QA gain or useful novelty has been established.

The question-blind audit found that candidate-only shallow trees classify72–77%
of the earlier synthetic validation data correctly. A targeted intervention is to
remove that specific shortcut opportunity rather than add more program mutations.

## Construction

Take two original annotated questions on the SAME source page, with matching answer
units and different executable results. Merge their evidence without conflicting
span IDs. Preserve each original compiled program and use the same evidence in
all four records:

| Model input question | Model input program | Weak label |
|---|---|---|
| Q1 |P1|PASS|
| Q1 |P2|FAIL|
| Q2 |P1|FAIL|
| Q2 |P2|PASS|

Positives must reproduce their original annotations under BOTH current numerical
metrics. Each cross-program negative must be wrong under BOTH metrics for its
new question. Equal-answer ambiguity, conflicting evidence, unit mismatch or any
1024-token overflow rejects the entire quartet. Greedy seed42 SHA matching uses
each source case at most once; original report-level train/validation splits stay
unchanged. No development100 outcome or natural-error label enters construction.

Every evidence+program input appears once per label, and so does every
evidence+question input. Thus a deterministic classifier restricted to either
observable marginal scores exactly50% on the complete balanced corpus. This does
not eliminate joint shortcuts or prove financial understanding. No novelty claim
follows from this elementary balance property.

## Measured preparation result

403 quartets,1612 records:1416 training/354 quartets across219 reports, and196
validation/49 quartets across27 disjoint reports.806 original source cases used.
Of1197 possible same-page pairs,287 had differing units,30 ambiguous cross labels,
78 exceeded the length cap,391 reused already-matched sources,8 repeated questions.
No labels or source examples were added to the active trainer.

Both actual3B and7B GGUF tokenizers pass complete sequence/target encoding. Both
pinned HF tokenizers independently match all1612 sequences. Source questions,
programs, page/report/split identities, exact union evidence, actual model-prompt
binding and all executable labels replay correctly. There are1612 distinct full
model inputs and no contradictory labels for an identical full input. The same
question-blind depth3 tree now scores exactly50% on training AND validation.
This is data-quality evidence, not a neural generalization result.

The first expanded source audit mistakenly expected a positive diagonal record
to contain only its own source evidence. That auditor failed; positives correctly
contain BOTH source packets. Canonical audit04 independently reconstructs the
union at quartet level and passes. Original logs/source snapshots and the unchanged
dataset are preserved. Earlier successful basic parity is not misreported as that
stronger audit. Five targeted construction tests pass.

## Closest prior and claim limits

[Learning with Instance Bundles](https://aclanthology.org/2021.emnlp-main.584/)
already trains on related contrasting QA instances with contrastive losses.
[VitaminC](https://people.csail.mit.edu/tals/publication/vitaminc/)
already uses contrastive evidence to train more sensitive fact verification.
Primary abstracts/project description read; full-method comparison remains due.
Our current construction uses executable financial-program records and ordinary
binary-verdict targets; it does not replicate their objectives. Do not claim
question swapping, counterfactual training, crossed bundles or hard negatives as
new inventions. This is an evidence-driven candidate baseline/intervention, whose
useful distinction still needs measured results and closest-method comparison.

Labels remain the original weak FinQA numerical annotations, not independent
financial-expert adjudication. Changed evidence presentation and sample selection
can affect performance. No pure curriculum effect follows from comparison with a
checkpoint given less additional training.

## Next experiment and scope

The immediate next action is a small TRAINING-source quartet probe on the proven
SAS and MAS policies after their epochs/conversions/proofs, before spending the
remaining window on large comparison-only runs. Freeze eight quartets, one per
report, by existing quartet SHA before any NN outcome; preserve complete quartets.
Keep validation49 quartets unopened to NN-based method selection at that stage.
If both policies already solve the new family, do not add a training stage just
because the data exists.

If a meaningful gap exists, prepare a SMALL matched continuation experiment:
crossed negatives versus the CURRENT EXTENDED-CORPUS mutation negatives on the same selected
source questions, common evidence, positive programs, labels, update count and
initial checkpoint. Select candidate64 training quartets by SHA with one per report
and require all control/variant rows to fit BOTH tokenizers before inclusion.
Predeclare actor/critic replay to check forgetting and provide both systems the
same additional task examples. Report actual training-token differences; equal
update count does not imply identical compute. No continuation recipe or new NN
job is currently launched or approved as the frozen cross-tier method.

Natural, report-disjoint errors and both correct/wrong/withheld metrics must decide
utility; synthetic balance alone cannot. A useful effect needs a matched continued-
training control, stronger baseline comparison, and wider evaluation. Existing
full SAS training and frozen serial queue remain intact at this checkpoint. Any
priority revision must be explicit, preserve the waiting queue and frozen sources,
and never overlap model work. Do not let additional comparison-only runs consume
the entire feature-development window while this targeted experiment is pending.

[Prepared-data and audit evidence](evidence/critic-crossed-quartets-prepared-01.json).
Raw data/logs/source snapshots are on the authorized SSD under
`datasets/tier8_v2_critic/critic_quartets_01` and `runs/critic-quartets-*`.

## Frozen discovery probe implementation

`tier8_v2_quartet_probe.py` prepares the exact32-record training-only subset and
runs monitored greedy JSON reviews with the existing binary grammar,192 output
tokens per review,4096 context, eight CPU threads and6.4GB tree RSS cap. It does
not impose a forced label prefix. UNKNOWN/unparsed count as incorrect exact labels;
nonaccept gate accuracy is reported separately. Parent and queue independently
replay raw response text, token counts and complete-quartet metrics.

Five of the unchanged eight selected quartets have identical operation, step-
reference and constant topology between the two programs. This pre-inference
diagnostic does not alter selection; simple question-type/operator matching is
insufficient for that stratum, though richer joint shortcuts remain possible.

Predeclared stop rule: if BOTH joint SAS and extended MAS critic get at least30/32
exact labels and6/8 fully exact quartets, do not add a continuation stage solely
for this sampled family. The original trained MAS critic is an additional fixed
control. Never use this small training-source probe as validation or paper proof.

The old10-job queue was verified waiting with no child/model job or output,
snapshotted and explicitly superseded. Revised order: SAS conversion/proof, joint
SAS probe, original MAS critic probe, extended MAS critic training/conversion/proof,
then extended MAS probe. This yields discovery data while preparing the stronger
MAS baseline. All old100-report commands are preserved as deferred jobs, not
selected or run based on any100-report outcomes. Active SAS training is unchanged.
