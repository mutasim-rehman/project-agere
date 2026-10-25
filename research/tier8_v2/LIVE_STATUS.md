# Research checkpoint

**Observed 26 October 2026, 00:53 PKT.** Committed snapshot, not a live monitor.

| Item | Verified state |
|---|---|
| External baseline queue | Complete: 380 case–arm evaluations; Mortar SAS39/90, MAS26/90; FRAMES2/100,1/100 |
| SAS7B joint fit | Complete:2 actual updates,392 changed tensors;10.295GB tree RSS under unchanged10.5GB training cap |
| SAS7B full joint adaptation | Second full run stopped during preparation at10.563GB RSS;0 updates; compact CPU storage fit prepared |
| Shared SAS training exposure | Same drafting and extended verification examples as corresponding MAS adapters; fixed equal task-loss mass |
| Extended MAS critic | Dataset/parity/audit ready; training pending serial GPU availability |
| Novel repair mechanism | Development/strong-control design underway; no measured gain yet |
| Novelty | No demonstrated useful original method yet |

Full SAS adaptation still requires a reliable loading fit and is expected to take several hours. The joint fit includes the
longest input and longest supervised target; its RSS was close to the10.5GB cap.
Do not turn a successful short fit or lower training loss into an accuracy claim.
Runtime deployment still has a separate6.4GB process-tree limit.

Earlier matched24-case FinQA evidence: trained MAS critic delivered11 correct,
4 wrong,9 withheld versus plain3,0,21 (reported metric); raw9,6,9 versus2,1,21.
This is a coverage–risk tradeoff. Best old SAS13,5,6 had different adaptation;
matched shared SAS training is now addressing that baseline weakness.

The100-report development packets and174 natural-training packets remain
uninferred. Current research window ends approximately26October11:54PKT.
Before16/32GB, freeze common methods, prompts, repair/acceptance/scoring and
ablations. No new method may be introduced only at a later tier.

[Joint fit evidence](evidence/sas7b-joint-fit-completed-01.json) ·
[Full training launch](evidence/sas7b-joint-train-launch-01.json) ·
[External audit](evidence/external-baselines-completed-01.json) ·
[Feature freeze](FEATURE_FREEZE.md).

Raw weights, datasets and traces stay on the authorized SSD. Full goal remains active.

Pread fit passed at5.936GB, but full preparation did not. New compact CPU storage keeps exact BF16 weights and FP32 lookup results; CPU value/loss/gradient checks pass. Actual new fit still pending.
