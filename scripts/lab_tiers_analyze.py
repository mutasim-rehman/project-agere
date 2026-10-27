"""Reconstruct saved lab trajectories and paired report-level estimates offline."""
from collections import defaultdict
import json
from pathlib import Path
import random
import tarfile

from lab_tiers_common import append, completed_cases, inside, read, sha, verify, write


def paired(left, right, groups, metric, repeats=10000):
    if not left or set(left) != set(right) or not set(left) <= set(groups):
        raise ValueError('Require identical nonempty paired case IDs and report groups')
    by_group = defaultdict(list)
    for key in left:
        by_group[groups[key]].append(key)
    outcome = lambda v: ('correct_delivered' if v['score'][metric] else 'wrong_delivered') if v['delivered'] else 'withheld'
    fields = ('correct_delivered', 'wrong_delivered', 'withheld')
    clusters = []
    for keys in by_group.values():
        delta = [sum(int(outcome(right[i]) == f) - int(outcome(left[i]) == f) for i in keys) for f in fields]
        clusters.append((len(keys), delta))
    rng = random.Random(42)
    samples = [[] for _ in fields]
    for _ in range(repeats):
        drawn = rng.choices(clusters, k=len(clusters))
        denominator = sum(x[0] for x in drawn)
        for j in range(len(fields)):
            samples[j].append(sum(x[1][j] for x in drawn) / denominator)
    delta = {f: sum(c[1][j] for c in clusters) for j, f in enumerate(fields)}
    intervals = {}
    for j, f in enumerate(fields):
        values = sorted(samples[j])
        intervals[f] = [values[int(repeats*.025)], values[min(repeats-1, int(repeats*.975))]]
    return {'n': len(left), 'reports': len(clusters), 'delta_direction': 'MAS_minus_SAS',
        'delta_counts': delta, 'report_bootstrap_95_intervals': intervals,
        'resamples': repeats, 'seed': 42,
        'observed_pareto_only': delta['correct_delivered'] >= 0 and delta['wrong_delivered'] <= 0
            and (delta['correct_delivered'] > 0 or delta['wrong_delivered'] < 0),
        'limits': 'Descriptive paired bootstrap, not proof of equality, population noninferiority or a novel method. No post-hoc equivalence margin.'}


def analyze(ssd, out):
    from llama_cpp import Llama
    from completion_tokenization import completion_tokens
    from financial_trace_replay import replay
    from tier8_v2_natural_run import Models
    from lab_tiers import counts, verify_inputs
    manifest = read(out / 'manifest.json')
    if read(out / 'state.json')['status'] != 'complete':
        raise ValueError('All requested jobs must finish before final paired analysis')
    spec = manifest['protocol']
    cache = {}
    verify_inputs(ssd, spec, manifest['tiers'], cache)
    for relative, digest in manifest['freeze']['code_sha256'].items():
        if sha(out / 'code' / relative) != digest:
            raise ValueError('Archived code differs')
    packets = [json.loads(x) for x in inside(ssd, spec['dataset']['public']).read_text().splitlines()]
    gold = {x['id']: x for x in read(inside(ssd, spec['dataset']['gold']))}
    all_demos = read(inside(ssd, spec['dataset']['demos']))['examples']
    groups = {p['id']: p['id'].rsplit('/', 1)[0] for p in packets}
    audit_dir = out / 'analysis'
    audit_dir.mkdir(exist_ok=True)
    replayed, summaries, evidence = {}, {}, {}
    for folder in sorted(out.glob('tier*-*-*')):
        if not folder.is_dir():
            continue
        m, summary = read(folder / 'manifest.json'), read(folder / 'summary.json')
        cfg = m['job']
        records = completed_cases(folder / 'cases.jsonl', spec['dataset']['ids'])
        if len(records) != spec['dataset']['n'] or sha(folder / 'cases.jsonl') != summary['cases_sha256']:
            raise ValueError('Incomplete/changed cases: ' + folder.name)
        peak = 0
        for attempt in sorted(folder.glob('attempt-*')):
            state = read(attempt / 'state.json')
            if state.get('memory_breach') or state.get('swap_breach'):
                raise ValueError('Breached attempt cannot enter a valid result')
            sample_peak = 0
            with (attempt / 'memory.jsonl').open() as stream:
                for line in stream:
                    row = json.loads(line)
                    if not 0 < row['tree_rss_bytes'] <= m['cap_bytes'] or row.get('tree_swap_bytes', 0):
                        raise ValueError('Invalid memory sample')
                    sample_peak = max(sample_peak, row['tree_rss_bytes'])
            if sample_peak != state['peak_tree_rss_bytes']:
                raise ValueError('Memory peak does not replay')
            peak = max(peak, sample_peak)
            evidence[str(attempt.relative_to(out)) + '/memory.jsonl'] = sha(attempt / 'memory.jsonl')
        if peak != summary['sampled_peak_tree_rss_bytes']:
            raise ValueError('Aggregate memory peak differs')
        tokenizers = {}
        try:
            for role, model in cfg['models'].items():
                tokenizers[role] = Llama(model_path=str(inside(ssd, model['path'])), vocab_only=True,
                    n_gpu_layers=0, n_threads=1, verbose=False)
            def count(role, content, structured):
                return len(completion_tokens(tokenizers[role], Models.prompt(content, structured)))
            replayed[folder.name] = {p['id']: replay(p, gold[p['id']], row, cfg, count, all_demos[:cfg['demos']])
                for p, row in zip(packets, records)}
        finally:
            for tokenizer in tokenizers.values():
                tokenizer.close()
        # Aggregate raw records separately and compare to the recorded summary.
        recomputed = counts(records)
        for key in recomputed:
            if recomputed[key] != summary[key]:
                raise ValueError('Summary differs from replayed record totals')
        summaries[folder.name] = summary
        path = audit_dir / (folder.name + '-replayed.jsonl')
        path.write_text(''.join(json.dumps({'id': key, **value}) + '\n' for key, value in replayed[folder.name].items()))
        evidence[str(path.relative_to(out))] = sha(path)
        for name in ('manifest.json', 'summary.json', 'cases.jsonl'):
            evidence[str((folder / name).relative_to(out))] = sha(folder / name)
    comparisons = {}
    for tier in manifest['tiers']:
        for profile in spec['profiles']:
            left = replayed[f'tier{tier}-sas-{profile}']
            right = replayed[f'tier{tier}-mas-{profile}']
            comparisons[f'tier{tier}-{profile}'] = {
                metric: paired({k:v['full'] for k,v in left.items()}, {k:v['full'] for k,v in right.items()}, groups, metric)
                for metric in ('case_success', 'raw_execution_match')}
    result = {'status': 'complete_audited', 'protocol_id': spec['protocol_id'],
        'tiers': manifest['tiers'], 'primary_comparison': 'tier16-primary',
        'summaries': summaries, 'comparisons': comparisons, 'evidence_sha256': evidence,
        'manifest_sha256': sha(out / 'manifest.json'), 'new_generation_calls': 0,
        'novelty_established': False, 'null_hypothesis_proven': False,
        'non_neural_reference_control': {'always_withhold': {'correct_delivered': 0, 'wrong_delivered': 0, 'withheld': len(packets)},
            'note': 'Shows why wrong-delivery reduction alone is not utility. Not claimed to solve numerical QA.'},
        'limits': [spec['dataset']['limits'], spec['adaptation'], spec['statistics']['interpretation'],
            'One model family/checkpoint set/seed; actual prompts, model sizes and precision differ by deployment. Equal ceilings are not equal compute. Primary 16GB comparison; remaining profiles/32GB are secondary.']}
    write(audit_dir / 'summary.json', result)
    lines = ['# Offline lab evaluation summary', '', 'All counts are over the complete paired dataset, including withheld cases.', '',
        '| Job | Correct reported | Wrong reported | Withheld | Correct raw | Peak RSS GB |', '|---|---:|---:|---:|---:|---:|']
    for name, s in summaries.items():
        m, raw = s['full']['case_success'], s['full']['raw_execution_match']
        lines.append(f'| {name} | {m["correct_delivered"]} | {m["wrong_delivered"]} | {m["withheld"]} | {raw["correct_delivered"]} | {s["sampled_peak_tree_rss_bytes"]/1e9:.3f} |')
    lines.extend(['', 'Paired report-level intervals and all audit hashes: `analysis/summary.json`.', '',
        'No automatic proof of H0, equivalence, a novel method or deployment safety. See frozen manifest for scope/limitations.'])
    (audit_dir / 'REPORT.md').write_text('\n'.join(lines) + '\n')
    print('Audited summary:', audit_dir / 'REPORT.md')


def export(ssd, out):
    from lab_tiers import live_identity
    state = read(out / 'state.json')
    if live_identity(state.get('controller', {})) or any(live_identity(read(p).get('worker', {})) for p in out.glob('tier*/attempt-*/state.json')):
        raise ValueError('Wait until the controller/workers stop before making an immutable export')
    target = ssd / 'runs/lab_tiers_v1/exports'
    target.mkdir(exist_ok=True)
    path = target / (out.name + '-results.tar.gz')
    if path.exists():
        raise ValueError('Refuse export overwrite; preserve prior export or choose another run ID')
    if not (out / 'manifest.json').exists():
        raise ValueError('No run manifest')
    # The run tree contains code and traces, never model/runtime payloads. Include
    # exact public/scoring inputs so later audit need not rely on a mount path.
    spec = read(out / 'manifest.json')['protocol']
    with tarfile.open(path, 'w:gz') as tar:
        tar.add(out, arcname=out.name, recursive=True)
        for key in ('public', 'gold', 'demos'):
            tar.add(inside(ssd, spec['dataset'][key]), arcname=out.name + '/inputs/' + Path(spec['dataset'][key]).name)
    write(path.with_suffix(path.suffix + '.sha256.json'), {'file': path.name, 'sha256': sha(path),
        'contains_models': False, 'contains_runtime': False, 'contains_credentials': False,
        'note': 'Code/data/traces included. Neural token replay still requires the pinned runtime and original model vocabulary; numeric summaries and raw logs can be reviewed without it.'})
    print('Portable result archive:', path)
