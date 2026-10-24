# 8 GB tier study decisions

## Redevelopment — 24 October 2026

### Completed retrieval and controlled feedback experiments

- The frozen stronger-baseline sequence and its dependent proof pilot both
  completed. Table-complete SAS analysis obtained 13/24 reported-answer matches,
  8 raw execution matches, 13 correct deliveries, 5 wrong deliveries and 6 withheld.
  Against the original-packet SAS analysis there was one primary win and one loss.
  Peak RSS was 5,132,591,104 bytes; 5,359 output tokens and 2,758.61 inference seconds.
  Better operand availability did not produce an aggregate gain on this slice.
- The predeclared selection rule chose the original-packet SAS baseline. Two of
  its 24 cases triggered algebraic feedback. Plain retry and proof feedback both
  retained 13 correct answers and reduced wrong deliveries from 5 to 4 by changing
  MRO to INSUFFICIENT; neither corrected an answer. STT remained wrong. Proof used
  83 fresh output tokens versus 172 plain, but 3,582 prompt tokens versus 3,239.
  This tiny development component replay establishes no accuracy advantage or
  general efficiency advantage for proof feedback. Both paired analyses validate.
- Historical scores use the original declared-unit reported-answer metric. A
  potential mismatch between its accepted unit labels and the deployment prompt
  is under audit. Preserve completed outputs and the original selection decision;
  any corrected evaluation must have a separate explicit version and sidecar.

### Additional prior and input-availability checks

- Inspected DCRC's main method/setup (arXiv:2605.31064v1): source-labelled task
  routing, conflict/missing symbol binding, deterministic execution and training
  on Qwen2.5 1.5B/3B/7B. These compiler/auditing components are established. Our
  untuned protocol should not be presented as the best attainable small-model
  performance; training and less restrictive prompting controls remain open.
- Inspected VerityMath's abstract and method: program-level unit assertions,
  generated annotations and fine-tuning. Its reported checker-enhanced variants
  slightly underperform their plain program baselines. This reinforces measuring
  feedback/checker value against retry rather than claiming benefit from structure.
- Offline literal-availability check: original packets contain every annotated
  nonconstant operand value in 20/24 cases; table-complete packets do so in 24/24.
  None of the missing original values appears only in the question. Equal-valued
  wrong cells can still match, so this is not semantic source coverage or achieved
  accuracy. Stored packet/helper/source hashes and all missing-value records;
  no evidence selection or frozen inputs were changed.

### Paired repair-result validation

- Added a dedicated component-replay evaluator rather than treating replay as a
  fresh generation run. It requires complete memory-valid runs, identical model/
  source/code/snapshot identities, matching initial states and algebraic cohorts,
  correct condition order and consistent case-level token debits.
- It recomputes source executions, baseline/final scores, delivery gates and
  functional-influence triggers. Logged retry prompts must contain the symbolic
  diagnostic only in the proof condition. Unflagged cases cannot change or spend
  retry tokens. These checks prevent a cohort or bookkeeping change from looking
  like useful feedback.
- Reports all-case paired outcomes as primary, eligible-only outcomes secondarily,
  corrections/regressions, wrong deliveries/withholding, fresh tokens/prompts/calls,
  truncation, fresh worker wall time/RSS and recorded baseline costs separately.
  Input-artifact and analysis-code hashes preserve reproducibility. No discordance
  or a zero bootstrap interval must not be interpreted as equivalence or novelty.
- One hundred twenty-nine tests pass, including a full evaluator integration
  fixture with mocked model replies and real development source packets. That
  fixture is software validation, not an observed model repair gain. Only new
  analysis code/tests were added; all 53 frozen experiment inputs remain unchanged.

### Controlled proof-feedback repair component

- Implemented a gold-free repair function and a separate memory-monitored replay
  harness. Plain and proof conditions use the same exact-cancellation trigger,
  model, 512-token retry allowance and 192-token verification allowance. Only
  proof exposes the value-influence diagnostic and its legitimacy/domain caveats.
  Both can KEEP, replace with a grounded reference plan, or explicitly abstain.
- Original generation/verification tokens are debited before fresh calls from
  the same 2048-case ledger. Invalid proposals preserve the old state; changed
  proposals are executed and reverified. Algebraic cancellation is not itself a
  rejection reason. This tests feedback value, not just the effect of an extra call.
- Parent exports model-only snapshots, rejecting inconsistent token traces and
  duplicate case IDs. Worker does not read old scores; gold evaluation occurs
  after all repair calls. Fresh repair latency/tokens and recorded baseline costs
  remain separate. This is fixed-output component replay, not measured fresh
  end-to-end generation; any positive result still needs a fresh integrated run.
- Preflight checks baseline completeness, packet/evaluation hashes, helper hashes,
  model/runtime compatibility and AST equality of actual inference/scoring helpers.
  The parent records code/checkpoint/snapshot hashes and sampled process-tree RSS,
  rejects concurrent inference and existing outputs, and retains failed partials.
- One hundred twenty-two tests pass, covering labels excluded from snapshots,
  shared budget debit, proof/plain trigger equality, legitimate KEEP, invalid
  replacement rollback, post-verification delivery gating and exhausted budget.
  Actual grammar compilation passed on both eligible strong-SAS baseline cases;
  compatibility preflight passed. No real repair gains are measured yet.
- Prospective development-pilot rule: after the frozen sequence completes,
  choose between SAS analysis and SAS table-complete analysis by higher primary
  correctness, then correct delivery, fewer wrong deliveries and fewer output
  tokens (stable name tie break). Run plain then proof on ALL saved cases of that
  selected baseline; eligibility is algebraic, never selected using case labels.
  Aggregate development selection is disclosed; this is not a held-out test.
- Only new files were added to the experiment path. The existing frozen SAS
  retrieval run and all 46 input hashes remain unchanged.
- Prepared a prospective pilot controller and plan proof-feedback-pilot-01.json.
  It verifies the live baseline controller's PID/creation time and requires its
  journal to finish complete before baseline selection or any repair inference.
  It then runs plain and proof serially on the selected full saved cohort.
  Fifty-three hashes freeze baseline inputs plus new repair code and the old
  completed candidate's artifacts. No retry/overwrite behavior is introduced.
- Selection-rule tests bring the suite to 124 passing checks. The plan is recorded
  before the table-complete baseline result is known. Prompt lengths and actual
  token/call expenditure can differ across conditions and must be reported; only
  trigger policy and output ceilings are matched. No causal or novelty result is
  established by the plan or by unit tests.
- Launched the pilot controller: exec session 19102, PID 146872. Its journal
  confirms a verified-live wait on controller PID 121418 and matching creation
  time. The SAS retrieval worker remains active; no repair inference has started.
  All 53 frozen input hashes were revalidated after launch. Journal/log prefix:
  logs/proof-feedback-pilot-01. Preserve completed journals/results at the next
  measurement milestone; do not edit frozen code/data or start competing models.

### Full larger-drafter allocation result

- Matched 3B Q4 analysis completed 24/24 within peak RSS 3,829,968,896 bytes:
  4 reported-answer matches, 2 raw execution matches, 3 correct deliveries,
  1 wrong delivery, 20 withheld (19 explicit abstentions), 4778 output tokens.
  Compared with 1.5B analysis, primary accuracy gains four cases and loses one,
  net +3/24. Exploratory exact McNemar p=0.375; this is not a general advantage.
- Peak RSS decreases from 5.246 to 3.830 GB, output tokens 5692 to 4778,
  prompt tokens 99479 to 96037; recorded inference time increases 770.29 to
  980.64 seconds. Precision among delivered answers must not conceal low overall
  coverage. The tiny critic also withheld one correct answer; executability gating
  rejects many PASS judgments on abstaining outputs, so PASS counts alone mislead.
- Functional-influence audit finds no canceled source value in its five executable
  programs. The stronger 3B system's dominant issue is abstention/semantic binding,
  not the cancellation pattern from weaker generation. Do not claim one diagnostic
  explains all remaining errors. All 24 cases and negative outcomes are retained.
- The controller has started SAS table-complete analysis after valid completion;
  remaining code/data inputs stay frozen. Further baseline tuning should consider
  the implemented 256-token analysis option because all 128-token notes truncate,
  before treating either configuration as a capacity ceiling.

### Preserve source-identity uncertainty in numeric training programs

- Added a separate partial-binding compiler. A numeric operand keeps every
  matching source-cell ID; annotated evidence spans are recorded as hints and
  cannot silently narrow the domain. Repeated ambiguous occurrences keep separate
  slots whose domains may overlap/alias. Only a unique numeric cell identity may
  be automatically reused. An ambiguous result has no resolved training target;
  resolution requires an explicit admissible assignment and preserves operations,
  constants and prior-step references. Domain membership is not semantic truth.
- A concrete training record (AWK/2018/page_172.pdf-2) asks about 2019 and 2020
  values, both 65, but its annotated source points to the 2021 row, also 65.
  The former compiler's first matching annotated cell creates a constant transfer
  sketch. Numeric execution success alone cannot establish source-role identity.
  No original report claims or all-annotation error rates are inferred from this.
- Audited all 620 bank examples using training source only: 529 have unique
  numeric-cell mapping in the available packet; 91 are ambiguous. Three of four
  canceled legacy sketches are ambiguous by this conservative test. Unique numeric
  mapping still does not prove that the right periods/roles were retrieved.
  All uniquely mapped plans exactly match their historical compiled targets.
- This exposes uncertainty rather than pretending to resolve it by splitting
  equal values into independent causal variables. Future transfer must resolve
  cell roles or explicitly abstain/exclude an ambiguous demonstration. The model-
  facing bank, frozen jobs and their inputs are unchanged. One hundred eleven
  tests pass, including no forced alias, annotation hints, constants, reference
  preservation, explicit assignments and parser rejection. Novelty/gains unproven.

### Full original-MAS formula-analysis result

- Original 1.5B MAS analysis completed 24/24, peak RSS 5,245,755,392 bytes:
  1 correct and correctly delivered, 17 wrong deliveries, 6 withheld, 5692 output
  tokens. All 24 programs execute with lexical source support, yet 23 are wrong.
  Relative to its no-analysis baseline, correctness is unchanged at 1/24, with
  one newly correct case and one regression; wrong deliveries increase 13 to 17.
  This is a negative result, not evidence that longer reasoning helps this model.
- Extended exact influence diagnostics: four programs have canceled source-value
  influence, including three wrong deliveries, and no correct flagged case in
  this development slice. This is an observed diagnostic association; annotated
  training ambiguity and legitimate cancellation still prohibit a blanket gate.
- The frozen controller has started the matched 3B full 24-case analysis after
  valid completion of the 1.5B run. The SAS table-complete run remains next.
  All 46 frozen inputs are unchanged; current diagnostics only add new offline
  code/artifacts outside that execution path. No confirmatory claims are made.

### Exact functional-influence diagnostic

- Added an offline bounded rational-polynomial audit of source-reference programs.
  Each quantity ID is an independent symbol, even if observed values coincide.
  A zero rational derivative proves value independence on the program's defined
  domain, unlike a local numerical gradient that can vanish at a stationary point.
  Division-definedness guards are retained. This is standard symbolic algebra,
  not a claim that differentiation, provenance or cancellation detection is new.
- Bounds on operations, polynomial terms and coefficient bits return unknown on
  excess work; unsupported inputs are not certified. A canceled quantity may
  still establish that division is defined or legitimately cancel, so the audit
  is a repair hint, not a correctness certificate or automatic rejection policy.
- Completed-program audit: two source-cancellation cases in the original MAS
  baseline (one wrong delivery), none in original SAS, two in stronger SAS analysis
  (both wrong deliveries), none in the eight-case 3B diagnostic. Strong SAS examples
  include multiplying a financial amount by zero and canceling a period quantity
  by dividing and multiplying by it. No model-selected repair is measured yet.
- Countercheck on all 620 training sketches finds four flagged numeric targets.
  All reuse one source variable in an apparent two-period comparison: value-only
  target compilation can bind equal numbers from distinct source roles to the
  same cell, creating constant transfer sketches. This exposes source-identity
  ambiguity in the training adapter; it does not prove that legitimate zero-change
  answers are wrong. Future sketch derivation must preserve/resolve cell roles or
  mark such transfers ambiguous. The frozen bank is unchanged, and the current
  queued runs use the separate fixed examples, not these four retrieved sketches.
- Audit checks each run's packet hash and historical quantity-catalog code hash
  before interpreting references. One hundred five tests pass, including exact
  cancellation, distinct equal-valued cells, stationary points, division guards
  and resource exhaustion. No frozen input changed; only new offline files/tests
  were added. A future proof-informed repair needs comparison against retry and
  simple identity heuristics before any utility or originality claim.

### Table-complete retrieval control and larger-drafter diagnostic

- Added a shared non-oracle packet variant retaining all table rows and the four
  highest-ranked text units. It uses the same lexical ranking as before, never
  annotated evidence. On the fixed 24 IDs, post-selection annotation coverage
  improves from 19 to 23 fully covered cases (34/41 to 40/41 evidence units).
  ETR/2004/page_213.pdf-2 still lacks an annotated text unit. Maximum selected
  source text is 2052 characters; actual token fitting/accuracy remain untested.
- Kept old public packets immutable and wrote a new dataset plus provenance and
  coverage audit. New run manifests hash the retrieval implementation. Paired
  analysis keeps strict packet-hash equality by default; an explicit retrieval-
  change flag permits different packets only for the same FinQA evaluation-source
  hash and identical nonempty case sets. Ninety-seven tests pass, including gold-
  independent evidence selection and refusal of different evaluation sources.
- Larger 3B Q4 drafter diagnostic completed 8/8 within peak RSS 3,823,435,776 bytes:
  2 reported-answer matches, 1 raw match, 1 correct delivery, 1 wrong delivery,
  6 withheld, 5 abstentions, 1631 output tokens. This establishes sampled fit and
  limited diagnostic performance, not a clean checkpoint gain: a full matching
  1.5B analysis baseline is still required. Preserve all eight cases and traces.
- Next sequence will run full 24-case MAS analysis with the original 1.5B and
  then the 3B drafter on identical old packets, followed by the stronger SAS
  table-complete retrieval control. All are development experiments. The completed
  8-case result can authorize the serial sequence without inventing a live PID;
  missing or failed completion evidence still stops execution.
- Frozen and launched strong-baselines-sequence-02: exec session 3195,
  controller PID 121418, first worker PID 121451. Forty-six input hashes cover
  code, both packet variants, demos, evaluation source and weight manifests.
  The journal confirms valid completion of the eight-case dependency and starts
  full MAS 1.5B analysis. Then it runs matched 3B analysis and SAS table-complete
  analysis, serially. No code/data changes until completion or explicit replanning.

### Endpoint integration and stronger-baseline falsification

- Integrated optional endpoint repair in the financial pipeline: select with at
  most 192 output tokens while reserving 192 for post-edit verification, all on
  the existing shared ledger. A changed raw plan must compile to the exact
  preserved prefix; it is reverified and remains subject to the delivery gate.
  It can trigger despite an initial neural PASS, but cannot invent a new result.
  Ninety-three tests pass, including false-PASS repair, no-call single-step KEEP
  and rejection by the post-selection delivery gate. CLI restricts this primitive
  to source-reference financial programs; sketch baseline remains no-repair only.
- Extended the offline candidate audit to the stronger completed SAS analysis
  baseline. Oracle prefix gains are 0/24 there, versus 2/24 in its weaker direct
  baseline. Strong generation already eliminated the recoverable endpoint errors.
  This rules out a positive endpoint-gain claim on the current strong SAS slice;
  do not spend another full inference run pretending this is promising evidence.
- Keep the implemented primitive as an explicit control, not the main candidate
  contribution. New repair must survive strong generation; next priorities are
  source retrieval and semantic binding errors. Broader task results are needed
  before asserting the same failure pattern outside this development slice.
- The larger-drafter first-eight run is live (exec 40310, worker PID 117680).
  Its worker emitted stages before endpoint edits and retains its original
  5852a16 code snapshot/hashes. No hot reload or competing inference occurs.

### Larger quantized drafter allocation control

- Official Qwen 3B Q4_K_M weights downloaded and SHA-256 verified at revision
  7dabda4d13d513e3e842b20f0d435c732f172cbe: 2,104,932,768 bytes,
  hash 626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d.
  Source/download log and a separate candidate manifest are preserved. Original
  model manifests and historical configurations are unchanged.
- Added optional MAS drafter-model 3b-q4; default remains 1.5b-f16. Verification
  still selects the explicitly requested 0.5B or 1.5B checkpoint; selecting the
  larger drafter cannot silently change verifier size. Per-case metadata records
  actual drafter/verifier files and labels the model-allocation control separately.
- This tests whether quantizing a larger drafter improves use of the same RAM
  budget; it changes both model size and precision and is not a clean architecture
  ablation or novelty claim. Memory fit and quality require actual inference.
  Ninety contract tests pass, including distinct checkpoint loading and explicit
  verifier identity. Next diagnostic uses the fixed first eight development cases,
  128-token analysis, fixed training demos and the original 0.5B verifier; no repair.

### Completed reasoning and frozen sketch sequence

- Full SAS 128-token analysis ablation completed 24/24 within peak RSS
  5,131,788,288 bytes. Reported-answer correctness and correct delivery improved
  from 7/24 to 13/24, with six newly correct cases and zero regressions on that
  metric; wrong deliveries decreased from six to five, withheld from 11 to six.
  Output tokens increased 2059 to 5135 and prompt tokens 73469 to 98085.
- Paired exploratory exact McNemar p=0.03125; no multiple-comparison adjustment
  or fresh confirmation. All 24 analysis calls reached the 128-token allowance.
  Raw executable-reference matches increased 6 to 8 with different percentage
  conventions; the zero-regression statement applies only to the primary
  declared-unit reported-answer metric. This known reasoning baseline is a
  useful development improvement, not a novelty claim.
- Frozen serial diagnostics completed without competing inference: MAS sketch
  0/2 correct, both wrongly delivered, 156 tokens, peak RSS 5,236,670,464 bytes;
  SAS sketch 1/2 correct and delivered, no wrong deliveries, one abstention,
  110 tokens, peak RSS 5,114,847,232 bytes. MAS chose wrong quantity bindings;
  SAS abstained on the payment-volume case. Preserve both negative/partial results.
- The controller journal ends complete; all three runs have matching expected
  record counts, successful exit status and sampled peaks below the cap. The
  frozen execution sequence is finished, so source changes may resume. Next
  independent controls are larger quantized drafter allocation and endpoint repair.

### Source-operand risk diagnostic

- Audited completed source-reference baselines for source quantities with integer
  values in 1900..2100. This post-hoc heuristic flags 9/24 MAS cases (five wrong
  deliveries) and 1/24 SAS case (one wrong delivery); no flagged case is correct
  in this small development slice. It does not identify the primary error or
  prove that each flagged value is a date.
- Preserved the exact quantity IDs, step/operand positions and source contexts.
  Several are clear calendar contexts. Others look like escaped punctuation
  (e.g. 2022 before bullet-like phrases, 2014 in an otherwise missing-looking
  table cell); these are hypotheses requiring original-report verification, not
  permission to globally rewrite source numbers or reinterpret missing evidence.
- Countercheck against the training-only bank finds 18 annotated executable
  examples requiring year-range slots, including legitimate monetary amounts
  and valid duration calculations. Therefore reject a blanket numeric-range
  mask despite its attractive post-hoc development appearance. This is not an
  estimated held-out detector false-positive rate.
- The finding motivates source-role-aware typing as a future baseline/control,
  not a novelty claim. Withholding suspect outputs alone does not improve correct
  answer coverage. Current packets, inference code and all frozen queue inputs
  remain unchanged. Audit code/results/logs are preserved separately.

### Bounded answer-endpoint selector module

- Implemented a separate gold-free endpoint module. For a source-supported,
  executable ANSWER program it offers KEEP and every nonempty executable proper
  prefix (at most eight choices total). Unit, retained operations, operands and
  internal references stay fixed. Invalid/abstaining programs are outside this
  primitive's scope; full regeneration remains a necessary comparator.
- Selection accepts only a candidate ID. Application checks the exact expected
  prefix and rejects tampered units, operands or drop scope. Equal-valued choices
  are retained because different source lineages can yield the same number;
  numerical equality alone does not prove that a measure is relevant.
- Added a caller-budgeted model-choice callback with source/question/program and
  a finite hypothetical-result menu. KEEP remains available; a missing/invalid
  choice preserves the original. Caller integration must charge the shared case
  ledger and reverify changed answers. It is not yet enabled in the frozen runner,
  and no actual model-selected gains are claimed.
- The offline prefix audit now uses this same candidate implementation and still
  finds 2/24 oracle-potential corrections in each completed baseline. Eighty-eight
  tests pass, including exact prefix preservation, tamper rejection, same-value
  provenance, no model call without alternatives, and malformed-selection KEEP.
- Only new/unfrozen offline code was added/edited. All 38 frozen sketch-sequence
  inputs remain unchanged. Integrate and measure endpoint repair after that serial
  sequence completes; preserve the positive/negative strong-baseline results first.

### Serial sketch diagnostic execution

- Prepared a frozen two-job sequence: MAS then SAS, first two development records,
  no analysis, retrieved demonstrations, sketch planner, no repair. These isolate
  the planner from the ongoing direct-program SAS analysis ablation. The two
  familiar debug cases are exploratory, not confirmatory evidence.
- The sequence identifies the current SAS monitor by PID 68882 and its actual
  creation time, waits for that process, and requires a complete memory-valid
  24-case summary before starting either job. It refuses an observed active
  inference process, changed frozen inputs, existing outputs, or failed run;
  it does not restart/retry a job or overwrite its artifacts.
- Stored argv, source/data hashes and dependency identity in
  data/sketch-smokes-sequence-01.json. The controller records each wait/launch/exit
  in a new journal; each experiment retains the normal memory/stage evidence.
  Eighty tests pass, including rejection of failed/partial/over-cap dependencies.
  This is execution plumbing, not a research contribution. Preserve frozen code
  and data until the queued experiments finish, or explicitly replace the plan.
- Launched the sequence controller: exec session 83583, PID 76671. Its journal
  confirms a verified-live wait on the identified monitor. No queued inference
  has begun while the direct SAS run is active. Journal/log paths use the prefix
  logs/sketch-smokes-sequence-01. Commit the completed journal with final results.
- A new offline-only prefix auditor was added after freezing the plan; it is not
  imported by deployment and none of the 38 frozen input files was changed.
  Candidate prefixes use saved answer/evidence only; original declared unit is
  fixed, and gold scores candidates afterward. The completed baseline audit finds
  2/24 oracle-correctable errors in each arm: MAS Visa average payment volume and
  PNC derivatives ratio; SAS Citi return and Devon amortization average. Correct
  intermediates were followed by wrong extra operations. This exposes recovery
  headroom missed by the earlier unused-edge-only audit, not achieved model gains.
- Keep endpoint repair as a candidate for measurement after the frozen queue.
  The phenomenon is not novel: ThinkBrake's published abstract studies correct
  intermediate reasoning overwritten by later output and proposes a stopping
  policy. A program-endpoint selector needs a useful measured distinction, rather
  than calling intermediate-answer selection itself original.

### Training-sketch and source-binding baseline

- Added a separate offline shape audit, never imported by deployment. Retrieve
  candidates from the public question first, then inspect development gold only
  to compare strict variable-abstracted program+unit signatures. Ten of 24 cases
  have a matching shape among the top-two unit-compatible candidates, compared
  with 15/24 somewhere in the full bank. Nineteen references can be represented
  by the current packet/target adapter; four lack required operands and one has
  reported/execution disagreement. All 24 remain in the denominator.
- These are candidate-expressibility diagnostics, not model gains or a complete
  algebraic coverage test. Equivalent alternate programs can have different
  shapes, and tokenizer fitting can further reduce candidates. No oracle shape
  matches or bindings are written to public packets or the model-facing bank.
  The result motivates checking both retrieval and binding, not expecting this
  restricted sketch library to solve every development question.

- Added optional `--planner sketch` for both SAS and MAS. It uses question-only
  retrieved training examples and abstracts their source operands into V slots,
  retaining repeated-variable identity, operations, constants, step dependencies
  and declared units. Slot context and training question explain the formula;
  training numeric values are explicitly not current evidence.
- A single <=384-token constrained call chooses a sketch and maps all V slots to
  current A quantity IDs, or chooses NONE. Code instantiates and executes that
  structure before the existing verifier. The choice cannot introduce literals,
  constants, steps or operations. Incorrect formula selection/binding is still
  possible; executability and training provenance do not imply semantic truth.
- Exact tokenizer fitting reserves 768 generation tokens and filters incompatible
  output-unit sketches. The same 2048-token case ledger, memory monitoring and
  source packets remain. Proposed/fitted source IDs and raw sketch choice are
  recorded separately. Current implementation supports no-repair evaluation only;
  later repair comparisons require explicit controls, not silent mode mixing.
- This is a staged program-induction baseline related to FinMAN-style planning,
  not an originality claim. Separating formula choice from source binding is meant
  to strengthen generation and expose which decisions a future repair must change.
- Rebuilt the same 620-example bank with sketch metadata; independent audit
  confirms selection IDs unchanged and no development annual-report overlaps.
  Prior bank versions remain in Git and old run hashes remain immutable. All 24
  choice schemas and the empty-source abstention schema compile. Seventy-eight
  contract tests pass. Real-model gains remain unmeasured; SAS worker 68915 is
  still live, so no competing inference is launched.
- Closer-prior review found BudgetVerify (arXiv:2609.33052v1). Inspected its
  methodology/setup: offline training correctness/cost labels supervise a router
  over no check, local revision and independent solve-first calculator verification.
  Inputs are pre-verification features. This closes a broad adaptive financial
  verification/token-allocation novelty claim. A host-RSS limit was not found in
  those sections; do not claim no prior RAM-constrained method without fuller
  review. Our strict change contracts still require demonstrated benefit over
  those established alternatives, not merely implementation under another cap.
- Inspected FinChain dataset/metric sections: controlled symbolic templates,
  semantic/numeric step alignment with DTW and 5% relative numeric tolerance.
  Treat as possible supplementary mechanism evaluation; do not loosen our main
  metric or equate numeric closeness with correct measure binding. No FinChain
  data/test split was downloaded or opened. CIFQA abstract adds a further prior
  for financial specialist agents plus deterministic rule/calculation tools.

### Question-retrieved training demonstrations

- Added a stronger known baseline: question-only BM25 retrieval over eligible
  training demonstrations (k1=1.2, b=0.75, omit numeric tokens, deterministic ID
  ties). Select up to two different annual-report groups; exact tokenizer fitting
  still reserves 768 generation tokens. Both arms receive the same retrieval
  policy and public question. The existing fixed examples remain an ablation.
- Built 620 eligible examples from the pinned 6251-row training split. Excluded
  all 2511 training rows whose company/year report group occurs anywhere in the
  883-row development split before reading their training targets. Remaining
  examples require executable <=4-operation targets, supported quantities, matching
  training references, and <=1800 characters. Filtering shapes the demonstration
  bank only; no evaluation cases are removed. Build counts/hashes are preserved.
- Development IDs are used solely for source-group exclusion; development answers
  and programs do not affect selection. Similar questions across different reports
  remain eligible and are expected in a retrieval baseline. This is not evidence
  of novel reasoning or proof against pretraining contamination.
- Each case records proposed example IDs/scores separately from IDs that actually
  fit the prompt. The bank and retrieval source code are hashed in run manifests.
  Also added previously omitted program_graph.py to new-run code hashes. Historic
  manifests are not rewritten. Seventy-three contract tests pass; model gains are
  not yet measured. The existing SAS analysis worker is allowed to finish first.
- Independent bank/selection audit confirms zero development report overlaps and
  distinct selected report groups on all 24 public questions. Saved proposed IDs
  and scores before inference; do not confuse relevance with achieved correctness.
- SAS 128-token formula analysis completed on the same first two cases: 2/2
  reported-answer matches, 1/2 raw executable-reference matches, both correctly
  delivered, no wrong deliveries, 454 tokens, peak RSS 5,119,905,792 bytes. Both
  analysis stages hit their 128-token allowance. The no-analysis SAS prefix had
  0/2 correct. This motivates a larger development ablation, not a general gain
  claim. MAS with analysis remains 0/2 on those cases.
- Next isolated run measures MAS 1.5B verification with fixed demonstrations and
  no analysis before combining improvements. It shares the drafter checkpoint,
  resets KV between roles and omits the unused extractor. Label this homogeneous
  two-role setup accurately; it is not independently trained specialist diversity.
- Read Haque et al. setup/introduction (PDF pp. 1–3): failing tests plus traces
  inform complete-function repair, with alternative/adaptive representations.
  Our lack of deployment answer keys is a constraint, not proof of originality.
- Stronger-verifier smoke completed: 0/2 correct, both wrong answers still passed
  the 1.5B critic, 219 tokens, peak RSS 3,861,532,672 bytes. This configuration fits
  comfortably but does not establish better semantic verification. Original 0.5B
  controls remain available; do not present checkpoint size as achieved quality.
- Retrieved-demo MAS smoke completed: 0/2 correct, one wrong delivery and one
  withheld, 218 tokens, peak RSS 5,243,023,360 bytes. Both selected examples fit
  each prompt. More relevant training questions did not fix quantity/formula
  selection. Keep this negative baseline; broad MAS testing is not justified as
  a claimed gain from this smoke alone.
- Started full first-24 SAS formula-analysis development ablation (session 14672),
  128 analysis tokens, fixed demonstrations and otherwise matching its baseline.
  This follows a positive 2-case diagnostic; all 24 cases are retained, including
  the debug cases. It is development reuse, not a fresh confirmatory test.

### Bounded dependency-reconnection policy

- Implemented actual gold-free selection among KEEP and at most seven executable
  single-edge reconnects. Rank candidates by remaining unused steps, backward-edge
  distance and stable ID; never by correctness labels. A 192-token selection call
  and post-selection verification share the existing per-case output ledger.
- Reconnection can trigger despite a neural PASS because an unused intermediate
  is a structural hint. It is not proof of an error. Programs without eligible
  candidates are unchanged, including incorrect programs; this narrow policy
  cannot solve general measure-selection or formula errors.
- The selected raw plan is recompiled and asserted identical to the enumerated
  candidate. Operations, source quantities, declared units and other edges stay
  fixed. KEEP remains available. Unit tests exercise a false-PASS correction and
  no-candidate preservation; 68 tests pass. No real-model repair gain is claimed.
- Strong generation remains the priority. See REDEVELOPMENT_PLAN.md for the
  staged optimization, matched-resource controls and confirmatory requirements.
- Matching SAS first-24 baseline has completed under peak RSS 5,131,907,072 bytes:
  7 reported-answer matches, 6 raw-execution matches, 7 correct deliveries,
  6 incorrect deliveries and 11 withheld, 2059 output tokens. MAS has 1 match,
  1 correct delivery and 13 incorrect deliveries on the same IDs. Paired exact
  McNemar p=0.0703125 is exploratory, not a final architecture conclusion.
- Final graph coverage is limited: zero oracle-correctable MAS errors and one SAS
  error. Do not expand this narrow mechanism into the main contribution without
  evidence. Prioritize measure/formula reasoning. A two-case MAS 128-token
  formula-analysis smoke is now running, otherwise matching the baseline.
- MAS formula-analysis smoke completed inside peak RSS 5,237,657,600 bytes, with
  0/2 correct and both wrongly delivered; 449 output tokens. Both 128-token
  analysis calls ended at their allowance. The first analysis repeats the wrong
  total-volume measure instead of payment volume, so more fluent reasoning did
  not establish better grounding. Preserve the negative result. Matching SAS
  analysis is live, session 86455; no concurrent inference is launched.
- Added a close-prior warning from the published abstract of Haque et al. (2025),
  https://aclanthology.org/2025.knowledgenlp-1.17/: execution-trace-based program
  repair is established and not uniformly helpful. Full-method review is pending.

### First resident MAS pilot

- `mas-none-smoke-01` completed 4/4 cases inside the 6.40 GB cap, peak measured
  parent-plus-worker RSS 5,787,037,696 bytes. Correct complete answers: 1/4;
  delivered correct: 0/4; delivered incorrect: 0/4. This is a diagnostic sample.
- All extractor/drafter fact proposals matched in the four cases. The small
  verifier always emitted PASS with identity_name_mismatch in unsupported_fields.
  The gate correctly rejected contradictory verdicts. No generation was truncated;
  observed prompt lengths were 531–795 tokens, well below context 2048.
- Next intervention is grounded in these traces: constrain case IDs and citations
  to valid values for both arms; use per-field verifier judgments; test independent
  drafting rather than passing the extractor's proposed answer into the drafter.
  Record specialist disagreement for later ablation instead of assuming consensus
  is reliable. Broader experiments remain necessary.
- Implemented configurable joint/field verification, proposal/independent handoff,
  and free/enumerated citations so the combined intervention can later be ablated.
  The default pilot uses field checks and independent drafting. Every model stage
  now persists immediately, preserving partial-run evidence if a later stage fails.
  Thirty tests pass. These are implementation checks, not model-performance results.
- The next distinct-instance run breached the cap at 6,410,784,768 bytes before
  completing a case. A free-citation control also breached the cap before a case.
  This does not support blaming citation enumeration alone. Both runs are invalid
  and preserved, and cannot enter paired accuracy comparisons. The earlier fit
  was an observed sampled peak, not a guarantee of stable repeated-load fit.
- Optimize deployment by sharing the identical 0.5B checkpoint instance between
  extractor and verifier, which are called serially. Keep three agent roles and
  reset KV state before every call for both arms. Label shared versus distinct
  residency explicitly. Sharing weights is deployment engineering, not a novelty
  claim; role-specific fine-tuned weights would require separate instances.
- Shared resident pilot `mas-shared-independent-field-smoke-04` completed under
  peak RSS 5,144,936,448 bytes. Complete correct cases remain 1/4; correct delivered
  cases improved from 0/4 to 1/4, with no incorrect deliveries in either run. All
  four cases are the same, so no accuracy improvement is established. Inference
  tokens rose from 1,222 to 1,321. This combined intervention needs ablations and
  larger evaluation; it is not evidence of novelty.
- Next run tests transactional patch repair on the same four development cases.
  The 7B first shard has now passed the official SHA-256 check; second shard is
  downloading. The SAS arm will receive the same compact schemas and field checks.
- Patch pilot `mas-shared-patch-smoke-05`: 1/4 correct and correctly delivered,
  zero incorrect deliveries, zero repair gains or regressions, peak RSS
  5,145,071,616 bytes. Tokens increased to 1,709 from 1,321 without accuracy gain.
  Do not retain this intervention as an empirical improvement on these cases.
  Raw repair responses mostly repeat existing facts; investigate answer anchoring
  and stronger independent re-extraction as a known CoVe-style baseline.
- Both official 7B shards now pass SHA-256 verification. The first SAS four-case
  pilot is running serially after the MAS runs, with the same schema and verifier
  controls. Do not infer a final result from a partial case file.
- Public FinQA development data is supplemental; potential pretraining contamination
  is unknown. No claim of unseen financial-document validation is justified yet.
- SAS pilot `sas-field-smoke-01` completed: 3/4 correct, 2/4 correctly delivered,
  no incorrect deliveries, peak parent-plus-worker RSS 4,978,413,568 bytes, 707
  generated tokens. One correct missing-date answer was withheld because the
  verifier returned UNKNOWN for explicit absence. This is an observed false reject.
  The fourth case was incorrect; do not report the partial 3/3 as the final result.
- The same four-case SAS patch-repair run is now live (`sas-patch-smoke-02`).
  It uses the same repair and verification policy as MAS. Inspect completion and
  traces before selecting the next intervention. No publication conclusion follows
  from the exploratory 3/4 SAS versus 1/4 MAS comparison.
- Continuation inspected the live SAS repair process rather than restarting it.
  It completed: 3/4 correct, 2/4 correctly delivered, zero incorrect deliveries,
  no repair gains or regressions, 839 tokens versus 707 without repair. Peak RSS
  4,978,438,144 bytes. The current anchored patch policy improves neither arm on
  these four cases. Preserve this negative result and move beyond the rule-solvable
  KYC pilot instead of claiming success from extra engineering alone.
- Implemented a FinQA development adapter: cited arithmetic programs, bounded
  deterministic execution, source-visible operand/operation/unit checks, and
  localized program-step repair with recomputation of dependents. These are
  baselines/components; no new-method claim is established by implementation.
- Both FinQA arms use context 4096 provisionally (KYC diagnostics retain 2048),
  the same 2048 total generated-token ceiling, and the same measured 6.40 GB RSS
  ceiling. Memory fit must be verified by actual runs. Program and verification
  grammars compile under the installed runtime; 43 tests pass.
- FinQA gold audit was completed before numerical model inference on the fixed
  first-24 prefix. Percentage executable answers mix fraction and percentage-point
  conventions; two records disagree with their reported answers even after display
  rounding. Retain all 24. Primary diagnostic correctness uses reported-answer
  rounding and the model's declared unit; raw exe_ans tolerance 1e-5 is separate.
  Neither metric is FinQA's official program-equivalence score. Gold is never used
  to rescale deployment output or choose a repair.
- False-lock correctness is not assessed per FinQA program step: numerical gold
  does not uniquely identify a valid alternative reasoning program. Do not reuse
  the KYC field-lock metric as if it provided such ground truth.
- First real-report MAS smoke (fixed first two records) completed at peak RSS
  5,251,465,216 bytes: 0/2 correct, both delivered incorrectly, 309 generated tokens.
  All stages finished without truncation. Cited arithmetic was executable but
  semantically wrong; the 0.5B verifier returned PASS on both. Do not equate source
  support, successful execution, or a verifier PASS with correct financial reasoning.
- Matching first-two SAS real-report smoke is live. Wait for its actual completion
  before modifying the numerical pipeline or declaring a comparative result.
- Matching SAS smoke completed at peak RSS 5,118,742,528 bytes: 0/2 correct,
  both withheld, 209 tokens. It abstained on the first answerable packet; on the
  second it used a computed literal with STEP#0 instead of the required #0 value
  reference, so deterministic execution rejected it despite model verifier PASS.
  These are concrete encoding/verification failures, not evidence of a capacity floor.
- Next baseline ablation uses finite source-quantity references, question-only
  unit constraints, and optional removal of the weak source selector. Copying
  quantities is established numerical-QA practice. Keep literal mode available
  and do not call these baseline improvements a novel algorithm.
- Added explicit literal/reference, free/question-derived unit, and selector
  suggest/none switches. Reference mode generates atom IDs or prior-step IDs;
  code resolves their numeric values and source citations. It cannot invent a
  numeric literal, but can still select irrelevant quantities or wrong operations.
- Selector-disabled MAS is explicitly a draft/verify pair (two active roles),
  not a three-role team. The shared 0.5B instance still supplies verification.
  Record active roles in each case. Both arms retain identical preprocessing and
  token/memory ceilings. Fifty-two tests pass; reference grammar compiles.
- Corrected numeric extraction for decimals immediately before sentence-final
  punctuation. The prior boundary could drop such values. This is a parser fix,
  not a model reasoning gain; old results remain immutable with their code hashes.
- MAS source-reference smoke completed: 0/2 correct, both withheld, peak RSS
  5,252,325,376 bytes, 325 tokens. First plan contradicted its INSUFFICIENT decision
  with a nonempty program; second referenced #0 in step 0 and every subsequent
  step referenced itself. The checker rejected both despite model verifier PASS.
- The second reference prompt reached 3,303 tokens because the quantity catalog
  repeats source context. Neither run hit its output cap, but this is inefficient.
  Next controls should compact the catalog and enforce causal references in the
  generation grammar, not rely on tiny models learning protocol constraints.
  A matching SAS reference smoke is live before those controls are changed.
- Matching SAS reference smoke completed: 0/2 correct, both delivered incorrectly,
  peak RSS 5,122,637,824 bytes, 207 tokens. The first program divided total volume
  rather than payment volume by transaction count (129.4 instead of 127.4); this is
  a semantic metric-selection error despite valid source references.
- Added causal reference grammar and compact/full catalog controls. The grammar
  permits only earlier results, forces empty abstention, and requires each step
  to depend on source input or a prior grounded result. This restricts programs
  with constant-only auxiliary steps and must be disclosed. Semantic relevance
  is still unproven; syntax validity is not correctness. Fifty-four tests pass.
- Prepare training-only demonstrations as a strong baseline, with fixed selection
  and no development/test answers in prompts. Stop optimizing only the first two
  records after protocol smoke; expand to the declared 24-case development slice.
- Causal/compact smoke completed for both arms: MAS 0/2 correct (one abstention,
  one wrong delivery), SAS 0/2 correct (two abstentions). No future/self references
  remained in answered programs. The second prompt shrank from 3,303 to 1,318
  tokens. This is a protocol/input-cost improvement, not an accuracy improvement.
- Downloaded pinned FinQA training JSON (6,251 records) inside .local; retain its
  SHA-256 manifest and selected examples in Git. Choose first eligible single-step
  and multi-step examples from sorted training IDs, on distinct documents absent
  from ALL development records. Skip identity-only programs and inconsistent
  references. No development answers determine the demonstration targets.
- Initial selection found duplicate training questions/documents and a numeric
  constant that could be misbound to a calendar-day token. Before any demo-based
  inference, added document diversity and preserved explicit constants. Selected
  AAL/2014/page_89.pdf-2 and AAL/2014/page_92.pdf-1; audit logs retain selection rules.
- Demonstrations are included only when exact model-tokenizer counts leave 768
  tokens plus chat margin for generation. Record which examples fit each case.
  Next run evaluates the entire declared 24-case slice, including the two reference
  disagreements and incomplete retrieval cases. Fifty-six tests pass.
- A broader primary-source check identified FinMAN (EMNLP 2025) as a close prior
  baseline. It already stages formula planning, extraction, code execution and
  checking, and examines token/runtime scaling. Do not claim those as new. The
  published constrained-decoding literature also motivates prompt adaptation and
  demonstrations. RELATED_WORK_MATRIX.md records inspected scope and open gaps.
- Added an optional 128/256-token natural-language measure/formula analysis stage
  before structured programming. It shares the existing 2048-token ledger; the
  verifier does not see these preliminary notes. This is a reasoning baseline,
  not a novelty claim. Its default is zero, preserving the running common recipe.
  Fifty-seven tests pass; real model validation remains pending.
- Full 24-case MAS demonstration baseline completed: 1/24 correct under both
  reported-answer and raw-execution metrics; 1 correct delivery, 13 wrong deliveries,
  10 withheld. All 24 programs were source-supported and executable; no stage was
  truncated. Peak RSS 5,247,533,056 bytes, 2,710 output tokens total. This is a
  negative quality result despite successful protocol enforcement.
- Matching 24-case SAS baseline is live with analysis_tokens=0. Preserve the common
  recipe for comparison before applying the optional formula-analysis intervention.
- Independent audit confirms both selected demonstration pages AND annual-report
  groups are absent from all FinQA development records. This verifies the actual
  selected examples; broader pretraining contamination remains unknown.
- Added a MAS verifier-size ablation: reuse the already available 1.5B checkpoint
  instead of the weak 0.5B critic, with an explicit shared-instance label. When the
  selector is disabled, do not load an unused extractor. This homogeneous role-pair
  uses one checkpoint and separate reset calls; do not describe it as independently
  trained specialists. Default remains 0.5B and the live SAS run is unchanged.
  Fifty-nine tests pass; this profile still needs actual inference evaluation.
- A saved SAS program computed a useful intermediate and then bypassed it in the
  final step. Added gold-free dataflow diagnostics, value-preserving dead-step
  pruning for executable programs, and bounded single-edge reconnection candidates.
  Operations, quantities, units and all other edges stay fixed; KEEP remains an option.
- Offline candidate coverage uses gold only AFTER enumerating candidates and is
  labeled an oracle upper bound, never a model repair gain. MAS has three programs
  with unused steps but no correct reconnection candidate; a partial SAS snapshot
  has one candidate-recoverable error. This argues against treating orphan repair
  as a general solution for the weak MAS generator. A selector has not been tested.
- Snapshot readers ignore only an unfinished final JSONL record, not malformed
  completed records. Larger-verifier and formula-analysis inference still await
  the currently live SAS baseline; avoid concurrent inference contention.

- User authorized iterative code changes, 8 GB research and evaluation, milestone
  commits and pushes, and evidence retention. New files and artifacts stay inside
  this directory; this overrides the historical external-SSD storage convention.
- Preserve the historical runner and results. New code uses separate v2 modules.
- Current checkout has no GGUF weights, no llama-cpp runtime, and no old raw traces.
  Host reports 15.44 decimal GB RAM; 8 GB results here are simulated by a cap.
- Runtime bootstrap initially failed: system Python 3.14 lacks ensurepip. Install
  a project-local Python/runtime instead of changing the host installation.
- Targeted repair, claim verification, and budgeted audits already have prior art
  (Self-Refine, CRITIC, CLR, BRA-Audit). Candidate contribution is transactional
  evidence repair and measured repair-induced regression under tight resources;
  originality and effectiveness remain unproven.
- First milestone isolates deployment checks from gold labels. A supported span
  is not necessarily the correct field value. Missing status needs explicit absence
  evidence. Neither limitation will be hidden by a success metric.
- Credentials from .env are used only for Git authentication; never logged or committed.
- Milestone 1: eight contract tests passed; commit 5db7756 pushed to origin/main.
- Rule-only v1 development baseline scored 150/150 fully correct structured cases,
  including 20 mismatch-positive cases and 51 missing fields, using zero generated
  tokens. Deployment prediction was given neither labels nor calculator_inputs.
  The original scorer was used only after prediction. Per-case evidence and a
  SHA-256 summary are retained under research/tier8_v2/evidence/.
- Consequence: v1 is a regression/smoke suite, not sufficient evidence for a useful
  architecture contribution. Next data must include natural-language, multi-document
  evidence selection, temporal precedence, and conflicts. Retain a rule-only baseline
  and measure template/layout generalization; do not equate synthetic success with
  financial deployment readiness.
- Official pinned Qwen GGUF downloads are used for this reconstruction. Their F16
  files may differ in size from the earlier locally converted weights; hashes and
  actual fit must be recorded before claiming a reproduction of the old runtime.
- Milestone 2 (9bb1262) pushed. New development probes now separate source support
  from semantic correctness: a stale registry value passes lexical support but
  fails gold evaluation. Missing values cite explicit absence statements, rather
  than treating a null citation as proof of absence. This changes the v2 contract;
  the historical v1 scorer is unchanged.
- v2 pilot implements source-visible verifier calls, an actual delivery gate,
  constrained JSON, full/patch/no-repair ablations, and process-tree RSS sampling
  throughout load and generation. The nominal cap includes parent-monitor RSS.
  Patch repairs cannot edit unrelated fact entries. Semantic verification is still
  fallible: a supported-but-wrong claim can be locked, which must be measured.
- The first v2 pilot covers temporal KYC reconciliation only; credit expansion,
  role search, adaptive routing, full paired evaluations, new frozen confirmation,
  and full-paper novelty review remain required work.
- CPU wheel 0.3.19 installed but failed import because its shared object requires
  musl on this glibc host. Preserve install evidence; build 0.3.16 locally instead.
- Milestone 3 (70ec680) pushed. Review then found semantic source roles encoded in
  diagnostic document IDs; replace those with opaque randomized IDs before any
  model evaluation and regenerate the development manifest. No model results exist
  for the earlier probe version.
- Added paired analysis that rejects incomplete, memory-invalid, mismatched-data,
  duplicated-ID and unpaired runs. Sixteen tests now pass across contracts, data,
  delivery gates and paired statistics.
- Full method inspection of BRA-Audit Algorithm 1 confirms localized rollback and
  re-auditing are prior art. Do not claim novelty for those concepts. Keep testing
  field-level transactional preservation, false locks and repair regressions as a
  narrower hypothesis; the publication contribution remains unproven.
- Continued from verified progress: five commits were pushed in the previous goal
  turn. The source-runtime installation and model download processes remain live;
  source cache size and weight partial size have increased. Do not restart them
  solely because installation has not printed a progress line.
- Before pilot runs, enforce per-run weight SHA-256 checks (including both 7B
  shards), reject contradictory PASS verdicts, and reserve 192 output tokens for
  post-repair verification. These controls address evidence validity rather than
  implying a research finding.
- Record verifier confusion and wrong fields left locked, not just repair gains.
  Low repair regression alone is insufficient if the controller preserves incorrect
  fields. These metrics use gold only in the independent analysis after generation.
- Download only FinQA development data plus license/documentation from official
  repository commit 0f16e2867befa6840783e58be38c9efb9229d742. This is supplementary
  public financial-report validation, not a replacement for the KYC/credit scope.
  FinQA's test data remains unopened.
- Add a separately labeled 0.5B primitive diagnostic for runtime/token corruption
  checks. It cannot be counted as SAS-versus-MAS evidence.
- The generator-aware rule control solves all 24 temporal KYC probes. Treat them
  as regression tests, not evidence that an LLM is needed. Do not tune synthetic
  complexity merely to defeat a parser. Public-report tasks and broader independent
  sources are needed to establish practical value.
- FinQA first-24 development slice: non-oracle shared lexical retrieval includes
  all annotated evidence in 19/24 cases, and 34/41 annotated evidence units. Missing
  evidence is a measured retrieval limitation, not automatically a generation error.
- Official small-model GGUF files include larger embeddings than the earlier
  conversions. Prepare reproducible native-F16 conversion with F16 output and
  embedding tensors, preserving original hashes. Native F16 remains unquantized;
  actual resident fit and generation behavior must be measured after conversion.
- Runtime source build completed and imports: llama-cpp-python 0.3.16, numpy 2.5.4,
  psutil 7.2.2. The 0.5B primitive diagnostic passed 3/3 (arithmetic, name copying,
  explicit missing status) at measured peak RSS 1,437,417,472 bytes. This is not a
  full-task or architecture result and contradicts no broader capacity hypothesis.
- The proposed F16 conversion did NOT reduce either official file's size: 0.5B
  remains 1,266,425,696 bytes and 1.5B 3,560,416,288 bytes. The earlier suggestion
  that F32 embeddings caused the difference was an unverified assumption; it is
  not supported by this conversion. Measure resident MAS fit before further changes.
- The first 7B shard transfer ended after 703,227,414 of 3,993,201,344 bytes and
  was rejected. Retain rejected prefix metadata and original failure log. Added
  Content-Range-validated resume with final SHA-256 verification; retry is live.
- Added bounded cited-operand arithmetic for forthcoming public-report experiments.
  Deterministic execution is established FinQA methodology, not a novelty claim.
  Constants are explicitly whitelisted; final results must depend on source evidence.
  Numerical citation support still does not prove the correct financial interpretation.

**Study:** `tier8-8gb-v1`  
**SSD:** `H:\AGERE` (`AGERE_SSD_ROOT`)  
**Repo:** `D:\project-agere`  
**Date:** 18 October 2026

This file records choices and blockers for the overnight 8 GB run. It does not replace `DEVELOPMENT_START.md`. Where this file narrows the study, the narrowing is the 8 GB-only scope the user requested.

## Scope

- Only the 8 GB tier.
- SAS: `Qwen2.5-7B-Instruct` GGUF `Q4_K_M`.
- MAS: 1.5B F16 orchestrator/drafter, 0.5B F16 extractor, 0.5B F16 verifier.
- Resident loading is attempted first. If the combined weights do not fit the cap, the team is sequential load/unload and is labeled as such.
- Inference is CPU (`n_gpu_layers=0`). The GPU is only for QLoRA.
- Dev is 150 cases (100 KYC + 50 credit). The frozen test split is KYC 100 + credit 75 and is not opened until `frozen_systems.json` exists.
- Seed 42, temperature 0, one greedy run. Extra seeds would repeat the same outputs.
- FRAMES is a control after the headline, if time remains. MortarBench is not the headline.
- Headline metrics: invention rate (lower is better) and mismatch recall (higher is better), plus grounding and refusal. Scoring is `scripts/phase3.py` through `scripts/tier8_study.py`.
- A hardened change is kept only if dev invention falls or mismatch recall rises and the other does not collapse (`better()` in `scripts/tier8_study.py`).

## RAM cap

The cap is `min(6.4 GB, available RAM minus 1 GB safety)`. It is not raised to force a model to fit.

On 18 October 2026 the host had 16.39 GB total and about 6.7 GB available. The effective cap was about 5.68 GB. Loading `qwen2.5-7b-instruct-q4_k_m.gguf` crossed that cap in about 20 seconds. The runner stopped the process. No dev case was scored. ChatGPT, Spotify, and Cursor were left running.

A later measurement the same night showed 6.8 GB available, so the cap was 5.8 GB. One retry was run. At 6.85 GB available the cap was 5.85 GB. The 7B Q4 load reached 6.40 GB RSS and the runner stopped it. No dev case was scored.

The host was then measured at 7.60 GB available, so the cap was the full nominal ceiling of 6.40 GB. `qwen2.5-7b-instruct-q4_k_m.gguf` was loaded once at context 4096. The resident constructor crossed the cap. The runner then loaded that same single file once more under the sequential path, which is the same load for a one-model arm. That second constructor returned at **6.59 GB** RSS. The process stopped. Context 4096 was not loaded again. ChatGPT, Spotify, and Cursor were not closed. The cap was not raised.

The locked protocol lowers context when the scored workload does not fit. Both arms would have used the same context. With 7.72 GB available the cap stayed 6.40 GB. One load at context **2048** returned at **6,466,244,608 bytes (6.466 GB)**. With 7.85 GB available the cap stayed 6.40 GB. One load at context **1024** returned at **6,407,192,576 bytes (6.407 GB)**. Both are above the 6,400,000,000 byte cap. No lower context was tried. No dev case was scored.

The 1024-token load was 7,192,576 bytes over the cap. That is a compute-buffer fit adjustment, not a cap change. `Llama()` now uses `n_batch=64` and `n_ubatch=64` instead of `n_batch=256`. Context stays 1024. Contexts 4096 and 2048 were not retried. The cap stays 6,400,000,000 bytes. With 7.67 GB available, that one load returned at **6,406,934,528 bytes (6.407 GB)**, still 6,934,528 bytes over the cap. It was not loaded again.

## Packages

Installed into `D:\project-agere\.venv` on 18 October 2026:

- `torch==2.6.0+cu124` from `H:\AGERE\tmp\torch-2.6.0+cu124-cp312-cp312-win_amd64.whl`. CUDA is available on the RTX 4050.
- `transformers==5.20.1`, `peft==0.21.2`, `accelerate==1.15.0`, `bitsandbytes==0.50.2`.

QLoRA was not started. The order runs training only after the naive dev floor exists, and that floor does not exist.

## Naive development floor

Rerun with F16 KV, no flash attention, no memory map, context 2048, seed 42. Both arms stayed under the 6.40 GB cap. This replaces the discarded Q4-KV run.

| Arm | Valid JSON | Invention | Mismatch recall | Grounding | Refusal | Peak RSS |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| SAS 7B Q4 | 100% | 78.0% | 0% | 81.8% | 0% | 5.03 GB |
| MAS resident | 62% | 91.4% | 0% | 37.2% | 0% | 5.53 GB |

Invention is among complete claim sets. The team had 93 complete sets. Failure tags: SAS `S6` on 117 of 150; MAS `M2` 57, `M3` 85, `M7` 8. Neither arm flagged a name mismatch or refused a missing field. The untouched team is worse on invention, grounding, and valid JSON.

## Result

The naive floor above is the untouched comparison. The fine-tune, the hardened team, and the held-out test follow it.

The first QLoRA attempt loaded the 7B on the RTX 4050 and then failed before the first step: installed `transformers` 5.20 takes the 3% warmup as `warmup_steps=0.03`, not `warmup_ratio`. The locked ratio is unchanged. The retry uses that argument.

QLoRA then completed: 600 rows, 2 epochs, sequence length 512, train loss 0.2195, about 4.9 hours on the RTX 4050. The adapter is `H:\AGERE\weights\adapters\tier8-7b-qlora`. It is a PEFT adapter, not a GGUF LoRA, so it is not loaded onto the Q4 file. The scored SAS remains the base Q4_K_M with the staged prompt.

The hardened development run died after writing `CR-DEV-0032` (132 of 150 SAS cases). The process was gone and the case file had not been updated for about an hour. The runner resumes completed case ids, so that run was started again rather than repeated.

The resumed hardened dev run finished. It did not beat the untouched floor.

| Arm | Valid JSON | Invention | Mismatch recall | Grounding |
| :--- | ---: | ---: | ---: | ---: |
| Hardened SAS | 19.3% | 100% of 29 complete sets | 20% | 10.7% |
| Hardened MAS | 0% | none scored | 0% | 0% |

Hardened SAS tags: `S3` 121, `S6` 29. Hardened MAS tag: `M2` on all 150. Valid JSON collapsed, so both repairs are reverted. The frozen systems are the untouched 7B Q4 and the untouched team.

## Held-out test

Pooled Agere-KYC-Synth (100) and Agere-Credit-Synth (75). Seed 42, temperature 0, context 2048, F16 KV, no memory map. Both arms stayed under the 6.40 GB cap.

| Arm | Valid JSON | Invention | Mismatch recall | Grounding | Refusal | Peak RSS |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| SAS 7B Q4 | 100% | 71.4% | 0% | 84.4% | 0% | 5.03 GB |
| MAS resident | 63.4% | 80.2% | 0% | 36.3% | 0% | 5.54 GB |

Invention is lower-better, among complete claim sets. The team had 111 complete sets. SAS tags: `S6` on 125 of 175. MAS tags: `M2` 64, `M3` 89, `M7` 22. The single quantized model invented less and grounded more. Neither arm caught a planted name mismatch or refused a missing field.

FRAMES closed-book control, 100 questions: SAS exact match 1%, MAS exact match 2%. That small team edge does not override the KYC and credit invention result.

The 8 GB study is complete. The QLoRA adapter remains on disk and was not part of this scored comparison.

The 7B Q4 load does not fit the 6.40 GB cap at any locked context. Peaks, one load each:

| Context | Process RSS |
| --- | --- |
| 4096 | 6.59 GB (runner print, two decimal places) |
| 2048 | 6,466,244,608 bytes (6.466 GB) |
| 1024 | 6,407,192,576 bytes (6.407 GB) |

The cap is 6,400,000,000 bytes. These peaks are not scored runs.

One later load kept context 1024 and used `n_batch=64` and `n_ubatch=64`. Process RSS was **6,406,934,528 bytes (6.407 GB)**. That is still over the cap. It is not a scored run.

A fit measurement on the same night found the overrun was Windows counting a memory-mapped weight file on top of a private allocation. With `use_mmap=False` and context 2048, a long prompt stays near **4.92 GB** RSS. The three team models together stayed near **5.31 GB**. The cap was not raised.

Q4_0 KV cache plus flash attention also fit, at 4.83 GB, and a full 150-case naive run was completed under that setting. Every case was invalid JSON. A direct check showed the cause: `2+2` came back as `The023.` with Q4 KV and flash attention, and as `4` with the default F16 KV cache and flash attention off. The F16 setting used **4.92 GB** on a 1,601-token prompt. That 150-case run is not a result. It is stored aside as `dev_invalid_q4kv`. The rerun uses F16 KV, no flash attention, and no memory map.

## Policy corpus

Both hardened arms share the synthetic SOP at `H:\AGERE\datasets\policy\agere-policy-v1\sop.jsonl`. It is original project text. Official SBP wording is not invented. Naive runs still see policy retrieval as unavailable, matching the Phase 3 floor.

## QLoRA

The RTX 4050 has 6 GB of VRAM. The locked sequence length is 2048. If that step does not fit, training uses 512 tokens and the deviation is labeled. The SFT rows are short JSON tasks and are not truncated by 512 in any material way. Training reads only the finetune train and finetune-dev files. The test split is not used.

The scored SAS remains the Q4 GGUF under the RAM cap. A GGUF LoRA is applied only if conversion succeeds. Otherwise the frozen SAS is the base Q4 with the staged prompt, and the adapter status is written as such.

The torch wheel is `H:\AGERE\tmp\torch-2.6.0+cu124-cp312-cp312-win_amd64.whl` (download completed). If `bitsandbytes` fails on Windows, QLoRA is skipped and the comparison continues with the base Q4 file.

## Sequential team

If more than one model is resident and the combined weight files plus the measured 1.72 GB runtime overhead exceed the cap, the team is sequential load/unload and is labeled as such. That path was not reached. The single 7B Q4 model itself exceeded 6.40 GB.

## Runs that break the cap

A run whose peak RSS exceeds the cap is invalid. It is not averaged into the result.
