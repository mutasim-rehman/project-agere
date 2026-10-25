"""One pinned backbone with distinct validated role adapters and fresh KV state.

Known shared-backbone serving, not a novelty claim (see LRAgent). This backend is
experimental until actual isolated-versus-switched logit/generation and memory
checks pass. It does not reuse KV or merge policies. Never silently substitute a
joint adapter for a separately trained critic. Existing baseline runs stay intact.
"""
from tier8_artifact_paths import artifact_path
from tier8_v2_adapter_runtime import _validated_adapter
from tier8_v2_adapter_convert import validate_adapter
from tier8_v2_run import Models, MODEL_FILES, verified_models


def activate_policy(model, api, handle):
    """Clear old KV and ALL policies before setting exactly one adapter.

    Llama.reset sets n_tokens=0. The existing completion/eval paths then remove
    KV from position0 before processing any prompt. No prefix-state reuse occurs.
    Activation failure leaves zero active adapters and never runs a base fallback.
    """
    if not handle:
        raise ValueError('Missing native policy handle')
    model.reset()
    api.llama_clear_adapter_lora(model._ctx.ctx)
    if api.llama_set_adapter_lora(model._ctx.ctx, handle, 1.0):
        api.llama_clear_adapter_lora(model._ctx.ctx)
        model.reset()
        raise RuntimeError('Native role activation failed; no base-policy fallback')


class SharedRoleModels(Models):
    def __init__(self, *, context, actor_adapter, critic_adapter, weights_root, profile='3b'):
        from llama_cpp import Llama, LlamaGrammar, llama_cpp as api
        import math
        if profile not in ('3b', '7b') or type(context) is not int or context <= 0:
            raise ValueError('Unsupported backbone/context')
        actor = _validated_adapter(actor_adapter, profile, 'drafter', 'drafter')
        critic = _validated_adapter(critic_adapter, profile, 'verifier', 'critic')
        if actor['sha256'] == critic['sha256']:
            raise ValueError('Require distinct specialist policies')
        for info in (actor, critic):
            manifest, summary, _ = validate_adapter(artifact_path(info['training_run']))
            n = manifest.get('training_n', 0)
            validation = summary.get('validation_teacher_forced_loss')
            if (n <= 0 or summary['mode'] != 'train' or summary.get('examples_processed') != n
                    or summary['optimizer_updates'] != (n + 7) // 8
                    or not isinstance(validation, (int, float)) or not math.isfinite(validation)):
                raise ValueError('Require full actual specialist epoch and finite validation')
        self.verified_models = verified_models('sas' if profile == '7b' else 'mas',
            verifier_model='3b', drafter_model='3b-q4', use_selector=False, weights_root=weights_root)
        filename = MODEL_FILES['sas']['sas'] if profile == '7b' else 'qwen2.5-3b-instruct-q4_k_m.gguf'
        self.context, self.grammar, self.api = context, LlamaGrammar, api
        self.adapter_info, self.verifier_adapter_info = actor, critic
        self.adapter_applications, self.handles = {}, {}
        self.activation_history, self.active_role = [], None
        self._closed = False
        self.shared_model = Llama(model_path=str(artifact_path(weights_root) / filename), n_ctx=context,
            n_gpu_layers=0, n_threads=8, n_threads_batch=8, n_batch=64, n_ubatch=64,
            seed=42, use_mmap=False, verbose=False, logits_all=False)
        self.models = {'drafter': self.shared_model, 'verifier': self.shared_model}
        try:
            for role, info in [('drafter', actor), ('verifier', critic)]:
                handle = api.llama_adapter_lora_init(self.shared_model._model.model,
                                                   str(artifact_path(info['file'])).encode('utf-8'))
                if not handle:
                    raise RuntimeError('Native adapter initialization failed: ' + role)
                self.handles[role] = handle
                self.shared_model._stack.callback(api.llama_adapter_lora_free, handle)
                self.adapter_applications[role] = {**info, 'runtime_handle_initialized': True,
                    'backbone_instance': 'shared0', 'adapter_policy_distinct': True,
                    'fresh_kv_each_call': True}
            # LIFO: clear context references BEFORE freeing adapter handles.
            self.shared_model._stack.callback(api.llama_clear_adapter_lora, self.shared_model._ctx.ctx)
            self.shared_model._stack.callback(self._mark_closed)
        except BaseException:
            self.shared_model.close()
            self._closed = True
            raise

    def _mark_closed(self):
        self._closed, self.active_role = True, None

    def activate(self, role):
        if self._closed or role not in self.handles:
            raise ValueError('Closed backend or unknown role')
        self.active_role = None
        activate_policy(self.shared_model, self.api, self.handles[role])
        self.active_role = role
        self.activation_history.append({'role': role, 'adapter_sha256': self.adapter_applications[role]['sha256'],
                                        'all_previous_adapters_cleared': True, 'kv_prefix_reuse': False})

    def call(self, role, content, schema, budget, requested, stage):
        self.activate(role)
        value, event = Models.call(self, role, content, schema, budget, requested, stage)
        return value, {**event, 'serving_backend': 'shared_backbone_distinct_role_adapters',
                       'active_adapter_sha256': self.adapter_applications[role]['sha256'],
                       'kv_prefix_reuse': False}

    def close(self):
        if not self._closed:
            self.shared_model.close()
