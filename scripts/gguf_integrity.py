"""Read GGUF metadata and tensor extents without loading tensor payloads.

Restricted to the F16/F32 and K-quant tensor formats emitted by our pinned
Qwen F16/Q4_K_M pipeline. Extent validation detects truncation; SHA-256
manifests remain necessary to detect content corruption.
"""
import math
from pathlib import Path
import struct


def inspect_gguf(path: Path) -> dict:
    length = path.stat().st_size
    scalar_sizes = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
    tensor_sizes = {0: (1, 4), 1: (1, 2), 12: (256, 144), 13: (256, 176), 14: (256, 210)}
    with path.open('rb') as stream:
        def read(n):
            if n < 0 or stream.tell() + n > length:
                raise ValueError('Truncated GGUF metadata')
            value = stream.read(n)
            if len(value) != n:
                raise ValueError('Short GGUF read')
            return value

        def number(fmt):
            return struct.unpack('<' + fmt, read(struct.calcsize('<' + fmt)))[0]

        def string():
            size = number('Q')
            if size > 16 * 1024 * 1024:
                raise ValueError('Unreasonable GGUF string size')
            return read(size).decode('utf-8', errors='replace')

        def skip(kind, depth=0):
            if kind in scalar_sizes:
                read(scalar_sizes[kind])
            elif kind == 8:
                string()
            elif kind == 9 and depth < 2:
                subtype, count = number('I'), number('Q')
                if count > 10_000_000:
                    raise ValueError('Unreasonable metadata array')
                if subtype in scalar_sizes:
                    size = count * scalar_sizes[subtype]
                    if stream.tell() + size > length:
                        raise ValueError('Truncated metadata array')
                    stream.seek(size, 1)
                else:
                    for _ in range(count):
                        skip(subtype, depth + 1)
            else:
                raise ValueError(f'Unsupported GGUF metadata type {kind}')

        if read(4) != b'GGUF' or number('I') not in (2, 3):
            raise ValueError('Not a supported little-endian GGUF')
        tensors, fields = number('Q'), number('Q')
        if not 0 < tensors < 1_000_000 or fields > 1_000_000:
            raise ValueError('Invalid GGUF counts')
        alignment = 32
        for _ in range(fields):
            name, kind = string(), number('I')
            if name == 'general.alignment':
                if kind != 4:
                    raise ValueError('Invalid alignment type')
                alignment = number('I')
            else:
                skip(kind)
        if not alignment or alignment > 4096 or alignment & (alignment - 1):
            raise ValueError('Invalid GGUF alignment')
        extents = []
        for _ in range(tensors):
            string()
            dimensions = number('I')
            if not 1 <= dimensions <= 4:
                raise ValueError('Invalid tensor dimensions')
            shape = [number('Q') for _ in range(dimensions)]
            kind, offset = number('I'), number('Q')
            if kind not in tensor_sizes or not all(shape):
                raise ValueError(f'Unsupported tensor type or shape: {kind}, {shape}')
            block, size = tensor_sizes[kind]
            if math.prod(shape) % block or offset % alignment:
                raise ValueError('Invalid tensor alignment or block size')
            extents.append((offset, offset + math.prod(shape) // block * size))
        data_start = (stream.tell() + alignment - 1) // alignment * alignment
        end = data_start + max(end for _, end in extents)
        previous_end = 0
        for start, finish in sorted(extents):
            if start < previous_end:
                raise ValueError('Overlapping tensors')
            previous_end = finish
        if end > length:
            raise ValueError(f'Truncated tensor payload: need {end} bytes, found {length}')
        return {'tensor_count': tensors, 'required_bytes': end, 'actual_bytes': length}
