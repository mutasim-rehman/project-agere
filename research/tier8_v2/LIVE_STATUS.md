# Research checkpoint

**Observed 26 October 2026, 02:13 PKT.** Committed snapshot, not a live monitor.

| Item | Verified state |
|---|---|
| SAS7B full joint adaptation |**Running:193/476 updates**,1544/3801 examples;482 validation pending |
| Training resources |Worker about4.07GB, complete tree about8.33GB including12 compiler workers;10.5GB training cap |
| Discovery-first continuation |**Live, waiting for full SAS**;8 frozen serial jobs,5 broad comparison jobs explicitly deferred |
| Fixed probe |32 greedy binary reviews from8 training reports, same inputs for joint SAS/original MAS critic/extended MAS critic |
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
