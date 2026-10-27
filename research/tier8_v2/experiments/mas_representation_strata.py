"""Post-hoc descriptive stratification of completed MAS policies; no exclusions.

Categories depend on reference programs and are NOT deployment features. No
training, inference, threshold fitting, semantic adjudication or metric changes.
"""
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SSD=Path('/run/media/mutasim/Data/AGERE')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def outcome(row,metric):
    return ('correct_delivered' if row['score'][metric] else 'wrong_delivered') if row['delivered'] else 'withheld'


def main():
    audit=SSD/'runs/tier8_representation_audit/model-selection-01';ap=audit/'cases.jsonl'
    source={r['id']:r for r in map(json.loads,ap.read_text().splitlines())}
    source_summary=json.loads((audit/'summary.json').read_text())
    if sha(ap)!=source_summary['details_sha256'] or len(source)!=52:raise ValueError('Reference audit differs')
    seq=SSD/'runs/tier8_matched_continuation/matched-study-01'
    pair_paths=[seq/'independent-model-selection-mas-pair-01.json',seq/'model_selection-crossed_mas-vs-baseline_original_critic_common_actor.json']
    pairs=[json.loads(p.read_text()) for p in pair_paths]
    if any(not p['all_prompts_execution_delivery_scores_and_token_ledgers_replayed'] for p in pairs):raise ValueError('Full policy replay required')
    policies={};tables={};inputs=[Path(__file__),ap,audit/'summary.json',*pair_paths]
    metrics=['case_success','raw_execution_match']
    for label,pair,side in [('control_mas',pairs[0],'left'),('crossed_mas',pairs[0],'right'),
                          ('baseline_original_critic_common_actor',pairs[1],'left')]:
        root=SSD/'runs/tier8_method_qa'/('model_selection-'+label+'-full-01');cases=root/'cases.jsonl';summary=json.loads((root/'summary.json').read_text())
        if summary['status']!='complete' or summary['n']!=52 or summary['exit_code'] or sha(cases)!=pair['input_sha256'][str(cases)]:raise ValueError('Incomplete or changed policy')
        rows=[json.loads(x) for x in cases.read_text().splitlines()];saved={r['case_id']:r for r in rows}
        if len(rows)!=len(saved) or set(saved)!=set(source):raise ValueError('Unpaired/duplicate coverage')
        policies[label]=saved;tables[label]={};inputs += [cases,root/'summary.json']
        for metric in metrics:
            groups=defaultdict(Counter)
            for key,r in saved.items():
                c=groups[source[key]['binding_status']];c['n']+=1;c[outcome(r,metric)]+=1
                c['initial_candidate_correct']+=bool(r['initial_score'][metric]);c['final_candidate_correct']+=bool(r['score'][metric])
            totals=Counter()
            for g in groups.values():totals.update(g)
            if totals['n']!=52:raise ValueError('Strata do not sum to full cohort')
            expected=pair['conditions'][side]['full']['metrics'][metric]
            if any(totals[k]!=expected[k] for k in ['correct_delivered','wrong_delivered','withheld']):raise ValueError('Strata do not recombine to audited outcomes')
            tables[label][metric]={k:dict(v) for k,v in groups.items()}
    transitions={}
    for left in ['control_mas','baseline_original_critic_common_actor']:
        transitions[left+' -> crossed_mas']={}
        for metric in metrics:
            groups=defaultdict(Counter)
            for key,r in policies[left].items():
                groups[source[key]['binding_status']][outcome(r,metric)+' -> '+outcome(policies['crossed_mas'][key],metric)]+=1
            transitions[left+' -> crossed_mas'][metric]={k:dict(v) for k,v in groups.items()}
    reports={k:len({r['report_group'] for r in source.values() if r['binding_status']==k}) for k in {r['binding_status'] for r in source.values()}}
    out=SSD/'runs/tier8_representation_audit/mas-policy-strata-01'
    if out.exists():raise ValueError('Fresh descriptive audit required')
    out.mkdir();details=out/'cases.jsonl';details.write_text(''.join(json.dumps({'id':key,'binding_status':a['binding_status'],'report_group':a['report_group'],'policies':{label:{'delivered':r[key]['delivered'],'score':r[key]['score'],'initial_score':r[key]['initial_score']} for label,r in policies.items()}},sort_keys=True)+'\n' for key,a in source.items()))
    result={'status':'complete_descriptive_posthoc_stratification','n':52,'reports':15,'reports_per_overlapping_stratum':reports,
        'policy_strata':tables,'transitions_by_stratum':transitions,'input_sha256':{str(p):sha(p) for p in inputs},
        'details_sha256':sha(details),'cases_excluded':0,'model_calls':0,'thresholds_or_scores_changed':False,
        'limits':'Post-hoc, reference-dependent exploratory strata; not an inference-time feature, new training target, causal mechanism proof, significance test or novelty. Direct annotated-program mapping is not task solvability/semantic certification. Report groups overlap across strata. All52 cases and original full metrics retained; do not use these labels for routing or selection-specific rules.'}
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'result':str(out),'n':52,'reports':15}))


if __name__=='__main__':main()
