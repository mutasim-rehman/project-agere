# Research checkpoint

**Observed 27 October 2026, 08:21 PKT.** Committed snapshot, not a live monitor. Goal active;
useful novel-method improvement remains unproven. No cross-tier freeze.

| Item | Verified state |
|---|---|
| Original joint7B SAS adaptation | Complete476 updates/3801 examples; converted/application-proven |
| Matched common3B actor | Complete16 updates/128 examples; converted/application-proven |
| Matched3B critics | Both complete48 updates/384 examples; converted/application-proven |
| Natural MAS selection | All three52-case runs complete; full trace/token/memory replay passes |
| Matched control7B SAS | Complete64 updates/512 examples,448 validation; converted/application-proven |
| Matched crossed7B SAS | Fit complete2 updates; full epoch has NOT started |
| Controller status | Original01 process disappeared during crossed-epoch metadata preparation. No output created. Explicit suffix recovery is being audited; no model worker live at this observation |

The original controller's last state file is stale. A running claim requires its
matching live PID/create-time, not that state file alone. No observed failure/exit
was logged; cause is unknown. Original plan/journal/logs/results are preserved.
Completed model work will not be repeated. Recovery retains every pending command,
recipe, dataset, metric and scientific obligation.

Training allowance10.5GB is DISTINCT from6.4GB deployment cap. Completed control
SAS training sampled8.275GB and native application proof5.140GB. Fit updates are
discarded; every full epoch reloads the trained original initializer. Teacher
validation loss is not natural QA. [Control SAS evidence](evidence/matched-control-sas-complete-01.json).

## Natural MAS result: candidate not adopted

| Critic with identical common actor | Reported correct/wrong/withheld | Raw correct/wrong/withheld |
|---|---|---|
| Matched control |3 /19 /30|5 /17 /30|
| Crossed |3 /15 /34|5 /13 /34|
| Strong original |4 /22 /26|6 /20 /26|

Same52 initial actor plans/responses/prompts/usage match across all three critics.
Crossed prevents5 control wrong deliveries but introduces1 new wrong: net4 fewer
wrong with observed correct retained.15-report uncertainty includes zero/harm.
Against ORIGINAL, crossed prevents10 wrong but introduces3 wrong AND withholds1
correct. It FAILS the predeclared no-correct-loss rule. Do not claim novel overall
superiority from the matched-control result. [Detailed comparisons](MATCHED_MAS_SELECTION.md).

Both matched policies spend substantial repair work with zero per-case delivery/
correctness change versus measured no-repair prefixes. Correct generation remains
weak. Prefixes are trajectory ablations, not fresh independent generation runs.

## Other measured findings and limits

Shared3B role switching separately matches distinct-backbone logits/completions on
two prompts/four switches:4.831→2.571GB sampled RSS. Known-method engineering,
not novel QA improvement. Frozen natural MAS uses TWO specialist instances; its
shared CLI flag only deduplicates identical weight+adapter pairs. Do not apply
that separate memory saving to natural runs.

[Representation audit](REPRESENTATION_COVERAGE_AUDIT.md): source/catalog coverage
and reference conventions limit interpretation. First-row data can be lost, but a
naive preservation variant recovers1 fitting case and loses1: net coverage41/73
unchanged. Not adopted. All cases and both existing metrics are retained.

Remaining: crossed SAS full training/conversion/proof, natural SAS comparisons,
original-classic actor baseline,49-case reserved paired audits and secondary SAS
prompt checks. Both architectures still require controlled strengthening before
16/32GB tiers. Code/decisions/aggregate evidence are pushed; raw logs, datasets,
weights and detailed replay stay on the authorized SSD.
