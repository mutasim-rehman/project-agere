# Natural SAS selection: control complete, paired result pending

The fixed 52-question / 15-report control-SAS run completed and passed independent
replay of prompts, adapter application/proof, token counts, arithmetic, numerical
scores, delivery decisions and every memory sample. Sampled peak process-tree
RSS is 5,355,872,256 bytes under the 6.4 GB deployment cap. No stages truncated.
Crossed-SAS is running; the original joint-SAS baseline and secondary prompts
remain required. Do not infer a method gain or architecture winner from this
single completed condition.

| Control-SAS trajectory | Reported correct / wrong / withheld | Raw correct / wrong / withheld |
|---|---|---|
| Full review and repair |8 /23 /21|10 /21 /21|
| Measured no-repair prefix |8 /21 /23|10 /19 /23|

Initial candidates match 10 reported answers and 13 raw execution answers; final
candidates match eight and ten respectively. There are zero repairs from wrong
to numerically correct under either metric. Two reported and three raw initially
correct candidates regress. Prefix views use recorded trajectory stages, not
newly generated no-repair or critic-free runs.

Two delivery decisions change: `EW/2004/page_83.pdf-1` and
`EW/2004/page_83.pdf-2`, both withheld by the initial review, become wrong
deliveries after repair. Both initial drafts match BOTH numerical metrics; the
initial verdict is FAIL, the repaired program matches neither metric, and the
final verdict is PASS. The saved source/execution traces verify the sequence.
Both questions share one report: do not present them as independent replication
or as independently adjudicated financial semantics. All 52 questions remain.

Repair consumes an additional 45,486 prompt tokens, 972 generated tokens and
1,144.825 seconds (19.1 minutes) of recorded stage inference versus the no-repair
prefix. Correct deliveries remain unchanged and wrong deliveries increase by two
under both conventions. This is a negative result for this exact policy/sample,
not a claim that every repair method or SAS architecture is ineffective. It also
does not establish first-use novelty for the known self-correction failure mode.

Final-candidate verification rates must not hide the rejected correct drafts
that repair removed. Compare complete trajectories and fixed candidate probes;
do not change metrics, thresholds, case inclusion or training targets based on
these selection outcomes. The same-source crossed candidate, stronger original,
reserved audit and prompt controls remain in the serial sequence.

[Pinned completion evidence](evidence/matched-control-sas-natural-complete-01.json)
links the full replay, memory, raw model outputs and per-case repair transitions
on the authorized SSD. [Single-condition audit command](experiments/audit_natural_condition.py)
uses vocabulary-only tokenization, with zero new generation calls. These are
exploratory public training-source report holdouts, not publication confirmation.
