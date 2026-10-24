# Research checkpoint — 24 October 2026

Goal remains active. A novel, useful repair method and publication-quality evidence
are not established. Do not mark the goal complete from these development results.

## Infrastructure and code

- Local source-built llama-cpp-python 0.3.16, verified pinned GGUFs, CPU inference.
- Nominal sampled process-tree RSS ceiling 6.40 decimal GB; output cap 2048/case.
- Three MAS roles can share identical weights; each call resets KV state.
- Bounded cited arithmetic, source-pointer plans, causal grammar, unit controls,
  compact catalogs, graph-preserving patches, training-only demonstrations.
- Optional 128/256-token formula/measure analysis is implemented but has not yet
  been evaluated with real models. Default zero preserves the common baseline.
- 68 tests pass. These checks establish contracts, not financial correctness.
- A gold-free dependency-reconnection selector is implemented and unit-tested.
  It offers KEEP plus at most seven single-edge alternatives and rechecks the
  selected program. Actual model-selected repair gains remain unmeasured.
- Use ignored .local/git-askpass with .env for milestone Git pushes. Do not expose
  credentials or touch the user's unrelated .GITIGNORE.

## Completed measurements

- Original synthetic rules: 150/150; temporal KYC rules: 24/24. Treat as regression
  suites, not the main argument that financial LLMs are useful.
- Four-case temporal KYC: MAS 1/4 correct and 1 correct delivery after controls;
  SAS 3/4 correct and 2 correct deliveries. Patch repair gained nothing in either.
- MAS distinct-instance repeats breached 6.4 GB; shared setup fits near 5.14 GB.
- Initial FinQA debug recipes (two cases) exposed source-supported wrong arithmetic,
  format mistakes and false verifier accepts. Raw runs are preserved.
- Full first-24 FinQA MAS baseline with compact causal references and two training
  examples: 1/24 correct, 1 correct delivery, 13 wrong deliveries, 10 withheld.
  All 24 programs were source-supported/executable; peak RSS 5.248 GB; no truncation.
  Raw-execution and reported-answer metrics both have one match.
- Shared retrieval includes all annotated evidence in 19/24 cases. Two reference
  records disagree; all remain included with separate metrics.
- Both selected training demonstration pages and annual-report groups are absent
  from the entire development split; their IDs and source hashes are recorded.

## Live run

Matching SAS baseline: research/tier8_v2/runs/finqa-sas-demos-dev24-01
Exec session: 55655. Revalidate this handle or its actual worker process before
calling it stopped. It runs the same recipe with analysis_tokens=0. Partial output
is not a final result. Do not launch a competing inference job on this host.

## Next steps

1. Inspect and commit/push the completed SAS 24-case run and paired analysis.
2. Validate budgeted formula analysis in actual inference, then evaluate it in both
   arms with the same recipe. Strong baselines must separate reasoning from syntax.
3. Investigate stronger resident-model verification and FinMAN-style staged formula
   planning. Current tiny-critic PASS decisions are not trustworthy.
4. Evaluate whole-program retry, local repair, and independent re-extraction after
   strong generation works. Measure false locks and harm as well as gains.
5. Complete closer-prior review, develop a demonstrably useful distinction, freeze
   new confirmatory systems/data, and evaluate beyond the current development slice.

FinMAN, CoVe, BRA-Audit and financial program induction are close priors; do not
claim those established concepts as novel. Read RELATED_WORK_MATRIX.md and
NOVELTY_AUDIT.md. No new frozen confirmatory evaluation exists. The old test split
has not been opened during redevelopment. Broader KYC/credit coverage is unfinished.
