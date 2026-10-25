"""Memory-monitored reversible adapter/last-logit check on validation prompts.

Supports a full SAS dual-task policy or a MAS binary critic. No QA targets or
accuracy inference. Unlike the legacy proof, never allocate n_ctx*vocabulary
history logits. All three phases evaluate and charge the full forced prefix.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import psutil
from binary_verifier_score import VerificationBudget, score, LABELS
from tier8_artifact_paths import artifact_path
from tier8_v2_adapter_runtime import load_adapter, load_critic_adapter
from tier8_v2_adapter_convert import validate_adapter
from tier8_v2_posttrain_queue import sha, write
from tier8_v2_run import MODEL_FILES, WEIGHTS, verified_models

ROOT = Path(__file__).resolve().parents[1]
CAP = 6400000000


def label_logprobs(logits):
    maximum = max(logits.values())
    normalizer = maximum + math.log(sum(math.exp(v - maximum) for v in logits.values()))
    return {key: value - normalizer for key, value in logits.items()}


def worker(args):
    import fcntl
    from llama_cpp import Llama, llama_cpp as api
    from tier8_v2_adapt import guard_no_inference
    guard_no_inference()
    lock = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / 'runs/tier8_external.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    root, dataset = artifact_path(args.out), artifact_path(args.dataset)
    info = (load_adapter(args.adapter, 'sas', '3b-q4') if args.arm == 'sas'
            else load_critic_adapter(args.adapter, '3b'))
    run = artifact_path(info['training_run'])
    manifest, summary, _ = validate_adapter(run)
    n, validation = manifest.get('training_n', 0), summary.get('validation_teacher_forced_loss')
    if (manifest['mode'] != 'train' or n <= 0 or summary.get('examples_processed') != n
            or summary['optimizer_updates'] != (n + 7) // 8
            or not isinstance(validation, (int, float)) or not math.isfinite(validation)):
        raise ValueError('Require complete epoch and finite validation, not fit adapter')
    if manifest['input_sha256'].get(str(dataset)) != sha(dataset):
        relative = str(dataset.relative_to(ROOT)) if dataset.is_relative_to(ROOT) else None
        if not relative or manifest['input_sha256'].get(relative) != sha(dataset):
            raise ValueError('Proof dataset must be bound to actual training')
    row = next(r for r in map(json.loads, dataset.read_text().splitlines())
               if r['split'] == 'validation' and r.get('purpose') == 'critic')
    model_path = artifact_path(args.model_path) if args.model_path else (
        WEIGHTS / MODEL_FILES['sas']['sas'] if args.arm == 'sas'
        else artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / 'weights/tier8_v2/qwen2.5-3b-instruct-q4_k_m.gguf'))
    models = verified_models(args.arm, verifier_model='3b', use_selector=False,
                             drafter_model='3b-q4', weights_root=str(model_path.parent))
    if model_path.name not in {Path(m['file']).name for m in models}:
        raise ValueError('Model path does not name the pinned deployment model')
    model = Llama(model_path=str(model_path), n_ctx=4096, n_gpu_layers=0, n_threads=8,
                  n_threads_batch=8, n_batch=64, n_ubatch=64, seed=42, use_mmap=False,
                  verbose=False, logits_all=False, lora_path=str(artifact_path(info['file'])), lora_scale=0.0)
    try:
        if not getattr(model, '_lora_adapter', None):
            raise ValueError('Missing runtime adapter handle')
        budget, phases = VerificationBudget(max_prefill_tokens=12288, max_checks=3), []
        for scale in (0.0, 1.0, 0.0):
            if api.llama_set_adapter_lora(model._ctx.ctx, model._lora_adapter, scale):
                raise ValueError('Runtime rejected adapter scale')
            event = score(model, row['prompt'], budget, context=4096)
            if event['status'] != 'scored':
                raise ValueError('Validation prefix could not be fully scored')
            # With logits_all=False there is exactly one native output row.
            # Independent native entry points must expose the same label values.
            pointer = model._ctx.get_logits()
            repeated = {label: float(pointer[event['label_ids'][label]]) for label in LABELS}
            if repeated != event['label_logits']:
                raise ValueError('Native last-output logits entry points disagree')
            phases.append({'scale': scale, 'event': event,
                           'conditional_label_logprobs': label_logprobs(event['label_logits'])})
        zero, one, repeated = [p['conditional_label_logprobs'] for p in phases]
        drift = max(abs(zero[k] - repeated[k]) for k in LABELS)
        effect = max(abs(zero[k] - one[k]) for k in LABELS)
        if drift > 1e-5 or effect <= max(1e-5, 10 * drift):
            raise ValueError('No reversible conditional label effect established')
        proof = {'pass': True, 'arm': args.arm, 'adapter': info, 'source_id': row['source_id'],
                 'dataset': str(dataset), 'dataset_sha256': sha(dataset), 'phases': phases,
                 'zero_repeat_max_label_logprob_drift': drift, 'max_label_logprob_effect': effect,
                 'actual_prefill_tokens': budget.prefill_tokens, 'actual_generated_tokens': 0,
                 'native_entry_points_equal': True, 'logits_all': False,
                 'verified_models': models,
                 'scope': 'Training-validation conditional label adapter effect; not QA gain, calibration, or parity with unconstrained greedy JSON generation.'}
        write(root / 'proof.json', proof)
    finally:
        model.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arm', required=True, choices=('sas', 'mas'))
    parser.add_argument('--adapter', required=True)
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--model-path')
    parser.add_argument('--out', required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    if args.worker:
        worker(args)
        return
    root = artifact_path(args.out)
    if root.exists():
        raise ValueError('Refuse overwrite')
    if psutil.virtual_memory().available < CAP + 1000000000:
        raise MemoryError('Insufficient available host memory')
    root.mkdir(parents=True)
    command = [sys.executable, '-u', str(Path(__file__)), *sys.argv[1:], '--worker']
    source_files = [Path(__file__), ROOT / 'scripts/binary_verifier_score.py',
                    ROOT / 'scripts/completion_tokenization.py', ROOT / 'scripts/tier8_v2_adapter_runtime.py']
    write(root / 'manifest.json', {'command': command, 'source_sha256': {str(p): sha(p) for p in source_files},
                                  'cap_bytes': CAP, 'model_path': args.model_path, 'dataset_sha256': sha(artifact_path(args.dataset)),
                                  'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
    peak, breach, child = 0, False, None
    try:
        with (root / 'worker.log').open('x') as log, (root / 'memory.jsonl').open('x') as memory:
            child = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT, start_new_session=True, close_fds=True)
            while child.poll() is None:
                try:
                    proc = psutil.Process(child.pid)
                    rss = sum(p.memory_info().rss for p in [psutil.Process(), proc, *proc.children(recursive=True)] if p.is_running())
                except psutil.NoSuchProcess:
                    continue
                available = psutil.virtual_memory().available
                peak = max(peak, rss)
                memory.write(json.dumps({'time': time.time(), 'tree_rss_bytes': rss, 'host_available_bytes': available}) + '\n')
                memory.flush()
                if rss > CAP or available < 1000000000:
                    breach = True
                    os.killpg(child.pid, signal.SIGKILL)
                    break
                time.sleep(.2)
            code = child.wait()
        proof = json.loads((root / 'proof.json').read_text()) if (root / 'proof.json').exists() else {}
        valid = code == 0 and not breach and proof.get('pass') is True
        write(root / 'summary.json', {'status': 'complete' if valid else 'failed', 'exit_code': code,
                                      'peak_tree_rss_bytes': peak, 'cap_bytes': CAP,
                                      'memory_breach': breach, 'measured_reasoning_gain': False})
        if not valid:
            raise RuntimeError('Last-logit proof failed; preserve evidence, no retry')
    finally:
        if child and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()


if __name__ == '__main__':
    main()
