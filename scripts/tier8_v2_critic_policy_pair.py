"""Matched two-trained-critic validation; no model calls or novelty claim.

Separates artifact/proof validation from pure case replay. Identical drafts and
critic prompts are necessary for critic-only attribution, not generalization.
"""
import hashlib
import json
import math
from pathlib import Path

from evidence_atoms import atom_catalog, compile_plan
from financial_review_protocol import BINARY_INSTRUCTION, binary_review
from tier8_artifact_paths import artifact_path
from tier8_v2_adapter_runtime import load_adapter, load_critic_adapter
from tier8_v2_financial_pipeline import checked, evaluate_financial

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def policies(manifests):
    a, b = manifests
    for key in ['data_sha256', 'evaluation_source_sha256', 'code_sha256', 'cap_bytes',
                'models', 'runtime', 'task_policy']:
        if a[key] != b[key]:
            raise ValueError('Trained pair differs: ' + key)
    config = lambda m: {k: v for k, v in m['config'].items() if k not in ['out', 'verifier_adapter']}
    if config(a) != config(b) or a['adapter'] != b['adapter']:
        raise ValueError('Actor or noncritic configuration differs')
    cfg = a['config']
    required = {'task': 'finqa', 'arm': 'mas', 'repair': 'none', 'drafter_model': '3b-q4',
                'verifier_model': '3b', 'critic_protocol': 'binary', 'program_mode': 'reference',
                'planner': 'direct', 'analysis_tokens': 0, 'selector': 'none'}
    if any(cfg.get(k) != v for k, v in required.items()):
        raise ValueError('Require the frozen direct binary no-repair study')
    if any(not m.get('verifier_adapter') for m in manifests):
        raise ValueError('Both conditions must contain trained critics')
    for m in manifests:
        for info, role, purpose in [(m['adapter'], 'drafter', 'drafter'),
                                    (m['verifier_adapter'], 'verifier', 'critic')]:
            if info.get('role') != role or info.get('purpose') != purpose or info.get('profile') != '3b':
                raise ValueError('Adapter role/purpose/profile differs')
    if a['verifier_adapter']['sha256'] == b['verifier_adapter']['sha256']:
        raise ValueError('Identical critic weights are not a policy contrast')
    if not 0 < a['cap_bytes'] <= 6400000000:
        raise ValueError('Invalid deployment cap')


def proof_effect(proof):
    phases = proof['phases']
    if proof['pass'] is not True or [p['scale'] for p in phases] != [0, 1, 0]:
        raise ValueError('Require reversible adapter application')
    if any(p['usage']['completion_tokens'] != 1 for p in phases):
        raise ValueError('Application proof must use one-token phases')
    zero, one, repeat = [p['top_logprobs'] for p in phases]
    if not zero or set(zero) != set(repeat):
        raise ValueError('Application repeat-token support differs')
    if any(not math.isfinite(v) for p in [zero, one, repeat] for v in p.values()):
        raise ValueError('Nonfinite application evidence')
    common = set(zero) & set(one)
    drift = max(abs(zero[k] - repeat[k]) for k in zero)
    effect = max((abs(zero[k] - one[k]) for k in common), default=0)
    if drift > 1e-5 or effect <= max(1e-5, 10 * drift):
        raise ValueError('Adapter effect is absent or not reproducible')
    if (not all(math.isfinite(proof[k]) for k in ['zero_repeat_max_logprob_drift', 'max_common_token_logprob_effect']) or
            proof['common_tokens'] != len(common) or
            abs(proof['zero_repeat_max_logprob_drift'] - drift) > 1e-12 or
            abs(proof['max_common_token_logprob_effect'] - effect) > 1e-12):
        raise ValueError('Application summary does not reproduce')


def replay_condition(m, s, condition, public, gold):
    """Audit one recorded condition; this is not a two-policy comparison."""
    ids = [r["id"] for r in public]
    if not ids or len(ids) != len(set(ids)) or [r["case_id"] for r in condition] != ids:
        raise ValueError("Incomplete or duplicated condition IDs")
    if (s['status'] != 'complete' or s['exit_code'] != 0 or s['n'] != len(ids) or
            s['expected'] != len(ids) or s['cap_bytes'] != m['cap_bytes'] or
            not 0 < s['peak_tree_rss_bytes'] <= m['cap_bytes'] or
            s.get('memory_breached', False)):
        raise ValueError('Need complete memory-valid runs')
    expected_apps = {'drafter': m['adapter'], 'verifier': m['verifier_adapter']}
    for case, packet in zip(condition, public):
        if packet['question'] != gold[packet['id']]['qa']['question']:
            raise ValueError('Question differs from source')
        if (case['repair'] != 'none' or case['repair_attempted'] or case['repair_accepted'] or
                case['initial_plan'] != case['plan'] or case['initial_answer'] != case['answer'] or
                case['initial_execution'] != case['execution']):
            raise ValueError('Candidate changed or repair was attempted')
        if set(case['adapter_applications']) != set(expected_apps):
            raise ValueError('Wrong adapter roles')
        for role, info in expected_apps.items():
            if (case['adapter_applications'][role].get('runtime_handle_initialized') is not True or
                    case['adapter_applications'][role] != {**info, 'runtime_handle_initialized': True}):
                raise ValueError('Applied adapter identity/handle differs')
        stages = case['stages']
        if [(s['stage'], s['role']) for s in stages] != [('program', 'drafter'), ('verify_program', 'verifier')]:
            raise ValueError('Unexpected model stage/role sequence')
        if case['tokens'] != sum(s['generated_tokens'] for s in stages) or not 0 <= case['tokens'] <= 2048:
            raise ValueError('Generation token ledger differs')
        for stage in stages:
            if type(stage['generated_tokens']) is not int or stage['generated_tokens'] < 0:
                raise ValueError('Invalid stage token count')
            if stage['generated_tokens'] and (stage['prompt_tokens_source'] != 'runtime_usage_verified' or
                    not 0 < stage['prompt_tokens'] or
                    not stage['generated_tokens'] <= stage['effective_limit'] <= stage['requested_tokens']):
                raise ValueError('Unverified model token accounting')
        parsed = lambda s: json.loads(s) if s else None
        try:
            decoded = parsed(stages[0]['response'])
        except json.JSONDecodeError:
            decoded = None
        if decoded != case['initial_plan']:
            raise ValueError('Initial plan does not match recorded generation')
        try:
            answer = compile_plan(decoded, atom_catalog(packet['evidence']))
        except ValueError as exc:
            answer = {'decision': 'ANSWER', 'steps': None, 'compile_error': str(exc)}
        execution = checked(answer, packet['evidence'])
        if answer != case['answer'] or execution != case['execution']:
            raise ValueError('Source program/execution does not replay')
        expected_prompt = ('Question: ' + packet['question'] + '\nFinancial report evidence by source ID:\n' +
            json.dumps(packet['evidence']) + '\nProposed program:\n' + json.dumps(answer) +
            '\nDeterministic execution:\n' + json.dumps(execution) + '\n' + BINARY_INSTRUCTION)
        if stages[1]['prompt'] != expected_prompt:
            raise ValueError('Critic input is not the recorded source/program/execution')
        try:
            review = binary_review(parsed(stages[1]['response']))
        except json.JSONDecodeError:
            review = None
        delivered = not execution['issues'] and isinstance(review, dict) and review['verdict'] == 'PASS'
        if (type(case['delivered']) is not bool or case['delivered'] != delivered or
                case['initial_verdict'] != review or case['final_verdict'] != review):
            raise ValueError('Delivery/verdict does not replay')
        score = evaluate_financial(gold[packet['id']], answer, execution)
        if case['score'] != score or case['initial_score'] != score:
            raise ValueError('Numerical scores do not replay')
    return {"n": len(ids), "source_execution_score_and_delivery_replayed": True}


def replay_pair(manifests, summaries, rows, public, gold):
    policies(manifests)
    ids = [r['id'] for r in public]
    if not ids or len(ids) != len(set(ids)) or any(i not in gold for i in ids):
        raise ValueError('Public/source IDs are empty, duplicated or missing')
    if any([r['case_id'] for r in condition] != ids for condition in rows):
        raise ValueError('Case rows do not match the complete public input order')
    for m, s, condition in zip(manifests, summaries, rows):
        replay_condition(m, s, condition, public, gold)
    for left, right in zip(*rows):
        if (left['initial_plan'] != right['initial_plan'] or left['initial_answer'] != right['initial_answer'] or
                left['stages'][0]['prompt'] != right['stages'][0]['prompt'] or
                left['stages'][1]['prompt'] != right['stages'][1]['prompt']):
            raise ValueError('Fixed actor draft or actual model prompts changed')
        for i in range(2):
            fields = ['prompt_tokens', 'prompt_tokens_required', 'prompt_tokens_source',
                      'requested_tokens', 'effective_limit']
            if i == 0:
                fields += ['response', 'generated_tokens', 'finish_reason']
            if any(left['stages'][i].get(k) != right['stages'][i].get(k) for k in fields):
                raise ValueError('Actor output or common critic allowance/encoding changed')
    return {'n': len(ids), 'identical_initial_drafts': True, 'identical_actor_prompts': True,
            'identical_critic_prompts': True, 'same_actor_adapter': True,
            'two_distinct_trained_critics': True, 'separate_critic_application_recorded': True,
            'source_execution_score_and_delivery_replayed': True}


def verify_condition_artifacts(m, proof_root, checked_files=None):
    """Validate one trained policy/proof; alone this is not a policy contrast."""
    proof_root = artifact_path(proof_root)
    if checked_files is None:
        checked_files = {}
    def verify(path, digest):
        path = artifact_path(path)
        if str(path) not in checked_files:
            checked_files[str(path)] = sha(path)
        actual = checked_files[str(path)]
        if actual != digest:
            raise ValueError('Changed artifact: ' + str(path))
    if load_adapter(m['config']['adapter'], 'mas', '3b-q4') != m['adapter'] or \
            load_critic_adapter(m['config']['verifier_adapter']) != m['verifier_adapter']:
        raise ValueError('Validated adapter differs from run metadata')
    for model in m['models']:
        verify(model['file'], model['sha256'])
    for name, digest in m['code_sha256'].items():
        if Path(name).name != name:
            raise ValueError('Unsafe generation-source name')
        verify(ROOT / 'scripts' / name, digest)
    verify(m['config']['data'], m['data_sha256'])
    verify(m['evaluation_source'], m['evaluation_source_sha256'])
    proof = json.loads((proof_root / 'proof.json').read_text())
    pm = json.loads((proof_root / 'manifest.json').read_text())
    ps = json.loads((proof_root / 'summary.json').read_text())
    if (proof['adapter'] != m['verifier_adapter'] or pm['adapter'] != m['verifier_adapter'] or pm['purpose'] != 'critic' or
            ps['status'] != 'complete' or ps['exit_code'] != 0 or not ps['adapter_effect_proven'] or
            ps['memory_breached'] or not 0 < ps['peak_tree_rss_bytes'] <= ps['cap_bytes'] <= m['cap_bytes'] or
            ps['cap_bytes'] != pm['cap_bytes'] or
            sorted(p['sha256'] for p in pm['verified_models']) != sorted(p['sha256'] for p in m['models'])):
        raise ValueError('Wrong or incomplete critic application proof')
    proof_effect(proof)
    for name, digest in pm['code_sha256'].items():
        if Path(name).name != name:
            raise ValueError('Unsafe proof-source name')
        verify(ROOT / 'scripts' / name, digest)
    if proof['dataset_sha256'] != pm['dataset_sha256']:
        raise ValueError('Proof dataset differs')
    verify(pm['dataset'], pm['dataset_sha256'])
    training = json.loads((artifact_path(m['verifier_adapter']['training_run']) / 'manifest.json').read_text())
    if training['input_sha256'].get(pm['dataset']) != pm['dataset_sha256']:
        raise ValueError('Application proof is not bound to its training dataset')
    entries = [json.loads(s) for s in artifact_path(pm['dataset']).read_text().splitlines()]
    selected = [r for r in entries if r['source_id'] == proof['source_id']]
    if (len(selected) != 1 or selected[0]['split'] != 'validation' or
            hashlib.sha256(selected[0]['prompt'].encode()).hexdigest() != proof['prompt_sha256']):
        raise ValueError('Application prompt is not the claimed validation example')
    for name in ['proof.json', 'manifest.json', 'summary.json']:
        checked_files[str(proof_root / name)] = sha(proof_root / name)
    return checked_files


def trained_pair(left, right, left_proof, right_proof):
    roots = list(map(artifact_path, [left, right]))
    manifests = [json.loads((p / 'manifest.json').read_text()) for p in roots]
    policies(manifests)
    checked_files = {}
    summaries = [json.loads((p / 'summary.json').read_text()) for p in roots]
    rows = [[json.loads(s) for s in (p / 'cases.jsonl').read_text().splitlines()] for p in roots]
    for m, proof_root in zip(manifests, map(artifact_path, [left_proof, right_proof])):
        verify_condition_artifacts(m, proof_root, checked_files)
    m = manifests[0]
    public = [json.loads(s) for s in artifact_path(m['config']['data']).read_text().splitlines()][:m['config']['limit']]
    source = json.loads(artifact_path(m['evaluation_source']).read_text())
    result = replay_pair(manifests, summaries, rows, public, {r['id']: r for r in source})
    result['verified_artifact_sha256'] = checked_files
    return result
