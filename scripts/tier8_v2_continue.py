"""Matched, fixed-recipe continuation of a proven full adapter.

Preparation requires completed initialization artifacts. Fit updates are discarded;
the full epoch reloads the original initializer and resets AdamW. No resume/retry.
"""
import argparse
import json
import math
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import time

import psutil
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha, write, check_inputs
from tier8_v2_adapter_convert import validate_adapter, check_architecture
from tier8_v2_sas_offload_fit import training_runtime, load_policy, restore_cpu_matrices

ROOT = Path(__file__).resolve().parents[1]
RECIPE = {'learning_rate': 1e-4, 'weight_decay': 0., 'clip_norm': 1.,
          'accumulation': 8, 'epochs': 1, 'seed': 42, 'optimizer_reset': True,
          'lora': {'r': 8, 'lora_alpha': 16, 'lora_dropout': .05, 'target_modules': 'all-linear'}}


def complete_initializer(run, profile, purpose):
    manifest, summary, adapter = validate_adapter(run)
    n = manifest.get('training_n', 0)
    value = summary.get('validation_teacher_forced_loss')
    if (manifest['mode'] != 'train' or manifest['profile'] != profile or
            manifest.get('purpose', 'drafter') != purpose or n <= 0 or
            summary.get('examples_processed') != n or summary['optimizer_updates'] != (n + 7) // 8 or
            manifest.get('validation_n', 0) <= 0 or not isinstance(value, (float, int)) or
            not math.isfinite(value) or manifest['lora'] != RECIPE['lora']):
        raise ValueError('Require a complete compatible full-epoch initializer')
    check_inputs(manifest)
    return manifest, adapter


def identity(plan):
    """Fit and full training must have identical data, initializer and recipe."""
    return {k: plan[k] for k in ('profile', 'purpose', 'dataset_manifest', 'parity_manifest',
                                'initializer', 'recipe', 'input_sha256', 'runtime_versions',
                                'training_base', 'training_n', 'validation_n')}


def deployment_input_hashes(plan):
    """Keep large training-base identities without asking inference to read them.

The plan/controller/worker still STREAM-hash every source shard. The deployment
runtime validates manifest/adapter identity; its legacy input helper read_bytes()
must never allocate a full HF source shard under the deployment memory cap.
"""
    base = plan['training_base']; folder = Path(base['folder'])
    if plan['profile'] == '3b':
        weights = {str(folder / base['weight_file'])}
    else:
        weights = {str(folder / Path(row['path']).name) for row in base['artifacts']
                   if row['path'].endswith('.safetensors')}
    if not weights or not weights <= set(plan['input_sha256']):
        raise ValueError('Source weight identities missing from monitored training plan')
    return ({p: h for p, h in plan['input_sha256'].items() if p not in weights},
            {p: plan['input_sha256'][p] for p in sorted(weights)})


def require_fit(path, plan):
    fit_plan = json.loads((path / 'plan.json').read_text())
    state = json.loads((path / 'state.json').read_text())
    summary = json.loads((path / 'fit/summary.json').read_text())
    if (fit_plan['mode'] != 'fit' or identity(fit_plan) != identity(plan) or
            state['state'] != 'complete' or summary['status'] != 'complete' or
            summary['optimizer_updates'] != 2 or summary['examples_processed'] != 2 or
            summary['changed_adapter_tensors'] <= 0 or not summary['initializer_exactly_loaded']):
        raise ValueError('Full continuation requires its own identical measured fit')
    validate_adapter(path / 'fit')


def discovery_gate(root):
    from tier8_v2_joint_posttrain import verify_result
    launch_path = ROOT / 'research/tier8_v2/evidence/joint-discovery-posttrain-launch-02.json'
    launch = json.loads(launch_path.read_text())
    if artifact_path(launch['plan']).parent != root or sha(root / 'plan.json') != launch['plan_sha256']:
        raise ValueError('Require the declared frozen discovery queue')
    plan = json.loads((root / 'plan.json').read_text())
    state = json.loads((root / 'state.json').read_text())
    if state['state'] != 'complete':
        raise ValueError('Wait for all frozen baseline discovery jobs')
    check_inputs(plan)
    probes = [j for j in plan['jobs'] if j['kind'] == 'quartet_probe']
    target = [j for j in probes if j['arm'] == 'sas' or 'extended' in str(j['adapter'])]
    if len(probes) != 3 or len(target) != 2:
        raise ValueError('Missing intended baseline policies')
    for job in plan['jobs']:
        verify_result(job)
    metrics = [json.loads((artifact_path(j['result']) / 'metrics.json').read_text()) for j in target]
    if all(m['exact_label_correct'] >= 30 and m['complete_exact_quartets'] >= 6 for m in metrics):
        raise ValueError('Predeclared ceiling stop rule: do not manufacture a continuation gain')
    files = [launch_path, root / 'plan.json', root / 'state.json']
    files += [artifact_path(p) for p in plan['input_sha256']]
    for job in probes:
        files += [artifact_path(job['result']) / n for n in
                  ('summary.json', 'metrics.json', 'policy.json', 'responses.jsonl')]
    return files


def prepare(out, dataset_path, initializer, profile, mode, fit, discovery):
    if out.exists():
        raise ValueError('Require a new continuation output directory')
    discovery_files = discovery_gate(discovery)
    data = json.loads(dataset_path.read_text())
    purpose = data['purpose']
    if profile == '7b' and purpose != 'drafter':
        raise ValueError('7B is the joint SAS policy')
    initial, adapter = complete_initializer(initializer, profile, purpose)
    corpus = artifact_path(data['output_file'])
    parity_path = dataset_path.parent / 'parity.json'
    parity = json.loads(parity_path.read_text())
    if (sha(corpus) != data['output_sha256'] or not parity['pass'] or
            parity['dataset_sha256'] != sha(corpus) or parity['dataset_manifest_sha256'] != sha(dataset_path)):
        raise ValueError('Continuation corpus/parity identity differs')
    source_files = [ROOT / 'scripts' / n for n in (
        'tier8_v2_continue.py', 'tier8_v2_adapt.py', 'tier8_v2_adapter_convert.py',
        'tier8_v2_sas_offload_fit.py', 'tier8_v2_posttrain_queue.py', 'tier8_artifact_paths.py',
        'sas_cpu_weight_storage.py', 'sas_frozen_cpu_prepare.py', 'sas_safetensors_pread.py',
        'frozen_head_loss.py', 'supervised_logits.py')]
    tokenizer = ROOT / 'weights/hf-tokenizers' / ('sas-7b-q4' if profile == '7b' else 'mas-3b-q4')
    files = source_files + discovery_files + [p for p in tokenizer.iterdir() if p.is_file()]
    files += [dataset_path, corpus, parity_path, initializer / 'manifest.json', initializer / 'summary.json']
    files += [p for p in adapter.iterdir() if p.is_file()]
    # Bind upstream training inputs too, including the pinned source model registry.
    files += [artifact_path(p) for p in initial.get('input_sha256', {})]
    if profile == '3b':
        base = initial['training_base']; folder = artifact_path(base['folder'])
        files += [folder / base['weight_file']] + [folder / r['file'] for r in base['config_files']]
    else:
        base = initial['training_base']
        files += [ROOT / 'manifests/hf_snapshots.json']
        files += [artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / r['path']) for r in base['artifacts']]
    plan = {'kind': 'matched_adapter_continuation', 'out': str(out), 'mode': mode,
            'profile': profile, 'purpose': purpose, 'initializer': str(initializer),
            'dataset_manifest': str(dataset_path), 'parity_manifest': str(parity_path),
            'training_base': base, 'recipe': RECIPE, 'fit_proof': str(fit) if fit else None,
            'training_n': data['training_n'], 'validation_n': data['validation_n'],
            'runtime_versions': training_runtime(), 'input_sha256': {str(p): sha(p) for p in files},
            'host_tree_cap_bytes': 10500000000, 'host_reserve_bytes': 1000000000,
            'minimum_available_before_worker': 9000000000, 'sampling_interval_seconds': .2,
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'scope': 'Conditional matched continuation; established SFT/rehearsal. Not QA or novelty evidence.'}
    if mode == 'train':
        if fit is None:
            raise ValueError('Full continuation requires measured fit')
        require_fit(fit, plan)
    elif fit is not None:
        raise ValueError('Fit must reload the full initializer, not another fit')
    out.mkdir(parents=True)
    write(out / 'plan.json', plan)
    print(json.dumps({'plan': str(out / 'plan.json'), 'sha256': sha(out / 'plan.json')}))


def restore_exact_adapter(model, adapter):
    """Load all saved LoRA tensors and prove byte-value equality before updates."""
    import torch
    from safetensors.torch import load_file
    from peft import set_peft_model_state_dict, get_peft_model_state_dict
    saved = load_file(str(adapter / 'adapter_model.safetensors'), device='cpu')
    if not saved or any('lora_' not in n or not torch.isfinite(v).all().item() for n, v in saved.items()):
        raise ValueError('Invalid saved initializer tensors')
    set_peft_model_state_dict(model, saved, adapter_name='default')
    actual = get_peft_model_state_dict(model, adapter_name='default')
    if set(saved) != set(actual) or any(
            saved[n].dtype != actual[n].dtype or not torch.equal(saved[n], actual[n].detach().cpu())
            for n in saved):
        raise ValueError('Initializer failed exact state equality')
    if not any(torch.count_nonzero(v).item() for n, v in saved.items() if 'lora_B' in n):
        raise ValueError('Initializer contains no learned B matrices')
    return len(saved)


def worker(plan):
    import fcntl
    from tier8_v2_adapt import encode_example, guard_no_inference
    guard_no_inference()
    lock = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / 'runs/tier8_external.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    check_inputs(plan)
    if plan['recipe'] != RECIPE or training_runtime() != plan['runtime_versions']:
        raise ValueError('Continuation recipe/runtime changed')
    if plan['mode'] == 'train':
        require_fit(artifact_path(plan['fit_proof']), plan)
    for key, relative in {'HF_HOME': '.local/hf-training', 'TRITON_CACHE_DIR': '.local/triton-cache',
                          'CUDA_CACHE_PATH': '.local/cuda-cache', 'TMPDIR': '.local/tmp',
                          'TORCHINDUCTOR_CACHE_DIR': '.local/torchinductor-cache'}.items():
        os.environ[key] = str(ROOT / relative)
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false',
                      PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True')
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import get_peft_model, LoraConfig, prepare_model_for_kbit_training
    from supervised_logits import supervised_window
    from frozen_head_loss import causal_frozen_head_loss
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise ValueError('CUDA BF16 required')
    torch.set_num_threads(2)
    random.seed(42); torch.manual_seed(42); torch.cuda.manual_seed_all(42)
    initial, adapter = complete_initializer(artifact_path(plan['initializer']), plan['profile'], plan['purpose'])
    profile = 'sas-7b-q4' if plan['profile'] == '7b' else 'mas-3b-q4'
    tokenizer_dir = ROOT / 'weights/hf-tokenizers' / profile
    folder = artifact_path(plan['training_base']['folder'])
    check_architecture(json.loads((folder / 'config.json').read_text()), json.loads((tokenizer_dir / 'config.json').read_text()))
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir), local_files_only=True)
    data = json.loads(artifact_path(plan['dataset_manifest']).read_text())
    parity = json.loads(artifact_path(plan['parity_manifest']).read_text())
    if not parity['profiles'][profile]['pass'] or parity['transformers_version'] != plan['runtime_versions']['transformers']:
        raise ValueError('Current-profile tokenizer parity required')
    rows = []
    for line in artifact_path(data['output_file']).read_text().splitlines():
        raw = json.loads(line); row = encode_example(tokenizer, raw, profile)
        row.update(task=raw.get('purpose', plan['purpose']), family=raw.get('family', 'rehearsal'))
        rows.append(row)
    train = [r for r in rows if r['split'] == 'train']
    validation = [r for r in rows if r['split'] == 'validation']
    weights = data.get('task_loss_weights', {plan['purpose']: 1.})
    if (len(train), len(validation)) != (plan['training_n'], plan['validation_n']) or any(
            r['task'] not in weights for r in rows) or any(not math.isfinite(w) or w <= 0 for w in weights.values()):
        raise ValueError('Continuation counts/task weights differ')
    out = artifact_path(plan['out']) / plan['mode']; out.mkdir(exist_ok=False)
    def event(state, **fields):
        with (out / 'events.jsonl').open('a') as stream:
            stream.write(json.dumps({'state': state, 'time': time.time(), **fields}) + '\n'); stream.flush()
    deployment_inputs, source_weights = deployment_input_hashes(plan)
    write(out / 'manifest.json', {**{k: plan[k] for k in ('mode', 'profile', 'purpose', 'training_base',
        'training_n', 'validation_n', 'source_commit', 'scope', 'initializer')},
        'input_sha256': deployment_inputs, 'training_base_artifact_sha256': source_weights,
        'training_base_hash_policy': 'All source weights stream-verified by monitored training controller/worker; their identities are retained here. Deployment validates this manifest and adapter without rereading HF source shards.',
        'lora': RECIPE['lora'], 'optimizer': RECIPE, 'seed': 42, 'task_loss_weights': weights,
        'runtime': plan['runtime_versions'], 'initializer_fit_updates_inherited': False})
    started = time.monotonic()
    event('loading')
    torch.cuda.reset_peak_memory_stats()
    if plan['profile'] == '7b':
        from sas_cpu_weight_storage import StorageDetachedQwen2ForCausalLM
        from sas_safetensors_pread import pread_checkpoint_loading
        from sas_frozen_cpu_prepare import prepare_frozen_cpu_model
        policy = load_policy()
        quant = BitsAndBytesConfig(**policy['quantization'], bnb_4bit_compute_dtype=torch.bfloat16)
        with pread_checkpoint_loading():
            model = StorageDetachedQwen2ForCausalLM.from_pretrained(str(folder), local_files_only=True,
                trust_remote_code=False, use_safetensors=True, low_cpu_mem_usage=True,
                quantization_config=quant, device_map=policy['device_map'], torch_dtype=torch.bfloat16,
                attn_implementation='sdpa')
        if [getattr(m, '_cpu_storage_detach_count', 0) for m in
                (model.get_input_embeddings(), model.get_output_embeddings())] != [1, 1]:
            raise ValueError('CPU storage detachment did not run exactly once')
        restore_cpu_matrices(model); model.config.use_cache = False
        model = prepare_frozen_cpu_model(model)
    else:
        model = AutoModelForCausalLM.from_pretrained(str(folder), local_files_only=True,
            trust_remote_code=False, use_safetensors=True, device_map={'': 0},
            torch_dtype=torch.bfloat16, attn_implementation='sdpa')
        model.config.use_cache = False
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                               gradient_checkpointing_kwargs={'use_reentrant': False})
    model = get_peft_model(model, LoraConfig(**RECIPE['lora'], bias='none', task_type='CAUSAL_LM'))
    tensor_count = restore_exact_adapter(model, adapter)
    trainable = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    if len(trainable) != tensor_count or any('lora_' not in n or p.device.type != 'cuda' for n, p in trainable):
        raise ValueError('Trainable tensors differ from the exact initializer')
    event('initializer_exactly_loaded', tensors=tensor_count, adapter_sha256=sha(adapter / 'adapter_model.safetensors'))
    params = [p for _, p in trainable]; before = [p.detach().cpu().clone() for p in params]
    optimizer = torch.optim.AdamW(params, lr=RECIPE['learning_rate'], weight_decay=RECIPE['weight_decay'])
    base = model.get_base_model()
    def loss_for(row):
        with torch.autocast('cuda', dtype=torch.bfloat16):
            if plan['profile'] == '7b':
                ids = torch.tensor([row['input_ids']], device='cpu')
                labels = torch.tensor([row['labels']], device='cuda')
                embeddings = base.get_input_embeddings()(ids).float().to('cuda')
                hidden = base.model(inputs_embeds=embeddings, use_cache=False).last_hidden_state
                loss = causal_frozen_head_loss(hidden.to(torch.bfloat16), base.lm_head.weight, labels, 1024)
            else:
                window = supervised_window(row)
                loss = model(input_ids=torch.tensor([window['input_ids']], device='cuda'),
                    labels=torch.tensor([window['labels']], device='cuda'), logits_to_keep=window['logits_to_keep']).loss
        if not torch.isfinite(loss).item():
            raise ValueError('Nonfinite continuation loss')
        return loss
    if plan['mode'] == 'fit':
        groups = [[max(train, key=lambda r: (len(r['input_ids']), r['source_id']))],
                  [max(train, key=lambda r: (sum(v != -100 for v in r['labels']), r['source_id']))]]
        event('fit_cases', source_ids=[g[0]['source_id'] for g in groups], tokens=[len(g[0]['input_ids']) for g in groups])
    else:
        random.Random(42).shuffle(train); groups = [train[i:i + 8] for i in range(0, len(train), 8)]
    model.train()
    for step, group in enumerate(groups, 1):
        optimizer.zero_grad(set_to_none=True); total = 0.
        for row in group:
            loss = weights[row['task']] * loss_for(row) / len(group)
            total += loss.detach().item(); loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(params, RECIPE['clip_norm'])
        if not torch.isfinite(norm).item() or norm.item() <= 0:
            raise ValueError('No finite nonzero adapter gradient')
        optimizer.step()
        if any(not torch.isfinite(p).all().item() for p in params):
            raise ValueError('Nonfinite continued adapter')
        event('update', step=step, examples=len(group), loss=total, gradient_norm=norm.item(),
              gpu_peak_allocated=torch.cuda.max_memory_allocated(), gpu_peak_reserved=torch.cuda.max_memory_reserved())
    changed = sum(not torch.equal(a, b.detach().cpu()) for a, b in zip(before, params))
    if not changed:
        raise ValueError('Continuation did not change the initializer')
    model.save_pretrained(str(out / 'adapter'), safe_serialization=True)
    validation_loss = None; by_family_task = {}
    if plan['mode'] == 'train':
        model.eval(); measured = []
        with torch.no_grad():
            for row in validation:
                value = loss_for(row).item(); measured.append((row, value))
                by_family_task.setdefault(row['family'] + '|' + row['task'], []).append(value)
        validation_loss = sum(weights[r['task']] * v for r, v in measured) / len(measured)
        by_family_task = {k: {'n': len(v), 'mean': sum(v) / len(v)} for k, v in by_family_task.items()}
    summary = {'status': 'complete', 'mode': plan['mode'], 'optimizer_updates': len(groups),
        'examples_processed': sum(map(len, groups)), 'initializer_exactly_loaded': True,
        'initializer_tensor_count': tensor_count, 'changed_adapter_tensors': changed,
        'trainable_parameters': sum(p.numel() for p in params), 'last_training_loss': total,
        'validation_teacher_forced_loss': validation_loss, 'validation_by_family_task': by_family_task,
        'wall_seconds': time.monotonic() - started, 'gpu_peak_allocated': torch.cuda.max_memory_allocated(),
        'gpu_peak_reserved': torch.cuda.max_memory_reserved(),
        'adapter_files': {p.name: sha(p) for p in (out / 'adapter').iterdir() if p.is_file()},
        'deployment_adapter_applied': False, 'measured_reasoning_gain': False}
    write(out / 'summary.json', summary); event('complete', **summary)


def controller(path):
    import fcntl
    plan = json.loads(path.read_text()); frozen = sha(path); root = artifact_path(plan['out'])
    lock = (root / 'controller.lock').open('a'); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (root / 'state.json').exists():
        raise ValueError('No implicit continuation retry/resume')
    child = None
    def record(state, **fields):
        item = {'state': state, 'time': time.time(), **fields}
        with (root / 'journal.jsonl').open('a') as stream:
            stream.write(json.dumps(item) + '\n'); stream.flush(); os.fsync(stream.fileno())
        write(root / 'state.json', item)
    def interrupted(sig, frame):
        raise InterruptedError(f'Signal {sig}')
    signal.signal(signal.SIGTERM, interrupted); signal.signal(signal.SIGINT, interrupted)
    try:
        check_inputs(plan)
        if plan['recipe'] != RECIPE or training_runtime() != plan['runtime_versions']:
            raise ValueError('Recipe/runtime changed')
        if psutil.virtual_memory().available < plan['minimum_available_before_worker']:
            raise ValueError('Insufficient preflight headroom; no retry')
        command = [str(ROOT / '.venv-training/bin/python'), '-u', str(Path(__file__)), '--plan', str(path), '--worker']
        record('starting', command=command)
        peak = 0; breach = False
        with (root / 'worker.log').open('x') as log, (root / 'memory.jsonl').open('x') as memory:
            child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=log, stdin=subprocess.DEVNULL,
                                     start_new_session=True, close_fds=True)
            proc = psutil.Process(child.pid)
            while child.poll() is None:
                try:
                    members = [{'pid': p.pid, 'rss': p.memory_info().rss} for p in
                               [psutil.Process(), proc, *proc.children(recursive=True)] if p.is_running()]
                except psutil.NoSuchProcess:
                    continue
                rss = sum(p['rss'] for p in members); peak = max(peak, rss)
                available = psutil.virtual_memory().available
                memory.write(json.dumps({'time': time.time(), 'tree_rss_bytes': rss,
                    'process_rss': members, 'host_available_bytes': available}) + '\n'); memory.flush()
                if rss > plan['host_tree_cap_bytes'] or available < plan['host_reserve_bytes']:
                    breach = True; os.killpg(child.pid, signal.SIGKILL); break
                time.sleep(plan['sampling_interval_seconds'])
            code = child.wait(); child = None
        if code or breach or sha(path) != frozen:
            raise RuntimeError(f'Continuation failed: exit={code}, memory_breach={breach}')
        check_inputs(plan)
        summary = json.loads((root / plan['mode'] / 'summary.json').read_text())
        expected = 2 if plan['mode'] == 'fit' else plan['training_n']
        if (summary['status'] != 'complete' or summary['examples_processed'] != expected or
                summary['optimizer_updates'] != (2 if plan['mode'] == 'fit' else (expected + 7) // 8) or
                not summary['initializer_exactly_loaded'] or summary['changed_adapter_tensors'] <= 0 or
                (plan['mode'] == 'train' and not math.isfinite(summary['validation_teacher_forced_loss']))):
            raise ValueError('Incomplete continuation result')
        record('complete', peak_tree_rss_bytes=peak, fit_only=plan['mode'] == 'fit', measured_reasoning_gain=False)
    except BaseException as exc:
        if child and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL); child.wait()
        record('failed', error=repr(exc)); raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true'); parser.add_argument('--out')
    parser.add_argument('--dataset-manifest'); parser.add_argument('--initializer')
    parser.add_argument('--profile', choices=['3b', '7b']); parser.add_argument('--mode', choices=['fit', 'train'])
    parser.add_argument('--fit-proof'); parser.add_argument('--plan'); parser.add_argument('--worker', action='store_true')
    parser.add_argument('--discovery-root', default='/run/media/mutasim/Data/AGERE/runs/tier8_joint_posttrain/joint03-discovery02')
    args = parser.parse_args()
    if args.prepare:
        if not all((args.out, args.dataset_manifest, args.initializer, args.profile, args.mode)) or args.plan or args.worker:
            raise ValueError('Prepare requires explicit new output, data, full initializer, profile and mode')
        prepare(artifact_path(args.out), artifact_path(args.dataset_manifest), artifact_path(args.initializer),
                args.profile, args.mode, artifact_path(args.fit_proof) if args.fit_proof else None,
                artifact_path(args.discovery_root))
    elif args.plan:
        path = artifact_path(args.plan)
        worker(json.loads(path.read_text())) if args.worker else controller(path)
    else:
        parser.error('Prepare or run a frozen plan')


if __name__ == '__main__':
    main()
