# Live research checkpoint

**Observed 25 October 2026, 15:26 PKT.** This is a committed snapshot, not a live process monitor.

| Item | Verified state |
|---|---|
| Critic training | Running; **169/393 updates (43.0%)**, 1352/3140 training examples |
| Remaining training | Approximately 43 minutes at measured pace, plus validation/save |
| GPU memory | Peak allocated 3.92 GB; reserved 4.23 GB |
| Broader development | 100 questions from 100 reports prepared; no model inference yet |
| External MortarBench/FRAMES | 26/380 case–arm evaluations saved; original job interrupted; recovery waits for training to finish |
| Host memory | 9.35 GB available at this observation; original 7.4 GB recovery preflight currently feasible |
| Software checks | 204 passed; no competing CPU inference launched |

Training process identity was verified against its launch timestamp and command.
Its trainer, encoded corpus, parity and weights remain frozen. Training uses a GPU;
it is separate from the simulated 8 GB CPU deployment study. CPU evaluation must
wait for training completion and a fresh headroom check.

## What is established

The critic fit passed two actual updates with 504 changed tensors. Its corpus has
3140 training and 382 validation examples, report-group separation and exact
HF/GGUF token agreement. Positives reproduce annotations; controlled negatives
change an operation or source operand. They are not independently adjudicated
semantic labels or natural model errors.

On the reused 24-question development slice, best completed SAS has 13 reported
answer matches (8 raw execution matches); adapted MAS has 11 (9 raw matches).
The adapted MAS still delivered 11 wrong answers with its weak critic. These
conditions differ in tuning and do not establish an architecture winner.

## What remains unproven

**No demonstrated useful novel method yet.** The current epoch strengthens a known
adaptation baseline. Its validation, GGUF conversion, reversible application proof,
verification discrimination and actual QA gains still need evaluation. A saved
adapter or low training loss cannot substitute for these checks. Comparable SAS
adaptation and publication-quality confirmation also remain outstanding.

## Next gates

1. Finish the epoch and verify complete counts, finite validation and saved tensors.
2. Convert and prove the critic adapter is applied to the intended role.
3. Evaluate matched controls and natural errors, then broaden beyond reused cases.
4. Recover the preserved external evaluation when model serialization and memory allow.

[Detailed supervisor update](SUPERVISOR_UPDATE_2026-10-25.md) ·
[Decisions](../../DECISIONS.md) ·
[Training launch proof](evidence/critic3b-training-launch-01.json) ·
[Fit proof](evidence/critic3b-fit-01.json) ·
[Critic deployment gates](CRITIC_DEPLOYMENT.md)
