"""Train-only diagnostic of critic discrimination and output protocol effects.

Reference positives are annotation-consistent, not independently adjudicated.
Counterfactual negatives are single-operation mutations that execute with valid
source references but fail both recorded numerical correctness metrics.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from tier8_v2_adaptation_data import validate_prepared
from evidence_atoms import atom_catalog,compile_plan
from evidence_calculator import execute,OPERATIONS
from evidence_contract import TokenLedger
from tier8_v2_financial_pipeline import VERIFY,verdict,evaluate_financial
from tier8_v2_run import Models
from tier8_v2_adapter_runtime import load_critic_adapter
from tier8_artifact_paths import artifact_path

ROOT=Path(__file__).resolve().parents[1]
RICH_INSTRUCTION=('Independently judge operand relevance (correct row/year), operations, and units for the question. '
 'Arithmetic execution alone does not prove relevance. Return checks, steps_to_repair, repair_kind. '
 'Use NONE only if all checks PASS and no steps need repair; PATCH for localized step corrections; '
 'REPLAN for an incorrect/missing sequence of operations. UNKNOWN means evidence is insufficient.')
BINARY_INSTRUCTION=('Independently judge operand relevance (correct row/year), operations, and units for the question. '
 'Arithmetic execution alone does not prove relevance. Return verdict PASS only if all three are correct; '
 'FAIL if any is incorrect; UNKNOWN if evidence is insufficient.')
BINARY={'type':'object','properties':{'verdict':{'enum':['PASS','FAIL','UNKNOWN']}},'required':['verdict'],'additionalProperties':False}

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def append(p,d):
    with p.open('a') as f:f.write(json.dumps(d)+'\n');f.flush();os.fsync(f.fileno())

def mutations(target,evidence,gold):
    atoms=atom_catalog(evidence)
    for i,step in enumerate(target['steps']):
        for op in OPERATIONS:
            if op==step['op']:continue
            plan=deepcopy(target);plan['steps'][i]['op']=op
            compiled=compile_plan(plan,atoms);execution=execute(compiled['steps'],evidence)
            if execution['issues']:continue
            score=evaluate_financial(gold,compiled,execution)
            if not score['case_success'] and not score['raw_execution_match']:
                yield compiled,execution,{'step':i,'old_operation':step['op'],'new_operation':op}

def prepare(limit):
    source=ROOT/'research/tier8_v2/data/finqa-cell-adaptation-validation-02.jsonl'
    train=ROOT/'.local/datasets/finqa/train.json'
    gold={r['id']:r for r in json.loads(train.read_text())}
    prepared=[];labels=[];groups=set()
    for r in map(json.loads,source.read_text().splitlines()):
        if r['report_group'] in groups:continue
        validate_prepared(r);public=r['public'];answer=compile_plan(r['target'],atom_catalog(public['evidence']))
        execution=execute(answer['steps'],public['evidence']);g=gold[r['source_id']]
        positive=evaluate_financial(g,answer,execution)
        if not positive['case_success'] or not positive['raw_execution_match']:continue
        negative=next(mutations(r['target'],public['evidence'],g),None)
        if negative is None:continue
        groups.add(r['report_group'])
        for variant,candidate,computed,expected,mutation in [('reference',answer,execution,True,None),('operation_mutation',negative[0],negative[1],False,negative[2])]:
            ident=f"{public['id']}::{variant}"
            prepared.append({'id':ident,'question':public['question'],'evidence':public['evidence'],'candidate':candidate,'execution':computed})
            labels.append({'id':ident,'source_id':r['source_id'],'report_group':r['report_group'],'expected_accept':expected,'construction':variant,'mutation':mutation,'quality_scope':r['quality_scope']})
        if len(groups)==limit:break
    if len(groups)!=limit:raise ValueError('Insufficient independent qualifying report groups')
    return prepared,labels,{'validation_source_sha256':sha(source),'training_gold_sha256':sha(train),'report_groups':sorted(groups),'selection':'first qualifying validation record per distinct report group; no inference-dependent filtering','scope':'train-only controlled discrimination probe, not a natural-error benchmark or external confirmation'}

def worker(root,profile):
    from llama_cpp import Llama,LlamaGrammar
    m=json.loads((root/'manifest.json').read_text());entry=m['models'][profile]
    adapter=load_critic_adapter(m['adapter_directory']) if m.get('adapter_directory') else None
    if adapter and profile!='3b':raise ValueError('Trained critic supports 3B only')
    options={'lora_path':str(artifact_path(adapter['file'])),'lora_scale':1.0} if adapter else {}
    model=Llama(model_path=entry['ssd_file'],n_ctx=4096,n_gpu_layers=0,n_threads=8,n_threads_batch=8,n_batch=64,n_ubatch=64,seed=42,use_mmap=False,verbose=False,**options)
    if adapter and not getattr(model,'_lora_adapter',None):raise ValueError('Critic adapter backend handle missing')
    runtime=Models.__new__(Models);runtime.models={'verifier':model};runtime.context=4096;runtime.grammar=LlamaGrammar
    for r in map(json.loads,(root/'public.jsonl').read_text().splitlines()):
        content='Question: '+r['question']+'\nFinancial report evidence by source ID:\n'+json.dumps(r['evidence'])+'\nProposed program:\n'+json.dumps(r['candidate'])+'\nDeterministic execution:\n'+json.dumps(r['execution'])
        budget=TokenLedger()
        for protocol,instruction,schema in [('rich',RICH_INSTRUCTION,VERIFY),('binary',BINARY_INSTRUCTION,BINARY)]:
            if protocol not in m.get('protocols',['rich','binary']):continue
            raw,event=runtime.call('verifier',content+'\n'+instruction,schema,budget,192,'critic_probe_'+protocol)
            review=verdict(raw) if protocol=='rich' else raw
            append(root/f'{profile}-responses.jsonl',{'id':r['id'],'protocol':protocol,'raw':raw,'verdict':review.get('verdict') if isinstance(review,dict) else None,'adapter_application':{**adapter,'runtime_handle_initialized':True} if adapter else None,'event':event})
            print(profile,r['id'],protocol,review,flush=True)
    model.close()

def main():
    import psutil
    p=argparse.ArgumentParser();p.add_argument('--run-id',required=True);p.add_argument('--groups',type=int,default=12);p.add_argument('--worker',choices=['0.5b','3b'])
    p.add_argument('--profile',choices=['all','0.5b','3b'],default='all');p.add_argument('--protocol',choices=['all','rich','binary'],default='all')
    p.add_argument('--inputs');p.add_argument('--adapter');p.add_argument('--application-proof');args=p.parse_args()
    import re
    if not re.fullmatch('[a-zA-Z0-9_-]+',args.run_id):raise ValueError('Unsafe run ID')
    ssd=Path(os.environ['AGERE_SSD_ROOT']).resolve();root=ssd/'runs/tier8_critic_probe'/args.run_id
    if args.worker:worker(root,args.worker);return
    if args.adapter and (args.profile!='3b' or args.protocol!='binary' or not args.application_proof):raise ValueError('Trained critic requires 3B binary protocol and application proof')
    import fcntl
    lock=(ssd/'runs/tier8_external.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    names={'tier8_external_eval.py','tier8_external_recover.py','tier8_v2_run.py','tier8_v2_adapt.py','tier8_v2_critic_probe.py'}
    for proc in psutil.process_iter(['pid','cmdline']):
        if proc.pid!=os.getpid() and any(Path(a).name in names for a in (proc.info['cmdline'] or [])):raise RuntimeError('Another model workload is active')
    cap=min(6400000000,psutil.virtual_memory().available-1000000000)
    if cap<3400000000:raise MemoryError('Insufficient room for single-critic diagnostic')
    root.mkdir(parents=True,exist_ok=False)
    adapter=load_critic_adapter(args.adapter) if args.adapter else None
    proof_sha=None
    if adapter:
        proof_root=artifact_path(args.application_proof)
        proof_summary=json.loads((proof_root/'summary.json').read_text());proof=json.loads((proof_root/'proof.json').read_text())
        if proof_summary['status']!='complete' or not proof['pass'] or proof['adapter']['sha256']!=adapter['sha256'] or proof['adapter']['purpose']!='critic':raise ValueError('Applied critic proof does not match adapter')
        proof_sha=sha(proof_root/'proof.json')
    if args.inputs:
        source=artifact_path(args.inputs);original=json.loads((source/'manifest.json').read_text())
        if original['status']!='complete' or sha(source/'public.jsonl')!=original['public_sha256'] or sha(source/'labels.jsonl')!=original['labels_sha256']:raise ValueError('Frozen probe inputs invalid')
        public=[json.loads(s) for s in (source/'public.jsonl').read_text().splitlines()];labels=[json.loads(s) for s in (source/'labels.jsonl').read_text().splitlines()]
        if len(public)!=2*args.groups or len(labels)!=len(public):raise ValueError('Frozen probe count differs')
        provenance={**original['provenance'],'copied_from':str(source),'copied_manifest_sha256':sha(source/'manifest.json')}
    else:public,labels,provenance=prepare(args.groups)
    profiles=['0.5b','3b'] if args.profile=='all' else [args.profile]
    protocols=['rich','binary'] if args.protocol=='all' else [args.protocol]
    for row in public:append(root/'public.jsonl',row)
    for row in labels:append(root/'labels.jsonl',row)
    sources=['scripts/tier8_v2_critic_probe.py','scripts/tier8_v2_run.py','scripts/tier8_v2_financial_pipeline.py','scripts/completion_tokenization.py','scripts/evidence_atoms.py','scripts/evidence_calculator.py','scripts/evidence_contract.py','scripts/tier8_v2_adaptation_data.py','scripts/evidence_cells.py']
    sources+=['scripts/tier8_v2_adapter_runtime.py','scripts/tier8_v2_adapter_convert.py','scripts/tier8_artifact_paths.py','scripts/financial_review_protocol.py']
    manifest={'status':'preflight','cap_bytes':cap,'provenance':provenance,'public_sha256':sha(root/'public.jsonl'),'labels_sha256':sha(root/'labels.jsonl'),'source_sha256':{n:sha(ROOT/n) for n in sources},'models':{},'profiles':{},'protocols':protocols,'adapter_directory':str(artifact_path(args.adapter)) if args.adapter else None,'adapter':adapter,'application_proof_sha256':proof_sha,'n_programs':len(public),'n_calls_per_profile':len(protocols)*len(public),'context':4096,'max_tokens_per_protocol':192,'max_tokens_per_program':192*len(protocols),'note':'Each critic loaded alone. Rich vs binary changes protocol/instructions, not an isolated JSON-schema effect. Applied adapter only when explicitly requested and validated.'}
    write(root/'manifest.json',manifest)
    entries=[json.loads((ROOT/'research/tier8_v2/evidence/candidate-model-3b.json').read_text())]+json.loads((ROOT/'research/tier8_v2/evidence/native-models.json').read_text())
    for profile,name in [('0.5b','qwen2.5-0.5b-instruct-native-f16.gguf'),('3b','qwen2.5-3b-instruct-q4_k_m.gguf')]:
        if profile not in profiles:continue
        entry=next(e for e in entries if Path(e['file']).name==name);source=ROOT/entry['file']
        dest=ssd/'weights/tier8_v2'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():
            partial=dest.with_suffix('.copying')
            with source.open('rb') as f,partial.open('xb') as g:shutil.copyfileobj(f,g,8*1024*1024)
            if partial.stat().st_size!=entry['bytes'] or sha(partial)!=entry['sha256']:raise ValueError('SSD model copy differs')
            partial.rename(dest)
        if dest.stat().st_size!=entry['bytes'] or sha(dest)!=entry['sha256']:raise ValueError('SSD model identity differs')
        manifest['models'][profile]={**entry,'ssd_file':str(dest)};write(root/'manifest.json',manifest)
    manifest['status']='running';write(root/'manifest.json',manifest)
    for profile in profiles:
        if sha(root/'public.jsonl')!=manifest['public_sha256'] or sha(root/'labels.jsonl')!=manifest['labels_sha256']:raise ValueError('Frozen diagnostic data changed')
        for n,digest in manifest['source_sha256'].items():
            if sha(ROOT/n)!=digest:raise ValueError('Frozen source changed')
        with (root/f'{profile}-worker.log').open('x') as log:
            child=subprocess.Popen([sys.executable,'-u',str(Path(__file__)),'--run-id',args.run_id,'--worker',profile],stdout=log,stderr=log)
            proc=psutil.Process(child.pid);peak=0;breach=False
            while child.poll() is None:
                try:rss=sum(p.memory_info().rss for p in [psutil.Process(),proc,*proc.children(recursive=True)] if p.is_running())
                except psutil.NoSuchProcess:continue
                peak=max(peak,rss);available=psutil.virtual_memory().available
                append(root/f'{profile}-memory.jsonl',{'time':time.time(),'tree_rss_bytes':rss,'host_available_bytes':available})
                if rss>cap or available<1000000000:breach=True;child.kill();break
                time.sleep(.2)
            code=child.wait()
        responses=[json.loads(s) for s in (root/f'{profile}-responses.jsonl').read_text().splitlines()] if (root/f'{profile}-responses.jsonl').exists() else []
        expected={(r['id'],protocol) for r in public for protocol in protocols}
        actual=[(r['id'],r['protocol']) for r in responses]
        if len(set(actual))!=len(actual) or not set(actual)<=expected:raise ValueError('Duplicate or unexpected responses')
        target={r['id']:r for r in labels};summary={}
        for protocol in protocols:
            rows=[r for r in responses if r['protocol']==protocol]
            summary[protocol]={'n':len(rows),'true_accept':sum(r['verdict']=='PASS' and target[r['id']]['expected_accept'] for r in rows),'false_accept':sum(r['verdict']=='PASS' and not target[r['id']]['expected_accept'] for r in rows),'false_reject':sum(r['verdict']!='PASS' and target[r['id']]['expected_accept'] for r in rows),'true_reject':sum(r['verdict']!='PASS' and not target[r['id']]['expected_accept'] for r in rows),'unknown':sum(r['verdict']=='UNKNOWN' for r in rows),'unparsed':sum(r['verdict'] is None for r in rows)}
        manifest['profiles'][profile]={'status':'complete' if code==0 and not breach and len(responses)==len(protocols)*len(public) else 'failed','exit_code':code,'peak_tree_rss_bytes':peak,'cap_bytes':cap,'protocols':summary};write(root/'manifest.json',manifest)
        if manifest['profiles'][profile]['status']!='complete':raise RuntimeError('Incomplete critic diagnostic')
    manifest['status']='complete';write(root/'manifest.json',manifest);print(json.dumps(manifest['profiles']),flush=True)

if __name__=='__main__':main()
