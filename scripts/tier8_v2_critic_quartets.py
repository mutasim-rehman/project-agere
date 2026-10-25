"""Same-page crossed question/program quartets with exact marginal balance.

Known contrastive-instance construction, not a first-use/novelty claim. Positives
reuse original annotated programs; negatives must fail both current metrics for
the other question. All four records use identical union evidence and answer unit.
Reject the entire quartet on any conflict, ambiguous label or1024-token overflow.
No neural calls, natural development outcomes or test data enter construction.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import itertools
import json
import os
from pathlib import Path
import re

from evidence_calculator import execute
from tier8_artifact_paths import artifact_path
from tier8_v2_adaptation_prompts import tokenized_target
from tier8_v2_critic_data import prompt
from tier8_v2_financial_pipeline import evaluate_financial
from tier8_v2_posttrain_queue import sha, write
from tier8_v2_run import verified_models

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ('mas-3b-q4', 'sas-7b-q4')


def parse_reference(row):
    if row['target'] != {'verdict': 'PASS'}:
        raise ValueError('Reference positives only')
    text = row['prompt']
    marker = '\nFinancial report evidence by source ID:\n'
    if text.count(marker) != 1:
        raise ValueError('Ambiguous evidence marker')
    left, tail = text.split(marker)
    question = left.split('<|im_start|>user\nQuestion: ', 1)[1]
    decoder = json.JSONDecoder()
    evidence, offset = decoder.raw_decode(tail)
    tail = tail[offset:]
    prefix = '\nProposed program:\n'
    if not tail.startswith(prefix):
        raise ValueError('Program boundary')
    candidate, offset = decoder.raw_decode(tail[len(prefix):])
    computed = execute(candidate['steps'], evidence)
    public = {'question': question, 'evidence': evidence}
    if computed['issues'] or prompt(public, candidate, computed) != text:
        raise ValueError('Positive prompt does not roundtrip exactly')
    match = re.fullmatch(r'(.+\.pdf)-\d+', row['original_source_id'])
    if not match:
        raise ValueError('Page identity')
    return {'id': row['original_source_id'], 'report_group': row['report_group'], 'page': match[1],
            'split': row['split'], 'public': public, 'candidate': candidate}


def crossed(left, right, gold):
    """Return all four records together; the caller must filter them together."""
    if (left['id'] == right['id'] or left['page'] != right['page'] or
            left['split'] != right['split'] or left['report_group'] != right['report_group']):
        raise ValueError('Not two same-page/split/report sources')
    if left['public']['question'] == right['public']['question']:
        raise ValueError('Same question')
    if left['candidate']['answer_unit'] != right['candidate']['answer_unit']:
        raise ValueError('Different units')
    evidence = dict(left['public']['evidence'])
    for key, text in right['public']['evidence'].items():
        if key in evidence and evidence[key] != text:
            raise ValueError('Source span collision')
        evidence[key] = text
    evidence = dict(sorted(evidence.items()))
    sources = [left, right]
    quartet = []
    for qi, pi in itertools.product(range(2), repeat=2):
        q, p = sources[qi], sources[pi]
        candidate = deepcopy(p['candidate'])
        computed = execute(candidate['steps'], evidence)
        if computed['issues']:
            raise ValueError('Union evidence execution')
        measured = evaluate_financial(gold[q['id']], candidate, computed)
        positive = qi == pi
        if positive and not (measured['case_success'] and measured['raw_execution_match']):
            raise ValueError('Reference label ambiguity')
        if not positive and (measured['case_success'] or measured['raw_execution_match']):
            raise ValueError('Cross program not wrong under both metrics')
        public = {'question': q['public']['question'], 'evidence': evidence}
        quartet.append({'question_source_id': q['id'], 'program_source_id': p['id'],
            'question': public['question'], 'evidence': evidence, 'candidate': candidate,
            'execution': computed, 'prompt': prompt(public, candidate, computed),
            'target': {'verdict': 'PASS' if positive else 'FAIL'},
            'report_group': q['report_group'], 'split': q['split']})
    verify_balance(quartet)
    return quartet


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def verify_balance(rows):
    """Each observable marginal appears equally with PASS and FAIL.

    Guarantees apply to classifiers restricted to these marginals, not arbitrary
    joint shortcuts such as question/program length interactions.
    """
    if not rows or len(rows) % 4:
        raise ValueError('Incomplete quartets')
    for view in ('question', 'candidate'):
        counts = defaultdict(Counter)
        for row in rows:
            key = canonical([row['evidence'], row[view]])
            counts[key][row['target']['verdict']] += 1
        if any(c['PASS'] != c['FAIL'] or c['PASS'] == 0 for c in counts.values()):
            raise ValueError('Unbalanced evidence-plus-' + view)
    return True


def build(out, source_manifest):
    from llama_cpp import Llama
    m = json.loads(source_manifest.read_text()); source = artifact_path(m['output_file'])
    if sha(source) != m['output_sha256'] or m['purpose'] != 'critic':
        raise ValueError('Critic source identity differs')
    gold_path = ROOT / '.local/datasets/finqa/train.json'
    name = str(gold_path.relative_to(ROOT))
    if m['input_sha256'].get(name) != sha(gold_path):
        raise ValueError('Original training annotations differ')
    gold = {r['id']: r for r in json.loads(gold_path.read_text())}
    positives = [parse_reference(r) for r in map(json.loads, source.read_text().splitlines())
                 if r['target'] == {'verdict': 'PASS'}]
    groups = defaultdict(list)
    report_splits = defaultdict(set)
    for row in positives:
        groups[(row['split'], row['page'])].append(row)
        report_splits[row['report_group']].add(row['split'])
    if any(len(v) != 1 for v in report_splits.values()):
        raise ValueError('Report split leakage')
    pairs = []
    for members in groups.values():
        for a, b in itertools.combinations(sorted(members, key=lambda r: r['id']), 2):
            key = hashlib.sha256(('quartet42|' + a['id'] + '|' + b['id']).encode()).hexdigest()
            pairs.append((key, a, b))
    ssd = artifact_path(os.environ['AGERE_SSD_ROOT'])
    weights = ssd / 'weights/tier8_v2'
    entries = verified_models('sas', weights_root=str(weights)) + verified_models('mas', verifier_model='3b',
        use_selector=False, drafter_model='3b-q4', weights_root=str(weights))
    tokenizers = {}
    try:
        tokenizers[PROFILES[0]] = Llama(model_path=str(weights / 'qwen2.5-3b-instruct-q4_k_m.gguf'), vocab_only=True, verbose=False)
        tokenizers[PROFILES[1]] = Llama(model_path=str(weights / 'qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf'), vocab_only=True, verbose=False)
        used, rejected, rows = set(), Counter(), []
        for key, a, b in sorted(pairs, key=lambda item: item[0]):
            if a['id'] in used or b['id'] in used:
                rejected['source_already_matched'] += 1
                continue
            try:
                quartet = crossed(a, b, gold)
                for index, row in enumerate(quartet):
                    row['source_id'] = key + '::' + str(index)
                    row['quartet_id'] = key
                    row['purpose'] = 'critic'
                    row['annotation_scope'] = 'Same-page reference positives, cross-question numerical negatives under both metrics; not independently adjudicated financial semantics.'
                    row['tokenization'] = {profile: tokenized_target(tokenizer, row['prompt'], row['target'], 1024)
                        for profile, tokenizer in tokenizers.items()}
            except ValueError as exc:
                rejected[str(exc)] += 1
                continue
            used.update((a['id'], b['id']))
            rows.extend(quartet)
    finally:
        for tokenizer in tokenizers.values():
            tokenizer.close()
    verify_balance(rows)
    output = out / 'examples.jsonl'
    output.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    counts = Counter(r['split'] for r in rows)
    manifest = {'purpose': 'critic', 'profiles': list(PROFILES), 'kept_n': len(rows),
        'training_n': counts['train'], 'validation_n': counts['validation'], 'quartets': len(rows) // 4,
        'group_counts': {split: len({r['report_group'] for r in rows if r['split'] == split}) for split in ('train', 'validation')},
        'max_training_tokens': 1024, 'deployment_context': 4096, 'output_file': str(output), 'output_sha256': sha(output),
        'source_positive_cases': len(positives), 'candidate_same_page_pairs': len(pairs), 'rejected_pairs': dict(rejected),
        'input_sha256': {str(p): sha(p) for p in (source_manifest, source, gold_path)},
        'source_sha256': {str(p): sha(p) for p in (Path(__file__), ROOT / 'scripts/tier8_v2_critic_data.py',
            ROOT / 'scripts/tier8_v2_financial_pipeline.py', ROOT / 'scripts/tier8_v2_adaptation_prompts.py')},
        'tokenizer_models': entries, 'marginal_balance_verified': True,
        'training_ready': counts['train'] > 0 and counts['validation'] > 0,
        'model_calls': 0, 'test_opened': False, 'actual_qa_gain': False, 'novelty_established': False,
        'selection': 'Seed42 SHA sorted eligible same-page pairs, greedily disjoint source cases. Same units and common conflict-free union evidence. Reject whole quartet on any numerical ambiguity or either-tokenizer overflow. Preserve original report split.',
        'limits': 'Known instance-bundle/counterfactual construction. Exact50% upper bound for deterministic evidence+program-only or evidence+question-only classifiers on complete balanced set, not proof of financial semantics or absence of joint shortcuts. No trained policy or natural QA improvement.'}
    write(out / 'manifest.json', manifest)
    print(json.dumps({k: manifest[k] for k in ('kept_n', 'training_n', 'validation_n', 'quartets', 'group_counts', 'rejected_pairs', 'training_ready')}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-manifest', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = artifact_path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    build(out, artifact_path(args.source_manifest))


if __name__ == '__main__':
    main()
