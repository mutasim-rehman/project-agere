# Research checkpoint — 24 October 2026

Goal remains active. A novel, useful repair method and publication-quality evidence
are not established. Do not mark the goal complete from these development results.

## Infrastructure and code

- Local source-built llama-cpp-python 0.3.16, verified pinned GGUFs, CPU inference.
- Nominal sampled process-tree RSS ceiling 6.40 decimal GB; output cap 2048/case.
- Three MAS roles can share identical weights; each call resets KV state.
- Bounded cited arithmetic, source-pointer plans, causal grammar, unit controls,
  compact catalogs, graph-preserving patches, training-only demonstrations.
- Optional 128/256-token formula/measure analysis is implemented. A two-case MAS
  128-token smoke completed 0/2 correct, both wrongly delivered; both analysis
  stages reached their token limit. Default zero preserves the common baseline.
- Matching SAS analysis smoke completed 2/2 reported-answer matches (1/2 raw
  execution matches), both correctly delivered, versus 0/2 in its baseline prefix.
  Both analysis calls reached their allowance. Larger development testing remains.
- 78 tests pass. These checks establish contracts, not financial correctness.
- Optional training-sketch planner chooses a retrieved formula and binds its
  variables to current quantities. Preserves operations/constants/units and logs
  choice versus bindings. All 24 schemas compile; real-model gains unmeasured.
- Offline strict-shape diagnostic: retrieved top-two sketches match the annotated
  program+unit shape in 10/24 cases; the full bank matches 15/24. Alternative
  equivalent programs are not counted; this is not achieved accuracy. Five
  unrepresentable/discordant references remain in the denominator with reasons.
- Optional question-only BM25 demonstration retrieval uses 620 eligible training
  examples, excluding all annual reports in development. MAS smoke remains 0/2
  correct, one wrong delivery and one withheld; both demos fit each prompt. Fixed
  demonstrations remain available. Proposed and fitted example IDs are logged.
- Shared 1.5B-verifier MAS smoke also remains 0/2 correct, both wrongly delivered;
  peak RSS 3.862 GB. Greater verifier size alone did not fix semantic checking.
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
- Matching SAS baseline completed: 7/24 reported-answer matches, 6/24 raw execution
  matches, 7 correct deliveries, 6 incorrect deliveries, 11 withheld. Peak RSS
  5.132 GB; 2059 generated tokens; no stage truncation. The paired success
  difference is +6/24 for SAS, exploratory exact McNemar p=0.0703.
- Completed graph audit finds only one oracle-correctable SAS error and zero MAS
  errors under the bounded reconnection candidate set. This is a narrow mechanism,
  not a promising general solution to the present semantic reasoning failures.
- Shared retrieval includes all annotated evidence in 19/24 cases. Two reference
  records disagree; all remain included with separate metrics.
- Both selected training demonstration pages and annual-report groups are absent
  from the entire development split; their IDs and source hashes are recorded.

## Live run

Full SAS formula-analysis ablation: research/tier8_v2/runs/finqa-sas-analysis-dev24-01
Exec session: 14672. Revalidate its worker process before calling it stopped.
24 development cases, 128 analysis tokens, fixed demonstrations; matches the
no-analysis baseline otherwise. The debug prefix is reused development data.
Partial output is not a final result. Do not launch competing inference here.

## Next steps

1. Preserve the completed SAS run and paired analysis; do not infer a general
   architecture winner from these development cases.
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
