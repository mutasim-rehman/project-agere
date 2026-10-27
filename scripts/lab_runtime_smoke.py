"""Engineering-only F16/Q4 offline runtime smoke; not a research evaluation."""
import fcntl
import json
from pathlib import Path
import time

from lab_tiers_common import read, sha, ssd_root, write


def main():
    from llama_cpp import Llama, LlamaGrammar, __version__
    from completion_tokenization import completion_tokens
    root = ssd_root()
    if read(root / 'runs/lab_handoff/closure-v1/closure.json')['status'] != 'existing_8gb_prompt_evaluations_closed':
        raise ValueError('Finish the original8GB study and audits first')
    out = root / 'runs/lab_handoff/runtime-smoke-v1'
    if out.exists():
        raise ValueError('Refuse runtime smoke overwrite')
    lock = (root / 'runs/tier8_external.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    artifacts = read(root / 'phase2/manifests/gguf_artifacts.json')['artifacts']
    results = []
    for name in ['qwen2.5-0.5b-instruct-f16.gguf', 'qwen2.5-7b-instruct-q4_k_m.gguf']:
        item = next(a for a in artifacts if Path(a['path']).name == name)
        path = root / item['path']
        if sha(path) != item['sha256']:
            raise ValueError('Smoke model hash differs')
        model = Llama(model_path=str(path), n_ctx=512, n_gpu_layers=0, n_threads=2,
            n_threads_batch=2, n_batch=64, n_ubatch=64, seed=42, use_mmap=False, verbose=False)
        try:
            schema = {'type': 'object', 'properties': {'ok': {'const': True}},
                'required': ['ok'], 'additionalProperties': False}
            grammar = LlamaGrammar.from_json_schema(json.dumps(schema), verbose=False)
            prompt = '<|im_start|>user\nReturn the required JSON object.<|im_end|>\n<|im_start|>assistant\n'
            expected_prompt = len(completion_tokens(model, prompt))
            outputs = []
            for _ in range(2):
                model.reset()
                result = model.create_completion(prompt, max_tokens=16, temperature=0, top_k=1,
                    seed=42, repeat_penalty=1, stop=['<|im_end|>'], grammar=grammar)
                if result['usage']['prompt_tokens'] != expected_prompt or json.loads(result['choices'][0]['text']) != {'ok': True}:
                    raise ValueError('Grammar/token-accounting runtime contract failed')
                outputs.append(result)
            if outputs[0]['choices'][0]['text'] != outputs[1]['choices'][0]['text']:
                raise ValueError('Fresh reset reproducibility failed')
            results.append({'model': item, 'outputs': outputs, 'reset_outputs_equal': True})
        finally:
            model.close()
    out.mkdir(parents=True)
    write(out / 'summary.json', {'status': 'passed', 'llama_cpp': __version__, 'new_generation_calls': 4,
        'results': results, 'time': time.time(), 'script_sha256': sha(Path(__file__)),
        'scope': 'Forced-schema API/grammar/token/reset compatibility smoke on two small models. Not 14B/32B evaluation, accuracy improvement, RAM-tier validation or novelty evidence.'})
    print('Offline runtime smoke passed:', out)


if __name__ == '__main__':
    main()
