"""Freeze natural-report comparisons before matched continuation outcomes.

Produces commands and overlap evidence only. Does not launch model work, overwrite
the frozen discovery queue, or silently activate its deferred commands.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess

from tier8_artifact_paths import artifact_path
from tier8_v2_demo_retrieval import report_group
from tier8_v2_posttrain_queue import sha, write
from tier8_v2_natural_selection import public_packet

ROOT = Path(__file__).resolve().parents[1]


def financial_command(arm, public, source, out, actor, critic, weights, n, analysis=0, demos=0):
    if arm not in ('sas', 'mas') or (arm == 'mas') != bool(critic):
        raise ValueError('MAS requires a critic; SAS uses its own checkpoint')
    command = [ROOT / '.venv/bin/python', ROOT / 'scripts/tier8_v2_natural_run.py', '--arm', arm,
        '--task', 'finqa', '--repair', 'full', '--data', public, '--evaluation-source', source,
        '--limit', str(n), '--context', '4096', '--program-mode', 'reference',
        '--unit-mode', 'question', '--selector', 'none', '--causal-mode', 'grammar',
        '--catalog-style', 'compact', '--planner', 'direct', '--critic-protocol', 'binary',
        '--residency', 'shared', '--weights-root', weights, '--demos', str(demos),
        '--analysis-tokens', str(analysis), '--adapter', actor, '--out', out]
    if arm == 'mas':
        command += ['--drafter-model', '3b-q4', '--verifier-model', '3b', '--verifier-adapter', critic]
    return list(map(str, command))


def prepare(out):
    if out.exists():
        raise ValueError('Require a new study directory')
    ssd = artifact_path(Path(os.environ['AGERE_SSD_ROOT']))
    natural = ssd / 'datasets/tier8_v2_natural/natural_reports62_01'
    selection = json.loads((natural / 'selection.json').read_text())
    source = artifact_path(selection['source_copy'])
    if sha(source) != selection['source_sha256']:
        raise ValueError('Natural source changed')
    original = {r['id']: r for r in json.loads(source.read_text())}
    datasets = [ssd / 'datasets' / value for value in (
        'tier8_v2_sas/sas_joint_extended_01', 'tier8_v2_critic/critic_extended_sft_02',
        'tier8_v2_critic/critic_binary_sft_02', 'tier8_v2_continuation/matched_01/control_sas',
        'tier8_v2_continuation/matched_01/crossed_sas', 'tier8_v2_continuation/matched_01/control_mas_critic',
        'tier8_v2_continuation/matched_01/crossed_mas_critic', 'tier8_v2_continuation/matched_01/common_mas_actor')]
    datasets += [ROOT / 'research/tier8_v2/evidence/deployment-sft-1024-02.json']
    files = [Path(__file__), natural / 'selection.json', source]
    exposures = {}
    for name in ('finqa-training-demo-bank.json', 'finqa-training-demos.json'):
        path = ROOT / 'research/tier8_v2/data' / name
        info = json.loads(path.read_text())
        examples = info['examples'] if 'bank' in name else info['examples'][:2]
        exposures[str(path)] = {report_group(r['source_id']) for r in examples}
        files.append(path)
    for path in datasets:
        manifest = path if path.is_file() else path / 'manifest.json'
        info = json.loads(manifest.read_text()); data = artifact_path(info['output_file'])
        if sha(data) != info['output_sha256']:
            raise ValueError('Fitting corpus changed')
        rows = [json.loads(s) for s in data.read_text().splitlines()]
        exposures[str(manifest)] = {r['report_group'] for r in rows}
        files += [manifest, data]
    overlap = {}
    for partition in ('model_selection', 'diagnostic_audit'):
        part = selection['partitions'][partition]; public = artifact_path(part['public_file'])
        packets = [json.loads(s) for s in public.read_text().splitlines()]
        ids = [r['id'] for r in packets]; groups = {report_group(i) for i in ids}
        if sha(public) != part['sha256'] or len(ids) != len(set(ids)) or sorted(ids) != sorted(part['ids']):
            raise ValueError('Natural packet selection changed')
        if any(packet != public_packet(original[packet['id']]) for packet in packets):
            raise ValueError('Natural packets differ from question-only source retrieval')
        overlap[partition] = {name: sorted(groups & seen) for name, seen in exposures.items()}
        if any(overlap[partition].values()):
            raise ValueError('Natural reports overlap fitting/validation corpora')
        files.append(public)
    runs = ssd / 'runs/tier8_method_qa'
    trained = ssd / 'runs/tier8_matched_continuation'
    sas_base = ssd / 'runs/tier8_sas_training/sas7b-joint-converted-03'
    actor_base = ROOT / 'research/tier8_v2/runs/adapter-3b-converted-02'
    critic_base = ssd / 'runs/tier8_critic_training/critic3b-extended-converted-01'
    common_actor = trained / 'common-actor-converted-01'
    policies = [('baseline_sas', 'sas', sas_base, None), ('baseline_mas', 'mas', actor_base, critic_base)]
    for arm in ('sas', 'mas'):
        for condition in ('control', 'crossed'):
            actor = trained / f'{condition}-sas-converted-01' if arm == 'sas' else common_actor
            critic = trained / f'{condition}-critic-converted-01' if arm == 'mas' else None
            policies.append((condition + '_' + arm, arm, actor, critic))
    jobs = []
    for partition in ('model_selection', 'diagnostic_audit'):
        part = selection['partitions'][partition]
        # Both matched conditions, even if only one looks promising on selection.
        for name, arm, actor, critic in policies:
            if partition == 'diagnostic_audit' and name.startswith('baseline'):
                continue
            result = runs / f'{partition}-{name}-full-01'
            jobs.append({'name': partition + '-' + name, 'partition': partition,
                'condition': name, 'arm': arm, 'adapter': str(actor),
                'critic_adapter': str(critic) if critic else None, 'result': str(result),
                'expected': part['n'], 'cap_bytes': 6400000000,
                'command': financial_command(arm, part['public_file'], source, result,
                    actor, critic, ssd / 'weights/tier8_v2', part['n'])})
    secondary = []
    part = selection['partitions']['model_selection']
    for name, arm, actor, critic in policies:
        if arm != 'sas':
            continue
        result = runs / f'model_selection-{name}-analysis128-demos2-full-01'
        secondary.append({'name': name + '-analysis128-demos2', 'result': str(result),
            'expected': part['n'], 'command': financial_command('sas', part['public_file'],
                source, result, actor, None, ssd / 'weights/tier8_v2', part['n'], 128, 2)})
    files += list((ROOT / 'scripts').glob('*.py'))
    plan = {'kind': 'matched_continuation_natural_evaluation', 'status': 'prepared_not_launched',
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'input_sha256': {str(p): sha(p) for p in files}, 'natural_report_overlap': overlap,
        'jobs': jobs, 'secondary_sas_prompt_jobs': secondary,
        'launch_gate': 'Frozen discovery complete; continuation ceiling rule permits training; each fitted/full adapter completes conversion and measured native application proof. Serial NN only. Do not launch nonexistent/partial adapters.',
        'primary': 'Within architecture, crossed minus current-mutation control on correct deliveries and wrong deliveries, both reported-unit and raw-execution metrics; withholding separately. Whole-policy effects, not necessarily pure-gate effects.',
        'policy': 'Identical reference/compact/question-unit grammar, direct0-analysis0-demos, binary review, one full regeneration after rejection. Generated ledger2048; per-call768/192/768/192; actual prefill/decode/time/RSS reported. Existing full-retry policy, no new mechanism.',
        'ablation': 'Replay initial draft/review prefix as no-repair outcome; exclude repair work from prefix costs. Replay ungated executable initial draft separately. These are measured trajectory prefixes, not newly generated counterfactual trajectories.',
        'adoption': 'Selection52/15reports is exploratory. A candidate is promising only if correct deliveries do not fall and wrong deliveries do not rise under BOTH metrics, with at least one strict gain. Evaluate BOTH matched policies for BOTH architectures on reserved audit49/15reports regardless of selection outcome. Conflicting metrics or tradeoffs do not establish an unqualified improvement. Report-cluster intervals; no tuned scalar error penalty.',
        'strong_baseline': 'Baseline full adapters reported too. SAS analysis128+2fixed-training-demos is a prespecified secondary prompt check for all3 SAS policies, not selectively the winner. If omitted for time, disclose unmeasured prompt optimality; do not claim globally best SAS.',
        'limits': 'Public training-source held-out reports; not pretraining-clean confirmation. No QA or novelty result yet. New methods remain forbidden after tier freeze.100-report public dev remains deferred, with original SAS-only model-flag error documented; regenerate its commands before use.'}
    out.mkdir(parents=True); write(out / 'plan.json', plan)
    print(json.dumps({'plan': str(out / 'plan.json'), 'sha256': sha(out / 'plan.json'),
                      'primary_jobs': len(jobs), 'secondary_jobs': len(secondary), 'model_calls': 0}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--out', required=True)
    prepare(artifact_path(parser.parse_args().out))
