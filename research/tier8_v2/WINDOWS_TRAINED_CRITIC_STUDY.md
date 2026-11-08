# Windows 8 GB matched trained critic replay

The earlier unadapted binary reviewer abstained on every
candidate. The order-agreement reviewer accepted two wrong
answers on naturally generated programs. This experiment tests
two existing trained critics on identical generated candidates.

The 16 fixed candidates are the wider-evidence arm of the
completed retrieval pilot. All cases are retained, including
wrong candidates and any execution failures. The frozen replay
packet includes question, evidence, program and execution only.
Its SHA-256 is
`c22a01671d09e19295b434582c1859093da730f5f0967c34abb2b24125ef72f5`.
None of its report IDs appears in the four inspected critic
training and validation corpora: the two matched continuation
conditions, extended critic SFT and binary critic SFT. This is
a verification replay on an existing cohort, not a new
end-to-end replication.

Both critics use the same 3B Q4 base, binary prompt and schema,
and 192-token ceiling. Only the matched continuation adapter
changes. The control and crossed conditions differ in their
negative data construction as described in
[the matched continuation protocol](MATCHED_CONTINUATION.md).
Adapter order alternates by question. We count PASS on a valid
execution as a delivery. FAIL, UNKNOWN, malformed output and
invalid execution withhold. Accepting every executable candidate
is a fixed-coverage diagnostic comparator. Report official and
reported-answer correct, wrong and withheld counts on all cases.

SSD files under `runs/tier8_matched_continuation`:

- `control-critic-converted-01/adapter-f16.gguf` SHA-256
  `b25e76673814e5f2fc3257f106566bce27c38d614bd5e8febf1b2d107eb84fb3`
- `crossed-critic-converted-01/adapter-f16.gguf` SHA-256
  `a67e3c416314062e84a92978a148da3b8cda1a61ede560c876eaf6190080a814`

Use `tier8_windows_trained_critic.py replay` with both adapters,
the frozen cohort, and a 6.1 GB job commit limit. Run
`summarize` with the saved ledger and pinned FinQA scorer.

## Independent recomputation control

Run a separate 7B Q4 direct solver on those same evidence
packets. It sees the question and sources but never the
candidate, calculated result, or review decisions. It returns a
number and unit using a 192-token ceiling. The gate accepts the
frozen program only when the independent result agrees in
value and unit. Fraction and percentage points are normalized
to the same ratio. Number and ratio remain distinct. The
numeric tolerance is 0.00001 times the larger of one and the
absolute program result.

This borrows independent recomputation as a cross-check. Both
models still share the same source packet and model family, so
their errors can correlate. It is a sequential 7B reviewer with
a different evidence interface and checkpoint, rather than a
causal isolation of input visibility. Include its actual compute,
correct/wrong/withheld and memory results alongside the trained
critics and accept-all comparator. The 6.1 GB worker commit
limit applies to this control.

We report both coverage and error among accepted cases, along
with correct and wrong deliveries over all assigned questions.
Rejecting every candidate has zero wrong deliveries and
undefined accepted-case error. These fixed thresholds are
descriptive and carry no calibrated selective-risk guarantee.
[Selective classification](https://arxiv.org/abs/1705.08500)

Use `tier8_windows_trained_critic.py independent` with the same
frozen candidate cohort and `--direct-weights` pointing to the
first SSD 7B Q4 shard. Score that ledger separately.

## Matched trained-critic results

Under official scoring, accepting all executable programs gives
4 correct and 12 wrong answers. The control critic gives 3 correct,
0 wrong and 13 withheld. The crossed critic gives 2 correct,
0 wrong and 14 withheld. Reported-answer scoring counts the same
accepted cases as correct, while its accept-all baseline counts
3 correct and 13 wrong. The control retained all three candidates
that matched both scoring conventions. The crossed condition
lost one additional correct candidate without reducing observed
wrong deliveries further. This does not support adopting the
crossed training method over control.

Both completed 16 calls, peaked at about 2.52 GB sampled RSS
and 2.92 GB worker commit, and took about 17–18 seconds per
review including model loading. Zero wrong answers among three
accepted cases is an observation on a small replay, not a
calibrated safety guarantee.
All three control-accepted programs also matched the annotated
symbolic expression in the normalized backward-slice audit.
The one official-only candidate the control withheld did not.

## Frozen transfer replay

We freeze all 21 narrow-evidence candidates from the separate
retrieval replication. Narrow retrieval was chosen at the recipe
level after the wider-evidence accuracy gain failed to replicate.
No candidates are excluded by correctness. The same four critic
training files were audited and no candidate report overlapped.
The frozen input SHA-256 is
`0dc7db01534ca92511ba26e239b40210f759441967c8e356d73c5ebda70e4bb6`.
Run the same matched critics and report both metrics. This
tests transfer to different reports and the narrow recipe,
so a change in coverage may reflect candidate mix as well as
review behavior.
