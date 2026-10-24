# Research checkpoint — 24 October 2026

Goal remains active. Useful novelty, a validated repair gain and publication-quality
confirmation are not established. Historical results and raw runs remain preserved.

## Current implementation

- Source-built llama-cpp-python 0.3.16; pinned official weights and training data.
- CPU, F16 KV, context 4096 for FinQA, 2048 output tokens per case; nominal sampled
  parent+worker RSS cap 6.40 decimal GB. This simulates an 8 GB tier on a larger host.
- Source-pointer arithmetic, causal grammar, compact/full catalogs, unit controls,
  deterministic execution, verification and full/patch/edge repair baselines.
- Fixed or question-retrieved training demos; 620 retrieved examples exclude all
  annual-report groups represented anywhere in development. Example IDs are logged.
- Direct generation or retrieved-sketch/source-binding planner; optional budgeted
  formula analysis. These are stronger known baselines, not originality claims.
- Separate exact-prefix endpoint selector is implemented, with KEEP and immutable
  retained calculations. Pipeline integration and real-model evaluation are pending.
- Optional 3B Q4 drafter profile is implemented as a separately labelled model-
  allocation control. Weights verified (2,104,932,768 bytes); no fit/quality claim yet.
- 90 contract tests pass. They do not establish financial reasoning correctness.

## Completed development measurements

- Original synthetic rules: 150/150; temporal KYC rules: 24/24. Use as regression
  suites, not main evidence of useful LLM reasoning. Four-case KYC repair gave no gain.
- FinQA first-24 MAS direct baseline: 1 correct, 1 correct delivery, 13 wrong
  deliveries, 10 withheld; all programs executable/source-supported; peak RSS 5.248 GB.
- Matching SAS direct baseline: 7 reported-answer matches, 6 raw execution matches,
  7 correct deliveries, 6 wrong deliveries, 11 withheld; peak RSS 5.132 GB.
- Full SAS formula-analysis ablation: 13 reported-answer matches, 8 raw execution
  matches, 13 correct deliveries, 5 wrong deliveries, 6 withheld; peak RSS 5.132 GB.
  Primary metric gained six cases with zero losses; exploratory McNemar p=0.03125.
  Output tokens 2059 to 5135; prompt tokens 73469 to 98085. All 24 analysis calls
  reached the 128-token allowance. This is reused development data, not confirmation.
- MAS two-case controls: analysis 0/2, larger 1.5B verifier 0/2, retrieved demos 0/2,
  sketch planner 0/2. SAS sketch planner 1/2 plus one abstention. All fit the cap.
- Shared retrieval includes all annotated evidence in 19/24. Two numerical
  references disagree; retain all cases and report declared-unit and raw metrics.
- The frozen serial sequence completed; its journal and all three run artifacts
  are committed. Source edits may resume. No old worker needs restarting.

## Mechanism diagnostics

- Strict sketch+unit shape matches: retrieved top two cover 10/24, whole bank 15/24.
  Equivalent formulas are not counted. This is expressibility, not achieved accuracy.
- Single-edge reconnection oracle coverage: zero MAS and one SAS error. Endpoint
  prefixes contain a correct answer in two errors per arm with original units fixed.
  These are oracle upper bounds; no model-selected repair gains are established.
- Post-hoc year-range operands occur in nine MAS and one SAS baseline cases.
  Eighteen annotated training examples require the same numeric range, so no
  blanket numeric filter or source-number rewriting was introduced.

## Next measurements

1. Test the larger quantized MAS drafter under actual memory monitoring, with its
   profile and changed precision explicitly separated from the original FP16 study.
2. Integrate bounded endpoint selection with the shared token ledger and post-edit
   verification; compare gains, regressions and costs against full regeneration.
3. Broaden development evaluation after positive diagnostics, then freeze systems
   and new confirmatory data. Stronger verification and KYC/credit coverage remain.

FinMAN, BudgetVerify, CoVe, BRA-Audit, ThinkBrake and program induction are close
priors. Strict change preservation still needs a useful distinction against them.
No new sealed confirmatory evaluation exists; the FinQA test split remains unopened.

Use .local/git-askpass with .env for milestone pushes; never expose credentials.
Leave the unrelated user-owned .GITIGNORE untouched.
