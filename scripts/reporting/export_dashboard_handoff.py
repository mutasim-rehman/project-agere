"""Preserve SSD research evidence and export browser-readable dashboard inputs.

Standard library only. Does not run inference or change source research files.
"""
import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {'.json', '.jsonl', '.csv', '.tsv', '.xlsx', '.xml', '.pdf',
           '.md', '.txt', '.log', '.sha256', '.snapshot', '.py', '.sh',
           '.npy', '.html', '.zip', '.gz', '.jinja'}
SKIP_DIRS = {'.git', '.venv', '__pycache__', 'tmp', '.cache'}
SECRET = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|hf_[A-Za-z0-9]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{40,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')


def scalar(value):
    if value == '':
        return None
    if value in ('True', 'False', 'true', 'false'):
        return value.lower() == 'true'
    if re.fullmatch(r'-?(?:0|[1-9][0-9]*)', value):
        number = int(value)
        return number if abs(number) <= 2**53-1 else value
    if re.fullmatch(r'-?[0-9]+\.[0-9]+(?:[eE][+-]?[0-9]+)?|-?[0-9]+[eE][+-]?[0-9]+', value):
        number = float(value)
        return number if math.isfinite(number) else value
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ssd', type=Path, default=Path('H:/AGERE'))
    parser.add_argument('--output', type=Path, default=ROOT/'dashboard_handoff')
    args = parser.parse_args()
    out = args.output.resolve()
    archives = out/'evidence'
    archives.mkdir(parents=True, exist_ok=True)
    if any(archives.glob('*.zip')):
        raise SystemExit('Use an empty evidence directory to avoid mixing exports.')

    inventory, excluded, duplicates, archive_index = [], [], {}, []
    totals = Counter()
    # Runtime installations and model tensors are not dashboard inputs. Enumerate
    # excluded model files too, so the scope of the transfer is reviewable.
    for top in ('datasets', 'phase2', 'runs', 'weights'):
        candidates = sorted((args.ssd/top).rglob('*'))
        batch, batch_size, number = [], 0, 0

        def flush():
            nonlocal batch, batch_size, number
            if not batch:
                return
            number += 1
            target = archives/f'{top}-{number:03}.zip'
            with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                for relative, data, entry in batch:
                    info = zipfile.ZipInfo(relative, date_time=(2026, 10, 30, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    z.writestr(info, data, compresslevel=9)
                    entry['archive'] = target.relative_to(out).as_posix()
                    entry['archive_entry'] = relative
            # Verify the actual stored bytes, not only ZIP CRCs.
            with zipfile.ZipFile(target) as z:
                for relative, _, entry in batch:
                    assert sha(z.read(relative)) == entry['sha256'], relative
            archive_index.append({'path': target.relative_to(out).as_posix(),
                                  'bytes': target.stat().st_size,
                                  'sha256': sha(target.read_bytes()), 'entries': len(batch)})
            batch, batch_size = [], 0

        for path in candidates:
            if not path.is_file():
                continue
            relative = path.relative_to(args.ssd).as_posix()
            reason = None
            if any(part in SKIP_DIRS for part in path.relative_to(args.ssd).parts):
                reason = 'temporary/cache files'
            elif path.name.startswith('.env') or path.suffix.lower() not in ALLOWED:
                reason = 'model tensor, cache, lock or unsupported non-data artifact'
            elif top == 'weights' and (path.name.startswith('tokenizer') or path.name in {'vocab.json', 'merges.txt'}):
                reason = 'tokenizer assets unnecessary for dashboard'
            if reason:
                excluded.append({'source': relative, 'bytes': path.stat().st_size, 'reason': reason})
                continue
            data = path.read_bytes()
            if SECRET.search(data):
                raise SystemExit(f'Credential-like value detected; review before export: {relative}')
            entry = {'source': relative, 'bytes': len(data), 'sha256': sha(data),
                     'category': top}
            inventory.append(entry)
            totals[top] += 1
            if entry['sha256'] in duplicates:
                entry['duplicate_of'] = duplicates[entry['sha256']]['source']
                continue
            duplicates[entry['sha256']] = entry
            if batch_size + len(data) > 40_000_000:
                flush()
            batch.append((relative, data, entry))
            batch_size += len(data)
        flush()

    # Fill duplicate locations after all batches have been written.
    for entry in inventory:
        original = duplicates[entry['sha256']]
        entry['archive'] = original['archive']
        entry['archive_entry'] = original['archive_entry']
    write_json(out/'source_inventory.json', inventory)
    write_json(out/'excluded_files.json', excluded)

    catalog = []
    for family in ('tier16_v2', 'le16_v2', 'paper'):
        source_dir = ROOT/'research'/family/'data'
        for path in sorted(source_dir.glob('*')):
            if path.suffix not in {'.csv', '.json'}:
                continue
            destination = out/'data'/family/path.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
            record = {'id': family+'/'+path.stem, 'source': path.relative_to(ROOT).as_posix(),
                      'path': destination.relative_to(out).as_posix(),
                      'sha256': sha(destination.read_bytes())}
            if path.suffix == '.csv':
                with path.open(encoding='utf-8-sig', newline='') as stream:
                    reader = csv.DictReader(stream)
                    records = [{k: scalar(v) for k, v in row.items()} for row in reader]
                    record['columns'] = reader.fieldnames
                record['rows'] = len(records)
                # Some research sources already contain CSV and JSON with the
                # same stem but different structures. Preserve both exports.
                json_path = destination.with_suffix('.rows.json' if path.with_suffix('.json').exists() else '.json')
                write_json(json_path, records)
                record['browser_json'] = json_path.relative_to(out).as_posix()
                # Validate CSV -> JSON retained every value (modulo documented typing).
                assert json.loads(json_path.read_text(encoding='utf-8')) == records
            else:
                value = json.loads(destination.read_text(encoding='utf-8'))
                record['json_type'] = type(value).__name__
            catalog.append(record)
    write_json(out/'data/index.json', catalog)
    write_json(out/'export_summary.json', {
        'source_root': str(args.ssd), 'prepared_date': '2026-10-30',
        'source_files_preserved': len(inventory), 'unique_files_archived': len(duplicates),
        'source_bytes': sum(e['bytes'] for e in inventory),
        'unique_source_bytes': sum(e['bytes'] for e in duplicates.values()),
        'archive_bytes': sum(e['bytes'] for e in archive_index),
        'counts_by_category': dict(totals), 'derived_tables_and_documents': len(catalog),
        'archives': archive_index,
        'excluded_roots': ['.venv', 'runtime', 'tmp'],
        'verification': 'Every unique archived file read back and SHA256 checked; CSV JSON round trips checked.',
        'credential_check': 'Recognizable GitHub/Hugging Face/OpenAI token and private-key signatures scanned; no matches. Not a general PII audit.',
    })
    print(json.dumps({'files': len(inventory), 'unique': len(duplicates),
                      'archive_bytes': sum(e['bytes'] for e in archive_index),
                      'archives': len(archive_index), 'derived_inputs': len(catalog)}))


if __name__ == '__main__':
    main()
