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
