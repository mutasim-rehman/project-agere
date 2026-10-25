"""Offline matched-critic audit; does not alter verdicts, scores or delivery gates."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def analyze(left,right):
    def keyed(rows):
        ids=[r['case_id'] for r in rows]
        if len(set(ids))!=len(ids):raise ValueError('Duplicate case IDs')
        return dict(zip(ids,rows))
    a,b=keyed(left),keyed(right)
    if set(a)!=set(b):raise ValueError('Unpaired case cohorts')
    result={'n':len(a),'identical_initial_plans':0,'identical_verifier_prompts':0,'arms':{}}
    for k in a:
        if a[k]['initial_plan']!=b[k]['initial_plan']:raise ValueError('Draft plans changed; cannot isolate critic')
        result['identical_initial_plans']+=1
        prompts=[]
        for row in [a[k],b[k]]:
            stages=[s for s in row['stages'] if s['stage']=='verify_program']
            if len(stages)!=1:raise ValueError('Expected one initial verification stage')
            prompts.append(stages[0]['prompt'])
        if prompts[0]!=prompts[1]:raise ValueError('Critic inputs changed')
        result['identical_verifier_prompts']+=1
    for label,rows in [('left',left),('right',right)]:
        signature=Counter();dimensions={k:Counter() for k in ['operands','operations','units']}
        contradictory=0;true_accept=0;false_accept=0;true_reject=0;false_reject=0;unparsed=0
        for row in rows:
            v=row['initial_verdict'];correct=bool(row['initial_score']['case_success'])
            if not isinstance(v,dict):unparsed+=1;accepted=False
            else:
                checks=v.get('checks',{});signature[json.dumps(checks,sort_keys=True)]+=1
                for k in dimensions:dimensions[k][checks.get(k,'MISSING')]+=1
                contradictory+=int(v.get('repair_kind')=='NONE' and any(checks.get(k)!='PASS' for k in dimensions))
                accepted=v.get('verdict')=='PASS'
            true_accept+=int(correct and accepted);false_accept+=int(not correct and accepted)
            true_reject+=int(not correct and not accepted);false_reject+=int(correct and not accepted)
        result['arms'][label]={'checks_signature_counts':dict(signature),'dimension_counts':{k:dict(v) for k,v in dimensions.items()},'repair_NONE_with_nonPASS_check':contradictory,'unparsed':unparsed,'true_accept':true_accept,'false_accept':false_accept,'true_reject':true_reject,'false_reject':false_reject,'delivered_correct':sum(r['delivered'] and r['score']['case_success'] for r in rows),'delivered_incorrect':sum(r['delivered'] and not r['score']['case_success'] for r in rows)}
    result['interpretation']='Matched local development diagnostic. Numerical answer correctness is not semantic proof. Repair NONE with a nonPASS check violates the stated prompt, but is not itself evidence that the rejection is wrong. Do not infer larger-model verification capability from size alone.'
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--left',required=True);p.add_argument('--right',required=True);p.add_argument('--out',required=True);args=p.parse_args()
    paths=[(ROOT/v).resolve() for v in [args.left,args.right,args.out]]
    if any(not v.is_relative_to(ROOT) for v in paths):raise ValueError('Audit paths must stay in repository')
    left,right,out=paths
    if out.exists():raise ValueError('Refuse overwrite')
    rows=lambda path:[json.loads(s) for s in path.read_text().splitlines()]
    result=analyze(rows(left),rows(right))
    result['input_sha256']={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [left,right]}
    result['audit_source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
