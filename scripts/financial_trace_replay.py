"""Replay recorded financial model responses through the unchanged pipeline.

No generation or model weights: a caller supplies the exact deployment tokenizer
counter. This audits the prompts, full token ledger, execution, review and repair.
"""
from copy import deepcopy
import json
import math

from tier8_v2_financial_pipeline import run_financial, evaluate_financial


class RecordedModels:
    def __init__(self, stages, count, context):
        self.stages = stages
        self.count = count
        self.context = context
        self.position = 0

    def count_prompt_tokens(self, role, content):
        return self.count(role, content, True)

    def call(self, role, content, schema, budget, requested, stage):
        if self.position >= len(self.stages):
            raise ValueError('Missing recorded model call')
        event = self.stages[self.position]; self.position += 1
        if (event['role'], event['stage'], event['prompt']) != (role, stage, content):
            raise ValueError('Recorded stage, role or prompt differs from replay')
        required = self.count(role, content, schema is not None)
        limit = min(max(0, self.context - required - 8), budget.allowance(requested))
        generated = event['generated_tokens']
        if type(generated) is not int or not 0 <= generated <= limit:
            raise ValueError('Generated tokens exceed replayed context/budget')
        if not isinstance(event['seconds'], (float, int)) or not math.isfinite(event['seconds']) or event['seconds'] < 0:
            raise ValueError('Invalid inference duration')
        if limit == 0:
            expected = {'prompt_tokens': 0, 'prompt_tokens_required': required,
                'prompt_tokens_source': 'not_executed', 'generated_tokens': 0,
                'finish_reason': 'no_context_or_budget', 'response': '', 'seconds': 0}
            if any(event.get(k) != v for k, v in expected.items()):
                raise ValueError('Skipped call is not a zero-work context/budget skip')
            return None, deepcopy(event)
        if (event['prompt_tokens_source'] != 'runtime_usage_verified' or event['prompt_tokens'] != required
                or event['requested_tokens'] != requested or event['effective_limit'] != limit):
            raise ValueError('Recorded prompt tokens or allowances differ from deployment replay')
        budget.charge(generated)
        answer = event['response']
        if schema is not None:
            try:
                answer = json.loads(answer)
            except json.JSONDecodeError:
                answer = None
        return answer, deepcopy(event)

    def require_consumed(self):
        if self.position != len(self.stages):
            raise ValueError('Unconsumed recorded model calls')


def replay(public, gold, case, config, count, demonstrations=()):
    models = RecordedModels(case['stages'], count, config['context'])
    options = dict(representation=config['program_mode'], unit_mode=config['unit_mode'],
        selector=config['selector'], causal_mode=config['causal_mode'], catalog_style=config['catalog_style'],
        demonstrations=demonstrations, analysis_tokens=config['analysis_tokens'],
        planner=config['planner'], critic_protocol=config['critic_protocol'])
    expected = run_financial(public, models, config['arm'], config['repair'], **options)
    models.require_consumed()
    if any(case.get(k) != value for k, value in expected.items()):
        wrong = [k for k, value in expected.items() if case.get(k) != value]
        raise ValueError('Recorded pipeline result differs: ' + ','.join(wrong))
    for score_key, answer_key, execution_key in (
            ('initial_score', 'initial_answer', 'initial_execution'), ('score', 'answer', 'execution')):
        if case[score_key] != evaluate_financial(gold, expected[answer_key], expected[execution_key]):
            raise ValueError('Recorded numerical scoring differs from source replay')
    # Identical initial calls under full/none policies: this is a measured prefix,
    # not a newly generated alternative trajectory or a critic-free model run.
    end = next(i for i, s in enumerate(case['stages']) if s['stage'] == 'verify_program') + 1
    prefix = case['stages'][:end]
    initial_models = RecordedModels(prefix, count, config['context'])
    initial = run_financial(public, initial_models, config['arm'], 'none', **options)
    initial_models.require_consumed()
    if initial['answer'] != case['initial_answer'] or initial['execution'] != case['initial_execution']:
        raise ValueError('No-repair prefix changed the initial program')
    def view(answer, execution, delivered, stages):
        return {'score': evaluate_financial(gold, answer, execution), 'delivered': delivered,
            'generated_tokens': sum(s['generated_tokens'] for s in stages),
            'prompt_tokens': sum(s['prompt_tokens'] for s in stages),
            'inference_seconds': sum(s['seconds'] for s in stages),
            'truncated_stages': sum(s['finish_reason'] == 'length' for s in stages)}
    return {
        'full': view(expected['answer'], expected['execution'], expected['delivered'], case['stages']),
        'no_repair_prefix': view(initial['answer'], initial['execution'], initial['delivered'], prefix),
        'ungated_initial_prefix': view(initial['answer'], initial['execution'],
            not initial['execution']['issues'], prefix[:-1])}
