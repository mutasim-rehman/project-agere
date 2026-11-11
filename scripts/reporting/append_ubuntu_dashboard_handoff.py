"""Append the completed Ubuntu replication to an existing portable handoff.

No inference, paper updates, or replacement of the historical result tables.
The source is a local preservation tree with original SSD-relative paths.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import zipfile

from export_dashboard_handoff import SECRET, sha, write_json

RUN = 'lab-16-ubuntu-noswap-v1'
DATE = '2026-11-11'


def append_handoff(source, out):
    run = source / 'runs/lab_tiers_v1' / RUN
    manifest = json.loads((run / 'manifest.json').read_text())
    audit = json.loads((run / 'analysis/summary.json').read_text())
    preservation = json.loads((source / 'preservation.json').read_text())
    assert audit['status'] == 'complete_audited'
    assert sha((run / 'manifest.json').read_bytes()) == audit['manifest_sha256']
    for relative, expected in audit['evidence_sha256'].items():
        assert sha((run / relative).read_bytes()) == expected, relative
    for relative, expected in manifest['freeze']['code_sha256'].items():
        assert sha((run / 'code' / relative).read_bytes()) == expected, relative

    inventory = json.loads((out / 'source_inventory.json').read_text())
    summary = json.loads((out / 'export_summary.json').read_text())
    excluded = json.loads((out / 'excluded_files.json').read_text())
    excluded_sources = {e['source'] for e in excluded}
    by_source = {e['source']: e for e in inventory}
    by_hash = {e['sha256']: e for e in inventory}
    pending, batch, batch_bytes = [], [], 0
    additions = []

    def flush():
        nonlocal batch, batch_bytes
        if not batch:
            return
        number = 1
        while (out / f'evidence/ubuntu16-20261111-{number:03d}.zip').exists():
            number += 1
        name = f'evidence/ubuntu16-20261111-{number:03d}.zip'
        target = out / name
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for entry, data in batch:
                info = zipfile.ZipInfo(entry['source'], (2026, 11, 11, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, data, compresslevel=9)
                entry.update(archive=name, archive_entry=entry['source'])
        with zipfile.ZipFile(target) as z:
            for entry, _ in batch:
                assert sha(z.read(entry['source'])) == entry['sha256']
        additions.append({'path': name, 'bytes': target.stat().st_size,
                          'sha256': sha(target.read_bytes()), 'entries': len(batch)})
        batch, batch_bytes = [], 0

    for path in sorted(source.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(source).as_posix()
        if relative.split('/')[0] not in ('runs', 'datasets'):
            continue
        if path.suffix == '.lock' or path.name.startswith('preflight-marker-'):
            if relative not in excluded_sources:
                excluded.append({'source': relative, 'bytes': path.stat().st_size,
                                 'reason': 'Runtime lock or temporary preflight marker'})
            continue
        data = path.read_bytes()
        if SECRET.search(data):
            raise ValueError('Credential-like content: ' + relative)
        digest = sha(data)
        if relative in by_source:
            assert by_source[relative]['sha256'] == digest, 'Existing source changed: ' + relative
            continue
        entry = {'source': relative, 'bytes': len(data), 'sha256': digest,
                 'category': relative.split('/')[0]}
        if digest in by_hash:
            entry['duplicate_of'] = by_hash[digest]['source']
        else:
            if batch_bytes + len(data) > 40_000_000:
                flush()
            by_hash[digest] = entry
            batch.append((entry, data))
            batch_bytes += len(data)
        pending.append(entry)
    flush()
    for entry in pending:
        original = by_hash[entry['sha256']]
        entry.update(archive=original['archive'], archive_entry=original['archive_entry'])
    inventory += pending
    for entry in inventory:
        prefix = f'runs/lab_tiers_v1/{RUN}/'
        if entry['source'].startswith(prefix):
            relative = entry['source'][len(prefix):]
            if relative in preservation['reconstructed_replay_sha256']:
                entry['preservation_origin'] = 'Reconstructed from saved traces; exact original audit SHA256 match'
            elif relative == 'analysis/REPORT.md':
                entry['preservation_origin'] = 'Regenerated from original sealed analysis code; no original report hash available'
    write_json(out / 'source_inventory.json', inventory)
    write_json(out / 'excluded_files.json', excluded)

    data_dir = out / 'data/tier16_ubuntu'
    catalog = [e for e in json.loads((out / 'data/index.json').read_text())
               if not e['id'].startswith('tier16_ubuntu/')]
    # Git normalized the Windows export's text files to LF. Keep the original
    # export digest while making catalog hashes describe actual checked-out bytes.
    for entry in catalog:
        data = (out / entry['path']).read_bytes()
        digest = sha(data)
        if digest != entry['sha256']:
            assert sha(data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')) == entry['sha256'], entry['path']
            entry['original_export_sha256'] = entry['sha256']
            entry['sha256'] = digest
            entry['checkout_line_endings'] = 'LF; original Windows export used CRLF'

    def table(name, value, source_name):
        path = data_dir / (name + '.json')
        write_json(path, value)
        item = {'id': 'tier16_ubuntu/' + name, 'source': source_name,
                'path': path.relative_to(out).as_posix(), 'sha256': sha(path.read_bytes()),
                'json_type': type(value).__name__, 'run_id': RUN}
        if isinstance(value, list):
            item.update(rows=len(value), browser_json=item['path'])
        catalog.append(item)

    cases, stages, resources, jobs = [], [], [], []
    ids = manifest['protocol']['dataset']['ids']
    for job, result in sorted(audit['summaries'].items()):
        records = [json.loads(line) for line in (run / job / 'cases.jsonl').read_text().splitlines()]
        assert [r['case_id'] for r in records] == ids
        assert result['n'] == 160 and result['status'] == 'complete'
        jobs.append({'run_id': RUN, 'job': job, **result})
        for row in records:
            def outcome(metric):
                return 'withheld' if not row['delivered'] else 'correct' if row['score'][metric] else 'wrong'
            cases.append({'run_id': RUN, 'tier': 16, 'job': job, 'arm': row['arm'],
                          'profile': job.split('-', 2)[2], 'case_id': row['case_id'],
                          'report': row['case_id'].rsplit('/', 1)[0],
                          'company': row['case_id'].split('/')[0], 'delivered': row['delivered'],
                          'reported_correct': row['score']['case_success'],
                          'raw_correct': row['score']['raw_execution_match'],
                          'reported_outcome': outcome('case_success'), 'raw_outcome': outcome('raw_execution_match'),
                          'initial_reported_correct': row['initial_score']['case_success'],
                          'initial_raw_correct': row['initial_score']['raw_execution_match'],
                          'repair_attempted': row.get('repair_attempted', False),
                          'generated_tokens': row['tokens'],
                          'prompt_tokens': sum(s['prompt_tokens'] for s in row['stages']),
                          'inference_seconds': sum(s['seconds'] for s in row['stages']),
                          'attempt': row['attempt'], 'completed_time': row['completed_time']})
            for stage in row['stages']:
                stages.append({'run_id': RUN, 'job': job, 'case_id': row['case_id'],
                               **{k: stage[k] for k in ('stage', 'role', 'seconds', 'prompt_tokens',
                                  'generated_tokens', 'finish_reason', 'requested_tokens', 'effective_limit')
                                  if k in stage}})
        for attempt in sorted((run / job).glob('attempt-*')):
            state = json.loads((attempt / 'state.json').read_text())
            assert not state.get('memory_breach') and not state.get('swap_breach')
            resources.append({'run_id': RUN, 'job': job, 'attempt': attempt.name, **state})
    for job in jobs:
        subset = [r for r in cases if r['job'] == job['job']]
        for metric, field in [('case_success', 'reported_outcome'), ('raw_execution_match', 'raw_outcome')]:
            actual = Counter(r[field] for r in subset)
            assert job['full'][metric] == {'correct_delivered': actual['correct'],
                                          'wrong_delivered': actual['wrong'], 'withheld': actual['withheld']}
    for name, value in [('case_outcomes', cases), ('job_summaries', jobs), ('stage_metrics', stages),
                        ('resource_events', resources), ('audited_analysis', audit), ('manifest', manifest)]:
        table(name, value, f'runs/lab_tiers_v1/{RUN}/')
    table('preservation', preservation, 'Local preservation audit; see evidence inventory')
    write_json(out / 'data/index.json', catalog)
    if 'historical_export' not in summary:
        summary['historical_export'] = {k: summary[k] for k in
                                        ('prepared_date', 'source_root', 'source_files_preserved', 'archive_bytes')}
    summary['archives'] += additions
    summary.update(prepared_date=DATE, latest_source_root=preservation['source_root'],
                   source_files_preserved=len(inventory), unique_files_archived=len(by_hash),
                   source_bytes=sum(e['bytes'] for e in inventory),
                   unique_source_bytes=sum(e['bytes'] for e in by_hash.values()),
                   archive_bytes=sum(e['bytes'] for e in summary['archives']),
                   counts_by_category=dict(Counter(e['category'] for e in inventory)),
                   derived_tables_and_documents=len(catalog), ubuntu_replication=preservation)
    write_json(out / 'export_summary.json', summary)
    print(json.dumps({'added_sources': len(pending), 'new_archives': len(additions),
                      'case_outputs': len(cases), 'stage_rows': len(stages)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--handoff', type=Path, default=Path('dashboard_handoff'))
    args = parser.parse_args()
    append_handoff(args.source.resolve(), args.handoff.resolve())
