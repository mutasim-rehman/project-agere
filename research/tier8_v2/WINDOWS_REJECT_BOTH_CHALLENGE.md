# Windows 8 GB verifier challenge with a reject-both option

The previous 3B forced-choice test showed that the model can prefer
some correct programs to near misses when a correct option is present.
This follow-up tests whether it can also withhold when neither option
is correct.

Six new company-year reports were selected in a fixed hash order from
the same FinQA test snapshot as the prior challenge. We excluded its
four reports and the same three prior development and training sources.
The six exact question IDs had no matches in the tracked research,
configuration, and manifest files before archiving the cohort. The
frozen cohort has SHA-256
`f8878be4cf758be8da78eaac5e2fa34cafa1513a849fdba6961a29cc088be3ab`.
See [the earlier challenge](WINDOWS_VERIFIER_CHALLENGE.md) for the source
and scorer hashes and runtime provenance.

Each report supplies one reference program and two single-edit,
executable near misses with distinct results. The official FinQA
execution evaluator validates the translated reference against the
annotated answer and verifies that both near misses disagree with it.
Both near misses also fail the two historical numerical metrics.
The reference and near misses use the same evidence. This diagnostic
uses constructed candidates and does not estimate natural delivery.

For each question, the 3B model reviews a reference/near-miss pair and a
near-miss/near-miss pair. It sees each pair in both orders and must return
A, B, or NEITHER. We report correct selection on the former, false
acceptance on the latter, and report counts stable across both orders.
We also evaluate a two-call agreement gate that accepts only when both
orders select the same program. A gate that always withholds has zero
false acceptances and zero correct deliveries.

Use `scripts/tier8_windows_challenge.py freeze --reject-both` with the
same arguments as the prior challenge plus `--exclude-cohort` pointing
to its frozen cohort. Then use `replay-reject` on the new archived
cohort and `summarize-reject` on the replay ledger. Inference is native
Windows, CPU only, with a 6.4 GB sampled working-set guard.

## Results

All 24 presentations completed. Peak sampled working-set RSS was
2,459,185,152 bytes (2.46 decimal GB). Measurements do not verify
Windows paging or unsampled peaks.

- With one correct candidate, single presentations produced eight
  correct selections, one wrong selection, and three withholds out of
  twelve. Agreement across reversed orders retained three correct
  deliveries and withheld three of the six report pairs.
- With both candidates wrong, single presentations produced five
  false accepts and seven correct withholds out of twelve. Only three
  reports returned NEITHER in both orders. The agreement rule withheld
  on all six report pairs, because none selected the same wrong program
  in both orders.

Across both pair types, the agreement rule produced three correct,
zero wrong, and nine withheld outcomes. It filtered all six observed
wrong choices while retaining some coverage. The two presentations
per pair and two pair types per report are dependent measurements.
Zero observed wrong deliveries on six reports does not establish a
low population error rate. This run used one reference and constructed
errors rather than a naturally generated candidate pool.

This is a concrete 8 GB result for the agreement rule. The next
deployment-oriented question is whether two generated candidates
provide enough correct programs for this rule to retain useful
coverage, and whether correlated errors survive the agreement check.
The 16 GB tier remains gated.
