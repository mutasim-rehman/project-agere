"""Freeze broader FinQA development packets using IDs/report groups only.

Conservatively exclude cases declared in prior FinQA run manifests, including
failed runs, as well as persisted case IDs. No claim of pristine held-out data:
this is a public development source whose labels were already accessible.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil

from tier8_artifact_paths import artifact_path
from tier8_v2_demo_retrieval import report_group
from tier8_v2_finqa import packet

ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def select(rows,excluded_ids,excluded_groups,n):
    chosen=[];groups=set(excluded_groups)
    for row in rows:
        ident=row['id'];group=report_group(ident)
        if ident in excluded_ids or group in groups:continue
        chosen.append(row);groups.add(group)
        if len(chosen)==n:break
    if len(chosen)!=n:raise ValueError('Insufficient eligible distinct report groups')
    return chosen

def exposures(roots,source_ids):
    seen=set();files={};manifests=0
    for root in roots:
        if not root.exists():continue
        for path in sorted(root.rglob('manifest.json')):
            m=json.loads(path.read_text());cfg=m.get('config',{})
            if cfg.get('task')!='finqa':continue
            data=artifact_path(cfg['data']);expected=m.get('data_sha256')
            if expected is None or sha(data)!=expected:raise ValueError(f'Cannot audit historical declared input: {path}')
            limit=cfg['limit'];rows=[json.loads(s) for s in data.read_text().splitlines()][:limit]
            seen.update(r['id'] for r in rows if r['id'] in source_ids);files[str(path)]=sha(path);files[str(data)]=expected;manifests+=1
        for path in sorted(root.rglob('cases.jsonl')):
            text=path.read_text()
            if text and not text.endswith('\n'):raise ValueError(f'Incomplete case tail needs exposure audit: {path}')
            relevant=False
            for row in map(json.loads,text.splitlines()):
                ident=row.get('case_id',row.get('id'))
                if ident in source_ids:seen.add(ident);relevant=True
            if relevant:files[str(path)]=sha(path)
    return seen,files,manifests

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-id',required=True);p.add_argument('--n',type=int,default=100);a=p.parse_args()
    import re
    if a.n<=0 or not re.fullmatch('[a-zA-Z0-9_-]+',a.run_id):raise ValueError('Invalid selection size or ID')
    ssd=Path(os.environ['AGERE_SSD_ROOT']).resolve();out=artifact_path(ssd/'datasets/tier8_v2_finqa'/a.run_id)
    if out.exists():raise ValueError('Refuse overwrite')
    source=ROOT/'research/tier8_v2/external/finqa/dataset-dev.json';rows=json.loads(source.read_text());ids={r['id'] for r in rows}
    pin=json.loads((ROOT/'research/tier8_v2/evidence/finqa-development-manifest.json').read_text())
    if sha(source)!=pin['source_sha256'] or len(ids)!=len(rows):raise ValueError('Pinned development source differs or has duplicate IDs')
    seen,files,nmanifests=exposures([ROOT/'research/tier8_v2/runs',ssd/'runs'],ids)
    exposed_groups={report_group(i) for i in seen}
    training_paths=[ROOT/f'research/tier8_v2/data/finqa-cell-adaptation-{s}-02.jsonl' for s in ['train','validation']]
    training_groups={r['report_group'] for path in training_paths for r in map(json.loads,path.read_text().splitlines())}
    chosen=select(rows,seen,exposed_groups|training_groups,a.n)
    public=[packet(row) for row in chosen]
    out.mkdir(parents=True)
    path=out/'public.jsonl';path.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in public))
    shutil.copyfile(source,out/'source-dev.json')
    report={'status':'frozen_development_selection','n':len(chosen),'distinct_report_groups':len({report_group(r['id']) for r in chosen}),'source_split':'development','source_sha256':sha(source),'source_copy':str(out/'source-dev.json'),'public_file':str(path),'public_sha256':sha(path),'selected_ids':[r['id'] for r in chosen],'selected_report_groups':[report_group(r['id']) for r in chosen],'excluded_prior_declared_or_persisted_cases':len(seen),'excluded_prior_report_groups':len(exposed_groups),'audited_generation_manifests':nmanifests,'exposure_files_sha256':files,'training_source_sha256':{str(path.relative_to(ROOT)):sha(path) for path in training_paths},'selection':'first qualifying source record per distinct report group, source order; exclude all declared/persisted prior-case reports and prepared training/validation reports; never filter by answer/program/performance','retrieval':'unchanged non-oracle lexical packet(limit8); no gold units or supplied retrieval/model_input used','model_calls':0,'test_opened':False,'code_sha256':{str(path.relative_to(ROOT)):sha(path) for path in [Path(__file__),ROOT/'scripts/tier8_v2_finqa.py',ROOT/'scripts/tier8_v2_demo_retrieval.py']},'limits':'Broader development and new inference cases relative to audited sources, not pristine unseen labels or publication confirmation. Audit covers declared inputs and saved cases in named run roots; public pretraining contamination unassessed.'}
    (out/'selection.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['n','distinct_report_groups','excluded_prior_declared_or_persisted_cases','excluded_prior_report_groups','audited_generation_manifests','public_sha256']}),flush=True)

if __name__=='__main__':main()
