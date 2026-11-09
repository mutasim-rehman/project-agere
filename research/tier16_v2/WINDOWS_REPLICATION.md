# Native Windows replication of the sealed 16 GB study

This run reuses the original 160 FinQA packets from 50 company-year
reports, the archived inference code and the exact SSD model files.
It compares the 14B Q4 monolith with the resident 1.5B/3B/0.5B F16
team. It runs the primary profile first, then the direct control
and repair ablation, with both arms in each profile. There are 960
outputs on 160 unique questions. The Windows host and llama.cpp
Python binding differ from the original Linux runtime. This is a
cross-platform replication on the same cohort. The 8 GB planning
experiments remain a separate study.

## Run from standalone PowerShell

Connect the SSD as `H:`, close other apps including Codex, and
keep the laptop plugged in and awake. Run this in PowerShell:

```powershell
& 'D:\project-agere\.venv\Scripts\python.exe' -X utf8 'D:\project-agere\.local\paper-submission-main\scripts\lab_tiers_windows.py' --ssd 'H:\AGERE'
```

The runner first checks the archived protocol, code, cohort,
demonstrations, scoring source and all four GGUF hashes. It then
loads one recipe at a time, saves every completed case, and replays
the completed output traces to verify prompts, tokens, execution,
review and scores. The final summary includes correct, wrong and
withheld outcomes, paired case transitions and 10,000-resample
report-cluster bootstrap intervals. The same command can resume
after Ctrl+C using the saved, monitored prefix. Failed or
unverified attempts stay on disk and are excluded from scoring.

Output is under `H:\AGERE\runs\windows_tier16\windows16-replication-v1`.
Use `summary.json` for the paper analysis, `manifest.json` for runtime
and provenance, and the per-attempt files for raw outputs and
resource traces. Use `--preflight-only` to check the inputs, runtime,
and current headroom without loading model weights.

## Resource interpretation

Both recipes use CPU inference, 4,096 context, eight threads, a
2,048-token output cap and non-memory-mapped model loads. The
controller requires 12.0 GB of host-available RAM before model
load. Each worker job has an 11.5 GB commit limit. The controller
also checks combined working set against 11.5 GB and stops the run
if system available memory falls below 0.5 GB. Working-set and
available-memory samples are taken roughly every 200 ms.

The run records system-wide pages input and output rates, plus
pagefile configuration and usage before and after the workload.
These measurements help identify host memory pressure. They do
not attribute paging to a model process or prove an uninterrupted
no-paging run. The summary records that qualification separately
from the accuracy audit.
[Microsoft Windows memory counters](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/how-to-determine-the-appropriate-page-file-size-for-64-bit-versions-of-windows)
