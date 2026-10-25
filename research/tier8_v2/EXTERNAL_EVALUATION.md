# SSD external baseline evaluation — 25 October 2026

Run: `/run/media/mutasim/Data/AGERE/runs/tier8_external/external_baselines_20261025_01`.
Controller log: `/run/media/mutasim/Data/AGERE/runs/external_baselines_20261025_01.log`.
Source: `scripts/tier8_external_eval.py`; launched from commit `caf3a3a`.
Code and environments stay on the computer; all new raw packets, labels,
responses, memory samples, run manifests and reports stay on the SSD.

The queue runs all 90 prepared MortarBench questions for SAS, then MAS,
followed by all 100 FRAMES questions for SAS, then MAS. No adapters are applied.
This is a new external baseline measurement, not confirmation of an adapted
system and not evidence that the existing adaptation generalizes.

- SAS: original SSD Qwen2.5-7B Q4_K_M.
- MAS: distinct simultaneously resident 1.5B F16 drafter, 0.5B F16 extractor,
  and 0.5B F16 verifier. The two small instances are separate.
- CPU, eight threads, context 4096, greedy seed42, temperature0.
- Common ceiling: 2048 generated tokens per case. Actual allowances differ:
  SAS brief analysis128 + answer768; MAS extraction256 + draft512 + critique256
  + final768. This compares configured systems under an equal ceiling, not
  equal token expenditure. Actual output and prompt tokens are retained.
- RSS: a single cap fixed before the queue, min(6.4 billion bytes,
  available RAM minus1 billion bytes); sample controller+worker tree every0.2s,
  terminate on RSS breach or less than1GB host available. Simulated tier on
  a larger machine, not physical 8GB validation.
- Model bytes and SHA256 must match the SSD Phase2 manifest. Both datasets
  must match the committed `manifests/test.sha256` before inference starts.
- No resume/overwrite; an incomplete or failed arm stops the remaining queue.

MortarBench packets use only question, answer type, bank-statement JSON and
ULAD XML. JSON records and XML leaf paths are rendered as source units;
question-only lexical IDF ranks units into a fixed 1700-token evidence ceiling.
The 0.5B tokenizer constructs packets once, shared identically by both arms.
Labels and annotated answer IDs never rank or select evidence. Packet source
IDs, available-unit counts and full selected text are retained. This retrieval
can miss relevant evidence and does not include separate PDFs/paystubs.
Missing evidence is not reliable evidence of absence; forced boolean/list
outputs are a limitation of this baseline and should not be used for decisions.

MortarBench scoring is **local exploratory typed exact match**, not a claimed
reproduction of its official benchmark scoring. Boolean yes/no labels map to
booleans; ID lists compare as order-independent sets; none maps to an empty
set; malformed model JSON cannot match an empty gold set. Results should also
be examined by answer type and loan group (only nine prepared cases).

FRAMES is the original documented closed-book negative control. Models receive
only the question; evidence links are not fetched. Preserve strict case-insensitive
trimmed exact match, and separately report punctuation-normalized sensitivity.
It does not measure retrieval performance or prove multi-hop reasoning ability.

Both external datasets were present in the historical project's frozen manifest.
Their historical evaluation/exposure has not been exhaustively audited; do not
call this a pristine unseen test or a preregistered publication confirmation.
All labels accessed during format/scorer checks are development exposure.

Validation before launch: 171 tests passed, including label isolation, nested
JSON/XML rendering, invalid-versus-empty answers, ID-set comparison, and separate
strict/normalized FRAMES scoring. The test log and full environment/launch metadata
are saved on the SSD. Tests establish software behavior, not model quality.
