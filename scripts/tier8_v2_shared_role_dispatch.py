"""Wait for the declared discovery queue, then exec the frozen serving proof.

exec replaces this lightweight waiter: no extra resident controller or overlapping
model worker remains outside the proof's complete-tree monitor. No retry/resume.
"""
import argparse
import json
import os
from pathlib import Path
import signal
import time

import psutil
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha, write, check_inputs
from tier8_v2_joint_posttrain import verify_result

ROOT = Path(__file__).resolve().parents[1]


def require_complete(root, plan):
    state = json.loads((root / 'state.json').read_text())
    events = [json.loads(line) for line in (root / 'journal.jsonl').read_text().splitlines()]
    if (state['state'] != 'complete' or not state.get('all_jobs_finished') or not events or
            events[-1] != state or [e['job'] for e in events if e['state'] == 'job_complete'] !=
            [j['name'] for j in plan['jobs']]):
        raise ValueError('Discovery queue has not completed every declared job')
    check_inputs(plan)
    for job in plan['jobs']:
        verify_result(job)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--plan', required=True)
    args = parser.parse_args(); path = artifact_path(args.plan)
    plan = json.loads(path.read_text()); frozen = sha(path); root = path.parent
    if (root / 'state.json').exists():
        raise ValueError('No dispatcher retry/resume')
    def record(state, **fields):
        event = {'state': state, 'time': time.time(), **fields}
        with (root / 'journal.jsonl').open('a') as stream:
            stream.write(json.dumps(event) + '\n'); stream.flush(); os.fsync(stream.fileno())
        write(root / 'state.json', event)
    def interrupted(sig, frame):
        raise InterruptedError(f'Signal {sig}')
    signal.signal(signal.SIGTERM, interrupted); signal.signal(signal.SIGINT, interrupted)
    try:
        check_inputs(plan)
        serving = json.loads(artifact_path(plan['serving_plan']).read_text())
        check_inputs(serving)
        command = plan['command']
        if (command != serving['command'] or command[:2] != [str(ROOT / '.venv/bin/python'),
                str(ROOT / 'scripts/tier8_v2_shared_role_proof.py')]):
            raise ValueError('Only the exact declared frozen serving proof may be executed')
        target = artifact_path(command[command.index('--out') + 1])
        if target.exists():
            raise ValueError('Proof output already exists')
        dep = plan['dependency']; dependency_path = artifact_path(dep['plan'])
        if sha(dependency_path) != dep['plan_sha256']:
            raise ValueError('Declared discovery plan changed')
        try:
            process = psutil.Process(dep['pid'])
        except psutil.NoSuchProcess:
            process = None
        if process:
            if process.create_time() != dep['create_time'] or dep['plan'] not in process.cmdline():
                raise ValueError('Dependency process identity differs')
            record('waiting_for_discovery', pid=dep['pid'], create_time=dep['create_time'])
            while True:
                try:
                    if process.status() == psutil.STATUS_ZOMBIE:
                        break
                    process.wait(timeout=45); break
                except psutil.TimeoutExpired:
                    if process.create_time() != dep['create_time']:
                        raise ValueError('Dependency PID reused')
                except psutil.NoSuchProcess:
                    break
        if sha(path) != frozen:
            raise ValueError('Dispatch plan changed while waiting')
        check_inputs(plan); check_inputs(serving)
        require_complete(dependency_path.parent, json.loads(dependency_path.read_text()))
        if target.exists():
            raise ValueError('Proof output appeared while waiting; no overwrite')
        record('exec_proof', command=command, proof_output=str(target),
               all_discovery_jobs_independently_verified=True, waiter_replaced_not_resident=True)
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.execv(command[0], command)
    except BaseException as exc:
        record('failed', error=repr(exc)); raise


if __name__ == '__main__':
    main()
