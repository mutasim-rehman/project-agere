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
- Exact-prefix endpoint selector is integrated with KEEP, immutable retained
  calculations, the shared output ledger and post-edit verification. Real-model
  evaluation is pending; strong SAS has zero oracle prefix gains on these cases.
- Optional 3B Q4 drafter profile is implemented as a separately labelled model-
  allocation control. Eight-case diagnostic completed within peak RSS 3.823 GB:
  2 correct, 1 correct delivery, 1 wrong delivery, 6 withheld. Full matched testing
  remains necessary before claiming an allocation gain.
- 124 contract tests pass. They do not establish financial reasoning correctness.
- Separate memory-monitored fixed-output repair harness is ready for plain versus
  proof feedback on the same algebraically flagged cohort. Original output tokens
  are debited; changed answers are reverified. Grammar/compatibility checks pass,
  but real-model repair gain and fresh end-to-end benefit remain unmeasured.

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
- Full original-MAS analysis completed: 1/24 correct, 1 correct delivery, 17 wrong
  deliveries, 6 withheld; peak RSS 5.246 GB, 5692 output tokens. Accuracy matches
  its direct baseline with one win/one loss, while wrong deliveries rose 13 to 17.
- Matched full 3B Q4 analysis completed: 4/24 correct, 3 correct deliveries,
  1 wrong delivery, 20 withheld (19 abstentions); peak RSS 3.830 GB. It gains four
  cases and loses one versus 1.5B; exploratory McNemar p=0.375. Lower memory/output
  tokens accompany longer inference time, and useful answer coverage remains low.
- Shared retrieval includes all annotated evidence in 19/24. Two numerical
  references disagree; retain all cases and report declared-unit and raw metrics.
- New table-complete plus four-text-unit packets include all annotated evidence
  in 23/24 (40/41 units). This is retrieval coverage, not model accuracy; actual
  inference and token fitting remain untested. Original packets remain available.
- The frozen serial sequence completed; its journal and all three run artifacts
  are committed. Source edits may resume. No old worker needs restarting.

## Mechanism diagnostics

- New offline exact value-influence audit detects algebraically canceled source
  quantities, conditional on defined divisions. It flags two wrong deliveries in
  stronger SAS, but is not a semantic correctness certificate or rejection rule.
  Four numeric training sketches also flag, exposing equal-value cell-binding
  ambiguity in transfer construction. No frozen bank/code input was modified.
- A partial-binding compiler now preserves candidate source identities instead
  of silently choosing the first equal-valued cell. Training-bank audit finds
  529 unique numeric mappings and 91 ambiguous examples. These are not semantic
  error counts; model-facing targets remain unchanged during the frozen sequence.

- Strict sketch+unit shape matches: retrieved top two cover 10/24, whole bank 15/24.
  Equivalent formulas are not counted. This is expressibility, not achieved accuracy.
- Single-edge reconnection oracle coverage: zero MAS and one SAS error. Endpoint
  prefixes contain a correct answer in two errors per arm with original units fixed.
  The stronger SAS analysis baseline has zero oracle prefix gains. These are oracle
  upper bounds; no model-selected repair gains are established. Endpoint repair is
  currently a control, not a promising main contribution on the stronger system.
- Post-hoc year-range operands occur in nine MAS and one SAS baseline cases.
  Eighteen annotated training examples require the same numeric range, so no
  blanket numeric filter or source-number rewriting was introduced.

## Live run and next measurements

Larger-drafter first-eight diagnostic completed; no restart is needed. It loaded
the pre-endpoint 5852a16 pipeline; its manifest hashes remain preserved.

Serial plan data/strong-baselines-sequence-02.json is live: exec session 3195,
controller PID 121418. Both matched MAS analyses completed; SAS table-complete
analysis is now running. Journal/log prefix:
logs/strong-baselines-sequence-02. Forty-six source/data hashes are frozen; do not
edit those inputs or launch competing inference until completion/replanning.

Prepared follow-up: data/proof-feedback-pilot-01.json, plain versus proof feedback
on the better completed SAS baseline under a predefined aggregate selection rule.
It waits for the baseline controller and retains all selected baseline cases.
Fifty-three hashes freeze its inputs; actual repair results remain unmeasured.

1. Test the larger quantized MAS drafter under actual memory monitoring, with its
   profile and changed precision explicitly separated from the original FP16 study.
2. Improve retrieval and measure binding. Endpoint selection is now integrated but
   cannot improve the current stronger SAS slice even with oracle prefix selection.
3. Broaden development evaluation after positive diagnostics, then freeze systems
   and new confirmatory data. Stronger verification and KYC/credit coverage remain.

FinMAN, BudgetVerify, CoVe, BRA-Audit, ThinkBrake and program induction are close
priors. Strict change preservation still needs a useful distinction against them.
No new sealed confirmatory evaluation exists; the FinQA test split remains unopened.

Use .local/git-askpass with .env for milestone pushes; never expose credentials.
Leave the unrelated user-owned .GITIGNORE untouched.
