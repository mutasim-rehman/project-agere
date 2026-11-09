# Ubuntu 16 GB replication

This launcher repeats the original sealed Linux 16 GB study
on the same 160 FinQA questions from 50 reports. It runs both
deployment recipes under the primary, direct-control, and repair
profiles. The earlier resource-failed results and the Windows
8 GB planner study are separate evidence. The new run uses a new
ID and does not import their outputs.

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
bash scripts/lab_tiers_ubuntu16.sh "/media/$USER/Data/AGERE"
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
