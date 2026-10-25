"""Prepare weakly annotated, balanced verifier SFT without touching test data.

Reference positives reproduce training annotations. Executable single-edit
negatives fail both numerical metrics. This is not semantic adjudication, a novel
method, or a natural-error distribution. Rows and tokenization evidence stay SSD.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path

from tier8_v2_adaptation_data import validate_prepared
from tier8_v2_adaptation_prompts import tokenized_target
from tier8_v2_critic_probe import BINARY_INSTRUCTION
from tier8_v2_demo_retrieval import BANK
from tier8_v2_run import Models
from evidence_atoms import atom_catalog,compile_plan
from evidence_calculator import execute,OPERATIONS
from tier8_v2_financial_pipeline import evaluate_financial

ROOT=Path(__file__).resolve().parents[1]
PROFILE='mas-3b-q4'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def write(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n')
def rank(source,change):return hashlib.sha256(('42|'+source+'|'+json.dumps(change,sort_keys=True)).encode()).hexdigest()

def negative_candidates(row,gold):
    atoms=atom_catalog(row['public']['evidence']);evidence=row['public']['evidence'];target=row['target']
    pool=[k for k,v in row['cell_view']['catalog'].items() if v['cell_role']=='data']
    for i,step in enumerate(target['steps']):
        edits=[({'kind':'operation','step':i,'before':step['op'],'after':op},'op',op) for op in OPERATIONS if op!=step['op']]
        for side in ['left','right']:
            original=step[side]
            if original not in atoms:continue
            alternatives=sorted((k for k in pool if atoms[k]['value']!=atoms[original]['value']),key=lambda k:rank(row['source_id'],{'step':i,'side':side,'ref':k}))[:8]
            edits += [({'kind':'operand','step':i,'side':side,'before':original,'after':ref},side,ref) for ref in alternatives]
        for change,key,value in edits:
            candidate=deepcopy(target);candidate['steps'][i][key]=value
            compiled=compile_plan(candidate,atoms);execution=execute(compiled['steps'],evidence)
            if execution['issues']:continue
            metric=evaluate_financial(gold,compiled,execution)
            if not metric['case_success'] and not metric['raw_execution_match']:
                yield compiled,execution,change

def select_negative(source,choices):
    families=sorted({change['kind'] for _,_,change in choices})
    family=families[int(hashlib.sha256(('family42|'+source).encode()).hexdigest(),16)%len(families)]
    return min((item for item in choices if item[2]['kind']==family),key=lambda x:rank(source,x[2]))

def prompt(public,candidate,execution):
    content='Question: '+public['question']+'\nFinancial report evidence by source ID:\n'+json.dumps(public['evidence'])+'\nProposed program:\n'+json.dumps(candidate)+'\nDeterministic execution:\n'+json.dumps(execution)+'\n'+BINARY_INSTRUCTION
    return Models.prompt(content)

def validate_groups(rows,excluded):
    train={r['report_group'] for r in rows if r['split']=='train'}
    val={r['report_group'] for r in rows if r['split']=='validation'}
    if train&val or (train|val)&set(excluded):raise ValueError('Report group leakage')
    if any(r['split'] not in ['train','validation'] for r in rows):raise ValueError('Unexpected split')
    return train,val

def build(root):
    from llama_cpp import Llama
    baseline=json.loads((ROOT/'research/tier8_v2/evidence/deployment-sft-1024-02.json').read_text())
    bank=json.loads((ROOT/BANK).read_text());train_path=ROOT/'.local/datasets/finqa/train.json'
    if sha(train_path)!=bank['source_sha256']:raise ValueError('Training annotation source changed')
    paths=[ROOT/f'research/tier8_v2/data/finqa-cell-adaptation-{s}-02.jsonl' for s in ['train','validation']]
    rows=[]
    for path in paths:
        if sha(path)!=baseline['input_sha256'][str(path.relative_to(ROOT))]:raise ValueError('Prepared source changed')
        rows += [json.loads(s) for s in path.read_text().splitlines()]
    train_groups,val_groups=validate_groups(rows,bank['excluded_report_groups'])
    gold={r['id']:r for r in json.loads(train_path.read_text())}
    ssd=Path(os.environ['AGERE_SSD_ROOT']).resolve()
    model=ssd/'weights/tier8_v2/qwen2.5-3b-instruct-q4_k_m.gguf'
    entry=json.loads((ROOT/'research/tier8_v2/evidence/candidate-model-3b.json').read_text())
    if sha(model)!=entry['sha256']:raise ValueError('Pinned GGUF tokenizer model changed')
    tokenizer=Llama(model_path=str(model),vocab_only=True,verbose=False)
    output=root/'examples.jsonl';rejected=Counter();kept=Counter();kinds=Counter();groups={'train':set(),'validation':set()};n=0
    for row in rows:
        validate_prepared(row);g=gold[row['source_id']];public=row['public']
        positive=compile_plan(row['target'],atom_catalog(public['evidence']));execution=execute(positive['steps'],public['evidence'])
        metric=evaluate_financial(g,positive,execution)
        if not metric['case_success'] or not metric['raw_execution_match']:rejected['reference_not_both_metrics_correct']+=1;continue
        choices=list(negative_candidates(row,g))
        if not choices:rejected['no_executable_wrong_single_edit']+=1;continue
        candidate,computed,change=select_negative(row['source_id'],choices)
        pair=[]
        try:
            for kind,answer,result,target in [('reference',positive,execution,{'verdict':'PASS'}),('mutation',candidate,computed,{'verdict':'FAIL'})]:
                rendered=prompt(public,answer,result)
                tokenized=tokenized_target(tokenizer,rendered,target,1024)
                if tokenized['completion_tokens']>192:raise ValueError('critic_target_exceeds_budget')
                pair.append({'source_id':row['source_id']+'::'+kind,'original_source_id':row['source_id'],'report_group':row['report_group'],'split':row['split'],'purpose':'critic','prompt':rendered,'target':target,'tokenization':{PROFILE:tokenized},'annotation_scope':'Reference reproduces source annotation under both numerical metrics; not independently adjudicated semantics. Mutation executes with source support but fails both metrics.','mutation':change if kind=='mutation' else None})
        except ValueError as exc:rejected[str(exc)]+=1;continue
        with output.open('a') as f:
            for example in pair:f.write(json.dumps(example)+'\n')
        kept[row['split']]+=2;groups[row['split']].add(row['report_group']);kinds[change['kind']]+=1;n+=2
    tokenizer.close()
    if min(kept.values(),default=0)<=0 or set(kept)!= {'train','validation'}:raise ValueError('Empty split')
    manifest={'purpose':'critic','target_role':'verifier','profiles':[PROFILE],'output_file':str(output),'output_sha256':sha(output),'kept_n':n,'training_n':kept['train'],'validation_n':kept['validation'],'kept_pairs':n//2,'max_training_tokens':1024,'deployment_context':4096,'target_budget':192,'group_counts':{k:len(v) for k,v in groups.items()},'eligible_source_group_counts':{'train':len(train_groups),'validation':len(val_groups)},'mutation_counts':dict(kinds),'rejected_pairs':dict(rejected),'balance':'one annotation-positive and one executable numerically wrong single-edit negative per retained source; reject both on length overflow','selection':'seed42 source-ID SHA selects eligible mutation family, then minimum mutation SHA within family; at most8 hashed alternatives per source operand','input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [*paths,train_path,ROOT/BANK]},'source_sha256':{p:sha(ROOT/p) for p in ['scripts/tier8_v2_critic_data.py','scripts/tier8_v2_critic_probe.py','scripts/tier8_v2_adaptation_data.py','scripts/tier8_v2_adaptation_prompts.py','scripts/tier8_v2_financial_pipeline.py','scripts/tier8_v2_run.py','scripts/evidence_atoms.py','scripts/evidence_calculator.py','scripts/evidence_cells.py']},'model_calls':0,'test_opened':False,'limits':'Weakly supervised annotated-program discrimination. Controlled mutations differ from natural errors. No per-field semantic labels, novelty, trained adapter or QA gain claimed.'}
    write(root/'manifest.json',manifest);print(json.dumps({k:manifest[k] for k in ['kept_n','training_n','validation_n','mutation_counts','rejected_pairs','group_counts']}),flush=True)

def parity(root):
    os.environ.update(HF_HOME=str(ROOT/'.local/hf-training'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    from transformers import AutoTokenizer,__version__ as version
    import tokenizers
    manifest=json.loads((root/'manifest.json').read_text());data=Path(manifest['output_file'])
    if sha(data)!=manifest['output_sha256']:raise ValueError('Dataset changed')
    snapshot=ROOT/'research/tier8_v2/evidence/hf-tokenizer-snapshots-01.json';assets=json.loads(snapshot.read_text())['profiles'][PROFILE];folder=ROOT/assets['folder']
    for entry in assets['files']:
        if sha(folder/entry['file'])!=entry['sha256']:raise ValueError('Pinned HF assets changed')
    tokenizer=AutoTokenizer.from_pretrained(str(folder),local_files_only=True,trust_remote_code=False);n=0;fail=[]
    for row in map(json.loads,data.read_text().splitlines()):
        expected=row['tokenization'][PROFILE];prefix=tokenizer.encode(row['prompt'],add_special_tokens=False);full=tokenizer.encode(row['prompt']+expected['response'],add_special_tokens=False)
        if hashlib.sha256(json.dumps(full).encode()).hexdigest()!=expected['input_ids_sha256'] or full[:len(prefix)]!=prefix or len(prefix)!=expected['label_mask_prefix_tokens'] or len(full)!=expected['total_tokens'] or len(full)>1024:fail.append(row['source_id'])
        n+=1
    report={'pass':not fail and n==manifest['kept_n'],'n':n,'failures':fail,'dataset_sha256':sha(data),'dataset_manifest_sha256':sha(root/'manifest.json'),'snapshots_sha256':sha(snapshot),'transformers_version':version,'tokenizers_version':tokenizers.__version__,'profile':PROFILE,'model_calls':0,'script_sha256':sha(Path(__file__))}
    if (root/'parity.json').exists():raise ValueError('Refuse parity overwrite')
    write(root/'parity.json',report);print(json.dumps(report),flush=True)
    if not report['pass']:raise ValueError('Tokenizer parity failed')

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['build','parity']);p.add_argument('--run-id',required=True);a=p.parse_args()
    import re
    if not re.fullmatch('[a-zA-Z0-9_-]+',a.run_id):raise ValueError('Unsafe run ID')
    root=Path(os.environ['AGERE_SSD_ROOT']).resolve()/'datasets/tier8_v2_critic'/a.run_id
    if a.mode=='build':root.mkdir(parents=True,exist_ok=False);build(root)
    else:parity(root)

if __name__=='__main__':main()
