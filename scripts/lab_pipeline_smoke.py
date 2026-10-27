"""Tiny real-model workflow test; never a 16/32 GB research result."""
import fcntl
import json
import os
from pathlib import Path
import shutil

from lab_tiers_common import ROOT, read, sha, ssd_root, write


def main():
    from lab_tiers import counts, job_config, monitor_job
    from tier8_v2_finqa import packet
    from financial_trace_replay import replay
    from completion_tokenization import completion_tokens
    from tier8_v2_natural_run import Models
    from llama_cpp import Llama
    ssd = ssd_root()
    if read(ssd / 'runs/lab_handoff/closure-v1/closure.json')['status'] != 'existing_8gb_prompt_evaluations_closed':
        raise ValueError('Finish the original8GB study and audits first')
    out = ssd / 'runs/lab_tiers_v1/ENGINEERING_SMOKE_ONLY'
    if out.exists():
        raise ValueError('Preserve smoke output, no implicit retry')
    lock = (ssd / 'runs/tier8_external.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    os.environ['AGERE_WORKLOAD_LOCK_FD'] = str(lock.fileno())
    out.mkdir(parents=True)
    code = out / 'code'
    for p in (ROOT / 'scripts').glob('*.py'):
        target = code / 'scripts' / p.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
    write(code / 'configs/lab_tiers/protocol.json', {'status': 'engineering_fixture_only'})
    write(code / 'configs/lab_tiers/freeze.json', {'status': 'engineering_fixture_only', 'code_sha256': {}})
    gold = {'id': 'ENGINEERING/fixture/page_1.pdf-1', 'table': [['', '2020', '2021'], ['Revenue', '100', '120']],
        'pre_text': [], 'post_text': [], 'qa': {'question': 'What was the percentage increase in revenue from2020 to2021?',
            'answer': '20%', 'exe_ans': .2, 'program': 'subtract(120, 100), divide(#0, 100)', 'gold_inds': {'table_1': ''}}}
    public = packet(gold)
    (out / 'public.jsonl').write_text(json.dumps(public) + '\n')
    write(out / 'gold.json', [gold])
    write(out / 'demos.json', {'examples': []})
    paths = {'public': out / 'public.jsonl', 'gold': out / 'gold.json', 'demos': out / 'demos.json'}
    data = {key: str(path.relative_to(ssd)) for key, path in paths.items()}
    data.update({key + '_sha256': sha(path) for key, path in paths.items()})
    data.update(n=1, ids=[gold['id']])
    artifact = next(x for x in read(ssd / 'phase2/manifests/gguf_artifacts.json')['artifacts']
        if Path(x['path']).name == 'qwen2.5-0.5b-instruct-f16.gguf')
    shared = read(ROOT / 'configs/lab_tiers/protocol.json')['common']
    spec = {'common': {**shared, 'context': 2048, 'threads': 2}, 'dataset': data,
        'profiles': {'engineering': {'analysis_tokens': 0, 'demos': 0, 'repair': 'none'}},
        'tiers': {'16': {'sas': {'sas': artifact}, 'mas': {r: artifact for r in ('extractor', 'drafter', 'verifier')}}}}
    results, cache = {}, {}
    for arm in ('sas', 'mas'):
        cfg = job_config(spec, 16, arm, 'engineering')
        monitor_job(ssd, out, code, cfg, 6400000000, cache, spec)
        folder = out / f'tier16-{arm}-engineering'
        record = json.loads((folder / 'cases.jsonl').read_text())
        tokenizers = {role: Llama(model_path=str(ssd / artifact['path']), vocab_only=True,
            n_gpu_layers=0, n_threads=1, verbose=False) for role in cfg['models']}
        try:
            def count(role, content, structured):
                return len(completion_tokens(tokenizers[role], Models.prompt(content, structured)))
            verified = replay(public, gold, record, cfg, count, ())
        finally:
            for tokenizer in tokenizers.values():
                tokenizer.close()
        results[arm] = {'summary': read(folder / 'summary.json'), 'replay': verified,
            'case_sha256': sha(folder / 'cases.jsonl')}
    write(out / 'engineering-summary.json', {'status': 'passed', 'results': results,
        'script_sha256': sha(Path(__file__)),
        'scope': 'One handcrafted fixture with0.5B F16 models tests real resident loading, handoff, pipeline, token ledger, monitor, checkpoints and exact saved-response replay. No assertion about QA accuracy; NOT a16/32GB-tier/model evaluation.'})
    os.environ.pop('AGERE_WORKLOAD_LOCK_FD', None)
    lock.close()
    print('Real workflow smoke and replay passed:', out)


if __name__ == '__main__':
    main()
