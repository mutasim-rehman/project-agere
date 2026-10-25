"""Offline numerical opportunity ceiling for the already frozen local pool.

Seal the gold-free pools, grouping and actual vocabulary-only work allocations
BEFORE reading numerical reference answers. This is not a model/policy evaluation.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import execute
from source_repair_pool import local_pool
from source_program_quotient import partition
from binary_verifier_score import PREFIX, VerificationBudget
from completion_tokenization import completion_tokens
from tier8_v2_critic_data import prompt
from tier8_v2_financial_pipeline import evaluate_financial
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha, write, check_inputs

ROOT = Path(__file__).resolve().parents[1]
MODES = ('bytes', 'numeric', 'numeric_sources', 'source_symbolic')
METRICS = ('case_success', 'raw_execution_match')


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--out', required=True)
    parser.add_argument('--redundancy-evidence', default='research/tier8_v2/evidence/source-quotient-diagnostic-01.json')
    args = parser.parse_args(); out = artifact_path(args.out)
    if out.exists():
        raise ValueError('Preserve existing diagnostic; no overwrite')
    prior_path = artifact_path(args.redundancy_evidence); prior = json.loads(prior_path.read_text())
    check_inputs(prior)
    for path, digest in prior['source_sha256'].items():
        if sha(artifact_path(path)) != digest:
            raise ValueError('Original pool/grouping source changed')
    inputs = list(prior['input_sha256'])
    public_path = next(artifact_path(p) for p in inputs if Path(p).name != 'cases.jsonl')
    snapshots = next(artifact_path(p) for p in inputs if Path(p).name == 'cases.jsonl')
    public = {r['id']: r for r in map(json.loads, public_path.read_text().splitlines())}
    # These are the ONLY fields read from saved model outputs before sealing.
    initial = [{'id': r['case_id'], 'plan': r['initial_plan']}
               for r in map(json.loads, snapshots.read_text().splitlines())]
    if len(initial) != len({r['id'] for r in initial}):
        raise ValueError('Duplicate snapshot IDs')
    from llama_cpp import Llama
    from tier8_v2_run import verified_models
    import os
    weights = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / 'weights/tier8_v2')
    models = verified_models('mas', verifier_model='3b', use_selector=False,
                             drafter_model='3b-q4', weights_root=str(weights))
    tokenizer = Llama(model_path=str(weights / 'qwen2.5-3b-instruct-q4_k_m.gguf'), vocab_only=True, verbose=False)
    sealed = []
    try:
        for case in initial:
            packet = public[case['id']]; atoms = atom_catalog(packet['evidence'])
            pool = local_pool(packet, case['plan'])
            groups = {mode: partition(pool['plans'], atoms, packet['evidence'], mode=mode) for mode in MODES}
            costs = []
            for plan in pool['plans']:
                candidate = compile_plan(plan, atoms); execution = execute(candidate['steps'], packet['evidence'])
                costs.append(len(completion_tokens(tokenizer, prompt(packet, candidate, execution) + PREFIX)))
            allocations = {}
            for mode, grouping in groups.items():
                budget = VerificationBudget(max_checks=4, max_prefill_tokens=8192)
                scored, skips = [], Counter()
                for group in grouping['groups']:
                    index = group[0]
                    if grouping['analyses'][index].get('execution', {}).get('issues', [True]):
                        skips['not_executable'] += 1
                    elif costs[index] + 8 > 4096:
                        skips['no_context'] += 1
                    elif not budget.can_charge(costs[index]):
                        skips['no_budget'] += 1
                    else:
                        budget.charge(costs[index]); scored.append(index)
                allocations[mode] = {'groups': grouping['groups'], 'scored_indices': scored,
                    'charged_prefill_tokens': budget.prefill_tokens, 'checks': budget.checks,
                    'skipped': dict(skips), 'symbolic_operations': grouping['symbolic_operations']}
            sealed.append({'id': case['id'], 'plans': pool['plans'], 'origins': pool['origins'],
                           'critic_prefill_costs': costs, 'allocations': allocations})
    finally:
        tokenizer.close()
    if len(sealed) != prior['n'] or sum(len(r['plans']) for r in sealed) != prior['total_candidates']:
        raise ValueError('Original pool counts do not reproduce')
    for mode in MODES:
        if sum(len(r['allocations'][mode]['groups']) for r in sealed) != prior['total_classes'][mode]:
            raise ValueError('Original grouping counts do not reproduce')
    out.mkdir(parents=True)
    pool_path = out / 'gold-free-pools-and-allocations.jsonl'
    pool_path.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in sealed))
    write(out / 'pool-seal.json', {'status': 'sealed_before_reference_answers', 'sha256': sha(pool_path),
        'n': len(sealed), 'candidates': sum(len(r['plans']) for r in sealed), 'vocab_only': True,
        'model_generation_calls': 0, 'models': models, 'budget': {'checks': 4, 'prefill_tokens': 8192, 'context': 4096},
        'input_sha256': prior['input_sha256'], 'source_sha256': {str(p): sha(p) for p in [Path(__file__),
            ROOT / 'scripts/source_repair_pool.py', ROOT / 'scripts/source_program_quotient.py',
            ROOT / 'scripts/tier8_v2_critic_data.py', ROOT / 'scripts/binary_verifier_score.py']}})
    # Reference answers become accessible ONLY after the independent pool seal.
    manifest = json.loads((snapshots.parent / 'manifest.json').read_text())
    source = artifact_path(manifest['evaluation_source'])
    if sha(source) != manifest['evaluation_source_sha256']:
        raise ValueError('Reference source changed')
    gold = {r['id']: r for r in json.loads(source.read_text())}
    rows = []
    for case in sealed:
        packet = public[case['id']]; atoms = atom_catalog(packet['evidence'])
        if packet['question'] != gold[case['id']]['qa']['question']:
            raise ValueError('Public/reference question differs')
        scores = []
        for plan in case['plans']:
            candidate = compile_plan(plan, atoms)
            scores.append(evaluate_financial(gold[case['id']], candidate, execute(candidate['steps'], packet['evidence'])))
        rows.append({'id': case['id'], 'metrics': {metric: {
            'initial_correct': bool(scores and scores[0][metric]),
            'full_pool_contains_correct': any(s[metric] for s in scores),
            'correct_candidate_indices': [i for i, s in enumerate(scores) if s[metric]],
            'correct_origin_families': sorted({case['origins'][i]['family'] for i, s in enumerate(scores) if s[metric]}),
            'bounded_representatives_contain_correct': {mode: any(scores[i][metric]
                for i in case['allocations'][mode]['scored_indices']) for mode in MODES}}
            for metric in METRICS}})
    result = {'status': 'offline_opportunity_not_policy_success', 'n': len(rows), 'rows': rows,
        'metrics': {metric: {
            'initial_numerically_correct_cases': sum(r['metrics'][metric]['initial_correct'] for r in rows),
            'full_pool_contains_correct_cases': sum(r['metrics'][metric]['full_pool_contains_correct'] for r in rows),
            'initially_wrong_full_pool_rescuable': sum(not r['metrics'][metric]['initial_correct'] and r['metrics'][metric]['full_pool_contains_correct'] for r in rows),
            'bounded_representatives_contain_correct_cases': {mode: sum(r['metrics'][metric]['bounded_representatives_contain_correct'][mode] for r in rows) for mode in MODES},
            'initially_wrong_bounded_rescuable': {mode: sum(not r['metrics'][metric]['initial_correct'] and r['metrics'][metric]['bounded_representatives_contain_correct'][mode] for r in rows) for mode in MODES}}
            for metric in METRICS},
        'input_sha256': {str(p): sha(p) for p in (prior_path, snapshots.parent / 'manifest.json', source, pool_path, out / 'pool-seal.json')},
        'new_model_calls': 0, 'new_regeneration': False, 'actual_policy_gain': False, 'novelty_established': False,
        'limits': 'Reused24; original pool unchanged/sealed before reference answers. Numerical candidate-availability upper bound only, assuming a perfect selector over the budget-allocated representatives. No learned scoring, delivery safety or semantic adjudication. No candidate/order/budget tuning permitted from these oracle labels.3B vocab-only cost replay;7B model behavior/performance not evaluated.'}
    write(out / 'opportunity.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'input_sha256')}))


if __name__ == '__main__':
    main()
