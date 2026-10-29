"""Qualified accuracy continuation; never hides a failed no-swap deployment."""
import argparse
import ast
import hashlib
import json
import shutil
from lab_tiers_common import ROOT, completed_cases, inside, read, run_id, sha, ssd_root, write


def validate_recovery(ssd, out):
    if not (out / 'continuation.json').exists():
        manifest = read(out / 'manifest.json') if (out / 'manifest.json').exists() else {}
        derived = any(read(p).get('source_swap_breach') for p in out.glob('tier*/attempt-*/state.json'))
        if manifest.get('continuation') or derived:
            raise ValueError('Required continuation qualification is missing')
        return None
    proof = read(out / 'continuation.json')
    if (out / 'manifest.json').exists():
        saved = read(out / 'manifest.json').get('continuation')
        if saved is not None and saved != proof:
            raise ValueError('Continuation qualification differs from saved run identity')
    if proof['resource_validity'] != 'invalid_for_uninterrupted_no_swap_deployment':
        raise ValueError('Recovery must retain failed deployment qualification')
    for relative, digest in proof['evidence_sha256'].items():
        if sha(inside(out, relative)) != digest:
            raise ValueError('Recovery evidence changed: ' + relative)
    prefix = b''.join(inside(out, proof['job'] + '/cases.jsonl').read_bytes().splitlines(keepends=True)[:proof['reused_cases']])
    if hashlib.sha256(prefix).hexdigest() != proof['prefix_sha256']:
        raise ValueError('Recovered completed-case prefix changed')
    return proof


def prepare(ssd, source_name, destination_name):
    from lab_tiers import freeze_check, live_identity, protocol
    source = ssd / 'runs/lab_tiers_v1' / run_id(source_name)
    target = ssd / 'runs/lab_tiers_v1' / run_id(destination_name)
    if target.exists():
        raise ValueError('Preserve existing recovery destination')
    old, spec = read(source / 'manifest.json'), protocol()
    freeze_check()
    if old['protocol'] != spec or live_identity(read(source / 'state.json').get('controller', {})):
        raise ValueError('Source must be stopped with identical protocol')
    for relative, digest in old['freeze']['code_sha256'].items():
        if sha(source / 'code' / relative) != digest:
            raise ValueError('Archived source changed')
        if relative not in {'scripts/lab_tiers.py', 'scripts/lab_tiers_analyze.py'} and sha(ROOT / relative) != digest:
            raise ValueError('Recovery would change frozen behavior: ' + relative)
    def inference(path):
        return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(path.read_text()).body
            if isinstance(n, ast.FunctionDef) and n.name in ('worker', 'counts', 'job_config', 'monitor_job')}
    if inference(source / 'code/scripts/lab_tiers.py') != inference(ROOT / 'scripts/lab_tiers.py'):
        raise ValueError('Inference or monitor behavior changed')
    jobs = [p for p in source.glob('tier*-*-*') if p.is_dir()]
    if len(jobs) != 1 or len(list(jobs[0].glob('attempt-*'))) != 1:
        raise ValueError('Recovery requires exactly one interrupted first job/attempt')
    job, attempt = jobs[0], next(jobs[0].glob('attempt-*'))
    state = read(attempt / 'state.json')
    if live_identity(state.get('worker', {})) or not state.get('swap_breach') or state.get('memory_breach'):
        raise ValueError('Requires a stopped swap-only failure')
    records = completed_cases(job / 'cases.jsonl', spec['dataset']['ids'])
    samples = [json.loads(x) for x in (attempt / 'memory.jsonl').read_text().splitlines()]
    cap = read(source / 'tier16-cap.json')['cap_bytes']
    bad = next(i for i, v in enumerate(samples) if v.get('tree_swap_bytes') or v['tree_rss_bytes'] > cap)
    if not records or len(records) == spec['dataset']['n'] or not bad or any(r['completed_time'] > samples[bad-1]['time'] for r in records):
        raise ValueError('Cannot certify incomplete completed-case prefix before invalid sample')
    # Reconstruct every reused prompt, token ledger, program, score and delivery
    # decision from saved outputs. Vocabulary only: no generation or gold filter.
    from llama_cpp import Llama
    from completion_tokenization import completion_tokens
    from financial_trace_replay import replay
    from tier8_v2_natural_run import Models
    cfg = read(job / 'manifest.json')['job']
    packets = [json.loads(x) for x in inside(ssd, spec['dataset']['public']).read_text().splitlines()]
    gold = {v['id']: v for v in read(inside(ssd, spec['dataset']['gold']))}
    demos = read(inside(ssd, spec['dataset']['demos']))['examples'][:cfg['demos']]
    tokenizers = {}
    try:
        for role, model in cfg['models'].items():
            tokenizers[role] = Llama(model_path=str(inside(ssd, model['path'])), vocab_only=True,
                n_gpu_layers=0, n_threads=1, verbose=False)
        def count(role, content, structured):
            return len(completion_tokens(tokenizers[role], Models.prompt(content, structured)))
        for packet, record in zip(packets, records):
            replay(packet, gold[packet['id']], record, cfg, count, demos)
    finally:
        for model in tokenizers.values():
            model.close()
    target.mkdir(parents=True)
    evidence = target / 'continuation-evidence'
    write(evidence / 'checkpoint-replay.json', {'status': 'passed', 'n': len(records),
        'new_generation_calls': 0, 'all_prompts_programs_scores_delivery_and_token_ledgers_replayed': True})
    for relative in ['manifest.json', 'state.json', 'tier16-cap.json', 'code/configs/lab_tiers/freeze.json',
            str(job.relative_to(source) / 'manifest.json'), str(job.relative_to(source) / 'cases.jsonl')]:
        dest = evidence / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, dest)
    shutil.copytree(attempt, evidence / job.name / attempt.name)
    dest_job = target / job.name
    dest_job.mkdir()
    shutil.copyfile(job / 'cases.jsonl', dest_job / 'cases.jsonl')
    shutil.copyfile(source / 'tier16-cap.json', target / 'tier16-cap.json')
    derived = dest_job / 'attempt-0001'
    derived.mkdir()
    (derived / 'memory.jsonl').write_text(''.join(json.dumps(v) + '\n' for v in samples[:bad]))
    write(derived / 'state.json', {'status': 'derived_checkpoint_prefix_NOT_independent_attempt',
        'source_swap_breach': True, 'memory_breach': False, 'swap_breach': False,
        'peak_tree_rss_bytes': max(v['tree_rss_bytes'] for v in samples[:bad]),
        'source': str(attempt.relative_to(ssd)), 'reused_cases': len(records),
        'scope': 'Pre-breach samples only; full failed source retained. Overall deployment validity remains FAILED.'})
    proof = {'resource_validity': 'invalid_for_uninterrupted_no_swap_deployment',
        'source_run': source_name, 'job': job.name, 'reused_cases': len(records),
        'next_case_number': len(records)+1, 'prefix_sha256': sha(dest_job / 'cases.jsonl'),
        'last_completed_time': records[-1]['completed_time'], 'last_clean_sample_time': samples[bad-1]['time'],
        'first_invalid_sample': samples[bad], 'cap_bytes': cap,
        'source_peak_swap_bytes': max(v.get('tree_swap_bytes', 0) for v in samples),
        'evidence_sha256': {str(p.relative_to(target)): sha(p) for p in sorted(evidence.rglob('*')) if p.is_file()},
        'limits': 'Accuracy continuation only; source swap failure forbids an uninterrupted no-swap deployment-pass claim. Every completed frozen prefix case is reused, without quality selection. Models/context/prompts/scores unchanged.'}
    write(target / 'continuation.json', proof)
    (target / 'RESOURCE_FAILURE_RETAINED.md').write_text('# Resource failure retained\n\n' + proof['limits'] + '\n')
    validate_recovery(ssd, target)
    print('Prepared qualified continuation:', target, 'next case', len(records)+1)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True)
    p.add_argument('--run-id', required=True)
    args = p.parse_args()
    prepare(ssd_root(), args.source, args.run_id)
