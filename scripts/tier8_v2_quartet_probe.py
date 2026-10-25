"""Frozen training-source quartet selection and monitored greedy critic probe.

Same192-token binary-review protocol as deployment, no forced label prefix or
gold in model input. Discovery only: annotated programs, not natural QA errors.
Complete quartets and one per report, selected before either neural outcome.
"""
import argparse
from collections import Counter, defaultdict
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
from financial_review_protocol import BINARY_SCHEMA
from tier8_artifact_paths import artifact_path
from tier8_v2_adapter_runtime import load_adapter, load_critic_adapter
from tier8_v2_posttrain_queue import sha, write
from tier8_v2_run import MODEL_FILES, verified_models

ROOT = Path(__file__).resolve().parents[1]
CAP = 6400000000


def select_training(rows, count=8):
    groups = defaultdict(list)
    for row in rows:
        if row['split'] == 'train':
            groups[row['quartet_id']].append(row)
    selected, reports = [], set()
    for key, quartet in sorted(groups.items()):
        if len(quartet) != 4 or len({r['report_group'] for r in quartet}) != 1:
            raise ValueError('Incomplete or cross-report quartet')
        report = quartet[0]['report_group']
        if report in reports:
            continue
        selected.extend(sorted(quartet, key=lambda r: r['source_id']))
        reports.add(report)
        if len(reports) == count:
            break
    if len(selected) != count * 4:
        raise ValueError('Insufficient distinct training reports')
    return selected


def prepare(source, out):
    manifest = json.loads((source / 'manifest.json').read_text())
    audit = json.loads((source / 'audit04.json').read_text())
    data = artifact_path(manifest['output_file'])
    if (not audit['pass'] or sha(data) != manifest['output_sha256'] or sha(data) != audit['dataset_sha256']
            or sha(source / 'manifest.json') != audit['dataset_manifest_sha256']
            or not audit['source_question_program_and_union_verified']
            or not audit['actual_model_prompt_binding_verified'] or audit['conflicting_identical_prompt_labels'] != 0):
        raise ValueError('Require completed canonical quartet audit')
    rows = select_training([json.loads(s) for s in data.read_text().splitlines()])
    out.mkdir(parents=True, exist_ok=False)
    selected = out / 'examples.jsonl'
    selected.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    write(out / 'selection.json', {'status': 'prepared_not_inferred', 'n': len(rows), 'n_quartets': 8, 'n_reports': 8,
        'source_sha256': sha(Path(__file__)), 'source_dataset_sha256': sha(data), 'output_sha256': sha(selected),
        'source_manifest': str(source / 'manifest.json'), 'source_manifest_sha256': sha(source / 'manifest.json'),
        'source_audit': str(source / 'audit04.json'), 'source_audit_sha256': sha(source / 'audit04.json'),
        'quartet_ids': sorted({r['quartet_id'] for r in rows}), 'report_groups': sorted({r['report_group'] for r in rows}),
        'selection': 'Training split only; ascending existing seed42 quartet SHA, first8 distinct reports; keep all4 cells. Identical inputs for both arms. No neural outcome used.',
        'inference': {'context': 4096, 'maximum_generated_tokens_per_review': 192, 'temperature': 0, 'top_k': 1,
                      'repeat_penalty': 1, 'seed': 42, 'grammar': BINARY_SCHEMA, 'forced_prefix': False},
        'decision_rule': 'If BOTH current policies achieve at least30/32 exact PASS/FAIL labels AND at least6/8 completely exact quartets, do not add a continuation stage solely for this family. Otherwise investigate a small matched current-extended-mutation versus crossed-negative continuation; natural held-out-report utility must decide adoption.',
        'limits': 'Small training-source discovery probe. Models have seen original source positives; crossed inputs are new. Not untouched validation, natural errors, calibrated risk or useful novelty.'})


def selected_rows(directory):
    selection = json.loads((directory / 'selection.json').read_text())
    data = directory / 'examples.jsonl'
    if sha(data) != selection['output_sha256']:
        raise ValueError('Pilot data changed')
    for prefix in ('source_manifest', 'source_audit'):
        if sha(artifact_path(selection[prefix])) != selection[prefix + '_sha256']:
            raise ValueError('Pilot construction provenance changed')
    rows = [json.loads(s) for s in data.read_text().splitlines()]
    original = json.loads(artifact_path(selection['source_manifest']).read_text())
    canonical_data = artifact_path(original['output_file'])
    if sha(canonical_data) != selection['source_dataset_sha256'] or sha(canonical_data) != original['output_sha256']:
        raise ValueError('Canonical quartet data changed')
    expected = select_training([json.loads(s) for s in canonical_data.read_text().splitlines()])
    if rows != expected:
        raise ValueError('Selection is not the exact declared training-only subset')
    if (len(rows) != 32 or len({r['source_id'] for r in rows}) != 32
            or {r['split'] for r in rows} != {'train'} or len({r['report_group'] for r in rows}) != 8
            or sorted({r['quartet_id'] for r in rows}) != selection['quartet_ids']):
        raise ValueError('Pilot coverage/split differs')
    return selection, rows


def analyze(rows, responses):
    target = {r['source_id']: r for r in rows}
    saved = {r['source_id']: r for r in responses}
    if not rows or len(target) != len(rows) or len(saved) != len(responses) or set(saved) != set(target):
        raise ValueError('Unmatched/duplicate probe outputs')
    verdicts, exact, gate, groups = Counter(), {}, {}, defaultdict(list)
    for key, row in target.items():
        response = saved[key]
        if response['prompt_sha256'] != hashlib.sha256(row['prompt'].encode()).hexdigest():
            raise ValueError('Scored prompt changed')
        value = response['verdict']
        if value not in ('PASS', 'FAIL', 'UNKNOWN', 'UNPARSED'):
            raise ValueError('Invalid saved verdict')
        try:
            decoded = json.loads(response['response'])
        except json.JSONDecodeError:
            decoded = None
        valid = isinstance(decoded, dict) and set(decoded) == {'verdict'} and decoded['verdict'] in ('PASS', 'FAIL', 'UNKNOWN')
        if value != (decoded['verdict'] if valid else 'UNPARSED'):
            raise ValueError('Saved verdict differs from actual response text')
        if (type(response['prompt_tokens']) is not int or not 0 < response['prompt_tokens'] <= 4096 - 200
                or type(response['generated_tokens']) is not int or not 0 <= response['generated_tokens'] <= 192
                or response['finish_reason'] not in ('stop', 'length')):
            raise ValueError('Invalid actual usage or finish reason')
        if 'tokenization' in row:
            profile = response.get('profile')
            if profile not in row['tokenization'] or response['prompt_tokens'] != row['tokenization'][profile]['prompt_tokens']:
                raise ValueError('Saved usage differs from pinned tokenizer prefix')
        verdicts[value] += 1
        exact[key] = value == row['target']['verdict']
        gate[key] = (value == 'PASS') == (row['target']['verdict'] == 'PASS')
        groups[row['quartet_id']].append(key)
    if any(len(ids) != 4 for ids in groups.values()):
        raise ValueError('Incomplete quartet outputs')
    return {'n': len(rows), 'n_quartets': len(groups), 'n_reports': len({r['report_group'] for r in rows}),
        'exact_label_correct': sum(exact.values()), 'exact_label_accuracy': sum(exact.values()) / len(rows),
        'gate_correct': sum(gate.values()), 'gate_accuracy': sum(gate.values()) / len(rows),
        'complete_exact_quartets': sum(all(exact[i] for i in ids) for ids in groups.values()),
        'complete_gate_quartets': sum(all(gate[i] for i in ids) for ids in groups.values()),
        'verdict_counts': dict(verdicts),
        'reference_accepts': sum(saved[i]['verdict'] == 'PASS' for i, r in target.items() if r['target']['verdict'] == 'PASS'),
        'cross_negative_accepts': sum(saved[i]['verdict'] == 'PASS' for i, r in target.items() if r['target']['verdict'] == 'FAIL'),
        'prompt_tokens': sum(r['prompt_tokens'] for r in responses),
        'generated_tokens': sum(r['generated_tokens'] for r in responses),
        'truncated_reviews': sum(r['finish_reason'] == 'length' for r in responses),
        'recorded_inference_seconds': sum(r['seconds'] for r in responses),
        'limits': 'Exact label metric treats UNKNOWN/unparsed as incorrect; gate metric treats them as nonaccept, not explicit correct negative judgments. Training-source discovery, not natural QA or confirmation.'}


def worker(args):
    import fcntl
    from llama_cpp import Llama, LlamaGrammar
    lock = artifact_path(Path(os.environ['AGERE_SSD_ROOT']) / 'runs/tier8_external.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    directory, out = artifact_path(args.selection), artifact_path(args.out)
    selection, rows = selected_rows(directory)
    info = load_adapter(args.adapter, 'sas', '3b-q4') if args.arm == 'sas' else load_critic_adapter(args.adapter, '3b')
    proof_root = artifact_path(args.proof)
    proof, summary = json.loads((proof_root / 'proof.json').read_text()), json.loads((proof_root / 'summary.json').read_text())
    if (not proof['pass'] or proof['adapter']['sha256'] != info['sha256'] or summary['status'] != 'complete'
            or summary['exit_code'] != 0 or summary['cap_bytes'] != CAP or summary['peak_tree_rss_bytes'] > CAP):
        raise ValueError('Require actual successful intended-adapter application proof')
    models = verified_models(args.arm, verifier_model='3b', drafter_model='3b-q4', use_selector=False, weights_root=args.weights_root)
    filename = MODEL_FILES['sas']['sas'] if args.arm == 'sas' else 'qwen2.5-3b-instruct-q4_k_m.gguf'
    model = Llama(model_path=str(artifact_path(args.weights_root) / filename), n_ctx=4096, n_gpu_layers=0,
        n_threads=8, n_threads_batch=8, n_batch=64, n_ubatch=64, seed=42, use_mmap=False, verbose=False,
        logits_all=False, lora_path=str(artifact_path(info['file'])), lora_scale=1.0)
    responses = []
    try:
        if not getattr(model, '_lora_adapter', None):
            raise ValueError('Missing actual adapter handle')
        write(out / 'policy.json', {'arm': args.arm, 'adapter': info, 'proof_sha256': sha(proof_root / 'proof.json'),
            'models': models, 'selection_sha256': sha(directory / 'selection.json'), 'inference': selection['inference']})
        grammar = LlamaGrammar.from_json_schema(json.dumps(BINARY_SCHEMA), verbose=False)
        with (out / 'responses.jsonl').open('x') as trace:
            for row in rows:
                model.reset()
                tokens = completion_tokens(model, row['prompt'])
                if len(tokens) + 192 + 8 > 4096:
                    raise ValueError('Review lacks full declared context reserve')
                started = time.monotonic()
                result = model.create_completion(row['prompt'], max_tokens=192, temperature=0, top_k=1,
                    repeat_penalty=1, seed=42, grammar=grammar, stop=['<|im_end|>'])
                choice, usage = result['choices'][0], result['usage']
                if usage['prompt_tokens'] != len(tokens):
                    raise ValueError('Actual prompt usage differs')
                try:
                    raw = json.loads(choice['text'])
                except json.JSONDecodeError:
                    raw = None
                valid = isinstance(raw, dict) and set(raw) == {'verdict'} and raw['verdict'] in ('PASS', 'FAIL', 'UNKNOWN')
                event = {'source_id': row['source_id'], 'prompt_sha256': hashlib.sha256(row['prompt'].encode()).hexdigest(),
                    'profile': 'sas-7b-q4' if args.arm == 'sas' else 'mas-3b-q4',
                    'prompt_tokens': usage['prompt_tokens'], 'generated_tokens': usage['completion_tokens'],
                    'requested_tokens': 192, 'finish_reason': choice['finish_reason'], 'response': choice['text'],
                    'verdict': raw['verdict'] if valid else 'UNPARSED', 'seconds': time.monotonic() - started}
                responses.append(event)
                trace.write(json.dumps(event) + '\n'); trace.flush()
                print(json.dumps({'source_id': row['source_id'], 'n_completed': len(responses)}), flush=True)
        write(out / 'metrics.json', analyze(rows, responses))
    finally:
        model.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--source')
    parser.add_argument('--arm', choices=('sas', 'mas'))
    parser.add_argument('--selection'); parser.add_argument('--adapter'); parser.add_argument('--proof'); parser.add_argument('--weights-root')
    parser.add_argument('--out', required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    out = artifact_path(args.out)
    if args.prepare:
        if not args.source:
            parser.error('--prepare requires --source')
        prepare(artifact_path(args.source), out)
        print(json.dumps({'selection': str(out / 'selection.json'), 'n': 32}))
        return
    if any(not getattr(args, key) for key in ('arm', 'selection', 'adapter', 'proof', 'weights_root')):
        parser.error('Probe requires arm,selection,adapter,proof,weights-root')
    if args.worker:
        worker(args)
        return
    selected_rows(artifact_path(args.selection))
    if out.exists():
        raise ValueError('Refuse overwrite')
    if psutil.virtual_memory().available < CAP + 1250000000:
        raise MemoryError('Insufficient host headroom')
    out.mkdir(parents=True)
    command = [sys.executable, '-u', str(Path(__file__)), *sys.argv[1:], '--worker']
    files = [Path(__file__), ROOT / 'scripts/tier8_v2_adapter_runtime.py', ROOT / 'scripts/completion_tokenization.py',
             ROOT / 'scripts/financial_review_protocol.py', artifact_path(args.selection) / 'selection.json',
             artifact_path(args.selection) / 'examples.jsonl', artifact_path(args.proof) / 'proof.json']
    write(out / 'manifest.json', {'command': command, 'input_sha256': {str(p): sha(p) for p in files},
                                 'cap_bytes': CAP, 'arm': args.arm, 'expected': 32, 'model_calls_expected': 32})
    child, peak, breach = None, 0, False
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
                available = psutil.virtual_memory().available
                peak = max(peak, rss)
                memory.write(json.dumps({'time': time.time(), 'tree_rss_bytes': rss, 'host_available_bytes': available}) + '\n'); memory.flush()
                if rss > CAP or available < 1000000000:
                    breach = True; os.killpg(child.pid, signal.SIGKILL); break
                time.sleep(.2)
            code = child.wait()
        _, rows = selected_rows(artifact_path(args.selection))
        responses = [json.loads(s) for s in (out / 'responses.jsonl').read_text().splitlines()] if (out / 'responses.jsonl').exists() else []
        valid = code == 0 and not breach and len(responses) == 32
        replay = analyze(rows, responses) if valid else None
        if valid and replay != json.loads((out / 'metrics.json').read_text()):
            raise ValueError('Parent metric replay differs')
        write(out / 'summary.json', {'status': 'complete' if valid else 'failed', 'exit_code': code, 'n': len(responses),
            'expected': 32, 'cap_bytes': CAP, 'peak_tree_rss_bytes': peak, 'memory_breach': breach,
            'metrics': replay, 'actual_qa_gain': False, 'novelty_established': False})
        if not valid:
            raise RuntimeError('Quartet probe failed; preserve evidence, no retry')
    finally:
        if child and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL); child.wait()


if __name__ == '__main__':
    main()
