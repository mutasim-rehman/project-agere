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
