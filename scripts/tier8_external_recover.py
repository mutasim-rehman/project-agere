"""Continue an interrupted SSD evaluation using its unchanged generation worker.

Completed records are validated and retained, never rewritten. New records live
in a separate recovery segment; aggregate summaries cite both source files.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import tier8_external_eval as baseline

ROOT = Path(__file__).resolve().parents[1]


def read_rows(path):
    if not path.exists(): return []
    raw = path.read_bytes()
    if raw and not raw.endswith(b'\n'): raise ValueError(f'Incomplete JSONL tail: {path}')
    return [json.loads(line) for line in raw.splitlines()]


def validate_prefix(records, source, task, arm):
    ids = [r.get('question_id',r.get('id')) for r in source]
    if len(set(ids)) != len(ids) or len(records)>len(source): raise ValueError('Duplicate source IDs or excess records')
    roles = ['sas','sas'] if arm=='sas' else ['extractor','drafter','verifier','drafter']
    for record,row,expected_id in zip(records,source,ids):
        if record['id']!=expected_id or record['gold']!=row['answer']: raise ValueError('Records are not the exact original prefix')
        if record['score']!=baseline.score(record['prediction'],row,task): raise ValueError('Stored score cannot be reproduced')
        stages=record['stages']
        if [s['role'] for s in stages]!=roles: raise ValueError('Incomplete/changed stage sequence')
        used=[s['usage']['completion_tokens'] for s in stages]
        if any(type(n)!=int or n<0 for n in used) or sum(used)!=record['generated_tokens'] or sum(used)>2048: raise ValueError('Invalid token ledger')
        prediction=baseline.parse(stages[-1]['response']) if task=='mortar' else stages[-1]['response']
        if prediction!=record['prediction']: raise ValueError('Prediction differs from the final stage')
    return len(records)


def main():
    import psutil
    parser=argparse.ArgumentParser()
    parser.add_argument('--original',required=True);parser.add_argument('--recovery-id',required=True)
    parser.add_argument('--worker',action='store_true');parser.add_argument('--task',choices=baseline.DATA);parser.add_argument('--arm',choices=baseline.SPECS)
    args=parser.parse_args()
    import re
    if not all(re.fullmatch(r'[a-zA-Z0-9_-]+',s) for s in (args.original,args.recovery_id)): raise ValueError('Unsafe run ID')
    ssd=Path(os.environ['AGERE_SSD_ROOT']).resolve()
    original=ssd/'runs/tier8_external'/args.original
    recovery=ssd/'runs/tier8_external'/args.recovery_id
    group=recovery/f'{args.task}-{args.arm}' if args.worker else None
    if args.worker:
        policy=json.loads((recovery/'manifest.json').read_text())
        for name,digest in policy['source_sha256'].items():
            if baseline.sha(ROOT/name)!=digest: raise ValueError('Frozen recovery/generation source changed')
        baseline.DATA[args.task]=str((group/'remaining-source.jsonl').relative_to(ssd))
        baseline.worker(args,ssd,group/'segment')
        return
    import fcntl
    lock=(ssd/'runs/tier8_external.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    workloads={'tier8_external_eval.py','tier8_external_recover.py','tier8_v2_run.py','tier8_v2_adapt.py','tier8_study.py','phase3.py','eval_checkpoints.py'}
    for p in psutil.process_iter(['pid','cmdline']):
        if p.pid!=os.getpid() and any(Path(a).name in workloads for a in (p.info['cmdline'] or [])): raise RuntimeError('Another evaluation/training workload is live')
    prior=json.loads((original/'manifest.json').read_text())
    if prior['status']!='interrupted': raise ValueError('Requires explicitly audited interrupted original run')
    if baseline.sha(ROOT/'scripts/tier8_external_eval.py')!=prior['source_sha256']: raise ValueError('Original generation worker changed')
    if baseline.sha(ROOT/'scripts/completion_tokenization.py')!=prior['tokenization_sha256']: raise ValueError('Original tokenizer accounting changed')
    cap=prior['cap_bytes']
    if psutil.virtual_memory().available < cap+1000000000: raise MemoryError('Cannot preserve original cap and host reserve')
    recovery.mkdir(parents=True,exist_ok=False)
    manifest={'status':'preflight','original':str(original),'original_manifest_sha256':baseline.sha(original/'manifest.json'),
        'cap_bytes':cap,'source_sha256':{p:baseline.sha(ROOT/p) for p in ['scripts/tier8_external_recover.py','scripts/tier8_external_eval.py','scripts/completion_tokenization.py']},
        'generation_policy':'Unchanged original baseline.worker; resume filters only completed prefix; shared packets copied byte-for-byte by JSON record',
        'controller_pid':os.getpid(),'controller_create_time':psutil.Process().create_time(),'segments':{}}
    baseline.write(recovery/'manifest.json',manifest)
    child=None
    def terminate(signum, frame):
        raise InterruptedError(f'Controller received signal {signum}')
    signal.signal(signal.SIGTERM,terminate);signal.signal(signal.SIGINT,terminate)
    try:
        for model in prior['models']:
            p=ssd/model['path'];print('verifying',p.name,flush=True)
            if p.stat().st_size!=model['size_bytes'] or baseline.sha(p)!=model['sha256']: raise ValueError('Original model hash mismatch')
        for task,spec in prior['datasets'].items():
            if baseline.sha(ssd/spec['path'])!=spec['sha256'] or baseline.sha(original/f'{task}-packets.jsonl')!=spec['packet_sha256']: raise ValueError('Original data/packets changed')
            source=read_rows(ssd/spec['path']);packets=read_rows(original/f'{task}-packets.jsonl')
            if len(source)!=spec['n'] or len(packets)!=len(source) or any(p['question']!=r['question'] for p,r in zip(packets,source)): raise ValueError('Source/packet alignment failure')
            for arm in baseline.SPECS:
                label=f'{task}-{arm}';old=original/label;records=read_rows(old/'cases.jsonl')
                n=validate_prefix(records,source,task,arm)
                old_memory=read_rows(old/'memory.jsonl');old_peak=max([r['tree_rss_bytes'] for r in old_memory] or [0])
                if old_peak>cap: raise MemoryError('Original segment exceeded fixed cap')
                group=recovery/label;group.mkdir();(group/'segment').mkdir()
                for row in source[n:]:baseline.append(group/'remaining-source.jsonl',row)
                for row in packets[n:]:baseline.append(group/f'{task}-packets.jsonl',row)
                meta={'original_completed':n,'expected':len(source),'original_cases_sha256':baseline.sha(old/'cases.jsonl') if records else None,'original_peak_rss_bytes':old_peak,'status':'pending'}
                manifest['segments'][label]=meta
                if n==len(source):
                    meta['status']='already_complete';continue
                meta['remaining_source_sha256']=baseline.sha(group/'remaining-source.jsonl')
                meta['remaining_packets_sha256']=baseline.sha(group/f'{task}-packets.jsonl')
        manifest['status']='running';baseline.write(recovery/'manifest.json',manifest)
        for label,meta in manifest['segments'].items():
            task,arm=label.split('-');group=recovery/label;old=original/label
            if baseline.sha(original/'manifest.json')!=manifest['original_manifest_sha256']: raise ValueError('Original manifest changed')
            spec=prior['datasets'][task]
            if baseline.sha(ssd/spec['path'])!=spec['sha256'] or baseline.sha(original/f'{task}-packets.jsonl')!=spec['packet_sha256']: raise ValueError('Original source/packet changed')
            if meta['status']=='already_complete':continue
            for name,digest in manifest['source_sha256'].items():
                if baseline.sha(ROOT/name)!=digest:raise ValueError('Frozen source changed')
            if meta['original_cases_sha256'] and baseline.sha(old/'cases.jsonl')!=meta['original_cases_sha256']:raise ValueError('Original cases changed')
            for name,key in [('remaining-source.jsonl','remaining_source_sha256'),(f'{task}-packets.jsonl','remaining_packets_sha256')]:
                if baseline.sha(group/name)!=meta[key]:raise ValueError('Frozen continuation input changed')
            meta['status']='running';baseline.write(recovery/'manifest.json',manifest)
            command=[sys.executable,'-u',str(Path(__file__)),'--original',args.original,'--recovery-id',args.recovery_id,'--worker','--task',task,'--arm',arm]
            peak=0;breach=False
            with (group/'segment/worker.log').open('x') as log:
                child=subprocess.Popen(command,stdout=log,stderr=log)
                proc=psutil.Process(child.pid)
                baseline.append(recovery/'journal.jsonl',{'event':'worker_started','label':label,'pid':child.pid,'create_time':proc.create_time(),'time':time.time(),'skipped_validated_prefix':meta['original_completed']})
                while child.poll() is None:
                    try:rss=sum(p.memory_info().rss for p in [psutil.Process(),proc,*proc.children(recursive=True)] if p.is_running())
                    except psutil.NoSuchProcess:continue
                    available=psutil.virtual_memory().available;peak=max(peak,rss)
                    baseline.append(group/'segment/memory.jsonl',{'time':time.time(),'tree_rss_bytes':rss,'host_available_bytes':available})
                    if rss>cap or available<1000000000:
                        breach=True
                        for p in proc.children(recursive=True):p.kill()
                        child.kill();break
                    time.sleep(.2)
                code=child.wait();child=None
            source=read_rows(ssd/prior['datasets'][task]['path'])
            old_records=read_rows(old/'cases.jsonl');new_records=read_rows(group/'segment/cases.jsonl')
            all_records=old_records+new_records
            validate_prefix(all_records,source,task,arm)
            summary={'status':'complete' if code==0 and not breach and len(all_records)==len(source) else 'failed','exit_code':code,'memory_breach':breach,'n':len(all_records),'expected':len(source),'reused_original_cases':len(old_records),'new_cases':len(new_records),'peak_tree_rss_bytes':max(peak,meta['original_peak_rss_bytes']),'segment_peak_tree_rss_bytes':peak,'cap_bytes':cap,'exact_matches':sum(r['score']['exact_match'] for r in all_records),'generated_tokens':sum(r['generated_tokens'] for r in all_records),'seconds':sum(r['seconds'] for r in all_records),'case_files':[str(old/'cases.jsonl'),str(group/'segment/cases.jsonl')],'original_case_bytes_unchanged':not old_records or baseline.sha(old/'cases.jsonl')==meta['original_cases_sha256']}
            baseline.write(group/'summary.json',summary);meta['status']=summary['status'];baseline.write(recovery/'manifest.json',manifest)
            print(label,json.dumps(summary),flush=True)
            if summary['status']!='complete':raise RuntimeError('Incomplete continuation; stop subsequent arms')
        manifest['status']='complete'
    except BaseException as exc:
        manifest['status']='interrupted' if isinstance(exc,(InterruptedError,KeyboardInterrupt)) else 'failed'
        manifest['failure']=repr(exc)
        if child and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait()
        raise
    finally:baseline.write(recovery/'manifest.json',manifest)

if __name__=='__main__':main()
