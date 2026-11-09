#!/usr/bin/env bash
# Re-run the sealed 16 GB protocol in a fresh Ubuntu no-swap scope.
set -euo pipefail

fail() { printf '%s\n' "$*" >&2; exit 1; }
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] ||
    fail 'Run this from an Ubuntu x86_64 desktop session.'

mode=launch
if [[ "${1:-}" == --worker ]]; then
    mode=worker
    shift
fi
(( $# <= 1 )) || fail 'Usage: bash scripts/lab_tiers_ubuntu16.sh [mounted AGERE folder]'
ssd="${1:-${AGERE_SSD_ROOT:-}}"
if [[ -z "$ssd" ]]; then
    candidates=()
    while IFS= read -r candidate; do
        [[ -d "$candidate/weights" && -d "$candidate/datasets" ]] || continue
        candidates+=("$(realpath -- "$candidate")")
    done < <(find "/media/$USER" "/run/media/$USER" -maxdepth 3 -type d -name AGERE 2>/dev/null || true)
    mapfile -t candidates < <(printf '%s\n' "${candidates[@]}" | sort -u)
    [[ ${#candidates[@]} == 1 && -n "${candidates[0]}" ]] ||
        fail 'Pass the mounted AGERE folder as the argument, e.g. "/media/$USER/Data/AGERE".'
    ssd="${candidates[0]}"
fi
ssd="$(realpath -e -- "$ssd")"
[[ -d "$ssd/weights" && -d "$ssd/datasets" ]] || fail "Not the AGERE SSD: $ssd"

if [[ "$mode" == launch ]]; then
    [[ -f /sys/fs/cgroup/cgroup.controllers ]] || fail 'The run requires cgroup v2.'
    exec systemd-run --user --scope --collect --property=MemorySwapMax=0 \
        bash "$(realpath -- "${BASH_SOURCE[0]}")" --worker "$ssd"
fi

identifier="${AGERE_LAB_RUN_ID:-lab-16-ubuntu-noswap-v1}"
[[ "$identifier" =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$ ]] || fail 'Invalid run ID.'
out="$ssd/runs/lab_tiers_v1/$identifier"
archive="$ssd/runs/lab_tiers_v1/exports/$identifier-results.tar.gz"
group="$(sed -n 's/^0:://p' /proc/self/cgroup)"
[[ -n "$group" && "$group" != / ]] || fail 'No isolated cgroup v2 scope.'
cgroup="/sys/fs/cgroup$group"
check_swap() {
    [[ -r "$cgroup/memory.swap.max" && -r "$cgroup/memory.swap.current" ]] ||
        fail 'The user scope has no accessible memory swap controller.'
    [[ "$(cat "$cgroup/memory.swap.max")" == 0 && "$(cat "$cgroup/memory.swap.current")" == 0 ]] ||
        fail 'Kernel did not enforce a zero-swap scope. Stopping.'
}
check_swap
mkdir -p -- "$out"
exec 8>"$ssd/runs/lab_tiers_v1/ubuntu16.lock"
flock -n 8 || fail 'An Ubuntu 16 GB workflow is already active on this SSD.'
exec 9>"$out/workflow.lock"
flock -n 9 || fail "This run is already active: $out/workflow.log"
if [[ -f "$archive" && -f "$archive.sha256.json" && -f "$out/workflow-status.txt" ]] &&
   grep -q '^COMPLETE ' "$out/workflow-status.txt"; then
    printf 'Already complete: %s\n' "$archive"
    exit 0
fi
[[ ! -e "$archive" ]] || fail "Preserve the existing export before retrying: $archive"
[[ ! -e "$out/continuation.json" ]] || fail 'Use a fresh run ID for the Ubuntu replication.'
if [[ -e "$out/manifest.json" && ! -d "$out/ubuntu-scopes" ]]; then
    fail 'This run ID was created outside the Ubuntu launcher. Use a fresh run ID.'
fi

exec > >(tee -a "$out/workflow.log") 2>&1
mkdir -p -- "$out/ubuntu-scopes"
scope_log="$(mktemp "$out/ubuntu-scopes/attempt-XXXXXXXX")"
record_scope() {
    printf '%s utc=%s cgroup=%s swap_max=%s swap_current=%s\n' "$1" "$(date -u +%FT%TZ)" \
        "$group" "$(cat "$cgroup/memory.swap.max")" "$(cat "$cgroup/memory.swap.current")" >> "$scope_log"
}
record_scope start
trap 'rc=$?; if (( rc != 0 )); then record_scope failed || true; printf "FAILED exit=%s at %s\n" "$rc" "$(date -u +%FT%TZ)" > "$out/workflow-status.txt"; fi' EXIT
printf 'RUNNING since %s\n' "$(date -u +%FT%TZ)" > "$out/workflow-status.txt"

# Stage the original sealed code on the Ubuntu filesystem. The live checkout
# contains later research edits and cannot serve as the old freeze.
code="$(python3 - "$ssd" "${XDG_CACHE_HOME:-$HOME/.cache}" <<'PY'
import hashlib
import json
from pathlib import Path
import shutil
import sys

ssd, cache = map(Path, sys.argv[1:])
source = ssd / "runs/lab_tiers_v1/lab-16-115gb-recovery-02"
raw = (source / "manifest.json").read_bytes()
digest = hashlib.sha256(raw).hexdigest()
if digest != "2bc2c447e1e2c09fde8883077105b74f52b847bbe80ad121b3b53303095c3ac8":
    raise SystemExit("Archived 16 GB manifest checksum differs")
freeze = json.loads(raw)["freeze"]
code = cache / "agere" / ("sealed-lab-" + digest[:16])
for name, expected in freeze["code_sha256"].items():
    original = source / "code" / name
    target = code / name
    if hashlib.sha256(original.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"Archived code checksum differs: {name}")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
    if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"Local sealed code checksum differs: {target}")
(code / "configs/lab_tiers/freeze.json").write_text(json.dumps(freeze), encoding="utf-8")
print(code.resolve())
PY
)"
export AGERE_SSD_ROOT="$ssd"
check_swap
bash "$code/scripts/lab_tiers.sh" preflight --tiers 16
check_swap
bash "$code/scripts/lab_tiers.sh" run --tiers 16 --run-id "$identifier"
check_swap
record_scope analysis_complete
bash "$code/scripts/lab_tiers.sh" export --tiers 16 --run-id "$identifier"
printf 'COMPLETE at %s\nAnalysis: %s\nArchive: %s\n' "$(date -u +%FT%TZ)" \
    "$out/analysis/summary.json" "$archive" > "$out/workflow-status.txt"
cat "$out/workflow-status.txt"
