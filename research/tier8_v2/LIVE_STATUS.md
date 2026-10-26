# Research checkpoint

**Observed27 October2026,01:30PKT.** Committed snapshot; raw serial state on SSD
is authoritative. Goal active. Useful method novelty remains unestablished.

| Item | Verified state |
|---|---|
| Joint7B SAS baseline | Complete:476 updates/3801 training examples, conversion and native application proof |
| Extended3B critic | Complete:393 updates/3140 examples, conversion and application proof |
| Fixed32-review diagnostic | SAS31/32; original MAS30/32; extended MAS27/32. Training-source probe, not natural QA |
| Shared3B role serving | Four switches exactly match distinct-backbone logits/completions; sampled4.831GB→2.571GB (~46.8% reduction) |
| Matched common actor fit02 | Complete:2 updates, exact prior adapter loaded, peak5.9996GB under10.5GB training cap; fit updates discarded |
| Matched continuation/natural QA | Serial50-job study01 launched; common actor complete16 updates/128 examples and converted; native application proof passed; both critic continuations complete48 updates/384 examples each and converted. both native proofs passed. Natural MAS control complete52/52 and independently replayed; crossed critic evaluation complete52/52; paired replay passes. Strong-original/common-actor evaluation complete; candidate loses one correct delivery, so adoption rule fails. Control SAS fit preparation running |
| Novel quality gain | Not demonstrated |

[Study launch](evidence/matched-serial-study-launch-01.json) fixes matched recipes,
all native proofs,52-case selection and49-case reserved audit, plus secondary SAS
prompt checks. MAS control/candidate share the same continued actor. The strong
original critic also runs with that actor, and original actor/critic remain a
separate reference. MAS natural comparisons are prioritized before7B continuation.
All NN jobs run serially with full-tree caps; no implicit retry or adoption.
Training10.5GB allowance is distinct from6.4GB deployment cap.

The original12-hour window elapsed while the chat was inactive; no worker remained
live at18:05UTC resumption. Do not count that interval as active experiments or
claim the base method is frozen. Real QA results will determine the next iteration.
Full study includes612 primary case–arms plus156 secondary prompt case–arms; it
will require substantial additional CPU inference time. No finish-time guarantee.

[Critic discovery](CRITIC_BASELINE_DISCOVERY.md) documents the extension regression
and unresolved count/fraction reference issue without changing official scores.
[Serving evidence](evidence/shared3b-serving-parity-complete-01.json) is a limited
engineering result on two prompts, not full natural equivalence or first-use
novelty. Existing role-LoRA and contrastive-bundle literature precludes claiming
those ingredients alone as novel.

The frozen local-repair opportunity audit rescued zero wrong cases within four
checks/8192 prefill tokens across all tested representative groupings. No NN repair
gain follows. Original external unadapted380-case–arm queue remains complete with
its previously disclosed scope limitations; deferred100-report jobs remain unrun.

Code, decisions and aggregate evidence are pushed. Raw logs, memory samples,
outputs, data and weights stay on the authorized SSD.16/32GB tiers remain pending
validation of the common method at8GB.

[Common actor completed](evidence/matched-common-actor-complete-01.json): exact initializer restored, all504 tensors changed;1204 memory samples replay to5,990,891,520-byte peak. Validation CE0.03393 is not natural accuracy. No QA improvement follows from training completion.

[Control critic completed](evidence/matched-control-critic-complete-01.json):48 updates/384 examples,416 teacher-validation rows,6.012GB sampled training peak. Validation CE0.04778 overall (crossed0.08538, mutation0.01443, replay0.02233). Families repeat positives; these are not416 independent observations. No natural gain or novelty follows.

[Crossed critic completed](evidence/matched-crossed-critic-complete-01.json): all48
updates/384 examples and3772 memory samples replay; peak6.017GB. Matched validation
bytes, initializer/base/recipe/runtime/counts verified identical. Recorded CE:

| Family | Control | Crossed |
|---|---:|---:|
| Crossed validation192 rows |0.085376|0.038352|
| Mutation validation192 rows |0.014434|0.025361|
| Replay32 rows |0.022335|0.016940|
| Overall416 rows |0.047784|0.030709|

This is a training/validation tradeoff, not natural QA or a novel method result.
Validation repeats positives; one training seed. Losses are recorded teacher
forwards, not independently recomputed by the metadata audit. Strong-original
critic comparisons remain mandatory.

Natural residency clarification: the frozen runner's `shared` flag deduplicates
only identical weight+adapter keys. Actor/critic adapters differ, so the live MAS
uses two instances. The separately proven single-backbone switching backend is
not adopted in this study. Do not apply its46.8% sampled-RSS saving to natural
runs. [Actual initialization evidence](evidence/natural-residency-scope-01.json).


First natural control completed and independently audited:52 cases, sampled
peak5.060GB under6.4GB,162851 prompt/4662 generated tokens,2050.7 inference seconds.
Reported metric3 correct deliveries/19 wrong/30 withheld; executable-reference
metric5/17/30. Initial candidate correctness4/52 reported,6/52 raw. No truncation.

Thirty full repairs changed11 programs, but EVERY case retained the same delivery
and both correctness indicators as the no-repair prefix. Extra64025 prompt tokens,
1555 generated tokens and786.4 seconds bought no measured outcome gain here.
38 cases contain all annotated evidence; only4 have correct initial reported
answers. Annotation coverage is not independently adjudicated evidence sufficiency.
This identifies a real weakness to investigate, not a novel successful method.
Do not compare accuracy directly with the earlier reused24-case slice.

[Full control replay evidence](evidence/matched-control-natural-complete-01.json).
Candidate and original-critic comparisons remain required; no hyperparameter,
training data, prompt or scoring changes are made from these control outcomes.


First matched natural pair complete52/52 each,15 reports. Same initial actor
outputs/prompts/usage exactly verified. Reported deliveries control3 correct/19
wrong/30 withheld versus crossed3/15/34; raw5/17/30 versus5/13/34. Five wrong
deliveries prevented, ONE new wrong delivery introduced: net4 fewer wrong, with
all observed correct deliveries retained. Report-cluster95% interval for change
in wrong deliveries per case is[-0.1739,+0.0204], including no benefit and harm.
The predefined exploratory sample gate passes; it is not statistical confirmation.

Crossed34 repairs change12 programs but every per-case delivery/both correctness
indicator still equals its no-repair prefix. The observed gain is initial gating,
not successful correction. Crossed costs170007 prompt/4900 generated tokens and
2136.1 inference seconds versus control162851/4662/2050.7. Both below6.4GB sampled
RSS (crossed5.067GB). No stronger-original superiority or novel method established.
[Paired result](MATCHED_MAS_SELECTION.md). Both systems still require strengthening
and full planned audits before cross-tier freeze.


Strong-original comparison COMPLETE: original reported4 correct/22 wrong/26 withheld
versus crossed3/15/34; raw6/20/26 versus5/13/34. Same52 initial actor responses,
plans/prompts/usage verified across all three conditions. Candidate prevents10
original wrong deliveries but introduces3 new wrong and withholds1 correct. Net7
wrong reduction comes with1 correct loss; predefined no-loss rule FAILS. Do not
adopt or claim novel superiority. Original1929.1s/153639 prompt/4492 generated;
candidate2136.1s/170007/4900. SAS continuation fit preparation is now running.
[Original comparison and uncertainty](MATCHED_MAS_SELECTION.md).
