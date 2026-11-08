# Windows 8 GB endpoint study

The capacity pilot found four reports with a correct intermediate
result overwritten by later operations. Work on early stopping in
language model reasoning reports a related overthinking mechanism.
Here the alternatives are executable, cited program prefixes rather
than sentence boundaries. [ThinkBrake](https://arxiv.org/abs/2510.00546)

## Frozen-candidate replay

The existing `program_endpoints.choose_endpoint` helper was replayed
with the unadapted 3B Q4 checkpoint. The input contained the question,
evidence, original program, and the values of all executable prefixes.
KEEP was always available. No gold was available during selection.
The six reports are the previously analyzed capacity cohort, so the
replay is a retrospective mechanism check.

All eleven programs with more than one operation were kept. The
single-operation program needed no call. Final exact execution matches
stayed at one of twelve. Always selecting the first executable step
would have yielded three of twelve, recovering three programs and
breaking one previously correct result. An answer-key oracle could
identify five correct endpoints across the twelve programs. The
analysis retains individual paired gains and losses.

Use `scripts/tier8_windows_endpoints.py replay` with the archived
capacity cohort and drafts, then `summarize` with the saved replay
ledger and pinned official scorer.

## Prospective count planning comparison

Use the same adapted 3B drafter twice on 16 additional reports.
The control gets 768 output tokens and a one-to-eight operation grammar.
The intervention first asks the unadapted 3B checkpoint for the minimum
operation count from the question and evidence alone, with a 96-token
ceiling. The adapted drafter then gets the same drafting prompt and
an exact-length grammar with a 672-token ceiling. An invalid count
falls back to the unrestricted grammar and remains in the denominator.
The aggregate ceiling is 768 in both arms. Order alternates by report.
There are no verifier calls. Primary analysis compares official execution
correctness, paired gains/losses and draft resources. Reported-answer
correctness is secondary.

The earlier whole-source exclusion rule left only three eligible
reports. This cohort excludes the two development sources, the initial
adapter train and validation data, the recorded common actor
continuation examples, and all five preceding Windows cohorts.
It permits reports present in the raw training-source archive if they
are absent from the audited training records. Do not describe this
as a pristine test or infer absence of pretraining exposure.
The 16-report cohort was frozen by hash before inference, one question
per report. SHA-256
`09db944d5e793bfca0096c80d465d3070c058645649746b2c9d08b0df4584d01`.

Use `tier8_windows_natural_pairs.py run --planned-length` with the
common actor adapter and the frozen cohort. Score with `summarize`
and supply the cohort to require all case IDs. The first condition is
unrestricted adapted drafting and the second is planned-length
adapted drafting. Both use the native Windows sampled 6.4 GB guard.

### Completed count planning run

All 32 drafts executed. The control produced one correct final
program out of 16 by official execution scoring. Planned length
produced three. The paired transitions were three recoveries,
one regression and twelve ties. The gain was 12.5 percentage
points on this cohort, with an exact two-sided McNemar p-value
of 0.625. The secondary reported-answer metric counted zero
correct control programs and three correct planned programs.
The sole correct control program under official execution
failed reported-answer scoring.

The planner returned a usable count for all cases and all drafts
matched the specified count. Three predictions matched the number
of annotated operations, eleven were longer, and two were shorter.
Alternative valid programs can have a different length. The
intervention did not shorten programs on average by the median:
2.5 operations in control versus 3.0 in planned. This run supports
a local benefit from constraining topology before generation.
It does not show that the gain came from reducing extra operations.

Median time including loading and the planning call was 33.6 seconds
versus 23.1 seconds for unrestricted drafting. Both peaked at
about 2.52 GB sampled RSS. Some offline audits ran concurrently,
so elapsed time is descriptive rather than a controlled CPU
benchmark. No delivery gate was evaluated and the 16 GB tier
remains gated.

### Symbolic equivalence and unused work

We applied the official FinQA symbolic comparator as a secondary
diagnostic, normalizing numeric spellings consistently and keeping
literal constants distinct from cited values. It agreed with the
execution labels for the prior adapter and capacity cohorts. In
the count study it accepted zero control programs and one planned
program before pruning. Two planned programs repeated a correct
division after an unused multiplication. Backward slicing from the
final answer removes the unused calculations and raises the planned
symbolic count to three. The official execution result was checked
to remain unchanged for every executable program in the audit.
This uses the backward-dependency idea from software program slicing.
[Weiser, Program Slicing](https://courses.cs.washington.edu/courses/cse503/11au/readings/weiser-slicing-icse81.pdf)

The control's lone execution match uses a cited 100 in place of the
reference's constant 100. It remains symbolically different after
pruning. Conversely, the 7B capacity drafts had no unused operations,
even though two continued past a correct intermediate result.
Dead-operation pruning cleans up redundant work and cannot recover
a correct intermediate value that the final output still depends on.
The symbolic audit does not certify the source identity or semantic
meaning of any matching expression.

### Gold-informed diagnostic

The planned count matched only three annotated operation counts.
To separate count prediction from operand binding, we freeze a
separate oracle diagnostic on the same 16 questions. Both arms
use the same adapted checkpoint, lexical evidence and 768-token
draft allowance. The second arm's grammar enforces the count
from the annotated reference program. It never sees the target
operands, operations, or answer. This intervention is gold
informed and does not qualify as a deployable candidate policy.
A valid alternative calculation can require a different number
of operations, so it is a diagnostic rather than a mathematical
upper bound.

The immutable case-to-count map is
`evidence/windows-endpoint-study/oracle-annotated-lengths.json`.
Use `run --oracle-lengths` with the same frozen cohort, adapter
and a 6.1 GB worker commit limit. Compare paired outcomes with
unrestricted drafting and report the previous predicted-count
result separately.
