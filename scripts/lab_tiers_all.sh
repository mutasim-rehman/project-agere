#!/usr/bin/env bash
# One detached workflow: preflight -> both tiers + analysis -> result archive.
set -euo pipefail
repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export AGERE_SSD_ROOT="${AGERE_SSD_ROOT:?Set AGERE_SSD_ROOT to the mounted AGERE folder}"
[[ -d "$AGERE_SSD_ROOT/weights" && -d "$AGERE_SSD_ROOT/datasets" ]] || { echo 'AGERE SSD assets are missing.' >&2; exit 2; }
export AGERE_SSD_ROOT="$(cd -- "$AGERE_SSD_ROOT" && pwd)"
tiers="${AGERE_LAB_TIERS:-16,32}"
identifier="${AGERE_LAB_RUN_ID:-lab-main-v2}"
case "$tiers" in 16|32|16,32|32,16) ;; *) echo 'AGERE_LAB_TIERS must be16,32 or16,32.' >&2; exit 2 ;; esac
[[ "$identifier" =~ ^[A-Za-z0-9][A-Za-z0-9_.-]*$ ]] || { echo 'Invalid lab run ID.' >&2; exit 2; }
export AGERE_LAB_TIERS="$tiers" AGERE_LAB_RUN_ID="$identifier"
out="$AGERE_SSD_ROOT/runs/lab_tiers_v1/$identifier"
mkdir -p "$out"
if [[ "${1:-}" != _worker ]]; then
    if [[ ! -f "$repo/configs/lab_tiers/freeze.json" ]]; then
        echo 'Lab handoff is not sealed yet. The remaining 8GB evaluation and real-model engineering checks must finish first.' | tee -a "$out/workflow-launch-errors.log" >&2
        exit 2
    fi
    command -v flock >/dev/null || { echo 'Required Ubuntu utility flock is unavailable.' >&2; exit 2; }
    exec 9>"$out/workflow.lock"
    if ! flock -n 9; then
        echo "This workflow is already running. Logs: $out/workflow.log"
        exit 0
    fi
    nohup bash "$repo/scripts/lab_tiers_all.sh" _worker </dev/null >>"$out/workflow.log" 2>&1 &
    echo "Started complete workflow, PID $!"
    echo "Logs, progress, analysis and final archive paths: $out/workflow.log"
    echo 'No further command is needed on success. Keep the PC awake and the SSD connected.'
    exit 0
fi
cd -- "$repo"
trap 'rc=$?; printf "FAILED exit=%s at %s; inspect workflow.log and retained attempt logs.\n" "$rc" "$(date -u +%FT%TZ)" > "$out/workflow-status.txt"; exit "$rc"' ERR
printf 'RUNNING since %s\n' "$(date -u +%FT%TZ)" > "$out/workflow-status.txt"
echo "Preflight started: $(date -u +%FT%TZ)"
bash scripts/lab_tiers.sh preflight --tiers "$tiers"
echo "Evaluations and automatic replay analysis started: $(date -u +%FT%TZ)"
bash scripts/lab_tiers.sh run --tiers "$tiers" --run-id "$identifier"
echo "Portable export started: $(date -u +%FT%TZ)"
archive="$AGERE_SSD_ROOT/runs/lab_tiers_v1/exports/$identifier-results.tar.gz"
if [[ -e "$archive" ]]; then
    echo 'A prior export already exists; refusing to overwrite evidence.' >&2
    false
fi
bash scripts/lab_tiers.sh export --run-id "$identifier"
printf 'COMPLETE at %s\nArchive: %s\n' "$(date -u +%FT%TZ)" "$archive" > "$out/workflow-status.txt"
cat "$out/workflow-status.txt"
