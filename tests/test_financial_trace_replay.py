from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from financial_trace_replay import replay
from tier8_v2_financial_pipeline import run_financial, evaluate_financial
from tier8_v2_method_analyze import compare


class ScriptedModels:
    context = 4096

    def __init__(self, responses):
        self.responses = iter(responses)

    def count_prompt_tokens(self, role, content):
        return 10

    def call(self, role, content, schema, budget, requested, stage):
        response = next(self.responses)
        limit = min(4078, budget.allowance(requested))
        budget.charge(10)
        return response, {'role': role, 'stage': stage, 'prompt': content,
            'prompt_tokens': 10, 'prompt_tokens_source': 'runtime_usage_verified',
            'generated_tokens': 10, 'requested_tokens': requested, 'effective_limit': limit,
            'finish_reason': 'stop', 'response': json.dumps(response), 'seconds': 1.}


class TraceReplay(unittest.TestCase):
    def setUp(self):
        self.public = {'id': 'R/2000/page_1.pdf-1', 'question': 'What is the ratio of profit to cost?',
            'evidence': {'T1': 'profit 20; cost 10'}, 'retrieval': {'gold_used': False}}
        self.gold = {'qa': {'exe_ans': 2, 'answer': '2'}}
        def program(op):
            return {'decision': 'ANSWER', 'answer_unit': 'number', 'steps': [{'op': op,
                'left': {'value': '20', 'span_id': 'T1'}, 'right': {'value': '10', 'span_id': 'T1'}}]}
        models = ScriptedModels([program('add'), {'verdict': 'FAIL'}, program('divide'), {'verdict': 'PASS'}])
        self.config = {'arm': 'sas', 'repair': 'full', 'context': 4096, 'program_mode': 'literal',
            'unit_mode': 'question', 'selector': 'none', 'causal_mode': 'check', 'catalog_style': 'full',
            'analysis_tokens': 0, 'planner': 'direct', 'critic_protocol': 'binary'}
        self.case = run_financial(self.public, models, 'sas', 'full', unit_mode='question',
                                  selector='none', critic_protocol='binary')
        for score, answer, execution in [('score', 'answer', 'execution'),
                                          ('initial_score', 'initial_answer', 'initial_execution')]:
            self.case[score] = evaluate_financial(self.gold, self.case[answer], self.case[execution])
        self.count = lambda role, content, structured: 10

    def test_full_repair_and_prefix_costs_replay(self):
        result = replay(self.public, self.gold, self.case, self.config, self.count)
        self.assertTrue(result['full']['delivered'])
        self.assertTrue(result['full']['score']['case_success'])
        self.assertFalse(result['no_repair_prefix']['delivered'])
        self.assertTrue(result['ungated_initial_prefix']['delivered'])
        self.assertFalse(result['ungated_initial_prefix']['score']['case_success'])
        self.assertEqual([result[k]['generated_tokens'] for k in
            ('full', 'no_repair_prefix', 'ungated_initial_prefix')], [40, 20, 10])

    def test_prompt_budget_and_score_tampering_reject(self):
        for kind in ('prompt', 'tokens', 'score'):
            bad = deepcopy(self.case)
            if kind == 'prompt':
                bad['stages'][1]['prompt'] += ' changed'
            elif kind == 'tokens':
                bad['stages'][0]['generated_tokens'] = 2049
            else:
                bad['score']['raw_execution_match'] = False
            with self.assertRaises(ValueError):
                replay(self.public, self.gold, bad, self.config, self.count)

    def test_no_repair_prefix_is_not_charged_for_later_calls(self):
        result = replay(self.public, self.gold, self.case, self.config, self.count)
        self.assertEqual(result['full']['inference_seconds'], 4)
        self.assertEqual(result['no_repair_prefix']['inference_seconds'], 2)
        self.assertEqual(result['ungated_initial_prefix']['inference_seconds'], 1)

    def test_global_pareto_rule_allows_one_metric_unchanged_but_rejects_conflict(self):
        result = replay(self.public, self.gold, self.case, self.config, self.count)
        left = {'R/2000/page_1.pdf-1': deepcopy(result)}
        right = deepcopy(left)
        for view in left[next(iter(left))].values():
            view['score']['case_success'] = False
        # Reported gain, raw unchanged satisfies the predeclared vector rule.
        compared = compare(left, right)
        self.assertTrue(compared['promising_under_both_metrics'])
        for view in right[next(iter(right))].values():
            view['score']['raw_execution_match'] = False
        self.assertFalse(compare(left, right)['promising_under_both_metrics'])


if __name__ == '__main__':
    unittest.main()
