"""Freeze training-source packets for natural-error research, without generation.

This prepares weak-supervision research inputs, not pristine confirmation data.
Exclude whole reports used by adaptation preparation, demonstrations or dev.
Selection and partitions depend on IDs only; gold labels never enter packets.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

from tier8_artifact_paths import artifact_path
from tier8_v2_demo_retrieval import BANK, report_group
from tier8_v2_finqa import packet

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def partition(rows, excluded, selection_reports=15, audit_reports=15):
    ids = [r['id'] for r in rows]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Require nonempty unique source IDs')
    if selection_reports <= 0 or audit_reports <= 0:
        raise ValueError('Require nonempty reserved partitions')
    eligible = {report_group(i) for i in ids} - set(excluded)
    groups = sorted(eligible, key=lambda g: (
        hashlib.sha256(('agere-natural-42:' + g).encode()).hexdigest(), g))
    if len(groups) <= selection_reports + audit_reports:
        raise ValueError('Insufficient reports for all three partitions')
    assignment = {g: ('diagnostic_audit' if n < audit_reports else
                      'model_selection' if n < audit_reports + selection_reports else
                      'fitting') for n, g in enumerate(groups)}
    return {name: sorted((r for r in rows if assignment.get(report_group(r['id'])) == name),
                         key=lambda r: r['id'])
            for name in ['fitting', 'model_selection', 'diagnostic_audit']}


def public_packet(row):
    public = packet(row)
    # packet() historically labels its dev consumer; this source is train.
    public['split'] = 'train'
    return public


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run-id', required=True)
    a = p.parse_args()
    if not re.fullmatch('[a-zA-Z0-9_-]+', a.run_id):
        raise ValueError('Unsafe run ID')
    out = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) /
                        'datasets/tier8_v2_natural' / a.run_id)
    if out.exists():
        raise ValueError('Refuse overwrite')
    source = ROOT / '.local/datasets/finqa/train.json'
    bank_path = ROOT / BANK
    bank = json.loads(bank_path.read_text())
    dev = ROOT / 'research/tier8_v2/external/finqa/dataset-dev.json'
    if sha(source) != bank['source_sha256'] or sha(dev) != bank['development_source_sha256']:
        raise ValueError('Pinned training/development sources changed')
    prepared = [ROOT / f'research/tier8_v2/data/finqa-cell-adaptation-{s}-02.jsonl'
                for s in ['train', 'validation']]
    pin_path = ROOT / 'research/tier8_v2/evidence/deployment-sft-1024-02.json'
    pin = json.loads(pin_path.read_text())
    for path in prepared:
        if sha(path) != pin['input_sha256'][str(path.relative_to(ROOT))]:
            raise ValueError('Pinned adaptation preparation changed')
    exclusions = {
        'adaptation_preparation': {r['report_group'] for path in prepared
                                  for r in map(json.loads, path.read_text().splitlines())},
        'demonstration_bank': {report_group(r['source_id']) for r in bank['examples']},
        'development': {report_group(r['id']) for r in json.loads(dev.read_text())},
        'bank_exclusions': set(bank['excluded_report_groups']),
    }
    partitions = partition(json.loads(source.read_text()), set().union(*exclusions.values()))
    out.mkdir(parents=True)
    shutil.copyfile(source, out / 'source-train.json')
    outputs = {}
    for name, rows in partitions.items():
        path = out / (name + '-public.jsonl')
        path.write_text(''.join(json.dumps(public_packet(r), sort_keys=True) + '\n' for r in rows))
        outputs[name] = {'n': len(rows), 'n_reports': len({report_group(r['id']) for r in rows}),
                         'ids': [r['id'] for r in rows], 'public_file': str(path), 'sha256': sha(path)}
    inputs = [source, dev, bank_path, pin_path, *prepared]
    report = {
        'status': 'frozen_inputs_only', 'source_split': 'train',
        'source_copy': str(out / 'source-train.json'), 'source_sha256': sha(source),
        'partitions': outputs, 'excluded_reports': {k: sorted(v) for k, v in exclusions.items()},
        'input_sha256': {str(path.relative_to(ROOT)): sha(path) for path in inputs},
        'code_sha256': {str(path.relative_to(ROOT)): sha(path) for path in [
            Path(__file__), ROOT / 'scripts/tier8_v2_finqa.py',
            ROOT / 'scripts/tier8_v2_demo_retrieval.py']},
        'selection': 'All eligible cases; whole-report SHA42 order reserves15 audit and15 model-selection reports; rest fitting. No answer/program/performance filter.',
        'retrieval': 'Unchanged question-only lexical limit8, no gold retrieval fields.',
        'model_calls': 0, 'test_opened': False,
        'limits': 'Training-source research only. No generation, natural-error labels or useful gain yet. Not pristine unseen data; public pretraining contamination and all historical experiment exposure unassessed. Diagnostic audit15 reports cannot certify low risk. Do not fit on model-selection/audit groups, or on development errors. Numerical agreement is weak supervision, not semantic adjudication.',
    }
    (out / 'selection.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: {'n': v['n'], 'reports': v['n_reports']} for k, v in outputs.items()}))


if __name__ == '__main__':
    main()
