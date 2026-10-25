# 8 GB tier study decisions

## Continuation — 25 October 2026

### Larger-verifier trial is live under the declared cap

- Launched verifier3b-sequence-01 after its source/plan commits were pushed. Exec
  session 68919; controller PID 312283, monitor 312285, worker 312318, verified live.
  Four complete case records and peak sampled RSS 4,817,920,000 bytes were present
  at observation. This is a partial resource check, not a final fit/quality result.
- Seventy-three inputs remain frozen. The trial retains all 24 cases and the same
  trained drafter; no partial quality result has selected a condition. Evaluate
  draft identity and delivery changes only after complete terminal output.
- Beyond this trial, literal/program-format controls, stronger SAS adaptation,
  broader report-disjoint evaluation and an original useful mechanism remain open.
  Improvement over the all-abstaining matched control alone is not publication
  evidence. The present useful gain is from established supervised adaptation.

### Larger quantized verifier allocation control implemented

- Added an explicit 3B Q4 verifier choice, using the already hash-pinned candidate
  checkpoint. With the trained 3B drafter, the same base filename has different
  adapter policies, so two separate resident instances are required. This prevents
  the trained drafter adapter from silently contaminating the plain verifier.
- Tests check that equal base+adapter policies share only when requested, while
  distinct adapter identities remain distinct even under shared residency. An
  unadapted same-base shared pair is just a staged self-check control; do not call
  it independent specialist weights. The current trial uses distinct policies.
- All 168 tests pass. Actual pair RSS fit and verifier benefit remain unmeasured.
  The full 24-case trial keeps the adapted drafter, data, prompts, token ceiling,
  sampling and no-repair policy unchanged. Check initial plans for exact equality
  afterward; do not attribute differences solely to verification if drafts differ.
  Prefer a new gate only if it reduces wrong delivery without sacrificing correct
  delivery, while reporting its extra latency/memory. No benefit is assumed.

### First actual adapted QA gain, with a delivery-risk failure

- Both matched 24-case jobs completed. Unadapted 3B, no analysis/demos: 0 correct,
  24 abstentions/withheld. Same configuration with the applied trained adapter:
  11 reported matches, 9 raw execution matches, 10 correct deliveries, 11 wrong
  deliveries, 3 withheld; all 24 programs executable/source-supported, no abstentions
  or truncated stages. V2 ratio-unit sensitivity leaves totals at 0 and 11.
- Matched primary gain +11/24, paired bootstrap interval [.25, .6667], exploratory
  exact McNemar p=.0009766. This is reused development data and an untuned matched
  baseline that abstains everywhere; it does not establish novelty or generalization.
- Compared separately with the previous stronger 3B analysis/demos configuration:
  4 -> 11 reported matches (8 wins, 1 loss), but prompts, adaptation and accounting
  differ. That comparison is explicitly exploratory, not isolated training effect.
  Best SAS remains 13 correct with 5 wrong deliveries versus trained MAS 11 correct
  and 11 wrong deliveries. No architecture win or optimized-system claim.
- Adapted peak RSS 3,898,769,408 bytes under 6.40 GB; 2,276 generated tokens, 42,492
  actual prompt tokens and 404.66 inference seconds. Matched unadapted peak 3.821 GB.
  Source support/execution is not semantic correctness. The 0.5B verifier accepted
  11 wrong answers and rejected one correct answer; stronger verification is now
  an evidence-driven priority. Do not optimize only accepted-answer precision.
- Next baseline intervention: a 3B Q4 verifier for the same trained 3B drafter.
  Different adapter identity requires separate role instances; actual RSS fit must
  be measured. Keep generation prompts/caps/data fixed, then check whether initial
  plans stayed identical. Success requires fewer wrong deliveries without losing
  correct delivery; no gain is assumed before the full trial.

### Role-adapter prior checks during the live paired evaluation

- Read primary arXiv abstracts for LRAgent v2, MapCoder-Lite v2 and DAC v2.
  Shared-backbone role adapters, memory-efficient multi-agent serving, role-wise
  fine-tuning and learned abstention/credit controls already exist. Their abstracts
  constrain priority claims; full-method comparison/replication remains pending.
- A stronger learned critic or shared larger-backbone role policies may be useful
  baseline improvements under our RAM ceiling, but cannot be presented as novelty
  by themselves. Do not mistake the current 0.5B critic for an optimized verifier.
  The live matched drafter-adaptation ablation remains unchanged; finish it before
  selecting further conditions. No partial accuracy was used to tune the run.

### Frozen matched applied-adapter evaluation

- New 24-case sequence: unadapted 3B Q4 + native 0.5B critic first, then the same
  configuration with the verified full-training adapter on the drafter only.
  Original source packets, causal reference grammar, compact catalog, question-
  derived units, zero demos/analysis/repair, 4096 context, 2048 output tokens/case,
  seed 42, eight CPU threads and sampled 6.40 GB RSS ceiling are fixed in both.
- Both use the new usage-verified token counter; the historical 128-analysis MAS
  condition is a separate stronger-baseline control, not the matched training
  ablation. Report correct answers/deliveries, wrong deliveries, withheld cases,
  paired differences and actual resources; run the v2 unit sensitivity afterward.
- The trained checkpoint has not seen development labels as training targets. This
  slice has been repeatedly used for development and cannot establish independent
  confirmation. Complete both jobs and retain all 24 cases before selecting a next
  condition. No positive result or novelty is assumed from lower token loss.

### Actual adapter effect proved; measured inference integration

- Added strict runtime loading of full-training converted adapters. Fit-only,
  wrong-profile, changed-provenance and changed-file artifacts are rejected. MAS
  attaches the 3B adapter only to its drafter; its 0.5B critic remains unadapted.
  SAS support requires a 7B adapter. Sharing keys include adapter identity so a
  base and adapted role cannot accidentally share the same altered instance.
  Each case records backend-handle initialization and artifact identity.
- Real scale 0 -> 1 -> 0 CPU diagnostic passed on a fixed training-validation
  prompt: zero-repeat logprob drift exactly 0, maximum common-token logprob effect
  22.7471, peak parent+worker RSS 4,337,459,200 bytes under cap 6.40 GB. This proves
  application/effect only; it is not QA gain or full-MAS memory measurement.
- Two earlier diagnostic attempts failed on harness issues: logprobs requires
  logits_all=True in this runtime; NumPy float logprobs needed conversion before
  JSON serialization. Both failed outputs/logs remain immutable. The successful
  third diagnostic uses the same full 4096 context and monitored memory ceiling.
- Integrated the tested completion encoder into inference preflight and asserted
  agreement with actual engine prompt-token usage. Skipped calls record zero
  prefill cost plus a separate required-context count. Analyses identify historical
  manual estimates versus verified usage. Old logs/scores are unchanged; old
  replay guards intentionally require their original runtime behavior.
- Added concurrency guards and adapter/token-accounting tests. All 166 tests pass.
  Fresh unadapted and adapted runs will use identical new code, original 24 public
  packets, no demos/analysis/repair, 3B Q4 drafter and native 0.5B verifier. This
  matches the adaptation prompt configuration; comparison to the stronger 128-
  analysis baseline is separate. No architecture or novelty claim is implied.

### Full 3B adaptation and conversion completed

- Full train-only epoch completed: 661 examples, 83 optimizer updates, 504 changed
  adapter tensors, 14,966,784 trainable parameters. Wall time 1,198.25 seconds;
  peak allocated GPU memory 4,050,905,088 bytes, reserved 4,227,858,432 bytes.
- Final training loss 0.0321 and 100-example teacher-forced validation loss 0.0347
  are token losses, not QA accuracy or evidence of generalization. No primary
  development/confirmation questions were used as training targets.
- Runtime-paired conversion succeeded: 504 finite paired LoRA tensors, F16 GGUF
  59,902,144 bytes; full SHA256 and source/training identities recorded. Sequence 02
  completed terminally. No adapter has yet been applied by the measured CPU runner;
  no reasoning gain, architecture win or novelty is established.
- The next gate is actual application proof followed by matched fresh unadapted/
  adapted no-analysis inference under the sampled RSS/output caps. Compare against
  the best existing MAS analysis baseline separately. Historical scores and manual
  prompt-token counts remain preserved; new inference will use verified accounting.

## Redevelopment — 24 October 2026

### Real full-context fit succeeded; full training is active

- Sequence 02's real 3B fit completed at 16:55:27 UTC. Same longest 1,024-token
  training sequence, two optimizer updates, finite nonzero gradients, and 504 changed
  adapter tensors (14,966,784 trainable parameters). Peak allocated GPU memory
  3,946,031,616 bytes, peak reserved 4,225,761,280 bytes. The memory repair preserved
  full context/targets and succeeded where the original full-logit path failed.
- The two losses (0.9611 then 0.1665) are repeated-example fit diagnostics, not QA
  accuracy or generalization. No deployment adapter has been applied. Adapter
  files are retained locally with exact hashes; large adapter/GGUF binaries are
  ignored by Git, consistent with base weights. Source/config/summary/log proof
  remains versioned and pushed.
- The controller immediately started the separate one-epoch 661-example training
  job. Launch identities and plan SHA are recorded; exec session 73451. Keep all
  42 frozen inputs unchanged until it completes or fails. Conversion follows only
  if full training validates. Do not duplicate the live training job.

### Preserve the full training objective with supervised-suffix logits

- Verified the installed Qwen2 forward API supports logits_to_keep. The new helper
  keeps every input token and every supervised target token, computing LM-head
  logits only for the last prefix position plus the complete target. Labels include
  that last masked position so causal shifting still predicts the first target.
  No example length, target or context was shortened to make the fit pass.
- A real tiny random CPU Qwen software check gives identical loss (4.1940789223)
  and zero maximum gradient difference across all 15 parameter tensors, versus
  computing logits for the entire prompt. This is software validation, not a
  trained-model gain or a novelty result. The optimization is an existing HF API.
- Enabled the documented expandable-segment CUDA allocator policy in the new
  trainer process. Actual fit/memory success still requires a new real-model run.
  Failure of the first fit remains retained; no optimizer update succeeded there.
- Added a versioned sequence 02 with 42 freshly frozen inputs and new fit/train/
  conversion output directories. It uses exactly the same 761-row corpus/split,
  full 1,024-token longest-example diagnostic, rank, optimizer and update counts.
  Terminal CPU dependency evidence is reused; the failed sequence is not restarted.
- Separately prepared a correct completion-token encoder for future inference
  accounting. Four BOS/CLS/EOS/SEP tests and all 761 full sequences per tokenizer
  pass. It is not yet integrated into the runner. All 159 tests pass.
- Training annotation audit: 75/761 packets omit at least one annotated span and
  19/761 targets use a span outside the supplied annotation set. These are label
  consistency diagnostics, not proven semantic errors; alternative support may
  be valid. The frozen corpus was not changed or silently declared adjudicated.

### Completed SAS length ablation and first real GPU fit failure

- The CPU sequence completed at 16:50:03 UTC. SAS 256-token analysis: 11/24 reported
  matches, 7 raw matches, 11 correct deliveries, 9 wrong deliveries and 4 withheld;
  7,844 generated tokens, peak RSS 5,124,149,248 bytes. The 128-token baseline has
  13 matches/13 correct deliveries, 5 wrong deliveries and 6 withheld. Longer
  reasoning did not improve either system on this fixed development slice.
- The waiting adaptation controller verified the completed dependency and runtime,
  then ran the real longest-example fit (WRK/2018/page_39.pdf-5, 1,024 full tokens).
  CUDA ran out of memory before the first optimizer update, requesting 594 MiB
  with 325 MiB free. Failed fit summary/events and the stopped sequence are retained.
  Full training and conversion did not start. No fit success or trained adapter.
- The 59-input CPU freeze and 40-input training freeze have both ended terminally.
  Do not rerun the old journal/output. The next fit will use a new versioned run.
  Preserve complete input context/labels and reduce unnecessary LM-head logits
  using the existing HF logits_to_keep API, validating loss/gradient equivalence
  before applying it. This is a known memory optimization, not a novelty claim.

### Verified queued adaptation controller is live

- Started the frozen sequence after committing/pushing its source and plan. Exec
  session 92859, controller PID 188824. It verified CPU controller PID 159981 by
  creation time and command argument and is waiting for its terminal completion.
  No training has started. Launch identity and plan SHA are saved separately.
- Rechecked both freezes: 59 CPU-study inputs and 40 adaptation inputs remain
  intact. The SAS worker is live; its partial case count is not used to select
  conditions. Do not restart either controller because an observation times out.

### Runtime complete; frozen real adaptation sequence queued

- Torch 2.6.0+cu124, PEFT 0.17.1, Accelerate 1.10.1 and bitsandbytes 0.48.1 import
  successfully in the isolated environment; all package versions are recorded.
  CUDA/BF16 is available. Torch reports 6,053,232,640 addressable device bytes;
  do not substitute the larger NVML nominal figure for actual training headroom.
  No model was loaded by these import/capability probes. An initial dependency
  import used default /tmp compiler scratch; trainer/converter execution explicitly
  roots TMPDIR and cache paths inside the repository for subsequent model work.
- The complete 3B NF4 base is verified: 2,054,625,552 bytes, SHA256 recorded in its
  manifest. Training/deployment architecture dimensions and RoPE settings agree;
  weight equivalence across NF4 and Q4_K_M is not claimed. The 7B base is not fetched.
- Repeated HF/GGUF token, prefix-mask and length parity after the GPU dependency
  installation; all 761 examples still pass for both profiles (parity revision 02).
  The trainer now requires this proof and verifies architecture before loading.
- Fetched 22 converter/GGUF Python sources at llama.cpp commit 4227c9be..., the
  submodule recorded by llama-cpp-python v0.3.16. Every Git blob/SHA256 validates.
  A large recursive tree request failed with IncompleteRead; the successful fetch
  uses small root/subtree requests. Both attempt logs remain. Converter --help
  succeeds in the training environment. Sources support Qwen PEFT adapters and
  the installed inference API exposes lora_path/lora_scale; application is untested.
- Added conversion validation for completed changed adapters, exact file hashes,
  compatible architecture, pinned converter files, LoRA metadata and finite paired
  matrices. Diagnostic fit adapters retain their diagnostic label. No actual
  conversion or applied-adapter inference has occurred. All 153 tests pass.
- Froze 40 training/data/runtime/converter inputs for adaptation-sequence-01.json.
  It waits on the identified CPU controller (PID plus creation time and command),
  requires complete SAS/journal evidence, verifies package versions, then performs
  fit -> full one-epoch training -> conversion. A failed fit or changed input stops
  the sequence without retries. Initialized adapters cannot satisfy its gate.
  This prevents idle handoffs while keeping training outside the CPU timing run.
- The sequence is baseline optimization, not novelty. Correct delivered reasoning,
  regressions, resource use and real adapter application still require evaluation.

### Temporary 1.5B cache reclamation and 3B base transfer

- CUDA packages need more disk than the tokenizer-only environment. Also removed
  the unused native 1.5B F16 cache after verifying its full SHA256 and ensuring all
  active inference is SAS. Reclaimed 3,560,416,288 bytes; retained the native 0.5B
  verifier and both Q4 inference profiles. This changes cache availability only;
  prior runs/metrics are preserved. Future 1.5B use must restore its pinned source
  and reproduce the recorded native conversion before claiming that profile ready.
- Source/native hashes and complete conversion/recovery provenance are retained in
  reclaimed-native-cache-02.json. Every one of the 59 frozen inputs still matches.
  SAS does not use the removed file. Disk headroom now supports the separate CUDA
  environment and a streamed 3B NF4 base transfer, which has been started. Verify
  its full size/LFS SHA before any fit; a partial transfer is not a usable model.
- Torch installer remains live. No training is running; successful installation,
  base verification, real two-update fit, full training, adapter conversion and
  measured applied-adapter reasoning remain separate required steps.

### Implemented guarded QLoRA fit/training path (execution pending)

- Added a pinned prequantized training-base fetcher with config/blob checks,
  resumable weight transfer, LFS SHA/size verification and a disk-headroom guard.
  The 3B metadata/config snapshot is prepared; its weights are not yet downloaded.
  Training NF4 and deployment GGUF Q4_K_M are explicitly distinct quantizations.
- Added a separate adapter trainer consuming exactly the HF/GGUF-parity-checked
  no-analysis deployment tokens. User/prompt tokens are masked; complete assistant
  targets are preserved. The frozen 661/100 train/validation split is checked.
  Base/config/data identities are verified before loading; only LoRA parameters
  may be trainable. The 7B path exists but GPU fit is not assumed or measured.
- First execution is a two-update fit diagnostic on the longest training sequence,
  exercising real forward/backward, nonzero finite gradients, optimizer-state
  memory and changed adapter tensors. It does not count as trained-system quality.
  Full baseline training is one epoch, batch-one accumulation eight, rank 8,
  alpha 16, dropout .05, all linear projections, AdamW lr 2e-4, clipping 1.0.
  This is an initial resource-feasible baseline, not an optimality claim.
- Training records loading/update events, losses, GPU allocated/reserved peaks,
  sampled host RSS, adapter file hashes and train-only validation teacher-forced
  loss. Peak tracking begins before model loading. Training resource measurements
  are separate from the simulated 8 GB deployment RSS ceiling. Applied GGUF adapter
  inference and actual task gains remain required; neither is inferred from loss.
- The live-process guard was exercised against the actual SAS monitor and refused
  before creating an output directory or importing/loading Torch. It also requires
  the CPU sequence's complete journal and valid SAS summary before model work.
  CUDA installation is ongoing; no real fit/training step has run. All 151 tests
  pass, including exact label masking and tokenizer mismatch rejection. Frozen
  inference code/data remain unchanged.

### Reclaimed reproducible model-download caches for adaptation

- SHA256-verified both original 0.5B/1.5B public FP16 GGUF downloads and their native
  runtime conversions, then removed only the redundant originals. Reclaimed
  4,826,841,984 bytes; free disk became 6,839,160,832 bytes. Native 0.5B/1.5B runtime
  weights, 3B/7B inference weights, datasets, logs and manifests remain present.
  Removed download files can be restored at their pinned repository revisions and
  hashes; conversion provenance is retained. No user-authored content was removed.
- All 59 frozen input hashes still match. SAS remains active and uses its retained
  7B shards. The source-download filenames in historical manifests are provenance,
  not a claim that those redundant cached originals are still on disk.
- Preparing Torch 2.6.0 from the official CUDA 12.4 wheel index in .venv-training,
  following PyTorch's documented previous-version installation. No actual model
  load/backward training is permitted until serial CPU inference is complete.
  Dependency installation/offline preparation may add host load; current latency
  measurements are exploratory, not a pristine isolated performance experiment.

### Official HF tokenizer parity verified before adaptation

- Created .venv-training independently; the research .venv and all frozen inference
  source/data inputs are untouched. Pinned Transformers 4.57.1 (known Qwen2.5
  integration) and Tokenizers 0.22.2; the complete resolved tokenizer environment
  is recorded. This deliberately avoids changing the active inference runtime.
- Downloaded only tokenizer/config assets from official Qwen 3B and 7B repositories
  at explicit commit SHAs. Verified file sizes and Git-blob or LFS hashes, then
  recorded local SHA256s. HF caches are inside the repository; parity uses local
  assets with remote code and online fallback disabled. No model weights fetched.
- HF AutoTokenizer matches every full deployment sequence, prompt prefix mask and
  length in all 761 retained rows for both profiles. This clears the tokenizer
  prerequisite only; no training, adapter application or reasoning gain occurred.
- Reviewed official Transformers 4.57.1 bitsandbytes and PEFT quantization guidance.
  QLoRA is an established baseline technique. Prequantized Unsloth snapshots are
  available (3B 2,054,625,552 bytes; 7B 5,547,254,622 bytes). Using them would change
  the training quantization from deployment GGUF Q4_K_M and must be labelled; no
  equivalence to the original FP16 training checkpoint is asserted.
- Host has an RTX 4050 with 6,141 MiB VRAM; GPU fit/backward-step feasibility remains
  untested. About 2.2 GB disk free is insufficient for a GPU stack plus base weights.
  Next reclaim only redundant public-download FP16 caches after checking their
  pinned hashes; retain native inference files and provenance. Actual training
  must wait until the active serial CPU inference sequence finishes.

### MAS 3B longer-analysis ablation completed

- The 256-token analysis run completed all 24 fixed development cases under peak
  sampled RSS 3,827,347,456 bytes (cap 6.40 GB). Four reported matches and four raw
  execution matches; 3 correct deliveries, 10 wrong deliveries, 11 withheld. Total
  generated tokens 7,653; recorded inference time 1,154.55 seconds. Prompt-token
  counts remain the frozen legacy manual estimates described below.
- Matched 128-token baseline: four reported matches, two raw matches, 3 correct
  deliveries, 1 wrong delivery, 20 withheld, 4,778 generated tokens. Primary paired
  comparison has one win and one loss (net zero, exploratory McNemar p=1). The
  separate v2 ratio-unit audit leaves both totals unchanged at four. More reasoning
  increases answered coverage without increasing correct delivery on this slice.
- No extra budget expansion is justified for MAS by this result. The original
  128-token condition remains preferable on these observed delivery/cost measures;
  neither is a broadly optimized or confirmed system. Verifier mistakes and actual
  model adaptation remain open; do not present more model calls as progress alone.
- SAS 256-token analysis started serially at 16:00:38 UTC. Sequence session 61231
  and its 59-input freeze remain active. Only the completed MAS run and its own
  log/paired audits are committed now; the live sequence journal remains open.

### Correct persisted adaptation identities and capture deployment SFT prompts

- Found and corrected our adaptation serialization bug before any model training:
  revision 01 sorted nested evidence keys after assigning A-IDs. Reloaded source
  IDs disagreed in 1,607/1,653 training and 192/198 validation examples. The earlier
  hash/split checks did not validate this property and were insufficient. Revision
  01 remains immutable historical evidence and is explicitly superseded; do not
  train on it. Its affected IDs/hashes are retained in a supersession audit.
- Revision 02 canonicalizes evidence order before generating labels, then reloads
  and checks every persisted catalog, target execution and cell binding. Counts
  remain 1,653 train / 198 validation. Added a serialization regression test. An
  additional audit reconstructs all 620 existing demonstration strings exactly;
  those strings preserve their ordering and the live inference inputs are unchanged.
- Added draft-prompt capture by stopping the actual deployment pipeline at its
  program call; no model output or invented verifier label is produced. Captured
  reference/compact/question-unit/causal prompts have no analysis or demonstrations.
  Both arms produce identical prompt text/schema. Cell metadata remains in the
  structured corpus, not in this existing deployment prompt. Evaluate this trained
  no-analysis configuration separately from the stronger analysis baselines.
- Inspected local llama-cpp-python completion source: generation recognizes chat
  special tokens, but our existing manual prompt counter does not. The live runner
  is frozen and its recorded counts remain historical manual estimates. New SFT
  encoding matches actual generation (special=True, no auto BOS/EOS; runtime flags
  checked). On all retained prompts both 3B/7B tokenizers show 21 fewer tokens than
  the manual counter. Correct runtime accounting after the frozen sequence ends;
  do not silently overwrite previous logs or use prompt counts as exact compute.
- Vocab-only tokenization makes zero generation calls. At 1,024 training tokens,
  761 examples fit both pinned tokenizers (661 train / 100 validation); 1,090 are
  excluded rather than truncated. Whole-sequence token hashes agree across both
  tokenizers. Prefix-mask boundaries, source identities, exact prompts, split
  isolation and saved hashes validate. This biases training toward shorter inputs.
- Early uncommitted prompt-export prototypes were superseded after special-token
  and source-order checks; their local artifacts/logs are preserved and never used
  for training. A policy check also initially rejected a harmless unused CLS token;
  the corrected check follows completion's actual BOS/EOS behavior. Final export
  requires HF tokenizer parity before training. Full suite: 148 tests pass.

### Train-only adaptation corpus with explicit binding quarantine

- Added a structured-data exporter over all 6,251 pinned FinQA training records,
  replacing the demo bank's 1,800-character cap with no character-length selection.
  It excludes the 2,511 training records whose annual-report groups appear anywhere
  in development, using the existing bank's group-exclusion metadata only.
- Eligibility requires the existing checked <=4-operation arithmetic/unit target,
  a unique numeric-to-source assignment from the strict partial compiler, target
  units admitted by current question grammar, and successful cell-level execution.
  Final targets never choose the first of multiple numerically compatible cells.
  Numeric uniqueness does not independently adjudicate the intended semantics.
- Exported 1,851 examples: 1,653 train across 422 report groups and 198 validation
  across 50 groups. Split is fixed by SHA256('agere-adapt-42:' + report-group) modulo
  10; groups cannot cross the split. No development answers/programs or test split
  enter this construction. Full materialized hash/group/count checks pass.
- Quarantined 559 ambiguous-binding examples and 46 target-unit/grammar conflicts;
  all other rejection counts and IDs are retained. Existing source/parser and
  reported/execution disagreements remain explicit rejections, not corrected data.
  This eligibility biases the corpus and is not a new benchmark or semantic gold.
- Output is structured data, not deployment-prompt-fitted SFT messages. Tokenizer
  fitting, cell-aware deployment integration, training in a separate environment,
  actual adapter application and both-arm evaluation remain undone. Training and
  synthetic/formula-derived labels are established methods, not a novelty claim.
- Full suite now passes 143 tests. The 59 live frozen inputs remain unchanged;
  MAS 256-token analysis continues, followed serially by SAS. CPU model training
  must not overlap the timing study. Source/data/code hashes and validation logs
  are retained; original demo banks and experiment outputs are unchanged.

### Preserve table-cell identity through source compilation

- Added evidence_cells.py as an independent, unused-by-live-runs module. It
  preserves every legacy A-ID, quantity value and ordering, validates that selected
  flattened rows exactly match the provided source table, and attaches row/column,
  measure label, column label and within-cell occurrence metadata. Unselected rows
  are not exposed. Ambiguous flattening is rejected. No QA fields are accepted.
- compile_cells copies source values into cell-specific citations and records each
  binding. Distinct equal-valued columns no longer collapse into one row citation
  in the execution trace. Narrative quantities still have span-level identity;
  this does not prove question relevance, intended period or formula correctness.
  The legacy parser already excludes column-header years from copied cell values;
  this change should not be described as fixing header-year extraction.
- Real-data audit: 5/24 original packets have 12 within-row equal-value collision
  groups; table-complete packets have 7/24 with 14 groups. These are representational
  ambiguities, not counted errors. Across four completed development runs, all 67
  executable reference plans retain their numeric values with cell-level support.
  All 620 training targets remain executable; 71 training packets have same-row
  equal-value collisions. No target was semantically adjudicated or replaced.
- Six new tests cover equal-valued column identity, unchanged values/IDs including
  negatives and narrative values, unselected-row isolation, source-table mismatch,
  ambiguous flattening and invented references. Full suite: 139 tests pass.
- Evidence and source/code hashes are retained in source-cell-identity-audit.json.
  None of the 59 frozen inputs changed; live MAS/SAS ablations remain isolated.
  Cell identity is a known grounding technique and an implementation foundation,
  not a novelty or measured accuracy claim. Deployment integration and matched
  metadata/control experiments remain pending after the frozen sequence ends.

### Running length ablation and closer semantic-verification prior

- Frozen 59 inputs for data/analysis256-sequence-01.json; controller exec session
  61231, PID 159981. MAS 3B 256-token analysis started and persisted its first case;
  SAS follows serially. No competing inference or changes to frozen scripts/data.
- Read VeriFin's method and relevant setup from arXiv:2608.10213v1. It binds XBRL
  facts and externally authorized formulas independently, then supplies symbolic
  constraint feedback for financial repair. This is close prior work; our span
  membership/algebra checks are not equivalent semantic guarantees. No replication.
- Encore's ACL 2024 abstract establishes formula-derived training reasoning and
  synthetic pretraining as prior work; full method review remains pending.
- Added a concrete post-pilot implementation order: representation control,
  structured source identity, ambiguity-aware training targets and verified adapter
  application for both arms, then matched binding repair if useful headroom exists.
  These remain proposals, not implemented methods or demonstrated novelty. Do not
  keep expanding a zero-gain proof trigger merely because the checker is exact.

### Versioned scoring sensitivity audit and reasoning-length experiment

- Confirmed a scorer/prompt mismatch: `number` is permitted for ratios, and the
  JPM ratio question's grammar forces it, but the legacy scorer rejects that label
  against a percent-bearing reference. A synthetic scoring-only counterexample
  reproduces this; it is not a model success or corrected experimental answer.
- Added a separate offline reported-units-v2-number-ratio evaluator. It treats
  number/fraction as canonical and scales only explicit percent. No prediction is
  rescaled according to gold magnitude. It revalidates completed cohorts, source
  hashes, executions and legacy scores, then writes separate sensitivity results.
  Historical artifacts, deployment prompts and inference scoring remain unchanged.
- The six completed analysis/replay runs have no changed case outcomes under v2.
  AAPL's bare .2 gross-margin reference remains an unresolved percentage-point
  annotation; no hand-written per-case scoring exception was introduced. Report
  legacy and v2 sensitivity together until reference conventions are adjudicated.
- All 133 tests pass. With every 128-token analysis stage truncated, the next
  matched development intervention is 256-token formula analysis, first MAS 3B Q4
  with its 0.5B verifier and then SAS 7B Q4. Use the same original public packets,
  fixed two training demonstrations, 24 cases, 2048 total generated tokens/case
  and sampled 6.40 GB RSS ceiling. Longer analysis consumes that shared budget.
  Compare each against its own completed 128-token condition; this is baseline
  tuning, not a new method or a pure architecture/precision ablation.
- No further expansion of proof-feedback repair is justified by its zero observed
  correction advantage. Source binding, training-target ambiguity and actual
  train-only model adaptation remain higher-priority mechanism work; their useful
  novelty is still unestablished. Do not call either arm optimized yet.

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


## 2026-10-25 — SSD external evaluation authorization and baseline queue

The user requested real evaluations and explicitly identified
`/run/media/mutasim/Data/AGERE` as the documented dataset/model location.
This supersedes the redevelopment repo-only storage assumption for these assets.
Code/envs stay local; new packets, traces, labels, predictions, logs and reports
stay on the SSD. Do not copy MortarBench customer-like fields into git.

The larger 3B critic completed all 24 FinQA development cases, preserved 11
correct drafts but withheld every answer (0 correct and 0 incorrect deliveries),
peak tree RSS 4.821 GB. Coverage collapse is a negative result.

Freeze an external exploratory baseline before further tuning: all 90 prepared
MortarBench questions and documented FRAMES100, SAS7BQ4 versus resident distinct
MAS1.5B F16 + two 0.5B F16 instances. Verify source data against committed
manifests/test.sha256 and models against SSD phase2 SHA256 manifest.
Use identical public evidence packets per arm, label-blind lexical retrieval,
4096 context, CPU8 threads, greedy seed42, 2048 total generated-token ceiling,
and fixed common cap min(6.4GB, availableRAM minus1GB). Sample parent+worker
RSS every0.2seconds and fail closed on breach/incomplete output.
MortarBench typed exact is a local exploratory metric; partial source retrieval
and absence of paystub/PDF extraction limit interpretation. FRAMES remains a
closed-book control. Original adapters are not silently applied.
The new runner does not establish adapted-system performance or novelty.

External queue is confirmed in actual inference, not merely planned: 3 MortarBench SAS cases persisted at this observation; sampled peak 5.18 GB under 6.4 GB. Run root: `/run/media/mutasim/Data/AGERE/runs/tier8_external/external_baselines_20261025_01`. Controller321561 / session46979. Full queue remains active; do not restart or edit the frozen runner. Launch pointer: evidence/external-evaluation-launch-01.json.

## 2026-10-25 — Supervisor progress audit and interrupted external queue

Read actual raw outputs/process inventory before reporting status: 26 MortarBench
SAS cases persisted (14 local exact matches), zero completed arms, no live
controller/worker and no terminal summary. Root cause unknown. Backed up the stale
SSD manifest and marked it interrupted with a separate observation; preserved
all cases/logs. No silent restart or fabricated completion. External inference
is currently stopped; previous ETA no longer represents a running queue.
Supervisor update records real SAS prompting and MAS adaptation gains, negative
critic/repair results, unequal best-system tuning, development reuse, and absence
of demonstrated useful novelty. No claim that any implemented mechanism is first.

## 2026-10-25 — Resume external evaluation without regenerating evidence

The previous goal turn is progress: it established stopped-process evidence and
corrected an inaccurate live status. There is no user-input blocker. Recovery
uses a separate wrapper and separate SSD segment, calling the original generation
worker unchanged. Its source SHA and prompt-token implementation SHA must match
the interrupted run. Frozen model/data hashes are rechecked. Existing case IDs
must be an exact prefix; labels/scores, final responses, role sequence and token
ledger must reproduce. Partial JSON tails are refused without rewriting them.
All 26 original cases passed these checks. Full suite:175 tests passed.

The new controller preserves the original cap and original peak RSS, records new
memory samples separately, rejects concurrent workloads and overwrites, and stops
on any failed arm. A detached process session is used so launch does not depend on
keeping an interactive tool session open. This improves lifecycle robustness;
the original interruption's root cause remains unknown. Recovering infrastructure
is not a novel research method. No generation prompt, retrieval, scoring, adapter,
model or token allocation is changed. Raw outputs remain on the authorized SSD.

## 2026-10-25 — Matched critic diagnosis and resource refusal

Recovery launch563f259 was refused before model loading: available RAM was about
6.7GB, below the unchanged6.4GB cap plus1GB reserve (later6.49GB). No controller
remains alive and no continuation case was generated. Preserve this failure log
and launch metadata; do not report the recovery as live. Do not close user apps.
Asked the user to free about1GB while independent work continues.

Boot-time evidence shows this host booted at06:41:45UTC, after the last original
sample06:38:33UTC. That reboot explains why old PIDs cannot still be live; it does
not establish whether the initial termination was a crash, shutdown or other cause.

A new offline audit proves all24 draft plans AND verifier prompts identical across
0.5B and3B critic trials. Weak critic:21 unanimousPASS,3 unanimousUNKNOWN;10 true
accepts,11 false accepts under the existing numerical answer metric. Larger critic:
23 operandFAIL,1 operandUNKNOWN;23 operationFAIL;0 accepts,11 false rejects.
All24 larger-critic outputs request repairNONE despite nonPASS checks, contrary
to their prompt. This is observed protocol/calibration failure, not proof of a
model-size effect or incorrect semantic judgment in every rejected case. No raw
verdicts or scores changed. Use a balanced, train-only program-discrimination
validation before treating another critic as strong. This is a local diagnostic,
not a novel method. Script/input hashes are in matched-critic-behavior-audit-01.json.

## 2026-10-25 — Train-only critic protocol-discrimination experiment

External recovery still cannot retain its original cap+reserve with available
RAM6.32GB, so no new full-arm trial is claimed. Independent single-critic
inference is feasible: use fixed min(6.4GB, available minus1GB) tree RSS ceiling,
load only one critic at a time and stop on cap/reserve breach. This is a component
diagnostic, not an 8GB SAS/MAS comparison. User's memory question remains pending.

Construct12 distinct report-group examples from the existing training-validation
corpus. Require annotated target correctness under BOTH existing numerical metrics.
For each, select the first deterministic single-operation mutation that retains
source operands and valid execution but fails BOTH metrics. Equal positives and
negatives; no inference-dependent selection. Source binding is numerically unique,
not independent semantic adjudication. Counterfactuals are controlled probes,
not naturally occurring draft errors or publication confirmation. Labels stay
separate from public inputs and are not read by workers.

Compare original rich review schema/instruction to binary PASS/FAIL/UNKNOWN review
on identical question/evidence/candidate/execution. Original rich instruction is
AST-checked against deployed code. This changes output protocol AND instructions;
do not attribute any effect solely to JSON grammar. Two profiles run serially:
original native0.5B F16 and3B Q4, no adapters, context4096, greedy seed42,8threads,
192 tokens/protocol (384 total/program). Use the existing Models.call prompt and
verified runtime token accounting. Save all raw prompts/responses/timing/memory
on SSD. Copy legacy pinned model binaries to SSD with exact byte/hash verification;
no weights are changed. Freeze sources and labels before model evaluation.

Full suite182 tests passed. This experiment assesses critic discrimination and
protocol sensitivity; it is not a novel algorithm or an adaptation gain.

## 2026-10-25 — Prior-art check while critic experiment runs

Read primary abstracts for CCL2024 judge calibration/contrastive negatives,
EACL2026 code-judge biases, and arXiv2607.05552 balanced wording/order/label controls.
Links/scopes are in RELATED_WORK_MATRIX.md. These constrain the next step:
critic calibration, curated negatives and label remapping are not automatically
novel. The current probe is necessary baseline strengthening, not the goal's
original contribution. A useful system-level mechanism still needs evidence.

## 2026-10-25 — Probe execution and uncertainty analysis

Actual single-critic experiment launched detachedPID23678, sourceb6243fa. Both
pinned model copies are verified on SSD, public/label data frozen before generation.
0.5B completed48 calls at1.472GB;3B confirmed live with33 saved reviews at latest
observation. 0.5B binary protocol accepts11/12 positives but also11/12 negatives;
do not mistake improved reference acceptance for discrimination. Original rich
format accepted6 positives and7 negatives. No full external queue restart occurred.

Added offline analysis that refuses incomplete/duplicate case-protocol grids,
reports complete pair separation versus both-accept/both-reject behavior, and
bootstraps report groups rather than treating paired mutations as independent.
UNKNOWN/unparsed are nonaccepts for delivery-gate metrics, not evidence of an
explicit correct negative judgment. Only12 groups; this is exploratory. Current
mutation-order recipe yields9 substitutions to add and3 to subtract; no broad
operator-robustness claim. Full suite184 tests passed. Analysis code does not
change the running worker or any frozen input.

## 2026-10-25 — Completed critic protocol probe: no pair discrimination

All96 actual model calls completed,48/profile. Full source/data hashes, labels,
responses, timings and memory remain on SSD. Peaks:0.5B1.472GB;3B2.376GB, both
below fixed5.453GB component cap. Analysis02 preserves explicit verdict histograms;
analysis01 remains on SSD as an earlier aggregate, not overwritten.

Neither critic/protocol separates the reference from the incorrect mutation on
ANY of12 report pairs.0.5B rich accepts6 references/7 mutations; binary11/11.
3B rich returnsFAIL24/24; binaryUNKNOWN24/24. UNKNOWN is not an explicit negative
judgment; its nonacceptance cannot demonstrate semantic competence. Gate accuracy
45.8/50/50/50percent reflects mostly acceptance bias, not useful paired reasoning.
No degenerate bootstrap interval is interpreted as equivalence. Source selection
is limited to reference-agreeing train-validation annotations and controlled
operator substitutions; no external/natural-error accuracy gain is established.

Decision: stop treating simpler review instructions as a sufficient verifier fix.
The next strong controls should establish role-specific program discrimination
(training labels from actual annotations, without invented per-field semantic
claims) and/or independent solving before a delivery gate is trusted. Compare
against known approaches; calibration/negative training/independent verification
are prior art. Original repair contribution and publication novelty remain unproven.

Full external recovery remains stopped. After the component run available RAM
briefly approached7.38GB, then7.27GB, below its7.4GB preflight; do not restart or
lower the frozen original cap to bypass that condition. All184 tests pass.

## 2026-10-25 — Weakly annotated role-verifier corpus

Last turn is progress:96 actual reviews disproved the simpler-format fix on the
controlled probe. Full recovery still lacks original7.4GB headroom (7.336GB at
this turn's checks), but verifier baseline development is independent work.

Prepare training and train-validation pairs from revision02 source-binding data,
retaining existing report-group separation and excluded development groups. Both
numerical metrics must accept a source-annotated reference and reject its single
operation/source-operand mutation; compilation/execution/source support must pass
for both. These are weak numerical annotation labels, not invented field-level
semantic explanations or independently adjudicated semantic truth. Binary target
PASS/FAIL only, original deployed binary critic prompt. Hash-select mutation family
before selecting one eligible edit so operand candidate count does not determine
family frequency. No test data or inference-dependent example selection.

Retain a pair only if both complete prompt/target sequences fit1024; never truncate
or keep one class alone. Save all rows/token-ID hashes/metadata on SSD; verify
actual HF/GGUF parity before training. Fit/train and applied-adapter evaluation
remain separate gates. Controlled-negative training is established baseline work,
not a new method; natural-error testing and comparable SAS adaptation remain needed.
187 tests pass before corpus preparation.

## 2026-10-25 — Mixed catalog build failure retained and fixed

critic_binary_sft_01 build failed with KeyError cell_role: text-quantity catalog
entries do not carry table cell metadata. No trained model or valid dataset is
claimed from that run. Its directory/log are preserved on SSD. Use explicit
get(cell_role)==data for operand-substitution pools; text-only examples may still
supply operation mutations. Added a regression fixture for mixed catalogs.
Start a new corpus ID02 rather than overwriting failed evidence.

## 2026-10-25 — Explicit role training and authorized SSD artifacts

Extend existing QLoRA trainer with explicit purpose/dataset/parity manifests while
preserving legacy drafter defaults and661/100 split requirements. Critic mode is
supported only for3B with explicit manifests, verified matching dataset purpose,
full token-ID parity and declared split counts. Fit remains2 actual optimizer
updates on the longest fitting train sequence; training remains one epoch with
existing optimizer/memory/logit-window policy. Training loss is not QA evidence.

Training/conversion artifacts may resolve only inside repo or the configured
mounted AGERE SSD with expected datasets/weights directories; resolve symlinks
before access. New data/model products stay SSD. Preserve repository-relative
legacy manifests; use absolute SSD references where required. Explicitly record
purpose through conversion, and refuse critic adapters in the drafter loader.
Runtime also compares purpose against the bound training manifest. No trained
critic is inferred from this interface change. Acquire the same SSD workload lock
and reject overlap with CPU runs/proofs before any model work. Training resources
remain separate from the8GB deployment cap.191 tests passed including path escape,
missing-SSD-marker and wrong-role rejection tests. No novelty claim.

## 2026-10-25 — Critic corpus02 and actual tokenizer parity passed

New corpus02 completed:3522 examples /1761 balanced pairs;3140 train across414
report groups,382 validation across49;90 pairs rejected together for length.
Mutations:959 operation and802 source-operand. All3522 full token sequences,
prefix boundaries and target lengths agree under pinned GGUF and official HF
training-environment tokenizer (Transformers4.57.1/tokenizers0.22.2). No model
training or accuracy result follows from these checks. Raw rows remain SSD;
small manifests/parity evidence copied into repo for provenance.

Copied the pinned3B NF4 training checkpoint and configs to SSD with exact hashes;
legacy repository copies and manifests remain untouched for previous actor proof.
Trainer now accepts an explicit verified training-base manifest, resolving folder
through the authorized artifact policy. New fit/train outputs use SSD.191 tests
passed. Next gate is an actual2-update fit on the longest critic sequence, with
optimizer/tensor/gradient/GPU-memory evidence. No automatic inference gain claim.

## 2026-10-25 — Actual critic fit passed

Actual3B NF4 critic fit completed2 optimizer updates on longest1023-token training
sequence. Finite nonzero gradient norms39.39/35.89;504 changed adapter tensors,
14,966,784 trainable parameters. Peak allocated GPU3,860,632,576 bytes/reserved
4,225,761,280; host RSS1.818GB observed at second update. Runtime9.18s after load
preflight. Raw events/weights/log/manifest on SSD; hash-bound aggregate in
critic3b-fit-01.json. The repeated-example loss decrease is not validation or QA
performance. This is an adaptation feasibility milestone, not novelty.

Next: one full training epoch over3140 examples,382 train-validation examples,
393 accumulation groups at existing optimizer settings, no prompt/data changes.
Keep conversion, actual adapter application proof and useful natural-error
verification improvements as distinct later requirements. CPU inference cannot
overlap GPU training. Full external queue remains pending host headroom and
serialized model-work availability. Do not call the fit adapter a deployed critic.

## 2026-10-25 — Full critic training actually running

After successful fit and source milestoneb89d297, launched the full critic epoch
in a detached processPID26043, exact identity/command/time in
critic3b-training-launch-01.json. Actual optimizer events confirm live learning,
not just a pending job. At the latest observation21/393 updates (168 examples)
had completed; GPU allocated3.912GB/reserved4.228GB, host RSS1.807GB. Pace~11.27s
per8-example update implies~70min training remaining at that observation, plus
validation/save overhead. No completed validation or inference gain is claimed.

The training dataset has no UNKNOWN targets; do not infer abstention calibration
or semantic completeness from balanced PASS/FAIL supervision. Evaluate natural
model errors and missing/ambiguous evidence separately before trusting the gate.
Do not edit trainer/data while this identified job is live or launch competing
model work. Full external recovery remains pending model-work serialization and
host headroom. Novel contribution and publication-quality confirmation remain
unproven; strong critic and comparably adapted SAS are still development needs.

## 2026-10-25 — Explicit critic deployment and proof interface prepared

Previous turn is progress: actual fit plus live full-epoch learning, not a status
restatement. TrainingPID26043 was revalidated this turn and continues; no trainer,
encoded dataset, parity or checkpoint file was changed. Runtime work is independent
of the active training inputs.

Add load_critic_adapter for verifier-purpose3B only. Recheck conversion, bound
training inputs, complete epoch counts, finite validation loss and tensor hashes;
reject actor/critic purpose interchange. Separate actor/critic policies remain
separate resident Llama instances even with identical base filenames. Application
metadata records each role's actual initialized adapter handle and SHA. No trained
critic has been loaded or evaluated yet.

Expose verdict-only review as an explicit FinQA protocol, matching the exact
training prompt/schema (tested). Preserve UNKNOWN separately and withhold; never
invent operand/unit/step-level feedback from a single verdict. Binary protocol
supports no repair or full regeneration; reject bounded/local repair modes because
there is no localization. Rich review remains the default control. Source-supported
execution alone still cannot authorize delivery.

Allow explicit SSD model directory only with exact pinned filenames/bytes/SHA,
SSD outputs through existing authorized artifact resolver, and shared workload
locking. Extend reversible0->1->0 proof with explicit critic purpose, bound
training-validation dataset and verified SSD model copy. Stream model hashing.
No proof/CPU model workload launched while training is active. Future matched
controls must use current runtime; old strict replay compatibility is not silently
relaxed after constructor changes.200 tests pass, including wrong-role/provenance
rejection, separate role policies, unknown delivery gate, exact protocol alignment
and refusal to invent patch scope. No accuracy or novelty claim.

## 2026-10-25 — Broader report-disjoint development packets frozen

Audited24 historical FinQA generation manifests plus persisted case files in repo
and SSD run roots, including declared inputs of failed runs. Exact input hashes
must reproduce; incomplete case tails abort selection. Audit found24 prior cases
across23 annual-report groups. Freeze100 further questions, one first eligible
record per distinct report, excluding those groups and prepared SFT train/validation
report groups. Selection uses IDs/groups/source order only, not answers, programs,
retrieval coverage or observed performance. No model inference on this set yet.

Unchanged lexical8-unit packet recipe; source copy and all new raw data/selection
ledger stay SSD. SHA public179237919324e7a31edb891d442a6e0e65dceb648b2ffb109dd901274874d3a8.
Call this broader development/new inference cases relative to audited roots, not
pristine unseen labels or a held-out test: the public dev source was accessible.
The evaluation-source option accepts only a byte-identical copy of the pinned dev
source, so SSD storage does not silently change labels or open test data.204 tests
pass, including group exclusion, label-independent selection and source identity.

User confirmed freeing memory and asked work to continue under the same scope,
documentation and GitHub push requirements for remote phone checks. Authorization
persists. Continue serialized model work; no CPU inference concurrent with the
identified GPU epoch. Keep GitHub STATUS and milestone evidence truthful/current.

## 2026-10-25 — Phone-friendly GitHub checkpoint

User requested continued work and remote visibility after freeing memory. Actual
available RAM now exceeds original7.4GB recovery requirement while GPU training
continues; memory blockage is resolved at this observation, but model-work
serialization still prevents concurrent CPU evaluation. Recheck after GPU exit.

Added a short README-linked LIVE_STATUS.md with explicit Pakistan-time observation,
verified process identity, actual update count, measured pace, pending gates and
novelty limits. It is a committed snapshot, not an automatic live monitor or a
promise that the job remains live after a later reboot. Replaced the stale front-
page September lab-status assertion with current checkpoint links; historical lab
guides remain preserved. No model sources or training inputs changed. No tests
added for this documentation-only milestone;204 existing checks passed already.

## 2026-10-25 — Frozen post-training evaluation queue

Current epoch remains live; previous turn is progress (explicit role runtime and
broader100-report development preparation). Prepare a serial fail-closed queue:
full epoch verification -> critic conversion -> reversible application proof ->
matched plain/applied binary controlled probes -> paired probe analysis -> matched
plain/applied natural24 QA -> draft/prompt identity guard and paired analysis ->
unit sensitivity -> original external baseline recovery. No report100 inference
or new novelty claim is hidden in this queue. Original external worker is unchanged.

Extend probe only through explicit profile/protocol/frozen-input/adapter arguments;
legacy defaults retain both critics/protocols. Applied mode requires validated
critic purpose and a matching successful application proof. New paired comparison
requires identical public/label hashes, model bytes, source code, context, token
limit, memory cap and actual prompts. UNKNOWN remains a nonaccept, not a proved
negative judgment. Natural QA must preserve actor output and critic input exactly.

Queue waits on the actual training PID/create-time/out identity, checks complete
393-update epoch and all saved/input hashes, then freezes sources and runtime
versions. It never retries or overwrites. Every job gets a separate process group;
monitor queue controller plus complete subprocess tree under6.4GB and1GB host
reserve, retaining inner runner evidence too. Any failed dependency/job/identity/
hash/memory gate stops later stages. All artifacts remain on SSD. Offline paired
and unit-audit tools now accept authorized SSD paths without rescoring raw records.
209 tests pass before queue freeze, including incomplete epoch, changed source,
changed actor draft/prompt and always-accept-vs-pair-discrimination controls.

## 2026-10-25 — Pre-launch queue freeze audit tightened

First plan01 was prepared but NOT launched. Pre-launch inspection found that
explicit converter/tokenizer metadata and two imported FinQA/data helpers should
also be frozen. Add them and the training-base config files, and reverify actual
training base/config hashes after the epoch before conversion. Keep plan01 as
superseded evidence; build a new plan02 rather than silently replacing it. No
model output or active training input is changed. No automatic retry is involved.

## 2026-10-25 — Plan02 frozen for automatic serial execution

Plan02 contains10 explicit jobs and54 frozen inputs. Plan01 is marked superseded
before launch on SSD, unchanged. Plan02 copied to repo as metadata only. The active
epoch was still live at337/393 updates on this observation; no completion inferred.
Queue will wait, then validate the full epoch before conversion/proof and matched
binary critic/QA controls. Natural QA guard requires identical actor outputs and
critic prompts, with only critic adaptation differing. Unit sidecars preserve raw
primary scores. Original unadapted external recovery is last. Fresh100 report
packets are deliberately not evaluated before these development gates.

All model work remains serial and complete process-tree RSS monitored. Failures
stop the queue without retries/overwrite; a queue-complete marker is not research
completion or a novelty claim. See POSTTRAIN_QUEUE.md for precise limitations.

## 2026-10-25 — Cache prior-art screening during verified training wait

Primary-source review now includes LRAgent§3.2/AppendixC.2 and abstracts ofForkKV,
PReCachev2 and standard-LoRA shared-prefix tradeoffs. Scope/URLs are recorded in
RELATED_WORK_MATRIX.md. Backbone/cache sharing and role-aware cache corrections
have close prior work; do not label them a new contribution merely because they
could save RAM here. No cache implementation or active study source changed.
Current Models.call retains its per-call KV reset. Future exact-prefix efficiency
work must distinguish identical-policy reuse from adapter-tainted states and
measure real prefill work rather than only nominal input-token counts.

## 2026-10-25 — Full critic epoch, conversion and application completed

Actual epoch completed393 updates/3140 examples,504 changed tensors,14,966,784
trainable parameters. Teacher-forced validation loss0.017987 (not QA accuracy),
4651.4s recorded training walltime; GPU allocated3.920GB/reserved4.228GB.
Queue independently verified full counts, data/base/config/adapter hashes.

Conversion completed:504 tensors,59,902,112 bytes, critic purpose preserved;
SHA0150e57abf60da3c51597b788be8e1053c543bcc301818023d000be3058c7692.
Reversible application proof PASSED:zero-scale repeat drift0.0, maximum common-
token logprob effect12.4837, runtime adapter handle initialized. Inner proof peak
4.528GB; complete queue process-tree peak4.580GB, under6.4GB. This establishes
real application/effect, not verifier quality, QA gains or novelty.

The frozen queue is now executing matched plain/applied binary probes. The plain
condition reproducedUNKNOWN24/24; applied condition is not interpreted until all
24 outputs complete. No source/data/prompt was changed based on partial outcomes.
All raw logs/weights/proof stay SSD; hash-bound aggregates are committed.

## 2026-10-25 — Matched controlled critic discrimination improves

Both24-program binary runs completed with identical frozen inputs/code/base model,
prompt text, cap and token allowances; trained condition uses the proved adapter.
Plain:UNKNOWN24/24,0 reference accepts/0 mutation accepts,0/12 pairs separated.
Trained:11/12 references accepted,0/12 incorrect mutations accepted,11/12 pairs
separated;23/24 delivery-gate classifications. Paired gate delta+0.4583, report-
cluster bootstrap95%[0.375,0.5], only12 groups and controlled weak annotations.
This is a genuine measured discrimination gain from known-method role fine-tuning,
not novel methodology, natural-error QA improvement or a safety certification.

Queue has moved to matched natural24 QA. Initial drafts/prompts must match before
critic attribution. Do not extrapolate controlled95.8% to financial question-answer
accuracy. Broad100-report packets remain uninferred. GitHub checkpoint updated.

## 2026-10-25 — Delivery-effect analysis specified before adapted QA results

With the actor fixed, critic adaptation cannot change candidate-answer accuracy.
Add a separate offline analysis module, not an edit to any frozen queue input.
Require completed paired no-repair runs and the existing strict draft/prompt/role
identity guard. Report correct delivered coverage, incorrect-delivery rate,
withholding and undefined precision for a zero-delivery control. Analyze BOTH
existing reported-answer and raw executable-reference metrics; do not choose the
more favorable convention after seeing results.

Bootstrap complete annual-report clusters, preserving unequal cluster sizes, and
show descriptive sample Pareto dominance separately from uncertainty. Report an
illustrative penalty grid0/1/2/5/10 for wrong deliveries with nondelivery utility0;
these are not validated financial costs and no penalty is selected as primary.
A coverage gain with more wrong answers cannot automatically be called dominant.
Tests cover that tradeoff, zero-delivery precision, cluster handling, changed
candidate truth and missing cases.212 tests pass. No model workload or frozen
source/data was changed. Natural QA results remain incomplete at specification.

## 2026-10-25 — Natural-error transfer is a coverage–risk tradeoff

Matched24-case no-repair comparison passed strict identical draft/prompt/actor
and separate critic-application guards. Plain binary3B:3 correct delivered,
0 wrong,21 withheld. Trained binary3B:11 correct,4 wrong,9 withheld (reported-answer
metric). Raw execution:2/1/21 versus9/6/9. Candidate accuracy remains11/24 reported
and9/24 raw; this is a gate effect, not answer generation improvement. Correct
coverage gains8/24 but wrong deliveries rise4/24; no Pareto dominance. Report-
cluster95% intervals for those deltas:[.167,.52] and[.04,.333]. Illustrative error
penalty break-even2, not a validated financial cost. Unit sidecar changes no cases.
Complete inner process-tree peaks:plain4.842GB,trained4.908GB under6.4GB decimal.
Evidence: `evidence/critic3b-natural24-delivery-results-01.json`.

Manual error hypotheses: missing future-period evidence (one case lacks annotated
row), missing net-of-allowance subtraction, inconsistent percent scaling, and wrong
pension measure/entity. These guide training-only natural-error controls; they are
not adjudicated semantic labels or license for gold-specific patches. Constructed
single-edit validation performance does not establish reliable natural verification.

External recovery02 is now genuinely running (controller40968/worker41022 observed),
preserving original26 cases. All FinQA queue stages1–9 passed. Broad100-report
inference, comparable SAS adaptation, useful novelty and publication confirmation
remain outstanding.212 tests pass. Earlier running/stopped statements are dated
history; LIVE_STATUS.md carries the latest snapshot.

Do not deploy a gold-specific fix or infer calibrated safety from mutation accuracy.
Keep frozen external sources unchanged while the queue runs. Next corpus/control
should use natural training-only drafter errors and complete-policy evaluation.

## 2026-10-25 — Reserve training-source natural-error partitions before inference

New independent selector excludes whole reports in all adaptation preparations,
demonstration bank, development source and bank exclusions. Remaining174 cases
span62 reports. SHA42 whole-report assignment freezes fitting73 cases/32 reports,
model-selection52/15, diagnostic-audit49/15; no gold/performance selection. Same
lexical8-unit retrieval; public packets explicitly say train and contain no gold
answers/programs/retrieval labels. Full source copy, packets and selection live SSD.
Code/tests plus small provenance manifest committed.216 tests pass. No model calls,
natural-error labels, retraining or result gain follow from this preparation.

This is training-source research, not pristine exposure-free confirmation. Known
preparation/demo/dev exclusions are audited; all historical access and pretraining
contamination are not.15 diagnostic reports cannot certify low risk. Do not fit
on either reserved partition; future tuning invalidates any untouched-audit claim.
Do not add inspected dev24 errors to the fitting corpus. Natural-error generation
must wait for current external inference to finish; do not overlap workloads.

Next comparison should retain naturally correct outputs and report numerical
metric disagreements rather than force all syntactically valid programs positive
or all disagreements negative. Natural-error labels remain weak numerical labels,
not independently adjudicated semantic truth. Before a new epoch, freeze corpus,
update-matched mutation-only control and complete delivery-policy evaluation.
SAS comparable adaptation remains necessary; this preparation is not that result.

## 2026-10-25 — Prepare comparable SAS adaptation without shorter training inputs

Current evidence confirms original full7B HF assets on SSD but no new comparable
SAS adaptation run or fit. Local PEFT prepare_model_for_kbit_training casts
nonquantized BF16/FP16 parameters to FP32. Qwen7B has untied152064x3584 input and
output matrices: together4.36GB atFP32, before its quantized decoder/activations.
That is a shape estimate, not a measured7B allocation or an observed7B OOM.

Added independent frozen_head_loss.py. It streams frozen vocabulary blocks to
hidden-state device, performs stable full-vocabulary mean CE, and recomputes blocks
in backward. Causal wrapper uses full decoder context and ordinary next-token
shift; no training target/context/vocabulary shortening or gradient pruning.
Frozen CPU head and separate embedding offload are the intended integration path.
The current trainer and all54 frozen queue inputs are unchanged.

Six CPU tests pass in training runtime: dense loss/gradient comparisons across
FP64/FP32/BF16 and block boundaries, finite differences, extreme logits, ignored
labels, scaling, causal boundary, and two real tiny random Qwen2+LoRA optimizer
updates matching dense-reference gradients/parameters within explicit tolerances.
This is not full7B training, CUDA transfer validation, memory fit or QA gain.
Evidence/log hashes: evidence/frozen-head-loss-cpu-proof-01.json; logs SSD.

Memory-efficient cross entropy already has strong prior art (Cut Your Losses,
arXiv2411.09009, abstract read). This reference helper is baseline engineering,
not a novel algorithm or the paper's optimized kernel. Next measure actual serial
7B fit with frozen CPU embedding/head and monitored host/GPU peaks after external
queue completes. Only then attempt the same661/100 adaptation protocol and prove
converted adapter application before paired QA. Do not claim both systems equally
optimized yet. Keep old failed3B fit provenance and do not mislabel it as7B failure.

## 2026-10-25 — Primary-source check narrows semantic-verifier novelty

Read primary abstracts of Same-Number Citation Swaps (2610.08675v2) and Enhancing
Arguments Recognition (FindingsEMNLP2024). Fixed-number wrong-role citations with
valid-equivalent controls, and financial-operand supervision, already exist.
Record these before designing a claim from the four natural false accepts. A useful
improvement may still be achievable, but same-number/source-role tests alone are
not defensible originality. Full-method distinctions remain unverified.

Primary FinAgent-RAG record2605.05409 is WITHDRAWN,5July2026, for fundamental
experimental design errors; do not repeat search-snippet performance as reliable
prior results. No external benchmark protocol or current code changed by this read.

## 2026-10-25 — Queue a real comparable SAS7B fit after external completion

Previous turn is progress: added a numerically tested frozen-head loss and verified
ongoing external inference; useful novelty remains unproven. This turn implements
an independent serial fit controller/worker, leaving all54 current queue inputs
unchanged. A frozen new plan waits for original dependency PID/create-time/plan,
requires every job complete in order plus external arm/original-byte validation,
rechecks code/data/tokenizer/runtime, and makes only one fit attempt. No retries.

Use the original661/100 actor corpus, longest complete training sequence, rank8/
alpha16/all-linear LoRA, AdamW2e-4 and clip1; fit is two actual updates, not an epoch.
All official7B source assets must match existing pinned snapshot hashes. NF4 decoder
on GPU; actual frozen embedding/head on CPU. Local Accelerate source inspection
shows CPU device_map hooks ordinarily reload whole matrices onto GPU. Detach the
leaf hooks to restore CPU weights, explicitly compute CPU embeddings and transfer
inputs_embeds; stream the frozen head instead of calling its forward.

CPU tests verify actual hook meta→CPU restoration and exact original weights,
input_ids versus explicit embeddings, all-linear frozen heads, and checkpointed
BF16 LoRA gradients. The latter found a real precision defect in the earlier helper:
BF16 per-block backward rounding yielded one5.33% gradient discrepancy. Preserve
the failed log and old source; fix FP32 product accumulation before the final cast.
The unchanged tolerance now passes. A4099-vocabulary multi-block gradient test also
passes.15 targeted training-runtime CPU tests pass; general suite231 run with10
runtime-dependent skips covered by those targeted tests. No GPU/full7B fit yet.

Plan training resource policy:10.5GB controller-tree RSS cap,1GB host reserve,9GB
available-memory preflight,0.2s sampling, plus recorded actual GPU peaks. This is
separate training resource use, not8GB deployment fit; deployment remains6.4GB.
Only start after the existing external queue succeeds and exits. Success still
requires full SAS adaptation, conversion, reversible application proof and QA.
Method novelty remains unproven. Details SAS_OFFLOAD_FIT.md and CPU evidence JSON.

## 2026-10-25 — Actual waiting fit controller launched from21be703

Prepared and launched SSD sas7b-offload-fit-01 with planSHA
1b2ca7371810444610e7fc348df8a794e0e060f40a4b660284266b22647ad523.
ControllerPID47307/create-time1792930227.21 verified live/sleeping; state
waiting_for_frozen_evaluation on controller36374/create-time1792926351.41.
Zero child workers and no fit directory confirm no7B model load or updates yet.
Launch/plan evidence committed; controller logs/state/memory/weights stay SSD.
Current external recovery controller40968/worker41022 also verified live;46/90
Mortar SAS cases saved including26 preserved originals. All4 external arms still
must complete; no final external result or novelty claim follows from this count.

Queued process performs no Git operations and cannot complete this research goal.
Later milestones still need agent inspection, commit/push, comparable adaptation
and validated useful novelty. A future failed fit is evidence to diagnose, not a
reason to retry implicitly, weaken memory checks or claim a trained SAS system.

## 2026-10-25 — Controlled critic negative-family extension prepared

Previous turn is progress: implemented/measured CPU checks and launched a verified
waiting SAS fit controller. Current external and waiting controllers revalidated.
Do not classify this as a new user-input blocker; queued model work is live.

Natural dev24 failures suggest training gaps beyond single-operator/source-operand
edits: output scaling and omitted intermediate calculations. Add two established
augmentation families: append multiply/divide100 without changing declared output
units, or bypass one used nonfinal arithmetic node through a source/prior operand,
rewiring all consumers and renumbering subsequent references. Keep only executable
source-supported candidates wrong under BOTH existing numerical metrics. This is
not semantic adjudication, a natural-error corpus, or a novel mutation algorithm.

Control original dataset exactly: same3522 rows,3140/382 split,414/49 groups,
1761 positive rows byte-identical, source order and planned393 epoch updates.
Nominate half source IDs by SHA42; choose an eligible new family/candidate by SHA;
otherwise retain old negative. Do not try another family when nominated candidate
overflows1024. Final820 replacements:626 output scale,194 node bypass;34 length
fallbacks. Negative totals:520 operation,421 operand,626 scale,194 bypass.
Training tokens2271875→2312723 (+1.798%); validation264358→270765. Same updates is
not identical compute. No training or QA gain follows from data preparation.

Final corpus02 lives SSD datasets/tier8_v2_critic/critic_extended_sft_02.01 is
preserved/superseded before training because inherited original selection metadata
needed explicit base-versus-extension wording and original dataset pinning;02
example bytes are identical. Preparation01 measured0.360GB whole-tree peak under
3GB preparation cap;02 did not repeat memory measurement. Vocabulary tokenization
only, zero model forwards. HF/GGUF parity all3522 passed. An independent auditor
that never calls mutation generators replayed BOTH3522-row corpora, checked exact
positive row bytes, source order, numerical labels and stored executions. All pass.

Seven new unit tests pass; inference-runtime regression238 run with10 training-
runtime skips already covered by the unchanged targeted training-runtime tests.
Hashes/aggregates: evidence/critic-curriculum-prepared-02.json. Code/data/logs kept;
all raw training rows on SSD. No inspected development cases enter the corpus.

Prepared—not scheduled—one controlled new epoch and paired broader100-report dev
comparison against the current trained critic, fixed actor/no repair. Before this
comparison, extend analysis with explicit trained-versus-trained pairing/labels;
existing natural_pair assumes untrained control. Report both numerical metrics,
correct/wrong/withheld and cost; do not select favorable units or hide extra risk.
Candidate accuracy must match, since only verifier changes. Corpus families are
coupled; individual effects need later ablation only if combined gain warrants it.
SAS fit remains queued first; comparable full SAS adaptation still outstanding.
No premature novelty claim; publication confirmation remains outstanding.

Current checkpoint: external controller40968/worker41022 verified;62/90 Mortar
SAS cases saved. SAS fit47307 verified sleeping, zero children. Corpus feature
committeda66e276; final test-log/source bindings and prepared training-base hash
recorded. No additional neural job launched and no frozen source changed.

## 2026-10-25 — Explicit trained-versus-trained delivery analysis implemented

Previous turn is progress: fixed-source/positive/update critic corpus and full
numerical/token audits completed. Current controllers revalidated live; no restart
on a waiting state. Delivery analyzer is not among either live plan's frozen
inputs; confirm this before editing. All frozen inference/training sources remain
unchanged. New module adds strict two-trained-critic pairing; legacy plain-trained
mode stays the default with unchanged metric values.

Require distinct validated full critic adapters, same actor and noncritic config,
identical model/source/code/runtime/cap metadata, and two real reversible application
proofs bound to each training-validation prompt/dataset. Recompute proof effects
from phase logprobs, not trusted summary scalars. Validate current model/source
artifact hashes. Reconstruct recorded initial plans and source executions, both
numerical scores, binary verdicts and delivery flags. Require exact public input
coverage/order, no repairs, intended initialized C handles and matching actual
actor outputs, prompts and critic allowances. No-context failures remain counted
as withheld; do not discard them as incomplete candidate solutions.

Explicit CLI comparison-kind trained-variants requires both proofs and named
trained conditions; plain/untrained and duplicate condition labels rejected before
input reads. Statistical deltas always right-minus-left. General study footer says
development analysis (broader100 is not previously inferred, but still public dev).
The old plain-trained natural24 replay reproduces ALL metric values and matching
guard exactly. Actual current trained24 case execution/score/delivery replay and
27 artifact checks pass; actual reversible proof effect recomputes. Self-comparing
the same critic is correctly refused as a treatment contrast. This is verification
infrastructure, not a model improvement or a newly evaluated second trained critic.

248 inference-runtime tests run,10 unchanged training-runtime-dependent skips;
all new10 guard tests pass. Earlier targeted15 training-runtime tests cover those
unchanged skips. Successful two-distinct-trained pairing is tested with fixtures;
real positive pairing awaits extended training/conversion/proof/QA. Raw diagnostic
reports/logs remain SSD, small aggregate/source hashes committed. Prepared100-report
experiment now has concrete analysis args; it remains not scheduled. Goal active,
useful novelty and publication confirmation remain unproven.

## 2026-10-25 — Completed external evidence and first SAS loading-cap failure

## Latest authoritative terminal results — external complete, SAS fit stopped

All380 original unadapted external case-arm evaluations completed. Mortar local
exact:SAS39/90,MAS26/90; FRAMES closed-book strict2/100,1/100 (same punctuation
sensitivity). Mortar9-case-cluster paired MAS−SAS−.144,95%[-.239,-.045]; FRAMES
question-bootstrap[-.05,.02]. All original26 cases preserved; complete external
queue-tree peak5.628GB under6.4GB. Partial-document/local scoring and unequal
allowances896/1792 mean no full-benchmark/optimized-architecture claim.

MAS returned empty transaction lists57/57: all11 correct matches are empty-gold;
0/46 nonempty-gold matches. All required identifiers are literally retrieved in19
of46, not semantic sufficiency. Final generations all stopped normally. SAS13/46
nonempty matches. This is an observed unadapted-system capability/retrieval gap,
not evidence that more agents or unused token budget helps. Corpus/critic FinQA
experiments remain separate, not transferred performance claims.

Queued7B fit started after external completion and was killed by its monitor
while loading (first shard complete). Tree RSS10.547761GB exceeded separate10.5GB
training cap, with host available11.643687GB at last sample. Zero updates, no
adapter/fit summary, only loading event. No physical OOM or GPU fit result is
established. Original failed source/logs preserved. Diagnose mapped checkpoint
storage retention; test CPU-weight detachment before one new protocol attempt,
without raising cap or shrinking context/targets. Neither controller remains live.

Trained-versus-trained analysis guard is implemented/tested; actual second critic
still untrained.248 tests covered across required runtimes. Broad100-report and
174-case natural packets still uninferred. Useful novelty/publication confirmation
and comparable full SAS adaptation remain outstanding. LIVE_STATUS.md is current.

External audit independently replays380 scores/token ledgers and validates unchanged
shared public packets. Initial audit assumed the wrong stage token key; preserve
failed log01, correct to usage.completion_tokens, and rerun into new reports02/03.
No model results were regenerated or rewritten. Grouping uses explicit source
test_case_number, not guessed ID prefixes. Rule constants remain fixed diagnostics.
Current installed Transformers ignores offload_state_dict/low_cpu_mem_usage kwargs;
do not claim those flags solve loading memory. Inspect actual CPU parameter
assignment and safetensor storage ownership before modifying loader behavior.

## 2026-10-25 — Twelve-hour contribution window and cross-tier method freeze

User requires current8GB stage to establish the common feature/method base;
16GB/32GB cannot introduce new methods. About12 hours allocated starting18:54UTC,
approximate end06:54UTC26October (11:54PKT). Do not confuse deadline with achieved
novelty. Prioritize one useful differentiated mechanism and strong controls, not
more infrastructure or unrelated task expansion. Freeze shared policy before
higher tiers, with tier-specific capacity/resource/training choices predeclared.

First revised SAS fit addresses a concrete loading hypothesis: cloned CPU matrices
can release checkpoint-mapped storage ownership between shards. Use public Torch
leaf post-load hooks through a Qwen subclass, preserving exact weights/dtypes and
normal forward. CPU test proves distinct storage/equal values; actual improvement
unproven. Preserve old failed source snapshot/run. Same10.5GB RSS cap,1GB reserve,
9GB headroom and full sequence/targets. Add USS/PSS diagnostics without replacing
RSS enforcement. Prepare now accepts a missing dependency PID only when all its
frozen jobs and external outputs demonstrably completed. No blind restart.
