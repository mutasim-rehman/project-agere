"""Frozen serial matched continuation and natural QA; no retries or promotion.

Existing common-actor fit is an explicit audited prerequisite. Every new full
epoch reloads its original initializer. All fitting data, recipes and job commands
are fixed before natural study outputs. Completion is not evidence of novelty.
"""
import argparse
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import time

import psutil
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha, write, check_inputs
from tier8_v2_joint_posttrain import kill_tree
from tier8_v2_continue import require_fit, RECIPE, discovery_gate
from tier8_v2_adapter_convert import validate_adapter

ROOT = Path(__file__).resolve().parents[1]


def prepare(out, study_path, actor_fit):
    if out.exists():
        raise ValueError('Require a new sequence directory')
    study = json.loads(study_path.read_text()); check_inputs(study)
    ssd = artifact_path(Path(os.environ['AGERE_SSD_ROOT']))
    corpus = ssd / 'datasets/tier8_v2_continuation/matched_01'
    work = ssd / 'runs/tier8_matched_continuation'
    discovery = ssd / 'runs/tier8_joint_posttrain/joint03-discovery02'
    files = discovery_gate(discovery)
    fit_plan = json.loads((actor_fit / 'plan.json').read_text()); require_fit(actor_fit, fit_plan)
    if fit_plan['dataset_manifest'] != str(corpus / 'common_mas_actor/manifest.json'):
        raise ValueError('Wrong common-actor fit')
    files += [actor_fit / n for n in ('plan.json', 'state.json', 'fit/summary.json', 'fit/manifest.json')]
    cpu = ROOT / '.venv/bin/python'; train_python = ROOT / '.venv-training/bin/python'
    script = lambda name: ROOT / 'scripts' / name
    jobs = []
    def job(name, kind, command, result, **extra):
        jobs.append({'name': name, 'kind': kind, 'command': list(map(str, command)),
            'result': str(result), 'cap_bytes': 10500000000 if kind in ('fit', 'train') else 6400000000, **extra})
    reproof = study['baseline_actor_reproof']
    job('reprove-original-actor', 'proof', reproof['command'], reproof['result'])
    policies = [('common-actor', 'common_mas_actor', '3b', ROOT / 'research/tier8_v2/runs/adapter-3b-train-02', actor_fit)]
    for name in ('control', 'crossed'):
        policies.append((name + '-critic', name + '_mas_critic', '3b',
            ssd / 'runs/tier8_critic_training/critic3b-extended-train-01', None))
    for name in ('control', 'crossed'):
        policies.append((name + '-sas', name + '_sas', '7b',
            ssd / 'runs/tier8_sas_training/sas7b-joint-train-compact-03/train', None))
    for name, data_name, profile, initial, existing_fit in policies:
        manifest = corpus / data_name / 'manifest.json'
        fit = existing_fit or work / (name + '-fit-01')
        train = work / (name + '-train-01')
        convert = work / (name + '-converted-01')
        common = [cpu, script('tier8_v2_continue.py'), '--prepare', '--dataset-manifest', manifest,
                  '--initializer', initial, '--profile', profile, '--discovery-root', discovery]
        if existing_fit is None:
            job('prepare-' + name + '-fit', 'prepare', [*common, '--out', fit, '--mode', 'fit'], fit / 'plan.json')
            job('fit-' + name, 'fit', [cpu, script('tier8_v2_continue.py'), '--plan', fit / 'plan.json'], fit)
        job('prepare-' + name + '-epoch', 'prepare', [*common, '--out', train, '--mode', 'train', '--fit-proof', fit], train / 'plan.json')
        job('train-' + name, 'train', [cpu, script('tier8_v2_continue.py'), '--plan', train / 'plan.json'], train,
            expected=json.loads(manifest.read_text())['training_n'])
        job('convert-' + name, 'convert', [train_python, script('tier8_v2_adapter_convert.py'), '--run', train / 'train', '--out', convert], convert)
        proof = work / (name + '-applied-proof-01')
        if profile == '7b':
            command = [cpu, script('tier8_v2_last_logit_proof.py'), '--arm', 'sas', '--adapter', convert,
                '--dataset', corpus / data_name / 'examples.jsonl', '--model-path', ssd / 'weights/tier8_v2/qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf', '--out', proof]
        else:
            command = [cpu, script('tier8_v2_adapter_proof.py'), '--arm', 'mas', '--purpose',
                'drafter' if name == 'common-actor' else 'critic', '--adapter', convert,
                '--dataset', corpus / data_name / 'examples.jsonl', '--model-path', ssd / 'weights/tier8_v2/qwen2.5-3b-instruct-q4_k_m.gguf', '--out', proof]
        job('prove-' + name, 'proof', command, proof)
    # Add the strong original critic with the SAME continued actor, plus its
    # original actor. Never claim a gain only against the regressed extension.
    baseline = next(j for j in study['jobs'] if j['condition'] == 'baseline_mas' and j['partition'] == 'model_selection')
    for label, actor in [('baseline_original_critic_common_actor', work / 'common-actor-converted-01'),
                         ('baseline_original_classic_mas', ROOT / 'research/tier8_v2/runs/adapter-3b-converted-02')]:
        item = deepcopy(baseline); item['condition'] = label; item['name'] = 'model_selection-' + label
        item['result'] = str(ssd / 'runs/tier8_method_qa' / (item['name'] + '-full-01'))
        item['adapter'] = str(actor)
        item['critic_adapter'] = str(ssd / 'runs/tier8_critic_training/critic3b-converted-01')
        for flag, value in [('--adapter', actor), ('--verifier-adapter', ssd / 'runs/tier8_critic_training/critic3b-converted-01'), ('--out', item['result'])]:
            item['command'][item['command'].index(flag) + 1] = str(value)
        study['jobs'].append(item)
    study['input_sha256'][str(study_path)] = sha(study_path)
    study['input_sha256'][str(Path(__file__))] = sha(Path(__file__))
    study['baseline_addendum'] = 'Original critic tested with common continued actor and original actor. No data/metric/policy changes. Matched comparisons are prioritized before broader baselines.'
    proof_map = {
        'baseline_sas': {'actor': str(ssd / 'runs/tier8_sas_training/sas7b-joint-last-logit-proof-03')},
        'baseline_mas': {'actor': reproof['result'], 'critic': str(ssd / 'runs/tier8_critic_training/critic3b-extended-applied-proof-01')},
        'baseline_original_critic_common_actor': {'actor': str(work / 'common-actor-applied-proof-01'), 'critic': str(ssd / 'runs/tier8_critic_training/critic3b-applied-proof-01')},
        'baseline_original_classic_mas': {'actor': reproof['result'], 'critic': str(ssd / 'runs/tier8_critic_training/critic3b-applied-proof-01')}}
    for condition in ('control', 'crossed'):
        proof_map[condition + '_mas'] = {'actor': str(work / 'common-actor-applied-proof-01'), 'critic': str(work / (condition + '-critic-applied-proof-01'))}
        proof_map[condition + '_sas'] = {'actor': str(work / (condition + '-sas-applied-proof-01'))}
    def natural(label, partition):
        selected = next(j for j in study['jobs'] if j['condition'] == label and j['partition'] == partition)
        job(selected['name'], 'natural', selected['command'], selected['result'], expected=selected['expected'])
    def analysis(left, right, partition):
        result = out / (partition + '-' + right + '-vs-' + left + '.json')
        job('analyze-' + result.stem, 'analysis', [cpu, script('tier8_v2_method_analyze.py'), '--study', out / 'study.json',
            '--proofs', out / 'proofs.json', '--left', left, '--right', right, '--partition', partition, '--out', result], result)
    for label in ('control_mas', 'crossed_mas', 'control_sas', 'crossed_sas'):
        natural(label, 'model_selection')
    for arm in ('mas', 'sas'):
        analysis('control_' + arm, 'crossed_' + arm, 'model_selection')
    for label in ('baseline_original_critic_common_actor', 'baseline_original_classic_mas', 'baseline_sas', 'baseline_mas'):
        natural(label, 'model_selection')
    analysis('baseline_original_critic_common_actor', 'crossed_mas', 'model_selection')
    analysis('baseline_sas', 'crossed_sas', 'model_selection')
    for label in ('control_mas', 'crossed_mas', 'control_sas', 'crossed_sas'):
        natural(label, 'diagnostic_audit')
    for arm in ('mas', 'sas'):
        analysis('control_' + arm, 'crossed_' + arm, 'diagnostic_audit')
    for item in study['secondary_sas_prompt_jobs']:
        job('secondary-' + item['name'], 'natural', item['command'], item['result'], expected=item['expected'])
    # Obtain one complete, strong-controlled natural MAS result promptly while
    # preserving every SAS training/evaluation and reserved-audit obligation.
    early_names = {'model_selection-control_mas', 'model_selection-crossed_mas',
        'model_selection-baseline_original_critic_common_actor',
        'analyze-model_selection-crossed_mas-vs-control_mas',
        'analyze-model_selection-crossed_mas-vs-baseline_original_critic_common_actor'}
    early = [j for j in jobs if j['name'] in early_names]
    if len(early) != len(early_names):
        raise ValueError('Missing early matched/strong-reference comparison')
    remaining = [j for j in jobs if j['name'] not in early_names]
    cut = next(i for i, j in enumerate(remaining) if j['name'] == 'prepare-control-sas-fit')
    jobs = remaining[:cut] + early + remaining[cut:]
    for item in jobs:
        if artifact_path(item['result']).exists():
            raise ValueError('Planned fresh output already exists: ' + item['name'])
    files += [Path(__file__), study_path, ROOT / 'scripts/tier8_v2_continue.py',
        ROOT / 'scripts/tier8_v2_method_analyze.py', ROOT / 'scripts/financial_trace_replay.py']
    out.mkdir(parents=True)
    write(out / 'study.json', study); write(out / 'proofs.json', proof_map)
    files += [out / 'study.json', out / 'proofs.json']
    plan = {'kind': 'serial_matched_continuation_and_real_qa', 'out': str(out), 'jobs': jobs,
        'recipe': RECIPE, 'common_actor_fit': str(actor_fit),
        'input_sha256': {str(p): sha(p) for p in files},
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': 'Matched full continuations, proofs and real natural selection/audit; no retries or automatic adoption. Original strong critic retained. Secondary prompt results remain distinct policies.'}
    write(out / 'plan.json', plan)
    print(json.dumps({'plan': str(out / 'plan.json'), 'sha256': sha(out / 'plan.json'), 'jobs': len(jobs)}))


def verify(job):
    root = artifact_path(job['result']); kind = job['kind']
    if kind == 'prepare':
        check_inputs(json.loads(root.read_text())); return
    if kind in ('fit', 'train'):
        state = json.loads((root / 'state.json').read_text()); m, s, _ = validate_adapter(root / kind)
        expected = 2 if kind == 'fit' else job['expected']
        if (state['state'] != 'complete' or s['examples_processed'] != expected or
                s['optimizer_updates'] != (2 if kind == 'fit' else (expected + 7) // 8) or
                not s['initializer_exactly_loaded'] or (kind == 'train' and not math.isfinite(s['validation_teacher_forced_loss']))):
            raise ValueError('Incomplete exact-initialized continuation')
        return
    if kind == 'convert':
        m = json.loads((root / 'manifest.json').read_text())
        if m['status'] != 'complete' or m['diagnostic_only'] or sha(artifact_path(m['file'])) != m['sha256']:
            raise ValueError('Invalid full conversion')
        return
    if kind in ('proof', 'natural'):
        s = json.loads((root / 'summary.json').read_text())
        if (s['status'] != 'complete' or s['exit_code'] or s['cap_bytes'] != 6400000000 or
                not 0 < s['peak_tree_rss_bytes'] <= s['cap_bytes'] or s.get('memory_breach', False) or s.get('memory_breached', False)):
            raise ValueError('Invalid proof or natural run')
        if kind == 'proof':
            if json.loads((root / 'proof.json').read_text())['pass'] is not True:
                raise ValueError('Application effect not proven')
        elif s['n'] != job['expected'] or s['expected'] != job['expected']:
            raise ValueError('Partial natural run')
        return
    if kind == 'analysis':
        result = json.loads(root.read_text())
        if not result['all_prompts_execution_delivery_scores_and_token_ledgers_replayed'] or not result['input_sha256']:
            raise ValueError('Incomplete policy analysis')
        return
    raise ValueError('Unsupported sequence job')


def require_fresh(job):
    root = artifact_path(job['result'])
    if job['kind'] in ('fit', 'train'):
        if not (root / 'plan.json').is_file() or (root / 'state.json').exists():
            raise ValueError('Require a prepared but never-started continuation controller')
    elif root.exists():
        raise ValueError('Fresh job output exists: ' + job['name'])


def run(path):
    import fcntl
    plan = json.loads(path.read_text()); frozen = sha(path); root = path.parent
    lock = (root / 'controller.lock').open('a'); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (root / 'state.json').exists():
        raise ValueError('No implicit sequence restart/resume')
    child = None
    def record(state, **fields):
        event = {'state': state, 'time': time.time(), **fields}
        with (root / 'journal.jsonl').open('a') as stream:
            stream.write(json.dumps(event) + '\n'); stream.flush(); os.fsync(stream.fileno())
        write(root / 'state.json', event)
    def interrupted(sig, frame):
        raise InterruptedError(f'Signal {sig}')
    signal.signal(signal.SIGTERM, interrupted); signal.signal(signal.SIGINT, interrupted)
    try:
        for job in plan['jobs']:
            if sha(path) != frozen:
                raise ValueError('Sequence plan changed')
            check_inputs(plan)
            require_fresh(job)
            minimum = 9000000000 if job['kind'] in ('fit', 'train') else job['cap_bytes'] + 1250000000
            if psutil.virtual_memory().available < minimum:
                raise MemoryError('Insufficient host headroom; no retry')
            record('job_started', job=job['name'], command=job['command'])
            peak = 0; breach = False
            with (root / (job['name'] + '.log')).open('x') as log, (root / (job['name'] + '-memory.jsonl')).open('x') as memory:
                child = subprocess.Popen(job['command'], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log,
                    stderr=subprocess.STDOUT, start_new_session=True, close_fds=True)
                while child.poll() is None:
                    try:
                        proc = psutil.Process(child.pid)
                        rss = sum(p.memory_info().rss for p in [psutil.Process(), proc, *proc.children(recursive=True)] if p.is_running())
                    except psutil.NoSuchProcess:
                        continue
                    available = psutil.virtual_memory().available; peak = max(peak, rss)
                    memory.write(json.dumps({'time': time.time(), 'tree_rss_bytes': rss, 'host_available_bytes': available}) + '\n'); memory.flush()
                    if rss > job['cap_bytes'] or available < 1000000000:
                        breach = True; kill_tree(child); break
                    time.sleep(.2)
                code = child.wait(); child = None
            record('job_exited', job=job['name'], exit_code=code, memory_breach=breach, peak_tree_rss_bytes=peak)
            if code or breach:
                raise RuntimeError('Preserve failed job; no retry: ' + job['name'])
            verify(job); record('job_complete', job=job['name'])
        record('complete', all_jobs_finished=True, novelty_established=False)
    except BaseException as exc:
        if child and child.poll() is None:
            kill_tree(child); child.wait()
        record('failed', error=repr(exc)); raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true'); parser.add_argument('--out'); parser.add_argument('--study')
    parser.add_argument('--actor-fit'); parser.add_argument('--plan'); args = parser.parse_args()
    if args.prepare:
        if not all((args.out, args.study, args.actor_fit)) or args.plan:
            parser.error('Prepare requires new output, frozen study and successful actor fit')
        prepare(artifact_path(args.out), artifact_path(args.study), artifact_path(args.actor_fit))
    elif args.plan:
        run(artifact_path(args.plan))
    else:
        parser.error('Prepare or run one frozen sequence')
