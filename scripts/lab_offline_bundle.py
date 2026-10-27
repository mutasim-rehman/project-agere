"""Copy the already-installed CPU runtime to the SSD; never download/install.

The matching ELF loader/system libraries isolate native extensions from the lab
PC's older glibc. The shell launcher copies this immutable bundle onto the host
before executing it, allowing an SSD mounted noexec.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def build(ssd):
    if sys.platform != 'linux' or os.uname().machine != 'x86_64':
        raise ValueError('Bundle construction requires the working Linux x86_64 runtime')
    out = ssd / 'runtime/agere-cpu-v2'
    if out.exists():
        raise ValueError('Refuse runtime overwrite')
    source = Path(sys.base_prefix)
    if not source.is_relative_to(ROOT / '.local/python'):
        raise ValueError('Use the existing project standalone Python')
    out.mkdir(parents=True)
    shutil.copytree(source, out / 'python', symlinks=False,
        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    site = out / 'site-packages'
    site.mkdir()
    packages = ['llama-cpp-python', 'numpy', 'diskcache', 'jinja2', 'markupsafe', 'psutil', 'typing_extensions']
    versions = {}
    for name in packages:
        distribution = importlib.metadata.distribution(name)
        versions[name] = distribution.version
        # Copy only package roots named by the distribution, including vendored
        # native libraries and license metadata; never copy a whole training env.
        roots = {str(f).split('/')[0] for f in distribution.files or []
            if not str(f).startswith(('../', '/'))}
        for item in roots:
            src = Path(distribution.locate_file(item))
            dst = site / item
            if dst.exists():
                continue
            if src.is_dir():
                shutil.copytree(src, dst, symlinks=False,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            elif src.is_file():
                shutil.copy2(src, dst)
    cpu_libs = ROOT / '.local/lab-cpu-build/bin'
    if not (cpu_libs / 'libllama.so').is_file():
        raise ValueError('Build the cached-source portable AVX2 runtime first')
    cpu_overrides = {}
    for src in cpu_libs.glob('*.so*'):
        if src.is_file():
            dst = site / 'llama_cpp/lib' / src.name
            shutil.copyfile(src, dst)
            cpu_overrides[src.name] = sha(src)
    libraries = out / 'syslib'
    libraries.mkdir()
    origins = {}
    candidates = [out / 'python/bin/python3.12', *out.glob('site-packages/**/*.so*'),
        *out.glob('python/lib/python3.12/lib-dynload/*.so')]
    for candidate in candidates:
        if not candidate.is_file():
            continue
        report = subprocess.run(['ldd', str(candidate)], capture_output=True, text=True)
        if 'not found' in report.stdout:
            raise ValueError('An installed runtime dependency is unavailable: ' + report.stdout)
        for line in report.stdout.splitlines():
            match = re.search(r'(?:=>\s+)?(/[^\s]+)', line)
            if not match:
                continue
            src = Path(match[1])
            if not src.is_file() or src.is_relative_to(out):
                continue
            dst = libraries / src.name
            if dst.exists() and sha(dst) != sha(src):
                raise ValueError('Conflicting native library: ' + src.name)
            if not dst.exists():
                shutil.copy2(src, dst)
                origins[src.name] = {'source': str(src), 'sha256': sha(src)}
    loader = libraries / 'ld-linux-x86-64.so.2'
    if not loader.exists():
        raise ValueError('Matching ELF loader not found')
    license_dir = out / 'licenses'
    license_dir.mkdir()
    for package in ['libc6', 'libstdc++6', 'libgcc-s1', 'libgomp1']:
        copyright_file = Path('/usr/share/doc') / package / 'copyright'
        if copyright_file.is_file():
            shutil.copy2(copyright_file, license_dir / (package + '-copyright'))
    launcher = out / 'python.sh'
    launcher.write_text('''#!/usr/bin/env bash
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONHOME="$here/python"
export PYTHONPATH="$here/site-packages"
export PYTHONNOUSERSITE=1
export PYTHONDONTWRITEBYTECODE=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export AGERE_PYTHON_LAUNCHER="$here/python.sh"
export AGERE_RUNTIME_ROOT="$here"
exec "$here/syslib/ld-linux-x86-64.so.2" --library-path "$here/syslib:$here/site-packages/llama_cpp/lib" "$here/python/bin/python3.12" "$@"
''')
    launcher.chmod(0o755)
    manifest = {'kind': 'offline-existing-runtime-copy-v1', 'platform': 'Linux-x86_64',
        'python': sys.version, 'packages': versions, 'system_library_origins': origins,
        'downloads': 0, 'package_installs': 0, 'portable_cpu_libraries': cpu_overrides,
        'cpu_build': 'Cached llama-cpp-python0.3.16 vendor source; GGML_NATIVE=OFF, AVX2/F16C/FMA/BMI2/SSE4.2; AVX512/CUDA=OFF.',
        'files': {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*')) if p.is_file()}}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    with (out / 'SHA256SUMS').open('w') as f:
        for p in sorted(out.rglob('*')):
            if p.is_file() and p.name != 'SHA256SUMS':
                f.write(sha(p) + '  ' + str(p.relative_to(out)) + '\n')
    pin = {'bundle_relative': str(out.relative_to(ssd)), 'manifest_sha256': sha(out / 'manifest.json'),
        'checksums_sha256': sha(out / 'SHA256SUMS'), 'platform': 'Linux-x86_64',
        'packages': versions}
    target = ROOT / 'configs/lab_tiers/runtime_pin.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise ValueError('Refuse committed runtime pin overwrite')
    target.write_text(json.dumps(pin, indent=2) + '\n')
    print(json.dumps({'bundle': str(out), 'pin': str(target), 'files': len(manifest['files']),
        'bytes': sum(p.stat().st_size for p in out.rglob('*') if p.is_file())}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ssd', required=True)
    args = p.parse_args()
    root = Path(args.ssd).resolve(strict=True)
    if not (root / 'datasets').is_dir() or not (root / 'weights').is_dir():
        p.error('Expected existing AGERE SSD')
    build(root)
