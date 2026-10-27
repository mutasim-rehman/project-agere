"""Seal fitting-only header-materialized packets, then audit coverage and tokens.

No neural forwards or changes to active study packets/training/inference. This
is source retention preparation, not a novel or validated QA method.
"""
from collections import Counter
from decimal import InvalidOperation
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from tier8_artifact_paths import artifact_path
from table_header_materialization import materialize, atom_facts
from evidence_atoms import atom_catalog
from program_binding_domains import binding_domains
from tier8_v2_adaptation_prompts import capture
from completion_tokenization import completion_tokens


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def state(program, packet):
    try:
        p = binding_domains(program, atom_catalog(packet['evidence']))
        return 'mappable', p['numeric_binding_unique']
    except InvalidOperation: return 'numeric_literal_failure', False
    except ValueError as exc: return str(exc), False


def main():
    base = artifact_path('/run/media/mutasim/Data/AGERE/datasets/tier8_v2_natural/natural_reports62_01')
    public_path, source_path = base / 'fitting-public.jsonl', base / 'source-train.json'
    selection_path = base / 'selection.json'; selection = json.loads(selection_path.read_text())['partitions']['fitting']
    public = [json.loads(x) for x in public_path.read_text().splitlines()]
    if (sorted(p['id'] for p in public) != sorted(selection['ids']) or
            artifact_path(selection['public_file']) != public_path or sha(public_path) != selection['sha256']):
        raise ValueError('Require unchanged exact fitting partition')
    original = json.loads(source_path.read_text()); source = {r['id']: r for r in original}
    if len(source) != len(original): raise ValueError('Duplicate source IDs')
    out = artifact_path('/run/media/mutasim/Data/AGERE/runs/tier8_representation_audit/header-materialization-fitting-01')
    if out.exists(): raise ValueError('Fresh fitting diagnostic output required')
    candidate = []
    for p in public:
        row = source[p['id']]
        if row['qa']['question'] != p['question']: raise ValueError('Source question differs')
        candidate.append(materialize(p, row['table']))
    # Packet transform accepts only public input + raw table, never QA references.
    # Seal every packet before reference-based diagnostic or token counting.
    out.mkdir(parents=True); data = out / 'candidate-public.jsonl'
    data.write_text(''.join(json.dumps(x, sort_keys=True) + '\n' for x in candidate)); sealed = sha(data)
    rows, transitions, counts = [], Counter(), Counter()
    for old, new in zip(public, candidate):
        if list(old['evidence']) != list(new['evidence']) or atom_facts(old['evidence']) - atom_facts(new['evidence']):
            raise ValueError('Old source selection or catalog fact lost')
        a, ua = state(source[old['id']]['qa']['program'], old); b, ub = state(source[old['id']]['qa']['program'], new)
        transitions[a + ' -> ' + b] += 1
        counts.update({'mappable_before': a == 'mappable', 'mappable_after': b == 'mappable',
            'unique_before': ua, 'unique_after': ub})
        rows.append({'id': old['id'], 'before': a, 'after': b, 'unique_before': ua, 'unique_after': ub,
            'appended_cells': len(new['first_row_materialization']['appended_cells']),
            'extra_evidence_characters': sum(len(new['evidence'][k])-len(v) for k,v in old['evidence'].items())})
    from llama_cpp import Llama
    weights = artifact_path('/run/media/mutasim/Data/AGERE/weights/tier8_v2')
    profiles = [('mas', 'qwen2.5-3b-instruct-q4_k_m.gguf'),
                ('sas', 'qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf')]
    tokens = []
    for arm, filename in profiles:
        model = Llama(model_path=str(weights / filename), vocab_only=True, n_gpu_layers=0,
            n_threads=1, n_threads_batch=1, verbose=False)
        try:
            for old, new in zip(public, candidate):
                before, after = [capture(p, arm) for p in (old,new)]
                a,b = [len(completion_tokens(model, p['prompt'])) for p in (before,after)]
                tokens.append({'id':old['id'], 'arm':arm, 'before_prompt_tokens':a, 'after_prompt_tokens':b,
                    'extra_prompt_tokens':b-a, 'before_full_draft_reserve_fits':a+768+8<=4096,
                    'after_full_draft_reserve_fits':b+768+8<=4096})
        finally: model.close()
    if sha(data) != sealed: raise ValueError('Sealed packets changed while auditing')
    detail = out / 'coverage.jsonl'; detail.write_text(''.join(json.dumps(x)+'\n' for x in rows))
    token_file = out / 'tokens.jsonl'; token_file.write_text(''.join(json.dumps(x)+'\n' for x in tokens))
    token_summary = {}
    for arm,_ in profiles:
        measured = [x for x in tokens if x['arm']==arm]; extra = [x['extra_prompt_tokens'] for x in measured]
        token_summary[arm] = {'n':len(measured), 'total_extra_prompt_tokens':sum(extra),
            'median_extra_prompt_tokens':statistics.median(extra),'max_extra_prompt_tokens':max(extra),
            'before_full_draft_reserve_fits':sum(x['before_full_draft_reserve_fits'] for x in measured),
            'after_full_draft_reserve_fits':sum(x['after_full_draft_reserve_fits'] for x in measured),
            'new_reserve_failures':sum(x['before_full_draft_reserve_fits'] and not x['after_full_draft_reserve_fits'] for x in measured)}
    files = [Path(__file__),public_path,source_path,selection_path,*sorted((ROOT/'scripts').glob('*.py'))]
    result = {'status':'complete_offline_fitting_prototype','n':len(rows),'counts':dict(counts),
        'transitions':dict(transitions),'changed_cases':[x for x in rows if (x['before'],x['unique_before'])!=(x['after'],x['unique_after'])],
        'all_old_span_keys_order_and_catalog_facts_retained':True,'packet_sealed_before_reference_scoring':True,
        'tokenizer_only':True,'neural_forward_calls':0,'token_summary':token_summary,
        'candidate_public_sha256':sealed,'coverage_sha256':sha(detail),'tokens_sha256':sha(token_file),
        'input_sha256':{str(p):sha(p) for p in files},'adopted':False,'natural_qa_gain_demonstrated':False,
        'limits':'Outcome-guided exploratory fitting73 only; no selection/reserved packets modified. Same eight selected span IDs but extra source content/prompt tokens, not information/token-matched. Augmented spans are context groups with source row/column/offset ledger. Existing-parser mapping/unique numeric identities are not semantic certification. No trainable SFT corpus, HF/GGUF parity or full-policy context proof. Vocab-only counters use existing pinned model paths without full weight rehash here; future training/evaluation still requires normal full checks. Known preprocessing baseline candidate, no first-use novelty.'}
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'result':str(out),'counts':result['counts'],'token_summary':token_summary}))


if __name__=='__main__':main()
