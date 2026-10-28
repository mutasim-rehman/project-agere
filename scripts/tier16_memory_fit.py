"""Engineering resident-load probe, no benchmark questions or accuracy claims."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import threading

from lab_tiers_common import ROOT, append, read, sha, ssd_root, write


def load_probe(ssd, arm, out, context):
    import psutil
    controller = json.loads(os.environ['AGERE_FIT_CONTROLLER'])
    def watch_controller():
        while True:
            try:
                parent = psutil.Process(controller['pid'])
                if parent.create_time() != controller['create_time'] or parent.status() == psutil.STATUS_ZOMBIE:
                    os._exit(75)
            except psutil.NoSuchProcess:
                os._exit(75)
            time.sleep(.2)
    threading.Thread(target=watch_controller, daemon=True).start()
    from llama_cpp import Llama
    spec = read(ROOT / 'configs/lab_tiers/protocol.json')
    models = {}
    try:
        for role, entry in spec['tiers']['16'][arm].items():
            print('Loading resident role', role, flush=True)
            models[role] = Llama(model_path=str(ssd / entry['path']), n_ctx=context,
                n_gpu_layers=0, n_threads=8, n_threads_batch=8, n_batch=64,
                n_ubatch=64, seed=42, use_mmap=False, verbose=False)
        print('All roles resident; generation probe starts', flush=True)
        results = []
        for role, model in models.items():
            # Long generic input exercises prompt batches without exposing the
            # sealed financial benchmark. All MAS roles stay resident throughout.
            unit = 'Read the following neutral engineering test sentence. '
            target = context - 256
            repetitions = target // len(model.tokenize(unit.encode()))
            prompt = '<|im_start|>user\n' + unit * repetitions
            prompt += '\nReturn the word ready.<|im_end|>\n<|im_start|>assistant\n'
            result = model.create_completion(prompt, max_tokens=8, temperature=0, top_k=1, seed=42,
                repeat_penalty=1, stop=['<|im_end|>'])
            results.append({'role': role, 'usage': result['usage'], 'text': result['choices'][0]['text']})
            print('Role completed', role, result['usage'], flush=True)
        write(out / (arm + '-worker-result.json'), {'status': 'passed', 'results': results,
            'context': context, 'all_models_resident': True})
        time.sleep(1)
    finally:
        for model in models.values():
            model.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--worker', choices=['sas', 'mas'])
    p.add_argument('--out', required=True)
    p.add_argument('--context', type=int, default=8192)
    args = p.parse_args()
    ssd = ssd_root()
    out = Path(args.out).resolve()
    if not out.is_relative_to(ssd / 'runs'):
        raise ValueError('Probe evidence must stay on SSD')
    if args.worker:
        load_probe(ssd, args.worker, out, args.context)
        return
    import psutil
    if out.exists():
        raise ValueError('Preserve old probe; choose new evidence directory')
    lock = (ssd / 'runs/tier8_external.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    out.mkdir(parents=True)
    (out / 'probe-source.py').write_bytes(Path(__file__).read_bytes())
    os.environ['AGERE_FIT_CONTROLLER'] = json.dumps({'pid': os.getpid(), 'create_time': psutil.Process().create_time()})
    cap = 11500000000
    spec = read(ROOT / 'configs/lab_tiers/protocol.json')
    write(out / 'manifest.json', {'cap_bytes': cap, 'protocol': spec,
        'script_sha256': sha(Path(__file__)), 'initial_available_bytes': psutil.virtual_memory().available,
        'context': args.context,
        'scope': 'Engineering probe only. Near-context-length neutral input, eight output tokens per role. Not full benchmark/worst-case/product validation.'})
    checked = set()
    for arm in ['sas', 'mas']:
        for entry in spec['tiers']['16'][arm].values():
            if entry['path'] not in checked:
                if sha(ssd / entry['path']) != entry['sha256']:
                    raise ValueError('Model hash changed')
                checked.add(entry['path'])
        launcher = os.environ.get('AGERE_PYTHON_LAUNCHER', sys.executable)
        peak, failure, process = 0, None, None
        try:
            with (out / (arm + '-worker.log')).open('x') as log:
                process = subprocess.Popen([launcher, str(Path(__file__).resolve()), '--worker', arm,
                    '--out', str(out), '--context', str(args.context)], stdout=log, stderr=subprocess.STDOUT,
                    start_new_session=True, pass_fds=(lock.fileno(),))
                while process.poll() is None:
                    members = [psutil.Process()]
                    try:
                        child = psutil.Process(process.pid)
                        members += [child] + child.children(recursive=True)
                    except psutil.NoSuchProcess:
                        pass
                    rss, swap = 0, 0
                    for member in members:
                        try:
                            rss += member.memory_info().rss
                            for line in Path(f'/proc/{member.pid}/status').read_text().splitlines():
                                if line.startswith('VmSwap:'):
                                    swap += int(line.split()[1])*1024
                        except (psutil.NoSuchProcess, FileNotFoundError):
                            pass
                    available = psutil.virtual_memory().available
                    peak = max(peak, rss)
                    append(out / (arm + '-memory.jsonl'), {'time': time.time(), 'tree_rss_bytes': rss,
                        'tree_swap_bytes': swap, 'host_available_bytes': available})
                    if rss > cap or swap or available < 256000000:
                        failure = 'rss_cap' if rss > cap else 'swap' if swap else 'host_headroom'
                        os.killpg(process.pid, signal.SIGTERM)
                        break
                    time.sleep(.1)
                try:
                    rc = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    rc = process.wait()
            result = {'status': 'passed' if rc == 0 and failure is None else 'failed',
                'sampled_peak_tree_rss_bytes': peak, 'cap_bytes': cap, 'failure': failure,
                'exit_code': rc, 'scope': 'Sampled engineering trajectory, not a hard limit or worst-case bound.'}
            write(out / (arm + '-summary.json'), result)
            print(arm, json.dumps(result), flush=True)
            if result['status'] != 'passed':
                raise ValueError('Engineering fit probe failed: ' + str(out))
        finally:
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    write(out / 'summary.json', {'status': 'passed', 'cap_bytes': cap, 'arms': ['mas', 'sas'],
        'new_research_evaluation_calls': 0, 'novelty_established': False})


if __name__ == '__main__':
    main()
