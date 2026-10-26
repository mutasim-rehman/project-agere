"""Fitting-only offline test: add first table row to unchanged lexical top-eight.

No model calls, no changes to frozen natural packets, no header semantic labels.
"""
from collections import Counter
from decimal import InvalidOperation
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from tier8_artifact_paths import artifact_path
from tier8_v2_finqa import tokens
from evidence_atoms import atom_catalog
from program_binding_domains import binding_domains


def packet_with_first_row(row):
    evidence = {}; header = row['table'][0] if row['table'] else []
    if header:
        evidence['table_0'] = ' ; '.join(f'column {j}: {value}' for j, value in enumerate(header))
    for i, cells in enumerate(row['table'][1:], 1):
        evidence[f'table_{i}'] = ' ; '.join(f"{header[j] if j < len(header) else 'column ' + str(j)}: {value}" for j, value in enumerate(cells))
    for i, text in enumerate(row['pre_text'] + row['post_text']):
        if tokens(text):
            evidence[f'text_{i}'] = text
    query = Counter(tokens(row['qa']['question']))
    counts = {key: Counter(tokens(text)) for key, text in evidence.items()}
    frequencies = Counter(t for c in counts.values() for t in c)
    def score(key):
        c = counts[key]
        return sum(min(c[t], 2) * (len(counts) + 1) / (frequencies[t] + 1) for t in query) / max(1, sum(c.values())) ** .5
    selected = sorted(evidence, key=lambda key: (-score(key), key))[:8]
    return {'id': row['id'], 'split': 'train', 'question': row['qa']['question'],
        'evidence': {key: evidence[key] for key in selected},
        'retrieval': {'method': 'lexical-idf-length-normalized-with-first-row', 'limit': 8,
            'source_units': len(evidence), 'gold_used': False}}


def state(program, evidence):
    try:
        binding_domains(program, atom_catalog(evidence)); return 'mappable'
    except InvalidOperation:
        return 'numeric_literal_failure'
    except ValueError as exc:
        return str(exc)


def main():
    base = artifact_path('/run/media/mutasim/Data/AGERE/datasets/tier8_v2_natural/natural_reports62_01')
    public_path, source_path = base / 'fitting-public.jsonl', base / 'source-train.json'
    public = [json.loads(x) for x in public_path.read_text().splitlines()]
    selection = json.loads((base / 'selection.json').read_text())['partitions']['fitting']
    if sorted(r['id'] for r in public) != sorted(selection['ids']):
        raise ValueError('Require exact fitting partition')
    source = {r['id']: r for r in json.loads(source_path.read_text())}
    out = artifact_path('/run/media/mutasim/Data/AGERE/runs/tier8_representation_audit/first-row-fitting-01')
    if out.exists():
        raise ValueError('Fresh diagnostic output required')
    rows, packets = [], []
    for old in public:
        original = source[old['id']]; new = packet_with_first_row(original); packets.append(new)
        rows.append({'id': old['id'], 'before': state(original['qa']['program'], old['evidence']),
                     'after': state(original['qa']['program'], new['evidence'])})
    out.mkdir(parents=True)
    details = out / 'cases.jsonl'; details.write_text(''.join(json.dumps(x) + '\n' for x in rows))
    data = out / 'candidate-public.jsonl'; data.write_text(''.join(json.dumps(x, sort_keys=True) + '\n' for x in packets))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    summary = {'status': 'complete_offline_fitting_test', 'n': len(rows),
        'transitions': dict(Counter(r['before'] + ' -> ' + r['after'] for r in rows)),
        'mappable_before': sum(r['before'] == 'mappable' for r in rows),
        'mappable_after': sum(r['after'] == 'mappable' for r in rows),
        'changed_status_cases': [r for r in rows if r['before'] != r['after']],
        'model_forward_calls': 0, 'selection_or_reserved_audit_packets_changed': False,
        'input_sha256': {str(p): sha(p) for p in [Path(__file__), public_path, source_path, base / 'selection.json',
            ROOT / 'scripts/tier8_v2_finqa.py', ROOT / 'scripts/evidence_atoms.py', ROOT / 'scripts/program_binding_domains.py']},
        'details_sha256': sha(details), 'candidate_packets_sha256': sha(data),
        'decision': 'No net direct-reference coverage gain; do not adopt or claim a QA improvement. Preserve existing frozen study. More careful information retention/budget controls would be needed.',
        'limits': 'Motivated by selection-case inspection, assessed on fitting reports only. Fixed eight source units, not token-matched. Existing-parser mapping is not task solvability or financial semantic correctness. No first-use novelty.'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n'); print(json.dumps(summary))


if __name__ == '__main__':
    main()
