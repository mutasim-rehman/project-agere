"""Audit and compare full matched financial policies, without model inference."""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import random

from tier8_artifact_paths import artifact_path
from tier8_v2_posttrain_queue import sha, write, check_inputs
from tier8_v2_adapter_runtime import load_adapter, load_critic_adapter
from tier8_v2_critic_policy_pair import proof_effect
from tier8_v2_demo_retrieval import report_group
from tier8_v2_natural_run import Models, model_files, natural_partition
from completion_tokenization import completion_tokens
from financial_trace_replay import replay

ROOT = Path(__file__).resolve().parents[1]
METRICS = ('case_success', 'raw_execution_match')
VIEWS = ('full', 'no_repair_prefix', 'ungated_initial_prefix')


def outcome(view, metric):
    return ('correct_delivered' if view['score'][metric] else 'wrong_delivered') if view['delivered'] else 'withheld'


def summarize(records):
    if not records:
        raise ValueError('Empty policy records')
    result = {}
    for view in VIEWS:
        rows = [r[view] for r in records.values()]
        result[view] = {'generated_tokens': sum(r['generated_tokens'] for r in rows),
            'prompt_tokens': sum(r['prompt_tokens'] for r in rows),
            'inference_seconds': sum(r['inference_seconds'] for r in rows),
            'truncated_stages': sum(r['truncated_stages'] for r in rows), 'metrics': {}}
        for metric in METRICS:
            counts = Counter(outcome(r, metric) for r in rows)
            delivered = counts['correct_delivered'] + counts['wrong_delivered']
            result[view]['metrics'][metric] = {
                **{k: counts[k] for k in ('correct_delivered', 'wrong_delivered', 'withheld')},
                'candidate_correct': sum(r['score'][metric] for r in rows),
                'precision_when_delivered': counts['correct_delivered'] / delivered if delivered else None}
    return result


def compare(left, right):
    if not left or set(left) != set(right):
        raise ValueError('Require nonempty paired case sets')
    groups = defaultdict(list)
    for key in sorted(left):
        groups[report_group(key)].append(key)
    result = {'n': len(left), 'reports': len(groups), 'delta_direction': 'right_minus_left',
              'conditions': {'left': summarize(left), 'right': summarize(right)}, 'views': {}}
    for view in VIEWS:
        result['views'][view] = {}
        for metric in METRICS:
            changes = {i: {k: int(outcome(right[i][view], metric) == k) -
                int(outcome(left[i][view], metric) == k) for k in
                ('correct_delivered', 'wrong_delivered', 'withheld')} for i in sorted(left)}
            values = {k: [] for k in next(iter(changes.values()))}
            rng = random.Random(42); clusters = list(groups.values())
            for _ in range(10000):
                sample = [i for cluster in rng.choices(clusters, k=len(clusters)) for i in cluster]
                for key in values:
                    values[key].append(sum(changes[i][key] for i in sample) / len(sample))
            counts = {key: sum(row[key] for row in changes.values()) for key in values}
            result['views'][view][metric] = {'delta_counts': counts,
                'delta_per_case': {k: v / len(left) for k, v in counts.items()},
                'report_cluster_bootstrap_95_intervals': {k: [sorted(v)[249], sorted(v)[9749]] for k, v in values.items()},
                'transitions': dict(Counter(outcome(left[i][view], metric) + ' -> ' +
                    outcome(right[i][view], metric) for i in sorted(left))),
                'sample_pareto_improvement': counts['correct_delivered'] >= 0 and counts['wrong_delivered'] <= 0
                    and (counts['correct_delivered'] > 0 or counts['wrong_delivered'] < 0)}
    primary = [result['views']['full'][m]['delta_counts'] for m in METRICS]
    result['promising_under_both_metrics'] = (all(c['correct_delivered'] >= 0 and c['wrong_delivered'] <= 0 for c in primary)
        and any(c['correct_delivered'] > 0 or c['wrong_delivered'] < 0 for c in primary))
    result['limits'] = ('Exploratory public training-source reports, not publication confirmation or financial safety. '
        'Whole-report resampling; small or degenerate intervals do not establish equivalence. '
        'Prefix outcomes/work are recorded trajectory ablations, not fresh generations. '
        'No scalar error penalty or outcome-selected metric. Novelty is not inferred from a positive result.')
    return result


class ArtifactChecks:
    def __init__(self):
        self.files = {}

    def verify(self, path, digest):
        path = artifact_path(path); key = str(path)
        if key not in self.files:
            self.files[key] = sha(path)
        if self.files[key] != digest:
            raise ValueError('Changed artifact: ' + key)

    def proof(self, info, root, run_models):
        root = artifact_path(root)
        proof, summary, manifest = [json.loads((root / n).read_text()) for n in
                                   ('proof.json', 'summary.json', 'manifest.json')]
        if (not proof['pass'] or proof['adapter'] != info or summary['status'] != 'complete' or
                summary['exit_code'] != 0 or summary.get('memory_breached', False) or
                summary.get('memory_breach', False) or manifest['cap_bytes'] != summary['cap_bytes'] or not
                0 < summary['peak_tree_rss_bytes'] <= summary['cap_bytes'] <= 6400000000):
            raise ValueError('Incomplete/wrong adapter effect proof')
        phases = proof['phases']
        if [p['scale'] for p in phases] != [0, 1, 0]:
            raise ValueError('Wrong effect proof phases')
        if 'conditional_label_logprobs' in phases[0]:
            from binary_verifier_score import LABELS
            from tier8_v2_last_logit_proof import label_logprobs
            maps = [p['conditional_label_logprobs'] for p in phases]
            if (proof['logits_all'] or not proof['native_entry_points_equal'] or any(
                    p['event']['status'] != 'scored' or set(p['conditional_label_logprobs']) != set(LABELS) or
                    p['conditional_label_logprobs'] != label_logprobs(p['event']['label_logits']) for p in phases)):
                raise ValueError('Invalid native label proof')
            if (proof['actual_generated_tokens'] != 0 or proof['actual_prefill_tokens'] <= 0 or
                    proof['actual_prefill_tokens'] != sum(p['event']['prompt_tokens'] for p in phases)):
                raise ValueError('Native proof work ledger differs')
            zero, one, repeat = maps
            drift = max(abs(zero[k] - repeat[k]) for k in LABELS)
            effect = max(abs(zero[k] - one[k]) for k in LABELS)
            if (any(not math.isfinite(v) for m in maps for v in m.values()) or drift > 1e-5 or
                    effect <= max(1e-5, 10 * drift) or
                    proof['zero_repeat_max_label_logprob_drift'] != drift or proof['max_label_logprob_effect'] != effect):
                raise ValueError('Native effect does not reproduce')
            for path, digest in manifest['source_sha256'].items():
                self.verify(path, digest)
            models = proof['verified_models']; dataset = artifact_path(proof['dataset'])
        else:
            proof_effect(proof)
            if manifest['adapter'] != info or not summary['adapter_effect_proven']:
                raise ValueError('Legacy application identity differs')
            for name, digest in manifest['code_sha256'].items():
                if Path(name).name != name:
                    raise ValueError('Unsafe proof code path')
                self.verify(ROOT / 'scripts' / name, digest)
            models = manifest['verified_models']; dataset = artifact_path(manifest['dataset'])
        deployed = {m['sha256'] for m in run_models}
        if not deployed <= {m['sha256'] for m in models}:
            raise ValueError('Application proof does not bind deployed base model')
        self.verify(dataset, proof['dataset_sha256'])
        if manifest['dataset_sha256'] != proof['dataset_sha256']:
            raise ValueError('Proof dataset metadata differs')
        training = json.loads((artifact_path(info['training_run']) / 'manifest.json').read_text())
        if not any(artifact_path(p) == dataset and h == proof['dataset_sha256'] for p, h in training['input_sha256'].items()):
            raise ValueError('Proof validation data is not bound to actual training')
        selected = [r for r in map(json.loads, dataset.read_text().splitlines()) if r['source_id'] == proof['source_id']]
        if len(selected) != 1 or selected[0]['split'] != 'validation':
            raise ValueError('Proof example is not a unique validation record')
        import hashlib
        rendered = selected[0]['prompt']
        if 'event' in phases[0]:
            from binary_verifier_score import PREFIX
            if any(p['event']['prompt'] != rendered or p['event']['forced_prefix'] != PREFIX for p in phases):
                raise ValueError('Native proof rendered prompt/prefix differs')
            rendered += PREFIX
        expected = hashlib.sha256(rendered.encode()).hexdigest()
        prompts = [p['event']['prompt_sha256'] for p in phases] if 'event' in phases[0] else [proof['prompt_sha256']]
        if any(p != expected for p in prompts):
            raise ValueError('Proof prompt differs from actual validation')
        for n in ('proof.json', 'manifest.json', 'summary.json'):
            self.verify(root / n, sha(root / n))


def load_condition(job, proofs, checks, tokenizers):
    from llama_cpp import Llama
    root = artifact_path(job['result'])
    m, s = [json.loads((root / n).read_text()) for n in ('manifest.json', 'summary.json')]
    cfg = m['config']; rows = [json.loads(line) for line in (root / 'cases.jsonl').read_text().splitlines()]
    if (s['status'] != 'complete' or s['exit_code'] != 0 or s['n'] != s['expected'] or s['n'] != job['expected']
            or len(rows) != s['n'] or s['cap_bytes'] != m['cap_bytes'] or m['cap_bytes'] != 6400000000 or
            not 0 < s['peak_tree_rss_bytes'] <= m['cap_bytes']):
        raise ValueError('Incomplete/memory-invalid natural policy')
    sampled_peak = 0
    with (root / 'memory.jsonl').open() as stream:
        for line in stream:
            sample = json.loads(line); rss = sample['tree_rss_bytes']
            if type(rss) is not int or not 0 < rss <= m['cap_bytes']:
                raise ValueError('Memory samples exceed the common deployment cap')
            sampled_peak = max(sampled_peak, rss)
    if sampled_peak != s['peak_tree_rss_bytes']:
        raise ValueError('Recorded memory maximum does not replay')
    command = job['command'][2:]
    for flag, value in zip(command[::2], command[1::2]):
        if str(cfg[flag[2:].replace('-', '_')]) != value:
            raise ValueError('Actual policy differs from frozen command: ' + flag)
    if natural_partition(artifact_path(cfg['data']), artifact_path(m['evaluation_source'])) != m['research_source']:
        raise ValueError('Research partition identity differs')
    for name, digest in m['code_sha256'].items():
        if Path(name).name != name:
            raise ValueError('Unsafe generation source path')
        checks.verify(ROOT / 'scripts' / name, digest)
    for model in m['models']:
        checks.verify(model['file'], model['sha256'])
    checks.verify(cfg['data'], m['data_sha256']); checks.verify(m['evaluation_source'], m['evaluation_source_sha256'])
    actor = load_adapter(cfg['adapter'], cfg['arm'], cfg['drafter_model'])
    critic = load_critic_adapter(cfg['verifier_adapter']) if cfg['arm'] == 'mas' else None
    if actor != m['adapter'] or critic != m['verifier_adapter']:
        raise ValueError('Actual trained adapters differ')
    for info in (actor, critic) if critic else (actor,):
        base = artifact_path(info['training_run'])
        tm, ts = [json.loads((base / n).read_text()) for n in ('manifest.json', 'summary.json')]
        n = tm['training_n']; validation = ts['validation_teacher_forced_loss']
        if (tm['mode'] != 'train' or n <= 0 or tm['validation_n'] <= 0 or ts['examples_processed'] != n or
                ts['optimizer_updates'] != (n + 7) // 8 or not isinstance(validation, (float, int)) or not math.isfinite(validation)):
            raise ValueError('Require full epochs and finite validation for every deployed policy')
    checks.proof(actor, proofs['actor'], m['models'])
    if critic:
        checks.proof(critic, proofs['critic'], m['models'])
    applications = {'sas': actor} if cfg['arm'] == 'sas' else {'drafter': actor, 'verifier': critic}
    expected_apps = {role: {**info, 'runtime_handle_initialized': True} for role, info in applications.items()}
    allocation = model_files(cfg['arm'], cfg['verifier_model'], False, cfg['drafter_model'])
    def count(role, content, structured):
        path = artifact_path(cfg['weights_root']) / allocation[role]
        if str(path) not in tokenizers:
            tokenizers[str(path)] = Llama(model_path=str(path), vocab_only=True, verbose=False)
        return len(completion_tokens(tokenizers[str(path)], Models.prompt(content, structured)))
    public = [json.loads(line) for line in artifact_path(cfg['data']).read_text().splitlines()]
    if [r['case_id'] for r in rows] != [r['id'] for r in public] or len({r['case_id'] for r in rows}) != len(rows):
        raise ValueError('Missing/duplicate or reordered cases')
    gold = {r['id']: r for r in json.loads(artifact_path(m['evaluation_source']).read_text())}
    demos = []
    if cfg['demos']:
        if cfg['demo_policy'] != 'fixed':
            raise ValueError('This frozen study uses fixed demonstrations')
        path = ROOT / 'research/tier8_v2/data/finqa-training-demos.json'
        checks.verify(path, m['demonstrations_sha256'])
        demos = json.loads(path.read_text())['examples'][:cfg['demos']]
    replayed = {}
    for packet, row in zip(public, rows):
        if row['adapter_applications'] != expected_apps:
            raise ValueError('Missing or wrong actual runtime adapter handle')
        if packet['question'] != gold[packet['id']]['qa']['question']:
            raise ValueError('Public/source question differs')
        replayed[row['case_id']] = replay(packet, gold[packet['id']], row, cfg, count, demos)
    totals = {'case_successes': sum(r['score']['case_success'] for r in rows),
        'raw_execution_matches': sum(r['score']['raw_execution_match'] for r in rows),
        'initial_case_successes': sum(r['initial_score']['case_success'] for r in rows),
        'delivered_correct': sum(r['delivered'] and r['score']['case_success'] for r in rows),
        'delivered_incorrect': sum(r['delivered'] and not r['score']['case_success'] for r in rows),
        'withheld': sum(not r['delivered'] for r in rows), 'total_generated_tokens': sum(r['tokens'] for r in rows),
        'repair_gains': sum(not r['initial_score']['case_success'] and r['score']['case_success'] for r in rows),
        'repair_regressions': sum(r['initial_score']['case_success'] and not r['score']['case_success'] for r in rows)}
    if any(s[k] != v for k, v in totals.items()):
        raise ValueError('Run aggregate scores/work differ from replayed cases')
    for n in ('manifest.json', 'summary.json', 'cases.jsonl', 'memory.jsonl'):
        checks.verify(root / n, sha(root / n))
    return m, rows, replayed


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('study', 'proofs', 'left', 'right', 'partition', 'out'):
        p.add_argument('--' + name, required=True)
    a = p.parse_args(); out = artifact_path(a.out)
    if out.exists():
        raise ValueError('Refuse analysis overwrite')
    study_path = artifact_path(a.study); study = json.loads(study_path.read_text()); check_inputs(study)
    proof_path = artifact_path(a.proofs); proofs = json.loads(proof_path.read_text())
    jobs = []
    for label in (a.left, a.right):
        found = [j for j in study['jobs'] if j['condition'] == label and j['partition'] == a.partition]
        if len(found) != 1:
            raise ValueError('Comparison is not in the frozen primary study')
        jobs.append(found[0])
    if jobs[0]['arm'] != jobs[1]['arm'] or a.left == a.right:
        raise ValueError('Compare two distinct policies within an architecture')
    checks = ArtifactChecks(); tokenizers = {}
    try:
        loaded = [load_condition(j, proofs[j['condition']], checks, tokenizers) for j in jobs]
        left, right = [v[0] for v in loaded]
        for key in ('data_sha256', 'evaluation_source_sha256', 'code_sha256', 'models', 'task_policy', 'research_source', 'runtime'):
            if left[key] != right[key]:
                raise ValueError('Unmatched policy settings: ' + key)
        strip = lambda m: {k: v for k, v in m['config'].items() if k not in ('out', 'adapter', 'verifier_adapter')}
        if strip(left) != strip(right):
            raise ValueError('Inference methods/configurations differ')
        same_actor = left['adapter'] == right['adapter']
        if not any(j['condition'].startswith('baseline') for j in jobs):
            from tier8_v2_continue import RECIPE
            fitting = []
            for job, m in zip(jobs, (left, right)):
                info = m['adapter'] if job['arm'] == 'sas' else m['verifier_adapter']
                tm = json.loads((artifact_path(info['training_run']) / 'manifest.json').read_text())
                expected_name = job['condition'] if job['arm'] == 'sas' else job['condition'] + '_critic'
                sources = [path for path in study['input_sha256'] if Path(path).name == 'manifest.json'
                           and Path(path).parent.name == expected_name]
                if len(sources) != 1 or tm['input_sha256'].get(sources[0]) != study['input_sha256'][sources[0]]:
                    raise ValueError('Actual continuation is not bound to its frozen condition dataset')
                if tm.get('optimizer') != RECIPE or tm['lora'] != RECIPE['lora']:
                    raise ValueError('Matched continuation optimizer/adapter recipe differs')
                fitting.append(tm)
            if fitting[0]['initializer'] != fitting[1]['initializer'] or fitting[0]['training_base'] != fitting[1]['training_base']:
                raise ValueError('Matched policies did not share the same actual initializer/base')
        if jobs[0]['arm'] == 'mas' and not any(j['condition'].startswith('baseline') for j in jobs):
            if not same_actor:
                raise ValueError('Matched MAS policies require the identical common actor')
            for x, y in zip(loaded[0][1], loaded[1][1]):
                actor_keys = ('role', 'stage', 'prompt', 'prompt_tokens', 'prompt_tokens_source',
                              'requested_tokens', 'effective_limit', 'generated_tokens', 'finish_reason', 'response')
                if x['initial_plan'] != y['initial_plan'] or any(
                        x['stages'][0].get(k) != y['stages'][0].get(k) for k in actor_keys):
                    raise ValueError('Fixed MAS actor initial draft/prompt changed')
        result = compare(loaded[0][2], loaded[1][2])
        result.update(left=a.left, right=a.right, partition=a.partition, arm=jobs[0]['arm'],
            same_actor_adapter=same_actor, all_prompts_execution_delivery_scores_and_token_ledgers_replayed=True,
            measured_new_generation_calls=0, tokenizer_only=True, novelty_established=False)
        checks.verify(study_path, sha(study_path)); checks.verify(proof_path, sha(proof_path))
        for path in (Path(__file__), ROOT / 'scripts/financial_trace_replay.py'):
            checks.verify(path, sha(path))
        result['input_sha256'] = checks.files
        write(out, result)
        print(json.dumps({'out': str(out), 'n': result['n'], 'reports': result['reports'],
                          'promising_under_both_metrics': result['promising_under_both_metrics']}))
    finally:
        for model in tokenizers.values():
            model.close()


if __name__ == '__main__':
    main()
