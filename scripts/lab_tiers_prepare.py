"""Seal offline lab inputs and a prospective higher-tier inference protocol.

Selection uses IDs/report membership only. No generation, training, downloads,
or changes to the running 8 GB study. New source/catalog prototypes are excluded.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from tier8_v2_finqa import packet

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def group(identifier):
    return identifier.rsplit('/', 1)[0]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(value, indent=2) + '\n')


def prepare(ssd):
    out = ssd / 'datasets/lab_tiers/finance_reports_v1'
    if out.exists():
        raise ValueError('Refuse sealed dataset overwrite')
    source = ssd / 'datasets/tier8_v2_finqa/dev_report100_01/source-dev.json'
    prior = ssd / 'datasets/tier8_v2_finqa/dev_report100_01/selection.json'
    old = json.loads(prior.read_text())
    if sha(source) != old['source_sha256']:
        raise ValueError('FinQA source differs from its existing pin')
    rows = json.loads(source.read_text())
    exclusions = set(old['selected_report_groups'])
    exposures = {str(prior.relative_to(ssd)): sha(prior)}
    development = ROOT / 'research/tier8_v2/data/finqa-development-public.jsonl'
    prior_groups = {group(json.loads(s)['id']) for s in development.read_text().splitlines()}
    if len(prior_groups) != old['excluded_prior_report_groups']:
        raise ValueError('Prior exposure-count reconstruction differs; inspect before selecting')
    exclusions.update(prior_groups)
    # Exclude all report groups used by the recent natural-error research as well.
    natural = ssd / 'datasets/tier8_v2_natural/natural_reports62_01/selection.json'
    for part in json.loads(natural.read_text())['partitions'].values():
        exclusions.update(group(i) for i in part['ids'])
    exposures[str(natural.relative_to(ssd))] = sha(natural)
    eligible = sorted({group(r['id']) for r in rows} - exclusions,
        key=lambda g: (hashlib.sha256(('agere-lab-confirmation-v1:' + g).encode()).hexdigest(), g))
    if len(eligible) < 50:
        raise ValueError('Fewer than50 unexposed report groups; do not silently weaken selection')
    selected_groups = eligible[:50]
    selected = sorted((r for r in rows if group(r['id']) in set(selected_groups)), key=lambda r: r['id'])
    public = [packet(r) for r in selected]
    demo_source = ROOT / 'research/tier8_v2/data/finqa-training-demos.json'
    demo_groups = {group(x['source_id']) for x in json.loads(demo_source.read_text())['examples']}
    if demo_groups & set(selected_groups):
        raise ValueError('Demonstration reports overlap selected confirmation reports')
    # Seal all model-facing packets before opening answer/program annotations for
    # the separate scoring payload. packet() accepts no gold labels in its output.
    out.mkdir(parents=True)
    data = out / 'public.jsonl'
    data.write_text(''.join(json.dumps(p, sort_keys=True) + '\n' for p in public))
    gold = out / 'scoring-source.json'
    gold.write_text(json.dumps(selected) + '\n')
    demos = out / 'demonstrations.json'
    shutil.copyfile(demo_source, demos)
    model_manifest = json.loads((ssd / 'phase2/manifests/gguf_artifacts.json').read_text())
    by_file = {Path(x['path']).name: x for x in model_manifest['artifacts']}
    def model(size, kind):
        entry = by_file[f'qwen2.5-{size}-instruct-{kind}.gguf']
        path = ssd / entry['path']
        if path.stat().st_size != entry['size_bytes']:
            raise ValueError('Missing/truncated staged model: ' + str(path))
        return {k: entry[k] for k in ('path', 'sha256', 'size_bytes', 'model', 'source_revision', 'gguf_type')}
    config = {
        'protocol_id': 'finance-deployment-lab-v1', 'primary_tier': 16,
        'runtime_pin': 'configs/lab_tiers/runtime_pin.json',
        'dataset': {'public': str(data.relative_to(ssd)), 'public_sha256': sha(data),
            'gold': str(gold.relative_to(ssd)), 'gold_sha256': sha(gold),
            'demos': str(demos.relative_to(ssd)), 'demos_sha256': sha(demos),
            'n': len(public), 'reports': 50, 'source_sha256': sha(source),
            'ids': [p['id'] for p in public], 'report_groups': selected_groups,
            'exposure_manifests_sha256': exposures,
            'selection': 'First50 eligible whole reports by fixed ID hash; all their questions, no answer/difficulty/outcome filter.',
            'limits': 'Public FinQA development-source reports not used in the recorded8GB research selections. No guarantee of pretraining cleanliness or complete coverage of unrecorded human exposure. Numerical QA, not KYC/credit invention or mismatch recall.'},
        'common': {'context': 8192, 'threads': 8, 'output_token_cap': 2048, 'seed': 42,
            'temperature': 0, 'n_gpu_layers': 0, 'use_mmap': False,
            'program_mode': 'reference', 'unit_mode': 'question', 'selector': 'suggest',
            'causal_mode': 'grammar', 'catalog_style': 'compact', 'planner': 'direct', 'critic_protocol': 'binary'},
        'profiles': {
            'primary': {'analysis_tokens': 128, 'demos': 2, 'repair': 'none'},
            'direct_control': {'analysis_tokens': 0, 'demos': 0, 'repair': 'none'},
            'repair_ablation': {'analysis_tokens': 128, 'demos': 2, 'repair': 'full'}},
        'tiers': {
            '16': {'nominal_cap_bytes': 12800000000, 'sas': {'sas': model('14b', 'q4_k_m')},
                'mas': {'extractor': model('1.5b', 'f16'), 'drafter': model('3b', 'f16'), 'verifier': model('0.5b', 'f16')}},
            '32': {'nominal_cap_bytes': 25600000000, 'sas': {'sas': model('32b', 'q4_k_m')},
                'mas': {'extractor': model('3b', 'f16'), 'drafter': model('7b', 'f16'), 'verifier': model('0.5b', 'f16')}}},
        'adaptation': 'Pretrained models in BOTH main arms; no compatible14B/32B trained adapters exist on SSD.8GB SFT results remain a separate experiment. No claim of equally optimal fine-tuning.',
        'scope_amendment': 'Prospective source-grounded numerical financial QA deployment comparison, FP16 resident specialists versus larger Q4 monolith. Does not establish original KYC/credit invention/mismatch endpoints.',
        'statistics': {'primary': '16GB primary-profile SAS versus MAS, all cases including withheld.',
            'endpoints': ['correct_delivered', 'wrong_delivered', 'withheld'],
            'metrics': ['case_success', 'raw_execution_match'], 'resampling_unit': 'whole_report',
            'bootstrap_resamples': 10000, 'seed': 42,
            'interpretation': 'Paired effect estimates/intervals; no automatic proof of H0/equivalence. Other profiles/32GB secondary; no favorable-metric selection or best-only reporting.'},
        'excluded_methods': ['header materialization', 'source-span catalog expansion', 'new repair controllers', '8GB adapter applied to another model size'],
        'freeze_requires': 'Both queued8GB secondary prompt jobs and their paired audits complete before sealing code for lab execution.'}
    write(out / 'selection.json', {'source': str(source.relative_to(ssd)), 'excluded_report_groups': sorted(exclusions),
        'selected_report_groups': selected_groups, 'n': len(public), 'model_calls': 0,
        'source_sha256': sha(source), 'public_sha256': sha(data), 'gold_sha256': sha(gold)})
    write(ROOT / 'configs/lab_tiers/protocol.json', config)
    print(json.dumps({'dataset': str(out), 'n': len(public), 'reports': 50, 'config': 'configs/lab_tiers/protocol.json'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ssd', required=True)
    args = parser.parse_args()
    prepare(Path(args.ssd).resolve(strict=True))
