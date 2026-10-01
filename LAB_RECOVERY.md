# Ubuntu lab recovery and bounded runs

## What the September 30 SSD evidence shows

Inspected on the development PC with the SSD at `H:\AGERE`. The lab logs used
`/media/labuser/Data/AGERE`; verify that mount on every PC before running anything.

- First conversion session: `phase2/logs/session_20260930T103108Z_convert.log`.
  The 0.5B converter exited successfully at 11:35:38 UTC. Logging ends just
  after the 1.5B writer announced its output.
- Second session: `phase2/logs/session_20260930T114359Z_convert.log`.
  All source hashes finished at about 12:39:38 UTC. The 0.5B output was reused.
  Logging ends during 1.5B writing, at about 36%, around 12:40:29 UTC.
- The 32B messages were **source-file verification**, before model conversion.
  Neither run reached 32B conversion or quantization.
- The 0.5B GGUF contains all 290 tensor extents: 994,156,512 bytes required and
  present. The 1.5B partial requires 3,093,669,024 bytes but contains only
  1,155,470,496. Structural completeness does not replace a payload checksum.
- No final GGUF manifest, quantized outputs, or smoke results exist. Phase 2
  is incomplete. Midpoint diagnostics and Phase 3 should follow recovery.
- The NTFS SSD had 158,285,168,640 bytes free during inspection (~147.4 GiB).
  The writer reported roughly 36 MB/s. This does not identify the USB link or
  prove an I/O fault; it can be consistent with a slower USB path. Check the
  recorded mount/USB/kernel evidence on Ubuntu and connect directly to a
  reliable port with a known-good cable before resuming.

The user observed a black screen followed by the account chooser, with all
applications closed after login. The later user journal export
`user-session-crash-window.log` records `systemd-oomd` killing processes from
the terminal's VTE scope at both stop times. The scope reached a 26.6 GiB
memory peak at 16:35:43 PKT on the first run and 26.1 GiB at 17:40:29 PKT on
the second; both report 0 bytes of swap peak. At the same timestamps,
`systemd-oomd` killed GNOME Shell and other desktop services, and GNOME's user
session shut down. This matches the black screen and account chooser. The
repeatable cause is severe memory pressure during the terminal workload,
followed by `systemd-oomd` terminating the desktop session. The user journal
does not identify the exact child process or show the kernel's global memory
state, so it cannot establish whether the converter alone, other concurrent
programs, or their combined memory use triggered the pressure. The repeated
1.5B stop is not evidence that the 32B model exhausted RAM; 32B had only been
source-verified, not converted.

## Recovery on the actual lab PC

Reuse the existing Python 3.12 environment and pinned runtime. From the local
repository checkout:

```bash
git pull --ff-only
export AGERE_SSD_ROOT='/media/labuser/Data/AGERE'
findmnt -T "$AGERE_SSD_ROOT"
.venv/bin/python scripts/lab_run.py diagnose
```

`diagnose` copies bounded current/previous kernel journal extracts, boot list,
OOM-daemon and display-manager logs, coredump listings, GPU information,
memory, CPU, temperatures, mount and USB topology into
`$AGERE_SSD_ROOT/runs/lab_diagnostics/`. Missing permissions/tools are recorded
instead of treated as clean evidence. Previous boot logs require journal
retention; logging out without rebooting leaves evidence in the current boot.
Do this before another long run. Share that directory to narrow the cause.

If journal files say access denied, a lab administrator can export the kernel
journal with elevated read privileges. Do not disable the OOM daemon, remove
the display driver, reformat NTFS, or change global swap/VM settings on the
basis of these incomplete logs.

To keep a user service alive across a complete logout, enable lingering once
if the lab permits it (this is a persistent user setting, reversible with
`loginctl disable-linger "$USER"`):

```bash
loginctl enable-linger "$USER"
```

Do not relaunch Phase 2 directly in a GNOME terminal. Run it through
`scripts/lab_run.py`, which launches a detached user service with an aggregate
memory ceiling, host-RAM reserve, and telemetry. This contains a memory-limit
failure to the experiment job instead of allowing terminal pressure to take
down the desktop. Use the current repository version containing that launcher
and wait for its recorded status. If the bounded retry is stopped by its cap,
keep the failed output and telemetry for review; do not raise the cap or
disable `systemd-oomd` on this 32 GB host.

First retry only the interrupted model:

```bash
.venv/bin/python scripts/lab_run.py run -- phase2.py convert --models 1.5b
```

The launcher prints a `tail -F` command for live progress and a `systemctl`
command to stop that exact job. It starts a background service; **returning to
the prompt does not mean conversion completed**. Use:

```bash
.venv/bin/python scripts/lab_run.py status
```

Wait for `Recorded state: completed` before each following job. Each job has
a new directory under `runs/lab_jobs/`, containing `launch.json`,
`console.log`, `telemetry.jsonl`, `kernel-live.log`, before/after diagnostics,
and `state.json`. A stale `running` state plus a failed/missing service means
an interrupted job, not success. Services do not resume automatically after
a reboot. A kernel OOM killing the entire service can prevent a final state
write; inspect `systemd-status.log` and the next `diagnose` export too.

After the 1.5B retry succeeds, complete conversion and then smoke checks:

```bash
.venv/bin/python scripts/lab_run.py run -- phase2.py convert
# Wait for completion and inspect status before starting smoke.
.venv/bin/python scripts/lab_run.py run -- phase2.py smoke --tier all
```

Full conversion rechecks all source hashes, reuses structurally complete
outputs, and publishes the seven-file SHA-256 manifest. A selected-model
recovery hashes only those sources and does not publish an all-tier manifest.
The interrupted `.partial.gguf` for a retried model is restarted; completed
0.5B output is retained. Existing crash logs remain append-only.

After Phase 2 reports complete, run the midpoint diagnostics, then Phase 3,
waiting for each service to finish:

```bash
.venv/bin/python scripts/eval_checkpoints.py setup
.venv/bin/python scripts/lab_run.py run -- eval_checkpoints.py run --tier all --format both --run-id guarded_dev_v1
# Read the result and variant failures before continuing.
.venv/bin/python scripts/lab_run.py run -- phase3.py run --tier all --arm both --run-id guarded_floor_v1
```

## Resource policy for this 32 GB Ubuntu desktop

- All current models run on **CPU**. The recorded runtime installed
  `torch 2.11.0+cpu` and built llama.cpp with CUDA off. An RTX 3080 does not
  expand host RAM or automatically accelerate these commands. Changing the
  inference backend needs a separately recorded protocol/configuration.
- The launcher reserves **4 GiB of available host RAM**, plus 1 GiB of
  launch-time fluctuation room. Its whole-job hard limit is the smaller of
  80% of actual physical RAM and available RAM minus those allowances.
  `--max-gib N` can lower this ceiling. `--reserve-gib N` changes the explicit
  host reserve; keep the default for this recovery.
- Linux `MemoryHigh` is 90% of that ceiling; `MemoryMax` limits the entire
  service including child processes and charged file cache. Job swap is
  disabled; host swap is unchanged. Exceeding the hard limit can kill the
  job. This containment is preferable to allowing the experiment unlimited
  memory, but it cannot prevent unrelated driver/hardware/desktop faults.
- A once-per-second supervisor records RAM, swap, dirty/writeback pages,
  cgroup memory/events/pressure, I/O, and free SSD space. It stops a workload
  if host available RAM drops below the reserve or free SSD space below
  2 GiB. Numerical libraries use at most four threads and service priority
  is lowered. This slows throughput; do not mix resulting timing numbers
  with older settings.
- Model RSS caps remain at most **6.4 / 12.8 / 25.6 GB** for the three tiers.
  They are further limited by measured host headroom and the outer job
  ceiling minus 1 GiB for the runner. File-cache accounting and process RSS
  are different measurements; both are recorded. Phase 3 freezes one model
  cap for both arms of a tier. Use a new run ID after a changed resource setup.
- Conversion and quantization now receive aggregate caps, four numerical
  threads, a 1 GiB llama.cpp quantizer row buffer, and memory watchdogs. Lazy
  conversion remains enabled. The pinned quantizer documents
  `--max-buffer-size` to reduce quantization RAM, at a possible speed cost. The code
  does not load an entire F16 model for inference merely to convert it.
  A 32B conversion may still exceed available memory; a guarded failure
  requires inspection or a larger host, not a claim that every size fits.
- Original HF 14B and 32B F16 **will not fit this conservative 32 GB job
  budget**. Their diagnostic workers fail the memory preflight and continue
  other variants. These are missing reference measurements, never zero
  scores. Complete their paired comparisons on a larger-memory host. The
  32B preflight estimate is 64 GiB for weights/loading overhead alone;
  host reserve and job overhead require additional RAM.
- 32 GB-tier GGUF inference remains conditional on fitting weights, KV
  caches, and workspaces under the measured limit. Lower context for both
  arms and rerun smoke if appropriate, or use a suitable larger host while
  retaining the tier ceiling. Do not silently change model sizes or raise
  caps to obtain a pass.

Only one launcher job per checkout is allowed. Do not run conversion and
evaluation concurrently or start another checkout against the same SSD.
The service is independent of the interactive terminal; lingering controls
logout survival, and no service survives loss of power. All logs and outputs
remain on the SSD; code, environment, builds, and a local concurrency lock stay
on the PC.

Implementation references: [systemd-run v255 documentation](https://github.com/systemd/systemd/blob/v255/man/systemd-run.xml),
[systemd resource controls](https://github.com/systemd/systemd/blob/v255/man/systemd.resource-control.xml),
[Linux cgroup v2 memory accounting and delegation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html).
The Ubuntu systemd/service path needs execution on the lab PC; Windows
inspection cannot establish that the original logout is fixed.
