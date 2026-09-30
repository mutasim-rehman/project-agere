# Phase 3: untouched dev floors on all RAM tiers

This runner evaluates the untouched SAS Q4_K_M model and the three resident MAS F16 instances at **8 GB, 16 GB, and 32 GB**. It uses the 100 Agere-KYC-Synth dev cases and 50 Agere-Credit-Synth dev cases for each arm and tier. The 16 GB result remains the primary research comparison. The frozen test files are not opened; their names and SHA-256 hashes are copied into each SSD run manifest before scoring.

**Run this after Phase 2 has finished.** Each tier needs passed SAS and MAS smoke records with the same context, all selected GGUF files, the Phase 2 GGUF SHA-256 manifest, and the existing Python environment and pinned llama.cpp CPU build on the lab PC. The runner verifies those inputs. The SSD must be mounted at the actual path in `AGERE_SSD_ROOT`; all evaluation cases, stage traces, model-server logs, session logs, memory records, manifests, summaries, and floors stay on the SSD.

## Windows PowerShell

From the cloned repository on the lab PC, replace `X:\AGERE` with the actual mounted SSD path:

```powershell
git pull --ff-only
$env:AGERE_SSD_ROOT = 'X:\AGERE'
.\.venv\Scripts\python.exe scripts\phase3.py run --tier all --arm both
.\.venv\Scripts\python.exe scripts\phase3.py summarize --tier all
```

The run prints each case's tier, arm, progress, generated tokens, structured invention flag, and observed peak RSS. It visits **16 GB, 8 GB, then 32 GB**; each arm is run alone, and all three MAS model processes remain resident together for its cases. The runner applies the same fixed host-adjusted cap to both arms of a tier, leaves 1 GB of host memory available for the OS, and terminates model servers on a memory breach. Its defaults use the matching Phase 2 smoke contexts. A full all-tier CPU run can take a long time; leave the SSD connected and keep background RAM use stable.

If a tier or arm fails, inspect its SSD `failure.json`, `memory.json`, server logs, and session log. Rerun the same command to resume completed cases. To rerun just one tier or arm, use `--tier 8`, `--tier 16`, or `--tier 32`, and optionally `--arm sas` or `--arm mas`. If a memory breach occurred, use a **new run ID** after changing the setup; the breached run is marked invalid and cannot create a floor. To preview the workflow without a full floor, use `--limit 10 --run-id preview10`; this preview covers only the first 10 KYC cases.

## Linux

```bash
git pull --ff-only
export AGERE_SSD_ROOT=/media/your-user/AGERE
.venv/bin/python scripts/phase3.py run --tier all --arm both
.venv/bin/python scripts/phase3.py summarize --tier all
```

Linux requires the same writable delegated cgroup v2 memory controller used in Phase 2. A host that cannot load the 32 GB tier under its cap will log that tier's failure while preserving completed 16 GB and 8 GB results. Run that tier later on a suitable host with the SSD and the same repository commit.

## What is scored

Both arms receive the same deterministic `document_extractor`, `financial_calculator`, and `policy_retriever` results. The SAS makes one completion. MAS makes one extractor, one drafter, and one verifier completion; the verifier's view is recorded but it does **not** gate or repair the naive draft. The `citation_verifier` then checks exact source spans and calculator IDs in either arm's structured facts. Per-case generation stays within a 2,048-token ceiling and includes no adapter or fine-tune.

Summaries report valid JSON, structured invention among complete claim sets, mismatch recall, grounding accuracy, missing-field refusal correctness, failure tags, generated tokens, latency, and process-tree peak RSS. These are **provisional synthetic dev floors**. The 2,048 ceiling counts generated output tokens, not private reasoning tokens. The dataset-quality review and versioned policy corpus are still pending. The retriever explicitly returns `UNAVAILABLE`, and draft prose is retained for later human review rather than silently counted as fully grounded. Do not use these metrics as the final held-out paper result.

## SSD outputs

```text
AGERE_SSD_ROOT/runs/phase3/untouched_dev_v1/
  logs/session_<timestamp>.log
  all_tiers_summary.json
  tier8/                         # likewise tier16/ and tier32/
    run_manifest.json            # dev hashes, frozen test references, model hashes, cap, context
    naive_sas/
      cases.jsonl                # one result per dev case, appended immediately
      stages.jsonl               # one line per model stage
      summary.json
      memory.json
      memory_sessions.jsonl
      logs/server_sas.log
    naive_mas/
      cases.jsonl
      stages.jsonl
      summary.json
      memory.json
      memory_sessions.jsonl
      logs/server_*.log
    naive_floor.json             # created once when both full arms finish and memory is valid
    phase3_summary.json
```

The repository contains only the runner and documentation. Do not copy dataset cases or generated evaluation outputs into git.
