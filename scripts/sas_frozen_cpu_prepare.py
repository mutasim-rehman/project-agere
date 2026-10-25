"""Keep exact BF16 frozen CPU matrices while preparing an NF4 LoRA decoder.

Equivalent to the pinned PEFT preparation for this supported policy, except no
whole-matrix FP32 materialization on CPU. Caller must convert embedding LOOKUP
results to FP32 before decoder input, and use the existing BF16 streamed head.
This is a memory-storage optimization, not a new objective or quantization.
"""
def prepare_frozen_cpu_model(model):
    import torch
    if not getattr(model, 'is_loaded_in_4bit', False):
        raise ValueError('Require loaded NF4 model')
    matrices = [model.get_input_embeddings().weight, model.get_output_embeddings().weight]
    if any(p.device.type != 'cpu' or p.dtype != torch.bfloat16 for p in matrices):
        raise ValueError('Require exact BF16 frozen CPU matrices')
    for parameter in model.parameters():
        parameter.requires_grad_(False)
        if any(parameter is p for p in matrices):
            continue
        if parameter.dtype in (torch.float16, torch.bfloat16) and parameter.__class__.__name__ != 'Params4bit':
            parameter.data = parameter.data.to(torch.float32)
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    return model
