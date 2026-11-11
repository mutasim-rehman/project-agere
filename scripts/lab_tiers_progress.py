"""Read-only terminal heartbeat for the sealed lab runner."""
import argparse
import json
from pathlib import Path
import time


def checksum_activity(pid):
    """Inspect file positions without opening or modifying model contents."""
    pending, seen = [pid], set()
    while pending:
        pid = pending.pop()
        if pid in seen:
            continue
        seen.add(pid)
        proc = Path('/proc') / str(pid)
        try:
            pending.extend(int(x) for x in (proc / f'task/{pid}/children').read_text().split())
            for fd in (proc / 'fd').iterdir():
                target = fd.resolve()
                if target.suffix != '.gguf':
                    continue
                info = (proc / 'fdinfo' / fd.name).read_text()
                position = int(next(line.split()[1] for line in info.splitlines() if line.startswith('pos:')))
                size = target.stat().st_size
                if size and position:
                    return (f'Model file read: {target.name} '
                            f'{min(position / size, 1):.0%} '
                            f'({position/1e9:.2f}/{size/1e9:.2f} GB); startup checks may read files repeatedly')
        except (OSError, ValueError, StopIteration):
            continue
    return ''


def read_json(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def tail(path):
    try:
        with path.open('rb') as stream:
            stream.seek(0, 2)
            stream.seek(max(0, stream.tell() - 8192))
            lines = stream.read().splitlines()
        return lines[-1].decode(errors='replace') if lines else ''
    except OSError:
        return ''


def snapshot(out):
    states = list(out.glob('tier*/attempt-*/state.json'))
    if not states:
        return 'Waiting for sealed runner startup / input verification'
    path = max(states, key=lambda p: p.stat().st_mtime_ns)
    state = read_json(path)
    attempt = path.parent
    progress = read_json(attempt / 'progress.json')
    manifest = read_json(attempt.parent / 'manifest.json')
    completed = progress.get('completed', state.get('completed_before', 0))
    expected = manifest.get('dataset', {}).get('n', '?')
    memory = {}
    try:
        memory = json.loads(tail(attempt / 'memory.jsonl'))
    except ValueError:
        pass
    rss = memory.get('tree_rss_bytes', 0) / 1e9
    sample_time = memory.get('time')
    age = f'{max(0, time.time() - sample_time):.0f}s' if sample_time else '?'
    if sample_time and time.time() - sample_time > 60:
        return (f'{attempt.parent.name} saved checkpoint {completed}/{expected}; '
                f'previous attempt sample is {age} old. Waiting for a fresh worker sample.')
    detail = tail(attempt / 'worker.log')[:400]
    return (f'{attempt.parent.name} {completed}/{expected} '
            f'status={state.get("status", "starting")} RSS={rss:.2f} GB sample_age={age}'
            f'\n  Latest worker log: {detail or "loading runtime/model; no log output yet"}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('--controller-pid', type=int)
    args = parser.parse_args()
    while True:
        activity = checksum_activity(args.controller_pid) if args.controller_pid else ''
        message = snapshot(args.run_dir)
        if activity:
            message = activity + '\n  ' + message
        print('[lab progress] ' + message, flush=True)
        time.sleep(30)
