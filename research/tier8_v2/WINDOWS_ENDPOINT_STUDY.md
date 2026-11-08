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
