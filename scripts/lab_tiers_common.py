"""Small offline lab primitives; all run artifacts are SSD-relative."""
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    temporary.replace(path)


def append(path, value):
    with path.open('a') as f:
        f.write(json.dumps(value, sort_keys=True) + '\n')
        f.flush()
        os.fsync(f.fileno())


def ssd_root(value=None):
    p = Path(value or os.environ['AGERE_SSD_ROOT']).resolve(strict=True)
    if not (p / 'datasets').is_dir() or not (p / 'weights').is_dir():
        raise ValueError('Not an existing AGERE SSD: ' + str(p))
    return p


def inside(ssd, relative):
    if Path(relative).is_absolute():
        raise ValueError('Manifest paths must be SSD-relative')
    p = (ssd / relative).resolve()
    if not p.is_relative_to(ssd):
        raise ValueError('Path escapes SSD')
    return p


def fingerprint(path):
    s = path.stat()
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def verify(path, digest, cache):
    before = fingerprint(path)
    key = str(path)
    if cache.get(key) != [before, digest]:
        actual = sha(path)
        if fingerprint(path) != before or actual != digest:
            raise ValueError('Changed input: ' + str(path))
        cache[key] = [before, digest]


def run_id(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', value):
        raise ValueError('Unsafe run ID')
    return value


def completed_cases(path, expected_ids, repair_tail=False):
    """Require an exact ordered prefix. Preserve a torn last write before repair."""
    if not path.exists():
        return []
    data = path.read_bytes()
    lines = data.splitlines(keepends=True)
    records, valid = [], b''
    for i, line in enumerate(lines):
        try:
            record = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            if not repair_tail or i != len(lines) - 1 or line.endswith(b'\n'):
                raise ValueError('Corrupt completed-case ledger: ' + str(path))
            saved = path.with_name(path.name + '.torn-' + str(time.time_ns()))
            saved.write_bytes(line)
            temporary = path.with_suffix('.recovered')
            temporary.write_bytes(valid)
            temporary.replace(path)
            break
        if len(records) >= len(expected_ids) or record['case_id'] != expected_ids[len(records)]:
            raise ValueError('Cases are not the exact unique frozen prefix')
        records.append(record)
        valid += line
    if repair_tail and valid and not valid.endswith(b'\n'):
        with path.open('ab') as f:
            f.write(b'\n')
            f.flush()
            os.fsync(f.fileno())
    return records


def gguf_file_type(path):
    """Read the file-type metadata without loading any tensors."""
    formats = {0: 'B', 1: 'b', 2: 'H', 3: 'h', 4: 'I', 5: 'i', 6: 'f', 7: '?', 10: 'Q', 11: 'q', 12: 'd'}
    with path.open('rb') as f:
        def number(fmt):
            raw = f.read(struct.calcsize('<' + fmt))
            if len(raw) != struct.calcsize('<' + fmt):
                raise ValueError('Truncated GGUF metadata')
            return struct.unpack('<' + fmt, raw)[0]
        def string():
            n = number('Q')
            if n > 16 * 1024 * 1024:
                raise ValueError('Unreasonable GGUF string')
            raw = f.read(n)
            if len(raw) != n:
                raise ValueError('Truncated GGUF string')
            return raw.decode('utf8', errors='replace')
        def value(kind, depth=0):
            if kind in formats:
                return number(formats[kind])
            if kind == 8:
                return string()
            if kind == 9 and depth < 2:
                subtype, n = number('I'), number('Q')
                if n > 10000000:
                    raise ValueError('Unreasonable GGUF array')
                for _ in range(n):
                    value(subtype, depth + 1)
                return None
            raise ValueError('Unsupported GGUF metadata type')
        if f.read(4) != b'GGUF' or number('I') not in (2, 3):
            raise ValueError('Not a supported GGUF')
        number('Q')
        fields = number('Q')
        if fields > 1000000:
            raise ValueError('Unreasonable GGUF field count')
        for _ in range(fields):
            name, kind = string(), number('I')
            result = value(kind)
            if name == 'general.file_type':
                return result
    raise ValueError('GGUF file type missing')
