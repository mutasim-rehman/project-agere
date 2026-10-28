# Ubuntu lab run: 16 GB and 32 GB, entirely offline after git pull

The8GB prompt checks and closure audits are complete. The portable runtime and
real SAS/MAS workflow smoke tests passed on28 October2026, including saved-response
replay. The sealed handoff includes `configs/lab_tiers/freeze.json`; code/input
hashes are enforced before evaluation. Actual14B/32B accuracy and full-tier fit
are evaluated by the tier runs, not established by the small engineering tests.

Revision v2 follows the user's11.5GB application budget. Real neutral long-input
probes at context4096 observed peaks9.98GB for14B-Q4 SAS and10.85GB for resident
1.5B/3B/0.5B-F16 MAS, with no process swap. Original weights are unchanged; common
context is reduced from8192 to4096 for both arms and tiers. The prior8192 probes
and their swap failures remain on SSD. This is measured engineering fit, not
full-benchmark/worst-case/product validation. Pinned sample hashes/limits are in
`configs/lab_tiers/memory_fit.json` and the original traces stay on SSD.

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
bash scripts/lab_tiers.sh status --run-id lab-main-v2
tail -F "$AGERE_SSD_ROOT/runs/lab_tiers_v1/lab-main-v2/console.log"
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

For this laptop, launch only16GB, including preflight, all six evaluations,
automatic final analysis and result archive:

```bash
(
  set -euo pipefail
  cd /home/mutasim/Desktop/project-agere
  export AGERE_SSD_ROOT="/run/media/mutasim/Data/AGERE"
  AGERE_LAB_TIERS=16 AGERE_LAB_RUN_ID=lab-16-115gb-v2 bash scripts/lab_tiers_all.sh
)
```

Live console and per-case worker output, refreshing every5 seconds:

```bash
watch -n 5 'tail -n 8 /run/media/mutasim/Data/AGERE/runs/lab_tiers_v1/lab-16-115gb-v2/console.log; tail -n 5 /run/media/mutasim/Data/AGERE/runs/lab_tiers_v1/lab-16-115gb-v2/tier16-*/attempt-*/worker.log 2>/dev/null'
```

Ctrl+C exits the viewer only. This15.4GB physical host is eligible for the nominal
16GB tier. Revision v2 fixes **application tree RSS at at most11.5 decimal GB**
for every16GB arm/profile, including controller overhead. There is a separate1GB
host reserve: start with12.5GB available RAM, while application usage stays below
11.5GB. Close unused applications to provide that reserve. The monitor records
actual fit/failure; sampled RSS does not guarantee a hard bound between samples.
Old run IDs and higher-cap failures remain intact; use the new v2 run ID shown
above. The common context is4096 for both systems and tiers; original F16 MAS/Q4 SAS
weights are retained. The laptop cannot run the32GB tier.

## Results for later inspection

After all jobs, the controller automatically runs a vocabulary-only full replay
audit and writes `analysis/REPORT.md` plus machine-readable comparisons. Check
that status reports both evaluation and analysis complete. To re-audit or create
a portable archive after the controller exits:

```bash
bash scripts/lab_tiers.sh analyze --run-id lab-main-v2
bash scripts/lab_tiers.sh export --run-id lab-main-v2
```

The export is under `AGERE/runs/lab_tiers_v1/exports/`. Bring back the SSD, or copy
that `.tar.gz` and its checksum. It contains raw model responses, prompts, usage,
scores, stage traces, memory samples, failed/interrupted attempts, frozen code,
input/scoring data and manifests. Model/runtime payloads are excluded from the
archive; retain them on SSD for independent token replay. No upload is automatic.

```text
AGERE/runs/lab_tiers_v1/lab-main-v2/
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
The16GB application ceiling is fixed11.5GB; the32GB ceiling is25.6GB and may be
lowered by insufficient available host RAM. The exact paired cap is recorded.
No swapping or silently substituted
smaller model is accepted. Sampling is every0.2s; this is not a hard-cgroup claim.

The main comparison uses PRETRAINED checkpoints in both arms. Existing trained7B
adapters do not match14B/32B; they are not silently reused. This is numerical
financial QA, not proof of KYC/credit safety, a novel algorithm or globally
optimal fine-tuning. Read the [prospective protocol](research/lab_tiers/PROTOCOL.md)
and frozen JSON matrix before interpreting a winner.
