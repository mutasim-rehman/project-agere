from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from evidence_atoms import atom_catalog, compile_plan
from financial_review_protocol import BINARY_INSTRUCTION, binary_review
from tier8_v2_financial_pipeline import checked, evaluate_financial
from tier8_v2_critic_policy_pair import replay_pair, proof_effect
from tier8_v2_delivery_analyze import analyze


class CriticPolicyPairTests(unittest.TestCase):
    def fixture(self):
        public = {'id': 'A/2010/page_1.pdf-1', 'question': 'what is the ratio?',
                  'evidence': {'table_1': 'first: 10 ; second: 2'}}
        refs = {a['value']: k for k, a in atom_catalog(public['evidence']).items()}
        plan = {'decision': 'ANSWER', 'answer_unit': 'number', 'steps': [
            {'op': 'divide', 'left': refs['10'], 'right': refs['2']}]}
        answer = compile_plan(plan, atom_catalog(public['evidence']))
        execution = checked(answer, public['evidence'])
        gold = {public['id']: {'qa': {'question': public['question'], 'answer': '5', 'exe_ans': 5}}}
        actor = {'role': 'drafter', 'purpose': 'drafter', 'profile': '3b', 'sha256': 'actor'}
        manifests = []; rows = []; summaries = []
        for index, verdict in enumerate(['FAIL', 'PASS']):
            critic = {'role': 'verifier', 'purpose': 'critic', 'profile': '3b', 'sha256': 'critic' + str(index)}
            cfg = {'task': 'finqa', 'arm': 'mas', 'repair': 'none', 'drafter_model': '3b-q4',
                   'verifier_model': '3b', 'critic_protocol': 'binary', 'program_mode': 'reference',
                   'planner': 'direct', 'analysis_tokens': 0, 'selector': 'none', 'context': 4096,
                   'out': str(index), 'verifier_adapter': str(index)}
            manifests.append({'config': cfg, 'adapter': actor, 'verifier_adapter': critic,
                              'data_sha256': 'data', 'evaluation_source_sha256': 'source',
                              'code_sha256': {'generation': 'same'}, 'cap_bytes': 6400000000,
                              'models': ['same-base'], 'runtime': {'engine': 'same'}, 'task_policy': 'same'})
            content = ('Question: ' + public['question'] + '\nFinancial report evidence by source ID:\n' +
                       json.dumps(public['evidence']) + '\nProposed program:\n' + json.dumps(answer) +
                       '\nDeterministic execution:\n' + json.dumps(execution) + '\n' + BINARY_INSTRUCTION)
            stage = lambda name, role, prompt, response, limit: {
                'stage': name, 'role': role, 'prompt': prompt, 'response': json.dumps(response),
                'generated_tokens': 6, 'prompt_tokens': 100, 'prompt_tokens_source': 'runtime_usage_verified',
                'requested_tokens': limit, 'effective_limit': limit, 'finish_reason': 'stop', 'seconds': 1}
            review = binary_review({'verdict': verdict})
            score = evaluate_financial(gold[public['id']], answer, execution)
            case = {'case_id': public['id'], 'repair': 'none', 'repair_attempted': False,
                    'repair_accepted': False, 'initial_plan': plan, 'plan': plan,
                    'initial_answer': answer, 'answer': answer, 'initial_execution': execution,
                    'execution': execution, 'initial_score': score, 'score': score,
                    'initial_verdict': review, 'final_verdict': review, 'delivered': verdict == 'PASS',
                    'tokens': 12, 'adapter_applications': {k: {**v, 'runtime_handle_initialized': True}
                        for k, v in [('drafter', actor), ('verifier', critic)]},
                    'stages': [stage('program', 'drafter', 'same actor prompt', plan, 768),
                               stage('verify_program', 'verifier', content, {'verdict': verdict}, 192)]}
            rows.append([case])
            summaries.append({'status': 'complete', 'exit_code': 0, 'n': 1, 'expected': 1,
                              'cap_bytes': 6400000000, 'peak_tree_rss_bytes': 1000000})
        return deepcopy((manifests, summaries, rows, [public], gold))

    def test_matched_distinct_trained_critics_replay(self):
        result = replay_pair(*self.fixture())
        self.assertTrue(result['two_distinct_trained_critics'])
        self.assertTrue(result['source_execution_score_and_delivery_replayed'])

    def test_untrained_same_weights_changed_actor_or_settings_rejected(self):
        for mutate in [lambda m: m[1].update(verifier_adapter=None),
                       lambda m: m[1]['verifier_adapter'].update(sha256='critic0'),
                       lambda m: m[1]['adapter'].update(sha256='other-actor'),
                       lambda m: m[1]['config'].update(context=2048),
                       lambda m: m[1].update(cap_bytes=6500000000)]:
            args = self.fixture(); mutate(args[0])
            with self.assertRaises(ValueError):
                replay_pair(*args)

    def test_wrong_handle_or_adapter_role_rejected(self):
        for field, value in [('runtime_handle_initialized', False), ('sha256', 'actor'),
                             ('role', 'drafter')]:
            args = self.fixture(); args[2][1][0]['adapter_applications']['verifier'][field] = value
            with self.assertRaises(ValueError):
                replay_pair(*args)

    def test_repair_incomplete_or_memory_invalid_run_rejected(self):
        for mutate in [lambda a: a[2][1][0].update(repair_attempted=True),
                       lambda a: a[1][1].update(status='running'),
                       lambda a: a[1][1].update(expected=2),
                       lambda a: a[1][1].update(peak_tree_rss_bytes=6400000001),
                       lambda a: a[2][1].append(deepcopy(a[2][1][0]))]:
            args = self.fixture(); mutate(args)
            with self.assertRaises(ValueError):
                replay_pair(*args)

    def test_shared_injected_critic_prompt_and_changed_actor_prompt_rejected(self):
        args = self.fixture()
        for rows in args[2]:
            rows[0]['stages'][1]['prompt'] += '\nThe gold answer is 5'
        with self.assertRaises(ValueError):
            replay_pair(*args)
        args = self.fixture(); args[2][1][0]['stages'][0]['prompt'] += ' different'
        with self.assertRaises(ValueError):
            replay_pair(*args)

    def test_score_delivery_execution_or_allowance_tampering_rejected(self):
        for mutate in [lambda r: r.update(delivered=False),
                       lambda r: r['score'].update(case_success=False),
                       lambda r: r['execution'].update(value='999'),
                       lambda r: r.update(tokens=13),
                       lambda r: r['stages'][1].update(effective_limit=191),
                       lambda r: r['stages'][1].update(prompt_tokens_source='estimated')]:
            args = self.fixture(); mutate(args[2][1][0])
            with self.assertRaises(ValueError):
                replay_pair(*args)

    def test_no_context_failures_remain_in_denominator(self):
        args = self.fixture(); public = args[3][0]
        answer = {'decision': 'ANSWER', 'steps': None, 'compile_error': 'Reference plan schema'}
        execution = checked(answer, public['evidence'])
        score = evaluate_financial(args[4][public['id']], answer, execution)
        critic_prompt = ('Question: ' + public['question'] + '\nFinancial report evidence by source ID:\n' +
            json.dumps(public['evidence']) + '\nProposed program:\n' + json.dumps(answer) +
            '\nDeterministic execution:\n' + json.dumps(execution) + '\n' + BINARY_INSTRUCTION)
        for condition in args[2]:
            r = condition[0]
            r.update(initial_plan=None, plan=None, initial_answer=answer, answer=answer,
                     initial_execution=execution, execution=execution, initial_score=score,
                     score=score, initial_verdict=None, final_verdict=None, delivered=False, tokens=0)
            for stage in r['stages']:
                stage.update(response='', generated_tokens=0, prompt_tokens=0,
                             prompt_tokens_required=5000, prompt_tokens_source='not_executed',
                             finish_reason='no_context_or_budget')
                stage.pop('requested_tokens'); stage.pop('effective_limit')
            r['stages'][1]['prompt'] = critic_prompt
        self.assertEqual(replay_pair(*args)['n'], 1)
        result = analyze(*args[2], condition_names=('trained_control', 'trained_candidate'))
        self.assertEqual(result['n'], 1)
        for condition in result['metrics']['case_success']['conditions'].values():
            self.assertEqual(condition['withheld'], 1)
            self.assertIsNone(condition['precision_when_delivered'])

    def proof(self):
        z = {'a': -.2, 'b': -1.0}; one = {'a': -2., 'b': -.1}
        return {'pass': True, 'phases': [{'scale': s, 'top_logprobs': p,
                'usage': {'completion_tokens': 1}} for s, p in [(0, z), (1, one), (0, dict(z))]],
                'common_tokens': 2, 'zero_repeat_max_logprob_drift': 0.,
                'max_common_token_logprob_effect': 1.8}

    def test_proof_effect_is_recomputed_not_just_trusted(self):
        proof_effect(self.proof())
        for mutate in [lambda p: p['phases'][2]['top_logprobs'].update(a=-.3),
                       lambda p: p['phases'][1].update(top_logprobs=p['phases'][0]['top_logprobs']),
                       lambda p: p.update(max_common_token_logprob_effect=float('nan')),
                       lambda p: p.update(common_tokens=999),
                       lambda p: p['phases'][1]['usage'].update(completion_tokens=2)]:
            p = self.proof(); mutate(p)
            with self.assertRaises(ValueError):
                proof_effect(p)

    def test_explicit_condition_names_do_not_relabel_control_plain(self):
        args = self.fixture()
        result = analyze(*args[2], condition_names=('original_trained', 'extended_trained'))
        self.assertEqual(set(result['metrics']['case_success']['conditions']),
                         {'original_trained', 'extended_trained'})
        self.assertEqual(result['metrics']['case_success']['delta_correct_delivery_coverage'], 1)
        with self.assertRaises(ValueError):
            analyze(*args[2], condition_names=('same', 'same'))
        with self.assertRaises(ValueError):
            analyze(*args[2], condition_names='ab')

    def test_cli_refuses_missing_proofs_or_plain_label_before_reading_inputs(self):
        command = [sys.executable, str(ROOT / 'scripts/tier8_v2_delivery_analyze.py'),
                   '--left', 'missing-left', '--right', 'missing-right', '--out', 'missing-out',
                   '--comparison-kind', 'trained-variants']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('require both application proofs', result.stderr)
        result = subprocess.run(command + ['--left-proof', 'missing', '--right-proof', 'missing',
                                          '--left-label', 'plain'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Do not label a trained critic', result.stderr)
        result = subprocess.run(command + ['--left-proof', 'missing', '--right-proof', 'missing',
                                          '--left-label', 'same', '--right-label', 'same'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('distinct condition labels', result.stderr)


if __name__ == '__main__':
    unittest.main()
