"""Explicit suffix after an interrupted metadata preparation; never retry NN work.

Verifies the successful ordered prefix and unchanged original recipe/commands.
The original queue is preserved. Only absent metadata-preparation output qualifies.
"""
import argparse
import fcntl
import json
from pathlib import Path
import shutil
import subprocess
import time

import psutil
from tier8_artifact_paths import artifact_path
import tier8_v2_posttrain_queue as queue
from tier8_v2_matched_sequence import verify

ROOT = Path(__file__).resolve().parents[1]


def prefix(jobs, events):
    cursor, active, exited = 0, None, False
    for event in events:
        state = event['state']
        if state == 'job_started':
            if active is not None or cursor >= len(jobs) or event['job'] != jobs[cursor]['name']:
                raise ValueError('Unordered or overlapping original jobs')
            if event['command'] != jobs[cursor]['command']:
                raise ValueError('Original command changed')
            active, exited = event['job'], False
        elif state == 'job_exited':
            if active is None or event['job'] != active or exited or event['exit_code'] or event['memory_breach']:
                raise ValueError('No recovery across failed or duplicated jobs')
            exited = True
        elif state == 'job_complete':
            if active is None or event['job'] != active or not exited:
                raise ValueError('Completion without successful observed exit')
            cursor += 1; active, exited = None, False
        else:
            raise ValueError('Terminal/unknown journal event; no implicit recovery')
    if cursor >= len(jobs) or active != jobs[cursor]['name'] or exited or jobs[cursor]['kind'] != 'prepare':
        raise ValueError('Only a started, unexited metadata preparation may be recovered')
    return cursor


class ReadOnlyHashCache:
    """One audit pass; invalidate on inode/size/mtime/ctime change, check read race.

    Actual training controllers/workers retain their unchanged full byte checks.
    """
    def __init__(self, hash_function):
        self.hash_function, self.values = hash_function, {}

    @staticmethod
    def identity(path):
        s = path.stat()
        return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)

    def __call__(self, path):
        path = Path(path).resolve(); before = self.identity(path)
        if path not in self.values or self.values[path][0] != before:
            digest = self.hash_function(path)
            if self.identity(path) != before:
                raise ValueError('Input changed while reading recovery proof')
            self.values[path] = before, digest
        return self.values[path][1]


def prepare(original, launch_path, out):
    if out.exists():
        raise ValueError('Require a new explicit recovery directory')
    launch = json.loads(launch_path.read_text()); original_plan = original / 'plan.json'
    if artifact_path(launch['plan']) != original_plan or queue.sha(original_plan) != launch['plan_sha256']:
        raise ValueError('Original launch identity differs')
    try:
        old = psutil.Process(launch['pid'])
        if abs(old.create_time() - launch['create_time']) < .01:
            raise ValueError('Original controller still live; never start a duplicate')
    except psutil.NoSuchProcess:
        pass
    for proc in psutil.process_iter(['pid', 'cmdline']):
        names = {Path(a).name for a in proc.info['cmdline'] or []}
        if 'tier8_v2_matched_sequence.py' in names or ('--worker' in (proc.info['cmdline'] or []) and
                any(n.startswith('tier8_v2_') and n.endswith('.py') for n in names)):
            raise ValueError('Existing research controller/worker live')
    lock = (original / 'controller.lock').open('a'); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    plan = json.loads(original_plan.read_text()); state = json.loads((original / 'state.json').read_text())
    events = [json.loads(x) for x in (original / 'journal.jsonl').read_text().splitlines()]
    cursor = prefix(plan['jobs'], events); pending = plan['jobs'][cursor]
    if state.get('state') != 'job_started' or state.get('job') != pending['name']:
        raise ValueError('Original terminal observation differs from journal')
    target = artifact_path(pending['result'])
    if target.exists() or target.parent.exists():
        raise ValueError('Interrupted metadata output already exists; requires separate diagnosis')
    # Cache only this read-only prefix audit, not any future model execution.
    original_sha = queue.sha; cached = ReadOnlyHashCache(original_sha); queue.sha = cached
    verified = []
    try:
        queue.check_inputs(plan)
        for job in plan['jobs'][:cursor]:
            verify(job); verified.append({'name': job['name'], 'kind': job['kind'], 'result': job['result']})
    finally:
        queue.sha = original_sha
    out.mkdir(parents=True); snap = out / 'original-snapshot'; snap.mkdir()
    sources = ['plan.json', 'state.json', 'journal.jsonl', 'controller.log',
               pending['name'] + '.log', pending['name'] + '-memory.jsonl']
    snapshots = []
    for name in sources:
        src = original / name
        if src.is_file():
            dst = snap / name; shutil.copyfile(src, dst); snapshots.append(dst)
    memory = original / (pending['name'] + '-memory.jsonl')
    last = json.loads(memory.read_text().splitlines()[-1])
    audit = {'status': 'explicit_suffix_prepared_after_controller_disappearance', 'time': time.time(),
        'cause': 'Unknown abrupt disappearance; no observed exit or failure event. Do not infer a cause.',
        'original_controller_pid': launch['pid'], 'original_controller_create_time': launch['create_time'],
        'boot_time': psutil.boot_time(), 'last_original_sample': last,
        'successful_prefix_jobs_reverified': verified, 'first_pending_job': pending,
        'interrupted_metadata_output_absent': True, 'completed_model_work_repeated': False,
        'recipe_or_commands_changed': False,
        'audit_hashes': {str(path): value[1] for path, value in cached.values.items()},
        'scope': 'Explicit rerun of interrupted metadata preparation only; no failed NN replay or implicit restart.'}
    audit_path = out / 'recovery-audit.json'; queue.write(audit_path, audit)
    files = [Path(__file__), launch_path, original_plan, audit_path, *snapshots]
    continuation = {**plan, 'kind': 'explicit_pending_metadata_suffix', 'out': str(out),
        'jobs': plan['jobs'][cursor:], 'original_sequence': str(original),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'input_sha256': {**plan['input_sha256'], **{str(p): original_sha(p) for p in files}},
        'scope': 'Identical pending commands after audited interrupted metadata preparation; all original scientific obligations retained. No retries, promotion or novelty claim.'}
    queue.write(out / 'plan.json', continuation)
    print(json.dumps({'plan': str(out / 'plan.json'), 'sha256': original_sha(out / 'plan.json'),
        'completed_jobs_verified': cursor, 'remaining_jobs': len(continuation['jobs']), 'first': pending['name']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('original', 'launch', 'out'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    prepare(artifact_path(args.original), artifact_path(args.launch), artifact_path(args.out))
