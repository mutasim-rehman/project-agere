"""Serial monitored SAS7B fit/adaptation after the frozen evaluation.

Full adaptation requires a successful measured fit; neither phase is QA.
No retries, implicit resume, context shortening or concurrent model work.
"""
import argparse
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import psutil
from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha, write, check_inputs, validate_job

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'Qwen/Qwen2.5-7B-Instruct'


def training_runtime():
    probe = ('import importlib.metadata as m,json;'
             'print(json.dumps({k:m.version(k) for k in '
             '["torch","transformers","peft","bitsandbytes","accelerate","tokenizers","safetensors"]}))')
    return json.loads(subprocess.check_output(
        [str(ROOT / '.venv-training/bin/python'), '-c', probe], cwd=ROOT, text=True))


def load_policy():
    return {'device_map': {'model.embed_tokens': 'cpu', 'model.layers': 0,
                           'model.norm': 0, 'lm_head': 'cpu'},
            'quantization': {'load_in_4bit': True, 'bnb_4bit_quant_type': 'nf4',
                             'bnb_4bit_use_double_quant': True,
                             'llm_int8_enable_fp32_cpu_offload': True},
            'projection_dtype': 'bfloat16', 'vocabulary_block_size': 1024,
            'checkpoint_backend': 'safetensors pread via scoped Transformers safe_open compatibility shim',
            'frozen_cpu_storage': 'Keep original BF16 CPU embedding/head; FP32 lookup results before transfer; unchanged BF16 streamed head projection',
            'checkpoint_cpu_storage': 'clone non-resizable borrowed CPU storage on leaf assignment; retain already-owned dtype-converted tensors',
            'cpu_matrices': 'Detach Accelerate offload hooks; CPU embedding lookup, explicit inputs_embeds transfer; streamed CPU frozen head',
            'lora': {'r': 8, 'lora_alpha': 16, 'lora_dropout': .05,
                     'target_modules': 'all-linear'}}


def restore_cpu_matrices(model):
    """CPU placement must mean CPU computation/storage, not full GPU reloads.

    Accelerate normally replaces offloaded parameters with meta tensors and
    reloads the whole module on the GPU in pre_forward. Detaching its leaf hooks
    restores original CPU weights. Decoder callers then pass inputs_embeds and
    bypass the ordinary head forward in favor of frozen_head_loss.
    """
    from accelerate.hooks import remove_hook_from_module
    modules = [model.get_input_embeddings(), model.get_output_embeddings()]
    for module in modules:
        remove_hook_from_module(module, recurse=True)
        if module.weight.device.type != 'cpu' or hasattr(module, '_hf_hook'):
            raise ValueError('Could not restore actual CPU embedding/head storage')
        module.weight.requires_grad_(False)


def completed_dependency(root, plan):
    state = json.loads((root / 'state.json').read_text())
    events = [json.loads(line) for line in (root / 'journal.jsonl').read_text().splitlines()]
    if (state.get('state') != 'complete' or not state.get('all_jobs_finished')
            or not events or events[-1] != state
            or [e['job'] for e in events if e['state'] == 'job_complete'] !=
            [j['name'] for j in plan['jobs']]):
        raise ValueError('Prior queue did not complete every frozen job')
    # Includes original-byte preservation and all four completed external arms.
    validate_job(plan['jobs'][-1], plan['cap_bytes'])


def require_fit(root):
    p = json.loads((root / 'plan.json').read_text())
    state = json.loads((root / 'state.json').read_text())
    s = json.loads((root / 'fit/summary.json').read_text())
    if (state['state'] != 'complete' or s['status'] != 'complete' or s['mode'] != 'fit' or
            s['optimizer_updates'] != 2 or s['changed_adapter_tensors'] <= 0 or p['policy'] != load_policy()):
        raise ValueError('Require successful measured fit under identical model policy')
    for name, digest in p['input_sha256'].items():
        path = artifact_path(name)
        if path == Path(__file__).resolve() and sha(path) != digest:
            # Completed fit predates full-epoch loop support; preserve its exact
            # driver snapshot and verify all shared loading/loss/data components.
            path = root / 'driver-source-snapshot.py'
        if sha(path) != digest:
            raise ValueError('Fit component/data identity differs: ' + name)
    for name, digest in s['adapter_files'].items():
        if Path(name).name != name or sha(root / 'fit/adapter' / name) != digest:
            raise ValueError('Fit adapter evidence differs')


def prepare(out, launch_file, mode='fit', fit_proof=None, dataset_manifest=None, parity_manifest=None):
    if out.exists():
        raise ValueError('Require new fit/controller output directory')
    launch = json.loads(launch_file.read_text())
    queue_plan = artifact_path(launch['plan'])
    if sha(queue_plan) != launch['plan_sha256']:
        raise ValueError('Dependency plan differs from original launch')
    try:
        process = psutil.Process(launch['pid'])
    except psutil.NoSuchProcess:
        process = None
        completed_dependency(queue_plan.parent, json.loads(queue_plan.read_text()))
    if process and (process.create_time() != launch['create_time'] or
            str(queue_plan) not in process.cmdline()):
        raise ValueError('Dependency controller identity differs')
    base = ROOT / 'research/tier8_v2'
    corpus = dataset_manifest or base / 'evidence/deployment-sft-1024-02.json'
    corpus_info = json.loads(corpus.read_text())
    data = artifact_path(corpus_info['output_file'])
    parity_manifest = parity_manifest or base / 'evidence/hf-tokenizer-parity-02.json'
    tokenizer = ROOT / 'weights/hf-tokenizers/sas-7b-q4'
    source = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) /
                           'weights/hf/Qwen--Qwen2.5-7B-Instruct')
    files = [Path(__file__), ROOT / 'scripts/frozen_head_loss.py',
             ROOT / 'scripts/sas_cpu_weight_storage.py',
             ROOT / 'scripts/sas_safetensors_pread.py',
             ROOT / 'scripts/sas_frozen_cpu_prepare.py',
             ROOT / 'scripts/tier8_v2_adapt.py', ROOT / 'scripts/tier8_v2_adapter_convert.py',
             ROOT / 'scripts/tier8_v2_posttrain_queue.py', ROOT / 'scripts/tier8_artifact_paths.py',
             ROOT / 'scripts/supervised_logits.py', ROOT / 'manifests/hf_snapshots.json',
             launch_file, queue_plan, corpus, data, parity_manifest,
             *tokenizer.glob('*'), source / 'config.json', source / 'model.safetensors.index.json']
    files = [p for p in files if p.is_file()]
    files += list((ROOT / '.venv-training').glob('lib/python*/site-packages/accelerate/hooks.py'))
    files += list((ROOT / '.venv-training').glob('lib/python*/site-packages/accelerate/big_modeling.py'))
    files += list((ROOT / '.venv-training').glob('lib/python*/site-packages/transformers/modeling_utils.py'))
    files += list((ROOT / '.venv-training').glob('lib/python*/site-packages/safetensors/torch.py'))
    files += list((ROOT / '.venv-training').glob('lib/python*/site-packages/safetensors/_safetensors_rust*.so'))
    versions = training_runtime()
    if mode == 'train':
        if fit_proof is None:
            raise ValueError('Full adaptation requires explicit successful fit')
        require_fit(fit_proof)
        files += [fit_proof / name for name in ['plan.json', 'state.json', 'fit/manifest.json', 'fit/summary.json']]
        if (fit_proof / 'driver-source-snapshot.py').exists():
            files.append(fit_proof / 'driver-source-snapshot.py')
    out.mkdir(parents=True)
    plan = {'kind': 'sas7b_offload_adaptation', 'mode': mode, 'out': str(out),
            'fit_proof': str(fit_proof) if fit_proof else None,
            'dataset_manifest': str(corpus), 'parity_manifest': str(parity_manifest),
            'training_n': corpus_info.get('training_n', 661),
            'validation_n': corpus_info.get('validation_n', 100),
            'dependency': {'pid': launch['pid'], 'create_time': launch['create_time'],
                           'root': str(queue_plan.parent), 'plan': str(queue_plan)},
            'input_sha256': {str(p): sha(p) for p in files}, 'source_model': str(source),
            'policy': load_policy(), 'host_tree_cap_bytes': 10500000000,
            'runtime_versions': versions,
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'host_reserve_bytes': 1000000000, 'minimum_available_before_worker': 9000000000,
            'sampling_interval_seconds': .2,
            'scope': ('Two-update feasibility only.' if mode == 'fit' else 'One full adaptation epoch after measured fit.') +
                     ' Training memory is separate from the simulated8GB deployment cap. No QA gain or novelty claim.'}
    write(out / 'plan.json', plan)
    print(json.dumps({'plan': str(out / 'plan.json'), 'sha256': sha(out / 'plan.json')}))


def worker(plan):
    from tier8_v2_adapt import encode_example, guard_no_inference
    from tier8_v2_adapter_convert import check_architecture
    import fcntl
    guard_no_inference()
    lock = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / 'runs/tier8_external.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    check_inputs(plan)
    if plan.get('mode', 'fit') == 'train':
        require_fit(artifact_path(plan['fit_proof']))
    if training_runtime() != plan['runtime_versions']:
        raise ValueError('Training runtime changed')
    dep = plan['dependency']
    completed_dependency(artifact_path(dep['root']), json.loads(artifact_path(dep['plan']).read_text()))
    if plan['policy'] != load_policy():
        raise ValueError('Unsupported training policy')
    for key, relative in {'HF_HOME': '.local/hf-training', 'TRITON_CACHE_DIR': '.local/triton-cache',
                          'CUDA_CACHE_PATH': '.local/cuda-cache', 'TMPDIR': '.local/tmp'}.items():
        os.environ[key] = str(ROOT / relative)
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                      TOKENIZERS_PARALLELISM='false', PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True')
    import random
    import torch
    import transformers
    import peft
    import bitsandbytes
    import accelerate
    from transformers import AutoTokenizer, BitsAndBytesConfig
    from sas_cpu_weight_storage import StorageDetachedQwen2ForCausalLM
    from peft import get_peft_model, LoraConfig
    from sas_frozen_cpu_prepare import prepare_frozen_cpu_model
    from frozen_head_loss import causal_frozen_head_loss
    torch.set_num_threads(2)
    random.seed(42); torch.manual_seed(42)
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise ValueError('CUDA BF16 required')
    torch.cuda.manual_seed_all(42)
    source = artifact_path(plan['source_model'])
    registry = json.loads((ROOT / 'manifests/hf_snapshots.json').read_text())
    entries = [r for r in registry['artifacts'] if r['repo_id'] == MODEL]
    if not entries or len({r['path'] for r in entries}) != len(entries):
        raise ValueError('Missing or duplicate pinned model assets')
    for row in entries:
        path = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / row['path'])
        if path.parent != source or path.stat().st_size != row['size_bytes'] or sha(path) != row['sha256']:
            raise ValueError('Official source model asset differs: ' + row['path'])
    cfg = json.loads((source / 'config.json').read_text())
    tokenizer_dir = ROOT / 'weights/hf-tokenizers/sas-7b-q4'
    check_architecture(cfg, json.loads((tokenizer_dir / 'config.json').read_text()))
    if cfg.get('tie_word_embeddings') or cfg['vocab_size'] != 152064 or cfg['hidden_size'] != 3584:
        raise ValueError('Require pinned untied Qwen7B architecture')
    base = ROOT / 'research/tier8_v2/evidence'
    data_path = artifact_path(plan.get('dataset_manifest', base / 'deployment-sft-1024-02.json'))
    data = json.loads(data_path.read_text())
    parity = json.loads(artifact_path(plan.get('parity_manifest', base / 'hf-tokenizer-parity-02.json')).read_text())
    corpus = artifact_path(data['output_file'])
    if (not parity['pass'] or not parity['profiles']['sas-7b-q4']['pass'] or
            parity['transformers_version'] != transformers.__version__ or
            sha(corpus) != data['output_sha256'] or sha(corpus) != parity['dataset_sha256'] or
            sha(data_path) != parity['dataset_manifest_sha256']):
        raise ValueError('Require unchanged corpus and current-runtime parity')
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir), local_files_only=True)
    if data.get('purpose', 'drafter') != 'drafter':
        raise ValueError('SAS policy dataset purpose differs')
    rows = []
    for line in corpus.read_text().splitlines():
        original = json.loads(line)
        row = encode_example(tokenizer, original, 'sas-7b-q4')
        row['training_task'] = original.get('purpose', 'drafter')
        rows.append(row)
    task_weights = data.get('task_loss_weights', {'drafter': 1.})
    if any(r['training_task'] not in task_weights for r in rows) or any(
            not isinstance(w, (int, float)) or not math.isfinite(w) or w <= 0 for w in task_weights.values()):
        raise ValueError('Invalid predeclared task weights')
    train = [r for r in rows if r['split'] == 'train']
    if len(train) != plan.get('training_n', 661) or sum(r['split'] == 'validation' for r in rows) != plan.get('validation_n', 100):
        raise ValueError('Comparable actor corpus/splits differ')
    longest = max(train, key=lambda r: (len(r['input_ids']), r['source_id']))
    mode = plan.get('mode', 'fit')
    out = artifact_path(plan['out']) / mode
    out.mkdir(exist_ok=False)
    def event(state, **fields):
        with (out / 'events.jsonl').open('a') as f:
            f.write(json.dumps({'state': state, 'time': time.time(), **fields}) + '\n'); f.flush()
    manifest = {'mode': mode, 'profile': '7b', 'purpose': 'drafter', 'seed': 42,
                'source_commit': plan['source_commit'],
                'input_sha256': plan['input_sha256'], 'policy': plan['policy'],
                'training_base': {'folder': str(source), 'artifacts': entries},
                'training_n': len(train), 'validation_n': sum(r['split'] == 'validation' for r in rows),
                'training_tasks': data.get('training_tasks', ['drafter']),
                'task_loss_weights': task_weights,
                'fit_source_id': longest['source_id'], 'fit_sequence_tokens': len(longest['input_ids']),
                'lora': plan['policy']['lora'],
                'runtime': {'torch': torch.__version__, 'transformers': transformers.__version__,
                            'peft': peft.__version__, 'bitsandbytes': bitsandbytes.__version__,
                            'accelerate': accelerate.__version__},
                'loss': 'Full decoder context; ordinary causal shift; all supervised targets and full vocabulary; BF16 head projection, FP32 logsumexp; frozen CPU head streamed by blocks',
                'scope': plan['scope']}
    write(out / 'manifest.json', manifest)
    started = time.monotonic()
    try:
        torch.cuda.reset_peak_memory_stats()
        event('loading')
        quant = BitsAndBytesConfig(**plan['policy']['quantization'], bnb_4bit_compute_dtype=torch.bfloat16)
        from sas_safetensors_pread import pread_checkpoint_loading
        with pread_checkpoint_loading():
            model = StorageDetachedQwen2ForCausalLM.from_pretrained(str(source), local_files_only=True,
                trust_remote_code=False, use_safetensors=True, low_cpu_mem_usage=True,
                quantization_config=quant, device_map=plan['policy']['device_map'],
                torch_dtype=torch.bfloat16, attn_implementation='sdpa')
        counts = [getattr(m, '_cpu_storage_detach_count', 0) for m in
                  [model.get_input_embeddings(), model.get_output_embeddings()]]
        if counts != [1, 1]:
            raise ValueError('CPU checkpoint-storage hooks did not run exactly once')
        event('cpu_checkpoint_storage_detached', counts=counts,
              clones=[getattr(m, '_cpu_storage_clone_count', 0) for m in
                      [model.get_input_embeddings(), model.get_output_embeddings()]])
        restore_cpu_matrices(model)
        event('cpu_matrices_restored', host_rss=psutil.Process().memory_info().rss)
        model.config.use_cache = False
        model = prepare_frozen_cpu_model(model)
        event('kbit_prepared', host_rss=psutil.Process().memory_info().rss)
        model = get_peft_model(model, LoraConfig(**plan['policy']['lora'], bias='none', task_type='CAUSAL_LM'))
        event('lora_prepared', host_rss=psutil.Process().memory_info().rss)
        base_model = model.get_base_model()
        if (base_model.get_input_embeddings().weight.device.type != 'cpu' or
                base_model.lm_head.weight.device.type != 'cpu' or base_model.lm_head.bias is not None):
            raise ValueError('Frozen embedding/head placement differs')
        trainable = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
        if not trainable or any('lora_' not in n or p.device.type != 'cuda' for n, p in trainable):
            raise ValueError('Require CUDA-only trainable adapters')
        params = [p for _, p in trainable]
        before = [p.detach().cpu().clone() for p in params]
        optimizer = torch.optim.AdamW(params, lr=2e-4, weight_decay=0)
        model.train()
        def loss_for(row):
            ids = torch.tensor([row['input_ids']], device='cpu')
            labels = torch.tensor([row['labels']], device='cuda')
            embeddings = base_model.get_input_embeddings()(ids).float().to('cuda')
            with torch.autocast('cuda', dtype=torch.bfloat16):
                hidden = base_model.model(inputs_embeds=embeddings, use_cache=False).last_hidden_state
                loss = causal_frozen_head_loss(hidden.to(torch.bfloat16), base_model.lm_head.weight,
                                              labels, plan['policy']['vocabulary_block_size'])
            if not torch.isfinite(loss).item():
                raise ValueError('Nonfinite fit loss')
            return loss
        if mode == 'fit':
            longest_target = max(train, key=lambda r: (sum(v != -100 for v in r['labels']), r['source_id']))
            groups = [[longest], [longest_target]]
            event('fit_cases', source_ids=[longest['source_id'], longest_target['source_id']],
                  tokens=[len(longest['input_ids']), len(longest_target['input_ids'])])
        else:
            random.Random(42).shuffle(train)
            groups = [train[i:i + 8] for i in range(0, len(train), 8)]
        for step, group in enumerate(groups, 1):
            optimizer.zero_grad(set_to_none=True)
            group_loss = 0.
            for row in group:
                loss = loss_for(row)
                weight = task_weights[row['training_task']]
                group_loss += weight * loss.detach().item() / len(group)
                (weight * loss / len(group)).backward()
            norm = torch.nn.utils.clip_grad_norm_(params, 1.)
            if not torch.isfinite(norm).item() or norm.item() <= 0:
                raise ValueError('No finite nonzero adapter gradient')
            optimizer.step()
            if any(not torch.isfinite(p).all().item() for p in params):
                raise ValueError('Nonfinite adapter after update')
            event('update', step=step, examples=len(group), loss=group_loss, gradient_norm=norm.item(),
                  gpu_peak_allocated=torch.cuda.max_memory_allocated(),
                  gpu_peak_reserved=torch.cuda.max_memory_reserved(), host_rss=psutil.Process().memory_info().rss)
        changed = sum(not torch.equal(a, b.detach().cpu()) for a, b in zip(before, params))
        if not changed:
            raise ValueError('Adapter did not change')
        model.save_pretrained(str(out / 'adapter'), safe_serialization=True)
        validation_loss = None
        validation_by_task = {}
        if mode == 'train':
            model.eval()
            with torch.no_grad():
                values = [(row['training_task'], loss_for(row).item()) for row in rows if row['split'] == 'validation']
            validation_loss = sum(task_weights[task] * value for task, value in values) / len(values)
            validation_by_task = {task: sum(v for t, v in values if t == task) / sum(t == task for t, _ in values)
                                  for task in task_weights if any(t == task for t, _ in values)}
            if not math.isfinite(validation_loss):
                raise ValueError('Nonfinite validation loss')
        summary = {'status': 'complete', 'mode': mode, 'optimizer_updates': len(groups),
                   'examples_processed': sum(map(len, groups)), 'changed_adapter_tensors': changed,
                   'trainable_parameters': sum(p.numel() for p in params),
                   'last_training_loss': group_loss, 'validation_teacher_forced_loss': validation_loss,
                   'validation_teacher_forced_loss_by_task': validation_by_task,
                   'wall_seconds': time.monotonic() - started,
                   'gpu_peak_allocated': torch.cuda.max_memory_allocated(),
                   'gpu_peak_reserved': torch.cuda.max_memory_reserved(),
                   'adapter_files': {p.name: sha(p) for p in (out / 'adapter').iterdir() if p.is_file()},
                   'deployment_adapter_applied': False, 'measured_reasoning_gain': False}
        write(out / 'summary.json', summary); event('complete', **summary)
    except BaseException as exc:
        write(out / 'summary.json', {'status': 'failed', 'error': repr(exc), 'model_training_result_valid': False})
        event('failed', error=repr(exc)); raise


def controller(plan_path):
    import fcntl
    plan = json.loads(plan_path.read_text()); frozen = sha(plan_path)
    root = artifact_path(plan['out'])
    lock = (root / 'controller.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (root / 'journal.jsonl').exists():
        raise ValueError('Never implicitly restart an existing fit controller')
    def record(state, **fields):
        item = {'state': state, 'time': time.time(), **fields}
        with (root / 'journal.jsonl').open('a') as f:
            f.write(json.dumps(item) + '\n'); f.flush(); os.fsync(f.fileno())
        write(root / 'state.json', item)
    child = None
    def interrupted(sig, frame):
        raise InterruptedError(f'Signal {sig}')
    signal.signal(signal.SIGTERM, interrupted); signal.signal(signal.SIGINT, interrupted)
    try:
        check_inputs(plan)
        dep = plan['dependency']
        try:
            process = psutil.Process(dep['pid'])
        except psutil.NoSuchProcess:
            process = None
        if process:
            if process.create_time() != dep['create_time'] or dep['plan'] not in process.cmdline():
                raise ValueError('Dependency PID identity mismatch')
            record('waiting_for_frozen_evaluation', pid=dep['pid'], create_time=dep['create_time'])
            while True:
                try:
                    if process.status() == psutil.STATUS_ZOMBIE:
                        break
                    process.wait(timeout=10); break
                except psutil.TimeoutExpired:
                    pass
                except psutil.NoSuchProcess:
                    break
        if sha(plan_path) != frozen:
            raise ValueError('Fit plan changed while waiting')
        check_inputs(plan)
        previous = json.loads(artifact_path(dep['plan']).read_text())
        completed_dependency(artifact_path(dep['root']), previous)
        if training_runtime() != plan['runtime_versions']:
            raise ValueError('Training runtime changed while waiting')
        if psutil.virtual_memory().available < plan['minimum_available_before_worker']:
            raise ValueError('Insufficient host headroom for offloaded training; no retry')
        command = [str(ROOT / '.venv-training/bin/python'), '-u', str(Path(__file__)),
                   '--plan', str(plan_path), '--worker']
        record('starting_fit', command=command, training_memory_separate_from_deployment=True)
        peak = 0; breach = False
        with (root / 'worker.log').open('x') as log, (root / 'memory.jsonl').open('x') as memory:
            child = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=log, start_new_session=True, close_fds=True)
            proc = psutil.Process(child.pid)
            while child.poll() is None:
                try:
                    members = [{'pid': p.pid, 'rss': p.memory_info().rss} for p in
                               [psutil.Process(), proc, *proc.children(recursive=True)] if p.is_running()]
                    rss = sum(p['rss'] for p in members)
                    detail = proc.memory_full_info()
                except psutil.NoSuchProcess:
                    continue
                available = psutil.virtual_memory().available; peak = max(peak, rss)
                memory.write(json.dumps({'time': time.time(), 'tree_rss_bytes': rss,
                                         'process_rss': members,
                                         'worker_uss_bytes': getattr(detail, 'uss', None),
                                         'worker_pss_bytes': getattr(detail, 'pss', None),
                                         'host_available_bytes': available}) + '\n'); memory.flush()
                if rss > plan['host_tree_cap_bytes'] or available < plan['host_reserve_bytes']:
                    breach = True; os.killpg(child.pid, signal.SIGKILL); break
                time.sleep(plan['sampling_interval_seconds'])
            code = child.wait(); child = None
        record('worker_exited', exit_code=code, memory_breach=breach, peak_tree_rss_bytes=peak)
        if code or breach:
            raise RuntimeError('Offload fit failed; preserve evidence, no retry')
        mode = plan.get('mode', 'fit')
        result = json.loads((root / mode / 'summary.json').read_text())
        expected_examples = 2 if mode == 'fit' else plan['training_n']
        expected_updates = 2 if mode == 'fit' else (expected_examples + 7) // 8
        if (result['status'] != 'complete' or result['optimizer_updates'] != expected_updates or
                result['examples_processed'] != expected_examples or result['changed_adapter_tensors'] <= 0 or
                (mode == 'train' and (not isinstance(result['validation_teacher_forced_loss'], (float, int)) or
                                      not math.isfinite(result['validation_teacher_forced_loss'])))):
            raise ValueError('Incomplete fit proof')
        record('complete', peak_tree_rss_bytes=peak, fit_only=mode == 'fit', measured_reasoning_gain=False)
    except BaseException as exc:
        if child and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL); child.wait()
        record('failed', error=repr(exc)); raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepare', action='store_true'); p.add_argument('--out')
    p.add_argument('--mode', choices=['fit', 'train'], default='fit'); p.add_argument('--fit-proof')
    p.add_argument('--dataset-manifest'); p.add_argument('--parity-manifest')
    p.add_argument('--dependency-launch', default='research/tier8_v2/evidence/critic3b-posttrain-launch-02.json')
    p.add_argument('--plan'); p.add_argument('--worker', action='store_true')
    a = p.parse_args()
    if a.prepare:
        if not a.out or a.plan or a.worker:
            raise ValueError('Prepare requires only new out and dependency launch')
        prepare(artifact_path(a.out), artifact_path(a.dependency_launch), a.mode,
                artifact_path(a.fit_proof) if a.fit_proof else None,
                artifact_path(a.dataset_manifest) if a.dataset_manifest else None,
                artifact_path(a.parity_manifest) if a.parity_manifest else None)
    elif a.plan:
        plan_path = artifact_path(a.plan)
        worker(json.loads(plan_path.read_text())) if a.worker else controller(plan_path)
    else:
        raise ValueError('Prepare a new plan or run an existing frozen plan')


if __name__ == '__main__':
    main()
