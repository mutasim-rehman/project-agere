"""Replay completed local external baselines, preserving interrupted segments.

Exploratory local scores only; no full MortarBench replication or architecture
winner claim. Mortar intervals resample whole explicit test_case_number groups.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import random
import re

from tier8_artifact_paths import artifact_path
from tier8_external_eval import DATA, score, sha, normalize

ROOT = Path(__file__).resolve().parents[1]


def paired(left, right, groups, metric):
    ids = list(left)
    if set(ids) != set(right) or set(ids) != set(groups):
        raise ValueError('Unmatched external IDs/groups')
    clusters = defaultdict(list)
    for i in ids:
        clusters[groups[i]].append(i)
    differences = {i: int(right[i]['score'][metric]) - int(left[i]['score'][metric]) for i in ids}
    rng = random.Random(42); units = list(clusters.values()); samples = []
    for _ in range(10000):
        sample = [i for group in rng.choices(units, k=len(units)) for i in group]
        samples.append(sum(differences[i] for i in sample) / len(sample))
    samples.sort()
    return {'n': len(ids), 'n_groups': len(units), 'mas_minus_sas': sum(differences.values()) / len(ids),
            'group_bootstrap_95_interval': [samples[249], samples[9749]],
            'mas_only_correct': sum(left[i]['score'][metric] is False and right[i]['score'][metric] is True for i in ids),
            'sas_only_correct': sum(left[i]['score'][metric] is True and right[i]['score'][metric] is False for i in ids),
            'both_correct': sum(left[i]['score'][metric] and right[i]['score'][metric] for i in ids)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--recovery', required=True); p.add_argument('--out', required=True)
    a = p.parse_args(); recovery, out = map(artifact_path, [a.recovery, a.out])
    if out.exists():
        raise ValueError('Refuse overwrite')
    rm = json.loads((recovery / 'manifest.json').read_text()); original = artifact_path(rm['original'])
    old = json.loads((original / 'manifest.json').read_text())
    if rm['status'] != 'complete' or rm['cap_bytes'] != 6400000000:
        raise ValueError('Require complete original-cap recovery')
    for name, digest in rm['source_sha256'].items():
        if sha(ROOT / name) != digest:
            raise ValueError('Original external evaluator changed')
    inputs = {str(recovery / 'manifest.json'): sha(recovery / 'manifest.json')}
    results = {}
    for task, n in [('mortar', 90), ('frames', 100)]:
        source = artifact_path(recovery.parents[2] / DATA[task])
        if sha(source) != old['datasets'][task]['sha256']:
            raise ValueError('Frozen external dataset changed')
        raw = [json.loads(s) for s in source.read_text().splitlines()]
        gold = {r.get('question_id', r.get('id')): r for r in raw}
        if len(gold) != n:
            raise ValueError('Unexpected source count or duplicate IDs')
        packet_path = original / (task + '-packets.jsonl')
        packets = [json.loads(s) for s in packet_path.read_text().splitlines()]
        if len(packets) != n or any(p['question'] != r['question'] for p, r in zip(packets, raw)):
            raise ValueError('Original public packet order differs')
        inputs[str(packet_path)] = sha(packet_path)
        conditions = {}; keyed = {}
        for arm in ['sas', 'mas']:
            path = recovery / (task + '-' + arm) / 'summary.json'; summary = json.loads(path.read_text())
            if (summary['status'] != 'complete' or summary['exit_code'] != 0 or summary['memory_breach'] or
                    summary['n'] != n or summary['expected'] != n or not summary['original_case_bytes_unchanged'] or
                    not 0 < summary['peak_tree_rss_bytes'] <= summary['cap_bytes'] == rm['cap_bytes']):
                raise ValueError('Incomplete or memory-invalid external arm')
            files = list(map(artifact_path, summary['case_files']))
            recovered_packet_path = recovery / (task + '-' + arm) / (task + '-packets.jsonl')
            meta = rm['segments'][task + '-' + arm]
            recovered_packets = [json.loads(s) for s in recovered_packet_path.read_text().splitlines()]
            if (sha(recovered_packet_path) != meta['remaining_packets_sha256'] or
                    recovered_packets != packets[meta['original_completed']:]):
                raise ValueError('Recovery public packets changed')
            inputs[str(recovered_packet_path)] = sha(recovered_packet_path)
            records = [json.loads(s) for f in files if f.exists() for s in f.read_text().splitlines()]
            by_id = {r['id']: r for r in records}
            if len(records) != n or len(by_id) != n or set(by_id) != set(gold):
                raise ValueError('Incomplete or duplicate external case coverage')
            for r in records:
                if (r['gold'] != gold[r['id']]['answer'] or score(r['prediction'], gold[r['id']], task) != r['score'] or
                        r['generated_tokens'] != sum(s['usage']['completion_tokens'] for s in r['stages'])):
                    raise ValueError('External score/gold/token ledger failed replay')
            counts = Counter((gold[r['id']].get('answer_type', 'closed_book'), r['score']['exact_match']) for r in records)
            conditions[arm] = {'n': n, 'exact_matches': sum(r['score']['exact_match'] for r in records),
                'typed_counts': {kind: {'n': sum(v for (t, _), v in counts.items() if t == kind),
                                       'correct': counts[(kind, True)]} for kind, _ in counts},
                'generated_tokens': sum(r['generated_tokens'] for r in records),
                'recorded_seconds': sum(r['seconds'] for r in records),
                'peak_tree_rss_bytes': summary['peak_tree_rss_bytes'],
                'final_finish_reasons': dict(Counter(r['stages'][-1]['finish_reason'] for r in records)),
                'note': 'Reported seconds sum saved case durations; SAS Mortar spans interruption/recovery.'}
            if task == 'mortar':
                shapes = {}
                for kind in {r['answer_type'] for r in raw if r['answer_type'] != 'boolean'}:
                    selected = [r for r in records if gold[r['id']]['answer_type'] == kind]
                    shapes[kind] = {'n': len(selected),
                        'empty_predictions': sum(normalize(r['prediction'].get('answer'), kind) == [] for r in selected if isinstance(r['prediction'], dict)),
                        'nonempty_gold': sum(bool(normalize(gold[r['id']]['answer'], kind)) for r in selected),
                        'nonempty_gold_exact_matches': sum(bool(normalize(gold[r['id']]['answer'], kind)) and r['score']['exact_match'] for r in selected)}
                conditions[arm]['identifier_prediction_shapes'] = shapes
            if task == 'frames':
                conditions[arm]['punctuation_normalized_matches'] = sum(r['score']['punctuation_normalized_match'] for r in records)
            keyed[arm] = by_id
            inputs[str(path)] = sha(path)
            for f in files:
                if f.exists():
                    inputs[str(f)] = sha(f)
        groups = {i: r['test_case_number'] if task == 'mortar' else i for i, r in gold.items()}
        results[task] = {'conditions': conditions, 'paired_exact': paired(keyed['sas'], keyed['mas'], groups, 'exact_match'),
                         'grouping': 'explicit test_case_number (shared financial case)' if task == 'mortar' else 'one group per question; cross-question dependence unassessed'}
        if task == 'mortar':
            presence = Counter()
            for r, packet in zip(raw, packets):
                if r['answer_type'] != 'txn_id_list':
                    continue
                targets = normalize(r['answer'], r['answer_type'])
                if not targets:
                    continue
                text = '\n'.join(packet['sources'])
                found = [bool(re.search(r'(?<![A-Za-z0-9_-])' + re.escape(t) + r'(?![A-Za-z0-9_-])', text)) for t in targets]
                presence['nonempty_gold_cases'] += 1
                presence['all_gold_identifiers_mentioned'] += all(found)
                presence['any_gold_identifier_mentioned'] += any(found)
            results[task]['retrieved_transaction_identifier_mentions'] = dict(presence)
            results[task]['mention_limit'] = 'Offline gold-assisted literal-ID presence diagnostic only; mention does not prove relevance or sufficient evidence.'
            results[task]['fixed_rule_diagnostics'] = {
                kind: {'n': sum(r['answer_type'] == kind for r in raw),
                       'constant_true_correct': sum(score({'answer': True}, r, task)['exact_match'] for r in raw if r['answer_type'] == kind),
                       'constant_false_correct': sum(score({'answer': False}, r, task)['exact_match'] for r in raw if r['answer_type'] == kind),
                       'constant_empty_list_correct': sum(score({'answer': []}, r, task)['exact_match'] for r in raw if r['answer_type'] == kind)}
                for kind in {r['answer_type'] for r in raw}}
        else:
            results[task]['paired_punctuation_normalized'] = paired(keyed['sas'], keyed['mas'], groups, 'punctuation_normalized_match')
        inputs[str(source)] = sha(source)
    report = {'status': 'complete_scores_replayed', 'case_arm_evaluations': 380, 'tasks': results,
              'input_sha256': inputs, 'source_sha256': sha(Path(__file__)),
              'limits': 'Original unadapted systems; simulated8GB tier. Mortar uses partial JSON/XML evidence, no PDFs/paystubs, local typed exact scoring and forced boolean/ID lists. FRAMES is closed-book strict matching with separate punctuation sensitivity. SAS maximum896 generated tokens versus MAS1792 under ceiling2048; actual expenditure differs. Not optimized/adapted systems, official full benchmark replication, pristine confirmation, causal architecture winner or novelty. Group bootstrap is exploratory; no repeated-run latency claim. Constant rules are fixed diagnostics, not gold-selected deployable policies.'}
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v['conditions'] for k, v in results.items()}))


if __name__ == '__main__':
    main()
