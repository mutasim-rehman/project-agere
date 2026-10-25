"""SSD-only external baseline evaluation. Outputs never enter git.

MortarBench typed exact match is an exploratory local metric, not an official
benchmark implementation. FRAMES is the documented closed-book control.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from completion_tokenization import completion_tokens

ROOT = Path(__file__).resolve().parents[1]
SPECS = {'sas': [('sas', '7b', 'q4_k_m')],
         'mas': [('extractor', '0.5b', 'f16'), ('drafter', '1.5b', 'f16'), ('verifier', '0.5b', 'f16')]}
DATA = {'mortar': 'datasets/external/MortarBench/ab3421d6b1a9f0cedbb9f98d34a4e1eb4473532f/data/questions.jsonl',
        'frames': 'datasets/external/FRAMES/58d9fb6330f3ab1316d1eca12e5e8ef23dcc22ef/frames_100.jsonl'}

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''): h.update(b)
    return h.hexdigest()

def write(p, obj):
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2) + '\n'); tmp.replace(p)

def append(p, obj):
    with p.open('a') as f:
        f.write(json.dumps(obj) + '\n'); f.flush(); os.fsync(f.fileno())

def words(s): return re.findall(r'[a-z0-9]+', s.lower())

def flatten(value, prefix):
    out = []
    if isinstance(value, dict):
        scalar = {k:v for k,v in value.items() if not isinstance(v, (dict,list))}
        if scalar: out.append(prefix + ' ' + json.dumps(scalar, separators=(',', ':')))
        for k,v in value.items():
            if isinstance(v, (dict,list)): out += flatten(v, prefix + '/' + k)
    elif isinstance(value, list):
        for i,v in enumerate(value): out += flatten(v, prefix + '/' + str(i))
    else: out.append(prefix + ': ' + str(value))
    return out

def source_lines(row):
    lines = []
    for field in ('bank_statement','ulad_du'):
        text = row.get(field, '')
        if not text: continue
        if isinstance(text, (dict,list)): lines += flatten(text, field); continue
        try: lines += flatten(json.loads(text), field); continue
        except (ValueError,TypeError): pass
        try:
            def walk(e, path):
                path += '/' + e.tag.split('}')[-1]
                if e.text and e.text.strip(): lines.append(path + ': ' + e.text.strip())
                for c in e: walk(c,path)
            walk(ET.fromstring(text), field)
        except ET.ParseError:
            lines += [field + ': ' + s for s in text.splitlines() if s.strip()]
    # Break long records without silently dropping any source text.
    return [s[i:i+600] for s in lines for i in range(0,len(s),600)]

def packet(row, tokenizer):
    lines = source_lines(row); query = Counter(words(row['question']))
    counts = [Counter(words(s)) for s in lines]
    df = Counter(w for c in counts for w in c)
    def score(i):
        return sum(min(counts[i][w],2)*(len(lines)+1)/(df[w]+1) for w in query)/max(1,sum(counts[i].values()))**.5
    order = sorted(range(len(lines)), key=lambda i:(-score(i),i))
    selected = []; used = 0
    for i in order:
        rendered = f'S{i}: {lines[i]}'
        cost = len(tokenizer.tokenize((rendered+'\n').encode(), add_bos=False))
        if used+cost <= 1700: selected.append((i,rendered)); used += cost
    return {'question':row['question'], 'answer_type':row['answer_type'],
            'sources':[s for _,s in sorted(selected)], 'source_units_total':len(lines),
            'selected_source_ids':[i for i,_ in sorted(selected)],
            'retrieval':'question-only lexical IDF, 1700 token ceiling, canonical 0.5B tokenizer'}

def parse(text):
    try: return json.loads(text)
    except ValueError: return None

def normalize(value, kind):
    if kind == 'boolean':
        if isinstance(value,bool): return value
        s = str(value).strip().lower()
        return {'true':True,'yes':True,'false':False,'no':False}.get(s, ('invalid',s))
    if isinstance(value, list): items = [str(v).strip() for v in value]
    else:
        s = str(value).strip()
        if s.lower() in ('none','[]','null','n/a',''): return []
        decoded = parse(s)
        items = [str(v).strip() for v in decoded] if isinstance(decoded,list) else re.split(r'[,;\n]+',s)
    return sorted(set(s.strip(" \t\r\n'\"") for s in items if s.strip()))

def score(answer, row, task):
    if task == 'frames':
        # Preserve original strict metric, add clearly separate normalization.
        strict = str(answer).strip().lower() == row['answer'].strip().lower()
        norm = lambda s: ' '.join(re.findall(r'\w+',str(s).lower()))
        return {'exact_match':strict,'punctuation_normalized_match':norm(answer)==norm(row['answer'])}
    pred = answer.get('answer') if isinstance(answer,dict) and 'answer' in answer else {'invalid':True}
    return {'exact_match':normalize(pred,row['answer_type']) == normalize(row['answer'],row['answer_type']),
            'valid_answer_json': isinstance(answer,dict) and 'answer' in answer,
            'answer_type':row['answer_type']}

def worker(args, ssd, out):
    from llama_cpp import Llama, LlamaGrammar
    models = {}
    for role,size,kind in SPECS[args.arm]:
        models[role] = Llama(model_path=str(ssd/f'weights/gguf/qwen2.5-{size}-instruct-{kind}.gguf'),
            n_ctx=4096,n_threads=8,n_threads_batch=8,n_batch=64,n_ubatch=64,
            n_gpu_layers=0,use_mmap=False,seed=42,verbose=False)
        print('loaded',role,flush=True)
    rows = [json.loads(s) for s in (ssd/DATA[args.task]).read_text().splitlines()]
    packets = [json.loads(s) for s in (out.parent/f'{args.task}-packets.jsonl').read_text().splitlines()]
    schema = {'type':'object','properties':{'answer':{'type':'boolean'} if args.task=='mortar' else {'type':'string'}},'required':['answer'],'additionalProperties':False}
    def call(role, content, limit, stages, budget, structured=False, kind=None):
        model = models[role]; model.reset()
        prompt = '<|im_start|>system\nYou analyze evidence for a human reviewer. Follow the requested output format.<|im_end|>\n<|im_start|>user\n'+content+'<|im_end|>\n<|im_start|>assistant\n'
        n = len(completion_tokens(model,prompt)); allowance = min(limit,2048-budget[0],4096-n-8)
        if allowance <= 0: raise ValueError('Context/budget exhausted; no silent truncation')
        options = {}
        if structured:
            spec = json.loads(json.dumps(schema))
            if kind != 'boolean' and args.task=='mortar': spec['properties']['answer'] = {'type':'array','items':{'type':'string'}}
            options['grammar'] = LlamaGrammar.from_json_schema(json.dumps(spec),verbose=False)
        start = time.monotonic()
        response = model.create_completion(prompt,max_tokens=allowance,temperature=0,top_k=1,seed=42,repeat_penalty=1,stop=['<|im_end|>'],**options)
        if response['usage']['prompt_tokens'] != n: raise ValueError('Prompt accounting mismatch')
        choice = response['choices'][0]; budget[0] += response['usage']['completion_tokens']
        stages.append({'role':role,'prompt':content,'response':choice['text'],'usage':response['usage'],'finish_reason':choice['finish_reason'],'seconds':time.monotonic()-start})
        return choice['text']
    for row,p in zip(rows,packets):
        stages = []; budget = [0]; start = time.monotonic()
        public = json.dumps(p)
        request = ('Answer the question. Return JSON with one key answer: a boolean for boolean questions, otherwise an array of exact transaction/account IDs. Use [] if none. Sources are retrieved excerpts; missing evidence may prevent reliable answers.' if args.task=='mortar' else 'Answer the question with the shortest factual phrase only. No explanation.')
        base = public+'\n'+request
        if args.arm == 'sas':
            reasoning = call('sas',base+'\nFirst reason briefly using the available evidence.',128,stages,budget)
            answer = call('sas',base+'\nAnalysis: '+reasoning+'\nNow give the final answer.',768,stages,budget,args.task=='mortar',p.get('answer_type'))
        else:
            extraction = call('extractor',base+'\nIdentify relevant facts and uncertainties. Do not answer yet.',256,stages,budget)
            draft = call('drafter',base+'\nFallible extraction: '+extraction+'\nGive a candidate answer and concise reasoning.',512,stages,budget)
            critique = call('verifier',base+'\nCandidate: '+draft+'\nCheck this candidate against sources, or flag factual uncertainties for a closed-book question.',256,stages,budget)
            answer = call('drafter',base+'\nCandidate: '+draft+'\nFallible review: '+critique+'\nGive the final answer.',768,stages,budget,args.task=='mortar',p.get('answer_type'))
        evaluated = parse(answer) if args.task=='mortar' else answer
        record = {'id':row.get('question_id',row.get('id')),'score':score(evaluated,row,args.task),'prediction':evaluated,'gold':row['answer'],'stages':stages,'generated_tokens':budget[0],'seconds':time.monotonic()-start}
        append(out/'cases.jsonl',record)
        print(json.dumps({k:record[k] for k in ('id','score','generated_tokens','seconds')}),flush=True)
    for m in models.values(): m.close()

def main():
    p = argparse.ArgumentParser(); p.add_argument('--run-id',required=True); p.add_argument('--worker',action='store_true'); p.add_argument('--task',choices=DATA);p.add_argument('--arm',choices=SPECS)
    args = p.parse_args()
    ssd = Path(os.environ['AGERE_SSD_ROOT']).resolve()
    if not ssd.is_dir() or ssd == ROOT: raise ValueError('Expected mounted external SSD')
    if not re.fullmatch(r'[a-zA-Z0-9_-]+',args.run_id): raise ValueError('Unsafe run ID')
    root = ssd/'runs/tier8_external'/args.run_id
    if args.worker: worker(args,ssd,root/f'{args.task}-{args.arm}'); return
    import psutil
    # A flock prevents duplicate launches of this runner; also reject known model workloads.
    import fcntl
    lock = (ssd/'runs/tier8_external.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    for process in psutil.process_iter(['pid','cmdline']):
        if process.pid == os.getpid(): continue
        cmd = process.info['cmdline'] or []
        if any(Path(a).name in ('tier8_v2_run.py','tier8_v2_adapt.py','tier8_study.py','phase3.py','eval_checkpoints.py') for a in cmd): raise RuntimeError('Another model workload is live')
    root.mkdir(parents=True,exist_ok=False)
    cap = min(6400000000,psutil.virtual_memory().available-1000000000)
    if cap < 5300000000: raise MemoryError('Insufficient memory for the fixed shared cap')
    artifacts = json.loads((ssd/'phase2/manifests/gguf_artifacts.json').read_text())['artifacts']
    selected = [a for a in artifacts if a['path'] in {f'weights/gguf/qwen2.5-{size}-instruct-{kind}.gguf' for specs in SPECS.values() for _,size,kind in specs}]
    if len(selected)!=3: raise ValueError('Missing model provenance')
    frozen_datasets = {}
    for line in (ROOT/'manifests/test.sha256').read_text().splitlines():
        digest, name = line.split(maxsplit=1); frozen_datasets[name.strip()] = digest
    for name in DATA.values():
        if frozen_datasets.get(name) != sha(ssd/name): raise ValueError('Dataset differs from committed frozen manifest: '+name)
    manifest = {'status':'preflight','cap_bytes':cap,'source_sha256':sha(Path(__file__)),'tokenization_sha256':sha(ROOT/'scripts/completion_tokenization.py'),'models':selected,'datasets':{k:{'path':v,'sha256':sha(ssd/v)} for k,v in DATA.items()},'context':4096,'output_token_ceiling':2048,'seed':42,'temperature':0,'threads':8,'mode':'resident distinct MAS instances','weights_verified':False,'note':'External exploratory baselines, no adapter; MortarBench local typed exact metric, FRAMES closed book; simulated 8GB tier.'}
    write(root/'manifest.json',manifest)
    for a in selected:
        print('verifying',a['path'],flush=True)
        if (ssd/a['path']).stat().st_size != a['size_bytes'] or sha(ssd/a['path'])!=a['sha256']: raise ValueError('Model checksum mismatch')
    manifest['weights_verified']=True
    from llama_cpp import Llama
    tok = Llama(model_path=str(ssd/'weights/gguf/qwen2.5-0.5b-instruct-f16.gguf'),vocab_only=True,verbose=False)
    for task,path in DATA.items():
        rows = [json.loads(s) for s in (ssd/path).read_text().splitlines()]
        packets = [packet(r,tok) if task=='mortar' else {'question':r['question'],'mode':'closed_book'} for r in rows]
        target = root/f'{task}-packets.jsonl'
        for row in packets: append(target,row)
        manifest['datasets'][task].update({'n':len(rows),'packet_sha256':sha(target)})
    tok.close(); manifest['status']='running'; write(root/'manifest.json',manifest)
    for task in DATA:
        for arm in SPECS:
            if sha(Path(__file__))!=manifest['source_sha256']: raise ValueError('Frozen runner changed')
            if sha(ssd/DATA[task])!=manifest['datasets'][task]['sha256'] or sha(root/f'{task}-packets.jsonl')!=manifest['datasets'][task]['packet_sha256']: raise ValueError('Frozen dataset/packet changed')
            out = root/f'{task}-{arm}'; out.mkdir()
            with (out/'worker.log').open('x') as log:
                child = subprocess.Popen([sys.executable,'-u',str(Path(__file__)),'--run-id',args.run_id,'--worker','--task',task,'--arm',arm],stdout=log,stderr=log)
                proc = psutil.Process(child.pid); peak = 0; breached=False
                while child.poll() is None:
                    try: rss = sum(x.memory_info().rss for x in [psutil.Process(),proc,*proc.children(recursive=True)] if x.is_running())
                    except psutil.NoSuchProcess: continue
                    peak=max(peak,rss)
                    append(out/'memory.jsonl',{'time':time.time(),'tree_rss_bytes':rss,'host_available_bytes':psutil.virtual_memory().available})
                    if rss > cap or psutil.virtual_memory().available < 1000000000:
                        breached=True
                        for x in proc.children(recursive=True): x.kill()
                        child.kill(); break
                    time.sleep(.2)
                code = child.wait()
            rows = [json.loads(s) for s in (out/'cases.jsonl').read_text().splitlines()] if (out/'cases.jsonl').exists() else []
            summary={'status':'complete' if code==0 and not breached and len(rows)==manifest['datasets'][task]['n'] else 'failed','exit_code':code,'memory_breach':breached,'n':len(rows),'expected':manifest['datasets'][task]['n'],'peak_tree_rss_bytes':peak,'cap_bytes':cap,'exact_matches':sum(r['score']['exact_match'] for r in rows),'generated_tokens':sum(r['generated_tokens'] for r in rows),'seconds':sum(r['seconds'] for r in rows)}
            write(out/'summary.json',summary);print(task,arm,json.dumps(summary),flush=True)
            if summary['status']!='complete':
                manifest['status']='failed';write(root/'manifest.json',manifest);raise RuntimeError(f'{task}-{arm} failed; subsequent runs not started')
    manifest['status']='complete';write(root/'manifest.json',manifest)

if __name__=='__main__': main()
