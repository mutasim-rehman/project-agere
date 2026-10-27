"""Offline resident FP16-MAS/Q4-SAS lab evaluations with SSD evidence/resume.

Uses frozen existing financial reasoning/review code. No downloads, training,
GPU dependency, new source catalog, or synthetic-paper-result substitutions.
"""
import argparse
from contextlib import redirect_stderr, redirect_stdout
import datetime
import fcntl
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import threading
import time

from lab_tiers_common import ROOT, append, completed_cases, fingerprint, gguf_file_type, inside, read, run_id, sha, ssd_root, verify, write


def protocol():
    return read(ROOT / 'configs/lab_tiers/protocol.json')


def freeze_check():
    path = ROOT / 'configs/lab_tiers/freeze.json'
    if not path.is_file():
        raise ValueError('Lab execution is not sealed yet: the two8GB prompt evaluations/audits must finish first.')
    frozen = read(path)
    if frozen.get('status') != 'sealed_for_lab':
        raise ValueError('Incomplete study freeze')
    for relative, digest in frozen['code_sha256'].items():
        if sha(ROOT / relative) != digest:
            raise ValueError('Code/config differs from frozen lab protocol: ' + relative)
    return frozen


def model_entries(spec, tiers):
    result = {}
    for tier in tiers:
        for arm in ('sas', 'mas'):
            for model in spec['tiers'][str(tier)][arm].values():
                result[model['path']] = model
    return result


def verify_inputs(ssd, spec, tiers, cache):
    data = spec['dataset']
    for key in ('public', 'gold', 'demos'):
        verify(inside(ssd, data[key]), data[key + '_sha256'], cache)
    for relative, model in model_entries(spec, tiers).items():
        p = inside(ssd, relative)
        if p.stat().st_size != model['size_bytes']:
            raise ValueError('Model missing/truncated: ' + relative)
        expected_type = 1 if model['gguf_type'] == 'F16' else 15
        if gguf_file_type(p) != expected_type:
            raise ValueError('Model precision differs from declared arm: ' + relative)
        print('Verify model SHA256:', relative, flush=True)
        verify(p, model['sha256'], cache)


def environment_check():
    if sys.platform != 'linux' or platform.machine() != 'x86_64':
        raise ValueError('Offline runtime targets Ubuntu/Linux x86_64')
    import llama_cpp
    import numpy
    import psutil
    runtime = os.environ.get('AGERE_RUNTIME_ROOT')
    if not runtime or not os.environ.get('AGERE_PYTHON_LAUNCHER'):
        raise ValueError('Use bash scripts/lab_tiers.sh with the prepared offline runtime')
    runtime = Path(runtime).resolve()
    pin = read(ROOT / 'configs/lab_tiers/runtime_pin.json')
    if sha(runtime / 'manifest.json') != pin['manifest_sha256'] or not Path(llama_cpp.__file__).resolve().is_relative_to(runtime):
        raise ValueError('Inference imports differ from pinned offline runtime')
    flags = Path('/proc/cpuinfo').read_text().lower()
    missing = [x for x in ('avx2', 'fma', 'f16c', 'bmi2', 'sse4_2') if x not in flags]
    if missing:
        raise ValueError('Portable CPU build requires: ' + ', '.join(missing))
    if llama_cpp.__version__ != '0.3.16':
        raise ValueError('Use the pinned offline launcher, not another Python environment')
    model_name = re.search(r'^model name\s*:\s*(.+)$', Path('/proc/cpuinfo').read_text(), re.M)
    return {'python': sys.version, 'llama_cpp': llama_cpp.__version__, 'numpy': numpy.__version__,
        'psutil': psutil.__version__, 'platform': platform.platform(),
        'physical_ram_bytes': psutil.virtual_memory().total,
        'cpu_runtime': llama_cpp.llama_print_system_info().decode(), 'device': 'cpu', 'gpu_layers': 0,
        'runtime_manifest_sha256': pin['manifest_sha256'], 'cpu_model': model_name[1] if model_name else platform.processor(),
        'host_id_sha256': __import__('hashlib').sha256(platform.node().encode()).hexdigest()}


def preflight(ssd, tiers, require_freeze=True):
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = ssd / 'runs/lab_tiers_v1/preflight' / (stamp + '-' + str(os.getpid()))
    out.mkdir(parents=True)
    try:
        info = environment_check()
        spec = protocol()
        if require_freeze:
            freeze_check()
        for tier in tiers:
            if info['physical_ram_bytes'] < int(tier * 1e9 * .9):
                raise ValueError(f'Tier{tier} requires appropriate physical RAM; detected{info["physical_ram_bytes"]/1e9:.2f} GB')
        cache = {}
        verify_inputs(ssd, spec, tiers, cache)
        data = spec['dataset']
        packets = [json.loads(x) for x in inside(ssd, data['public']).read_text().splitlines()]
        if [x['id'] for x in packets] != data['ids'] or len(packets) != data['n']:
            raise ValueError('Frozen packet IDs differ')
        demo_groups = {x['source_id'].rsplit('/', 1)[0] for x in read(inside(ssd, data['demos']))['examples']}
        if demo_groups & set(data['report_groups']):
            raise ValueError('Demonstration/confirmation report overlap')
        report = {'status': 'passed', 'tiers': tiers, 'environment': info, 'verified_inputs': cache,
            'protocol_sha256': sha(ROOT / 'configs/lab_tiers/protocol.json'),
            'free_ssd_bytes': shutil.disk_usage(ssd).free, 'new_model_calls': 0}
        write(out / 'report.json', report)
        print('Preflight passed. Report:', out / 'report.json', flush=True)
        return report
    except BaseException as exc:
        write(out / 'failure.json', {'status': 'failed', 'reason': str(exc), 'new_model_calls': 0})
        raise


def snapshot(out, frozen):
    code = out / 'code'
    for relative in frozen['code_sha256']:
        target = code / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    # Include the freeze itself, whose content intentionally is not self-hashed.
    shutil.copyfile(ROOT / 'configs/lab_tiers/freeze.json', code / 'configs/lab_tiers/freeze.json')
    return code


def job_config(spec, tier, arm, profile):
    return {**spec['common'], **spec['profiles'][profile], 'arm': arm,
        'tier': tier, 'profile': profile, 'models': spec['tiers'][str(tier)][arm]}


def kill_worker(process):
    import psutil
    try:
        p = psutil.Process(process.pid)
        members = p.children(recursive=True) + [p]
        for member in members:
            member.terminate()
        _, alive = psutil.wait_procs(members, timeout=4)
        for member in alive:
            member.kill()
    except psutil.NoSuchProcess:
        pass


def live_identity(record):
    import psutil
    try:
        p = psutil.Process(record['pid'])
        return p.create_time() == record['create_time'] and p.is_running() and p.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, KeyError):
        return False


def monitor_job(ssd, out, code, job, cap, cache, spec):
    import psutil
    name = f'tier{job["tier"]}-{job["arm"]}-{job["profile"]}'
    folder = out / name
    folder.mkdir(exist_ok=True)
    manifest_path = folder / 'manifest.json'
    proposed = {'job': job, 'cap_bytes': cap, 'dataset': spec['dataset'],
        'device': 'cpu', 'residency': 'all declared model instances resident; use_mmap=False',
        'adapters': None, 'protocol_sha256': sha(code / 'configs/lab_tiers/protocol.json')}
    if manifest_path.exists() and read(manifest_path) != proposed:
        raise ValueError('Resume would change job/cap/data')
    if (folder / 'summary.json').exists():
        summary = read(folder / 'summary.json')
        records = completed_cases(folder / 'cases.jsonl', spec['dataset']['ids'])
        if summary.get('status') != 'complete' or len(records) != spec['dataset']['n'] or sha(folder / 'cases.jsonl') != summary['cases_sha256']:
            raise ValueError('Completed job evidence differs')
        print('Already complete:', name, flush=True)
        return
    attempts = sorted(folder.glob('attempt-*'))
    for attempt in attempts:
        state = read(attempt / 'state.json') if (attempt / 'state.json').exists() else {}
        if live_identity(state.get('worker', {})):
            raise ValueError('An existing worker is still live; do not overlap/restart it: ' + str(attempt))
        if state.get('memory_breach') or state.get('swap_breach'):
            raise ValueError('A memory breach invalidated this run; preserve it and use a new run ID')
        if state.get('status') in ('starting', 'running'):
            # A killed controller cannot write its final peak. Recover only
            # durable sampled evidence, retaining the original state verbatim.
            samples = []
            memory_path = attempt / 'memory.jsonl'
            if not memory_path.exists():
                memory_path.touch()
            if memory_path.exists():
                lines = memory_path.read_bytes().splitlines(keepends=True)
                valid = []
                for index, line in enumerate(lines):
                    try:
                        sample = json.loads(line)
                    except (ValueError, UnicodeDecodeError):
                        if index != len(lines)-1 or line.endswith(b'\n'):
                            raise ValueError('Corrupted historical memory samples')
                        memory_path.with_name('memory.jsonl.torn-' + str(time.time_ns())).write_bytes(line)
                        memory_path.write_bytes(b''.join(valid))
                        break
                    if sample['tree_rss_bytes'] > cap or sample.get('tree_swap_bytes', 0):
                        raise ValueError('Historical memory/swap breach invalidated this run')
                    samples.append(sample)
                    valid.append(line)
            write(attempt / ('state-before-recovery-' + str(time.time_ns()) + '.json'), state)
            state.update(status='controller_lost_recovered',
                peak_tree_rss_bytes=max((s['tree_rss_bytes'] for s in samples), default=0),
                recovery_time=time.time(), recovery_scope='Durable samples only; no claim about unsampled RSS')
            write(attempt / 'state.json', state)
    prior = completed_cases(folder / 'cases.jsonl', spec['dataset']['ids'], repair_tail=True)
    verify_inputs(ssd, spec, [job['tier']], cache)
    if psutil.virtual_memory().available < cap + 1000000000:
        raise ValueError('Available RAM fell below frozen paired cap plus1GB reserve; free RAM and resume same command')
    if not manifest_path.exists():
        write(manifest_path, proposed)
    attempt = folder / f'attempt-{len(attempts)+1:04d}'
    attempt.mkdir()
    launcher = os.environ.get('AGERE_PYTHON_LAUNCHER', sys.executable)
    command = [launcher, str(code / 'scripts/lab_tiers.py'), '_worker', '--ssd', str(ssd),
        '--job-dir', str(folder), '--attempt', str(attempt)]
    state = {'status': 'starting', 'completed_before': len(prior), 'memory_breach': False, 'swap_breach': False,
        'controller': {'pid': os.getpid(), 'create_time': psutil.Process().create_time()}, 'command': command}
    write(attempt / 'state.json', state)
    print('Start:', name, f'completed={len(prior)}/{spec["dataset"]["n"]} cap={cap/1e9:.3f} GB', flush=True)
    peak = 0
    process = None
    try:
        with (attempt / 'worker.log').open('w') as log, (attempt / 'memory.jsonl').open('w') as memory:
            lock_fd = os.environ.get('AGERE_WORKLOAD_LOCK_FD')
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                pass_fds=(int(lock_fd),) if lock_fd else ())
            state.update(status='running', worker={'pid': process.pid, 'create_time': psutil.Process(process.pid).create_time()})
            write(attempt / 'state.json', state)
            while process.poll() is None:
                rss = 0
                swap = 0
                members = [psutil.Process()]
                try:
                    members += [psutil.Process(process.pid)] + psutil.Process(process.pid).children(recursive=True)
                except psutil.NoSuchProcess:
                    pass
                for p in members:
                    try:
                        rss += p.memory_info().rss
                        status = Path(f'/proc/{p.pid}/status').read_text()
                        match = re.search(r'^VmSwap:\s+(\d+)\s+kB', status, re.M)
                        swap += int(match[1])*1024 if match else 0
                    except (psutil.NoSuchProcess, FileNotFoundError):
                        pass
                peak = max(peak, rss)
                memory.write(json.dumps({'time': time.time(), 'tree_rss_bytes': rss, 'tree_swap_bytes': swap}) + '\n')
                memory.flush()
                if rss > cap or swap:
                    state['memory_breach'] = rss > cap
                    state['swap_breach'] = bool(swap)
                    kill_worker(process)
                    break
                time.sleep(.2)
            rc = process.wait()
        state.update(status='memory_breach' if state['memory_breach'] else 'swap_breach' if state['swap_breach'] else 'exited', exit_code=rc,
            peak_tree_rss_bytes=peak, ended=time.time())
        write(attempt / 'state.json', state)
        if rc or state['memory_breach'] or state['swap_breach']:
            raise ValueError('Worker failed; inspect ' + str(attempt / 'worker.log'))
        records = completed_cases(folder / 'cases.jsonl', spec['dataset']['ids'])
        if len(records) != spec['dataset']['n']:
            raise ValueError('Worker exited without all frozen cases')
        verify_inputs(ssd, spec, [job['tier']], cache)
        frozen = read(code / 'configs/lab_tiers/freeze.json')
        for relative, digest in frozen['code_sha256'].items():
            if sha(code / relative) != digest:
                raise ValueError('Archived worker source changed during job')
        all_peaks = [read(p / 'state.json').get('peak_tree_rss_bytes', 0) for p in folder.glob('attempt-*')]
        result = counts(records)
        result.update(status='complete', n=len(records), expected=spec['dataset']['n'],
            cap_bytes=cap, sampled_peak_tree_rss_bytes=max(all_peaks),
            cases_sha256=sha(folder / 'cases.jsonl'), attempts=len(all_peaks), resumed_cases=len(prior),
            memory_guard='sampled RSS/no-swap monitor including controller; no claim of a hard cgroup limit')
        write(folder / 'summary.json', result)
        print('Complete:', name, json.dumps(result['full']), flush=True)
    except BaseException:
        if process is not None and process.poll() is None:
            kill_worker(process)
        state.update(status='memory_breach' if state.get('memory_breach') else 'interrupted_or_failed',
            peak_tree_rss_bytes=peak, ended=time.time())
        write(attempt / 'state.json', state)
        raise


def counts(records):
    result = {'full': {}, 'initial': {}, 'candidate_repairs': {}}
    for metric in ('case_success', 'raw_execution_match'):
        correct = sum(r['delivered'] and r['score'][metric] for r in records)
        wrong = sum(r['delivered'] and not r['score'][metric] for r in records)
        result['full'][metric] = {'correct_delivered': correct, 'wrong_delivered': wrong,
            'withheld': len(records) - correct - wrong}
        result['initial'][metric] = sum(r['initial_score'][metric] for r in records)
        result['candidate_repairs'][metric] = {
            'gains': sum(not r['initial_score'][metric] and r['score'][metric] for r in records),
            'regressions': sum(r['initial_score'][metric] and not r['score'][metric] for r in records)}
    result['generated_tokens'] = sum(r['tokens'] for r in records)
    result['prompt_tokens'] = sum(s['prompt_tokens'] for r in records for s in r['stages'])
    result['inference_seconds'] = sum(s['seconds'] for r in records for s in r['stages'])
    result['truncated_stages'] = sum(s['finish_reason'] == 'length' for r in records for s in r['stages'])
    result['context_or_budget_skips'] = sum(s['finish_reason'] == 'no_context_or_budget' for r in records for s in r['stages'])
    result['repair_attempts'] = sum(bool(r.get('repair_attempted')) for r in records)
    result['source_supported_final_programs'] = sum(bool(r['score'].get('source_supported_program')) for r in records)
    return result


def worker(ssd, folder, attempt):
    from llama_cpp import Llama, LlamaGrammar
    from tier8_v2_natural_run import Models as ExistingModels
    from tier8_v2_financial_pipeline import run_financial, evaluate_financial
    manifest = read(folder / 'manifest.json')
    controller = read(attempt / 'state.json')['controller']
    stop_watch = threading.Event()
    def watch_parent():
        while not stop_watch.wait(.5):
            if not live_identity(controller):
                write(attempt / 'orphan-detected.json', {'reason': 'Controller identity disappeared; no unmonitored continuation', 'time': time.time()})
                os._exit(75)
    threading.Thread(target=watch_parent, daemon=True).start()
    job, data = manifest['job'], manifest['dataset']
    packets = [json.loads(x) for x in inside(ssd, data['public']).read_text().splitlines()]
    gold = {r['id']: r for r in read(inside(ssd, data['gold']))}
    demos = read(inside(ssd, data['demos']))['examples'][:job['demos']]
    done = completed_cases(folder / 'cases.jsonl', data['ids'])
    class Models(ExistingModels):
        def __init__(self):
            self.context, self.grammar = job['context'], LlamaGrammar
            self.models, self.adapter_applications = {}, {}
            self.adapter_info = self.verifier_adapter_info = None
            for role, model in job['models'].items():
                self.models[role] = Llama(model_path=str(inside(ssd, model['path'])),
                    n_ctx=job['context'], n_gpu_layers=0, n_threads=job['threads'], n_threads_batch=job['threads'],
                    n_batch=64, n_ubatch=64, seed=42, use_mmap=False, verbose=False)
                print('Resident model loaded:', role, model['path'], flush=True)
    models = Models()
    try:
        for p in packets[len(done):]:
            sink = lambda event: append(attempt / 'stages.jsonl', {'time': time.time(), **event})
            row = run_financial(p, models, job['arm'], job['repair'], event_sink=sink,
                representation=job['program_mode'], unit_mode=job['unit_mode'], selector=job['selector'],
                causal_mode=job['causal_mode'], catalog_style=job['catalog_style'], demonstrations=demos,
                analysis_tokens=job['analysis_tokens'], planner=job['planner'], critic_protocol=job['critic_protocol'])
            row['initial_score'] = evaluate_financial(gold[p['id']], row['initial_answer'], row['initial_execution'])
            row['score'] = evaluate_financial(gold[p['id']], row['answer'], row['execution'])
            row['attempt'] = attempt.name
            row['completed_time'] = time.time()
            if row['tokens'] > 2048:
                raise ValueError('Output-token ceiling exceeded')
            if not live_identity(controller):
                raise ValueError('Controller disappeared before case checkpoint')
            append(folder / 'cases.jsonl', row)
            done.append(row)
            write(attempt / 'progress.json', {'completed': len(done), 'expected': len(packets), 'last_case': p['id'], 'time': time.time()})
            print(json.dumps({'completed': len(done), 'expected': len(packets), 'id': p['id'],
                'reported_correct': row['score']['case_success'], 'delivered': row['delivered'], 'tokens': row['tokens']}), flush=True)
    finally:
        stop_watch.set()
        for model in models.models.values():
            model.close()


def run(ssd, identifier, tiers):
    import psutil
    frozen = freeze_check()
    spec = protocol()
    out = ssd / 'runs/lab_tiers_v1' / run_id(identifier)
    out.mkdir(parents=True, exist_ok=True)
    # Same lock used by8GB jobs; a live workload must never be duplicated.
    lock = (ssd / 'runs/tier8_external.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    # A worker keeps the same open-file lock alive if the controller is killed.
    # Thus a different run ID cannot overlap an orphaned native model process.
    os.environ['AGERE_WORKLOAD_LOCK_FD'] = str(lock.fileno())
    for existing in out.glob('tier*/attempt-*/state.json'):
        if live_identity(read(existing).get('worker', {})):
            raise ValueError('An owned worker is already live: ' + str(existing))
    state_path = out / 'state.json'
    state = {'status': 'preflight', 'tiers': tiers, 'time': time.time(),
        'controller': {'pid': os.getpid(), 'create_time': psutil.Process().create_time()}}
    write(state_path, state)
    cache = {}
    try:
        environment = environment_check()
        for tier in tiers:
            if environment['physical_ram_bytes'] < tier * 1e9 * .9:
                raise ValueError('Insufficient physical RAM for tier' + str(tier))
        verify_inputs(ssd, spec, tiers, cache)
        manifest_path = out / 'manifest.json'
        identity = {'protocol': spec, 'freeze': frozen, 'tiers': tiers, 'environment': environment,
            'verified_inputs_at_start': dict(cache)}
        if manifest_path.exists():
            previous = read(manifest_path)
            if any(previous[k] != identity[k] for k in ('protocol', 'freeze', 'tiers')):
                raise ValueError('Changed protocol/source/tier list; use a new run ID')
            for k in ('python', 'llama_cpp', 'numpy', 'psutil', 'cpu_runtime', 'runtime_manifest_sha256', 'cpu_model', 'host_id_sha256', 'physical_ram_bytes'):
                if previous['environment'][k] != environment[k]:
                    raise ValueError('Runtime changed across resume')
            code = out / 'code'
        else:
            code = snapshot(out, frozen)
            write(manifest_path, identity)
        for relative, digest in frozen['code_sha256'].items():
            if sha(code / relative) != digest:
                raise ValueError('Archived code changed')
        for tier in tiers:
            cap_file = out / f'tier{tier}-cap.json'
            if cap_file.exists():
                cap = read(cap_file)['cap_bytes']
            else:
                available = psutil.virtual_memory().available
                cap = min(spec['tiers'][str(tier)]['nominal_cap_bytes'], available - 1000000000)
                minimum = max(sum(x['size_bytes'] for x in spec['tiers'][str(tier)][arm].values()) for arm in ('sas', 'mas')) + 500000000
                if cap < minimum:
                    raise ValueError('Free more RAM before starting this tier; insufficient common resident budget')
                write(cap_file, {'cap_bytes': cap, 'nominal_cap_bytes': spec['tiers'][str(tier)]['nominal_cap_bytes'],
                    'physical_ram_bytes': environment['physical_ram_bytes'], 'available_before_tier': available,
                    'reserve_bytes': 1000000000, 'same_cap_all_arms_profiles': True})
            arms = ('sas', 'mas') if tier == 16 else ('mas', 'sas')
            for profile in spec['profiles']:
                for arm in arms:
                    state.update(status='running', current_job=f'tier{tier}-{arm}-{profile}', time=time.time())
                    write(state_path, state)
                    monitor_job(ssd, out, code, job_config(spec, tier, arm, profile), cap, cache, spec)
        state.update(status='complete', analysis_status='running', time=time.time())
        write(state_path, state)
        print('All neural evaluations complete; replay analysis starts:', out, flush=True)
        launcher = os.environ.get('AGERE_PYTHON_LAUNCHER', sys.executable)
        subprocess.run([launcher, str(code / 'scripts/lab_tiers.py'), 'analyze', '--ssd', str(ssd),
            '--run-id', identifier, '--tiers', ','.join(map(str, tiers))], check=True)
        state.update(analysis_status='complete', time=time.time())
        write(state_path, state)
        print('Evaluations and audited analysis complete:', out, flush=True)
    except BaseException as exc:
        state.update(status='interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed', reason=str(exc), time=time.time())
        write(state_path, state)
        raise
    finally:
        os.environ.pop('AGERE_WORKLOAD_LOCK_FD', None)
        lock.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('preflight', 'run', 'start', 'status', 'analyze', 'export', '_worker'))
    p.add_argument('--ssd')
    p.add_argument('--tiers', default='16,32')
    p.add_argument('--run-id', default='lab-main-v1')
    p.add_argument('--job-dir')
    p.add_argument('--attempt')
    args = p.parse_args()
    ssd = ssd_root(args.ssd)
    tiers = [int(x) for x in args.tiers.split(',')]
    if not tiers or len(tiers) != len(set(tiers)) or any(x not in (16, 32) for x in tiers):
        p.error('Use --tiers16, --tiers32 or --tiers16,32')
    identifier = run_id(args.run_id)
    out = ssd / 'runs/lab_tiers_v1' / identifier
    if args.command == '_worker':
        folder, attempt = Path(args.job_dir).resolve(), Path(args.attempt).resolve()
        if not folder.is_relative_to(ssd / 'runs/lab_tiers_v1') or not attempt.is_relative_to(folder):
            raise ValueError('Worker output escapes run directory')
        worker(ssd, folder, attempt)
    elif args.command == 'status':
        status = read(out / 'state.json') if (out / 'state.json').exists() else {'status': 'not_started'}
        status['controller_live'] = live_identity(status.get('controller', {}))
        print(json.dumps(status, indent=2))
        for progress in sorted(out.glob('tier*/attempt-*/progress.json')):
            print(progress.parent.parent.name, progress.parent.name, json.dumps(read(progress)))
    elif args.command == 'start':
        import psutil
        if (out / 'state.json').exists() and live_identity(read(out / 'state.json').get('controller', {})):
            raise ValueError('Controller already running; use status')
        freeze_check()
        out.mkdir(parents=True, exist_ok=True)
        launcher = os.environ.get('AGERE_PYTHON_LAUNCHER', sys.executable)
        with (out / 'console.log').open('a') as log:
            child = subprocess.Popen([launcher, str(Path(__file__).resolve()), 'run', '--ssd', str(ssd),
                '--tiers', args.tiers, '--run-id', identifier], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        print('Started controller PID', child.pid, '\nLog:', out / 'console.log', '\nRun ID:', identifier)
    elif args.command in ('analyze', 'export'):
        archived = out / 'code/scripts/lab_tiers.py'
        if archived.is_file() and Path(__file__).resolve() != archived.resolve():
            launcher = os.environ.get('AGERE_PYTHON_LAUNCHER', sys.executable)
            os.execv(launcher, [launcher, str(archived), args.command, '--ssd', str(ssd),
                '--run-id', identifier, '--tiers', args.tiers])
        from lab_tiers_analyze import analyze, export
        (analyze if args.command == 'analyze' else export)(ssd, out)
    else:
        if args.command == 'run':
            def terminate(signum, frame):
                raise KeyboardInterrupt('Controller terminated; retain checkpoints')
            signal.signal(signal.SIGTERM, terminate)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        log_dir = ssd / 'runs/lab_tiers_v1/commands'
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / f'{stamp}-{os.getpid()}-{args.command}.log').open('w') as log:
            class Tee:
                def write(self, value):
                    sys.__stdout__.write(value); log.write(value); log.flush()
                def flush(self):
                    sys.__stdout__.flush(); log.flush()
            with redirect_stdout(Tee()), redirect_stderr(Tee()):
                if args.command == 'preflight':
                    preflight(ssd, tiers)
                else:
                    run(ssd, identifier, tiers)


if __name__ == '__main__':
    main()
