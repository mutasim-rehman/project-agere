"""Replay serialized header packets and test every quantity with the executor.

Arithmetic/source support only. No question answering, neural forward, semantic
role adjudication, cell-level compilation or materialization-aware SFT proof.
"""
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha, check_inputs
from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import execute
from table_header_materialization import materialize, atom_facts


def main():
    plan_path = artifact_path('/run/media/mutasim/Data/AGERE/runs/tier8_representation_audit/header-neural-fitting-plan-01/plan.json')
    plan = json.loads(plan_path.read_text())
    check_inputs(plan)
    base = plan_path.parent
    source = {r['id']: r for r in json.loads((base / 'source-train.json').read_text())}
    old, new = [[json.loads(x) for x in (base / name).read_text().splitlines()]
        for name in ('control-public.jsonl', 'header-public.jsonl')]
    if len(old) != 73 or len(new) != 73:
        raise ValueError('All73 fitting cases required')
    out = artifact_path('/run/media/mutasim/Data/AGERE/runs/tier8_representation_audit/header-source-support-01')
    if out.exists():
        raise ValueError('Fresh output required')
    counts, case_checks, checks = Counter(), [], []
    for a, b in zip(old, new):
        if (list(a['evidence']) != list(b['evidence']) or
                b != materialize(a, source[a['id']]['table']) or
                atom_facts(a['evidence']) - atom_facts(b['evidence'])):
            raise ValueError('Serialized source/order/fact invariant failed')
        aa, bb = [atom_catalog(x['evidence']) for x in (a, b)]
        counts.update(cases=1, old_atoms=len(aa), candidate_atoms=len(bb), added_atoms=len(bb)-len(aa))
        for key, atom in bb.items():
            # Diagnostic add-zero program tests catalog -> compiler -> executor.
            # It is not a proposed answer and bypasses no runtime source checks.
            program = {'decision': 'ANSWER', 'answer_unit': 'number',
                'steps': [{'left': key, 'op': 'add', 'right': 'CONST:0'}]}
            result = execute(compile_plan(program, bb)['steps'], b['evidence'])
            if (result['issues'] or Decimal(result['value']) != Decimal(atom['value']) or
                    result['nodes'][0]['source_spans'] != [atom['span_id']]):
                raise ValueError('Quantity failed arithmetic/source support: ' + a['id'] + ':' + key)
            checks.append({'id': a['id'], 'quantity_id': key, 'atom': atom, 'execution': result})
        case_checks.append({'id': a['id'], 'old_atoms': len(aa), 'candidate_atoms': len(bb),
            'old_facts_and_serialized_span_order_retained': True,
            'raw_table_only_regeneration_and_cell_offset_ledger_verified': True})
    check_inputs(plan)
    out.mkdir(parents=True)
    for name, records in [('quantities.jsonl', checks), ('cases.jsonl', case_checks)]:
        (out / name).write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in records))
    files = [plan_path, Path(__file__), out / 'quantities.jsonl', out / 'cases.jsonl',
        ROOT / 'scripts/evidence_atoms.py', ROOT / 'scripts/evidence_calculator.py',
        ROOT / 'scripts/table_header_materialization.py']
    result = {'status': 'complete_source_support_preflight', 'counts': dict(counts),
        'checked_quantity_executions': len(checks), 'failures': 0,
        'neural_forward_calls': 0, 'adopted': False, 'novelty_established': False,
        'input_sha256': {**plan['input_sha256'], **{str(p): sha(p) for p in files}},
        'limits': 'Every quantity tested with diagnostic add-zero execution, not a question answer. Source-span numeric support only, not per-cell semantic relevance, question-unit grammar, full-policy context, tokenizer/SFT parity, neural accuracy or independent financial truth. Old quantities also checked;183 added catalog occurrences need not be183 distinct values.'}
    (out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'out': str(out), 'counts': dict(counts), 'checked': len(checks), 'failures': 0}))


if __name__ == '__main__':
    main()
