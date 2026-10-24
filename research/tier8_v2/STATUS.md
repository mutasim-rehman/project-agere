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
- 148 contract tests pass. They do not establish financial reasoning correctness.
- Separate memory-monitored fixed-output repair harness is ready for plain versus
  proof feedback on the same algebraically flagged cohort. Original output tokens
  are debited; changed answers are reverified. Grammar/compatibility checks pass,
  but real-model repair gain and fresh end-to-end benefit remain unmeasured.
- A dedicated paired replay evaluator now verifies shared snapshots/cohorts,
  recomputes scores and triggers, checks token debits and separates fresh repair
  costs from recorded baseline costs. Its integration fixture uses mocked replies.

## Adaptation data prepared; no training yet

Revision 01 is superseded and must not be used: serialization changed evidence
order after A-ID labelling. Revision 02 fixes the order before labelling and
revalidates every saved row. The current exporter and prompt capture reject
persisted source-ID mismatches. Existing live experiments/demos are unaffected.

Actual no-analysis/no-demo deployment prompt capture is complete: 761 examples
fit 1,024 training tokens for both GGUF tokenizers (661 train, 100 validation),
without truncation. Full token-ID hashes agree. See evidence/deployment-sft-1024-02.json
and data/ADAPTATION_README.md. HF tokenizer parity, training and actual adapter
application remain pending. Manual historical prompt counts treat chat markers as
ordinary text; generation recognizes them. Fix accounting after the frozen runs;
keep historical counts explicitly labelled estimates, with no silent rescoring.


A separate train-only exporter materialized 1,653 training examples (422 report
groups) and 198 validation examples (50 report groups), excluding every development
report group. It quarantines ambiguous bindings instead of producing first-match
source targets (559 rejected), checks deployment unit admissibility, and preserves
all rejection counts/IDs. Source uniqueness is numerical, not semantic adjudication.
Audit: evidence/cell-adaptation-data-02.json; independent materialized hash, split,
exclusion and total-count checks pass. Deployment prompt fitting is complete for the no-analysis baseline above;
HF parity, training, adapter application and comparative inference remain pending.
All 59 frozen live inputs remain unchanged. This is a baseline-enabling corpus,
not a demonstrated reasoning gain or original method.

## Source-cell foundation (not used in the live sequence)

A new independent cell catalog preserves legacy quantity IDs/values and selected
source rows, adds exact table coordinates/labels, and compiles cell-specific
citations. Narrative identity remains span-level; semantic correctness is not
certified. All 67 executable plans across four completed development baselines
retain their numeric outputs, and 620 training targets remain executable.
Within-row equal-valued cell collisions occur in 5/24 original packets, 7/24
table-complete packets and 71/620 training examples. These are not error rates.
Audit: evidence/source-cell-identity-audit.json. Integration and accuracy testing
are pending; all live frozen inputs remain unchanged.

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

## Completed follow-up and next measurements

MAS 3B 256-token analysis completed: 4/24 reported matches, 4 raw matches,
3 correct deliveries, 10 wrong deliveries, 11 withheld; peak RSS 3.827 GB.
Against 128 tokens: one primary win/one loss, unchanged correct delivery, wrong
deliveries 1 to 10, generated tokens 4778 to 7653. V2 unit sensitivity leaves
both totals unchanged. No further MAS reasoning-budget expansion is planned.
SAS 256-token analysis started at 16:00:38 UTC and remains in the frozen sequence.


The earlier baseline and proof-pilot controllers completed successfully. A new
analysis-length sequence is active (details below).
Table-complete SAS: 13/24 reported matches, 8 raw matches, 13 correct deliveries,
5 wrong deliveries, 6 withheld, peak RSS 5.133 GB. One win and one loss against
original-packet SAS analysis; more available operands did not improve the total.

The predeclared pilot selected original-packet SAS. Plain and proof feedback both
made zero corrections, with zero regressions. Both withheld MRO and retained STT's
wrong answer: correct deliveries 13, wrong deliveries 4, withheld 7. Only two cases
triggered. Proof consumed 83 fresh output tokens versus 172 plain, with more prompt
tokens (3582 versus 3239). This is component replay, not fresh end-to-end inference.
Validated paired results are in evidence/finqa-proofpilot-paired-01.json and
evidence/finqa-sas-table-analysis-dev24-paired.json. No proof-feedback gain exists.

The separate v2 ratio-unit sensitivity audit reproduces legacy scores and changes
none of the six analysis/replay totals. AAPL percentage-point annotation remains
unresolved; no historical result was overwritten. See evidence/finqa-unit-audit-v2.json.

Live frozen experiment: 256-token analysis for MAS 3B and SAS on the same original
24 packets, fixed two demos and unchanged total token/RSS ceilings. Compare each
against its own 128-token result. This is stronger-baseline tuning. Controller
session 61231, PID 159981; plan data/analysis256-sequence-01.json, journal/log prefix
logs/analysis256-sequence-01. MAS completed; SAS is now running. All 59 inputs remain frozen.
Historical metric/output files remain immutable; any revised scores must be
versioned separately. Next baseline work must address source binding, longer
reasoning and model adaptation, rather than presenting this negative pilot as
novelty. Broader evaluation and independently sourced confirmation remain open.

FinMAN, BudgetVerify, CoVe, BRA-Audit, ThinkBrake and program induction are close
priors. Strict change preservation still needs a useful distinction against them.
No new sealed confirmatory evaluation exists; the FinQA test split remains unopened.

Use .local/git-askpass with .env for milestone pushes; never expose credentials.
Leave the unrelated user-owned .GITIGNORE untouched.
