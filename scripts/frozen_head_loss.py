"""Vocabulary-block cross entropy for a frozen, optionally CPU-resident head.

Known memory-saving engineering (see Cut Your Losses, arXiv:2411.09009), not
novel methodology or its optimized CCE kernel. Recompute every block in backward;
no gradient pruning, sampling, vocabulary reduction or target truncation. This
helper does not itself implement model offload or demonstrate a 7B GPU fit.
"""
import torch
from torch.autograd.function import once_differentiable


class _FrozenHeadLoss(torch.autograd.Function):
    @staticmethod
    def forward(ctx, hidden, weight, targets, block_size):
        dtype = torch.float64 if hidden.dtype == torch.float64 else torch.float32
        shape = hidden.shape
        active = targets.reshape(-1) != -100
        h = hidden.reshape(-1, shape[-1])[active]
        y = targets.reshape(-1)[active]
        normalizer = torch.full((len(y),), -torch.inf, device=h.device, dtype=dtype)
        correct = torch.zeros_like(normalizer)
        # Explicit projection dtype, independent of the caller's autocast state.
        with torch.autocast(device_type=h.device.type, enabled=False):
            for start in range(0, weight.shape[0], block_size):
                w = weight[start:start + block_size].to(device=h.device, dtype=h.dtype)
                logits = (h @ w.T).to(dtype)
                normalizer = torch.logaddexp(normalizer, torch.logsumexp(logits, dim=-1))
                inside = (y >= start) & (y < start + len(w))
                correct[inside] = logits[inside, y[inside] - start]
        ctx.save_for_backward(hidden, weight, targets, normalizer)
        ctx.block_size = block_size
        return (normalizer - correct).mean()

    @staticmethod
    @once_differentiable
    def backward(ctx, grad_output):
        hidden, weight, targets, normalizer = ctx.saved_tensors
        active = targets.reshape(-1) != -100
        h = hidden.reshape(-1, hidden.shape[-1])[active]
        y = targets.reshape(-1)[active]
        grad_h = torch.zeros(h.shape, device=h.device, dtype=normalizer.dtype)
        with torch.autocast(device_type=h.device.type, enabled=False):
            for start in range(0, weight.shape[0], ctx.block_size):
                w = weight[start:start + ctx.block_size].to(device=h.device, dtype=h.dtype)
                logits = (h @ w.T).to(normalizer.dtype)
                derivative = torch.exp(logits - normalizer[:, None])
                inside = (y >= start) & (y < start + len(w))
                derivative[inside, y[inside] - start] -= 1
                derivative *= grad_output / len(y)
                # Match a low-precision linear layer's backward cast.
                grad_h += (derivative.to(h.dtype) @ w).to(normalizer.dtype)
        gradient = torch.zeros_like(hidden).reshape(-1, hidden.shape[-1])
        gradient[active] = grad_h.to(hidden.dtype)
        return gradient.reshape_as(hidden), None, None, None


def frozen_head_loss(hidden, weight, targets, block_size=1024):
    """Mean CE over explicit, already-aligned targets, ignoring -100 positions.

    Hidden/targets must share a CPU or CUDA device. Weight may reside on CPU or
    that same device; only one vocabulary block is copied at a time. All head
    weights must be frozen. No bias, label smoothing or higher-order gradients.
    FP32 accumulation except FP64 input, which preserves FP64 for verification.
    Low-precision blocking changes reduction order; bitwise equality is not claimed.
    """
    if (hidden.device.type not in ('cpu', 'cuda') or targets.device != hidden.device
            or weight.device not in (torch.device('cpu'), hidden.device)):
        raise ValueError('Unsupported tensor placement')
    if (hidden.ndim < 2 or weight.ndim != 2 or hidden.shape[-1] != weight.shape[1]
            or targets.shape != hidden.shape[:-1] or weight.shape[0] <= 0):
        raise ValueError('Invalid hidden/head/target shapes')
    if hidden.dtype not in (torch.float32, torch.float64, torch.bfloat16):
        raise ValueError('Use FP32, FP64 or BF16 hidden states')
    if not weight.is_floating_point() or weight.requires_grad:
        raise ValueError('Head must be a frozen floating-point matrix')
    if targets.dtype != torch.long or type(block_size) is not int or block_size <= 0:
        raise ValueError('Require integer target IDs and positive block size')
    active = targets != -100
    if not active.any().item() or ((targets[active] < 0) | (targets[active] >= len(weight))).any().item():
        raise ValueError('Require at least one valid vocabulary target')
    return _FrozenHeadLoss.apply(hidden, weight, targets, block_size)


def causal_frozen_head_loss(hidden, weight, labels, block_size=1024):
    """Full decoder context, ordinary next-token shift, masked-prefix mean CE.

    Labels align with the original complete input, as in HF causal-LM forward.
    Select active targets only inside frozen_head_loss, after shifting, so the
    final prefix position still predicts the first supervised target token.
    """
    if hidden.ndim != 3 or labels.shape != hidden.shape[:-1] or hidden.shape[1] < 2:
        raise ValueError('Require full batch/sequence hidden states and labels')
    return frozen_head_loss(hidden[:, :-1], weight, labels[:, 1:], block_size)
