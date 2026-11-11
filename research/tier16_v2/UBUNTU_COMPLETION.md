# Ubuntu 16 GB replication: completion and preservation

Recorded 11 November 2026. Run ID: `lab-16-ubuntu-noswap-v1`.

All six 160-case jobs completed: **960 case outputs on the same 160 questions
from 50 reports**. The saved controller state records `status=complete` and
`analysis_status=complete`; the saved analysis records `complete_audited`.
This replication is separate from `lab-16-115gb-recovery-02` and does not import
its case checkpoints. Historical recovery results and their resource failures
remain preserved. No 32 GB experiment has been added.

## Results

C / W / H means correct delivered / wrong delivered / withheld. Each row has
160 cases. Hours are summed inference measurements for checkpointed cases,
not wall-clock duration, restart overhead, or aborted work. GB is decimal.

| Profile / arm | Reported C / W / H | Raw C / W / H | Inference hours | Peak sampled RSS GB |
| --- | --- | --- | ---: | ---: |
| Primary / SAS | 78 / 48 / 34 | 38 / 88 / 34 | 11.668 | 10.075 |
| Primary / MAS | 5 / 3 / 152 | 5 / 3 / 152 | 3.383 | 10.946 |
| Direct control / SAS | 50 / 66 / 44 | 14 / 102 / 44 | 5.314 | 10.070 |
| Direct control / MAS | 0 / 5 / 155 | 0 / 5 / 155 | 0.897 | 10.934 |
| Repair ablation / SAS | 79 / 50 / 31 | 38 / 91 / 31 | 13.598 | 10.087 |
| Repair ablation / MAS | 5 / 3 / 152 | 5 / 3 / 152 | 3.781 | 10.946 |

Delivered flags and final score objects agree with the earlier preserved
recovery run for all 960 paired rows. This does not imply identical text,
latency or resource traces. The primary correctness/withholding trade-off is
unchanged; the result does not establish MAS superiority or equivalence.
The additional run does not add unique questions: do not pool its repeated
case outputs with the historical run as independent statistical observations.

## Runtime and resource interpretation

The sealed protocol uses CPU-only Qwen2.5-14B Q4_K_M SAS versus resident
1.5B/3B/0.5B F16 MAS, context 4096, eight threads, seed 42, greedy decoding,
and an 11.5 GB sampled controller-plus-worker RSS ceiling. Models, prompts,
precision and token budgets were not tuned for this replication.

The 16 retained worker attempts contain no recorded memory/swap breach;
Ubuntu scope records report `swap_max=0`. Peak sampled RSS is 10.946 GB.
The run resumed across interruptions and experienced SSD disconnections.
It is not one uninterrupted execution, a worst-case memory bound, or a
hardware/deployment reliability certification. Historical swap failures in
the earlier recovery run remain invalid; the new run does not erase them.

The launcher now displays startup model-file read positions and ongoing
checkpoint/resource progress. A stale sample is explicitly marked as stale.
A one-page Linux usable-RAM reporting change across reboot can be reconciled
only when the other guarded runtime identity fields match; the original
manifest and fresh preflight are retained under `resume-metadata-audit/`.

## Preservation and the SSD filesystem issue

The SSD Data partition was mounted read-only for preservation after Linux
reported NTFS metadata errors. All six case files, summaries, manifests,
sampled memory traces, stage traces, attempt states, frozen code and readable
bootstrap/preflight/scope/workflow logs have been copied into the handoff.
Model tensors and executable runtime installations remain excluded, as in
the previous handoff. Runtime identity/configuration and readable bootstrap
logs are retained.

Seven analysis files were unreadable through the SSD filesystem. The six
replay JSONL files were reconstructed locally using the archived sealed
analysis code, the pinned llama_cpp 0.3.16 vocabulary-only tokenizers, and
saved traces. **All six reconstructed replay hashes and all 40 analysis
evidence hashes match the original audit; the entire regenerated analysis
summary also matches the original bytes.** Frozen source and manifest hashes
were checked. No generation calls were made and model tensors were not
rehashed during this reconstruction. `analysis/REPORT.md` was regenerated
by the same analysis code; it has no recorded original report hash.

Two original artifacts remain unavailable:

- `runs/lab_tiers_v1/exports/lab-16-ubuntu-noswap-v1-results.tar.gz`
- `runs/lab_tiers_v1/bootstrap/20261111T133310Z-28590.log`

Only the export's temporary checksum sidecar is readable. The workflow
marker still says `RUNNING`; it is preserved verbatim. Therefore evaluation
and replay are complete, while successful completion of the original SSD
packaging step is **not confirmed**. The repository handoff ZIPs are separately
verified and provide the portable evidence without requiring that tarball.
No SSD repair, force mount, or modification of its original artifacts was
performed. See the machine-readable
[preservation record](../../dashboard_handoff/data/tier16_ubuntu/preservation.json)
for exact paths, hashes and qualifications.

## Dashboard use and restoration

Use [the updated handoff](../../dashboard_handoff/README.md) and its
[catalog](../../dashboard_handoff/data/index.json). The seven new JSON inputs
are under `data/tier16_ubuntu/`: case outcomes, job summaries, stage metrics,
attempt/resource records, the audited analysis, manifest and preservation
record. Every case includes `run_id`; use `(run_id, tier, job, case_id)` as
the key. Stage metrics contain per-call timing/token fields; complete prompt
and response traces remain in the evidence archives.

The original `data/tier16_v2/`, `data/le16_v2/`, and `data/paper/` snapshots
are unchanged. No manuscript, research-paper figures, paper data or PDFs
were regenerated. Existing statistical PDFs still describe the historical
run; use this addendum for the Ubuntu runtime/resource measurements.

From the repository root, with standard-library Python:

```bash
python3 dashboard_handoff/restore_evidence.py
python3 dashboard_handoff/restore_evidence.py --extract restored_agere
```

The first command verifies archive and per-source SHA256 hashes. The second
restores original relative paths, including deduplicated content. No SSD,
model download, inference runtime or API key is required for dashboard work.
Reconstructed replay files are marked in `source_inventory.json`; the
missing original tarball is not claimed to have been restored.
