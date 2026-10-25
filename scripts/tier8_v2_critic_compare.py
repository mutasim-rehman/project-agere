"""Paired binary critic comparison on exactly frozen controlled inputs."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import random
from tier8_artifact_paths import artifact_path


def compare(labels,left,right):
    target={r['id']:r for r in labels}
    if len(target)!=len(labels):raise ValueError('Duplicate label IDs')
    groups=defaultdict(list)
    for r in labels:groups[r['report_group']].append(r['id'])
    if any(sorted(target[i]['expected_accept'] for i in ids)!=[False,True] for ids in groups.values()):raise ValueError('Need one positive/negative per report')
    def keyed(rows):
        if any(r['protocol']!='binary' for r in rows):raise ValueError('Binary-only comparison')
        out={r['id']:r for r in rows}
        if len(out)!=len(rows) or set(out)!=set(target):raise ValueError('Incomplete/duplicate matched cases')
        return out
    a,b=keyed(left),keyed(right)
    if any(a[i]['event']['prompt']!=b[i]['event']['prompt'] for i in target):raise ValueError('Critic prompts changed')
    result={'n_programs':len(target),'n_report_groups':len(groups),'conditions':{}}
    for name,rows in [('plain',a),('adapted',b)]:
        accept=lambda i:rows[i]['verdict']=='PASS'
        tp=sum(accept(i) and target[i]['expected_accept'] for i in target);fp=sum(accept(i) and not target[i]['expected_accept'] for i in target)
        separated=sum(all(accept(i)==target[i]['expected_accept'] for i in ids) for ids in groups.values())
        result['conditions'][name]={'reference_accepts':tp,'incorrect_mutation_accepts':fp,'reference_nonaccepts':len(groups)-tp,'incorrect_mutation_nonaccepts':len(groups)-fp,'complete_pair_discriminations':separated,'verdict_counts':dict(Counter(r['verdict'] or 'UNPARSED' for r in rows.values())),'gate_accuracy':(tp+len(groups)-fp)/len(target),'generated_tokens':sum(r['event']['generated_tokens'] for r in rows.values()),'prompt_tokens':sum(r['event']['prompt_tokens'] for r in rows.values())}
    deltas=[]
    for ids in groups.values():
        correct=lambda rows,i:(rows[i]['verdict']=='PASS')==target[i]['expected_accept']
        deltas.append(sum(int(correct(b,i))-int(correct(a,i)) for i in ids)/2)
    rng=random.Random(42);samples=sorted(sum(rng.choices(deltas,k=len(deltas)))/len(deltas) for _ in range(10000))
    result.update(delta_gate_accuracy=sum(deltas)/len(deltas),report_cluster_bootstrap_95_interval=[samples[249],samples[9749]],limits='Controlled train-validation mutations; not natural errors or independently adjudicated semantics. UNKNOWN counts as nonaccept, not an explicit correct negative judgment. Degenerate intervals do not prove equivalence. Known-method adaptation, not novelty.')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--left',required=True);p.add_argument('--right',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    left,right,out=map(artifact_path,[a.left,a.right,a.out])
    if out.exists():raise ValueError('Refuse overwrite')
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    manifests=[json.loads((r/'manifest.json').read_text()) for r in [left,right]]
    for root,m in zip([left,right],manifests):
        if m['status']!='complete' or set(m['profiles'])!={'3b'} or m['protocols']!=['binary']:raise ValueError('Need complete 3B binary runs')
        profile=m['profiles']['3b']
        if profile['status']!='complete' or profile['exit_code']!=0 or profile['peak_tree_rss_bytes']>m['cap_bytes']:raise ValueError('Memory-invalid run')
        if digest(root/'public.jsonl')!=m['public_sha256'] or digest(root/'labels.jsonl')!=m['labels_sha256']:raise ValueError('Inputs changed')
    for key in ['public_sha256','labels_sha256','source_sha256','context','max_tokens_per_protocol','cap_bytes']:
        if manifests[0][key]!=manifests[1][key]:raise ValueError('Unmatched condition: '+key)
    if manifests[0]['models']['3b']['sha256']!=manifests[1]['models']['3b']['sha256'] or manifests[0]['adapter'] is not None or not manifests[1]['adapter']:raise ValueError('Need matched base versus applied adapter')
    load=lambda p:[json.loads(s) for s in p.read_text().splitlines()]
    result=compare(load(left/'labels.jsonl'),load(left/'3b-responses.jsonl'),load(right/'3b-responses.jsonl'))
    result.update(runs={'plain':str(left),'adapted':str(right)},manifest_sha256={str(r):digest(r/'manifest.json') for r in [left,right]},analysis_source_sha256=digest(Path(__file__)))
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
