"""Post-hoc gate-removal replay on fixed, no-repair primary candidates.

No model calls or changed drafts: deliver every executable saved candidate.
This does not measure fresh no-review inference, latency, or token savings.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'research/tier16_v2/data/case_outcomes.csv'
OUTPUT = ROOT / 'research/paper/data/gate_ablation.json'


def summarize(rows):
    results = []
    arm_ids = []
    for arm in ('sas', 'mas'):
        cases = [r for r in rows if r['profile'] == 'primary' and r['arm'] == arm]
        ids = {r['case_id'] for r in cases}
        if len(cases) != 160 or len(ids) != 160:
            raise ValueError('Expected exactly 160 unique primary questions per arm')
        arm_ids.append(ids)
        for metric in ('reported', 'raw'):
            for gate in (True, False):
                counts = Counter()
                for row in cases:
                    if row['repair_attempted'] != 'False':
                        raise ValueError('Fixed-candidate replay requires no repairs')
                    valid = row['execution_valid'] == 'True'
                    delivered = row['delivered'] == 'True'
                    if delivered and not valid:
                        raise ValueError('Delivered candidate must be executable')
                    if gate:
                        state = row[metric + '_outcome']
                        expected = ('correct' if row[metric + '_correct'] == 'True' else 'wrong') if delivered else 'withheld'
                        if state != expected:
                            raise ValueError('Saved outcome inconsistent with delivery/correctness')
                    else:
                        state = ('correct' if row[metric + '_correct'] == 'True' else 'wrong') if valid else 'withheld'
                    counts[state] += 1
                results.append({'arm': arm, 'metric': metric,
                                'review_gate': 'on' if gate else 'off', 'n': len(cases),
                                **{s: counts[s] for s in ('correct', 'wrong', 'withheld')}})
    if arm_ids[0] != arm_ids[1]:
        raise ValueError('Primary arms must contain the same question IDs')
    return results


if __name__ == '__main__':
    with SOURCE.open(newline='', encoding='utf-8') as stream:
        results = summarize(list(csv.DictReader(stream)))
    payload = {'analysis': 'post_hoc_fixed_candidate_gate_removal',
               'source': SOURCE.relative_to(ROOT).as_posix(),
               'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               'new_model_calls': 0,
               'limitations': 'Same saved executable candidates; no new draft generation, resource measurements, or inference-time no-review experiment.',
               'results': results}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(results, indent=2))
