"""Scoped Transformers compatibility shim for safetensors' public pread backend.

Transformers4.57.1 does not forward a safetensors backend choice. Its module-local
safe_open reference is replaced only during synchronous from_pretrained and then
restored, including on failure. No library file or tensor value is modified.
Model loading must be serial in this process. This is memory engineering only.
"""
from contextlib import contextmanager


@contextmanager
def pread_checkpoint_loading():
    from transformers import modeling_utils
    original = modeling_utils.safe_open

    def read_owned(*args, **kwargs):
        if kwargs.get('backend', 'pread') != 'pread':
            raise ValueError('Conflicting checkpoint backend')
        return original(*args, **dict(kwargs, backend='pread'))

    modeling_utils.safe_open = read_owned
    try:
        yield
    finally:
        modeling_utils.safe_open = original
