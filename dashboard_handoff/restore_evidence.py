"""Verify or restore all SSD evidence, including content-deduplicated files."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract', type=Path, help='Restore original relative paths here; omit to verify only.')
    args = parser.parse_args()
    summary = json.loads((BASE/'export_summary.json').read_text(encoding='utf-8'))
    inventory = json.loads((BASE/'source_inventory.json').read_text(encoding='utf-8'))
    for archive in summary['archives']:
        path = BASE/archive['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == archive['sha256'], path
    count = 0
    for name in sorted({e['archive'] for e in inventory}):
        with zipfile.ZipFile(BASE/name) as z:
            for entry in (e for e in inventory if e['archive'] == name):
                data = z.read(entry['archive_entry'])
                assert len(data) == entry['bytes'], entry['source']
                assert hashlib.sha256(data).hexdigest() == entry['sha256'], entry['source']
                if args.extract:
                    target = (args.extract/entry['source']).resolve()
                    if not target.is_relative_to(args.extract.resolve()):
                        raise ValueError('Unsafe archive path')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if target.exists() and target.read_bytes() != data:
                        raise FileExistsError(f'Refusing to overwrite different content: {target}')
                    target.write_bytes(data)
                count += 1
    print(f'Verified {count} source files across {len(summary["archives"])} archives.' +
          (f' Restored to {args.extract.resolve()}.' if args.extract else ''))


if __name__ == '__main__':
    main()
