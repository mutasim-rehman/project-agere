# Research checkpoint

**Observed 26 October 2026, 04:34 PKT.** Committed snapshot, not a live monitor.

| Item | Verified state |
|---|---|
| SAS7B full joint adaptation |**Complete:476 updates,3801 training examples,482 validation examples** |
| Training resources |Worker about4.07GB, complete tree about8.33GB including12 compiler workers;10.5GB training cap |
| Discovery-first continuation |**Running deployment proof/probes** after completed SAS conversion |
| Fixed probe |**SAS complete:31/32 labels,7/8 whole quartets**; original MAS running; extended MAS pending |
| Crossed curriculum |403 audited quartets/1612 rows;1416 train,196 validation; both tokenizer parity and source/execution/prompt replay pass |
| Useful novelty |Not established; no new quartet-trained model or quality gain yet |

The original10-job queue was deliberately superseded while waiting, with no model
child, started job or result. Original plan/source snapshots/journal are preserved.
This is a scientific priority change, not a failed model or memory run. Active SAS
training and its source/data remain unchanged; both live identities and frozen
input sets were reverified. New order: SAS conversion/proof, SAS quartet probe,
original MAS critic probe, extended MAS critic training/conversion/proof, extended
MAS probe. No concurrent NN workloads. All large100-report commands remain saved
as deferred jobs; their outcomes have not been consumed.

The probe uses actual deployed greedy JSON binary review,192 generated-token cap,
4096 context,8 CPU threads and6.4GB complete-tree deployment cap. UNKNOWN/unparsed
are wrong exact labels; gate nonaccept is separate. Five of the fixed8 quartet
pairs have the same operation/reference/constant topology. Source questions and
positive programs were already in training;16 crossed negatives are new question/
program combinations relative to both critic fitting corpora. This is training-
source discovery, not an independent generalization set. Canonical exposure audit
also identifies2 exact repeated positive prompts. No labels enter model prompts.

[Discovery launch](evidence/joint-discovery-posttrain-launch-02.json) ·
[Frozen discovery/deferred plan](evidence/joint-discovery-posttrain-plan-02.json) ·
[Old queue supersession](evidence/joint-posttrain-superseded-01.json) ·
[Crossed curriculum](COUNTERFACTUAL_VERIFIER_CURRICULUM.md) ·
[Question-blind artifact audit](CRITIC_ARTIFACT_AUDIT.md).

Artifact audit: shallow program-only trees classify72–77% of earlier synthetic
validation, but only5 correct/5 wrong/14 withheld on reused natural24 for the
extended tree versus existing neural11/4/9 (reported); raw4/6/14 versus9/6/9.
The new crossed data makes marginal-only accuracy exactly50%; this is a data
construction property, not an NN result or a novel principle. Contrastive bundle
training has established priors. Natural disjoint-report utility and matched
continued-training controls must decide whether this intervention helps.

External original-unadapted baseline queue remains complete:380 case–arm runs;
Mortar SAS39/90,MAS26/90; FRAMES2/100,1/100, with disclosed partial evidence/closed-
book limitations. No optimized-architecture winner follows from these figures.

[Cross-tier freeze](FEATURE_FREEZE.md): methods must be validated at8GB before
16/32GB. Approximate window end26October11:54PKT. Shared-role memory experiment
remains prepared, not native-tested or adopted; no extra optional serving work
before the targeted method experiment. Raw data/traces/weights stay on authorized
SSD; code and aggregate provenance are pushed. Goal remains active.

Conditional [matched continuation data](MATCHED_CONTINUATION.md) prepared and independently audited, not trained:512 SAS rows vs384 critic+128 common actor rows per condition; only127 new negative prompts differ. Positives/rehearsal/validation and exact task exposure match; both tokenizer profiles pass. Crossed tokens0.289% lower for SAS, so steps are not identical compute. Probe gate and actual fit/training/proof/natural utility remain required. Active source sets remain unchanged.

Fixed-recipe continuation worker implemented, not full-model tested or launched. AdamW1e-4/reset/one epoch, exact full trained LoRA restoration, discarded fit updates, paired data/source/init/runtime identity, serial lock and full-tree cap. Three targeted checks pass including actual tiny CPU PEFT state restoration. Baseline queue completion and ceiling stop rule enforced before preparation. [Worker evidence](evidence/matched-continuation-worker-01.json).

Canonical natural study is now03, before any study inference.01/source snapshots
preserved as preparation-only superseded. Complete pipeline/token/cost replay
passes on existing24 cases; four repair/metric checks and four continuation checks
pass. Training source shards remain stream-verified, separately retained in
manifest instead of multi-GB deployment read_bytes allocations. Strict current-role
baseline actor reproof04 planned, not run. No new QA gain or novelty result.
[Trajectory evidence](evidence/matched-policy-trace-audit-01.json) ·
[Natural study details](NATURAL_METHOD_EVALUATION.md).

Full SAS baseline adaptation is now audited complete:392 changed tensors,
20,185,088 trainable parameters,12087 seconds (about3h21m), weighted teacher-forced
validation loss0.025889 (drafter0.031829,critic0.014389). Replayed every476 update,
3801 processed examples and all memory samples. Sampled whole-tree peak8.339GB
under10.5GB TRAINING cap; not a deployment fit claim. Converted full adapter now
exists; reversible native application proof and32-review probes are running next.
No new greedy QA improvement or useful novelty inferred from these losses.
[Full training evidence](evidence/sas7b-joint-training-completed-03.json).

Native SAS application proof is now audited PASS:5.135GB sampled deployment peak
under6.4GB,0 zero-repeat drift,3.64457 maximum conditional-label log-probability
effect,2571 actual prefill tokens and0 generated tokens. One bound validation
prompt, not accuracy/calibration. Greedy32-review SAS quartet probe is running.
Analyzer normalizer-import/forced-prefix hash bugs corrected and covered by2
regression checks; canonical natural study03 supersedes02 with identical jobs,
data and metrics. [Native proof evidence](evidence/sas7b-joint-native-application-proven-03.json).

SAS crossed baseline result is strong:31/32 exact,16/16 positives accepted,
15/16 crossed negatives rejected; correct greedy question switches15/16 with
E/P fixed. One false accept confuses NON interest with NET interest income.
This limits the earlier question-blind-artifact hypothesis for the actual7B model.
Training-source discovery, not new natural QA accuracy or novelty. SAS ceiling
component passes; extended MAS still determines the BOTH-policy stop rule.
[Baseline discovery](CRITIC_BASELINE_DISCOVERY.md).
