"""Analyze complete paired critic probes with report-group uncertainty."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random


def analyze(labels,responses):
    by_id={r['id']:r for r in labels}
    if len(by_id)!=len(labels):raise ValueError('Duplicate labels')
    groups=defaultdict(list)
    for r in labels:groups[r['report_group']].append(r['id'])
    if any(sorted(by_id[i]['expected_accept'] for i in ids)!=[False,True] for ids in groups.values()):raise ValueError('Every report needs exactly one positive and one negative')
    out={'n_programs':len(labels),'n_report_groups':len(groups),'profiles':{}}
    for profile,rows in responses.items():
        keyed={(r['id'],r['protocol']):r for r in rows}
        expected={(i,p) for i in by_id for p in ['rich','binary']}
        if len(keyed)!=len(rows) or set(keyed)!=expected:raise ValueError('Missing/duplicate/unexpected probe responses')
        summary={}
        for protocol in ['rich','binary']:
            accepted={i:keyed[(i,protocol)]['verdict']=='PASS' for i in by_id}
            tp=sum(accepted[i] and by_id[i]['expected_accept'] for i in by_id)
            fp=sum(accepted[i] and not by_id[i]['expected_accept'] for i in by_id)
            full_pairs=0;both_accepted=0;both_rejected=0;inverted=0
            for ids in groups.values():
                pos=next(i for i in ids if by_id[i]['expected_accept']);neg=next(i for i in ids if not by_id[i]['expected_accept'])
                a,b=accepted[pos],accepted[neg]
                full_pairs+=int(a and not b);both_accepted+=int(a and b);both_rejected+=int(not a and not b);inverted+=int(not a and b)
            events=[keyed[(i,protocol)]['event'] for i in by_id]
            summary[protocol]={'reference_accepts':tp,'incorrect_mutation_accepts':fp,'reference_rejects':len(groups)-tp,'incorrect_mutation_rejects':len(groups)-fp,'complete_pair_discriminations':full_pairs,'both_accepted_pairs':both_accepted,'both_rejected_pairs':both_rejected,'inverted_pairs':inverted,'gate_accuracy':(tp+len(groups)-fp)/len(labels),'generated_tokens':sum(e['generated_tokens'] for e in events),'prompt_tokens':sum(e['prompt_tokens'] for e in events),'inference_seconds':sum(e['seconds'] for e in events)}
        deltas=[]
        for ids in groups.values():
            changes=[]
            for i in ids:
                correct=lambda p:(keyed[(i,p)]['verdict']=='PASS')==by_id[i]['expected_accept']
                changes.append(int(correct('binary'))-int(correct('rich')))
            deltas.append(sum(changes)/2)
        rng=random.Random(42)
        sampled=sorted(sum(rng.choices(deltas,k=len(deltas)))/len(deltas) for _ in range(10000))
        out['profiles'][profile]={'protocols':summary,'binary_minus_rich_gate_accuracy':sum(deltas)/len(deltas),'report_cluster_bootstrap_95_interval':[sampled[249],sampled[9749]],'new_reference_accepts':summary['binary']['reference_accepts']-summary['rich']['reference_accepts'],'additional_incorrect_mutation_accepts':summary['binary']['incorrect_mutation_accepts']-summary['rich']['incorrect_mutation_accepts']}
    out['limits']='Controlled train-validation mutations; reference labels not independently semantically adjudicated. UNKNOWN/unparsed count as nonaccept for gate metrics, not proof of a correct explicit rejection. Bootstrap resamples report pairs (10000,seed42); only12 groups in planned experiment. Protocol and instructions both change. This is not a novel method, natural-error QA improvement or full MAS memory measurement.'
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    root=Path(a.run).resolve();out=Path(a.out).resolve()
    if out.exists():raise ValueError('Refuse overwrite')
    manifest=json.loads((root/'manifest.json').read_text())
    if manifest['status']!='complete' or any(p['status']!='complete' or p['exit_code']!=0 or p['peak_tree_rss_bytes']>manifest['cap_bytes'] for p in manifest['profiles'].values()):raise ValueError('Need complete memory-valid run')
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    for name,key in [('public.jsonl','public_sha256'),('labels.jsonl','labels_sha256')]:
        if digest(root/name)!=manifest[key]:raise ValueError('Frozen probe data changed')
    load=lambda p:[json.loads(s) for s in p.read_text().splitlines()]
    paths={profile:root/f'{profile}-responses.jsonl' for profile in manifest['profiles']}
    result=analyze(load(root/'labels.jsonl'),{k:load(v) for k,v in paths.items()})
    result.update({'run':str(root),'source_manifest_sha256':digest(root/'manifest.json'),'response_sha256':{k:digest(v) for k,v in paths.items()},'analysis_source_sha256':digest(Path(__file__)),'memory':{k:{'peak_tree_rss_bytes':v['peak_tree_rss_bytes'],'cap_bytes':v['cap_bytes']} for k,v in manifest['profiles'].items()}})
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
