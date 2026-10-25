"""Controlled verifier-corpus extension with unchanged sources and positives.

Known augmentation: output scaling and executable subexpression projection.
Never train on inspected dev errors. All original pairs remain; overlength or
ineligible replacements fall back to the original negative, with counts recorded.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re

from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import execute
from tier8_artifact_paths import artifact_path
from tier8_v2_adaptation_data import validate_prepared
from tier8_v2_adaptation_prompts import tokenized_target
from tier8_v2_critic_data import ROOT, PROFILE, prompt, sha, parity
from tier8_v2_financial_pipeline import evaluate_financial


def rank(source, value):
    return hashlib.sha256(('critic-extension42|' + source + '|' +
                           json.dumps(value, sort_keys=True)).encode()).hexdigest()


def proposals(target):
    steps = target['steps']
    if target.get('decision') != 'ANSWER' or not steps:
        return
    if len(steps) < 8:
        for op in ['multiply', 'divide']:
            candidate = deepcopy(target)
            candidate['steps'].append({'op': op, 'left': '#' + str(len(steps) - 1),
                                       'right': 'CONST:100'})
            yield candidate, {'kind': 'output_scale', 'op': op, 'factor': 100}
    for index, step in enumerate(steps[:-1]):
        if not any(later[side] == '#' + str(index) for later in steps[index + 1:]
                   for side in ['left', 'right']):
            continue
        for side in ['left', 'right']:
            candidate = deepcopy(target)
            del candidate['steps'][index]
            for later in candidate['steps'][index:]:
                for operand in ['left', 'right']:
                    ref = later[operand]
                    if ref == '#' + str(index):
                        ref = step[side]
                    if ref.startswith('#') and int(ref[1:]) > index:
                        ref = '#' + str(int(ref[1:]) - 1)
                    later[operand] = ref
            yield candidate, {'kind': 'node_bypass', 'step': index, 'keep_operand': side}


def extension_candidates(row, gold):
    atoms = atom_catalog(row['public']['evidence'])
    for target, change in proposals(row['target']):
        compiled = compile_plan(target, atoms)
        result = execute(compiled['steps'], row['public']['evidence'])
        if result['issues']:
            continue
        score = evaluate_financial(gold, compiled, result)
        if not score['case_success'] and not score['raw_execution_match']:
            yield compiled, result, change


def selected_extension(source, choices):
    # Half the source IDs are nominated, before outcome-dependent eligibility.
    # No repeat-until-success or reallocation of failed replacement quotas.
    if int(rank(source, 'nominate'), 16) % 2 or not choices:
        return None
    families = sorted({c[2]['kind'] for c in choices})
    family = families[int(rank(source, 'family'), 16) % len(families)]
    return min((c for c in choices if c[2]['kind'] == family), key=lambda c: rank(source, c[2]))


def paired(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row['original_source_id']].append(row)
    for source, pair in groups.items():
        if (len(pair) != 2 or {r['target']['verdict'] for r in pair} != {'PASS', 'FAIL'}
                or len({r['split'] for r in pair}) != 1
                or len({r['report_group'] for r in pair}) != 1):
            raise ValueError('Require original balanced source pairs: ' + source)
        for row in pair:
            suffix = 'reference' if row['target']['verdict'] == 'PASS' else 'mutation'
            if row['source_id'] != source + '::' + suffix:
                raise ValueError('Unexpected source identity')
    return groups


def build(base, out):
    from llama_cpp import Llama
    original = json.loads((base / 'manifest.json').read_text())
    original_file = artifact_path(original['output_file'])
    if (original.get('purpose') != 'critic' or sha(original_file) != original['output_sha256']
            or original['output_sha256'] != '7b63467ad3da713c8a9accd17fe3311fffc9d0d0cdd4e61d02d573fc99fc69d0'
            or original['training_n'] != 3140 or original['validation_n'] != 382):
        raise ValueError('Require the original pinned critic corpus')
    original_rows = [json.loads(s) for s in original_file.read_text().splitlines()]
    pairs = paired(original_rows)
    prepared_paths = [ROOT / f'research/tier8_v2/data/finqa-cell-adaptation-{s}-02.jsonl'
                      for s in ['train', 'validation']]
    source = ROOT / '.local/datasets/finqa/train.json'
    for path in [*prepared_paths, source]:
        if original['input_sha256'][str(path.relative_to(ROOT))] != sha(path):
            raise ValueError('Original training source changed')
    prepared = {r['source_id']: r for p in prepared_paths
                for r in map(json.loads, p.read_text().splitlines())}
    gold = {r['id']: r for r in json.loads(source.read_text())}
    model = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) /
                          'weights/tier8_v2/qwen2.5-3b-instruct-q4_k_m.gguf')
    pin = ROOT / 'research/tier8_v2/evidence/candidate-model-3b.json'
    if sha(model) != json.loads(pin.read_text())['sha256']:
        raise ValueError('Pinned tokenizer GGUF differs')
    tokenizer = Llama(model_path=str(model), vocab_only=True, n_gpu_layers=0, verbose=False)
    replacements = {}; reasons = Counter(); counts = Counter(); eligibility = Counter()
    try:
        for ident, pair in pairs.items():
            row = prepared[ident]; validate_prepared(row)
            reference = next(r for r in pair if r['target']['verdict'] == 'PASS')
            negative = next(r for r in pair if r['target']['verdict'] == 'FAIL')
            positive = compile_plan(row['target'], atom_catalog(row['public']['evidence']))
            execution = execute(positive['steps'], row['public']['evidence'])
            if reference['prompt'] != prompt(row['public'], positive, execution):
                raise ValueError('Original reference prompt cannot be reproduced')
            choices = list(extension_candidates(row, gold[ident]))
            eligibility.update({c[2]['kind'] for c in choices})
            choice = selected_extension(ident, choices)
            if choice is None:
                reasons['not_nominated_or_no_valid_extension'] += 1
                continue
            candidate, computed, change = choice
            rendered = prompt(row['public'], candidate, computed)
            try:
                tokens = tokenized_target(tokenizer, rendered, negative['target'], 1024)
            except ValueError as exc:
                reasons['fallback_' + str(exc)] += 1
                continue
            replacement = deepcopy(negative)
            replacement.update(prompt=rendered, mutation=change)
            replacement['tokenization'][PROFILE] = tokens
            replacements[negative['source_id']] = replacement
            counts[change['kind']] += 1
    finally:
        tokenizer.close()
    rows = [replacements.get(r['source_id'], r) for r in original_rows]
    if (len(rows) != original['kept_n'] or [r['source_id'] for r in rows] !=
            [r['source_id'] for r in original_rows]
            or any(a != b for a, b in zip(rows, original_rows) if b['target']['verdict'] == 'PASS')):
        raise ValueError('Source order/count or reference changed')
    if not replacements or set(counts) != {'output_scale', 'node_bypass'}:
        raise ValueError('Both planned extension families must be represented')
    output = out / 'examples.jsonl'
    output.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    totals = lambda items: {split: sum(r['tokenization'][PROFILE]['total_tokens'] for r in items
                                     if r['split'] == split) for split in ['train', 'validation']}
    report = {**original, 'output_file': str(output), 'output_sha256': sha(output),
              'base_manifest': str(base / 'manifest.json'), 'base_manifest_sha256': sha(base / 'manifest.json'),
              'base_dataset_sha256': sha(original_file),
              'curriculum': 'Source-ID SHA42 nominates half the original pairs; choose eligible new family then candidate by SHA. Preserve original negative if not nominated, no eligible extension, or complete prompt exceeds1024. No quota reallocation.',
              'base_selection': original['selection'],
              'selection': 'Original frozen pairs/positives/order; negative replacements follow curriculum below; unchanged negatives retain original base_selection.',
              'replacement_counts': dict(counts), 'extension_eligible_sources': dict(eligibility),
              'unchanged_negative_reasons': dict(reasons),
              'all_source_ids_splits_and_reference_rows_identical': True,
              'training_optimizer_updates': (original['training_n'] + 7) // 8,
              'teacher_forced_total_tokens': {'original': totals(original_rows), 'extended': totals(rows)},
              'balance': 'Exactly same one positive/negative pair per original source, in identical order; only selected negative prompts/programs change.',
              'mutation_counts': dict(Counter(r['mutation']['kind'] for r in rows if r['mutation'])),
              'model_calls': 0, 'test_opened': False,
              'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in [
                  Path(__file__), ROOT / 'scripts/tier8_v2_critic_data.py',
                  ROOT / 'scripts/evidence_atoms.py', ROOT / 'scripts/evidence_calculator.py',
                  ROOT / 'scripts/tier8_v2_financial_pipeline.py', ROOT / 'scripts/tier8_v2_adaptation_prompts.py']},
              'limits': 'Known training augmentation, inspired by reused-development failure analysis; not novel or independent confirmation. Weak numerical labels, not semantic adjudication or natural-error corpus. Same sources/positives/splits/update count; token expenditure can differ and is reported. No training, deployment or QA improvement follows from preparing this corpus.'}
    report['input_sha256'] = {**original['input_sha256'], str(base / 'manifest.json'): sha(base / 'manifest.json'),
                              str(original_file): sha(original_file), str(pin.relative_to(ROOT)): sha(pin)}
    (out / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['kept_n', 'replacement_counts', 'unchanged_negative_reasons',
                                           'teacher_forced_total_tokens', 'training_optimizer_updates']}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['build', 'parity'])
    p.add_argument('--base', required=True); p.add_argument('--run-id', required=True)
    a = p.parse_args()
    if not re.fullmatch('[a-zA-Z0-9_-]+', a.run_id):
        raise ValueError('Unsafe run ID')
    out = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / 'datasets/tier8_v2_critic' / a.run_id)
    if a.mode == 'build':
        out.mkdir(parents=True, exist_ok=False)
        build(artifact_path(a.base), out)
    else:
        parity(out)


if __name__ == '__main__':
    main()
