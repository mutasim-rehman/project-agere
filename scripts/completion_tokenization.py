"""Match llama-cpp-python 0.3.16's nonempty string/no-suffix completion encoder.

Recognize chat special tokens and honor the model's actual BOS/CLS/EOS/SEP policy.
This fixes accounting/context reservation, not reasoning or answer correctness.
"""


def completion_tokens(model, prompt):
    if not isinstance(prompt, str) or not prompt:
        raise ValueError("Completion accounting requires a nonempty string without a suffix")
    vocab = model._model
    bos, cls, sep = model.token_bos(), vocab.token_cls(), vocab.token_sep()
    prefix = [cls if cls != -1 else bos]
    if not vocab.add_bos_token() or prefix == [-1]:
        prefix = []
    suffix = [sep if sep != -1 else model.token_eos()]
    if not vocab.add_eos_token() and sep == -1:
        suffix = []
    return prefix + model.tokenize(prompt.encode("utf-8"), add_bos=False, special=True) + suffix
