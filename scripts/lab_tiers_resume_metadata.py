"""Audit a one-page Linux usable-RAM reporting variation before sealed resume."""
import json
import os
from pathlib import Path
import time


def reconcile(out, report):
    manifest_path = out / 'manifest.json'
    if not manifest_path.exists():
        return False
    original = manifest_path.read_bytes()
    manifest = json.loads(original)
    previous = manifest['environment']
    preflight = json.loads(report.read_text())
    current = preflight['environment']
    keys = ('python', 'llama_cpp', 'numpy', 'psutil', 'cpu_runtime',
            'runtime_manifest_sha256', 'cpu_model', 'host_id_sha256')
    if preflight['status'] != 'passed' or any(previous[k] != current[k] for k in keys):
        raise ValueError('Runtime identity differs; RAM metadata reconciliation refused')
    old, new = previous['physical_ram_bytes'], current['physical_ram_bytes']
    if old == new:
        return False
    page = os.sysconf('SC_PAGE_SIZE')
    if abs(new - old) != page:
        raise ValueError('RAM changed by more than one page; reconciliation refused')
    actual = int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines()
                      if line.startswith('MemTotal:'))) * 1024
    if actual != new:
        raise ValueError('Preflight RAM differs from this host; reconciliation refused')
    audit = out / 'resume-metadata-audit' / str(time.time_ns())
    audit.mkdir(parents=True)
    (audit / 'manifest-before.json').write_bytes(original)
    (audit / 'preflight.json').write_bytes(report.read_bytes())
    (audit / 'change.json').write_text(json.dumps({
        'field': 'environment.physical_ram_bytes', 'before': old, 'after': new,
        'reason': 'One-page Linux usable-RAM reporting variation; runtime identity matches',
        'time': time.time()}, indent=2) + '\n')
    previous['physical_ram_bytes'] = new
    temporary = out / 'manifest-resume-metadata.tmp'
    temporary.write_text(json.dumps(manifest, indent=2) + '\n')
    temporary.replace(manifest_path)
    print(f'Reconciled one-page RAM report variation ({old} -> {new}); audit: {audit}', flush=True)
    return True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('preflight_report', type=Path)
    args = parser.parse_args()
    reconcile(args.run_dir, args.preflight_report)
