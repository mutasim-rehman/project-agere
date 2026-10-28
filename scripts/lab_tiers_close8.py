"""Close the existing8GB prompt checks and explicitly seal the lab handoff.

No inference/training jobs are launched by this tool. Existing frozen commands
are copied into an audit-only study, never changed or added to the live queue.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import time

from lab_tiers_common import ROOT, read, sha, ssd_root, write


def prepare(ssd):
    original = ssd / 'runs/tier8_matched_continuation/matched-study-01'
    out = ssd / 'runs/lab_handoff/closure-v1'
    if (out / 'study.json').exists():
        return out
    if out.exists():
        raise ValueError('Preserve incomplete closure preparation; use an explicit new version')
    plan, study, proofs = [read(original / n) for n in ('plan.json', 'study.json', 'proofs.json')]
    jobs = []
    for condition in ('baseline_sas', 'control_sas', 'crossed_sas'):
        declared = next(j for j in plan['jobs'] if j['name'] == f'secondary-{condition}-analysis128-demos2')
        job = deepcopy(next(j for j in study['jobs'] if j['condition'] == condition and j['partition'] == 'model_selection'))
        job.update(name=declared['name'], command=declared['command'], result=declared['result'])
        jobs.append(job)
    study['jobs'] = jobs
    study['scope'] = 'Audit-only view of predeclared secondary prompt jobs; commands unchanged from original plan.'
    study['input_sha256'][str(original / 'plan.json')] = sha(original / 'plan.json')
    out.mkdir(parents=True)
    write(out / 'study.json', study)
    write(out / 'proofs.json', {j['condition']: proofs[j['condition']] for j in jobs})
    return out


def run_audit(out, name, command):
    result = out / (name + '.json')
    if result.exists():
        existing = read(result)
        if existing.get('n') != 52 or not existing.get('all_prompts_execution_delivery_scores_and_token_ledgers_replayed'):
            raise ValueError('Existing closure result is not a complete paired audit')
        return result
    index = len(list(out.glob(name + '-attempt-*.log'))) + 1
    log = out / f'{name}-attempt-{index:04d}.log'
    with log.open('x') as stream:
        subprocess.run(command + ['--out', str(result)], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
    return result


def close(ssd, wait):
    out = prepare(ssd)
    state_path = ssd / 'runs/tier8_matched_continuation/matched-study-02/state.json'
    last = None
    while True:
        state = read(state_path)
        if state['state'] == 'failed':
            raise ValueError('Original sequence failed; preserve it, no implicit model retry')
        if state['state'] == 'complete':
            break
        if not wait:
            raise ValueError('Two planned8GB prompt jobs are not complete; repeat with --wait')
        job = state.get('job')
        if job != last:
            print('Waiting for original sequence:', job, flush=True)
            last = job
        write(out / 'state.json', {'status': 'waiting_for_existing_sequence', 'job': job, 'time': time.time()})
        time.sleep(30)
    results = []
    for left, right in [('control_sas', 'crossed_sas'), ('baseline_sas', 'crossed_sas')]:
        name = right + '-vs-' + left
        command = [sys.executable, str(ROOT / 'scripts/tier8_v2_method_analyze.py'),
            '--study', str(out / 'study.json'), '--proofs', str(out / 'proofs.json'),
            '--left', left, '--right', right, '--partition', 'model_selection']
        write(out / 'state.json', {'status': 'auditing_existing_results', 'comparison': name, 'time': time.time()})
        results.append(run_audit(out, name, command))
    data = {'status': 'existing_8gb_prompt_evaluations_closed', 'new_generation_calls': 0,
        'paired_results_sha256': {p.name: sha(p) for p in results},
        'primary_higher_tier_policy': 'Prospective pretrained FP16 resident MAS versus Q4 SAS; existing reasoned no-repair profile primary, direct and full-repair controls. Unvalidated source/catalog variants excluded.',
        'scope': 'Finite closure, not a declaration of novel-method superiority or a new training search.'}
    write(out / 'closure.json', data)
    write(out / 'state.json', {'status': 'closed', 'time': time.time()})
    print('Closed existing8GB evaluations:', out, flush=True)
    return out


def seal(ssd):
    out = ssd / 'runs/lab_handoff/closure-v1'
    data = read(out / 'closure.json')
    if data['status'] != 'existing_8gb_prompt_evaluations_closed':
        raise ValueError('Closure incomplete')
    for name, digest in data['paired_results_sha256'].items():
        if sha(out / name) != digest:
            raise ValueError('Closure result changed')
    checks = {
        'runtime': (ssd / 'runs/lab_handoff/runtime-smoke-v1/summary.json', ROOT / 'scripts/lab_runtime_smoke.py'),
        'workflow': (ssd / 'runs/lab_tiers_v1/ENGINEERING_SMOKE_ONLY/engineering-summary.json', ROOT / 'scripts/lab_pipeline_smoke.py'),
    }
    engineering = {}
    for name, (result, source) in checks.items():
        proof = read(result)
        if proof.get('status') != 'passed' or proof.get('script_sha256') != sha(source):
            raise ValueError('Current ' + name + ' smoke has not passed')
        engineering[name] = {'relative_to_ssd': str(result.relative_to(ssd)), 'sha256': sha(result)}
    spec = read(ROOT / 'configs/lab_tiers/protocol.json')
    if spec['tiers']['16'].get('cap_policy') == 'fixed_application_ceiling':
        proof = read(ROOT / 'configs/lab_tiers/memory_fit.json')
        if proof.get('status') != 'passed' or proof.get('cap_bytes') != spec['tiers']['16']['nominal_cap_bytes'] or proof.get('context') != spec['common']['context']:
            raise ValueError('Fixed-cap revision needs a matching resident fit proof')
        for relative, digest in proof['evidence_sha256'].items():
            if sha(ssd / relative) != digest:
                raise ValueError('Resident fit evidence changed')
        for arm in ('sas', 'mas'):
            if proof['models'][arm] != spec['tiers']['16'][arm]:
                raise ValueError('Resident fit models differ from protocol')
        engineering['resident_fit'] = {'config': 'configs/lab_tiers/memory_fit.json',
            'sha256': sha(ROOT / 'configs/lab_tiers/memory_fit.json')}
    destination = ROOT / 'configs/lab_tiers/freeze.json'
    if destination.exists():
        raise ValueError('Refuse freeze overwrite')
    files = [*sorted((ROOT / 'scripts').glob('*.py')),
        ROOT / 'scripts/lab_tiers.sh', ROOT / 'scripts/lab_tiers_all.sh',
        *sorted((ROOT / 'configs/lab_tiers').glob('*'))]
    protocol_doc = ROOT / 'research/lab_tiers/PROTOCOL.md'
    if not protocol_doc.is_file():
        raise ValueError('Write/review the prospective lab protocol before sealing')
    files.append(protocol_doc)
    frozen = {'status': 'sealed_for_lab', 'protocol_id': read(ROOT / 'configs/lab_tiers/protocol.json')['protocol_id'],
        'code_sha256': {str(p.relative_to(ROOT)): sha(p) for p in files if p.is_file()},
        'closure_relative_to_ssd': str(out.relative_to(ssd)), 'closure_sha256': sha(out / 'closure.json'),
        'engineering_checks': engineering,
        'new_methods_after_tier_transition': False, 'novelty_established': False,
        'scope_amendment': 'Numerical financial QA, pretrained both arms, 16GB primary; no KYC/credit-metric or fine-tuning-optimality claim.'}
    write(destination, frozen)
    print('Sealed lab code/config:', destination)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('prepare', 'close', 'seal'))
    p.add_argument('--ssd')
    p.add_argument('--wait', action='store_true')
    args = p.parse_args()
    root = ssd_root(args.ssd)
    if args.command == 'prepare':
        print(prepare(root))
    elif args.command == 'close':
        close(root, args.wait)
    else:
        seal(root)
