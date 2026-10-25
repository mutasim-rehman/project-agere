"""Independently replay the complete original/extended training corpora.

Never calls the curriculum mutation functions. Checks literal programs against
the existing executor and both numerical annotation metrics, not semantic truth.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from evidence_calculator import execute
from tier8_artifact_paths import artifact_path
from tier8_v2_critic_data import ROOT, PROFILE, sha, prompt
from tier8_v2_financial_pipeline import evaluate_financial


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', required=True); p.add_argument('--extended', required=True)
    p.add_argument('--out', required=True); a = p.parse_args()
    base, extended, out = map(artifact_path, [a.base, a.extended, a.out])
    if out.exists():
        raise ValueError('Refuse overwrite')
    manifests = [json.loads((d / 'manifest.json').read_text()) for d in [base, extended]]
    paths = [artifact_path(m['output_file']) for m in manifests]
    for m, path in zip(manifests, paths):
        if sha(path) != m['output_sha256']:
            raise ValueError('Dataset hash changed')
    lines = [path.read_text().splitlines() for path in paths]
    if len(lines[0]) != len(lines[1]) or len(lines[0]) != 3522:
        raise ValueError('Original source-pair counts changed')
    prepared_paths = [ROOT / f'research/tier8_v2/data/finqa-cell-adaptation-{s}-02.jsonl'
                      for s in ['train', 'validation']]
    source = ROOT / '.local/datasets/finqa/train.json'
    for path in [*prepared_paths, source]:
        if sha(path) != manifests[0]['input_sha256'][str(path.relative_to(ROOT))]:
            raise ValueError('Original source changed')
    prepared = {r['source_id']: r for path in prepared_paths
                for r in map(json.loads, path.read_text().splitlines())}
    gold = {r['id']: r for r in json.loads(source.read_text())}
    decoder = json.JSONDecoder(); counts = Counter(); changed = Counter()
    tokens = {name: Counter() for name in ['original', 'extended']}
    ids = []; groups = {'train': set(), 'validation': set()}
    for before, after in zip(*lines):
        old, new = json.loads(before), json.loads(after)
        if old['source_id'] != new['source_id']:
            raise ValueError('Source order/identity changed')
        ids.append(new['source_id'])
        if old['target']['verdict'] == 'PASS' and before != after:
            raise ValueError('Reference row bytes changed')
        fixed = lambda r: {k: v for k, v in r.items() if k not in ['prompt', 'tokenization', 'mutation']}
        if fixed(old) != fixed(new):
            raise ValueError('Fields outside negative replacement changed')
        if old != new:
            changed[(new['split'], new['mutation']['kind'])] += 1
        groups[new['split']].add(new['report_group'])
        for name, example in [('original', old), ('extended', new)]:
            ident = example['original_source_id']; public = prepared[ident]['public']
            tail = example['prompt'].split('\nProposed program:\n', 1)[1]
            candidate, _ = decoder.raw_decode(tail)
            tail = tail.split('\nDeterministic execution:\n', 1)[1]
            saved, _ = decoder.raw_decode(tail)
            execution = execute(candidate['steps'], public['evidence'])
            if execution['issues'] or execution != saved or prompt(public, candidate, execution) != example['prompt']:
                raise ValueError('Program/source/execution/prompt does not replay: ' + ident)
            score = evaluate_financial(gold[ident], candidate, execution)
            expected = example['target']['verdict'] == 'PASS'
            if score['case_success'] != expected or score['raw_execution_match'] != expected:
                raise ValueError('Numerical annotation label does not replay: ' + ident)
            counts[(name, example['split'], example['target']['verdict'])] += 1
            tokens[name][example['split']] += example['tokenization'][PROFILE]['total_tokens']
    if len(ids) != len(set(ids)) or groups['train'] & groups['validation']:
        raise ValueError('Duplicate IDs or cross-split report overlap')
    result = {'pass': True, 'rows_replayed_per_condition': len(ids),
              'source_order_and_positive_row_bytes_identical': True,
              'labels': {'|'.join(k): v for k, v in counts.items()},
              'changed_negatives': {'|'.join(k): v for k, v in changed.items()},
              'group_counts': {k: len(v) for k, v in groups.items()},
              'teacher_forced_total_tokens': {k: dict(v) for k, v in tokens.items()},
              'input_sha256': {str(p): sha(p) for p in [*paths, *prepared_paths, source,
                                                       base / 'manifest.json', extended / 'manifest.json']},
              'code_sha256': {str(p): sha(p) for p in [Path(__file__), ROOT / 'scripts/evidence_calculator.py',
                                                     ROOT / 'scripts/tier8_v2_financial_pipeline.py']},
              'model_calls': 0, 'test_opened': False,
              'limits': 'Full numerical replay and source-support checks using training annotations, not independent semantic adjudication. Tokenization parity is a separate check. No training or performance gain claimed.'}
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['pass', 'rows_replayed_per_condition', 'changed_negatives', 'group_counts']}))


if __name__ == '__main__':
    main()
