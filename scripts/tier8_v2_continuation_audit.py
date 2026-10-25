"""Replay matched continuation controls, weak labels and both tokenizer profiles.

No model inference. This audits preparation only, including identical positives,
rehearsal and validation, and exact SAS/MAS task-example exposure. Numerical
annotation replay is not independent financial-expert adjudication.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path

from evidence_calculator import execute
from tier8_artifact_paths import artifact_path
from tier8_v2_critic_artifact_audit import program_from_prompt
from tier8_v2_critic_data import prompt
from tier8_v2_financial_pipeline import evaluate_financial
from tier8_v2_posttrain_queue import sha, write

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('control_sas', 'crossed_sas', 'control_mas_critic', 'crossed_mas_critic', 'common_mas_actor')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def audit(root):
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
    from transformers import AutoTokenizer, __version__
    import tokenizers
    manifests, datasets = {}, {}
    for name in NAMES:
        manifest = json.loads((root / name / 'manifest.json').read_text())
        data = artifact_path(manifest['output_file'])
        if sha(data) != manifest['output_sha256']:
            raise ValueError('Dataset changed: ' + name)
        for path, digest in manifest['input_sha256'].items():
            if sha(artifact_path(path)) != digest:
                raise ValueError('Source input changed: ' + path)
        rows = [json.loads(s) for s in data.read_text().splitlines()]
        if len({r['source_id'] for r in rows}) != len(rows) or len(rows) != manifest['kept_n']:
            raise ValueError('Dataset duplicate IDs/count')
        if sum(r['split'] == 'train' for r in rows) != manifest['training_n'] or sum(r['split'] == 'validation' for r in rows) != manifest['validation_n']:
            raise ValueError('Split counts differ')
        train = {r['report_group'] for r in rows if r['split'] == 'train'}
        val = {r['report_group'] for r in rows if r['split'] == 'validation'}
        if train & val:
            raise ValueError('Report leakage')
        labels = defaultdict(set)
        for row in rows:
            labels[row['prompt']].add(canonical(row['target']))
        if any(len(values) != 1 for values in labels.values()):
            raise ValueError('Contradictory identical full inputs')
        manifests[name], datasets[name] = manifest, rows
    sources = manifests['control_sas']['input_sha256']
    qmanifest = next(artifact_path(p) for p in sources if p.endswith('/critic_quartets_01/manifest.json'))
    em = next(artifact_path(p) for p in sources if p.endswith('/critic_extended_sft_02/manifest.json'))
    am = next(artifact_path(p) for p in sources if p.endswith('/deployment-sft-1024-02.json'))
    qm, extended, actor = [json.loads(p.read_text()) for p in (qmanifest, em, am)]
    quad = {r['source_id']: r for r in map(json.loads, artifact_path(qm['output_file']).read_text().splitlines())}
    original_critic = {r['source_id']: r for r in map(json.loads, artifact_path(extended['output_file']).read_text().splitlines())}
    original_actor = {r['source_id']: r for r in map(json.loads, artifact_path(actor['output_file']).read_text().splitlines())}
    negative = {r['original_source_id']: r for r in original_critic.values() if r['target'] == {'verdict': 'FAIL'}}
    gold = {r['id']: r for r in json.loads((ROOT / '.local/datasets/finqa/train.json').read_text())}
    # Replay source binding once across the union of rows shared by datasets.
    seen = set()
    for name, rows in datasets.items():
        for row in rows:
            fingerprint = canonical(row)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            if row['family'].startswith('replay_'):
                key = row['source_id'].split('::', 1)[1]
                original = original_actor[key] if row['purpose'] == 'drafter' else original_critic[key]
                for field in ('prompt', 'target', 'split', 'report_group'):
                    if row[field] != original[field]:
                        raise ValueError('Rehearsal source differs')
                continue
            key = row['source_id'].split('::', 1)[1]
            original = quad[key]
            for field in ('question', 'evidence', 'target', 'split', 'report_group', 'quartet_id', 'question_source_id'):
                if row[field] != original[field]:
                    raise ValueError('New-source control differs: ' + field)
            mutation = row['family'] == 'mutation_validation' or name.startswith('control_') and row['family'] == 'new_training'
            expected_candidate = program_from_prompt(negative[row['question_source_id']]['prompt']) if mutation and row['target'] == {'verdict': 'FAIL'} else original['candidate']
            if row['candidate'] != expected_candidate:
                raise ValueError('Proposed program is not the declared intervention')
            computed = execute(row['candidate']['steps'], row['evidence'])
            if computed['issues'] or computed != row['execution']:
                raise ValueError('Execution replay differs')
            measured = evaluate_financial(gold[row['question_source_id']], row['candidate'], computed)
            positive = row['target'] == {'verdict': 'PASS'}
            if positive and not (measured['case_success'] and measured['raw_execution_match']) or not positive and (measured['case_success'] or measured['raw_execution_match']):
                raise ValueError('Weak numerical label differs')
            if row['prompt'] != prompt({'question': row['question'], 'evidence': row['evidence']}, row['candidate'], computed):
                raise ValueError('Actual model input differs from audited record')
    differences = {}
    for left, right in [('control_sas', 'crossed_sas'), ('control_mas_critic', 'crossed_mas_critic')]:
        a, b = datasets[left], datasets[right]
        if len(a) != len(b):
            raise ValueError('Unmatched condition lengths')
        changed = 0
        for x, y in zip(a, b):
            for key in ('source_id', 'split', 'report_group', 'purpose', 'target', 'family'):
                if x[key] != y[key]:
                    raise ValueError('Unmatched paired controls')
            if x != y:
                if x['family'] != 'new_training' or x['target'] != {'verdict': 'FAIL'}:
                    raise ValueError('Positive/rehearsal/validation changed')
                if x['question'] != y['question'] or x['evidence'] != y['evidence']:
                    raise ValueError('Negative question/evidence changed')
                changed += x['prompt'] != y['prompt']
        differences[left + '_to_' + right] = {'changed_negative_prompts': changed}
    common_actor = datasets['common_mas_actor']
    for condition in ('control', 'crossed'):
        joint = datasets[condition + '_sas']
        if [r for r in joint if r['purpose'] == 'drafter'] != common_actor:
            raise ValueError('SAS/MAS actor exposure differs')
        if [r for r in joint if r['purpose'] == 'critic'] != datasets[condition + '_mas_critic']:
            raise ValueError('SAS/MAS critic exposure differs')
    new_rows = [r for r in datasets['crossed_sas'] if r['family'] == 'new_training']
    for view in ('candidate', 'question'):
        counts = defaultdict(Counter)
        for row in new_rows:
            counts[canonical([row['evidence'], row[view]])][row['target']['verdict']] += 1
        if any(c['PASS'] != c['FAIL'] for c in counts.values()):
            raise ValueError('New crossed rows lost marginal balance')
    snapshots = ROOT / 'research/tier8_v2/evidence/hf-tokenizer-snapshots-01.json'
    pins = json.loads(snapshots.read_text())['profiles']
    reports, hf_cache = {}, {}
    for profile in manifests['control_sas']['profiles']:
        asset = pins[profile]; folder = artifact_path(asset['folder'])
        if any(sha(folder / f['file']) != f['sha256'] for f in asset['files']):
            raise ValueError('Tokenizer source changed')
        tokenizer = AutoTokenizer.from_pretrained(str(folder), local_files_only=True, trust_remote_code=False)
        for name, rows in datasets.items():
            for row in rows:
                saved = row['tokenization'][profile]
                if saved['response'] != json.dumps(row['target']) + '<|im_end|>':
                    raise ValueError('Encoded response does not match training target')
                key = (profile, row['prompt'], saved['response'])
                if key not in hf_cache:
                    prefix = tokenizer.encode(row['prompt'], add_special_tokens=False)
                    full = tokenizer.encode(row['prompt'] + saved['response'], add_special_tokens=False)
                    hf_cache[key] = (full[:len(prefix)] == prefix, len(prefix), len(full), hashlib.sha256(json.dumps(full).encode()).hexdigest())
                boundary, prefix_n, total_n, digest = hf_cache[key]
                if (not boundary or prefix_n != saved['label_mask_prefix_tokens'] or prefix_n != saved['prompt_tokens']
                        or total_n != saved['total_tokens'] or total_n > 1024 or digest != saved['input_ids_sha256']):
                    raise ValueError('Tokenizer parity differs')
            reports.setdefault(name, {})[profile] = {'pass': True, 'n': len(rows)}
    for name, manifest in manifests.items():
        report = {'pass': True, 'n': manifest['kept_n'], 'profiles': reports[name],
            'dataset_sha256': manifest['output_sha256'], 'dataset_manifest_sha256': sha(root / name / 'manifest.json'),
            'transformers_version': __version__, 'tokenizers_version': tokenizers.__version__, 'source_sha256': sha(Path(__file__)),
            'source_binding_and_labels_replayed': True, 'model_calls': 0, 'actual_qa_gain': False}
        if (root / name / 'parity.json').exists():
            raise ValueError('Refuse parity overwrite')
        write(root / name / 'parity.json', report)
    stats = {}
    for name, rows in datasets.items():
        stats[name] = {'n_train': manifests[name]['training_n'], 'n_validation': manifests[name]['validation_n'],
            'report_groups': {s: len({r['report_group'] for r in rows if r['split'] == s}) for s in ('train', 'validation')},
            'families': dict(Counter(r['split'] + '|' + r['family'] for r in rows)),
            'training_tokens': {p: sum(r['tokenization'][p]['total_tokens'] for r in rows if r['split'] == 'train') for p in reports[name]}}
    return {'pass': True, 'dataset_statistics': stats, 'paired_differences': differences,
        'same_positives_rehearsal_validation': True, 'same_sas_mas_task_rows': True,
        'new_crossed_training_marginals_balanced': True, 'new_crossed_train_rows': len(new_rows),
        'replay_mixture_fully_marginal_balanced': False, 'all_targets_bound_to_actual_encoded_responses': True,
        'source_sha256': sha(Path(__file__)), 'source_manifests_sha256': {name: sha(root / name / 'manifest.json') for name in NAMES},
        'model_calls': 0, 'actual_qa_gain': False, 'novelty_established': False,
        'limits': 'Preparation replay only. Validation positive records repeat across families and are not independent observations. Exact marginal balance applies to new256 rows, not the mixed rehearsal corpus. Weak numerical labels, not independent financial adjudication. Equal updates are not identical tokens/optimizer behavior.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True); args = p.parse_args()
    root = artifact_path(args.root)
    if (root / 'audit.json').exists():
        raise ValueError('Refuse audit overwrite')
    result = audit(root); write(root / 'audit.json', result)
    print(json.dumps({'pass': result['pass'], 'paired_differences': result['paired_differences'], 'new_crossed_train_rows': len([1] * result['new_crossed_train_rows'])}))


if __name__ == '__main__':
    main()
