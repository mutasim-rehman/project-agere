"""Paired delivery/withholding analysis for a frozen-drafter critic comparison.

Report both existing numerical metrics and illustrative error penalties; never
select a favorable penalty or confuse withheld-all precision with correctness.
"""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import random

from tier8_artifact_paths import artifact_path
from tier8_v2_demo_retrieval import report_group
from tier8_v2_posttrain_queue import natural_pair

PENALTIES=(0,1,2,5,10)


def analyze(left,right,condition_names=('plain','adapted')):
    if (not isinstance(condition_names,(tuple,list)) or len(condition_names)!=2 or any(not isinstance(n,str) or not n for n in condition_names)
            or condition_names[0]==condition_names[1]):raise ValueError('Need two distinct nonempty condition names')
    left_name,right_name=condition_names
    def keyed(rows):
        out={r['case_id']:r for r in rows}
        if not rows or len(out)!=len(rows):raise ValueError('Need unique nonempty cases')
        for r in rows:
            if type(r['delivered']) is not bool or r['tokens']!=sum(s['generated_tokens'] for s in r['stages']):raise ValueError('Invalid delivery flag/token accounting')
        return out
    a,b=keyed(left),keyed(right)
    if set(a)!=set(b):raise ValueError('Unpaired delivery cases')
    ids=sorted(a);groups=defaultdict(list)
    for i in ids:groups[report_group(i)].append(i)
    result={'n':len(ids),'n_report_groups':len(groups),'metrics':{},
            'condition_names':{'left':left_name,'right':right_name},'delta_direction':'right_minus_left'}
    for metric in ['case_success','raw_execution_match']:
        if any(a[i]['score'][metric]!=b[i]['score'][metric] for i in ids):raise ValueError('Candidate correctness changed; not a pure gate comparison')
        outcome=lambda r:'correct_delivery' if r['delivered'] and r['score'][metric] else 'incorrect_delivery' if r['delivered'] else 'withheld'
        counts={name:Counter(outcome(row) for row in rows.values()) for name,rows in [(left_name,a),(right_name,b)]}
        conditions={}
        for name,rows in [(left_name,a),(right_name,b)]:
            c=counts[name];delivered=c['correct_delivery']+c['incorrect_delivery']
            conditions[name]={'candidate_correct':sum(r['score'][metric] for r in rows.values()),'correct_delivered':c['correct_delivery'],'incorrect_delivered':c['incorrect_delivery'],'withheld':c['withheld'],'correct_delivery_coverage':c['correct_delivery']/len(ids),'incorrect_delivery_rate':c['incorrect_delivery']/len(ids),'precision_when_delivered':c['correct_delivery']/delivered if delivered else None,'generated_tokens':sum(r['tokens'] for r in rows.values()),'prompt_tokens':sum(s.get('prompt_tokens',0) for r in rows.values() for s in r['stages']),'recorded_inference_seconds':sum(s.get('seconds',0) for r in rows.values() for s in r['stages'])}
        dc=counts[right_name]['correct_delivery']-counts[left_name]['correct_delivery'];di=counts[right_name]['incorrect_delivery']-counts[left_name]['incorrect_delivery']
        changes={i:{key:int(outcome(b[i])==key)-int(outcome(a[i])==key) for key in ['correct_delivery','incorrect_delivery','withheld']} for i in ids}
        distributions={key:[] for key in ['correct_delivery','incorrect_delivery','withheld']};utilities={p:[] for p in PENALTIES}
        rng=random.Random(42);clusters=list(groups.values())
        for _ in range(10000):
            sampled=[i for cluster in rng.choices(clusters,k=len(clusters)) for i in cluster]
            total={key:sum(changes[i][key] for i in sampled)/len(sampled) for key in distributions}
            for key in distributions:distributions[key].append(total[key])
            for penalty in PENALTIES:utilities[penalty].append(total['correct_delivery']-penalty*total['incorrect_delivery'])
        interval=lambda values:[sorted(values)[249],sorted(values)[9749]]
        result['metrics'][metric]={'conditions':conditions,'delta_correct_delivery_coverage':dc/len(ids),'delta_incorrect_delivery_rate':di/len(ids),'report_cluster_bootstrap_95_intervals':{key:interval(values) for key,values in distributions.items()},'transitions':dict(Counter(outcome(a[i])+' -> '+outcome(b[i]) for i in ids)),'empirical_delivery_pareto_dominance':dc>=0 and di<=0 and (dc>0 or di<0),'illustrative_utility_delta':{str(p):{'per_case':(dc-p*di)/len(ids),'report_cluster_bootstrap_95_interval':interval(utilities[p])} for p in PENALTIES},'break_even_penalty_ratio':dc/di if di else None,'utility_expression_counts':f'{dc} - lambda * ({di})'}
    result['limits']='Development analysis, not publication confirmation. Report bootstrap uses whole reports, including unequal cluster sizes. Candidate accuracy must be identical. Non-delivery has illustrative utility0; wrong-delivery penalties0/1/2/5/10 are not validated financial costs and none is selected as primary. Zero-delivery precision is undefined, not100%. Sample Pareto dominance is descriptive; intervals may be degenerate and do not establish equivalence.'
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--left',required=True);p.add_argument('--right',required=True);p.add_argument('--out',required=True)
    p.add_argument('--comparison-kind',choices=['plain-trained','trained-variants'],default='plain-trained')
    p.add_argument('--left-proof');p.add_argument('--right-proof');p.add_argument('--left-label');p.add_argument('--right-label');a=p.parse_args()
    if a.comparison_kind=='trained-variants':
        if not a.left_proof or not a.right_proof:p.error('Two trained critics require both application proofs')
        names=(a.left_label or 'trained_control',a.right_label or 'trained_candidate')
        if any(n.lower() in ['plain','untrained'] for n in names):p.error('Do not label a trained critic plain or untrained')
    else:
        if a.left_proof or a.right_proof:p.error('Proof arguments require trained-variants mode')
        names=(a.left_label or 'plain',a.right_label or 'adapted')
    if names[0]==names[1]:p.error('Need distinct condition labels')
    left,right,out=map(artifact_path,[a.left,a.right,a.out])
    if out.exists():raise ValueError('Refuse overwrite')
    rows=[]
    for root in [left,right]:
        summary=json.loads((root/'summary.json').read_text());manifest=json.loads((root/'manifest.json').read_text())
        data=[json.loads(s) for s in (root/'cases.jsonl').read_text().splitlines()]
        if summary['status']!='complete' or summary['exit_code']!=0 or len(data)!=summary['n'] or summary['n']!=summary['expected'] or summary['peak_tree_rss_bytes']>summary['cap_bytes'] or manifest['config']['repair']!='none':raise ValueError('Need complete memory-valid no-repair conditions')
        rows.append(data)
    if a.comparison_kind=='trained-variants':
        from tier8_v2_critic_policy_pair import trained_pair
        matching=trained_pair(str(left),str(right),a.left_proof,a.right_proof)
        guard=Path(__file__).with_name('tier8_v2_critic_policy_pair.py')
    else:
        matching=natural_pair(str(left),str(right));guard=Path(__file__).with_name('tier8_v2_posttrain_queue.py')
    result=analyze(*rows,condition_names=names)
    result['comparison_kind']=a.comparison_kind
    result['matching_guard']=matching;result['runs']={names[0]:str(left),names[1]:str(right)}
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    result['input_sha256']={str(root/name):digest(root/name) for root in [left,right] for name in ['manifest.json','summary.json','cases.jsonl']}
    result['analysis_source_sha256']=digest(Path(__file__))
    result['guard_source_sha256']=digest(guard)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
