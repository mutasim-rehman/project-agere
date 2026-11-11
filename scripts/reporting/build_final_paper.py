"""Offline paper audit and figures; never invokes a model or edits source results.

Restore evidence with dashboard_handoff/restore_evidence.py first.
Usage: python scripts/reporting/build_final_paper.py --evidence PATH
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/final_aaai'
def read(p): return json.loads(Path(p).read_bytes())
def rows(p):
    with Path(p).open(encoding='utf-8-sig') as f:
        for line in f:
            if line.strip(): yield json.loads(line)
def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cluster_interval(values, groups, seed=42, draws=10000):
    keys=sorted(set(groups)); ix=[np.where(np.array(groups)==k)[0] for k in keys]
    sums=np.array([sum(np.array(values)[i]) for i in ix]); sizes=np.array([len(i) for i in ix])
    choices=np.random.default_rng(seed).integers(len(keys),size=(draws,len(keys)))
    estimates=sums[choices].sum(axis=1)/sizes[choices].sum(axis=1)
    return np.quantile(estimates,[.025,.975]).tolist()
def tex(s):
    return str(s).replace('\\', '/').replace('_', r'\_').replace('&',r'\&').replace('%',r'\%').replace('#',r'\#')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True);a=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'figures').mkdir(exist_ok=True)
    inv=[]; summaries=[]; parse_errors=[]
    # Inventory every research artifact and all preserved external artifacts.
    for base in [ROOT/'research', a.evidence]:
        for p in sorted(base.rglob('*')):
            if not p.is_file(): continue
            label=('repository/'+str(p.relative_to(ROOT)) if base==ROOT/'research' else 'preserved/'+str(p.relative_to(base))).replace('\\','/')
            inv.append(dict(path=label,bytes=p.stat().st_size,sha256=digest(p)))
            if p.suffix=='.json':
                try:
                    obj=read(p)
                    if any(k in p.name.lower() for k in ['summary','result','score','analysis','complete']):
                        # Keep entire summaries, including unfavorable and failed records.
                        summaries.append(dict(path=label,content=obj))
                except Exception as e: parse_errors.append(dict(path=label,error=str(e)))
    inv.append(dict(path='repository/DECISIONS.md',bytes=(ROOT/'DECISIONS.md').stat().st_size,sha256=digest(ROOT/'DECISIONS.md')))
    save('artifact_inventory.json',inv);save('all_result_summaries.json',summaries)
    save('artifact_parse_issues.json',parse_errors)
    run=a.evidence/'runs/lab_tiers_v1/lab-16-ubuntu-noswap-v1'
    case_export=read(ROOT/'dashboard_handoff/data/tier16_ubuntu/case_outcomes.json')
    js={x['job']:x for x in read(ROOT/'dashboard_handoff/data/tier16_ubuntu/job_summaries.json')}
    records={}; metrics={}; memory_count=0; memory_peak=0; attempts=0
    for p in sorted(run.glob('tier16-*/cases.jsonl')):
        job=p.parent.name; rr=list(rows(p)); records[job]=rr
        assert len(rr)==160 and len({r['case_id'] for r in rr})==160
        expected={r['case_id']:r for r in case_export if r['job']==job}
        for r in rr:
            ex=expected[r['case_id']]; assert r['delivered']==ex['delivered']
            assert r['score']['case_success']==ex['reported_correct']
            assert r['score']['raw_execution_match']==ex['raw_correct']
            assert sum(s['generated_tokens'] for s in r['stages'])==ex['generated_tokens']<=2048
        groups=['/'.join(r['case_id'].split('/')[:2]) for r in rr]
        d={}
        for metric in ['case_success','raw_execution_match']:
            c=sum(r['delivered'] and r['score'][metric] for r in rr)
            w=sum(r['delivered'] and not r['score'][metric] for r in rr)
            h=sum(not r['delivered'] for r in rr)
            assert (c,w,h)==tuple(js[job]['full'][metric][k] for k in ['correct_delivered','wrong_delivered','withheld'])
            d[metric]=dict(correct=c,wrong=w,withheld=h,candidate_correct=sum(r['initial_score'][metric] for r in rr),
                          correct_ci=cluster_interval([int(r['delivered'] and r['score'][metric]) for r in rr],groups))
        d['median_seconds']=float(np.median([sum(s['seconds'] for s in r['stages']) for r in rr]))
        d['inference_hours']=sum(sum(s['seconds'] for s in r['stages']) for r in rr)/3600
        d['peak_rss']=js[job]['sampled_peak_tree_rss_bytes'];metrics[job]=d
    assert len(records)==6
    ref=next(iter(records.values()));assert all([r['case_id'] for r in v]==[r['case_id'] for r in ref] for v in records.values())
    for p in run.glob('tier16-*/attempts/*/memory.jsonl'):
        attempts+=1
        for r in rows(p):
            memory_count+=1;rss=r['tree_rss_bytes'];memory_peak=max(memory_peak,rss)
            assert 0<rss<=11500000000 and r['tree_swap_bytes']==0
    # Some sealed versions place memory logs directly under attempt directories.
    if not attempts:
        for p in run.glob('tier16-*/attempt-*/memory.jsonl'):
            attempts+=1
            for r in rows(p):
                memory_count+=1;rss=r['tree_rss_bytes'];memory_peak=max(memory_peak,rss)
                assert 0<rss<=11500000000 and r['tree_swap_bytes']==0
    paired={}
    assert memory_count==668817 and attempts==16
    assert len({'/'.join(r['case_id'].split('/')[:2]) for r in ref})==50
    assert len({r['case_id'].split('/')[0] for r in ref})==36
    for profile in ['primary','direct_control','repair_ablation']:
        sas=records['tier16-sas-'+profile];mas=records['tier16-mas-'+profile]
        for metric in ['case_success','raw_execution_match']:
            dif=[int(m['delivered'] and m['score'][metric])-int(s['delivered'] and s['score'][metric]) for s,m in zip(sas,mas)]
            groups=['/'.join(r['case_id'].split('/')[:2]) for r in sas]
            paired[profile+'/'+metric]=dict(delta=float(np.mean(dif)),report_ci=cluster_interval(dif,groups),company_ci=cluster_interval(dif,[g.split('/')[0] for g in groups]))
    save('verified_tier16.json',dict(metrics=metrics,paired=paired,memory_samples=memory_count,attempts=attempts,peak_rss=memory_peak))
    # Independently re-score all saved TAT-QA predictions with the pinned official evaluator.
    sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(OUT/'vendor/tatqa'))
    import tier8_windows_planner_study as ps
    import tatqa_metric
    wp=ROOT/'research/tier8_v2/evidence/windows-planner-study'
    planner={}
    for split in ['dev','test']:
        cohort=list(rows(wp/f'tatqa-heldout-{split}-cohort.jsonl'))
        labels={q['uid']:q for t in read(OUT/f'vendor/tatqa/tatqa_dataset_{split}.json') for q in t['questions']}
        cases={};times={}
        for arm in ['mas','planner']:
            ledger=list(rows(wp/f'tatqa-{split}-{arm}-cases.jsonl'))
            assert [r['case_id'] for r in ledger]==[r['id'] for r in cohort]
            for r in ledger:
                pred=ps.candidate(r['initial_answer'],r['initial_execution'])
                correct,_=ps.scores(tatqa_metric,labels[r['case_id']],pred)
                outcome='withheld' if not r['delivered'] else 'correct' if correct else 'wrong'
                cases.setdefault(r['case_id'],{})[arm]=dict(candidate_correct=correct,outcome=outcome)
                assert r['tokens']==sum(s['generated_tokens'] for s in r['stages'])<=960
            times[arm]=[sum(s['elapsed_seconds'] for s in r['stages']) for r in ledger]
        if split=='dev':
            saved=read(wp/'tatqa-dev-scores.json')
            for arm in ['mas','planner']:
                saved_arm='planner_mas' if arm=='planner' else arm
                for r in saved['cases']:
                    assert all(cases[r['case_id']][arm][k]==r['arms'][saved_arm][k] for k in ['candidate_correct','outcome'])
            for r in rows(wp/'tatqa-dev-large-cases.jsonl'):
                for arm,key in [('direct7b','direct_large'),('program7b','program')]:
                    pred=r['arms'][key]['prediction'];correct,_=ps.scores(tatqa_metric,labels[r['case_id']],pred)
                    cases[r['case_id']][arm]=dict(candidate_correct=correct,outcome='withheld' if pred is None else 'correct' if correct else 'wrong')
                assert all(cases[r['case_id']][arm]['outcome']==next(c for c in saved['cases'] if c['case_id']==r['case_id'])['arms'][arm]['outcome'] for arm in ['direct7b','program7b'])
        counts={arm:dict(Counter(c[arm]['outcome'] for c in cases.values())) for arm in next(iter(cases.values()))}
        contrasts={}
        for kind in ['correct','wrong','candidate_correct']:
            def flag(x): return x['candidate_correct'] if kind=='candidate_correct' else x['outcome']==kind
            contrasts[kind]=ps.paired([flag(c['mas']) for c in cases.values()],[flag(c['planner']) for c in cases.values()])
        transitions=Counter(c['mas']['outcome']+' -> '+c['planner']['outcome'] for c in cases.values())
        planner[split]=dict(n=len(cases),counts=counts,contrasts=contrasts,transitions=dict(transitions),cases=cases,latency_seconds=times)
    save('verified_planner.json',planner)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42})
    colors=['#007C91','#C45438','#CBD2D8']
    fig,axes=plt.subplots(1,2,figsize=(7,2.7),layout='constrained')
    names=['SAS primary','MAS primary','SAS direct','MAS direct','SAS repair','MAS repair']
    keys=[f'tier16-{arm}-{pr}' for pr in ['primary','direct_control','repair_ablation'] for arm in ['sas','mas']]
    for ax,metric,title in zip(axes,['case_success','raw_execution_match'],['Reported-answer match','Raw execution match']):
        left=np.zeros(6)
        for col,k in zip(colors,['correct','wrong','withheld']):
            v=np.array([metrics[j][metric][k] for j in keys]);ax.barh(names,v/160*100,left=left/160*100,color=col,label=k.capitalize())
            for i,n in enumerate(v):
                if n>=10:ax.text((left[i]+n/2)/160*100,i,str(n),ha='center',va='center',fontsize=8,color='white' if k!='withheld' else '#26313A')
            left+=v
        ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xlabel('Share of 160 questions (%)');ax.set_title(title)
    axes[1].legend(loc='upper center',bbox_to_anchor=(.35,-.22),ncol=3,frameon=False)
    fig.savefig(OUT/'figures/tier16_outcomes.pdf',bbox_inches='tight');plt.close(fig)
    saved=read(wp/'tatqa-dev-scores.json')
    fig,axes=plt.subplots(1,2,figsize=(7,2.7),layout='constrained')
    aa=['direct7b','program7b','mas','planner_mas']; nn=['Direct 7B','Program 7B','MAS','Planner MAS']
    left=np.zeros(4)
    for col,k in zip(colors,['correct','wrong','withheld']):
        v=np.array([saved['counts'][x][k] for x in aa]);axes[0].barh(nn,v,left=left,color=col,label=k.capitalize())
        for i,n in enumerate(v):
            if n>3:axes[0].text(left[i]+n/2,i,str(n),ha='center',va='center',fontsize=8,color='white' if k!='withheld' else '#26313A')
        left+=v
    axes[0].invert_yaxis();axes[0].set_xlim(0,96);axes[0].set_xlabel('Questions (n = 96)');axes[0].set_title('Held-out delivery')
    xx=np.arange(2)
    candidate_counts=[saved['counts'][x]['candidate_correct'] for x in ['mas','planner_mas']]
    delivery_counts=[saved['counts'][x]['correct'] for x in ['mas','planner_mas']]
    axes[1].bar(xx-.18,candidate_counts,width=.36,color='#637B94',label='Correct candidate')
    axes[1].bar(xx+.18,delivery_counts,width=.36,color=colors[0],label='Correct delivery')
    for x,ys in [(xx-.18,candidate_counts),(xx+.18,delivery_counts)]:
        for i,y in zip(x,ys):axes[1].text(i,y+.5,str(y),ha='center',fontsize=8)
    axes[1].set_xticks(xx,['MAS','Planner MAS']);axes[1].set_ylim(0,34);axes[1].set_title('Candidate versus delivery');axes[1].set_ylabel('Correct answers / 96');axes[1].legend(frameon=False,fontsize=8)
    fig.savefig(OUT/'figures/planner_outcomes.pdf',bbox_inches='tight');plt.close(fig)
    cc=saved['planner_contrasts']['mas'];fig,ax=plt.subplots(figsize=(3.35,2.25),layout='constrained')
    for i,(k,l) in enumerate([('correct','Correct delivery'),('wrong','Wrong delivery'),('candidate_correct','Correct candidate'),('shape_match','Tree match (n=87)')]):
        q=cc[k];v=q['rate_delta']*100;lo,hi=np.array(q['paired_context_bootstrap_95'])*100
        ax.errorbar(v,i,xerr=[[v-lo],[hi-v]],fmt='o',color=colors[1] if k=='wrong' else colors[0],capsize=3)
    ax.set_yticks(range(4),['Correct delivery','Wrong delivery','Correct candidate','Tree match (n=87)']);ax.invert_yaxis();ax.axvline(0,color='#999999',lw=.8);ax.set_xlabel('Planner minus MAS (percentage points)')
    fig.savefig(OUT/'figures/planner_effects.pdf',bbox_inches='tight');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(7,2.55),layout='constrained')
    for i,arm in enumerate(['mas','planner']):
        t=planner['dev']['latency_seconds'][arm]
        axes[0].boxplot(t,positions=[i],widths=.5,showfliers=False,patch_artist=True,boxprops=dict(facecolor=colors[0] if i==0 else '#637B94'))
    axes[0].set_xticks([0,1],['MAS','Planner MAS']);axes[0].set_ylabel('Request time (seconds)');axes[0].set_title('Resident pair: 96 contexts')
    vv=[saved['resources'][x]['peak_job_commit']/1e9 for x in aa]
    axes[1].bar(nn,vv,color=['#8799AC','#8799AC',colors[0],colors[0]])
    axes[1].axhline(6.1,color=colors[1],ls='--',label='6.1 GB job limit');axes[1].set_ylim(0,7);axes[1].set_ylabel('Peak worker commit (decimal GB)');axes[1].tick_params(axis='x',labelsize=8);axes[1].legend(frameon=False,fontsize=8)
    fig.savefig(OUT/'figures/resources.pdf',bbox_inches='tight');plt.close(fig)
    # Historical result census: every exported condition, both scoring conventions.
    hist=read(ROOT/'dashboard_handoff/data/le16_v2/tier8_condition_inventory.json')
    lines=[r'\begin{longtable}{p{.55\textwidth}rrrr}',r'\caption{Historical Linux 8 GB condition census. R: reported; X: raw execution. C/W/H retain all cases. These overlapping development, selection and diagnostic conditions are not independent replications.}\\',r'Condition / metric & $n$ & C & W & H\\\hline\endfirsthead',r'Condition / metric & $n$ & C & W & H\\\hline\endhead']
    for x in hist:lines.append(tex(x['job'])+' / '+('R' if x['metric']=='case_success' else 'X')+f" & {x['n']} & {x['correct']} & {x['wrong']} & {x['withheld']} "+r'\\')
    lines.append(r'\end{longtable}');(OUT/'historical_inventory.tex').write_text('\n'.join(lines),encoding='utf-8')
    save('audit_summary.json',dict(evidence_files=len(inv),result_documents=len(summaries),parse_issues=len(parse_errors),tier16_cases=960,memory_samples=memory_count,attempts=attempts,planner_primary_contexts=96,planner_secondary_contexts=28,inference_calls=0))
    print(json.dumps(read(OUT/'audit_summary.json'),indent=2))
if __name__=='__main__':main()
