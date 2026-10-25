"""Gold-free pool redundancy diagnostic on already-saved initial drafts.

No model calls, reference answers, saved scores or saved verdicts are consumed.
This is an exploratory reused-draft engineering diagnostic, not an evaluation of
repair quality, attainable accuracy or a claim of useful/novel improvement.
"""
import argparse
import hashlib
import json
from pathlib import Path

from evidence_atoms import atom_catalog
from source_repair_pool import local_pool
from source_program_quotient import partition
from tier8_artifact_paths import artifact_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public', required=True)
    parser.add_argument('--snapshots', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    public_path, snapshots, out = map(artifact_path, [args.public, args.snapshots, args.out])
    if out.exists():
        raise ValueError('No overwrite')
    public = {r['id']: r for r in map(json.loads, public_path.read_text().splitlines())}
    saved = [json.loads(line) for line in snapshots.read_text().splitlines()]
    if len({r['case_id'] for r in saved}) != len(saved):
        raise ValueError('Duplicate snapshots')
    rows = []
    for row in saved:
        p = public[row['case_id']]
        pool = local_pool(p, row['initial_plan'])
        groups = {mode: partition(pool['plans'], atom_catalog(p['evidence']), p['evidence'], mode=mode)
                  for mode in ('bytes', 'numeric', 'numeric_sources', 'source_symbolic')}
        counts = {mode: len(result['groups']) for mode, result in groups.items()}
        rows.append({'id': row['case_id'], 'candidates': len(pool['plans']), 'classes': counts,
                     'symbolic_representatives_first4': [g[0] for g in groups['source_symbolic']['groups'][:4]],
                     'byte_representatives_first4': [g[0] for g in groups['bytes']['groups'][:4]],
                     'all_symbolic_operations': groups['source_symbolic']['symbolic_operations']})
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    result = {'status': 'complete', 'n': len(rows), 'rows': rows,
              'total_candidates': sum(r['candidates'] for r in rows),
              'total_classes': {mode: sum(r['classes'][mode] for r in rows)
                                for mode in ('bytes', 'numeric', 'numeric_sources', 'source_symbolic')},
              'first4_representative_lists_changed': sum(r['symbolic_representatives_first4'] != r['byte_representatives_first4'] for r in rows),
              'input_sha256': {str(p): digest(p) for p in (public_path, snapshots)},
              'source_sha256': {str(p): digest(p) for p in (Path(__file__),
                    Path(__file__).with_name('source_repair_pool.py'), Path(__file__).with_name('source_program_quotient.py'))},
              'measured_reasoning_gain': False, 'novelty_established': False,
              'limitations': 'Reused24 initial drafts; no regeneration, scores, target answers or model inference. Class reduction alone does not imply a useful verification saving or quality gain.'}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'input_sha256', 'source_sha256')}))


if __name__ == '__main__':
    main()
