# Research checkpoint — 24 October 2026

Goal remains active. No novel method or model improvement is established yet.

## Verified milestones

- `5db7756`: evidence contracts, atomic repair, token ledger; pushed.
- `9bb1262`: label-free deterministic v1 baseline; pushed.
- `70ec680`: source-visible/gated pipelines and temporal KYC probes; pushed.
- `6d861cd`: opaque document IDs, paired analysis, novelty audit; pushed.
- Current standard-library test suite: 16 passing tests.
- Rule-only original development baseline: 150/150 case success, 20/20 mismatches,
  51/51 missing fields, zero generated tokens. Raw predictions and scores retained.

## Infrastructure in progress

- Project-local Python 3.12 and dependencies installed.
- CPU llama-cpp-python 0.3.19 wheel fails import (musl dependency); local source
  installation of 0.3.16 is running. Inspect `logs/runtime-build.log` and the actual
  process/session before deciding whether it failed; an empty log is not failure.
- Official 0.5B F16 GGUF downloaded and SHA-256 verified. 1.5B download is running;
  7B Q4 shards follow. Verified entries are recorded in `evidence/models.json`.
- Official F16 files are larger than the old conversions. Inspect tensor types
  and resident fit; a reproducibly documented F16 conversion may be needed to
  keep the original MAS allocation inside 6.4 GB. Never silently raise the cap.

## Next executable checks

1. Confirm source-built runtime import; capture dependency versions.
2. Validate one small-model generation and constrained JSON under measured memory.
3. Finish weight integrity checks, establish both arms' resident fit.
4. Run a four-case smoke for each arm and no/full/patch repair before larger runs:
   `.venv/bin/python scripts/tier8_v2_run.py --arm sas --repair none --limit 4 --out research/tier8_v2/runs/sas-none-smoke-01`
   Use distinct output directories; the runner refuses to mix trials.
5. Inspect raw outputs and truncation before selecting prompt/budget changes.
6. Expand credit and task variation, add strong non-LLM baselines, allocate equal
   development effort, and complete the research loop described in PROTOCOL.md.

The 24-case KYC probe is development-only, not confirmatory evidence. The old
test split was not opened during this redevelopment. No new held-out test exists
yet. Best-system search, adaptive routing, external validation, full evaluation,
and a defensible originality assessment are still outstanding.
