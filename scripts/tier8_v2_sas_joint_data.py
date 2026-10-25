"""Matched task exposure for one SAS policy versus separate MAS adapters.

Combine existing drafting and extended-critic rows without new labels or sources.
Task-balanced loss is predeclared; this is a stronger baseline, not novelty.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path

from tier8_artifact_paths import artifact_path
from tier8_v2_adaptation_prompts import tokenized_target
from tier8_v2_critic_data import sha

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'sas-7b-q4'


def build(out):
    from llama_cpp import Llama
    sources = {'drafter': ROOT / 'research/tier8_v2/evidence/deployment-sft-1024-02.json',
               'critic': artifact_path(Path(os.environ['AGERE_SSD_ROOT']) /
                    'datasets/tier8_v2_critic/critic_extended_sft_02/manifest.json')}
    model = ROOT / 'weights/tier8_v2/qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf'
    from tier8_v2_run import verified_models
    for entry in verified_models('sas'):
        path = ROOT / 'weights/tier8_v2' / Path(entry['file']).name
        if sha(path) != entry['sha256']:
            raise ValueError('Pinned SAS tokenizer model differs')
    tokenizer = Llama(model_path=str(model), vocab_only=True, n_gpu_layers=0, verbose=False)
    rows = []; inputs = {}; counts = Counter(); groups = {'train': set(), 'validation': set()}
    try:
        for task, manifest_path in sources.items():
            m = json.loads(manifest_path.read_text()); data = artifact_path(m['output_file'])
            if sha(data) != m['output_sha256']:
                raise ValueError('Source corpus differs')
            inputs[str(manifest_path)] = sha(manifest_path); inputs[str(data)] = sha(data)
            for original in map(json.loads, data.read_text().splitlines()):
                row = deepcopy(original)
                row['source_id'] = task + '::' + row['source_id']; row['purpose'] = task
                row['tokenization'] = {PROFILE: tokenized_target(tokenizer, row['prompt'], row['target'], 1024)}
                counts[(task, row['split'])] += 1; groups[row['split']].add(row['report_group'])
                rows.append(row)
    finally:
        tokenizer.close()
    if counts != Counter({('drafter', 'train'): 661, ('drafter', 'validation'): 100,
                          ('critic', 'train'): 3140, ('critic', 'validation'): 382}):
        raise ValueError('Matched task exposure differs')
    if groups['train'] & groups['validation'] or len({r['source_id'] for r in rows}) != len(rows):
        raise ValueError('Report leakage or duplicate source IDs')
    data = out / 'examples.jsonl'; data.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    weights = {task: 3801 / (2 * counts[(task, 'train')]) for task in sources}
    m = {'purpose': 'drafter', 'training_tasks': ['drafter', 'critic'], 'profiles': [PROFILE],
         'training_n': 3801, 'validation_n': 482, 'kept_n': len(rows), 'max_training_tokens': 1024,
         'task_loss_weights': weights, 'task_counts': {'|'.join(k): v for k, v in counts.items()},
         'group_counts': {k: len(v) for k, v in groups.items()}, 'input_sha256': inputs,
         'output_file': str(data), 'output_sha256': sha(data), 'script_sha256': sha(Path(__file__)),
         'model_calls': 0, 'test_opened': False,
         'limits': 'Matched drafting/verification row exposure with MAS actor+extended critic; SAS uses one shared adapter. Fixed equal total training loss mass per task, one shuffled epoch. Optimizer/parameter sharing differs; no causal architecture winner or novelty claim. No filtering/truncation permitted; whole build fails on any overflow.'}
    (out / 'manifest.json').write_text(json.dumps(m, indent=2) + '\n')
    print(json.dumps({k: m[k] for k in ['training_n', 'validation_n', 'task_counts', 'task_loss_weights']}))


def parity(out):
    from transformers import AutoTokenizer, __version__
    import tokenizers
    m = json.loads((out / 'manifest.json').read_text()); data = artifact_path(m['output_file'])
    if sha(data) != m['output_sha256']:
        raise ValueError('Dataset differs')
    tokenizer = AutoTokenizer.from_pretrained(str(ROOT / 'weights/hf-tokenizers' / PROFILE),
                                             local_files_only=True, trust_remote_code=False)
    n = 0
    for row in map(json.loads, data.read_text().splitlines()):
        t = row['tokenization'][PROFILE]; prefix = tokenizer.encode(row['prompt'], add_special_tokens=False)
        full = tokenizer.encode(row['prompt'] + t['response'], add_special_tokens=False)
        if (full[:len(prefix)] != prefix or len(prefix) != t['label_mask_prefix_tokens'] or
                len(full) != t['total_tokens'] or len(full) > 1024 or
                hashlib.sha256(json.dumps(full).encode()).hexdigest() != t['input_ids_sha256']):
            raise ValueError('7B tokenizer parity failed: ' + row['source_id'])
        n += 1
    report = {'pass': n == m['kept_n'], 'n': n, 'profiles': {PROFILE: {'pass': True, 'n': n}},
              'dataset_sha256': sha(data), 'dataset_manifest_sha256': sha(out / 'manifest.json'),
              'transformers_version': __version__, 'tokenizers_version': tokenizers.__version__,
              'script_sha256': sha(Path(__file__)), 'model_calls': 0}
    if (out / 'parity.json').exists():
        raise ValueError('Refuse parity overwrite')
    (out / 'parity.json').write_text(json.dumps(report, indent=2) + '\n'); print(json.dumps(report))


def main():
    p = argparse.ArgumentParser(); p.add_argument('mode', choices=['build', 'parity']); p.add_argument('--out', required=True)
    a = p.parse_args(); out = artifact_path(a.out)
    if a.mode == 'build':
        out.mkdir(parents=True, exist_ok=False); build(out)
    else:
        parity(out)


if __name__ == '__main__':
    main()
