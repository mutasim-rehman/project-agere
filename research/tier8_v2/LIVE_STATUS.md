# Research checkpoint

**Observed 27 October 2026, 10:44 PKT.** Committed snapshot, not a live monitor.
Goal active; useful novel-method improvement remains unproven. No cross-tier freeze.

| Item | Verified state |
|---|---|
| Original joint 7B SAS | 476 updates / 3,801 examples; converted/application-proven |
| Matched common 3B actor | 16 updates / 128 examples; converted/application-proven |
| Matched 3B critics | Both 48 updates / 384 examples; converted/application-proven |
| Matched 7B SAS policies | Both 64 updates / 512 examples; converted/application-proven |
| Natural MAS selection | All three 52-case conditions audited |
| Natural control SAS | 52/52 complete; independent trace replay passed |
| Natural crossed SAS | Running under live one-shot service PID90142 |

Training used a separate 10.5 GB allowance; deployment cap is 6.4 GB.
Neither completed training nor lower teacher loss proves better answers.
[Training comparison](MATCHED_SAS_CONTINUATION.md).

## Natural MAS: candidate not adopted

| Critic with identical common actor | Reported correct/wrong/withheld | Raw correct/wrong/withheld |
|---|---|---|
| Matched control |3 /19 /30|5 /17 /30|
| Crossed |3 /15 /34|5 /13 /34|
| Strong original |4 /22 /26|6 /20 /26|

Crossed prevents five control wrong deliveries and introduces one: net four fewer.
Report-level uncertainty includes zero/harm. Against the original it loses one
correct answer, failing the predeclared no-correct-loss rule. Post-hoc attribution
places the net control error reduction in missing-catalog-operand cases; this is
not semantic-mechanism proof or a deployment routing feature. Both matched MAS
repairs add work with no per-case delivery/correctness change versus their recorded
no-repair prefixes. [Complete MAS comparisons](MATCHED_MAS_SELECTION.md).

## Natural SAS: control complete, comparison pending

| Control trajectory | Reported correct/wrong/withheld | Raw correct/wrong/withheld |
|---|---|---|
| Full |8 /23 /21|10 /21 /21|
| No-repair prefix |8 /21 /23|10 /19 /23|

All prompts, scores, tokens, source execution, adapter proofs and memory samples
replay. Sampled peak 5.356 GB below6.4 GB. Repair adds two wrong deliveries with
no correct-delivery increase and 19.1 minutes recorded inference work. Two correct
initial drafts rejected then wrong revisions accepted share one EW report; no
population or novel-mechanism claim. Initial candidate matches are10 reported/13
raw. Prefixes are measured trajectory ablations, not fresh neural runs.
[Complete control evidence and limits](MATCHED_SAS_SELECTION.md).

## Baseline engineering and representation diagnostics

Separate shared-3B serving proof: RSS4.831→2.571 GB on two prompts/four switches.
Known engineering, not natural QA improvement. Frozen natural MAS still uses two
specialist instances; do not apply the separate memory saving to those runs.

Header and catalog-only prototypes both improve direct reference mapping41→45/73
fitting cases. All added header quantities were already visible in original source
spans: this is catalog representability, not newly retrieved raw cell text.
Catalog-only preserves source text/old IDs but adds5,597 prompt tokens versus5,418
for header; no aggregate token saving. Neither has a neural QA gain or adoption.
[Representation audit](REPRESENTATION_COVERAGE_AUDIT.md).

Remaining: crossed-SAS selection/pair, stronger original baselines,49-case reserved
paired audits, secondary SAS prompts and unresolved trained MAS prompt coverage.
No claim either architecture is optimized. Prepared representation tests follow
current obligations; no concurrent neural jobs or silent packet substitutions.

Original controller01 disappeared during metadata preparation; cause unknown.
Explicit suffix02 reverified all30 completed jobs and retained20 pending commands
exactly. One-shot user service agere-matched-study-02-20261027 (Restart=no) is live;
verify its PID/create-time and actual children before reporting progress.
[Recovery evidence](evidence/matched-serial-study-launch-02.json).

[Supervisor checkpoint](SUPERVISOR_UPDATE_2026-10-27.md) is the earlier dated
snapshot; the control-SAS result above was completed afterward. Code/decisions/
aggregate evidence are pushed; weights, data and detailed raw proof remain on SSD.
