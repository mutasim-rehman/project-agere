# Ubuntu lab run: 16 GB and 32 GB, entirely offline after git pull

Preparation is gated until the two current8GB prompt checks, closure audits and
runtime/workflow smoke tests finish. The final handoff commit includes
`configs/lab_tiers/freeze.json`; the launcher refuses evaluation without it.

The SSD already holds all six required GGUFs and the sealed160-question/50-report
dataset. The prepared Linux x86_64 runtime includes Python, required packages,
portable AVX2 inference libraries and their matching C-library loader. Nothing
is installed into Ubuntu; no pip/apt/model downloads or Codex application needed.
The GPU is unused in this CPU-primary protocol.

From the cloned project directory on the32GB Ubuntu lab PC:

```bash
(
  set -e
  export AGERE_SSD_ROOT="/run/media/mutasim/Data/AGERE"
  git pull --ff-only
  bash scripts/lab_tiers_all.sh
)
```

This single paste starts a detached workflow: preflight, all16/32GB jobs,
automatic replay analysis, then portable export. No follow-up command is needed
on success. It writes `workflow.log` and `workflow-status.txt` in the run folder.
The same paste resumes interrupted evaluations, provided the frozen inputs and
host still match. A failed check stops the chain and leaves its reason on SSD;
it cannot promise unattended recovery from power loss or hardware failures.
Keep the PC awake and SSD connected. Git access may require existing credentials.

The launcher detects exactly one mounted `AGERE` directory under `/media/$USER`
or `/run/media/$USER`. If needed, set its actual location once:

```bash
export AGERE_SSD_ROOT="/media/$USER/Data/AGERE"
```

Use the mount path that actually exists; do not create a replacement empty
directory. The launcher prints the resolved SSD path and logs. It copies the
273MB runtime into ignored `.local/` on the PC and checks pinned hashes. This also
works when the SSD is mounted noexec. AVX2/FMA/F16C/BMI2/SSE4.2 CPU support is
checked before large model loading. Full model verification reads about54GB once
per run process and can take several minutes on a USB SSD.

`start` runs in the background and prints the console-log path. Closing the
terminal does not deliberately stop it. All12 jobs are serial: three fixed
profiles × two arms × two tiers. CPU evaluation can take a long time; actual
progress is durable on the SSD. Do not unplug the drive while it is running.

## Check progress or resume

```bash
bash scripts/lab_tiers.sh status --run-id lab-main-v1
tail -F "$AGERE_SSD_ROOT/runs/lab_tiers_v1/lab-main-v1/console.log"
```

If auto-detection was used and your shell has no `AGERE_SSD_ROOT`, use the full
console path printed by `start`, or set the actual mount path as above.

After interruption/reboot, repeat the SAME start command with the SAME tier list
and run ID. Completed cases/jobs are checked and skipped. Current code, data,
runtime, hardware and cap must match the saved manifest. An already-live worker
is never duplicated. A memory/swap breach invalidates the run: preserve its logs,
fix host conditions and use a NEW run ID. Never overwrite failed evidence.

To run only one tier, use `--tiers 16 --run-id lab-16-v1` or
`--tiers 32 --run-id lab-32-v1` consistently on both preflight/start. Do not resume
one run ID with a different tier list.16GB is primary;32GB is secondary.

## Results for later inspection

After all jobs, the controller automatically runs a vocabulary-only full replay
audit and writes `analysis/REPORT.md` plus machine-readable comparisons. Check
that status reports both evaluation and analysis complete. To re-audit or create
a portable archive after the controller exits:

```bash
bash scripts/lab_tiers.sh analyze --run-id lab-main-v1
bash scripts/lab_tiers.sh export --run-id lab-main-v1
```

The export is under `AGERE/runs/lab_tiers_v1/exports/`. Bring back the SSD, or copy
that `.tar.gz` and its checksum. It contains raw model responses, prompts, usage,
scores, stage traces, memory samples, failed/interrupted attempts, frozen code,
input/scoring data and manifests. Model/runtime payloads are excluded from the
archive; retain them on SSD for independent token replay. No upload is automatic.

```text
AGERE/runs/lab_tiers_v1/lab-main-v1/
  manifest.json, state.json, console.log
  tier16-cap.json, tier32-cap.json
  code/                         # immutable code/config snapshot
  tier16-sas-primary/            # likewise every arm/profile/tier
    manifest.json, cases.jsonl, summary.json
    attempt-0001/
      worker.log, stages.jsonl, memory.jsonl, state.json, progress.json
  analysis/
    REPORT.md, summary.json, *-replayed.jsonl
```

Preflight/bootstrap failures also write SSD logs, even before model loading.
The nominal12.8/25.6GB ceilings can be lowered by insufficient available RAM;
the exact paired effective cap is recorded. No swapping or silently substituted
smaller model is accepted. Sampling is every0.2s; this is not a hard-cgroup claim.

The main comparison uses PRETRAINED checkpoints in both arms. Existing trained7B
adapters do not match14B/32B; they are not silently reused. This is numerical
financial QA, not proof of KYC/credit safety, a novel algorithm or globally
optimal fine-tuning. Read the [prospective protocol](research/lab_tiers/PROTOCOL.md)
and frozen JSON matrix before interpreting a winner.
