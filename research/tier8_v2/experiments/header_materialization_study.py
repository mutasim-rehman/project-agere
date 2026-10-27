"""Prepare/audit a fitting-only representation comparison; never launch models.

The active matched study is unchanged. Four proposed runs use the existing
monitored runner. Analysis requires complete traces and replays both policies.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha, check_inputs
from tier8_v2_natural_run import natural_partition, financial_source
from table_header_materialization import materialize


def read(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines()]


def write(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


def prepare(out):
    if out.exists():
        raise ValueError('Fresh output required; refuse overwrite')
    base = artifact_path('/run/media/mutasim/Data/AGERE')
    natural = base / 'datasets/tier8_v2_natural/natural_reports62_01'
    prototype = base / 'runs/tier8_representation_audit/header-materialization-fitting-01'
    prior = base / 'runs/tier8_matched_continuation/matched-study-01'
    summary = read(prototype / 'summary.json')
    check_inputs(summary)
    public = natural / 'fitting-public.jsonl'
    source = natural / 'source-train.json'
    candidate = prototype / 'candidate-public.jsonl'
    original, augmented = rows(public), rows(candidate)
    if sha(candidate) != summary['candidate_public_sha256']:
        raise ValueError('Sealed candidate changed')
    natural_partition(public, source)
    gold = {r['id']: r for r in read(source)}
    if len(original) != 73 or len(augmented) != len(original):
        raise ValueError('Require all73 fitting cases')
    for old, new in zip(original, augmented):
        if new != materialize(old, gold[old['id']]['table']):
            raise ValueError('Candidate differs from raw-table-only transform')
    study, proofs = read(prior / 'study.json'), read(prior / 'proofs.json')
    out.mkdir(parents=True)
    # A separate pinned source/selection namespace keeps the original runner's
    # immutable partition checks intact. Never amend the active selection file.
    local_source = out / 'source-train.json'
    local_source.write_bytes(source.read_bytes())
    partitions = {}
    for label, path in [('control', public), ('header', candidate)]:
        target = out / (label + '-public.jsonl')
        target.write_bytes(path.read_bytes())
        partitions[label] = {**read(natural / 'selection.json')['partitions']['fitting'],
            'public_file': str(target), 'sha256': sha(target)}
    selection = {'status': 'prepared_fitting_representation_comparison',
        'source_split': 'train', 'source_copy': str(local_source),
        'source_sha256': sha(local_source), 'partitions': partitions,
        'publication_confirmation': False, 'model_calls': 0,
        'limits': 'Same73 previously explored fitting cases; no selection/reserved transformation. Extra content/tokens, not information/token matched.'}
    write(out / 'selection.json', selection)
    if financial_source(local_source) != local_source:
        raise ValueError('Pinned source validation failed')
    for p in partitions.values():
        natural_partition(Path(p['public_file']), local_source)
    jobs, selected_proofs = [], {}
    for arm, condition in [('mas', 'baseline_original_critic_common_actor'), ('sas', 'baseline_sas')]:
        template = next(j for j in study['jobs'] if j['condition'] == condition and j['partition'] == 'model_selection')
        for label in ('control', 'header'):
            name = arm + '-' + label
            job = deepcopy(template)
            job.update(name=name, partition=label, condition=name, expected=73,
                result=str(out / ('run-' + name)))
            replacements = {'--data': partitions[label]['public_file'], '--evaluation-source': str(local_source),
                '--limit': '73', '--out': job['result']}
            for flag, value in replacements.items():
                job['command'][job['command'].index(flag) + 1] = value
            jobs.append(job)
            selected_proofs[name] = proofs[condition]
    files = [Path(__file__), ROOT / 'scripts/table_header_materialization.py',
        prototype / 'summary.json', candidate, public, source, natural / 'selection.json',
        prior / 'study.json', prior / 'proofs.json', out / 'selection.json', local_source,
        *[Path(p['public_file']) for p in partitions.values()]]
    # Pin inference dependencies without changing their frozen source files.
    files.extend(ROOT / 'scripts' / n for n in (
        'tier8_v2_natural_run.py', 'tier8_v2_financial_pipeline.py',
        'tier8_v2_method_analyze.py', 'financial_trace_replay.py'))
    plan = {'status': 'prepared_not_executed', 'kind': 'fitting_only_header_representation',
        'jobs': jobs, 'proofs': selected_proofs, 'input_sha256': {str(p): sha(p) for p in files},
        'primary': 'Ungated initial-prefix reported and raw correctness; no loss under either metric and at least one strict gain, separately per architecture.',
        'secondary': 'Full delivery risk/coverage, no-repair prefix, repair gains/regressions, tokens, latency and peak RSS; unchanged scoring, whole-report intervals.',
        'execution_rule': 'Only after the active matched sequence terminates successfully and all four full-trace audits are ready. Serial monitored jobs only;6.4GB cap. Never skip original study obligations.',
        'selection_rule': 'All73 cases retained. No per-case routing, threshold tuning, checkpoint replacement or metric changes based on outcomes. Mixed architectures reported separately.',
        'novelty_established': False, 'adopted': False, 'neural_forward_calls': 0,
        'limits': 'Exploratory fitting study of known source-retention preprocessing. Drop-in frozen checkpoints, no training. Extra source content/tokens; no claim of token-matched algorithmic gain. Initial-prefix is a measured trajectory ablation, not an independent fresh generation. Does not establish publication confirmation or full cross-tier readiness.'}
    write(out / 'plan.json', plan)
    print(json.dumps({'plan': str(out / 'plan.json'), 'jobs': len(jobs), 'case_arms': 292, 'launched': False}))


def analyze(plan_path, arm, out):
    from tier8_v2_method_analyze import ArtifactChecks, load_condition, compare
    if out.exists():
        raise ValueError('Fresh analysis output required')
    plan = read(plan_path)
    check_inputs(plan)
    if plan['kind'] != 'fitting_only_header_representation':
        raise ValueError('Wrong study kind')
    jobs = [next(j for j in plan['jobs'] if j['name'] == arm + '-' + k) for k in ('control', 'header')]
    paths = [Path(j['command'][j['command'].index('--data') + 1]) for j in jobs]
    source = Path(jobs[0]['command'][jobs[0]['command'].index('--evaluation-source') + 1])
    gold = {r['id']: r for r in read(source)}
    a, b = [rows(p) for p in paths]
    if len(a) != 73 or len(b) != 73:
        raise ValueError('All fitting cases required')
    for old, new in zip(a, b):
        if new != materialize(old, gold[old['id']]['table']):
            raise ValueError('Representation intervention differs')
    checks, tokenizers = ArtifactChecks(), {}
    try:
        loaded = [load_condition(j, plan['proofs'][j['name']], checks, tokenizers) for j in jobs]
        left, right = [x[0] for x in loaded]
        for key in ('evaluation_source_sha256', 'code_sha256', 'models', 'task_policy', 'runtime', 'adapter', 'verifier_adapter'):
            if left[key] != right[key]:
                raise ValueError('Unmatched frozen policy: ' + key)
        strip = lambda m: {k: v for k, v in m['config'].items() if k not in ('out', 'data')}
        if strip(left) != strip(right):
            raise ValueError('Policy settings differ beyond representation')
        result = compare(loaded[0][2], loaded[1][2])
        primary = [result['views']['ungated_initial_prefix'][m]['delta_counts']['correct_delivered']
            for m in ('case_success', 'raw_execution_match')]
        result.update(arm=arm, exploratory_fitting_only=True, all73_cases_retained=True,
            all_prompts_execution_scores_tokens_memory_replayed=True,
            representation_generation_rule_verified=True,
            initial_generation_gate=all(x >= 0 for x in primary) and any(x > 0 for x in primary),
            drop_in_frozen_checkpoints=True, extra_source_content_and_tokens=True,
            novelty_established=False, adopted=False, measured_new_generation_calls=0,
            input_sha256={**plan['input_sha256'], **checks.files, str(plan_path): sha(plan_path), str(Path(__file__)): sha(Path(__file__))})
        # Revalidate after the potentially long trace/token audit as well.
        check_inputs(plan)
        write(out, result)
        print(json.dumps({'out': str(out), 'n': result['n'], 'initial_generation_gate': result['initial_generation_gate']}))
    finally:
        for tokenizer in tokenizers.values():
            tokenizer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'analyze'))
    parser.add_argument('--out', required=True)
    parser.add_argument('--plan')
    parser.add_argument('--arm', choices=('mas', 'sas'))
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare(artifact_path(args.out))
    else:
        if not args.plan or not args.arm:
            parser.error('Analysis requires --plan and --arm')
        analyze(artifact_path(args.plan), args.arm, artifact_path(args.out))
