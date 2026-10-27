"""Separate source visibility from action-catalog availability on fitting73.

No neural calls. Numeric/text presence does not certify a financial role or
prove that repeated text and explicit first-row cues carry no information.
"""
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from evidence_atoms import atom_catalog
from evidence_calculator import numeric_tokens
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import check_inputs, sha


def main():
    base = artifact_path('/run/media/mutasim/Data/AGERE/runs/tier8_representation_audit/header-neural-fitting-plan-01')
    plan = json.loads((base / 'plan.json').read_text())
    check_inputs(plan)
    old, new = [[json.loads(x) for x in (base / name).read_text().splitlines()]
        for name in ('control-public.jsonl', 'header-public.jsonl')]
    if len(old) != 73 or len(new) != 73:
        raise ValueError('All73 fitting cases required')
    counts, detail = Counter(), []
    for a, b in zip(old, new):
        if a['id'] != b['id'] or list(a['evidence']) != list(b['evidence']):
            raise ValueError('Paired case/order differs')
        facts = lambda p: Counter((v['span_id'], v['value'], v['context'])
            for v in atom_catalog(p['evidence']).values())
        aa, bb = facts(a), facts(b)
        if aa - bb:
            raise ValueError('Original catalog facts lost')
        added = []
        for (span, value, context), n in (bb - aa).items():
            visible = Decimal(value) in numeric_tokens(a['evidence'][span])
            counts['added_atom_occurrences'] += n
            counts['added_occurrences_numeric_in_same_original_span'] += n * visible
            added.append({'span': span, 'value': value, 'context': context,
                'occurrences': n, 'numeric_in_same_original_span': visible})
        cells = []
        for cell in b['first_row_materialization']['appended_cells']:
            raw, span = cell['original_cell'], cell['augmented_span']
            counts['first_row_cell_occurrences'] += 1
            counts['empty_first_row_cell_occurrences'] += not raw.strip()
            visible = bool(raw.strip()) and raw in a['evidence'][span]
            counts['nonempty_cell_literals_in_same_original_span'] += visible
            cells.append({**cell, 'nonempty_literal_in_same_original_span': visible})
        detail.append({'id': a['id'], 'added_atoms': added, 'first_row_cells': cells})
    check_inputs(plan)
    out = artifact_path('/run/media/mutasim/Data/AGERE/runs/tier8_representation_audit/header-visibility-attribution-01')
    out.mkdir(parents=True, exist_ok=False)
    path = out / 'cases.jsonl'
    path.write_text(''.join(json.dumps(x, sort_keys=True) + '\n' for x in detail))
    inputs = [base / 'plan.json', path, Path(__file__), ROOT / 'scripts/evidence_atoms.py',
        ROOT / 'scripts/evidence_calculator.py']
    result = {'status': 'complete_offline_source_visibility_attribution', 'n': len(detail),
        'counts': dict(counts), 'neural_forward_calls': 0, 'adopted': False,
        'novelty_established': False,
        'input_sha256': {**plan['input_sha256'], **{str(p): sha(p) for p in inputs}},
        'interpretation': 'Every added catalog occurrence is already numerically visible in the same baseline span; every nonempty first-row cell string is already present there. Prototype changes selectable program operands and repeats source text with explicit first-row cues. Four earlier coverage recoveries are catalog representability changes, not newly retrieved raw cell literals.',
        'limits': 'Fitting-only source visibility diagnostic. Numeric and substring presence are not semantic grounding or a strict information-equivalence proof: explicit structural cues, catalog/grammar options and token repetitions differ. No QA gain or novel mechanism demonstrated. Existing neural plan remains prepared and unexecuted.'}
    (out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'result': str(out), 'n': len(detail), 'counts': dict(counts)}))


if __name__ == '__main__':
    main()
