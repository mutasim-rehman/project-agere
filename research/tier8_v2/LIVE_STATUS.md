# Live research checkpoint

**Observed 25 October 2026, 17:38 PKT.** Committed snapshot, not a live monitor.

| Item | Verified state |
|---|---|
| Critic training | Complete:393 updates,3140 examples; conversion/application proof passed |
| Controlled probe |11/12 pairs separated after training versus0/12 plain |
| Natural24, plain critic |3 correct delivered,0 wrong,21 withheld |
| Natural24, trained critic |11 correct delivered,4 wrong,9 withheld |
| Attribution |All24 drafts and critic prompts identical; same adapted actor |
| Current workload |External recovery running;36 new Mortar SAS cases saved (62/90 including26 preserved) |
| Software checks |238 tests covered across inference/training runtimes; see evidence |
| Novelty |No demonstrated useful original method yet |

Natural counts above use the reported-answer metric. Raw execution gives plain
2 correct/1 wrong/21 withheld and trained9 correct/6 wrong/9 withheld. Candidate
accuracy is unchanged (11/24 reported,9/24 raw); only delivery decisions changed.
Training recovers8 correct deliveries but introduces4 wrong ones: a coverage–risk
tradeoff, not dominance. Report-cluster95% intervals: correct coverage delta
[0.167,0.52], wrong-delivery delta[0.04,0.333]. Small reused development sample.
The unit-sensitivity sidecar changes none of these24 results; one annotation issue
remains unresolved. Controlled probe results are not financial-QA accuracy.

## Current and next work

The frozen serial queue completed FinQA stages1–9 and started external recovery02.
It preserves26 original MortarBench SAS cases; unfinished segments contain64 SAS
MortarBench,90 MAS MortarBench,100 SAS FRAMES and100 MAS FRAMES cases. Completion
and accuracy remain pending. This is an exploratory local protocol, not a full
official benchmark replication. No concurrent model workload is started.

Four wrong accepted development programs suggest missing period evidence, omitted
net adjustments, unit scaling and wrong entity/measure selection. These are manual
diagnostic hypotheses, not independent labels. Next strengthen natural-error
verification on training-only groups, retain correct reference controls, and give
SAS comparable adaptation. No per-case gold-dependent production rules.

Prepared174 training-source packets from62 eligible reports, reserved by report
into fitting73/32, model-selection52/15 and diagnostic-audit49/15 cases/reports.
No natural-error generation or training has run on them.

The100-report broader development selection remains uninferred. Publication
confirmation and a differentiated useful repair mechanism remain outstanding.

## Resource evidence

Training GPU allocated3.920GB/reserved4.228GB, separate from inference RSS.
Natural plain tree peak4.842GB; adapted4.908GB under6.4GB decimal. Host has more
than8GB RAM: a monitored simulated tier, not physical8GB validation. Queue-level
complete-tree monitoring also applies; terminal external peak remains pending.

[Natural paired evidence](evidence/critic3b-natural24-delivery-results-01.json) ·
[Controlled result](evidence/critic3b-controlled-paired-results-01.json) ·
[Supervisor update](SUPERVISOR_UPDATE_2026-10-25.md) ·
[Frozen queue](POSTTRAIN_QUEUE.md) · [Decisions](../../DECISIONS.md)

Raw logs, datasets and weights stay on the authorized SSD; aggregates are committed.

## Latest preparation for SAS

Independent frozen-head blockwise loss helper passes dense-gradient checks and
two tiny Qwen2+LoRA updates against standard CE. It retains complete context,
targets and vocabulary. This is established memory engineering; full7B CPU/GPU
offload integration, real fit and comparable adaptation have NOT run. Current
frozen evaluation sources are untouched. [Numerical proof](evidence/frozen-head-loss-cpu-proof-01.json).

## Queued SAS fit gate

Controller47307/create-time1792930227.21 is verified sleeping in
`waiting_for_frozen_evaluation`; it has no model worker and no fit output yet.
After the current controller exits successfully, it revalidates every frozen job,
external arms/original preservation, source hashes and runtime, then permits ONE
measured two-update7B fit on the same actor corpus. Failure stops; no retries.
All new raw artifacts stay SSD. [Plan](evidence/sas7b-offload-fit-plan-01.json) ·
[Launch](evidence/sas7b-offload-fit-launch-01.json) · [Protocol](SAS_OFFLOAD_FIT.md).

Training has a separate10.5GB host-tree ceiling/1GB reserve/9GB preflight plus
recorded GPU peaks. It does not establish8GB deployment fit. True CPU-resident
embedding/head restore avoids Accelerate's full-matrix GPU reload hooks. A CPU
checkpointed BF16 test exposed per-block backward rounding; FP32 accumulation
fixed it without loosening tolerance. Old sources/failure logs preserved.
[Updated CPU evidence](evidence/sas7b-offload-cpu-checks-01.json) supersedes the
older helper checks. Actual7B CUDA fit, full adaptation and QA remain unproven.

## Next controlled critic experiment prepared, not scheduled

New counterexamples cover incorrect output scaling and omitted subexpressions:
626 scale+194 node-bypass replacements. Same3522 rows,1761 byte-identical positive
rows,3140/382 train/validation split,414/49 report groups and393 planned updates.
Training tokens rise1.798%; compute is not perfectly matched. All3522 HF/GGUF
parity checks pass; independent execution/label replay passes for both corpora.
No critic training or new QA result yet. These are constructed training negatives,
not the174-case natural-error packets (still uninferred).

[Corpus evidence](evidence/critic-curriculum-prepared-02.json) ·
[Prepared hypothesis/control/metrics](evidence/critic-curriculum-experiment-01.json).
After existing serial work, train/convert/prove the extended critic and compare
with the current trained critic on the preselected100-report development set.
First add an explicit trained-versus-trained pairing guard/condition names;
current analyzer assumes a plain control. No unsafe relabelling or novelty claim.
