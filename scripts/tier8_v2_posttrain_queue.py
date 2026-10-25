"""Frozen, fail-closed post-training sequence; no retries or implicit resumes.

Each subprocess is monitored as part of the complete controller process tree.
Raw outputs, logs and reports stay on the authorized SSD. No Git operations.
"""
import argparse
import hashlib
import json
import math
import os
import re
from pathlib import Path
import signal
import subprocess
import sys
import time

import psutil
from tier8_artifact_paths import artifact_path

ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'tier8_v2_adapter_convert.py','tier8_v2_adapter_proof.py','tier8_v2_critic_probe.py','tier8_v2_critic_compare.py','tier8_v2_run.py','tier8_v2_analyze.py','tier8_v2_unit_audit.py','tier8_external_recover.py'}


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def write(path,value):
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)

def check_inputs(plan):
    for path,expected in plan['input_sha256'].items():
        if sha(artifact_path(path))!=expected:raise ValueError('Frozen input changed: '+path)

def require_training(directory):
    root=artifact_path(directory);m=json.loads((root/'manifest.json').read_text());s=json.loads((root/'summary.json').read_text())
    validation=s.get('validation_teacher_forced_loss')
    if (m['purpose']!='critic' or m['profile']!='3b' or s['status']!='complete' or s['mode']!='train'
            or s['examples_processed']!=m['training_n'] or s['optimizer_updates']!=(m['training_n']+7)//8
            or s['changed_adapter_tensors']<=0 or not isinstance(validation,(int,float))
            or not math.isfinite(validation)):raise ValueError('Incomplete/invalid critic epoch')
    for name,digest in m['input_sha256'].items():
        if sha(artifact_path(name))!=digest:raise ValueError('Training input changed')
    for name,digest in s['adapter_files'].items():
        if Path(name).name!=name or sha(root/'adapter'/name)!=digest:raise ValueError('Trained adapter changed')
    return s

def natural_pair(left,right):
    roots=list(map(artifact_path,[left,right]));manifests=[json.loads((p/'manifest.json').read_text()) for p in roots]
    a,b=manifests
    for key in ['data_sha256','evaluation_source_sha256','code_sha256','cap_bytes','models']:
        if a[key]!=b[key]:raise ValueError('Natural pair differs: '+key)
    if a['adapter']['sha256']!=b['adapter']['sha256'] or a.get('verifier_adapter') is not None or not b.get('verifier_adapter'):raise ValueError('Unmatched actor/critic policies')
    rows=[[json.loads(s) for s in (p/'cases.jsonl').read_text().splitlines()] for p in roots]
    by_id=[{r['case_id']:r for r in rs} for rs in rows]
    if any(len(ids)!=len(rs) for ids,rs in zip(by_id,rows)) or set(by_id[0])!=set(by_id[1]):raise ValueError('Unmatched case IDs')
    for ident in by_id[0]:
        x,y=[rs[ident] for rs in by_id]
        if x['initial_plan']!=y['initial_plan'] or x['initial_answer']!=y['initial_answer']:raise ValueError('Critic comparison changed initial draft')
        prompts=lambda r:[s['prompt'] for s in r['stages'] if s['stage']=='verify_program']
        if len(prompts(x))!=1 or prompts(x)!=prompts(y):raise ValueError('Critic comparison changed verification input')
        if set(x['adapter_applications'])!={'drafter'} or set(y['adapter_applications'])!={'drafter','verifier'}:raise ValueError('Wrong role application record')
        for r in [x,y]:
            if not all(v['runtime_handle_initialized'] for v in r['adapter_applications'].values()):raise ValueError('Missing runtime adapter handle')
    return {'n':len(by_id[0]),'identical_initial_drafts':True,'identical_critic_prompts':True,'same_actor_adapter':True,'separate_critic_application_recorded':True}

def validate_job(job,cap):
    root=artifact_path(job['result']);kind=job['kind']
    if kind=='convert':
        m=json.loads((root/'manifest.json').read_text())
        if m['status']!='complete' or m['diagnostic_only'] or m['purpose']!='critic' or sha(artifact_path(m['file']))!=m['sha256']:raise ValueError('Invalid critic conversion')
        return {'adapter_sha256':m['sha256'],'tensor_count':m['tensor_count']}
    if kind in ['proof','natural']:
        s=json.loads((root/'summary.json').read_text())
        if s['status']!='complete' or s['exit_code']!=0 or s['peak_tree_rss_bytes']>cap or s['cap_bytes']!=cap:raise ValueError('Incomplete/memory-invalid result')
        if kind=='proof':
            p=json.loads((root/'proof.json').read_text())
            if not p['pass'] or p['adapter']['purpose']!='critic':raise ValueError('Critic application effect not proved')
        elif s['n']!=s['expected'] or s['n']!=job['expected']:raise ValueError('Natural case count differs')
        return s
    if kind=='probe':
        m=json.loads((root/'manifest.json').read_text())
        if m['status']!='complete' or m['cap_bytes']!=cap or set(m['profiles'])!={'3b'} or m['protocols']!=['binary']:raise ValueError('Invalid probe result')
        s=m['profiles']['3b']
        if s['status']!='complete' or s['exit_code']!=0 or s['peak_tree_rss_bytes']>cap or s['protocols']['binary']['n']!=job['expected']:raise ValueError('Invalid probe coverage/memory')
        return s
    if kind=='json':
        m=json.loads(root.read_text())
        if any(key not in m for key in job['required_keys']):raise ValueError('Analysis output incomplete')
        return {'file':str(root),'sha256':sha(root)}
    if kind=='external':
        m=json.loads((root/'manifest.json').read_text())
        if m['status']!='complete' or m['cap_bytes']!=cap:raise ValueError('External recovery incomplete')
        summaries={}
        for label,n in [('mortar-sas',90),('mortar-mas',90),('frames-sas',100),('frames-mas',100)]:
            s=json.loads((root/label/'summary.json').read_text())
            if s['status']!='complete' or s['n']!=n or s['peak_tree_rss_bytes']>cap or not s['original_case_bytes_unchanged']:raise ValueError('External arm incomplete/changed')
            summaries[label]=s
        return summaries
    raise ValueError('Unknown queue job kind')

def main():
    p=argparse.ArgumentParser();p.add_argument('--plan',required=True);args=p.parse_args();plan_path=artifact_path(args.plan);plan=json.loads(plan_path.read_text());root=plan_path.parent;plan_sha=sha(plan_path)
    import fcntl
    lock=(root/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    journal=root/'journal.jsonl'
    if journal.exists():raise ValueError('Existing queue journal; never restart implicitly')
    def record(state,**fields):
        item={'state':state,'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),**fields}
        with journal.open('a') as f:f.write(json.dumps(item)+'\n');f.flush();os.fsync(f.fileno())
        write(root/'state.json',item)
    child=None
    def interrupted(sig,frame):raise InterruptedError(f'Controller signal {sig}')
    signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
    try:
        check_inputs(plan);dep=plan['dependency']
        try:process=psutil.Process(dep['pid'])
        except psutil.NoSuchProcess:process=None
        if process:
            if process.create_time()!=dep['create_time'] or dep['out'] not in process.cmdline():raise ValueError('Dependency PID identity mismatch')
            record('waiting_for_training',verified_pid=dep['pid'],create_time=dep['create_time'],plan_sha256=plan_sha)
            while process.is_running():
                try:
                    if process.status()==psutil.STATUS_ZOMBIE:break
                    if process.create_time()!=dep['create_time']:raise ValueError('Dependency PID reused')
                    process.wait(timeout=10);break
                except psutil.TimeoutExpired:pass
                except psutil.NoSuchProcess:break
        training=require_training(dep['out']);record('training_complete',summary=training)
        for runtime,expected in plan.get('runtime_versions',{}).items():
            python=ROOT/('.venv/bin/python' if runtime=='cpu' else '.venv-training/bin/python')
            probe='import importlib.metadata as m,json,sys;print(json.dumps({k:m.version(k) for k in json.loads(sys.argv[1])}))'
            actual=json.loads(subprocess.check_output([str(python),'-c',probe,json.dumps(list(expected))],text=True,cwd=ROOT))
            if actual!=expected:raise ValueError('Runtime package versions changed')
        record('runtimes_verified')
        cap=plan['cap_bytes']
        if not 0<cap<=6400000000:raise ValueError('Invalid common memory cap')
        for job in plan['jobs']:
            if sha(plan_path)!=plan_sha:raise ValueError('Frozen plan changed')
            if not re.fullmatch('[a-z0-9_-]+',job['name']):raise ValueError('Unsafe job name')
            check_inputs(plan)
            if psutil.virtual_memory().available<cap+1250000000:raise MemoryError('Insufficient host headroom for common cap and launch overhead')
            if job.get('matched_natural_pair'):record('matched_natural_pair_validated',**natural_pair(*job['matched_natural_pair']))
            script=artifact_path(job['script'])
            if script.parent!=ROOT/'scripts' or script.name not in ALLOWED:raise ValueError('Queue script not allowed')
            if job['runtime'] not in ['cpu','training']:raise ValueError('Unknown runtime')
            python=ROOT/('.venv/bin/python' if job['runtime']=='cpu' else '.venv-training/bin/python')
            log=artifact_path(job['log']);result=artifact_path(job['result'])
            if log.exists() or result.exists():raise ValueError('Existing job result/log; refuse overwrite')
            if job['kind']=='json':result.parent.mkdir(parents=True,exist_ok=True)
            log.parent.mkdir(parents=True,exist_ok=True)
            command=[str(python),'-u',str(script),*job['args']]
            record('starting',job=job['name'],command=command)
            peak=0;breach=False
            with log.open('x') as stream:
                child=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stream,stderr=stream,start_new_session=True,close_fds=True)
                proc=psutil.Process(child.pid)
                with (root/(job['name']+'-memory.jsonl')).open('x') as memory:
                    while child.poll() is None:
                        try:rss=sum(q.memory_info().rss for q in [psutil.Process(),proc,*proc.children(recursive=True)] if q.is_running())
                        except psutil.NoSuchProcess:continue
                        available=psutil.virtual_memory().available;peak=max(peak,rss)
                        memory.write(json.dumps({'time':time.time(),'complete_queue_tree_rss_bytes':rss,'host_available_bytes':available})+'\n');memory.flush()
                        if rss>cap or available<1000000000:breach=True;os.killpg(child.pid,signal.SIGKILL);break
                        time.sleep(.2)
                code=child.wait();child=None
            record('subprocess_exited',job=job['name'],exit_code=code,full_tree_peak_bytes=peak,cap_bytes=cap,memory_breach=breach)
            if code!=0 or breach:raise RuntimeError('Job failed: '+job['name'])
            result_info=validate_job(job,cap);record('job_complete',job=job['name'],result=result_info,full_tree_peak_bytes=peak)
        record('complete',all_jobs_finished=True,novelty_established=False)
    except BaseException as exc:
        if child and child.poll() is None:
            os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
        record('interrupted' if isinstance(exc,(InterruptedError,KeyboardInterrupt)) else 'failed',error=repr(exc));raise

if __name__=='__main__':main()
