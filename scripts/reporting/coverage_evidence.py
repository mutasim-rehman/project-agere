"""Reconcile restoration with saved predictions; generate tables/plots without inference.

python scripts/reporting/coverage_evidence.py --evidence D:/.../paper-evidence
Original manuscripts and experimental artifacts are read-only.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, csv, hashlib, json, math, re, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import binomtest, chi2
import paper_statistical_tests as tests
import analyze_completed_tiers as old

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'paper/revised_aaai'
def read(p): return json.loads(Path(p).read_bytes())
def rows(p): return [json.loads(s) for s in Path(p).read_text(encoding='utf-8-sig').splitlines() if s.strip()]
def save(name,obj):
    def clean(x):
        if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [clean(v) for v in x]
        if isinstance(x,float) and not math.isfinite(x):return None
        return x
    # Undefined statistics remain undefined (null), rather than nonstandard JSON NaN.
    (OUT/name).write_text(json.dumps(clean(obj),indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def esc(s): return str(s).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&').replace('#',r'\#')
def fmt(v):
    if not math.isfinite(v): return '--'
    return f'{v:.3g}' if v<.001 else f'{v:.3f}'
def ci(v):return '['+', '.join(f'{100*x:+.2f}' for x in v)+']'
def table(name, caption, cols, heads, data, label=None):
    s=[r'\begin{longtable}{'+cols+'}',r'\caption{'+caption+'}'+(r'\label{'+label+'}' if label else '')+r'\\',
       ' & '.join(heads)+r'\\\toprule\endfirsthead',' & '.join(heads)+r'\\\toprule\endhead']
    s += [' & '.join(str(x) for x in row)+r'\\' for row in data]
    s += [r'\bottomrule\end{longtable}']
    (OUT/name).write_text('\n'.join(s),encoding='utf-8')
def assert_close(a,b,at=''):
    if isinstance(a,dict):
        assert set(a)==set(b),at
        for k in a:assert_close(a[k],b[k],at+'/'+k)
    elif isinstance(a,list):
        assert len(a)==len(b),at
        for i,(x,y) in enumerate(zip(a,b)):assert_close(x,y,at+'/'+str(i))
    elif isinstance(a,(float,int)) and not isinstance(a,bool):
        assert (math.isnan(a) and math.isnan(b)) or np.isclose(a,b,rtol=1e-10,atol=1e-13), (at,a,b)
    else:assert a==b,(at,a,b)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True);args=ap.parse_args();ev=args.evidence
    audit={'inference_calls':0,'input_hashes':{},'checks':[]}
    def raw(p):
        audit['input_hashes'][str(p.relative_to(ev))]=hashlib.sha256(p.read_bytes()).hexdigest();return rows(p)
    runs={}
    for run in ['lab-16-115gb-recovery-02','lab-16-ubuntu-noswap-v1']:
        runs[run]={p.parent.name:raw(p) for p in sorted((ev/'runs/lab_tiers_v1'/run).glob('tier16-*/cases.jsonl'))}
    hist=runs['lab-16-115gb-recovery-02'];new=runs['lab-16-ubuntu-noswap-v1']
    derived=tests.load(ROOT/'research/tier16_v2/data/case_outcomes.csv','job')
    for job,rr in hist.items():
        assert len(rr)==160
        nn={r['case_id']:r for r in new[job]}
        for r in rr:
            d=derived[job][r['case_id']]
            assert (d['delivered']=='True')==r['delivered']
            for met,col in [('case_success','reported'),('raw_execution_match','raw')]:
                assert (d[col+'_correct']=='True')==r['score'][met]
                assert d[col+'_outcome']==old.outcome(r,met)
            assert r['score']==nn[r['case_id']]['score'] and r['delivered']==nn[r['case_id']]['delivered']
    audit['checks'].append('960 historical case rows match original ledgers and Ubuntu delivery/score objects')
    jobs8=tests.load(ROOT/'research/le16_v2/data/tier8_case_outcomes.csv','condition')
    sys.path.insert(0,str(ROOT/'scripts'))
    from tier8_v2_financial_pipeline import checked,evaluate_financial
    source8={r['id']:r for r in read(ev/'datasets/tier8_v2_natural/natural_reports62_01/source-train.json')}
    packets8={r['id']:r for cohort in ['model_selection','diagnostic_audit'] for r in rows(ev/f'datasets/tier8_v2_natural/natural_reports62_01/{cohort}-public.jsonl')}
    count8=0
    for job,jj in jobs8.items():
        rr=raw(ev/'runs/tier8_method_qa'/job/'cases.jsonl');assert set(jj)=={r['case_id'] for r in rr}
        for r in rr:
            execution=checked(r['answer'],packets8[r['case_id']]['evidence'])
            assert execution==r['execution'],(job,r['case_id'])
            score=evaluate_financial(source8[r['case_id']],r['answer'],execution)
            assert score==r['score'],(job,r['case_id'])
            for met,col in [('case_success','reported'),('raw_execution_match','raw')]:
                assert jj[r['case_id']][col+'_outcome']==old.outcome(r,met)
            count8+=1
    audit['checks'].append(f'{count8} historical FinQA programs re-executed/rescored from source packets and reconciled against all 15 raw condition ledgers')
    # Recompute all 21 comparisons; compare every field with the retained battery.
    stored=read(ROOT/'research/paper/data/paper_statistical_tests.json');battery={}
    for tier,jobs,defs in [('tier16',derived,tests.COMPARISONS_16),('tier8',jobs8,tests.COMPARISONS_8)]:
        battery[tier]={}
        for key,label,left,right in defs:
            battery[tier][key]={'label':label,'left':left,'right':right}
            for met in ['reported','raw']:
                res=tests.compare(jobs,left,right,met);assert_close(res,stored[tier][key][met],tier+'/'+key+'/'+met)
                battery[tier][key][met]=res
                for e in res['endpoints'].values():
                    b,c=e['b_right_only'],e['c_left_only'];p=binomtest(b,b+c,.5).pvalue if b+c else 1
                    assert np.isclose(p,e['exact_mcnemar_p'],rtol=1e-10,atol=1e-30)
                    if b+c:assert np.isclose(chi2.sf(e['chi2'],1),e['chi2_p'],rtol=1e-10,atol=1e-30)
    save('restored_test_battery.json',battery)
    audit['checks'].append('All 126 endpoint rows and 42 metric-specific transition/symmetry blocks independently recomputed; tails cross-checked with SciPy')
    pri={};published=read(ROOT/'research/tier16_v2/data/statistical_analysis.json')['comparisons']['primary']['endpoints']
    for met in ['case_success','raw_execution_match']:
        for event in ['correct','wrong']:
            k=met+'/'+event;q=old.paired(new['tier16-sas-primary'],new['tier16-mas-primary'],met,event)
            q['company_sensitivity']=old.paired(new['tier16-sas-primary'],new['tier16-mas-primary'],met,event,'company')
            for field in q:assert_close(q[field],published[k][field],k+'/'+field)
            pri[k]=q
    save('restored_primary_sensitivity.json',pri)
    audit['checks'].append('All four primary report/company bootstrap, 98.75% intervals, equal weighting, deletion ranges and sign-flip results reproduced from raw Ubuntu ledgers')
    data=[]
    for k,q in pri.items():
        label=('Reported' if k.startswith('case') else 'Raw')+' '+k.split('/')[1]
        data.append([label,f'{100*q["delta_rate"]:+.2f}',ci(q['bootstrap95']),ci(q['bonferroni4_bootstrap98_75']),ci(q['company_sensitivity']['bootstrap95'])])
    table('primary_intervals.tex','Four Study A endpoints: MAS minus SAS, percentage points. Intervals use 50 report clusters; company sensitivity uses 36. The four 98.75\\% marginal intervals target approximate family coverage, not an exact finite-sample guarantee.','lrrrr',['Endpoint',r'$\Delta$', 'Report 95\\%','Report 98.75\\%','Company 95\\%'],data,'tab:primary-ci')
    data=[]
    for k,q in pri.items():
        label=('Reported' if k.startswith('case') else 'Raw')+' '+k.split('/')[1]
        data.append([label,f'{100*q["cluster_equal_delta"]:+.2f}',ci(q['cluster_equal_bootstrap95']),ci(q['leave_one_cluster_out_range']),fmt(q['cluster_sign_flip']['p'])])
    table('primary_sensitivity.tex','Weighting and influence sensitivity. Equal-report weighting estimates a different target. Deletion ranges are not confidence intervals; sign-flip tests require null sign symmetry.','lrrrr',['Endpoint',r'Equal-report $\Delta$','95\\% interval','Leave-one-report range','Sign-flip $p$'],data)
    # Recompute old manuscript strata from raw gold and raw candidates.
    gold={r['id']:r for r in read(ev/'datasets/lab_tiers/finance_reports_v1/scoring-source.json')}
    strata={};stepcounts=Counter()
    for cid,g in gold.items():stepcounts[len(re.findall(r'([a-z_]+)\(',g['qa']['program']))]+=1
    for arm in ['sas','mas']:
        for r in new['tier16-'+arm+'-primary']:
            ops=re.findall(r'([a-z_]+)\(',gold[r['case_id']]['qa']['program']);n=len(ops)
            family='table aggregate' if any(x.startswith('table_') for x in ops) else 'single add/subtract' if n==1 and ops[0] in ['add','subtract'] else 'single ratio/product' if n==1 else 'multi-step arithmetic'
            for category in [('1 step' if n==1 else '2 steps' if n==2 else '3+ steps'),family]:
                cell=strata.setdefault(category,{}).setdefault(arm,Counter());cell[old.outcome(r,'case_success')]+=1
    save('restored_strata.json',strata)
    data=[]
    for cat in ['1 step','2 steps','3+ steps','single add/subtract','single ratio/product','multi-step arithmetic','table aggregate']:
        v=strata[cat];data.append([cat,sum(v['sas'].values()),' / '.join(str(v['sas'][k]) for k in old.OUTCOMES),' / '.join(str(v['mas'][k]) for k in old.OUTCOMES)])
    table('strata.tex','Study A primary reported-score outcomes by reference program (post hoc). Step and operation-family partitions overlap one another; do not sum across partitions.','lrrr',['Reference stratum','$n$','SAS C/W/H','MAS C/W/H'],data,'tab:strata')
    # Both run resources, directly from saved stage durations.
    resources={};stage_rows=[];resource_rows=[]
    for run,rd in runs.items():
        resources[run]={}
        for job,rr in rd.items():
            times=[sum(s['seconds'] for s in r['stages']) for r in rr];c=sum(r['delivered'] and r['score']['case_success'] for r in rr)
            stages=defaultdict(lambda:Counter(seconds=0,generated_tokens=0,prompt_tokens=0))
            for r in rr:
                for s in r['stages']:
                    for field in ['seconds','generated_tokens','prompt_tokens']:stages[s['role']+'/'+s['stage']][field]+=s[field]
            summary=read(ev/'runs/lab_tiers_v1'/run/job/'summary.json')
            q=dict(peak_rss_bytes=summary['sampled_peak_tree_rss_bytes'],case_latency_seconds=times,hours=sum(times)/3600,median_seconds=float(np.median(times)),mean_seconds=float(np.mean(times)),seconds_per_reported_correct=sum(times)/c if c else None,generated_tokens=sum(r['tokens'] for r in rr),stages=stages)
            resources[run][job]=q
            resource_rows.append(['Historical' if 'recovery' in run else 'Ubuntu',esc(job.replace('tier16-','').replace('_',' ')),f'{q["hours"]:.3f}',f'{q["median_seconds"]:.1f}','--' if c==0 else f'{q["seconds_per_reported_correct"]:.1f}',q['generated_tokens'],f'{q["peak_rss_bytes"]/1e9:.3f}'])
            if job.endswith('-primary'):
                for stage,v in stages.items():stage_rows.append(['Hist.' if 'recovery' in run else 'Ubuntu',job.split('-')[1].upper(),esc(stage),f'{v["seconds"]/3600:.3f}',v['generated_tokens'],v['prompt_tokens']])
    save('restored_resources.json',resources)
    table('resources_extended.tex','Timing and sampled-RSS reconciliation across original recovery and Ubuntu repeat. Summed inference excludes aborted work, model loading and restart overhead. Seconds per correct is amortized measured work, not expected retries to solve a question; undefined at zero correct.','llrrrrr',['Run','Recipe','Hours','Median s','s/correct','Output tok','RSS GB'],resource_rows,'tab:resource-reconcile')
    table('stages.tex','Primary stage totals in both runs. Prompt tokens count every call; they are not one context window. Stages execute sequentially while model weights remain resident.',r'llp{.31\textwidth}rrr',['Run','Arm','Stage','Hours','Output tok','Prompt tok'],stage_rows,'tab:stages')
    # Synthetic test summaries reconciled to saved per-case scores; no false claim of fresh scoring.
    synthetic={}
    sys.path.insert(0,str(ROOT/'scripts'))
    import phase3
    synth_cases={}
    for kind in ['kyc','credit']:
        for c in raw(ev/f'datasets/agere_synthetic/agere-synth-v1/test/{kind}.jsonl'):
            c['_kind']=kind;synth_cases[c['id']]=c
    for arm in ['sas','mas']:
        rr=raw(ev/f'runs/tier8/tier8-8gb-v1/test/final_{arm}/cases.jsonl');ss=read(ev/f'runs/tier8/tier8-8gb-v1/test/final_{arm}/summary.json')
        sc=[r['score'] for r in rr]
        for r in rr:
            c=synth_cases[r['case_id']]
            assert phase3.score_case(c,r['answer'],phase3.common_tools(c),arm)==r['score'],r['case_id']
        q={'n':len(rr),'json':sum(s['valid_json'] for s in sc),'claim_sets':sum(s['structured_claims_complete'] for s in sc),'invention':sum(s['structured_invention'] is True for s in sc),'grounded':sum(s['grounded'] for s in sc),'grounding_total':sum(s['grounding_total'] for s in sc),'mismatch_detected':sum(s['mismatch_detected'] for s in sc),'mismatch_total':sum(s['mismatch_eligible'] for s in sc),'refusal_correct':sum(s['refusal_correct'] for s in sc),'refusal_total':sum(s['refusal_total'] for s in sc),'tokens':sum(r['generated_tokens'] for r in rr),'seconds':sum(r['elapsed_seconds'] for r in rr),'peak_rss':max(r['peak_rss_bytes'] for r in rr)}
        assert q['n']==175 and np.isclose(q['json']/175,ss['valid_json_rate'])
        assert np.isclose(q['invention']/q['claim_sets'],ss['structured_invention_rate_among_complete_claim_sets'])
        assert np.isclose(q['grounded']/q['grounding_total'],ss['grounding_accuracy'])
        synthetic[arm]=q
    save('restored_synthetic.json',synthetic)
    audit['checks'].append('350 historical synthetic answers independently rescored with source documents/deterministic tools and re-aggregated, including unequal invention denominators and resource totals')
    # Restore the memory column absent from the shortened historical condition census.
    inventory=read(ROOT/'dashboard_handoff/data/le16_v2/tier8_condition_inventory.json')
    grouped={}
    for item in inventory:grouped.setdefault(item['job'],{})[item['metric']]=item
    data=[]
    for job,pair in sorted(grouped.items()):
        r,x=pair['case_success'],pair['raw_execution_match']
        ss=read(ev/'runs/tier8_method_qa'/job/'summary.json')
        assert r['peak_rss_bytes']==ss['peak_tree_rss_bytes'],job
        data.append([esc(job),r['n'],'/'.join(str(r[k]) for k in ['correct','wrong','withheld']),
                     '/'.join(str(x[k]) for k in ['correct','wrong','withheld']),f'{r["peak_rss_bytes"]/1e9:.3f}'])
    table('historical_inventory_extended.tex','All 15 earlier FinQA conditions, including sampled memory. Cohorts overlap; these are not 15 independent replications. Reported and raw C/W/H retain every case.',r'p{.40\textwidth}rllr',['Condition','$n$','Reported C/W/H','Raw C/W/H','RSS GB'],data,'tab:historical-conditions')
    # Examples preserve raw responses in JSON; presentation shortens explicitly.
    ids=['ABMD/2007/page_52.pdf-1','AAPL/2003/page_24.pdf-1','AAPL/2003/page_24.pdf-2','PNC/2018/page_171.pdf-1','ABMD/2007/page_52.pdf-2']
    examples=[]
    for cid in ids:
        item={'id':cid,'annotation':gold[cid]['qa'],'runs':{}}
        for run,rd in runs.items():item['runs'][run]={arm:next(r for r in rd['tier16-'+arm+'-primary'] if r['case_id']==cid) for arm in ['sas','mas']}
        examples.append(item)
    for arm in ['sas','mas']:
        rr=rows(ev/f'runs/tier8/tier8-8gb-v1/test/final_{arm}/cases.jsonl');examples.append({'synthetic_arm':arm,'record':next(r for r in rr if r['case_id']=='CR-TEST-0001')})
    save('worked_example_traces.json',examples)
    # Complete battery, generated from recomputed values, including raw 8 GB rows previously only in CSV.
    for tier in ['tier16','tier8']:
        legend=[];data=[];sym=[]
        for i,(key,comp) in enumerate(battery[tier].items(),1):
            legend.append(f'{i}. {comp["label"]}')
            for met in ['reported','raw']:
                res=comp[met];sy=res['symmetry'];sym.append([f'{i} '+met,f'{sy["bowker_q"]:.2f}',sy['bowker_df'],fmt(sy['bowker_p']),fmt(sy['stuart_maxwell_q']),sy['stuart_maxwell_df'],fmt(sy['stuart_maxwell_p'])])
                for event,e in res['endpoints'].items():
                    data.append([f'{i} '+('R' if met=='reported' else 'X')+' '+event,f'{e["left_events"]}/{e["right_events"]}',f'{e["b_right_only"]}/{e["c_left_only"]}',f'{100*e["delta"]:+.2f}',ci(e['report_bootstrap95']),fmt(e['exact_mcnemar_p']),fmt(e['report']['durkalski_p'])])
        table(f'battery_{tier}.tex',f'Complete {tier[4:]} GB paired endpoint battery. R: reported, X: raw; C/W/H are events. IDs are defined immediately above. All tests here are post-hoc, unadjusted sensitivity analyses; exact tests assume independent pairs, score tests independent clusters and a large-cluster approximation.', 'lrrrrrr',['ID / score / event','L/R','gain/loss',r'$\Delta$ pp','Report 95\\%','Exact $p$','Score $p$'],data,'tab:battery-'+tier)
        table(f'symmetry_{tier}.tex',f'{tier[4:]} GB full-transition diagnostics. Asymptotic case-IID assumptions may fail, especially with sparse off-diagonal cells. Rank-zero statistics are undefined, not evidence of equivalence.','lrrrrrr',['ID / score','Bowker Q','df','$p$','SM Q','rank','$p$'],sym)
        (OUT/f'legend_{tier}.tex').write_text('\n'.join(r'\noindent '+esc(s)+r'\par' for s in legend))
    # Primary CR1/score/sign statistics retained explicitly.
    data=[]
    primary=battery['tier16']['primary']
    for met in ['reported','raw']:
        for event in ['C','W']:
            e=primary[met]['endpoints'][event];r=e['report'];data.append([met+' '+event,f'{100*r["se_cr1"]:.2f}',f'{r["design_effect"]:.2f}',fmt(r['p_cr1']),fmt(r['durkalski_p']),fmt(e['company']['durkalski_p']),f'{r["clusters_right_higher"]}/{r["clusters_left_higher"]}/{r["clusters_tied"]}'])
    table('cluster_tests.tex','Primary supplemental cluster diagnostics. CR1 uses normal tails; score uses chi-square(1). Right/left/tied counts refer to report-level event-rate differences, not independent confirmations.','lrrrrrr',['Endpoint','CR1 SE pp','DEFF','CR1 $p$','Report score $p$','Company score $p$','R/L/tied'],data)
    # Distinct visual insights: transitions, report heterogeneity/strata, stage work, utility/risk.
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,ax=plt.subplots(1,2,figsize=(7,2.8),layout='constrained')
    for a,met in zip(ax,['reported','raw']):
        mat=np.array(primary[met]['transition_left_rows_right_cols']);a.imshow(mat,cmap='Blues',vmin=0,vmax=84)
        for (i,j),v in np.ndenumerate(mat):a.text(j,i,str(v),ha='center',va='center',color='white' if v>45 else 'black')
        a.set_xticks(range(3),['Correct','Wrong','Withheld']);a.set_yticks(range(3),['Correct','Wrong','Withheld']);a.set_xlabel('MAS');a.set_ylabel('SAS');a.set_title(met.capitalize())
    fig.savefig(OUT/'figures/restored_transitions.pdf');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(7,2.8),layout='constrained')
    groups=defaultdict(list)
    for cid,r in derived['tier16-sas-primary'].items():groups[r['report']].append(cid)
    points=Counter()
    for group,ids2 in groups.items():
        rates=tuple(sum(derived['tier16-'+a+'-primary'][c]['reported_outcome']=='correct' for c in ids2)/len(ids2) for a in ['sas','mas']);points[rates]+=1
    for (x,y),n in points.items():axs[0].scatter(x,y,s=20*n,color='#007f8b',alpha=.7)
    axs[0].plot([0,1],[0,1],ls='--',color='gray');axs[0].set(xlabel='SAS report correct rate',ylabel='MAS report correct rate',title='50 reports (area = multiplicity)')
    names=['1 step','2 steps','3+ steps'];xx=np.arange(3)
    for i,arm in enumerate(['sas','mas']):axs[1].bar(xx+(i-.5)*.32,[strata[n][arm]['correct']/sum(strata[n][arm].values()) for n in names],.32,label=arm.upper(),color=['#637B94','#007f8b'][i])
    axs[1].set_xticks(xx,['1 step\nn=104','2 steps\nn=49','3+ steps\nn=7']);axs[1].set(ylabel='Correct delivered / stratum',title='Reference-defined strata');axs[1].legend(frameon=False)
    fig.savefig(OUT/'figures/restored_heterogeneity.pdf');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(7,2.8),layout='constrained');lam=np.linspace(0,3,300)
    for a,kappa in zip(axs,[0,.25]):
        for arm,col in [('sas','#637B94'),('mas','#007f8b')]:
            rr=new['tier16-'+arm+'-primary'];cc=Counter(old.outcome(r,'case_success') for r in rr)
            a.plot(lam,(cc['correct']-lam*cc['wrong']-kappa*cc['withheld'])/160,label=arm.upper(),color=col)
        a.axhline(-kappa,ls='--',color='gray',label='Always withhold');a.set(xlabel='Wrong-answer penalty',ylabel='Utility / question',title=f'Reported score, withholding cost {kappa}');a.legend(frameon=False)
    fig.savefig(OUT/'figures/restored_utility.pdf');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(7,2.8),layout='constrained')
    for i,arm in enumerate(['sas','mas']):
        q=resources['lab-16-ubuntu-noswap-v1']['tier16-'+arm+'-primary'];ss=list(q['stages'].values());labs=[s.split('/')[-1] for s in q['stages']]
        axs[i].barh(labs,[s['seconds']/3600 for s in ss],color='#007f8b');axs[i].set(xlabel='Summed inference hours',title=arm.upper()+' primary (Ubuntu)')
    fig.savefig(OUT/'figures/restored_stage_work.pdf');plt.close(fig)
    audit['checks'].append('All restored tables/plots derive from reconciled ledgers or recomputed statistics; example traces exported verbatim')
    save('coverage_evidence_checks.json',audit);print('\n'.join(audit['checks']))

if __name__=='__main__':main()
