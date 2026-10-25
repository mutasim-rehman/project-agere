"""Freeze the critic post-training and original external recovery queue."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser();p.add_argument('--run-id',required=True);a=p.parse_args()
    import os,re
    if not re.fullmatch('[a-zA-Z0-9_-]+',a.run_id):raise ValueError('Unsafe run ID')
    ssd=Path(os.environ['AGERE_SSD_ROOT']).resolve();root=artifact_path(ssd/'runs/tier8_posttrain'/a.run_id)
    if root.exists():raise ValueError('Refuse overwrite')
    launch_path=ROOT/'research/tier8_v2/evidence/critic3b-training-launch-01.json';launch=json.loads(launch_path.read_text())
    training=artifact_path(launch['out']);converted=ssd/'runs/tier8_critic_training/critic3b-converted-01';proof=ssd/'runs/tier8_critic_training/critic3b-applied-proof-01'
    probe_source=ssd/'runs/tier8_critic_probe/critic_protocol_validation12_01'
    probe_plain=ssd/'runs/tier8_critic_probe/critic_binary_plain12_01';probe_adapted=ssd/'runs/tier8_critic_probe/critic_binary_adapted12_01'
    natural_plain=ssd/'runs/tier8_critic_qa/finqa-adapted-actor-plain3b-binary-dev24-01';natural_adapted=ssd/'runs/tier8_critic_qa/finqa-adapted-actor-trained3b-binary-dev24-01'
    external=ssd/'runs/tier8_external/external_baselines_20261025_recovery02'
    for path in [converted,proof,probe_plain,probe_adapted,natural_plain,natural_adapted,external]:
        if path.exists():raise ValueError('Existing planned output: '+str(path))
    root.mkdir(parents=True);(root/'inputs').mkdir()
    public=root/'inputs/public-dev24.jsonl';shutil.copyfile(ROOT/'research/tier8_v2/data/finqa-development-public.jsonl',public)
    source=ssd/'datasets/tier8_v2_finqa/dev_report100_01/source-dev.json'
    actor=ROOT/'research/tier8_v2/runs/adapter-3b-converted-02';weights=ssd/'weights/tier8_v2';dataset=ssd/'datasets/tier8_v2_critic/critic_binary_sft_02/examples.jsonl'
    jobs=[]
    def add(name,script,runtime,args,kind,result,**extra):
        jobs.append({'name':name,'script':'scripts/'+script,'runtime':runtime,'args':[str(x) for x in args],'kind':kind,'result':str(result),'log':str(root/'logs'/(name+'.log')),**extra})
    add('01_convert','tier8_v2_adapter_convert.py','training',['--run',training,'--out',converted],'convert',converted)
    add('02_application_proof','tier8_v2_adapter_proof.py','cpu',['--adapter',converted,'--arm','mas','--purpose','critic','--dataset',dataset,'--model-path',weights/'qwen2.5-3b-instruct-q4_k_m.gguf','--out',proof],'proof',proof)
    for name,out,adapt in [('03_probe_plain',probe_plain,False),('04_probe_adapted',probe_adapted,True)]:
        args=['--run-id',out.name,'--profile','3b','--protocol','binary','--inputs',probe_source]
        if adapt:args+=['--adapter',converted,'--application-proof',proof]
        add(name,'tier8_v2_critic_probe.py','cpu',args,'probe',out,expected=24)
    result=root/'reports/critic-paired.json'
    add('05_probe_comparison','tier8_v2_critic_compare.py','cpu',['--left',probe_plain,'--right',probe_adapted,'--out',result],'json',result,required_keys=['conditions','delta_gate_accuracy','report_cluster_bootstrap_95_interval'])
    common=['--task','finqa','--arm','mas','--repair','none','--data',public,'--evaluation-source',source,'--limit','24','--context','4096','--program-mode','reference','--unit-mode','question','--selector','none','--causal-mode','grammar','--catalog-style','compact','--residency','shared','--drafter-model','3b-q4','--verifier-model','3b','--critic-protocol','binary','--adapter',actor,'--weights-root',weights,'--demos','0','--analysis-tokens','0']
    for name,out,adapt in [('06_natural_plain',natural_plain,False),('07_natural_adapted',natural_adapted,True)]:
        args=common+['--out',out]
        if adapt:args+=['--verifier-adapter',converted]
        add(name,'tier8_v2_run.py','cpu',args,'natural',out,expected=24)
    result=root/'reports/natural24-paired.json'
    add('08_natural_comparison','tier8_v2_analyze.py','cpu',[natural_plain,natural_adapted],'json',result,required_keys=['source_validation','paired','left','right'],matched_natural_pair=[str(natural_plain),str(natural_adapted)])
    jobs[-1]['log']=str(result)
    result=root/'reports/natural24-unit-sensitivity.json'
    add('09_unit_sensitivity','tier8_v2_unit_audit.py','cpu',[natural_plain,natural_adapted],'json',result,required_keys=['metric_version','runs']);jobs[-1]['log']=str(result)
    add('10_external_recovery','tier8_external_recover.py','cpu',['--original','external_baselines_20261025_01','--recovery-id',external.name],'external',external)
    scripts=['scripts/tier8_v2_posttrain_queue.py','scripts/tier8_v2_posttrain_plan.py','scripts/tier8_v2_adapt.py','scripts/tier8_v2_adapter_convert.py','scripts/tier8_v2_adapter_runtime.py','scripts/tier8_v2_adapter_proof.py','scripts/tier8_v2_critic_probe.py','scripts/tier8_v2_critic_compare.py','scripts/tier8_v2_run.py','scripts/tier8_v2_financial_pipeline.py','scripts/tier8_v2_analyze.py','scripts/tier8_v2_unit_audit.py','scripts/tier8_external_eval.py','scripts/tier8_external_recover.py','scripts/completion_tokenization.py','scripts/evidence_contract.py','scripts/evidence_atoms.py','scripts/evidence_cells.py','scripts/evidence_calculator.py','scripts/program_graph.py','scripts/program_endpoints.py','scripts/program_influence.py','scripts/tier8_v2_demos.py','scripts/tier8_v2_demo_retrieval.py','scripts/tier8_v2_sketches.py','scripts/tier8_v2_candidate_model.py','scripts/tier8_v2_table_retrieval.py','scripts/tier8_artifact_paths.py','scripts/financial_review_protocol.py']
    files=[ROOT/s for s in scripts]+[launch_path,training/'manifest.json',public,source,probe_source/'manifest.json',probe_source/'public.jsonl',probe_source/'labels.jsonl',actor/'manifest.json',ROOT/'research/tier8_v2/evidence/candidate-model-3b.json',ROOT/'research/tier8_v2/evidence/models.json',ROOT/'research/tier8_v2/evidence/native-models.json',ROOT/'research/tier8_v2/evidence/finqa-development-manifest.json',ssd/'runs/tier8_external/external_baselines_20261025_01/manifest.json',ssd/'runs/tier8_external/external_baselines_20261025_01/mortar-sas/cases.jsonl']
    train_manifest=json.loads((training/'manifest.json').read_text());files+=[artifact_path(s) for s in train_manifest['input_sha256']]
    versions={}
    for runtime,packages in [('cpu',['llama-cpp-python','psutil']),('training',['torch','transformers','peft','bitsandbytes'])]:
        python=ROOT/('.venv/bin/python' if runtime=='cpu' else '.venv-training/bin/python')
        probe='import importlib.metadata as m,json,sys;print(json.dumps({k:m.version(k) for k in json.loads(sys.argv[1])}))'
        versions[runtime]=json.loads(subprocess.check_output([str(python),'-c',probe,json.dumps(packages)],text=True))
    plan={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'cap_bytes':6400000000,'dependency':{'pid':launch['pid'],'create_time':launch['create_time'],'out':str(training)},'runtime_versions':versions,'input_sha256':{str(path):sha(path) for path in set(files)},'jobs':jobs,'scope':'Known-method critic conversion/application/calibration and matched reused-dev24 delivery comparison, then recovery of original unadapted external baselines. No fresh report100 inference, SAS adaptation or novelty claim. Each failure stops later jobs; no retries/resumes.'}
    (root/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'plan':str(root/'plan.json'),'jobs':len(jobs),'frozen_inputs':len(plan['input_sha256'])},indent=2))

if __name__=='__main__':main()
