"""Replay one completed frozen natural condition; no neural generation calls."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import check_inputs, sha
from tier8_v2_method_analyze import ArtifactChecks, load_condition, summarize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('study', 'proofs', 'condition', 'partition', 'out'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    study_path, proof_path, out = [artifact_path(x) for x in (args.study, args.proofs, args.out)]
    if out.exists():
        raise ValueError('Refuse audit overwrite')
    study, proofs = [json.loads(p.read_text()) for p in (study_path, proof_path)]
    check_inputs(study)
    jobs = [j for j in study['jobs'] if j['condition'] == args.condition and j['partition'] == args.partition]
    if len(jobs) != 1:
        raise ValueError('Require one declared frozen condition')
    checks, tokenizers = ArtifactChecks(), {}
    try:
        manifest, cases, replayed = load_condition(jobs[0], proofs[args.condition], checks, tokenizers)
        check_inputs(study)
        for path in (study_path, proof_path, Path(__file__), ROOT / 'scripts/tier8_v2_method_analyze.py',
                ROOT / 'scripts/financial_trace_replay.py'):
            checks.verify(path, sha(path))
        result = {'status': 'complete_independent_natural_trace_replay', 'condition': args.condition,
            'partition': args.partition, 'arm': jobs[0]['arm'], 'n': len(cases),
            'result': jobs[0]['result'], 'policy': summarize(replayed),
            'all_prompts_execution_delivery_scores_tokens_memory_and_adapter_proofs_replayed': True,
            'measured_new_generation_calls': 0, 'tokenizer_only': True,
            'novelty_established': False, 'adopted': False, 'input_sha256': checks.files,
            'limits': 'Single completed exploratory condition, not a paired method result or publication confirmation. Prefixes are recorded trajectory ablations, not fresh generations. Numerical scoring/source support do not establish independently adjudicated financial truth.'}
        out.mkdir(parents=True)
        path = out / 'replayed.jsonl'
        path.write_text(''.join(json.dumps({'id': key, **value}, sort_keys=True) + '\n'
            for key, value in replayed.items()))
        result['replayed_sha256'] = sha(path)
        (out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'out': str(out), 'n': len(cases), 'policy': result['policy']}))
    finally:
        for model in tokenizers.values():
            model.close()


if __name__ == '__main__':
    main()
