"""Gold-free finite local repair pool, shared by all reranking controls.

Do not insert algebraic rewrites just to manufacture deduplication savings.
Candidates are actual operator, noncommutative-order, source-binding and output
scale changes. They are not assumed incorrect or correct. Regeneration is supplied
by the same fixed actor call for every control. No verifier score affects the pool.
"""
from copy import deepcopy
import hashlib
import json

from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import execute, OPERATIONS


def local_pool(public, initial, regenerated=None, *, maximum=64):
    if set(public) & {'gold', 'qa', 'answer', 'program', 'model_input', 'gold_inds'}:
        raise ValueError('Pool accepts public evidence only')
    if type(maximum) is not int or not 1 <= maximum <= 64:
        raise ValueError('pool_limit')
    atoms = atom_catalog(public['evidence'])
    plans, origins, rejected = [], [], 0

    def add(candidate, change):
        nonlocal rejected
        try:
            if (not isinstance(candidate, dict) or set(candidate) != {'decision', 'answer_unit', 'steps'}
                    or candidate['decision'] != 'ANSWER'
                    or candidate['answer_unit'] not in ('number', 'fraction', 'percent')):
                raise ValueError('schema')
            answer = compile_plan(candidate, atoms)
            if execute(answer['steps'], public['evidence'])['issues']:
                raise ValueError('execution')
        except (ValueError, KeyError, TypeError):
            rejected += 1
            return
        if len(plans) < maximum:
            plans.append(deepcopy(candidate))
            origins.append(change)

    add(initial, {'family': 'initial'})
    if regenerated is not None:
        add(regenerated, {'family': 'regenerated'})
    # Local repair is defined relative to the original draft; an invalid original
    # can still be rescued by regeneration, but is not silently synthesized here.
    if not origins or origins[0]['family'] != 'initial':
        return {'plans': plans, 'origins': origins, 'rejected': rejected, 'maximum': maximum}
    families = {name: [] for name in ('operation', 'order', 'source', 'scale')}

    def proposal(family, change, edit):
        p = deepcopy(initial)
        edit(p)
        families[family].append((p, {'family': family, **change}))

    for index, step in enumerate(initial['steps']):
        for operation in OPERATIONS:
            if operation != step['op']:
                proposal('operation', {'step': index, 'after': operation},
                         lambda p, i=index, op=operation: p['steps'][i].update(op=op))
        if step['op'] in ('subtract', 'divide') and step['left'] != step['right']:
            proposal('order', {'step': index}, lambda p, i=index:
                     p['steps'][i].update(left=step['right'], right=step['left']))
        for side in ('left', 'right'):
            ref = step[side]
            if ref not in atoms:
                continue
            # Two nearest catalog positions in the same source span, and two
            # outside it. Equal-valued alternatives remain deliberate controls
            # for source-binding ambiguity, not correctness labels.
            keys = list(atoms)
            position = keys.index(ref)
            rank = lambda k: (abs(keys.index(k) - position), keys.index(k))
            nearby = sorted((k for k in keys if k != ref and atoms[k]['span_id'] == atoms[ref]['span_id']), key=rank)[:2]
            nearby += sorted((k for k in keys if atoms[k]['span_id'] != atoms[ref]['span_id']), key=rank)[:2]
            for replacement in nearby:
                proposal('source', {'step': index, 'side': side, 'before': ref, 'after': replacement},
                         lambda p, i=index, s=side, r=replacement: p['steps'][i].update({s: r}))
    if len(initial['steps']) < 8:
        for operation in ('multiply', 'divide'):
            proposal('scale', {'operation': operation, 'constant': '100'}, lambda p, op=operation:
                     p['steps'].append({'op': op, 'left': '#' + str(len(initial['steps']) - 1), 'right': 'CONST:100'}))
    # Stable hash order within families, round robin across families prevents the
    # 64-cap from silently removing all source or scaling alternatives.
    def key(item):
        return hashlib.sha256(('pool42|' + str(public['id']) + '|' + json.dumps(item[1], sort_keys=True)).encode()).hexdigest()
    families = {name: sorted(items, key=key) for name, items in families.items()}
    for index in range(max((len(v) for v in families.values()), default=0)):
        for items in families.values():
            if index < len(items):
                add(*items[index])
    return {'plans': plans, 'origins': origins, 'rejected': rejected, 'maximum': maximum}
