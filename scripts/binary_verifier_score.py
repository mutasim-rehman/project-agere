"""One-position binary-critic scoring without retaining all prompt logits.

Known forced-prefix classification, shared by every proposed selection control.
PASS margin is not a calibrated correctness probability. Every evaluated prompt
and forced-prefix token is charged; zero generated tokens does not mean free work.
"""
from dataclasses import dataclass
import hashlib
import json
import math
import time

from completion_tokenization import completion_tokens

PREFIX = '{"verdict": "'
LABELS = ('PASS', 'FAIL', 'UNKNOWN')


@dataclass
class VerificationBudget:
    max_prefill_tokens: int = 8192
    max_checks: int = 4
    prefill_tokens: int = 0
    checks: int = 0

    def __post_init__(self):
        if any(type(v) is not int or v < 0 for v in
               (self.max_prefill_tokens, self.max_checks, self.prefill_tokens, self.checks)):
            raise ValueError('Invalid verification budget')
        if self.prefill_tokens > self.max_prefill_tokens or self.checks > self.max_checks:
            raise ValueError('Overspent verification budget')

    def can_charge(self, tokens):
        if type(tokens) is not int or tokens <= 0:
            raise ValueError('Invalid prefill charge')
        return self.checks < self.max_checks and self.prefill_tokens + tokens <= self.max_prefill_tokens

    def charge(self, tokens):
        if not self.can_charge(tokens):
            raise ValueError('Verification budget exhausted')
        self.prefill_tokens += tokens
        self.checks += 1


def score(model, rendered_prompt, budget, *, context):
    if model._logits_all:
        raise ValueError('Require last-position-only logits allocation')
    if context != model.n_ctx():
        raise ValueError('Context differs from actual loaded model')
    prompt = rendered_prompt + PREFIX
    tokens = completion_tokens(model, prompt)
    label_ids = {}
    # Check against the ENTIRE prompt boundary, not isolated label tokenization.
    for label in LABELS:
        full = completion_tokens(model, prompt + label)
        if full[:-1] != tokens:
            raise ValueError('Label is not exactly one stable continuation token')
        label_ids[label] = full[-1]
    event = {'prompt': rendered_prompt, 'forced_prefix': PREFIX,
             'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
             'input_ids_sha256': hashlib.sha256(json.dumps(tokens).encode()).hexdigest(),
             'prompt_tokens_required': len(tokens), 'generated_tokens': 0,
             'label_ids': label_ids, 'context': context, 'accepted': False}
    if len(tokens) + 8 > context:
        return {**event, 'status': 'no_context', 'prompt_tokens': 0, 'seconds': 0}
    if not budget.can_charge(len(tokens)):
        return {**event, 'status': 'no_budget', 'prompt_tokens': 0, 'seconds': 0}
    budget.charge(len(tokens))
    started = time.monotonic()
    model.reset()
    model.eval(tokens)
    if model.n_tokens != len(tokens):
        raise ValueError('Evaluated token count differs')
    # eval(logits_all=False) deliberately leaves Python scores stale in this
    # installed runtime. Read the native last output row directly; never scores.
    pointer = model._ctx.get_logits_ith(-1)
    if not pointer:
        raise ValueError('No native final-position logits')
    logits = {label: float(pointer[index]) for label, index in label_ids.items()}
    if not all(math.isfinite(v) for v in logits.values()):
        raise ValueError('Nonfinite verifier logits')
    margin = logits['PASS'] - max(logits['FAIL'], logits['UNKNOWN'])
    return {**event, 'status': 'scored', 'prompt_tokens': len(tokens), 'label_logits': logits,
            'pass_margin': margin, 'accepted': margin > 0,
            'seconds': time.monotonic() - started,
            'interpretation': 'Forced-prefix label margin, not calibrated correctness or free verification.'}


def select_representatives(plans, grouping, score_candidate):
    """Stable representative scoring; duplicates contribute no extra votes.

    score_candidate(index, plan) must enforce its explicit work budget. Keep
    original on exact score ties; deliver only a strictly positive PASS margin.
    Full traces retain skipped candidates, scores and the representative map.
    """
    flat = [i for group in grouping['groups'] for i in group]
    if sorted(flat) != list(range(len(plans))) or any(not g for g in grouping['groups']):
        raise ValueError('Grouping is not a partition of this pool')
    events, best, best_margin = [], None, 0.0
    for group in grouping['groups']:
        index = group[0]
        analysis = grouping['analyses'][index]
        if analysis.get('execution', {}).get('issues', [True]):
            events.append({'index': index, 'status': 'not_executable', 'members': group})
            continue
        event = score_candidate(index, plans[index])
        events.append({'index': index, 'members': group, **event})
        if event['status'] == 'scored':
            margin = event['pass_margin']
            if not math.isfinite(margin):
                raise ValueError('Nonfinite score')
            if margin > best_margin:
                best, best_margin = index, margin
        # A cheaper later candidate may still fit the remaining prefill budget.
        # No-context/too-large candidates therefore never terminate the sweep.
    return {'selected_index': best, 'delivered': best is not None,
            'selected_margin': best_margin if best is not None else None, 'events': events}
