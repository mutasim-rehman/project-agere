"""One serial, monitored SAS7B offload fit gate after the frozen evaluation.

Two updates on the longest original training example, never full adaptation or
QA. No retries, implicit resume, context shortening or concurrent model work.
"""
import argparse
import json
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
             '["torch","transformers","peft","bitsandbytes","accelerate","tokenizers"]}))')
    return json.loads(subprocess.check_output(
        [str(ROOT / '.venv-training/bin/python'), '-c', probe], cwd=ROOT, text=True))


def load_policy():
    return {'device_map': {'model.embed_tokens': 'cpu', 'model.layers': 0,
                           'model.norm': 0, 'lm_head': 'cpu'},
            'quantization': {'load_in_4bit': True, 'bnb_4bit_quant_type': 'nf4',
                             'bnb_4bit_use_double_quant': True,
                             'llm_int8_enable_fp32_cpu_offload': True},
            'projection_dtype': 'bfloat16', 'vocabulary_block_size': 1024,
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


def prepare(out, launch_file):
    if out.exists():
        raise ValueError('Require new fit/controller output directory')
    launch = json.loads(launch_file.read_text())
    queue_plan = artifact_path(launch['plan'])
    if sha(queue_plan) != launch['plan_sha256']:
        raise ValueError('Dependency plan differs from original launch')
    process = psutil.Process(launch['pid'])
    if (process.create_time() != launch['create_time'] or
            str(queue_plan) not in process.cmdline()):
        raise ValueError('Dependency controller identity differs')
    base = ROOT / 'research/tier8_v2'
    corpus = base / 'evidence/deployment-sft-1024-02.json'
    data = artifact_path(json.loads(corpus.read_text())['output_file'])
    tokenizer = ROOT / 'weights/hf-tokenizers/sas-7b-q4'
    source = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) /
                           'weights/hf/Qwen--Qwen2.5-7B-Instruct')
    files = [Path(__file__), ROOT / 'scripts/frozen_head_loss.py',
             ROOT / 'scripts/tier8_v2_adapt.py', ROOT / 'scripts/tier8_v2_adapter_convert.py',
             ROOT / 'scripts/tier8_v2_posttrain_queue.py', ROOT / 'scripts/tier8_artifact_paths.py',
             ROOT / 'scripts/supervised_logits.py', ROOT / 'manifests/hf_snapshots.json',
             launch_file, queue_plan, corpus, data, base / 'evidence/hf-tokenizer-parity-02.json',
             *tokenizer.glob('*'), source / 'config.json', source / 'model.safetensors.index.json']
    files = [p for p in files if p.is_file()]
    files += list((ROOT / '.venv-training').glob('lib/python*/site-packages/accelerate/hooks.py'))
    files += list((ROOT / '.venv-training').glob('lib/python*/site-packages/accelerate/big_modeling.py'))
    versions = training_runtime()
    out.mkdir(parents=True)
    plan = {'kind': 'sas7b_two_update_offload_fit', 'out': str(out),
            'dependency': {'pid': launch['pid'], 'create_time': launch['create_time'],
                           'root': str(queue_plan.parent), 'plan': str(queue_plan)},
            'input_sha256': {str(p): sha(p) for p in files}, 'source_model': str(source),
            'policy': load_policy(), 'host_tree_cap_bytes': 10500000000,
            'runtime_versions': versions,
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'host_reserve_bytes': 1000000000, 'minimum_available_before_worker': 9000000000,
            'sampling_interval_seconds': .2,
            'scope': 'Training feasibility only; training memory is separate from the simulated8GB deployment cap. No full epoch, QA gain or novelty claim.'}
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
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import prepare_model_for_kbit_training, get_peft_model, LoraConfig
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
    data_path = base / 'deployment-sft-1024-02.json'
    data = json.loads(data_path.read_text())
    parity = json.loads((base / 'hf-tokenizer-parity-02.json').read_text())
    corpus = artifact_path(data['output_file'])
    if (not parity['pass'] or not parity['profiles']['sas-7b-q4']['pass'] or
            parity['transformers_version'] != transformers.__version__ or
            sha(corpus) != data['output_sha256'] or sha(corpus) != parity['dataset_sha256'] or
            sha(data_path) != parity['dataset_manifest_sha256']):
        raise ValueError('Require unchanged corpus and current-runtime parity')
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir), local_files_only=True)
    rows = [encode_example(tokenizer, json.loads(s), 'sas-7b-q4') for s in corpus.read_text().splitlines()]
    train = [r for r in rows if r['split'] == 'train']
    if len(train) != 661 or sum(r['split'] == 'validation' for r in rows) != 100:
        raise ValueError('Comparable actor corpus/splits differ')
    longest = max(train, key=lambda r: (len(r['input_ids']), r['source_id']))
    out = artifact_path(plan['out']) / 'fit'
    out.mkdir(exist_ok=False)
    def event(state, **fields):
        with (out / 'events.jsonl').open('a') as f:
            f.write(json.dumps({'state': state, 'time': time.time(), **fields}) + '\n'); f.flush()
    manifest = {'mode': 'fit', 'profile': '7b', 'purpose': 'drafter', 'seed': 42,
                'source_commit': plan['source_commit'],
                'input_sha256': plan['input_sha256'], 'policy': plan['policy'],
                'training_base': {'folder': str(source), 'artifacts': entries},
                'training_n': 661, 'validation_n': 100,
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
        model = AutoModelForCausalLM.from_pretrained(str(source), local_files_only=True,
            trust_remote_code=False, use_safetensors=True, low_cpu_mem_usage=True,
            quantization_config=quant, device_map=plan['policy']['device_map'],
            torch_dtype=torch.bfloat16, attn_implementation='sdpa')
        restore_cpu_matrices(model)
        model.config.use_cache = False
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                               gradient_checkpointing_kwargs={'use_reentrant': False})
        model = get_peft_model(model, LoraConfig(**plan['policy']['lora'], bias='none', task_type='CAUSAL_LM'))
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
        ids = torch.tensor([longest['input_ids']], device='cpu')
        labels = torch.tensor([longest['labels']], device='cuda')
        for step in [1, 2]:
            optimizer.zero_grad(set_to_none=True)
            embeddings = base_model.get_input_embeddings()(ids).to('cuda')
            with torch.autocast('cuda', dtype=torch.bfloat16):
                hidden = base_model.model(inputs_embeds=embeddings, use_cache=False).last_hidden_state
                loss = causal_frozen_head_loss(hidden.to(torch.bfloat16), base_model.lm_head.weight,
                                              labels, plan['policy']['vocabulary_block_size'])
            if not torch.isfinite(loss).item():
                raise ValueError('Nonfinite fit loss')
            loss.backward()
            norm = torch.nn.utils.clip_grad_norm_(params, 1.)
            if not torch.isfinite(norm).item() or norm.item() <= 0:
                raise ValueError('No finite nonzero adapter gradient')
            optimizer.step()
            if any(not torch.isfinite(p).all().item() for p in params):
                raise ValueError('Nonfinite adapter after update')
            event('update', step=step, loss=loss.item(), gradient_norm=norm.item(),
                  gpu_peak_allocated=torch.cuda.max_memory_allocated(),
                  gpu_peak_reserved=torch.cuda.max_memory_reserved(), host_rss=psutil.Process().memory_info().rss)
        changed = sum(not torch.equal(a, b.detach().cpu()) for a, b in zip(before, params))
        if not changed:
            raise ValueError('Adapter did not change')
        model.save_pretrained(str(out / 'adapter'), safe_serialization=True)
        summary = {'status': 'complete', 'mode': 'fit', 'optimizer_updates': 2,
                   'examples_processed': 2, 'changed_adapter_tensors': changed,
                   'trainable_parameters': sum(p.numel() for p in params),
                   'last_training_loss': loss.item(), 'validation_teacher_forced_loss': None,
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
                    rss = sum(p.memory_info().rss for p in [psutil.Process(), proc, *proc.children(recursive=True)] if p.is_running())
                except psutil.NoSuchProcess:
                    continue
                available = psutil.virtual_memory().available; peak = max(peak, rss)
                memory.write(json.dumps({'time': time.time(), 'tree_rss_bytes': rss,
                                         'host_available_bytes': available}) + '\n'); memory.flush()
                if rss > plan['host_tree_cap_bytes'] or available < plan['host_reserve_bytes']:
                    breach = True; os.killpg(child.pid, signal.SIGKILL); break
                time.sleep(plan['sampling_interval_seconds'])
            code = child.wait(); child = None
        record('worker_exited', exit_code=code, memory_breach=breach, peak_tree_rss_bytes=peak)
        if code or breach:
            raise RuntimeError('Offload fit failed; preserve evidence, no retry')
        result = json.loads((root / 'fit/summary.json').read_text())
        if result['status'] != 'complete' or result['optimizer_updates'] != 2 or result['changed_adapter_tensors'] <= 0:
            raise ValueError('Incomplete fit proof')
        record('complete', peak_tree_rss_bytes=peak, fit_only=True, measured_reasoning_gain=False)
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
    p.add_argument('--dependency-launch', default='research/tier8_v2/evidence/critic3b-posttrain-launch-02.json')
    p.add_argument('--plan'); p.add_argument('--worker', action='store_true')
    a = p.parse_args()
    if a.prepare:
        if not a.out or a.plan or a.worker:
            raise ValueError('Prepare requires only new out and dependency launch')
        prepare(artifact_path(a.out), artifact_path(a.dependency_launch))
    elif a.plan:
        plan_path = artifact_path(a.plan)
        worker(json.loads(plan_path.read_text())) if a.worker else controller(plan_path)
    else:
        raise ValueError('Prepare a new plan or run an existing frozen plan')


if __name__ == '__main__':
    main()
