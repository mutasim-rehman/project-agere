"""Offline reference-program coverage; no generation, filtering or semantic oracle."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re

from evidence_atoms import atom_catalog
from evidence_calculator import OPERATIONS
from program_binding_domains import binding_domains
from tier8_artifact_paths import artifact_path
from tier8_v2_financial_pipeline import reported_reference
from tier8_v2_demo_retrieval import report_group


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def convention(qa):
    ref = reported_reference(qa['answer'])
    try:
        value = Decimal(str(qa['exe_ans']))
        if ref and value.is_finite():
            tolerance = max(ref['tolerance'], Decimal('0.00001'))
            if abs(value - ref['value']) <= tolerance:
                return 'fraction' if ref['percent'] else 'number'
            if ref['percent'] and abs(value / 100 - ref['value']) <= tolerance:
                return 'percentage_points'
            return 'reported_execution_disagreement'
    except InvalidOperation:
        pass
    return 'unsupported_reference'


def inspect(packet, source):
    if packet['question'] != source['qa']['question']:
        raise ValueError('Question/source identity mismatch')
    program = source['qa']['program']; operations = re.findall(r'([a-z_]+)\(', program)
    result = {'id': packet['id'], 'report_group': report_group(packet['id']),
        'reference_program': program, 'operations': operations,
        'operators_outside_runtime_set': sorted(set(operations) - set(OPERATIONS)),
        'contains_percentage_literal': bool(re.search(r'\d(?:\.\d+)?%', program)),
        'reported_answer': source['qa']['answer'], 'executable_answer': source['qa']['exe_ans'],
        'reference_convention': convention(source['qa']),
        'evidence_sha256': hashlib.sha256(json.dumps(packet['evidence'], sort_keys=True).encode()).hexdigest()}
    try:
        partial = binding_domains(program, atom_catalog(packet['evidence']))
        result.update(binding_status='directly_mappable', numeric_binding_unique=partial['numeric_binding_unique'],
            source_slots=len(partial['slots']), ambiguous_slots=sum(not s['numeric_identity_unique'] for s in partial['slots'].values()))
    except InvalidOperation:
        result['binding_status'] = 'existing_parser_numeric_literal_failure'
    except ValueError as exc:
        result['binding_status'] = str(exc)
    return result


def run(public_path, source_path, out):
    if out.exists():
        raise ValueError('Require a fresh diagnostic output; no overwrite')
    public = [json.loads(x) for x in public_path.read_text().splitlines()]
    original = json.loads(source_path.read_text()); source = {r['id']: r for r in original}
    if (not public or len(source) != len(original) or len({r['id'] for r in public}) != len(public)
            or any(r.get('split') != 'train' for r in public)):
        raise ValueError('Require unique public training-source IDs')
    rows = [inspect(p, source[p['id']]) for p in public]
    counts = {key: dict(Counter(str(r[key]) for r in rows)) for key in
        ('binding_status', 'reference_convention', 'contains_percentage_literal')}
    out.mkdir(parents=True)
    details = out / 'cases.jsonl'; details.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows))
    script = Path(__file__)
    result = {'status': 'complete_offline_diagnostic', 'n': len(rows),
        'n_reports': len({r['report_group'] for r in rows}), 'counts': counts,
        'directly_mappable_unique': sum(r.get('numeric_binding_unique', False) for r in rows),
        'directly_mappable_ambiguous': sum(r['binding_status'] == 'directly_mappable' and not r['numeric_binding_unique'] for r in rows),
        'operation_counts': dict(Counter(op for r in rows for op in r['operations'])),
        'cases_removed': 0, 'model_forward_calls': 0, 'metrics_or_labels_changed': False,
        'input_sha256': {str(p.resolve()): digest(p) for p in [public_path, source_path, script,
            script.parent / 'program_binding_domains.py', script.parent / 'evidence_atoms.py',
            script.parent / 'evidence_calculator.py', script.parent / 'tier8_v2_financial_pipeline.py']},
        'details_sha256': digest(details),
        'limits': 'Outcome-guided exploratory diagnostic, not preregistered. Direct mapping tests this existing parser and exact annotated program only, not existence of equivalent arithmetic or a task-solvability ceiling. Ambiguous numeric cells are not resolved or semantically adjudicated. Percent literals are flagged, not normalized. Reference disagreement uses existing reported-answer rules; neither reference is independently certified. No held-out audit partition is opened or examples relabelled.'}
    (out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n'); print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('public', 'source', 'out'):
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    run(artifact_path(args.public), artifact_path(args.source), artifact_path(args.out))
