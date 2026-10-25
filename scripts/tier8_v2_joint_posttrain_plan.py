"""Prepare a frozen serial8GB baseline continuation; never launch model work."""
import argparse
import json
import os
from pathlib import Path
import subprocess

import psutil
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha, write

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dependency-launch', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    launch_path, out = map(artifact_path, [args.dependency_launch, args.out])
    if out.exists():
        raise ValueError('Refuse existing queue output')
    launch = json.loads(launch_path.read_text())
    dependency_plan = artifact_path(launch['plan'])
    if sha(dependency_plan) != launch['plan_sha256']:
        raise ValueError('Dependency plan differs')
    process = psutil.Process(launch['pid'])
    if process.create_time() != launch['create_time'] or str(dependency_plan) not in process.cmdline():
        raise ValueError('Require actual live SAS controller identity')
    dependency = json.loads(dependency_plan.read_text())
    if dependency['mode'] != 'train' or dependency['training_n'] != 3801:
        raise ValueError('Require matched full SAS adaptation')
    ssd = artifact_path(os.environ['AGERE_SSD_ROOT'])
    cpu, training = str(ROOT / '.venv/bin/python'), str(ROOT / '.venv-training/bin/python')
    script = lambda name: str(ROOT / 'scripts' / name)
    critic_data = ssd / 'datasets/tier8_v2_critic/critic_extended_sft_02'
    joint_data = ssd / 'datasets/tier8_v2_sas/sas_joint_extended_01'
    old_critic_data = ssd / 'datasets/tier8_v2_critic/critic_binary_sft_02'
    sas_run = dependency_plan.parent / 'train'
    sas_conversion = ssd / 'runs/tier8_sas_training/sas7b-joint-converted-03'
    sas_proof = ssd / 'runs/tier8_sas_training/sas7b-joint-last-logit-proof-03'
    critic_run = ssd / 'runs/tier8_critic_training/critic3b-extended-train-01'
    critic_conversion = ssd / 'runs/tier8_critic_training/critic3b-extended-converted-01'
    critic_proof = ssd / 'runs/tier8_critic_training/critic3b-extended-applied-proof-01'
    old_conversion = ssd / 'runs/tier8_critic_training/critic3b-converted-01'
    old_proof = ssd / 'runs/tier8_critic_training/critic3b-applied-proof-01'
    actor = ROOT / 'research/tier8_v2/runs/adapter-3b-converted-02'
    packet = ssd / 'datasets/tier8_v2_finqa/dev_report100_01'
    weights = ssd / 'weights/tier8_v2'
    old_qa = ssd / 'runs/tier8_critic_qa/finqa-adapted-actor-original-critic-report100-01'
    new_qa = ssd / 'runs/tier8_critic_qa/finqa-adapted-actor-extended-critic-report100-01'
    sas_qa = ssd / 'runs/tier8_sas_qa/finqa-joint-sas-direct-report100-01'
    sas_reason = ssd / 'runs/tier8_sas_qa/finqa-joint-sas-analysis128-demos2-report100-01'
    jobs = []
    def job(name, kind, command, result, **fields):
        jobs.append({'name': name, 'kind': kind, 'command': list(map(str, command)),
                     'result': str(result), 'cap_bytes': 10500000000 if kind == 'training' else 6400000000, **fields})
    job('convert-sas', 'sas_convert', [training, script('tier8_v2_adapter_convert.py'), '--run', sas_run, '--out', sas_conversion], sas_conversion)
    job('prove-sas-last-logit', 'sas_proof', [cpu, script('tier8_v2_last_logit_proof.py'), '--arm', 'sas', '--adapter', sas_conversion,
        '--dataset', joint_data / 'examples.jsonl', '--model-path', weights / 'qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf', '--out', sas_proof], sas_proof)
    job('train-extended-critic', 'training', [training, script('tier8_v2_adapt.py'), '--profile', '3b', '--mode', 'train', '--purpose', 'critic',
        '--dataset-manifest', critic_data / 'manifest.json', '--parity-manifest', critic_data / 'parity.json',
        '--training-base-manifest', old_critic_data / 'training-base-3b.json', '--out', critic_run], critic_run)
    job('convert-extended-critic', 'convert', [training, script('tier8_v2_adapter_convert.py'), '--run', critic_run, '--out', critic_conversion], critic_conversion)
    job('prove-extended-critic', 'proof', [cpu, script('tier8_v2_adapter_proof.py'), '--arm', 'mas', '--purpose', 'critic', '--adapter', critic_conversion,
        '--dataset', critic_data / 'examples.jsonl', '--model-path', weights / 'qwen2.5-3b-instruct-q4_k_m.gguf', '--out', critic_proof], critic_proof)
    common = ['--task', 'finqa', '--repair', 'none', '--data', packet / 'public.jsonl', '--evaluation-source', packet / 'source-dev.json',
              '--limit', '100', '--context', '4096', '--program-mode', 'reference', '--unit-mode', 'question', '--selector', 'none',
              '--causal-mode', 'grammar', '--catalog-style', 'compact', '--planner', 'direct', '--critic-protocol', 'binary',
              '--drafter-model', '3b-q4', '--verifier-model', '3b', '--residency', 'shared', '--weights-root', weights]
    for name, conversion, qa in [('original', old_conversion, old_qa), ('extended', critic_conversion, new_qa)]:
        job('mas-' + name + '-report100', 'natural', [cpu, script('tier8_v2_run.py'), '--arm', 'mas', *common,
            '--demos', '0', '--analysis-tokens', '0', '--adapter', actor, '--verifier-adapter', conversion, '--out', qa], qa, expected=100)
    report = out / 'critic-delivery-paired.json'
    job('critic-delivery-paired', 'json', [cpu, script('tier8_v2_delivery_analyze.py'), '--comparison-kind', 'trained-variants',
        '--left', old_qa, '--right', new_qa, '--left-proof', old_proof, '--right-proof', critic_proof,
        '--left-label', 'original_trained', '--right-label', 'extended_trained', '--out', report], report,
        required_keys=['metrics', 'matching_guard', 'input_sha256'])
    for name, qa, demos, analysis in [('direct', sas_qa, '0', '0'), ('analysis128-demos2', sas_reason, '2', '128')]:
        job('sas-' + name + '-report100', 'natural', [cpu, script('tier8_v2_run.py'), '--arm', 'sas', *common,
            '--demos', demos, '--analysis-tokens', analysis, '--adapter', sas_conversion, '--out', qa], qa, expected=100)
    for item in jobs:
        if artifact_path(item['result']).exists():
            raise ValueError('Planned result exists: ' + item['result'])
    files = list((ROOT / 'scripts').glob('*.py')) + [launch_path, dependency_plan,
        packet / 'public.jsonl', packet / 'source-dev.json', packet / 'selection.json',
        critic_data / 'manifest.json', critic_data / 'parity.json', critic_data / 'examples.jsonl',
        joint_data / 'manifest.json', joint_data / 'parity.json', joint_data / 'examples.jsonl',
        old_critic_data / 'training-base-3b.json', actor / 'manifest.json', old_conversion / 'manifest.json',
        old_proof / 'proof.json', old_proof / 'summary.json']
    files += list((ROOT / 'research/tier8_v2/evidence').glob('*models.json'))
    files += [ROOT / 'research/tier8_v2/evidence/candidate-model-3b.json']
    versions = {}
    for name, python, packages in [('cpu', cpu, ['llama-cpp-python', 'numpy', 'psutil']),
        ('training', training, ['torch', 'transformers', 'peft', 'bitsandbytes', 'accelerate', 'tokenizers', 'safetensors'])]:
        code = 'import importlib.metadata as m,json,sys;print(json.dumps({k:m.version(k) for k in json.loads(sys.argv[1])}))'
        versions[name] = json.loads(subprocess.check_output([python, '-c', code, json.dumps(packages)], text=True, cwd=ROOT))
    out.mkdir(parents=True)
    plan = {'kind': 'joint8gb_serial_posttrain', 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            'dependency': {k: launch[k] for k in ('pid', 'create_time', 'plan', 'plan_sha256')},
            'runtime_versions': versions, 'input_sha256': {str(p): sha(p) for p in files}, 'jobs': jobs,
            'scope': 'Baseline strengthening and exploratory100-report validation. No repair-method novelty established. Serial NN work only; no implicit restart or higher-tier changes.',
            'evaluation_limits': 'Public development100, selected after reused24 diagnosis; not untouched confirmation. SAS direct and analysis+demos are distinct policies, both reported. No SAS/MAS causal architecture claim from unequal parameterization or optimizer exposure.'}
    write(out / 'plan.json', plan)
    print(json.dumps({'plan': str(out / 'plan.json'), 'sha256': sha(out / 'plan.json'), 'jobs': len(jobs)}))


if __name__ == '__main__':
    main()
