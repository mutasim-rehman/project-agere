"""Actual distinct-versus-switched3B specialist parity and RSS measurement.

Run only after other NN work terminates. This compares full final-position logits
and32-token deterministic completions on bound training-validation prompts. It is
serving parity/feasibility, not natural QA improvement or a novel learning method.
"""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import psutil
from completion_tokenization import completion_tokens
from shared_role_models import SharedRoleModels
from tier8_artifact_paths import artifact_path
from tier8_v2_run import Models
from tier8_v2_posttrain_queue import sha, write

ROOT = Path(__file__).resolve().parents[1]
CAP = 6400000000


def bound_prompt(info, path):
    training = json.loads((artifact_path(info['training_run']) / 'manifest.json').read_text())
    path = artifact_path(path)
    name = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    if training['input_sha256'].get(name) != sha(path):
        raise ValueError('Validation prompt dataset is not bound to training')
    return next(row for row in map(json.loads, path.read_text().splitlines()) if row['split'] == 'validation')['prompt']


def observe(model, prompt, out, name):
    import numpy as np
    model.reset()
    ids = completion_tokens(model, prompt)
    if len(ids) + 32 + 8 > model.n_ctx() or model._logits_all:
        raise ValueError('Invalid proof context/logit allocation')
    model.eval(ids)
    if model.n_tokens != len(ids):
        raise ValueError('Prefill count differs')
    pointer = model._ctx.get_logits_ith(-1)
    if not pointer:
        raise ValueError('Missing final-position logits')
    logits = np.ctypeslib.as_array(pointer, shape=(model.n_vocab(),)).copy()
    if not np.isfinite(logits).all():
        raise ValueError('Nonfinite final-position logits')
    vector = out / (name + '-logits.npy')
    np.save(vector, logits, allow_pickle=False)
    model.reset()
    result = model.create_completion(prompt, max_tokens=32, temperature=0, top_k=1,
        repeat_penalty=1, seed=42, stop=['<|im_end|>'])
    if result['usage']['prompt_tokens'] != len(ids):
        raise ValueError('Completion prompt accounting differs')
    return logits, {'name': name, 'logits_file': str(vector), 'logits_sha256': sha(vector),
                    'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                    'prompt_tokens_evaluated': len(ids) + result['usage']['prompt_tokens'],
                    'generated_tokens': result['usage']['completion_tokens'],
                    'completion': result['choices'][0]['text'], 'usage': result['usage']}


def worker(args):
    import numpy as np
    out = artifact_path(args.out)
    write(out / 'phase.json', {'phase': 'distinct'})
    distinct = Models('mas', 4096, residency='shared', verifier_model='3b', use_selector=False,
        drafter_model='3b-q4', adapter=args.actor_adapter, verifier_adapter=args.critic_adapter,
        weights_root=args.weights_root)
    references, observations = {}, []
    try:
        if distinct.models['drafter'] is distinct.models['verifier']:
            raise ValueError('Distinct reference accidentally shared adapted policies')
        prompts = {'drafter': bound_prompt(distinct.adapter_info, args.actor_dataset),
                   'verifier': bound_prompt(distinct.verifier_adapter_info, args.critic_dataset)}
        for role in ('drafter', 'verifier'):
            logits, event = observe(distinct.models[role], prompts[role], out, 'distinct-' + role)
            references[role] = (logits, event)
            observations.append(event)
        # Ensure the parent records the full simultaneous-resident reference.
        write(out / 'distinct-ready.json', {'rss_bytes': psutil.Process().memory_info().rss})
    finally:
        for model in {id(m): m for m in distinct.models.values()}.values():
            model.close()
    del distinct
    gc.collect()
    write(out / 'phase.json', {'phase': 'shared'})
    shared = SharedRoleModels(context=4096, actor_adapter=args.actor_adapter,
        critic_adapter=args.critic_adapter, weights_root=args.weights_root, profile='3b')
    comparisons = []
    try:
        if shared.models['drafter'] is not shared.models['verifier']:
            raise ValueError('Shared backend did not share the actual backbone instance')
        for index, role in enumerate(('drafter', 'verifier', 'drafter', 'verifier')):
            shared.activate(role)
            logits, event = observe(shared.models[role], prompts[role], out, 'shared-' + str(index) + '-' + role)
            reference, saved = references[role]
            maximum = float(np.max(np.abs(logits - reference)))
            same = event['completion'] == saved['completion'] and event['usage'] == saved['usage']
            comparison = {'role': role, 'max_absolute_final_logit_difference': maximum,
                          'same_completion_and_usage': same}
            comparisons.append(comparison)
            observations.append(event)
            if maximum > 1e-5 or not same:
                raise ValueError('Distinct-versus-switched serving parity failed')
        write(out / 'proof.json', {'pass': True, 'comparisons': comparisons, 'observations': observations,
            'adapter_applications': shared.adapter_applications, 'activation_history': shared.activation_history,
            'verified_models': shared.verified_models, 'actual_prefill_tokens': sum(o['prompt_tokens_evaluated'] for o in observations),
            'actual_generated_tokens': sum(o['generated_tokens'] for o in observations),
            'scope': 'Two bound validation prompts, four role switches, full next-token vector and32-token deterministic completions. Not full-program/natural QA equivalence, calibrated independence or novelty.'})
    finally:
        shared.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('actor-adapter', 'critic-adapter', 'actor-dataset', 'critic-dataset', 'weights-root', 'out'):
        parser.add_argument('--' + arg, required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    if args.worker:
        worker(args)
        return
    import fcntl
    lock = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / 'runs/tier8_external.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    out = artifact_path(args.out)
    if out.exists():
        raise ValueError('Refuse overwrite')
    if psutil.virtual_memory().available < CAP + 1250000000:
        raise MemoryError('Insufficient host headroom')
    out.mkdir(parents=True)
    command = [sys.executable, '-u', str(Path(__file__)), *sys.argv[1:], '--worker']
    files = [Path(__file__), ROOT / 'scripts/shared_role_models.py', ROOT / 'scripts/tier8_v2_run.py',
             ROOT / 'scripts/tier8_v2_adapter_runtime.py', ROOT / 'scripts/completion_tokenization.py',
             artifact_path(args.actor_dataset), artifact_path(args.critic_dataset)]
    write(out / 'manifest.json', {'command': command, 'input_sha256': {str(p): sha(p) for p in files},
                                  'cap_bytes': CAP, 'logit_absolute_tolerance': 1e-5,
                                  'runtime': subprocess.check_output([sys.executable, '-c', 'import llama_cpp;print(llama_cpp.__version__)'], text=True).strip()})
    child, peak, breach, by_phase = None, 0, False, {}
    try:
        with (out / 'worker.log').open('x') as log, (out / 'memory.jsonl').open('x') as memory:
            child = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT, start_new_session=True, close_fds=True)
            while child.poll() is None:
                try:
                    proc = psutil.Process(child.pid)
                    rss = sum(p.memory_info().rss for p in [psutil.Process(), proc, *proc.children(recursive=True)] if p.is_running())
                except psutil.NoSuchProcess:
                    continue
                phase = json.loads((out / 'phase.json').read_text())['phase'] if (out / 'phase.json').exists() else 'setup'
                peak = max(peak, rss)
                by_phase[phase] = max(by_phase.get(phase, 0), rss)
                available = psutil.virtual_memory().available
                memory.write(json.dumps({'time': time.time(), 'phase': phase, 'tree_rss_bytes': rss, 'host_available_bytes': available}) + '\n'); memory.flush()
                if rss > CAP or available < 1000000000:
                    breach = True
                    os.killpg(child.pid, signal.SIGKILL)
                    break
                time.sleep(.2)
            code = child.wait()
        proof = json.loads((out / 'proof.json').read_text()) if (out / 'proof.json').exists() else {}
        valid = code == 0 and not breach and proof.get('pass') is True and {'distinct', 'shared'} <= set(by_phase)
        write(out / 'summary.json', {'status': 'complete' if valid else 'failed', 'exit_code': code,
            'memory_breach': breach, 'peak_tree_rss_bytes': peak, 'phase_peak_tree_rss_bytes': by_phase,
            'cap_bytes': CAP, 'measured_reasoning_gain': False, 'novelty_established': False})
        if not valid:
            raise RuntimeError('Serving parity proof failed; preserve evidence, no retry')
    finally:
        if child and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()


if __name__ == '__main__':
    main()
