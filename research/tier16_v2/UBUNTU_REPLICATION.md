# Ubuntu 16 GB replication

This launcher repeats the original sealed Linux 16 GB study
on the same 160 FinQA questions from 50 reports. It runs both
deployment recipes under the primary, direct-control, and repair
profiles. The earlier resource-failed results and the Windows
8 GB planner study are separate evidence. The new run uses a new
ID and does not import their outputs.

## Completion recorded 11 November 2026

All six jobs and replay audit are complete. See [completion and preservation](UBUNTU_COMPLETION.md) for results, resource scope and the separately verified repository handoff. The original SSD portable-export completion is not confirmed because of filesystem errors. The instructions below describe launching/resuming evaluation.

## Run

In the Ubuntu checkout on `main`, connect the AGERE SSD, close
other apps, and run:

```bash
git pull --ff-only origin main && bash scripts/lab_tiers_ubuntu16.sh
```

The launcher searches the usual Ubuntu mount directories. If
auto-detection is ambiguous, pass the full AGERE directory as
the argument. For example:

```bash
bash scripts/lab_tiers_ubuntu16.sh "/run/media/$USER/Data/AGERE"
```

Run as the logged-in desktop user. Keep the terminal session
open, the computer awake, and the SSD connected. A systemd user
scope must expose the cgroup v2 swap controller. The launcher
verifies that the effective `memory.swap.max` and current swap
usage are zero for that scope before inference. This sets no
system-wide swap policy. The original runner checks sampled
controller-plus-worker RSS against 11.5 GB, stops on observed
process swap, and requires at least 12.5 GB available before
model load. [systemd swap control](https://freedesktop.org/software/systemd/man/latest/systemd.resource-control.html)

The workflow verifies the SSD archive and stages its sealed
code and pinned runtime on the Ubuntu filesystem. It runs input
preflight, the six sequential jobs, the automatic replay audit,
the paired report-cluster analysis, and the portable export.
No additional model or package downloads are needed.

Results are relative to the mounted AGERE directory:

- `runs/lab_tiers_v1/lab-16-ubuntu-noswap-v1/workflow.log`
- `runs/lab_tiers_v1/lab-16-ubuntu-noswap-v1/analysis/summary.json`
- `runs/lab_tiers_v1/lab-16-ubuntu-noswap-v1/ubuntu-scopes/`
- `runs/lab_tiers_v1/exports/lab-16-ubuntu-noswap-v1-results.tar.gz`

After an ordinary interruption, repeat the same launcher command
to resume the saved prefix. The original runner rejects a resume
after a recorded memory or swap breach. In that case, preserve
the logs and start a separate run only after resolving the failure.

## Startup and resume diagnostics

The launcher prints progress every 30 seconds, including model file-read
positions during checksums. Reading a 9 GB model over USB 2.0 can take several
minutes; `Verify model SHA256` followed by increasing read positions is work
in progress. Subsequent stages can verify the models again. Stale historical
samples are labelled as stale, not shown as a live worker.

A one-page physical-RAM reporting difference after reboot is audited with a
backup of the prior manifest and fresh preflight. Other guarded runtime
identity changes or larger RAM changes are still rejected. Completed cases
remain checkpoints; an interrupted case restarts.

`Input/output error` is a storage failure, not slow inference. Stop and
resolve the SSD/cable/port/filesystem issue before resuming. If the mounted
path does not exist, check the actual mount; do not create a replacement
folder. The preservation addendum documents the NTFS errors observed in
this run and the artifacts that could not be read. No repair or force-mount
is performed by the launcher.
