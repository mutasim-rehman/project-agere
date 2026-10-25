# Research checkpoint

**Observed 26 October 2026, 01:06 PKT.** Committed snapshot, not a live monitor.

| Item | Verified state |
|---|---|
| External baseline queue | Complete:380 case–arm evaluations; Mortar SAS39/90,MAS26/90; FRAMES2/100,1/100 |
| SAS7B compact joint fit | Complete:2 actual updates,392 changed tensors;8.490GB tree RSS under10.5GB training cap |
| SAS7B full joint adaptation | **Running:29/476 updates**,232/3801 examples;482 validation pending |
| Training memory | Latest worker about4.07GB; whole tree about8.33GB including compiler workers |
| Extended MAS critic | Dataset/parity/audit ready; training pending serial GPU availability |
| Source-aware repair controls | Implemented;17 CPU checks pass; actual NN scorer/repair pilot pending |
| First redundancy diagnostic |370 candidates→368 source-symbolic classes; weak evidence for useful call savings |
| Novelty |No demonstrated useful original method yet |

The successful full run has progressed beyond the two preserved failed full
attempts, both0 updates. One failed during loading10.532GB; pread loading fixed
that stage but the next stopped during preparation10.563GB. Current compact frozen
CPU storage keeps BF16 weights, FP32 embedding lookup results and the existing
BF16 streamed head projection. Tiny CPU loss/gradient preservation checks pass;
actual7B training or QA equivalence is not asserted. New per-process traces show
Torch Inductor launching12 compiler workers; their RSS counts in the cap.

Full adaptation is provisionally several hours, followed by conversion, reversible
application proof and actual QA. Training loss is not a QA result. Deployment has
a separate6.4GB complete-tree cap. No overlapping NN model workloads.

Earlier matched24-case FinQA: trained MAS critic delivered11 correct,4 wrong,
9 withheld versus plain3,0,21 (reported metric); raw9,6,9 versus2,1,21. This remains
a coverage–risk tradeoff. Best old SAS13,5,6 had different adaptation. Shared SAS
training now uses the same drafting and extended verification examples as the MAS
role adapters, with fixed equal task-loss mass; this is baseline strengthening.

[Training checkpoint](evidence/sas7b-joint-train-progress-01.json) ·
[Training launch](evidence/sas7b-joint-train-compact-launch-03.json) ·
[Repair candidate and weak early diagnostic](SOURCE_REPAIR_CANDIDATE.md) ·
[External audit](evidence/external-baselines-completed-01.json) ·
[Cross-tier freeze](FEATURE_FREEZE.md).

The100-report development packets and174 natural-training packets remain
uninferred. Window ends approximately26October11:54PKT. Common methods must be
validated/frozen at8GB before16/32GB. Code and aggregate evidence are committed;
raw weights/datasets/traces stay on the authorized SSD. Goal remains active.

Serial follow-on controller is live and waiting for full SAS completion:10 frozen jobs covering conversion/proofs, extended MAS critic training, paired100-report critic evaluation, and both direct and analysis+demos SAS100 policies. [Frozen queue](evidence/joint-posttrain-plan-01.json). Model workloads remain serial. Full default suite274 tests with17 training-runtime skips.
