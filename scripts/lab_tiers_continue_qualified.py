"""Clone an already-qualified interrupted run; preserve all completed job data.

Preparation only. Does not change frozen inference code or erase resource failures.
"""
import argparse
import json
from pathlib import Path
import shutil
from lab_tiers_common import completed_cases, read, run_id, sha, ssd_root, write


def prepare(ssd, source_id, destination_id):
    from lab_tiers import live_identity, freeze_check
    from lab_tiers_recover import validate_recovery
    source = ssd / 'runs/lab_tiers_v1' / run_id(source_id)
    target = ssd / 'runs/lab_tiers_v1' / run_id(destination_id)
    if target.exists():
        raise ValueError('Refuse overwrite of continuation evidence')
    old = read(source / 'manifest.json')
    if old['freeze'] != freeze_check() or not validate_recovery(ssd, source):
        raise ValueError('Requires identical frozen code and an already-qualified source')
    if live_identity(read(source / 'state.json').get('controller', {})):
        raise ValueError('Source controller is live')
    plans, prefixes = [], {}
    for job in sorted(source.glob('tier*-*-*')):
        if not job.is_dir():
            continue
        records = completed_cases(job / 'cases.jsonl', old['protocol']['dataset']['ids'])
        prefixes[job.name] = {'n': len(records), 'sha256': sha(job / 'cases.jsonl')}
        if (job / 'summary.json').exists():
            if read(job / 'summary.json')['cases_sha256'] != prefixes[job.name]['sha256']:
                raise ValueError('Completed summary/cases mismatch')
        for attempt in sorted(job.glob('attempt-*')):
            state = read(attempt / 'state.json')
            if live_identity(state.get('worker', {})) or state.get('memory_breach'):
                raise ValueError('Live worker or RSS breach needs separate review')
            if state.get('swap_breach'):
                samples = [json.loads(x) for x in (attempt / 'memory.jsonl').read_text().splitlines()]
                cap = read(job / 'manifest.json')['cap_bytes']
                bad = next(i for i, v in enumerate(samples) if v.get('tree_swap_bytes') or v['tree_rss_bytes'] > cap)
                reused = [r for r in records if r.get('attempt') == attempt.name]
                if not bad or any(r['completed_time'] > samples[bad-1]['time'] for r in reused):
                    raise ValueError('Completed checkpoint at/after failed sample')
                plans.append((job.name, attempt.name, samples[:bad], len(reused), state,
                    max(v.get('tree_swap_bytes', 0) for v in samples)))
    if not plans:
        raise ValueError('No stopped swap attempt to recover')
    shutil.copytree(source, target)
    history = target / 'recovery-history' / source_id
    history.mkdir(parents=True)
    for name in ['manifest.json', 'state.json', 'continuation.json', 'workflow.log', 'workflow-status.txt']:
        if (target / name).exists():
            shutil.copyfile(target / name, history / name)
    shutil.copyfile(Path(__file__), history / 'preparation-source.py')
    failures = []
    for job, attempt, clean, n, state, swap in plans:
        dest = target / job / attempt
        archived = history / job / attempt
        archived.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dest), archived)
        dest.mkdir()
        (dest / 'memory.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in clean))
        write(dest / 'state.json', {'status': 'derived_checkpoint_prefix_NOT_independent_attempt',
            'source_swap_breach': True, 'swap_breach': False, 'memory_breach': False,
            'reused_cases': n, 'peak_tree_rss_bytes': max(v['tree_rss_bytes'] for v in clean),
            'source': str(archived.relative_to(target)),
            'scope': 'Pre-breach samples only; full failed attempt preserved. Overall deployment resource validity stays FAILED.'})
        failures.append({'job': job, 'attempt': attempt, 'reused_cases': n, 'peak_swap_bytes': swap})
    proof = read(target / 'continuation.json')
    proof['continued_from_run'] = source_id
    proof['additional_checkpoint_prefixes'] = prefixes
    proof['total_completed_cases_reused'] = sum(v['n'] for v in prefixes.values())
    proof['additional_source_swap_failures'] = failures
    proof['prospective_swap_control'] = 'New workflow will use a user-systemd cgroup with MemorySwapMax=0; prior failures remain invalid.'
    proof['evidence_sha256'].update({str(p.relative_to(target)): sha(p) for p in sorted(history.rglob('*')) if p.is_file()})
    write(target / 'continuation.json', proof)
    old['continuation'] = proof
    old['recovery_lineage'] = {'source_run': source_id, 'frozen_inference_unchanged': True,
        'completed_prefixes': prefixes, 'historical_swap_failure_retained': True}
    write(target / 'manifest.json', old)
    for job, prefix in prefixes.items():
        if sha(target / job / 'cases.jsonl') != prefix['sha256']:
            raise ValueError('Copy changed checkpoint data')
    for name in ['state.json', 'workflow.log', 'workflow-status.txt']:
        (target / name).unlink(missing_ok=True)
    validate_recovery(ssd, target)
    print('Prepared', target, 'completed cases preserved:', proof['total_completed_cases_reused'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    prepare(ssd_root(), args.source, args.run_id)
