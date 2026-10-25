"""Matched small continuation corpora, prepared without NN outcomes.

64 whole training quartets, current extended-mutation controls and fixed actor/
critic rehearsal. Only negative program inputs differ between trial conditions.
No training is launched; actual useful novelty remains an empirical question.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path

from evidence_calculator import execute
from tier8_artifact_paths import artifact_path
from tier8_v2_adaptation_prompts import tokenized_target
from tier8_v2_critic_artifact_audit import program_from_prompt
from tier8_v2_critic_data import prompt
from tier8_v2_financial_pipeline import evaluate_financial
from tier8_v2_posttrain_queue import sha, write
from tier8_v2_run import verified_models

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ('mas-3b-q4', 'sas-7b-q4')


def rank(kind, source):
    return hashlib.sha256(('continuation42|' + kind + '|' + source).encode()).hexdigest()


def extended_control(quartet, negatives, gold):
    control = deepcopy(quartet)
    for row in control:
        if row['target'] == {'verdict': 'PASS'}:
            continue
        negative = negatives[row['question_source_id']]
        text = negative['prompt']
        left, tail = text.split('\nFinancial report evidence by source ID:\n', 1)
        question = left.split('<|im_start|>user\nQuestion: ', 1)[1]
        original_evidence = json.JSONDecoder().raw_decode(tail)[0]
        if question != row['question'] or any(row['evidence'].get(k) != v for k, v in original_evidence.items()):
            raise ValueError('Extended control question/evidence differs')
        candidate = program_from_prompt(text)
        computed = execute(candidate['steps'], row['evidence'])
        measured = evaluate_financial(gold[row['question_source_id']], candidate, computed)
        if computed['issues'] or measured['case_success'] or measured['raw_execution_match']:
            raise ValueError('Extended control is not executable and wrong under both metrics')
        row.update(candidate=candidate, execution=computed,
            prompt=prompt({'question': row['question'], 'evidence': row['evidence']}, candidate, computed),
            program_source_id=row['question_source_id'] + '::existing_mutation',
            annotation_scope='Current extended-corpus mutation under common union evidence; weak numerical negative, not independently adjudicated financial semantics.',
            existing_mutation=negative.get('mutation'))
    return control


def select_replay(items, n, kind):
    """Hash order, prefer one source per report, then fill remaining by same hash."""
    ordered = sorted(items, key=lambda item: rank(kind, item[0]))
    result, used, reports = [], set(), set()
    for prefer_distinct_report in (True, False):
        for source, report, rows in ordered:
            if source in used or prefer_distinct_report and report in reports:
                continue
            used.add(source); reports.add(report); result.extend(rows)
            if len(used) == n:
                return result
    raise ValueError('Insufficient replay sources: ' + kind)


def build(out, quartet_root, extended_manifest, actor_manifest):
    from llama_cpp import Llama
    qm, audit = [json.loads((quartet_root / name).read_text()) for name in ('manifest.json', 'audit04.json')]
    qdata = artifact_path(qm['output_file'])
    if not audit['pass'] or sha(qdata) != audit['dataset_sha256'] or sha(quartet_root / 'manifest.json') != audit['dataset_manifest_sha256']:
        raise ValueError('Require canonical quartet source audit')
    em, am = [json.loads(p.read_text()) for p in (extended_manifest, actor_manifest)]
    edata, adata = artifact_path(em['output_file']), artifact_path(am['output_file'])
    if sha(edata) != em['output_sha256'] or sha(adata) != am['output_sha256']:
        raise ValueError('Rehearsal source changed')
    gold_path = ROOT / '.local/datasets/finqa/train.json'
    if qm['input_sha256'].get(str(gold_path)) != sha(gold_path):
        raise ValueError('Training annotation source changed')
    gold = {r['id']: r for r in json.loads(gold_path.read_text())}
    erows = [json.loads(s) for s in edata.read_text().splitlines()]
    arows = [json.loads(s) for s in adata.read_text().splitlines()]
    negatives = {r['original_source_id']: r for r in erows if r['target'] == {'verdict': 'FAIL'}}
    quartets = defaultdict(list)
    for row in map(json.loads, qdata.read_text().splitlines()):
        quartets[row['quartet_id']].append(row)
    weights = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / 'weights/tier8_v2')
    models = verified_models('sas', weights_root=str(weights)) + verified_models('mas', verifier_model='3b',
        use_selector=False, drafter_model='3b-q4', weights_root=str(weights))
    tokenizers = {}
    cache = {}
    def encode(row):
        key = (row['prompt'], json.dumps(row['target']))
        if key not in cache:
            cache[key] = {profile: tokenized_target(t, row['prompt'], row['target'], 1024) for profile, t in tokenizers.items()}
        row['tokenization'] = deepcopy(cache[key])
        return row
    rejected, selected_ids = Counter(), {'train': [], 'validation': []}
    crossed_train, mutation_train, validation = [], [], []
    excluded = {'train': set(), 'validation': set()}
    try:
        tokenizers[PROFILES[0]] = Llama(model_path=str(weights / 'qwen2.5-3b-instruct-q4_k_m.gguf'), vocab_only=True, verbose=False)
        tokenizers[PROFILES[1]] = Llama(model_path=str(weights / 'qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf'), vocab_only=True, verbose=False)
        training_reports = set()
        for key, quartet in sorted(quartets.items()):
            if len(quartet) != 4:
                raise ValueError('Incomplete source quartet')
            split, report = quartet[0]['split'], quartet[0]['report_group']
            if split == 'train' and (len(selected_ids['train']) == 64 or report in training_reports):
                continue
            control = extended_control(quartet, negatives, gold)
            candidate = deepcopy(quartet)
            try:
                for rows in (control, candidate):
                    for row in rows:
                        row['purpose'] = 'critic'
                        encode(row)
            except ValueError as exc:
                if str(exc) not in ('training_length_overflow', 'target_exceeds_deployment_output_allowance', 'deployment_reserve_overflow'):
                    raise
                rejected[split + '|' + str(exc)] += 1
                continue
            selected_ids[split].append(key)
            excluded[split].update(r['question_source_id'] for r in quartet)
            if split == 'train':
                training_reports.add(report)
                for control_row, candidate_row in zip(control, candidate):
                    control_row['source_id'] = 'new::' + control_row['source_id']
                    candidate_row['source_id'] = 'new::' + candidate_row['source_id']
                    control_row['family'] = candidate_row['family'] = 'new_training'
                mutation_train.extend(control); crossed_train.extend(candidate)
            else:
                for family, rows in (('crossed_validation', candidate), ('mutation_validation', control)):
                    for row in rows:
                        row['source_id'] = family + '::' + row['source_id']
                        row['family'] = family
                        validation.append(row)
        if len(selected_ids['train']) != 64 or not selected_ids['validation']:
            raise ValueError('Insufficient jointly eligible train/validation quartets')
        replays = {}
        for split, ncrit, nactor in [('train', 64, 128), ('validation', 16, 32)]:
            pairs = defaultdict(list)
            for row in erows:
                if row['split'] == split and row['original_source_id'] not in excluded[split]:
                    pairs[row['original_source_id']].append(row)
            if any(len(rows) != 2 or sorted(r['target']['verdict'] for r in rows) != ['FAIL', 'PASS'] for rows in pairs.values()):
                raise ValueError('Original critic replay pairs incomplete')
            critic = select_replay([(source, rows[0]['report_group'], rows) for source, rows in pairs.items()], ncrit, 'critic|' + split)
            actors = [r for r in arows if r['split'] == split and (split == 'validation' or r['source_id'] not in excluded[split])]
            actor = select_replay([(r['source_id'], r['report_group'], [r]) for r in actors], nactor, 'actor|' + split)
            for task, rows in [('critic', critic), ('drafter', actor)]:
                replays[(split, task)] = []
                for original in rows:
                    row = deepcopy(original)
                    row['source_id'] = 'replay_' + task + '::' + row['source_id']
                    row['purpose'], row['family'] = task, 'replay_' + task
                    replays[(split, task)].append(encode(row))
    finally:
        for tokenizer in tokenizers.values():
            tokenizer.close()
    critic_train = replays[('train', 'critic')]
    actor_train, actor_val = replays[('train', 'drafter')], replays[('validation', 'drafter')]
    critic_val = validation + replays[('validation', 'critic')]
    datasets = {'control_sas': mutation_train + critic_train + actor_train + critic_val + actor_val,
                'crossed_sas': crossed_train + critic_train + actor_train + critic_val + actor_val,
                'control_mas_critic': mutation_train + critic_train + critic_val,
                'crossed_mas_critic': crossed_train + critic_train + critic_val,
                'common_mas_actor': actor_train + actor_val}
    input_files = [quartet_root / 'manifest.json', quartet_root / 'audit04.json', qdata,
                   extended_manifest, edata, actor_manifest, adata, gold_path]
    manifests = {}
    for name, rows in datasets.items():
        if len({r['source_id'] for r in rows}) != len(rows):
            raise ValueError('Duplicate stage2 row IDs')
        train_reports = {r['report_group'] for r in rows if r['split'] == 'train'}
        val_reports = {r['report_group'] for r in rows if r['split'] == 'validation'}
        if train_reports & val_reports:
            raise ValueError('Cross-task report leakage')
        counts = Counter((r['split'], r['purpose']) for r in rows)
        ntrain = sum(v for (split, _), v in counts.items() if split == 'train')
        nval = len(rows) - ntrain
        joint = name.endswith('_sas')
        task_weights = {'drafter': 2., 'critic': 2 / 3} if joint else {rows[0]['purpose']: 1.}
        folder = out / name; folder.mkdir()
        data = folder / 'examples.jsonl'; data.write_text(''.join(json.dumps(r) + '\n' for r in rows))
        m = {'purpose': 'drafter' if joint or name == 'common_mas_actor' else 'critic',
            'training_tasks': ['drafter', 'critic'] if joint else [rows[0]['purpose']], 'profiles': list(PROFILES),
            'training_n': ntrain, 'validation_n': nval, 'kept_n': len(rows), 'planned_optimizer_updates': (ntrain + 7) // 8,
            'task_loss_weights': task_weights, 'task_counts': {'|'.join(k): v for k, v in counts.items()},
            'max_training_tokens': 1024, 'deployment_context': 4096, 'output_file': str(data), 'output_sha256': sha(data),
            'input_sha256': {str(p): sha(p) for p in input_files}, 'script_sha256': sha(Path(__file__)),
            'model_calls': 0, 'trained': False, 'actual_qa_gain': False, 'novelty_established': False}
        write(folder / 'manifest.json', m); manifests[name] = m
    # Enforce all intended controls before publishing a usable corpus bundle.
    for left, right in [('control_sas', 'crossed_sas'), ('control_mas_critic', 'crossed_mas_critic')]:
        a, b = datasets[left], datasets[right]
        if [(r['source_id'], r['split'], r['report_group'], r['purpose'], r['target']) for r in a] != [
                (r['source_id'], r['split'], r['report_group'], r['purpose'], r['target']) for r in b]:
            raise ValueError('Training source/label controls differ')
        for x, y in zip(a, b):
            if x['prompt'] != y['prompt'] and not (x['family'] == y['family'] == 'new_training' and x['target'] == {'verdict': 'FAIL'}):
                raise ValueError('Only new negative program inputs may differ')
            if x['family'] != 'new_training' or x['target'] == {'verdict': 'PASS'}:
                if x != y:
                    raise ValueError('Positive/replay/validation records differ')
    summary = {'status': 'prepared_not_trained', 'datasets': {k: {'training_n': m['training_n'], 'validation_n': m['validation_n'],
        'optimizer_updates': m['planned_optimizer_updates'], 'dataset_sha256': m['output_sha256'],
        'training_tokens': sum(r['tokenization']['sas-7b-q4']['total_tokens'] for r in datasets[k] if r['split'] == 'train')}
        for k, m in manifests.items()}, 'selected_quartets': selected_ids, 'rejected_quartets': dict(rejected),
        'same_positives_replay_validation_and_sources': True, 'source_sha256': sha(Path(__file__)),
        'limits': 'Conditional matched-study preparation, not authorization to skip baseline probe.64 new train quartets;128 critic and128 actor rehearsal rows. Common validation includes both crossed and mutation families with repeated positive observations; not independent samples. Replay weakens exact marginal balance of complete mixture. Equal updates/task examples not identical compute, optimizer state or SAS/MAS parameter sharing. Novel useful gain unproven.'}
    write(out / 'summary.json', summary)
    print(json.dumps({k: summary[k] for k in ('status', 'datasets', 'rejected_quartets')}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--quartets', required=True); p.add_argument('--extended-manifest', required=True)
    p.add_argument('--actor-manifest', default='research/tier8_v2/evidence/deployment-sft-1024-02.json')
    p.add_argument('--out', required=True); args = p.parse_args()
    out = artifact_path(args.out); out.mkdir(parents=True, exist_ok=False)
    build(out, artifact_path(args.quartets), artifact_path(args.extended_manifest), artifact_path(args.actor_manifest))


if __name__ == '__main__':
    main()
