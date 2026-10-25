"""Question-blind train-only artifact controls for binary critic curricula.

Features consume only the proposed compiled program, never question, evidence,
verdict, mutation metadata, source ID, tokenization or neural outputs. Fixed tiny
trees are fit on training reports and evaluated on existing validation reports.
This diagnoses shortcut opportunities, not natural financial verification quality.
"""
import argparse
from collections import Counter
from decimal import Decimal
import json
import math
from pathlib import Path

from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha
from tier8_v2_demo_retrieval import report_group


def program_from_prompt(prompt):
    marker = '\nProposed program:\n'
    if prompt.count(marker) != 1:
        raise ValueError('Ambiguous proposed program delimiter')
    text = prompt.split(marker, 1)[1]
    program, offset = json.JSONDecoder().raw_decode(text)
    if not text[offset:].startswith('\nDeterministic execution:\n'):
        raise ValueError('Unexpected program boundary')
    return program


def features(program):
    if not isinstance(program, dict) or set(program) != {'decision', 'answer_unit', 'steps'} or program['decision'] != 'ANSWER':
        raise ValueError('Expected answer program')
    steps = program['steps']
    if not isinstance(steps, list) or not 1 <= len(steps) <= 8:
        raise ValueError('Invalid steps')
    operations, constants, literals = Counter(), Counter(), []
    step_refs, sources = 0, []
    for step in steps:
        if set(step) != {'op', 'left', 'right'} or step['op'] not in ('add', 'subtract', 'multiply', 'divide'):
            raise ValueError('Invalid operation')
        operations[step['op']] += 1
        for side in ('left', 'right'):
            operand = step[side]
            if not isinstance(operand, dict) or set(operand) != {'value', 'span_id'}:
                raise ValueError('Invalid compiled operand')
            value, span = operand['value'], operand['span_id']
            if value.startswith('#'):
                step_refs += 1
            else:
                number = Decimal(value)
                if not number.is_finite():
                    raise ValueError('Nonfinite literal')
                literals.append(number)
                if span == 'CONST':
                    constants[number] += 1
                else:
                    sources.append((span, number))
    result = {'steps': len(steps), 'step_references': step_refs, 'source_operands': len(sources),
              'distinct_source_operands': len(set(sources)), 'constants': sum(constants.values()),
              'zero_literals': sum(v == 0 for v in literals), 'negative_literals': sum(v < 0 for v in literals),
              'distinct_literal_values': len(set(literals)),
              'max_log_literal_magnitude': max((math.log10(1 + abs(float(v))) for v in literals), default=0.)}
    for op in ('add', 'subtract', 'multiply', 'divide'):
        result['count_' + op] = operations[op]
        result['last_' + op] = int(steps[-1]['op'] == op)
    for number in (0, 1, 2, 100, 1000):
        result['constant_' + str(number)] = constants[Decimal(number)]
    return result


def fit_tree(rows, names, *, depth=3, minimum_leaf=32):
    """Fixed-depth greedy CART-style Gini split. All thresholds train-derived."""
    positive, n = sum(r['y'] for r in rows), len(rows)
    node = {'n': n, 'positives': positive, 'prediction': int(positive * 2 >= n)}
    if not depth or positive in (0, n) or n < 2 * minimum_leaf:
        return node
    parent = (positive ** 2 + (n - positive) ** 2) / n
    best = None
    for name in names:
        ordered = sorted(rows, key=lambda r: r['x'][name])
        left_positive = 0
        for i in range(1, n):
            left_positive += ordered[i - 1]['y']
            a, b = ordered[i - 1]['x'][name], ordered[i]['x'][name]
            if i < minimum_leaf or n - i < minimum_leaf or a == b:
                continue
            right_positive = positive - left_positive
            score = (left_positive ** 2 + (i - left_positive) ** 2) / i
            score += (right_positive ** 2 + (n - i - right_positive) ** 2) / (n - i)
            if score > parent + 1e-12 and (best is None or score > best[0] + 1e-12):
                best = (score, name, (a + b) / 2)
    if best is not None:
        _, name, threshold = best
        left = [r for r in rows if r['x'][name] <= threshold]
        right = [r for r in rows if r['x'][name] > threshold]
        node.update(feature=name, threshold=threshold,
                    left=fit_tree(left, names, depth=depth - 1, minimum_leaf=minimum_leaf),
                    right=fit_tree(right, names, depth=depth - 1, minimum_leaf=minimum_leaf))
    return node


def predict(tree, x):
    while 'feature' in tree:
        tree = tree['left'] if x[tree['feature']] <= tree['threshold'] else tree['right']
    return tree['prediction']


def load(path):
    rows, ids = [], set()
    for line in path.read_text().splitlines():
        r = json.loads(line)
        if r['source_id'] in ids or r['split'] not in ('train', 'validation') or r['target'] not in ({'verdict': 'PASS'}, {'verdict': 'FAIL'}):
            raise ValueError('Duplicate/invalid binary corpus')
        ids.add(r['source_id'])
        # Only the program enters x. Other fields are for training labels/audit.
        rows.append({'x': features(program_from_prompt(r['prompt'])), 'y': int(r['target']['verdict'] == 'PASS'),
                     'split': r['split'], 'report_group': r['report_group'], 'source_id': r['source_id'],
                     'mutation_family': (r.get('mutation') or {}).get('kind', 'reference')})
    train = {r['report_group'] for r in rows if r['split'] == 'train'}
    validation = {r['report_group'] for r in rows if r['split'] == 'validation'}
    if train & validation:
        raise ValueError('Report leakage')
    return rows


def metrics(tree, rows):
    counts = Counter()
    by_family = {}
    for row in rows:
        label, prediction = row['y'], predict(tree, row['x'])
        counts[(label, prediction)] += 1
        family = by_family.setdefault(row['mutation_family'], {'n': 0, 'correct': 0, 'accepted': 0})
        family['n'] += 1
        family['correct'] += int(label == prediction)
        family['accepted'] += prediction
    n = len(rows)
    return {'n': n, 'n_reports': len({r['report_group'] for r in rows}),
            'accuracy': (counts[(0, 0)] + counts[(1, 1)]) / n,
            'reference_accepts': counts[(1, 1)], 'reference_nonaccepts': counts[(1, 0)],
            'mutation_accepts': counts[(0, 1)], 'mutation_nonaccepts': counts[(0, 0)], 'by_family': by_family}


def natural_replay(models, snapshots, training_reports):
    """A gate-only component replay; all models fit before this function runs."""
    rows = [json.loads(line) for line in snapshots.read_text().splitlines()]
    if len({r['case_id'] for r in rows}) != len(rows) or not rows:
        raise ValueError('Duplicate/empty natural snapshots')
    if any(report_group(r['case_id']) in training_reports for r in rows):
        raise ValueError('Natural reports overlap critic fitting reports')
    if any(r['repair'] != 'none' or r['initial_answer'] != r['answer'] or r['initial_score'] != r['score'] for r in rows):
        raise ValueError('Require unchanged no-repair natural candidates')
    output = {}
    for corpus, variants in models.items():
        output[corpus] = {}
        for kind, model in variants.items():
            predictions, feature_rejections = [], 0
            for row in rows:
                try:
                    x = features(row['initial_answer'])
                    accepted = bool(predict(model['tree'], x)) and not row['initial_execution']['issues']
                except (ValueError, KeyError, TypeError):
                    accepted = False
                    feature_rejections += 1
                predictions.append(accepted)
            outcomes = {}
            for metric in ('case_success', 'raw_execution_match'):
                correct = sum(a and r['initial_score'][metric] for a, r in zip(predictions, rows))
                wrong = sum(a and not r['initial_score'][metric] for a, r in zip(predictions, rows))
                outcomes[metric] = {'correct_delivered': correct, 'wrong_delivered': wrong,
                                    'withheld': len(rows) - correct - wrong,
                                    'candidate_correct': sum(r['initial_score'][metric] for r in rows)}
            output[corpus][kind] = {**outcomes, 'feature_rejections': feature_rejections}
    return {'n': len(rows), 'n_report_groups': len({report_group(r['case_id']) for r in rows}),
            'snapshots_sha256': sha(snapshots), 'results': output,
            'limits': 'Offline gate-only component on already-used natural24 drafts; no fresh model calls, candidate changes, threshold tuning or end-to-end resource claim. Fitting labels come only from critic training reports. Does not establish neural shortcut use.'}


def controlled_replay(models, root, training_reports):
    public = [json.loads(s) for s in (root / 'public.jsonl').read_text().splitlines()]
    labels = [json.loads(s) for s in (root / 'labels.jsonl').read_text().splitlines()]
    by_id = {r['id']: r for r in labels}
    if len(by_id) != len(labels) or len({r['id'] for r in public}) != len(public) or set(by_id) != {r['id'] for r in public}:
        raise ValueError('Unmatched controlled inputs')
    rows = [{'x': features(r['candidate']), 'y': int(by_id[r['id']]['expected_accept']),
             'report_group': by_id[r['id']]['report_group'],
             'mutation_family': ((by_id[r['id']].get('mutation') or {}).get('kind', 'mutation')
                                 if not by_id[r['id']]['expected_accept'] else 'reference')}
            for r in public]
    results = {}
    for corpus, variants in models.items():
        results[corpus] = {}
        for kind, model in variants.items():
            measured = metrics(model['tree'], rows)
            reports = {r['report_group'] for r in rows}
            measured['complete_report_discriminations'] = sum(all(predict(model['tree'], r['x']) == r['y']
                for r in rows if r['report_group'] == group) for group in reports)
            results[corpus][kind] = measured
    return {'results': results, 'reports_overlapping_fitting': sorted({r['report_group'] for r in rows} & training_reports),
            'input_sha256': {name: sha(root / name) for name in ('public.jsonl', 'labels.jsonl')},
            'limits': 'Previously selected controlled mutation probe, not natural errors or fresh confirmation. Model fits precede replay. Scope of report overlap is explicit.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', required=True)
    parser.add_argument('--extended', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--natural-snapshots')
    parser.add_argument('--controlled-directory')
    args = parser.parse_args()
    paths = {name: artifact_path(value) for name, value in [('original', args.original), ('extended', args.extended)]}
    out = artifact_path(args.out)
    if out.exists():
        raise ValueError('No overwrite')
    datasets = {name: load(path) for name, path in paths.items()}
    identity = lambda rows: [(r['source_id'], r['split'], r['report_group'], r['y']) for r in rows]
    if identity(datasets['original']) != identity(datasets['extended']):
        raise ValueError('Not matched source cases/splits/labels')
    results = {}
    for name, rows in datasets.items():
        train = [r for r in rows if r['split'] == 'train']
        models = {'length_stump': fit_tree(train, ['steps'], depth=1),
                  'program_structure_tree_depth3': fit_tree(train, sorted(train[0]['x']), depth=3)}
        results[name] = {kind: {'tree': tree, 'training': metrics(tree, train), 'validation': {
            condition: metrics(tree, [r for r in other if r['split'] == 'validation'])
            for condition, other in datasets.items()}} for kind, tree in models.items()}
    result = {'status': 'complete', 'input_sha256': {name: sha(path) for name, path in paths.items()},
              'source_sha256': sha(Path(__file__)), 'minimum_leaf': 32, 'tree_depths': [1, 3], 'results': results,
              'novelty_established': False, 'neural_quality_gain': False,
              'limits': 'Fixed question-blind artifact controls on existing training/validation reports. Audit motivated by prior development results; aggregate neural outcomes were already known. No neural outputs enter features or fitting labels, and no hyperparameter search is performed. Validation is development, not fresh confirmation. Structural predictability is a shortcut opportunity, not proof that a neural critic uses it or that natural financial semantics are easy.'}
    fitting_reports = {r['report_group'] for rows in datasets.values() for r in rows if r['split'] == 'train'}
    if args.natural_snapshots:
        result['natural_component_replay'] = natural_replay(results, artifact_path(args.natural_snapshots), fitting_reports)
    if args.controlled_directory:
        result['controlled_probe_replay'] = controlled_replay(results, artifact_path(args.controlled_directory), fitting_reports)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({name: {kind: {condition: data['accuracy'] for condition, data in value['validation'].items()}
                            for kind, value in models.items()} for name, models in results.items()}))


if __name__ == '__main__':
    main()
