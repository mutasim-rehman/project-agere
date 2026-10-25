"""Detach frozen CPU matrices from checkpoint mmap ownership during loading.

Storage optimization only, not a learning method. Register leaf post-load hooks
before from_pretrained assigns weights. Cloning keeps values/dtypes unchanged.
"""
from transformers import Qwen2ForCausalLM


def detach_cpu_storage(module, incompatible_keys):
    weight = module.weight
    if weight.device.type == 'cpu':
        if not weight.is_floating_point():
            raise ValueError('Expected unquantized CPU embedding/head')
        weight.data = weight.detach().clone()
        module._cpu_storage_detach_count = getattr(module, '_cpu_storage_detach_count', 0) + 1


class StorageDetachedQwen2ForCausalLM(Qwen2ForCausalLM):
    def __init__(self, config):
        if config.tie_word_embeddings:
            raise ValueError('This loader requires untied matrices')
        super().__init__(config)
        self.get_input_embeddings().register_load_state_dict_post_hook(detach_cpu_storage)
        self.get_output_embeddings().register_load_state_dict_post_hook(detach_cpu_storage)
