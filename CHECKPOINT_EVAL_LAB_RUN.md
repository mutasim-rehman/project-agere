# Paired checkpoint diagnostic on the lab PC

This optional early run compares each **original Hugging Face F16 checkpoint** with its Phase 2 **GGUF output** on the same 60 synthetic dev tasks. In the 16 GB tier, that means 14B HF F16 versus 14B GGUF Q4_K_M, plus each of the 3B, 1.5B, and 0.5B HF checkpoints versus its GGUF F16 conversion. Use `--tier 8`, `--tier 32`, or `--tier all` for the other tiers. Shared MAS checkpoints are evaluated once per tier, even when two agent instances use the same file.

This is a **checkpoint-level diagnostic**, with strict JSON, missing-field, tool-call, and citation proxy scores. It is not the orchestrated SAS-versus-MAS comparison, does not measure the paper's full invention rate, and never reads train or frozen test rows. Keep the Phase 3 and Phase 6 evaluations separate. The `agere-synth-v1` starter set still needs the roadmap's data-quality review before a research claim.

The runner verifies the committed dev dataset hashes, the selected original HF file hashes, and each selected GGUF SHA-256 from the Phase 2 SSD manifest. It renders identical chat prompts with the original tokenizer for both formats, runs greedy CPU generation, saves each case immediately, resumes completed cases, and writes a summary after each variant. GGUF is subject to the tier's host-adjusted RAM cap and configured OS reserve (4 GiB by default under the Ubuntu launcher). Original F16 HF models are **quality references**, not tier-feasible deployment candidates: 14B and 32B exceed the conservative job budget on this 32 GB Ubuntu host. The runner records an explicit infeasible-reference failure and continues other variants; it does not emit a fake score. Do not compare HF and GGUF latency as a controlled performance result.

## Windows PowerShell

Run from the cloned repository on the lab PC **after Phase 2 conversion stops**. Replace `X:\AGERE` with the real mounted SSD path. If Phase 2 setup already created `.venv`, reuse it.

```powershell
git pull --ff-only
$env:AGERE_SSD_ROOT = 'X:\AGERE'
.\.venv\Scripts\python.exe scripts\eval_checkpoints.py setup
.\.venv\Scripts\python.exe scripts\eval_checkpoints.py run --tier 16 --arm both --format gguf
.\.venv\Scripts\python.exe scripts\eval_checkpoints.py run --tier 16 --arm both --format hf
.\.venv\Scripts\python.exe scripts\eval_checkpoints.py summarize --tier 16
```

The GGUF command works once `AGERE_SSD_ROOT/phase2/manifests/gguf_artifacts.json` exists. The HF command can run independently, but let conversion finish first to avoid competing for RAM and SSD bandwidth. For an early short preview, use `--limit 12 --run-id preview12` on **both** run commands; the full 60-row run uses the default `dev_sft_v1` run ID. A different limit, token cap, context, or dataset requires a new run ID. Each command prints per-case progress and elapsed time. Rerunning resumes finished cases rather than rewriting them.

To run another tier after the 16 GB run, change `--tier` to `8` or `32`. The original 32B F16 checkpoint has a 64 GiB weights/loading preflight estimate, plus the host reserve and runner allowance; its Q4_K_M GGUF diagnostic can run separately on a suitable 32 GB tier host. `--tier all` walks 16, 8, then 32 GB. If one variant fails, the runner records it, continues other variants, and exits nonzero at the end.

## Linux

```bash
git pull --ff-only
export AGERE_SSD_ROOT=/media/your-user/AGERE
.venv/bin/python scripts/eval_checkpoints.py setup
.venv/bin/python scripts/lab_run.py run -- eval_checkpoints.py run --tier 16 --arm both --format gguf
.venv/bin/python scripts/lab_run.py run -- eval_checkpoints.py run --tier 16 --arm both --format hf
.venv/bin/python scripts/eval_checkpoints.py summarize --tier 16
```

Run these jobs sequentially: the launcher returns after starting a background service, so use `lab_run.py status` and the printed `tail -F` command before starting the next job. Both HF and GGUF workers are bounded. On the 32 GB lab PC, original HF 14B/32B references exceed the safe budget; their failures are recorded without fabricated scores. See [lab recovery](LAB_RECOVERY.md).

## SSD outputs

```text
AGERE_SSD_ROOT/runs/checkpoint_diagnostics/
  setup.log
  dev_sft_v1/tier16/
    run_manifest.json             # dev hashes, frozen test manifest hash, exact task ids and settings
    hf_14b.jsonl                   # one saved response and score per case
    gguf_14b_q4_k_m.jsonl
    ...                            # other selected HF and GGUF checkpoints
    *.provenance.json              # model revisions and verified hashes
    summary.json                   # per-variant proxy scores and paired deltas
    failures.json                  # only if a variant could not finish
    logs/                          # worker, server, and sampled GGUF memory logs
```

The repository contains the runner and this guide. **All new results, manifests, and logs go to the mounted SSD.** Copy the SSD outputs into a separate analysis workflow when interpreting them; do not put dataset rows or generated case outputs in git.
