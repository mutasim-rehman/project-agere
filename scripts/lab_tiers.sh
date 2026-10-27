#!/usr/bin/env bash
# Ubuntu/Linux x86_64. No pip/apt/model downloads; all evidence stays on SSD.
set -euo pipefail
repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${AGERE_SSD_ROOT:-}" ]]; then
    candidates=()
    while IFS= read -r location; do
        [[ -d "$location/weights" && -d "$location/datasets" ]] && candidates+=("$location")
    done < <(find "/media/${USER}" "/run/media/${USER}" -maxdepth 3 -type d -name AGERE 2>/dev/null || true)
    if [[ ${#candidates[@]} -ne 1 ]]; then
        echo 'Set AGERE_SSD_ROOT to the mounted AGERE folder, then repeat this command.' >&2
        printf 'Detected: %s\n' "${candidates[@]:-none}" >&2
        exit 2
    fi
    export AGERE_SSD_ROOT="${candidates[0]}"
fi
ssd="$(cd -- "$AGERE_SSD_ROOT" && pwd)"
export AGERE_SSD_ROOT="$ssd"
mkdir -p "$ssd/runs/lab_tiers_v1/bootstrap"
log="$ssd/runs/lab_tiers_v1/bootstrap/$(date -u +%Y%m%dT%H%M%SZ)-$$.log"
exec > >(tee -a "$log") 2>&1
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { echo 'This bundle requires Linux x86_64.'; exit 2; }
[[ -d "$ssd/weights" && -d "$ssd/datasets" ]] || { echo 'Not the AGERE SSD.'; exit 2; }
bundle="$ssd/runtime/agere-cpu-v2"
pin="$repo/configs/lab_tiers/runtime_checksums.sha256"
[[ -f "$pin" && -f "$bundle/SHA256SUMS" ]] || { echo 'The prepared offline runtime bundle/pin is missing.'; exit 2; }
(cd -- "$ssd" && sha256sum -c "$pin")
digest="$(sha256sum "$bundle/SHA256SUMS" | cut -d' ' -f1)"
cache="$repo/.local/lab-offline-cpu-v2-${digest:0:12}"
if [[ ! -d "$cache" ]]; then
    mkdir -p "$repo/.local"
    temporary="${cache}.copy-$$"
    trap 'rm -rf -- "$temporary"' EXIT
    mkdir "$temporary"
    cp -a "$bundle/." "$temporary/"
    (cd -- "$temporary" && sha256sum -c SHA256SUMS > /dev/null)
    mv -- "$temporary" "$cache"
    trap - EXIT
fi
[[ "$(sha256sum "$cache/SHA256SUMS" | cut -d' ' -f1)" == "$digest" ]] || { echo 'Host runtime cache pin differs.'; exit 2; }
(cd -- "$cache" && sha256sum -c SHA256SUMS > /dev/null)
chmod u+x "$cache/python.sh" "$cache/syslib/ld-linux-x86-64.so.2" "$cache/python/bin/python3.12"
export AGERE_PYTHON_LAUNCHER="$cache/python.sh"
export AGERE_RUNTIME_ROOT="$cache"
cd -- "$repo"
echo "SSD: $ssd"
echo "Runtime: $cache"
echo "Bootstrap log: $log"
"$cache/python.sh" "$repo/scripts/lab_tiers.py" "$@"
