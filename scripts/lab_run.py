"""Ubuntu bounded jobs and crash evidence. All outputs go to AGERE_SSD_ROOT.

run starts a detached systemd user service; status reads its result. No sudo,
global VM tuning, GPU driver changes, or writes outside the job's cgroup.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from phase2 import GIB, REPO, kill_tree, now, validate_paths, write_json


def membership() -> Path:
    rows = Path('/proc/self/cgroup').read_text().splitlines()
    unified = next((r[3:] for r in rows if r.startswith('0::')), None)
    if unified is None:
        raise RuntimeError('Ubuntu cgroup v2 is required.')
    return Path('/sys/fs/cgroup') / unified.lstrip('/')


def guarded_root() -> Path:
    value = os.environ.get('AGERE_JOB_CGROUP')
    if not value:
        raise RuntimeError('Use scripts/lab_run.py run -- <script> <arguments> on Ubuntu.')
    root = Path(value).resolve(strict=True)
    current = membership().resolve()
    if not root.name.startswith('agere-') or not root.name.endswith('.service'):
        raise RuntimeError('Not an Agere job cgroup.')
    if not current.is_relative_to(root) or (root / 'memory.max').read_text().strip() == 'max':
        raise RuntimeError('Job is not inside its bounded systemd service.')
    if (root / 'memory.swap.max').read_text().strip() != '0':
        raise RuntimeError('Job swap must be disabled, without disabling host swap.')
    return root


def capture_to(command: list[str], output: Path) -> None:
    with output.open('w', encoding='utf-8') as stream:
        try:
            result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                    timeout=25, text=True)
            stream.write(f'\nexit={result.returncode}\n')
        except (OSError, subprocess.TimeoutExpired) as exc:
            stream.write(f'\nUnavailable: {exc}\n')


def diagnostics(directory: Path, ssd: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    commands = {
        'boots': ['journalctl', '--list-boots', '--no-pager'],
        'kernel-current': ['journalctl', '-k', '-b', '0', '-n', '1500', '--no-pager', '-o', 'short-iso'],
        'kernel-previous': ['journalctl', '-k', '-b', '-1', '-n', '1500', '--no-pager', '-o', 'short-iso'],
        'oomd': ['journalctl', '-u', 'systemd-oomd', '-n', '500', '--no-pager', '-o', 'short-iso'],
        'display-manager': ['journalctl', '-u', 'display-manager', '-n', '500', '--no-pager', '-o', 'short-iso'],
        'coredumps': ['coredumpctl', 'list', '--no-pager', '--since', '2 days ago'],
        'gpu': ['nvidia-smi'], 'cpu': ['lscpu'], 'memory': ['free', '-h'],
        'mount': ['findmnt', '-T', str(ssd)], 'usb': ['lsusb', '-t'],
        'disks': ['lsblk', '-o', 'NAME,SIZE,FSTYPE,MOUNTPOINTS,TRAN,MODEL'],
        'temperatures': ['sensors'], 'os': ['uname', '-a'],
    }
    for name, command in commands.items():
        capture_to(command, directory / f'{name}.log')
    print(f'Diagnostic evidence: {directory}', flush=True)


def sample(root: Path, process: subprocess.Popen, ssd: Path, device: int) -> dict:
    import psutil
    ram = psutil.virtual_memory()
    if os.stat(ssd).st_dev != device or not (ssd / 'weights' / 'hf').is_dir():
        raise RuntimeError('SSD is no longer mounted at the validated location.')
    record = {'at_utc': now(), 'host_available_bytes': ram.available,
              'host_total_bytes': ram.total, 'host_swap': psutil.swap_memory()._asdict(),
              'ssd_free_bytes': shutil.disk_usage(ssd).free}
    for name in ('memory.current', 'memory.peak', 'memory.events', 'memory.stat',
                 'memory.pressure', 'io.stat', 'cpu.stat'):
        path = root / name
        if path.exists():
            record[name] = path.read_text().strip()
    record['host_dirty_writeback'] = [r for r in Path('/proc/meminfo').read_text().splitlines()
                                      if r.startswith(('Dirty:', 'Writeback:'))]
    try:
        parent = psutil.Process(process.pid)
        record['process_tree_rss_bytes'] = sum(p.memory_info().rss for p in
                                               [parent, *parent.children(recursive=True)])
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        record['process_tree_rss_bytes'] = None
    return record


def worker(directory: Path, command: list[str]) -> int:
    paths = validate_paths()
    device = os.stat(paths.ssd).st_dev
    # Before spawning any children, move this controller into a leaf. The service
    # root must be empty before enabling its memory controller for child groups.
    root = membership()
    if not root.name.startswith('agere-') or not root.name.endswith('.service'):
        raise RuntimeError('worker must be launched by lab_run run.')
    os.environ['AGERE_JOB_CGROUP'] = str(root)
    guarded_root()
    leaf = root / 'controller'
    leaf.mkdir()
    (leaf / 'cgroup.procs').write_text(str(os.getpid()))
    (root / 'cgroup.subtree_control').write_text('+memory')
    # flock is host-local: avoids concurrent runs even on NTFS/FUSE SSDs.
    import fcntl
    lock_path = REPO / '.local' / 'lab-job.lock'
    lock_path.parent.mkdir(exist_ok=True)
    with lock_path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError('Another Agere lab job is active in this checkout.') from exc
        diagnostics(directory / 'before', paths.ssd)
        reserve = int(os.environ['AGERE_HOST_RESERVE_BYTES'])
        write_json(directory / 'state.json', {'status': 'running', 'started_at_utc': now(),
                    'command': command, 'cgroup': str(root), 'host_reserve_bytes': reserve})
        process = None
        follower = None
        reason = None
        code = 1
        mount_ok = True
        with (directory / 'kernel-live.log').open('a') as kernel_log:
            try:
                follower = subprocess.Popen(['journalctl', '-k', '-f', '-n', '30', '--no-pager',
                                             '-o', 'short-iso'], stdout=kernel_log, stderr=subprocess.STDOUT)
                process = subprocess.Popen(command, cwd=REPO)
                with (directory / 'telemetry.jsonl').open('a', encoding='utf-8') as stream:
                    while True:
                        record = sample(root, process, paths.ssd, device)
                        stream.write(json.dumps(record) + '\n')
                        stream.flush()
                        os.fsync(stream.fileno())
                        if record['host_available_bytes'] < reserve:
                            reason = 'Host available RAM fell below the reserved headroom.'
                        if record['ssd_free_bytes'] < 2 * GIB:
                            reason = 'SSD free space fell below 2 GiB.'
                        if reason:
                            kill_tree(process)
                        if process.poll() is not None:
                            code = process.wait()
                            break
                        time.sleep(1)
            finally:
                if process is not None and process.poll() is None:
                    kill_tree(process)
                    process.wait()
                if follower is not None:
                    follower.terminate()
                    follower.wait(timeout=10)
                try:
                    mount_ok = (os.stat(paths.ssd).st_dev == device and
                                (paths.ssd / 'weights' / 'hf').is_dir())
                except OSError:
                    mount_ok = False
                if mount_ok:
                    write_json(directory / 'state.json', {
                        'status': 'completed' if code == 0 and reason is None else 'failed',
                        'finished_at_utc': now(), 'returncode': code, 'safety_stop': reason,
                        'memory_events': (root / 'memory.events').read_text()})
                    diagnostics(directory / 'after', paths.ssd)
                else:
                    print('SSD unmounted: stopping without writing cleanup artifacts to the host mountpoint.',
                          file=sys.stderr, flush=True)
        return code if code > 0 else (1 if code < 0 or reason else 0)


def start(paths, script_args: list[str], reserve_gib: float, max_gib: float | None) -> int:
    import psutil
    if not script_args:
        raise RuntimeError('Supply a script and arguments after --.')
    script = (REPO / 'scripts' / script_args[0]).resolve()
    allowed = {'phase2.py', 'eval_checkpoints.py', 'phase3.py'}
    if script.parent != REPO / 'scripts' or script.name not in allowed:
        raise RuntimeError(f'Choose one of {sorted(allowed)}.')
    ram = psutil.virtual_memory()
    reserve = int(reserve_gib * GIB)
    cap = min(int(ram.total * .8), ram.available - reserve - GIB)
    if max_gib is not None:
        cap = min(cap, int(max_gib * GIB))
    if cap < 2 * GIB:
        raise RuntimeError('Less than 2 GiB usable job memory after reserving host headroom.')
    unit = f'agere-{time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())}-{os.getpid()}'
    directory = paths.ssd / 'runs' / 'lab_jobs' / unit
    directory.mkdir(parents=True)
    command = [sys.executable, '-u', str(script), *script_args[1:]]
    write_json(directory / 'launch.json', {'at_utc': now(), 'unit': unit + '.service',
               'command': command, 'job_memory_max_bytes': cap,
               'host_reserve_bytes': reserve, 'host_total_bytes': ram.total,
               'idle_host_available_bytes': ram.available, 'ssd_root': str(paths.ssd)})
    write_json(directory / 'state.json', {'status': 'starting'})
    args = ['systemd-run', '--user', '--unit', unit, '--expand-environment=no', '--property=Type=exec',
            '--property=Delegate=yes', f'--property=MemoryMax={cap}',
            f'--property=MemoryHigh={int(cap * .9)}', '--property=MemorySwapMax=0',
            '--property=OOMPolicy=kill', '--property=KillMode=control-group',
            '--property=Nice=10',
            f'--property=WorkingDirectory={REPO}',
            f'--property=StandardOutput=append:{directory / "console.log"}',
            '--property=StandardError=inherit',
            f'--setenv=AGERE_SSD_ROOT={paths.ssd}',
            f'--setenv=AGERE_HOST_RESERVE_BYTES={reserve}',
            '--setenv=PYTHONUNBUFFERED=1', '--setenv=OMP_NUM_THREADS=4',
            '--setenv=MKL_NUM_THREADS=4', '--setenv=OPENBLAS_NUM_THREADS=4',
            '--setenv=TOKENIZERS_PARALLELISM=false',
            f'--setenv=TMPDIR={paths.scratch}',
            f'--setenv=HF_HOME={paths.ssd / "weights" / "hub_cache"}',
            sys.executable, '-u', str(Path(__file__).resolve()), 'worker',
            '--directory', str(directory), '--', *command]
    subprocess.run(args, check=True)
    print(f'Job started: {unit}.service; memory ceiling {cap / GIB:.2f} GiB; '
          f'host reserve {reserve_gib:g} GiB. Completion is NOT implied by launch success.')
    print(f'Follow: tail -F "{directory / "console.log"}"')
    print(f'Status: {sys.executable} scripts/lab_run.py status')
    print(f'Stop: systemctl --user stop {unit}.service')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=('run', 'worker', 'diagnose', 'status'))
    parser.add_argument('--reserve-gib', type=float, default=4)
    parser.add_argument('--max-gib', type=float)
    parser.add_argument('--directory', type=Path)
    # Explicit split keeps all child flags out of the launcher's parser.
    argv = sys.argv[1:]
    split = argv.index('--') if '--' in argv else len(argv)
    args = parser.parse_args(argv[:split])
    command = argv[split + 1:]
    if args.reserve_gib < 1 or (args.max_gib is not None and args.max_gib < 2):
        parser.error('Reserve must be >=1 GiB and maximum >=2 GiB.')
    try:
        if sys.platform != 'linux':
            raise RuntimeError('Run this launcher on the Ubuntu lab PC.')
        paths = validate_paths()
        if args.step == 'diagnose':
            diagnostics(paths.ssd / 'runs' / 'lab_diagnostics' / time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()), paths.ssd)
            return 0
        if args.step == 'run':
            return start(paths, command, args.reserve_gib, args.max_gib)
        if args.step == 'worker':
            if not args.directory or not args.directory.resolve().is_relative_to(paths.ssd / 'runs' / 'lab_jobs'):
                raise RuntimeError('Invalid worker output directory.')
            return worker(args.directory, command)
        jobs = sorted((paths.ssd / 'runs' / 'lab_jobs').glob('agere-*'))
        if not jobs:
            raise RuntimeError('No lab jobs found on this SSD.')
        directory = jobs[-1]
        launch = json.loads((directory / 'launch.json').read_text())
        state = json.loads((directory / 'state.json').read_text())
        print(f'{directory}\nRecorded state: {json.dumps(state)}')
        capture_to(['systemctl', '--user', 'show', launch['unit'], '-p', 'ActiveState',
                    '-p', 'SubState', '-p', 'Result', '-p', 'ExecMainStatus', '-p', 'MemoryPeak'],
                   directory / 'systemd-status.log')
        print((directory / 'systemd-status.log').read_text())
        print('If state says running but the unit is failed/missing, execution was interrupted; inspect kernel logs.')
        return 0
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
