"""Independently replay quartet labels, marginal counts and both HF tokenizers.

No neural calls. Label verification uses the same disclosed numerical definitions,
so it is not independent financial adjudication. All source evidence is replayed.
Do not treat construction balance or token parity as actual QA improvement.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path

from evidence_calculator import execute
from tier8_artifact_paths import artifact_path
from tier8_v2_critic_artifact_audit import features, fit_tree, predict
from tier8_v2_financial_pipeline import evaluate_financial
from tier8_v2_posttrain_queue import sha, write
from tier8_v2_critic_data import prompt
from tier8_v2_critic_artifact_audit import program_from_prompt

ROOT = Path(__file__).resolve().parents[1]


def audit(root):
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
    from transformers import AutoTokenizer, __version__
    import tokenizers
    manifest = json.loads((root / 'manifest.json').read_text())
    data = artifact_path(manifest['output_file'])
    if sha(data) != manifest['output_sha256']:
        raise ValueError('Dataset changed')
    for name, digest in manifest['input_sha256'].items():
        if sha(artifact_path(name)) != digest:
            raise ValueError('Construction source changed')
    gold_path = ROOT / '.local/datasets/finqa/train.json'
    gold = {r['id']: r for r in json.loads(gold_path.read_text())}
    source_path = next(artifact_path(p) for p in manifest['input_sha256'] if p.endswith('/examples.jsonl'))
    originals = {}
    for record in map(json.loads, source_path.read_text().splitlines()):
        if record['target'] != {'verdict': 'PASS'}:
            continue
        evidence = json.JSONDecoder().raw_decode(record['prompt'].split('\nFinancial report evidence by source ID:\n', 1)[1])[0]
        originals[record['original_source_id']] = {**record, 'candidate': program_from_prompt(record['prompt']), 'evidence': evidence}
    rows = [json.loads(s) for s in data.read_text().splitlines()]
    if len(rows) != manifest['kept_n'] or len({r['source_id'] for r in rows}) != len(rows):
        raise ValueError('Row count or uniqueness')
    groups, report_splits, marginals = defaultdict(list), defaultdict(set), defaultdict(Counter)
    quartet_sources = defaultdict(set)
    for row in rows:
        quartet_sources[row['quartet_id']].add(row['question_source_id'])
    examples = []
    joint_labels = defaultdict(set)
    for row in rows:
        joint_labels[row['prompt']].add(row['target']['verdict'])
        q, p = originals[row['question_source_id']], originals[row['program_source_id']]
        if (row['question'] != gold[row['question_source_id']]['qa']['question'] or row['candidate'] != p['candidate']
                or row['report_group'] != q['report_group'] or row['report_group'] != p['report_group']
                or row['split'] != q['split'] or row['split'] != p['split']
                or row['question_source_id'].rsplit('.pdf-', 1)[0] != row['program_source_id'].rsplit('.pdf-', 1)[0]):
            raise ValueError('Source question/program/page/split identity differs')
        expected_evidence = {}
        for source_id in sorted(quartet_sources[row['quartet_id']]):
            for key, text in originals[source_id]['evidence'].items():
                if key in expected_evidence and expected_evidence[key] != text:
                    raise ValueError('Original source collision')
                expected_evidence[key] = text
        if row['evidence'] != expected_evidence:
            raise ValueError('Evidence is not exactly the source union')
        groups[row['quartet_id']].append(row)
        report_splits[row['report_group']].add(row['split'])
        computed = execute(row['candidate']['steps'], row['evidence'])
        if computed != row['execution'] or computed['issues']:
            raise ValueError('Execution replay differs')
        if prompt({'question': row['question'], 'evidence': row['evidence']}, row['candidate'], computed) != row['prompt']:
            raise ValueError('Model prompt is not the audited question/evidence/program')
        score = evaluate_financial(gold[row['question_source_id']], row['candidate'], computed)
        positive = row['question_source_id'] == row['program_source_id']
        if row['target'] != {'verdict': 'PASS' if positive else 'FAIL'}:
            raise ValueError('Crossed identity label differs')
        if (positive and not (score['case_success'] and score['raw_execution_match']) or
                not positive and (score['case_success'] or score['raw_execution_match'])):
            raise ValueError('Numerical annotation label differs')
        for view in ('question', 'candidate'):
            key = (row['split'], view, json.dumps([row['evidence'], row[view]], sort_keys=True))
            marginals[key][positive] += 1
        examples.append({'x': features(row['candidate']), 'y': int(positive), 'split': row['split']})
    if any(len(splits) != 1 for splits in report_splits.values()):
        raise ValueError('Report split leakage')
    for quartet in groups.values():
        if len(quartet) != 4 or len({json.dumps(r['evidence'], sort_keys=True) for r in quartet}) != 1:
            raise ValueError('Quartet incomplete or evidence differs')
        if len({r['candidate']['answer_unit'] for r in quartet}) != 1:
            raise ValueError('Quartet units differ')
        qs, ps = {r['question_source_id'] for r in quartet}, {r['program_source_id'] for r in quartet}
        if len(qs) != 2 or qs != ps or {(r['question_source_id'], r['program_source_id']) for r in quartet} != {(q, p) for q in qs for p in ps}:
            raise ValueError('Not complete2x2 crossing')
    if any(count[True] != count[False] or count[True] == 0 for count in marginals.values()):
        raise ValueError('Observable marginal label imbalance')
    if any(len(labels) != 1 for labels in joint_labels.values()):
        raise ValueError('Identical full model input has conflicting labels')
    tree = fit_tree([r for r in examples if r['split'] == 'train'], sorted(examples[0]['x']), depth=3)
    artifact_accuracy = {split: sum(predict(tree, r['x']) == r['y'] for r in examples if r['split'] == split)
                         / sum(r['split'] == split for r in examples) for split in ('train', 'validation')}
    if set(artifact_accuracy.values()) != {0.5}:
        raise ValueError('Question-blind artifact control exceeds balance')
    snapshots = ROOT / 'research/tier8_v2/evidence/hf-tokenizer-snapshots-01.json'
    pinned = json.loads(snapshots.read_text())['profiles']
    profiles = {}
    for profile in manifest['profiles']:
        asset = pinned[profile]
        folder = artifact_path(asset['folder'])
        for file in asset['files']:
            if sha(folder / file['file']) != file['sha256']:
                raise ValueError('Tokenizer asset changed')
        tokenizer = AutoTokenizer.from_pretrained(str(folder), local_files_only=True, trust_remote_code=False)
        for row in rows:
            saved = row['tokenization'][profile]
            prefix = tokenizer.encode(row['prompt'], add_special_tokens=False)
            full = tokenizer.encode(row['prompt'] + saved['response'], add_special_tokens=False)
            if (full[:len(prefix)] != prefix or len(prefix) != saved['label_mask_prefix_tokens']
                    or len(full) != saved['total_tokens'] or len(full) > 1024
                    or hashlib.sha256(json.dumps(full).encode()).hexdigest() != saved['input_ids_sha256']):
                raise ValueError('HF/GGUF parity differs: ' + row['source_id'])
        profiles[profile] = {'pass': True, 'n': len(rows)}
    return {'pass': True, 'n': len(rows), 'quartets': len(groups), 'profiles': profiles,
        'dataset_sha256': sha(data), 'dataset_manifest_sha256': sha(root / 'manifest.json'),
        'transformers_version': __version__, 'tokenizers_version': tokenizers.__version__,
        'snapshots_sha256': sha(snapshots), 'source_sha256': sha(Path(__file__)),
        'question_blind_tree_train_validation_accuracy': artifact_accuracy, 'marginal_balance_verified_per_split': True,
        'source_question_program_and_union_verified': True, 'actual_model_prompt_binding_verified': True,
        'distinct_full_model_prompts': len(joint_labels), 'conflicting_identical_prompt_labels': 0,
        'model_calls': 0, 'actual_qa_gain': False, 'novelty_established': False,
        'limits': 'Independent data/execution/tokenization replay under existing weak numerical labels. No independent financial semantics, trained improvement or new-algorithm priority follows. Exact50% bound applies only to complete balanced marginal views; joint shortcuts remain possible.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--out')
    args = parser.parse_args()
    root = artifact_path(args.root)
    output = artifact_path(args.out) if args.out else root / 'parity.json'
    if output.exists():
        raise ValueError('No overwrite')
    result = audit(root)
    write(output, result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
