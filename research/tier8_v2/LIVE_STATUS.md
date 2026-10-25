# Research checkpoint

**Observed 25 October 2026, 21:22 PKT.** Committed snapshot, not a live monitor.

| Item | Verified state |
|---|---|
| External queue | **Complete:380 case–arm evaluations**, all4 arms |
| MortarBench local exact | SAS39/90; MAS26/90 |
| FRAMES closed-book strict | SAS2/100; MAS1/100; punctuation sensitivity unchanged |
| External complete queue-tree peak |5.628GB under6.4GB decimal |
| SAS7B fit |**Stopped during loading**,10.548GB training RSS against10.5GB cap;0 updates |
| New critic corpus |820 replacements, same3522 rows/positives/splits/393 planned updates; parity/replay passed |
| Paired trained-critic analysis |Implemented; existing24-case replay/proof validated; no actual second trained critic yet |
| Software checks |248 tests covered across required runtimes |
| Novelty |No demonstrated useful original method yet |

## What the external results mean

These are ORIGINAL UNADAPTED systems using partial JSON/XML Mortar evidence and
local typed exact scoring; FRAMES is closed book. They are not a full official
benchmark replication, optimized-system comparison or architecture-effect estimate.
SAS allowance896 versus MAS1792 generated tokens; actual costs differ. Original26
SAS cases are preserved byte-for-byte and combined with new segments. Saved case
durations span interruption/recovery; no uninterrupted-latency claim.

MAS returned[] for every57 transaction-ID question:11 empty-answer matches but
**0/46 nonempty-gold exact matches**. All required IDs were literally present in19
of those46 retrieved packets; mention does not prove sufficient evidence. Final
outputs all stopped normally, so final token truncation does not explain this
collapse. SAS achieved13/46 nonempty transaction-ID matches. These are local
failure diagnoses, not claims about the adapted financial-program systems.

Mortar paired MAS−SAS difference−0.144;9 financial-case cluster bootstrap95%
[−0.239,−0.045]. FRAMES−0.01 with question-bootstrap[−0.05,0.02], near floor.
[Completed external audit](evidence/external-baselines-completed-01.json).

## Current work

Both old controllers have terminated. No fit updates completed. Host available
RAM remained above11.58GB during the failed fit, so the observed refusal was the
training RSS ceiling, not host-reserve exhaustion. Old trace cannot distinguish
private from mapped-file RSS. Loader storage retention is a hypothesis to test;
retain failed logs/source snapshot and keep the same cap for any revised attempt.
[Fit failure](evidence/sas7b-offload-fit-failure-01.json).

Current trained FinQA critic still delivers11 correct/4 wrong/9 withheld versus
plain3/0/21 on reused24 (reported metric); raw9/6/9 versus2/1/21. Coverage–risk
tradeoff, no dominance. The broader100-report packets and174 natural-training
packets remain uninferred. Extended critic training and full comparable SAS
adaptation remain outstanding. [Prepared critic experiment](evidence/critic-curriculum-experiment-01.json) ·
[Validated comparison guard](evidence/critic-trained-policy-guard-checks-01.json).

Raw weights, datasets, traces and results stay on the authorized SSD. Code and
small aggregate provenance are committed. Full research goal remains active.
