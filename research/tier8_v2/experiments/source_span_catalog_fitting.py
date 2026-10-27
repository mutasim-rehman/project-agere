"""Seal a catalog-only fitting baseline, then measure coverage and prompt cost.

No source text/selection changes, active pipeline edits or neural forwards.
Catalog-only capture patches only this process's imported function temporarily.
"""
from collections import Counter
from decimal import InvalidOperation, Decimal
import hashlib
import json
from pathlib import Path
import statistics
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from source_span_catalog import complete_catalog
from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import execute
from program_binding_domains import binding_domains
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import check_inputs, sha
from tier8_v2_adaptation_prompts import capture
from completion_tokenization import completion_tokens


def state(program, catalog):
    try:
        binding_domains(program, catalog)
        return 'mappable'
    except InvalidOperation:
        return 'numeric_literal_failure'
    except ValueError as exc:
        return str(exc)


def main():
    base = artifact_path('/run/media/mutasim/Data/AGERE/runs/tier8_representation_audit/header-neural-fitting-plan-01')
    plan = json.loads((base / 'plan.json').read_text())
    check_inputs(plan)
    public, header = [[json.loads(x) for x in (base / name).read_text().splitlines()]
        for name in ('control-public.jsonl', 'header-public.jsonl')]
    if len(public) != 73 or len(header) != 73:
        raise ValueError('All fitting73 required')
    out = artifact_path('/run/media/mutasim/Data/AGERE/runs/tier8_representation_audit/source-span-catalog-fitting-01')
    if out.exists():
        raise ValueError('Fresh output required')
    # No reference program/table/answer is used to generate these catalogs.
    candidate = [{'id': p['id'], 'catalog': complete_catalog(p['evidence'])} for p in public]
    out.mkdir(parents=True)
    sealed = out / 'catalogs.jsonl'
    sealed.write_text(''.join(json.dumps(x) + '\n' for x in candidate))
    digest = sha(sealed)
    source = {r['id']: r for r in json.loads((base / 'source-train.json').read_text())}
    counts, transitions, detail, prompts = Counter(), Counter(), [], []
    for p, h, record in zip(public, header, candidate):
        if p['id'] != h['id'] or p['id'] != record['id']:
            raise ValueError('Case order differs')
        old, new = atom_catalog(p['evidence']), record['catalog']
        if list(new.items())[:len(old)] != list(old.items()):
            raise ValueError('Original IDs or facts changed')
        for key, atom in new.items():
            probe = {'steps': [{'op': 'add', 'left': key, 'right': 'CONST:0'}]}
            execution = execute(compile_plan(probe, new)['steps'], p['evidence'])
            if execution['issues'] or Decimal(execution['value']) != Decimal(atom['value']):
                raise ValueError('Catalog operand cannot execute against original source')
        program = source[p['id']]['qa']['program']
        a, b, c = [state(program, catalog) for catalog in (old, new, atom_catalog(h['evidence']))]
        counts.update(cases=1, original_atoms=len(old), candidate_atoms=len(new),
            original_mappable=a == 'mappable', candidate_mappable=b == 'mappable', header_mappable=c == 'mappable')
        transitions[a + ' -> ' + b] += 1
        detail.append({'id': p['id'], 'before': a, 'catalog_only': b, 'header_materialization': c,
            'old_atoms': len(old), 'new_atoms': len(new)})
        original_prompt, header_prompt = [capture(x, 'mas')['prompt'] for x in (p, h)]
        with patch('tier8_v2_financial_pipeline.atom_catalog', complete_catalog):
            catalog_prompt = capture(p, 'mas')['prompt']
        prompts.append({'id': p['id'], 'original': original_prompt,
            'catalog_only': catalog_prompt, 'header_materialization': header_prompt})
    from llama_cpp import Llama
    weights = artifact_path('/run/media/mutasim/Data/AGERE/weights/tier8_v2')
    tokens, token_summary = [], {}
    for arm, filename in [('mas', 'qwen2.5-3b-instruct-q4_k_m.gguf'),
            ('sas', 'qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf')]:
        tokenizer = Llama(model_path=str(weights / filename), vocab_only=True,
            n_gpu_layers=0, n_threads=1, n_threads_batch=1, verbose=False)
        try:
            measured = []
            for row in prompts:
                n = {k: len(completion_tokens(tokenizer, row[k])) for k in
                    ('original', 'catalog_only', 'header_materialization')}
                measured.append({'id': row['id'], 'arm': arm, 'prompt_tokens': n,
                    'catalog_only_full_draft_reserve_fits': n['catalog_only'] + 768 + 8 <= 4096})
            tokens.extend(measured)
            extra = [x['prompt_tokens']['catalog_only'] - x['prompt_tokens']['original'] for x in measured]
            token_summary[arm] = {'n': len(measured), 'catalog_only_extra_tokens_total': sum(extra),
                'catalog_only_extra_tokens_median': statistics.median(extra),
                'catalog_only_extra_tokens_max': max(extra),
                'header_extra_tokens_total': sum(x['prompt_tokens']['header_materialization'] - x['prompt_tokens']['original'] for x in measured),
                'catalog_only_full_draft_reserve_fits': sum(x['catalog_only_full_draft_reserve_fits'] for x in measured)}
        finally:
            tokenizer.close()
    if sha(sealed) != digest:
        raise ValueError('Catalogs changed after sealing')
    check_inputs(plan)
    for name, records in [('coverage.jsonl', detail), ('tokens.jsonl', tokens), ('captured-prompts.jsonl', prompts)]:
        (out / name).write_text(''.join(json.dumps(x) + '\n' for x in records))
    files = [Path(__file__), Path(__file__).with_name('source_span_catalog.py'),
        *[out / n for n in ('catalogs.jsonl', 'coverage.jsonl', 'tokens.jsonl', 'captured-prompts.jsonl')]]
    result = {'status': 'complete_offline_catalog_only_fitting_baseline', 'counts': dict(counts),
        'transitions': dict(transitions), 'token_summary': token_summary,
        'catalogs_sealed_before_reference_diagnostics': True,
        'source_packets_and_old_quantity_ids_unchanged': True,
        'all_candidate_quantities_execute_against_original_source': True,
        'neural_forward_calls': 0, 'adopted': False, 'novelty_established': False,
        'input_sha256': {**plan['input_sha256'], **{str(p): sha(p) for p in files}},
        'limits': 'Exploratory fitting73 only. New entries are span-value pairs, not localized cells; no unique-cell binding or semantic certification. Catalog/grammar/prompt tokens change although original source text/IDs remain. Direct compact first-draft capture only; no full-policy context or HF/SFT parity proof. Vocab-only counters use pinned model paths without full weight rehash here; future neural work requires normal full checks. Temporary patch is local to this metadata process; active workers/files and prepared neural study are unchanged.'}
    (out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'out': str(out), 'counts': dict(counts), 'token_summary': token_summary}))


if __name__ == '__main__':
    main()
