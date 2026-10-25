"""Frozen serial continuation after a full SAS epoch; no retries or Git actions.

Supports training, conversion, monitored application proof and paired QA jobs.
Training and deployment keep separate predeclared whole-tree caps. This queue
does not decide novelty, tune methods, resume outputs or add higher-tier features.
"""
import argparse
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import psutil
from tier8_artifact_paths import artifact_path
from tier8_v2_adapter_convert import validate_adapter
from tier8_v2_posttrain_queue import sha, write, check_inputs, require_training, validate_job

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'tier8_v2_adapter_convert.py', 'tier8_v2_last_logit_proof.py',
           'tier8_v2_adapter_proof.py', 'tier8_v2_adapt.py', 'tier8_v2_run.py',
           'tier8_v2_delivery_analyze.py', 'tier8_v2_analyze.py', 'tier8_v2_unit_audit.py'}


def complete_sas(root, expected_plan_sha):
    plan = json.loads((root / 'plan.json').read_text())
    state = json.loads((root / 'state.json').read_text())
    if sha(root / 'plan.json') != expected_plan_sha or state['state'] != 'complete' or state.get('fit_only') is not False:
        raise ValueError('SAS dependency did not complete the frozen full epoch')
    check_inputs(plan)
    manifest, summary, _ = validate_adapter(root / 'train')
    validation = summary.get('validation_teacher_forced_loss')
    if (manifest['profile'] != '7b' or manifest.get('training_tasks') != ['drafter', 'critic']
            or summary['mode'] != 'train' or summary['examples_processed'] != plan['training_n']
            or summary['optimizer_updates'] != (plan['training_n'] + 7) // 8
            or not isinstance(validation, (int, float)) or not math.isfinite(validation)
            or state['peak_tree_rss_bytes'] > plan['host_tree_cap_bytes']):
        raise ValueError('SAS epoch/count/validation/memory proof incomplete')
    return summary


def verify_result(job):
    root, kind = artifact_path(job['result']), job['kind']
    if kind == 'training':
        return require_training(root)
    if kind == 'sas_convert':
        manifest = json.loads((root / 'manifest.json').read_text())
        if (manifest['status'] != 'complete' or manifest['diagnostic_only']
                or manifest['profile'] != '7b' or manifest['training_mode'] != 'train'
                or manifest['purpose'] != 'drafter' or sha(artifact_path(manifest['file'])) != manifest['sha256']):
            raise ValueError('Invalid SAS full conversion')
        return {'adapter_sha256': manifest['sha256'], 'tensor_count': manifest['tensor_count']}
    if kind == 'sas_proof':
        summary = json.loads((root / 'summary.json').read_text())
        proof = json.loads((root / 'proof.json').read_text())
        if (summary['status'] != 'complete' or summary['exit_code'] != 0
                or summary['cap_bytes'] != 6400000000 or summary['peak_tree_rss_bytes'] > 6400000000
                or proof['arm'] != 'sas' or not proof['pass'] or proof['logits_all']
                or not proof['native_entry_points_equal'] or proof['actual_prefill_tokens'] <= 0):
            raise ValueError('Invalid SAS last-logit proof')
        return summary
    return validate_job(job, 6400000000)


def kill_tree(process):
    try:
        parent = psutil.Process(process.pid)
        targets = parent.children(recursive=True)[::-1] + [parent]
    except psutil.NoSuchProcess:
        return
    for p in targets:
        try:
            p.kill()
        except psutil.NoSuchProcess:
            pass
    psutil.wait_procs(targets, timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True)
    args = parser.parse_args()
    plan_path = artifact_path(args.plan)
    plan, frozen = json.loads(plan_path.read_text()), sha(plan_path)
    root = plan_path.parent
    import fcntl
    lock = (root / 'controller.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (root / 'journal.jsonl').exists():
        raise ValueError('Never implicitly restart a queue')
    def record(state, **fields):
        item = {'state': state, 'time_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **fields}
        with (root / 'journal.jsonl').open('a') as stream:
            stream.write(json.dumps(item) + '\n'); stream.flush(); os.fsync(stream.fileno())
        write(root / 'state.json', item)
    def interrupted(sig, frame):
        raise InterruptedError('Queue signal ' + str(sig))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    child = None
    try:
        check_inputs(plan)
        dependency = plan['dependency']
        try:
            process = psutil.Process(dependency['pid'])
        except psutil.NoSuchProcess:
            process = None
        if process:
            if process.create_time() != dependency['create_time'] or dependency['plan'] not in process.cmdline():
                raise ValueError('Dependency process identity differs')
            record('waiting_for_full_sas', pid=process.pid, dependency_plan_sha256=dependency['plan_sha256'])
            while True:
                try:
                    if process.status() == psutil.STATUS_ZOMBIE:
                        break
                    process.wait(timeout=10)
                    break
                except psutil.TimeoutExpired:
                    pass
                except psutil.NoSuchProcess:
                    break
        summary = complete_sas(artifact_path(dependency['plan']).parent, dependency['plan_sha256'])
        record('full_sas_validated', summary=summary)
        for runtime, versions in plan['runtime_versions'].items():
            python = ROOT / ('.venv-training/bin/python' if runtime == 'training' else '.venv/bin/python')
            code = 'import importlib.metadata as m,json,sys;print(json.dumps({k:m.version(k) for k in json.loads(sys.argv[1])}))'
            actual = json.loads(subprocess.check_output([str(python), '-c', code, json.dumps(list(versions))], text=True, cwd=ROOT))
            if actual != versions:
                raise ValueError('Runtime changed: ' + runtime)
        record('runtimes_verified')
        for job in plan['jobs']:
            if sha(plan_path) != frozen:
                raise ValueError('Frozen queue plan changed')
            check_inputs(plan)
            if (len(job['command']) < 2 or Path(job['command'][1]).name not in ALLOWED
                    or Path(job['command'][1]).resolve() != ROOT / 'scripts' / Path(job['command'][1]).name):
                raise ValueError('Unapproved command')
            cap = job['cap_bytes']
            if cap != (10500000000 if job['kind'] == 'training' else 6400000000):
                raise ValueError('Job resource policy differs')
            minimum = 9000000000 if job['kind'] == 'training' else cap + 1250000000
            if psutil.virtual_memory().available < minimum:
                raise MemoryError('Insufficient host headroom; no retry')
            if artifact_path(job['result']).exists():
                raise ValueError('Job output already exists: ' + job['name'])
            record('job_started', job=job['name'], command=job['command'], cap_bytes=cap)
            peak, breach = 0, False
            with (root / (job['name'] + '.log')).open('x') as log, (root / (job['name'] + '-memory.jsonl')).open('x') as memory:
                child = subprocess.Popen(job['command'], cwd=ROOT, stdin=subprocess.DEVNULL,
                                         stdout=log, stderr=subprocess.STDOUT, start_new_session=True, close_fds=True)
                while child.poll() is None:
                    try:
                        proc = psutil.Process(child.pid)
                        members = [psutil.Process(), proc, *proc.children(recursive=True)]
                        rss = sum(p.memory_info().rss for p in members if p.is_running())
                    except psutil.NoSuchProcess:
                        continue
                    available = psutil.virtual_memory().available
                    peak = max(peak, rss)
                    memory.write(json.dumps({'time': time.time(), 'tree_rss_bytes': rss, 'host_available_bytes': available}) + '\n')
                    memory.flush()
                    if rss > cap or available < 1000000000:
                        breach = True
                        kill_tree(child)
                        break
                    time.sleep(.2)
                code = child.wait()
                child = None
            record('job_exited', job=job['name'], exit_code=code, memory_breach=breach, peak_tree_rss_bytes=peak)
            if code != 0 or breach:
                raise RuntimeError('Job failed; preserve evidence: ' + job['name'])
            record('job_complete', job=job['name'], validation=verify_result(job))
        record('complete', all_jobs_finished=True, novelty_established=False)
    except BaseException as exc:
        if child and child.poll() is None:
            kill_tree(child)
            child.wait()
        record('failed', error=repr(exc))
        raise


if __name__ == '__main__':
    main()
