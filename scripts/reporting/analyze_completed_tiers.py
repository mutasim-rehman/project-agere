"""Reproducible, inference-free analysis of the completed <=16GB evidence.

Only derived numerical tables enter Git. Raw prompts/responses stay on the SSD.
Supplemental tests are post hoc; report/company dependence is explicit.
"""
from collections import Counter, defaultdict
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
METRICS = ('case_success', 'raw_execution_match')
OUTCOMES = ('correct', 'wrong', 'withheld')
SEED, BOOT, FLIPS = 42, 10000, 65536


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8388608), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def csv_write(path, records):
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)


def outcome(row, metric):
    return 'withheld' if not row['delivered'] else 'correct' if row['score'][metric] else 'wrong'


def mcnemar(gain, loss):
    n = gain+loss
    return min(1., 2*sum(math.comb(n, k) for k in range(min(gain, loss)+1))/2**n) if n else 1.


def holm(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    result, previous = [None]*len(values), 0.
    for rank, i in enumerate(order):
        previous = max(previous, min(1., (len(values)-rank)*values[i]))
        result[i] = previous
    return result


def signflip(cluster_deltas):
    values = np.array(cluster_deltas, dtype=float)
    nonzero = values[values != 0]
    if not len(nonzero):
        return {'p': 1., 'method': 'degenerate_zero', 'draws': 1, 'nonzero_clusters': 0}
    observed = abs(values.sum())
    exact = len(nonzero) <= 18
    draws = 2**len(nonzero) if exact else FLIPS
    rng, hits = np.random.default_rng(SEED), 0
    for first in range(0, draws, 4096):
        count = min(4096, draws-first)
        if exact:
            signs = 2*((np.arange(first, first+count, dtype=np.uint64)[:, None] >> np.arange(len(nonzero), dtype=np.uint64)) & 1).astype(float)-1
        else:
            signs = rng.integers(0, 2, size=(count, len(nonzero)))*2-1
        hits += int(np.count_nonzero(np.abs(signs@nonzero) >= observed-1e-12))
    return {'p': hits/draws if exact else (hits+1)/(draws+1),
        'method': 'exact_cluster_sign_flip' if exact else 'monte_carlo_cluster_sign_flip',
        'draws': draws, 'extreme_draws': hits, 'nonzero_clusters': len(nonzero),
        'monte_carlo_resolution': None if exact else 1/(draws+1),
        'assumption': 'Independent clusters and sign-exchangeability/symmetry under null; NOT a randomized causal experiment.'}


def paired(left, right, metric, event, group='report'):
    a, b = {r['case_id']: r for r in left}, {r['case_id']: r for r in right}
    if not a or set(a) != set(b):
        raise ValueError('Require exact nonempty matched IDs')
    groups = defaultdict(list)
    deltas = []
    gain = loss = 0
    for key in sorted(a):
        x, y = int(outcome(a[key], metric) == event), int(outcome(b[key], metric) == event)
        d = y-x
        gain += d == 1; loss += d == -1
        groups[key.rsplit('/', 1)[0] if group == 'report' else key.split('/')[0]].append(d)
        deltas.append(d)
    sizes = np.array([len(v) for v in groups.values()])
    totals = np.array([sum(v) for v in groups.values()])
    rng = np.random.default_rng(SEED)
    indices = rng.integers(0, len(sizes), size=(BOOT, len(sizes)))
    estimates = totals[indices].sum(axis=1)/sizes[indices].sum(axis=1)
    equal_estimates = (totals/sizes)[indices].mean(axis=1)
    n, total = len(a), int(sum(deltas))
    leave = [(total-t)/(n-s) for s, t in zip(sizes, totals) if n > s]
    result = {'n': n, 'clusters': len(sizes), 'cluster_unit': group, 'delta_direction': 'right_minus_left',
        'metric': metric, 'event': event, 'delta_count': total, 'delta_rate': total/n,
        'bootstrap95': np.quantile(estimates, [.025, .975]).tolist(),
        'bonferroni4_bootstrap98_75': np.quantile(estimates, [.00625, .99375]).tolist(),
        'cluster_equal_delta': float(np.mean(totals/sizes)), 'cluster_equal_bootstrap95': np.quantile(equal_estimates, [.025, .975]).tolist(),
        'gain_events': int(gain), 'loss_events': int(loss), 'case_iid_exact_mcnemar_p': mcnemar(int(gain), int(loss)),
        'leave_one_cluster_out_range': [float(min(leave)), float(max(leave))],
        'effective_clusters_for_bounded_weights': float(n*n/np.sum(sizes*sizes)),
        'bounded_difference_halfwidth95': float(math.sqrt(2*np.sum((sizes/n)**2)*math.log(40))),
        'bounded_difference_halfwidth95_family4': float(math.sqrt(2*np.sum((sizes/n)**2)*math.log(160))),
        'cluster_sign_flip': signflip(totals), 'bootstrap_resamples': BOOT, 'seed': SEED,
        'limits': 'Intervals/tests conditional on independent resampling units; post-hoc supplemental tests. No equality, noninferiority or architecture-mechanism proof.'}
    return result


def summarize(records):
    n = len(records)
    result = {'n': n, 'reports': len({r['case_id'].rsplit('/', 1)[0] for r in records}),
        'companies': len({r['case_id'].split('/')[0] for r in records}), 'metrics': {}}
    for metric in METRICS:
        c = Counter(outcome(r, metric) for r in records)
        valid = [r for r in records if not r['execution']['issues']]
        correct_valid = sum(bool(r['score'][metric]) for r in valid)
        result['metrics'][metric] = {**{k: c[k] for k in OUTCOMES},
            'coverage': (c['correct']+c['wrong'])/n, 'correct_rate': c['correct']/n,
            'wrong_rate': c['wrong']/n, 'withheld_rate': c['withheld']/n,
            'precision_when_delivered': c['correct']/(c['correct']+c['wrong']) if c['correct']+c['wrong'] else None,
            'valid_candidates': len(valid), 'correct_candidates': correct_valid,
            'correct_candidates_withheld': sum(r['score'][metric] and not r['delivered'] for r in valid),
            'wrong_candidates_withheld': sum(not r['score'][metric] and not r['delivered'] for r in valid),
            'invalid_or_insufficient_withheld': sum(bool(r['execution']['issues']) and not r['delivered'] for r in records),
            'candidate_validity_q': len(valid)/n,
            'candidate_correctness_p': correct_valid/len(valid) if valid else None,
            'correct_acceptance_a': c['correct']/correct_valid if correct_valid else None,
            'wrong_acceptance_b': c['wrong']/(len(valid)-correct_valid) if len(valid)>correct_valid else None}
    result.update(prompt_tokens=sum(s['prompt_tokens'] for r in records for s in r['stages']),
        generated_tokens=sum(r['tokens'] for r in records),
        inference_seconds=sum(s['seconds'] for r in records for s in r['stages']),
        repair_attempts=sum(bool(r['repair_attempted']) for r in records),
        repair_accepted=sum(bool(r['repair_accepted']) for r in records),
        truncated_stages=sum(s['finish_reason'] == 'length' for r in records for s in r['stages']),
        cases_with_analysis_length_limit=sum(any(s['stage']=='analyze_question' and s['finish_reason']=='length' for s in r['stages']) for r in records),
        context_or_budget_skips=sum(s['finish_reason']=='no_context_or_budget' for r in records for s in r['stages']),
        decisions=dict(Counter(str(r['plan'].get('decision')) if isinstance(r.get('plan'), dict) else 'INVALID_PLAN' for r in records)),
        execution_issues=dict(Counter(v['code'] for r in records for v in r['execution']['issues'])),
        verdicts=dict(Counter(str(r.get('final_verdict', {}).get('binary_verdict','UNKNOWN')) for r in records)),
        metric_concordance=dict(Counter(('reported_yes' if r['score']['case_success'] else 'reported_no')+' / '+('raw_yes' if r['score']['raw_execution_match'] else 'raw_no') for r in records if r['delivered'])))
    times = [sum(s['seconds'] for s in r['stages']) for r in records]
    result['case_latency_seconds'] = {'mean': float(np.mean(times)), 'median': float(np.median(times)), 'p90': float(np.quantile(times,.9)), 'max': max(times)}
    return result


def transitions(left, right, metric):
    a = {r['case_id']: r for r in left}; b = {r['case_id']: r for r in right}
    if set(a) != set(b):
        raise ValueError('Mismatched transition IDs')
    return {x+' -> '+y: sum(outcome(a[k],metric)==x and outcome(b[k],metric)==y for k in a) for x in OUTCOMES for y in OUTCOMES}


def main(ssd):
    output = ROOT/'research/tier16_v2'; combined = ROOT/'research/le16_v2'
    run = ssd/'runs/lab_tiers_v1/lab-16-115gb-recovery-02'
    audit = read(run/'analysis/summary.json'); manifest = read(run/'manifest.json')
    if audit['status'] != 'complete_accuracy_audited_resource_invalid' or read(run/'state.json')['analysis_status'] != 'complete':
        raise ValueError('Expected completed qualified audited evaluation')
    provenance = {}
    def pin(path):
        relative = str(path.relative_to(ssd)) if path.is_relative_to(ssd) else str(path.relative_to(ROOT))
        provenance[relative] = {'sha256': digest(path), 'bytes': path.stat().st_size}
    for relative, expected in audit['evidence_sha256'].items():
        path = run/relative
        if digest(path) != expected:
            raise ValueError('Audited input changed: '+str(path))
        pin(path)
    for relative, expected in manifest['freeze']['code_sha256'].items():
        if digest(run/'code'/relative) != expected:
            raise ValueError('Frozen code changed')
    pin(run/'analysis/summary.json'); pin(run/'manifest.json'); pin(run/'continuation.json')
    if read(run/'continuation.json') != manifest['continuation']:
        raise ValueError('Continuation qualification differs from saved identity')
    for relative, expected in audit['continuation']['evidence_sha256'].items():
        if digest(run/relative) != expected:
            raise ValueError('Historical failure/recovery evidence changed: '+relative)
        pin(run/relative)
    archive = run.parent/'exports'/(run.name+'-results.tar.gz')
    checksum = read(archive.with_suffix(archive.suffix+'.sha256.json'))
    if digest(archive) != checksum['sha256']:
        raise ValueError('Archive checksum mismatch')
    pin(archive); pin(archive.with_suffix(archive.suffix+'.sha256.json'))
    table, data, per_case, per_report = {}, {}, [], []
    gold = {v['id']: v for v in read(ssd/manifest['protocol']['dataset']['gold'])}
    public = {v['id']:v for v in rows(ssd/manifest['protocol']['dataset']['public'])}
    for name, old_summary in audit['summaries'].items():
        records = rows(run/name/'cases.jsonl')
        if [r['case_id'] for r in records] != manifest['protocol']['dataset']['ids']:
            raise ValueError('Wrong ordered paired cases')
        current = summarize(records)
        for metric in METRICS:
            for key, old_key in [('correct','correct_delivered'), ('wrong','wrong_delivered'), ('withheld','withheld')]:
                if current['metrics'][metric][key] != old_summary['full'][metric][old_key]:
                    raise ValueError('Summary endpoint mismatch')
        for key in ['generated_tokens','prompt_tokens','inference_seconds','repair_attempts','truncated_stages','context_or_budget_skips']:
            if not math.isclose(current[key],old_summary[key],rel_tol=1e-12):
                raise ValueError('Work ledger mismatch: '+key)
        current['peak_rss_bytes'] = old_summary['sampled_peak_tree_rss_bytes']; current['cap_bytes'] = old_summary['cap_bytes']
        strata = defaultdict(list)
        for r in records:
            retrieved = set(gold[r['case_id']]['qa']['gold_inds']) <= set(public[r['case_id']]['evidence'])
            strata['all_annotated_evidence_retrieved' if retrieved else 'some_annotated_evidence_missing'].append(r)
            per_case.append({'tier':16,'job':name,'arm':r['arm'],'profile':name.split('-',2)[2], 'case_id':r['case_id'],
                'report':r['case_id'].rsplit('/',1)[0],'company':r['case_id'].split('/')[0], 'delivered':r['delivered'],
                'reported_correct':r['score']['case_success'],'raw_correct':r['score']['raw_execution_match'],
                'reported_outcome':outcome(r,'case_success'),'raw_outcome':outcome(r,'raw_execution_match'),
                'execution_valid':not bool(r['execution']['issues']),'initial_reported_correct':r['initial_score']['case_success'],
                'initial_raw_correct':r['initial_score']['raw_execution_match'], 'repair_attempted':r['repair_attempted'],
                'generated_tokens':r['tokens'],'prompt_tokens':sum(s['prompt_tokens'] for s in r['stages']),
                'inference_seconds':sum(s['seconds'] for s in r['stages']),'annotated_evidence_complete':retrieved,
                'attempt':r['attempt'],'completed_time':r['completed_time']})
        current['retrieval_strata'] = {k:{'n':len(v),'correct':sum(outcome(r,'case_success')=='correct' for r in v),
            'invalid_or_insufficient':sum(bool(r['execution']['issues']) for r in v)} for k,v in strata.items()}
        table[name], data[name] = current, records
        for report in sorted({r['case_id'].rsplit('/',1)[0] for r in records}):
            subset=[r for r in records if r['case_id'].rsplit('/',1)[0]==report]
            for metric in METRICS:
                c=Counter(outcome(r,metric) for r in subset)
                per_report.append({'job':name,'report':report,'metric':metric,'n':len(subset),**{k:c[k] for k in OUTCOMES}})
    comparisons = {}
    specifications = [(p,'tier16-sas-'+p,'tier16-mas-'+p) for p in ['primary','direct_control','repair_ablation']]
    specifications += [(a+'-reasoned_vs_direct','tier16-'+a+'-direct_control','tier16-'+a+'-primary') for a in ['sas','mas']]
    specifications += [(a+'-repair_vs_primary','tier16-'+a+'-primary','tier16-'+a+'-repair_ablation') for a in ['sas','mas']]
    primary_tests=[]
    for label,left,right in specifications:
        endpoints={}
        for metric in METRICS:
            for event in OUTCOMES:
                entry=paired(data[left],data[right],metric,event)
                entry['company_sensitivity']=paired(data[left],data[right],metric,event,'company')
                endpoints[metric+'/'+event]=entry
                if label=='primary' and event in ['correct','wrong']:
                    primary_tests.append(entry)
        comparisons[label]={'left':left,'right':right,'endpoints':endpoints,
            'transitions':{m:transitions(data[left],data[right],m) for m in METRICS}}
    adjusted=holm([e['cluster_sign_flip']['p'] for e in primary_tests])
    for entry,p in zip(primary_tests,adjusted):entry['holm_primary_family4_p']=p
    for arm in ['sas','mas']:
        a,b=data['tier16-'+arm+'-primary'],data['tier16-'+arm+'-repair_ablation']
        comparisons[arm+'-repair_vs_primary']['identical_initial_records']=sum(all(x[k]==y[k] for k in
            ['initial_answer','initial_execution','initial_score','initial_verdict','initial_plan']) for x,y in zip(a,b))
    concordance=[]
    for r in data['tier16-sas-primary']:
        if r['delivered'] and r['score']['case_success'] != r['score']['raw_execution_match']:
            g=gold[r['case_id']]['qa']
            concordance.append({'case_id':r['case_id'],'reported_correct':r['score']['case_success'],
                'raw_correct':r['score']['raw_execution_match'],'predicted':r['execution']['value'],
                'declared_unit':r['answer'].get('answer_unit'),'gold_answer':str(g['answer']),'gold_exe_ans':str(g['exe_ans'])})
    failures={}
    for path in run.rglob('state.json'):
        v=read(path)
        if v.get('swap_breach') or v.get('memory_breach'):
            memory=path.parent/'memory.jsonl';max_swap=0;first_bad=None
            with memory.open() as stream:
                for line in stream:
                    sample=json.loads(line);max_swap=max(max_swap,sample.get('tree_swap_bytes',0))
                    if first_bad is None and (sample.get('tree_swap_bytes',0) or sample['tree_rss_bytes']>11500000000):first_bad=sample['time']
            failures[digest(path)]={'relative':str(path.relative_to(run)), 'memory_breach':v.get('memory_breach'),
                'swap_breach':v.get('swap_breach'),'peak_rss_bytes':v.get('peak_tree_rss_bytes'),
                'max_swap_bytes':max_swap,'first_invalid_sample_time':first_bad}
    result={'protocol':manifest['protocol'],'run_id':run.name,'status':audit['status'], 'summaries':table,
        'comparisons':comparisons,'metric_disagreements':concordance,'source_failures':list(failures.values()),
        'unique_questions':160,'unique_reports':next(iter(table.values()))['reports'],
        'unique_companies':next(iter(table.values()))['companies'],'case_outputs':len(per_case),
        'archive':str(archive),'archive_sha256':checksum['sha256'],'resource_no_swap_pass':False,
        'inference_calls_made_by_analysis':0,
        'analysis_plan_status':'Post-hoc supplemental statistical analysis; primary deployment/profile and outcome definitions were frozen before evaluation. No equivalence margin was prespecified.',
        'bootstrap_engine':'NumPy default_rng42; percentile linear quantiles; differs slightly from original audit random.Random42 indexing. Original audit retained unchanged.',
        'statistical_assumptions':'Report independence for primary intervals; company-cluster sensitivity; sign-symmetry under null for sign-flip p-values. No randomized architecture intervention or sampling guarantee.'}
    write(output/'data/statistical_analysis.json',result)
    write(output/'evidence/original_audited_summary.json',audit)
    csv_write(output/'data/case_outcomes.csv',per_case);csv_write(output/'data/report_outcomes.csv',per_report)
    csv_write(output/'data/metric_disagreements.csv',concordance)
    csv_write(output/'data/resource_events.csv',list(failures.values()))
    stage_table=[]
    for name,records in data.items():
        by_stage=defaultdict(list)
        for record in records:
            for stage in record['stages']:by_stage[(stage['role'],stage['stage'])].append(stage)
        for (role,stage),events in by_stage.items():
            stage_table.append({'job':name,'role':role,'stage':stage,'calls':len(events),
                'prompt_tokens':sum(x['prompt_tokens'] for x in events),'generated_tokens':sum(x['generated_tokens'] for x in events),
                'inference_seconds':sum(x['seconds'] for x in events),'finish_length':sum(x['finish_reason']=='length' for x in events),
                'context_or_budget_skips':sum(x['finish_reason']=='no_context_or_budget' for x in events)})
    csv_write(output/'data/stage_metrics.csv',stage_table)
    flat=[]
    for label,comparison in comparisons.items():
        for name,e in comparison['endpoints'].items():
            flat.append({'comparison':label,'endpoint':name,'n':e['n'],'reports':e['clusters'],'delta':e['delta_rate'],
                'ci_low':e['bootstrap95'][0],'ci_high':e['bootstrap95'][1],'cluster_signflip_p':e['cluster_sign_flip']['p'],
                'holm_primary4_p':e.get('holm_primary_family4_p'),'mcnemar_iid_only_p':e['case_iid_exact_mcnemar_p'],
                'company_ci_low':e['company_sensitivity']['bootstrap95'][0],'company_ci_high':e['company_sensitivity']['bootstrap95'][1]})
    csv_write(output/'data/paired_effects.csv',flat)
    # Cross-tier evidence remains stratified. No pooled pseudo-random RAM effect.
    natural=ssd/'runs/tier8_method_qa'; t8, t8data={},{}
    paths=[p for p in sorted(natural.iterdir()) if p.is_dir() and (p/'summary.json').exists()]
    for p in paths:
        summary=read(p/'summary.json')
        if summary.get('status')!='complete':continue
        rec=rows(p/'cases.jsonl'); m=read(p/'manifest.json')
        s=summarize(rec);s['peak_rss_bytes']=summary['peak_tree_rss_bytes'];s['config']=m['config']
        for metric, old_key in [('case_success','delivered_correct')]:
            if s['metrics'][metric]['correct'] != summary[old_key]:raise ValueError('8GB mismatch')
        t8[p.name]=s;t8data[p.name]=rec
        for name in ['cases.jsonl','summary.json','manifest.json']:pin(p/name)
    cross={}
    for partition in ['model_selection','diagnostic_audit']:
        for condition in ['control','crossed']:
            a=partition+'-'+condition+'_sas-full-01';b=partition+'-'+condition+'_mas-full-01'
            cross[partition+'-'+condition]={'left':a,'right':b,
                'endpoints':{m+'/'+e:paired(t8data[a],t8data[b],m,e) for m in METRICS for e in OUTCOMES}}
    legacy={}
    for arm in ['sas','mas']:
        p=ssd/('runs/tier8/tier8-8gb-v1/test/final_'+arm)
        legacy[arm]=read(p/'summary.json');pin(p/'summary.json');pin(p/'cases.jsonl')
        if len(rows(p/'cases.jsonl'))!=175:raise ValueError('Legacy denominator changed')
    group8={r['case_id'].rsplit('/',1)[0] for k,v in t8data.items() for r in v}
    ids8={r['case_id'] for v in t8data.values() for r in v}
    ids16=set(manifest['protocol']['dataset']['ids']);group16={k.rsplit('/',1)[0] for k in ids16}
    write(combined/'data/cross_tier_analysis.json',{'tier8_natural':t8,'tier8_paired_architecture':cross,
        'legacy8_synthetic':legacy,'tier16':table,'comparability':{'overlapping_question_ids':sorted(ids8&ids16),
        'overlapping_reports':sorted(group8&group16),'unique_t8_finqa_questions':len(ids8),'unique_t8_finqa_reports':len(group8),
        'unique_t16_finqa_questions':len(ids16),'unique_t16_finqa_reports':len(group16),
        'pooling_permitted':False,'causal_ram_effect_identified':False,
        'confounders':['train-source versus dev-source questions','adapted versus pretrained checkpoints','Q4 shared MAS versus F16 resident MAS',
        '7B versus14B SAS','selector none versus suggest','prompt/repair recipes','native versus portable CPU build','different deployment cap and memory-control history']}})
    t8flat=[]
    for name,s in t8.items():
        for metric,d in s['metrics'].items():
            t8flat.append({'job':name,'metric':metric,'n':s['n'],'reports':s['reports'],
                **{k:d[k] for k in OUTCOMES},'generated_tokens':s['generated_tokens'],'prompt_tokens':s['prompt_tokens'],
                'inference_seconds':s['inference_seconds'],'peak_rss_bytes':s['peak_rss_bytes']})
    csv_write(combined/'data/tier8_condition_inventory.csv',t8flat)
    diagnostic_names=['finqa-mas-3b-adaptation-dev24-paired-01.json','critic3b-natural24-delivery-results-01.json',
        'external-baselines-completed-01.json','shared3b-serving-parity-complete-01.json',
        'header-materialization-fitting-01.json','source-span-catalog-fitting-01.json','header-visibility-attribution-01.json']
    diagnostics={}
    for name in diagnostic_names:
        path=ROOT/'research/tier8_v2/evidence'/name;pin(path)
        saved=read(path)
        diagnostics[name]={'source_sha256':digest(path),'data':{k:v for k,v in saved.items() if k not in ['input_sha256','source_sha256','code_sha256','cases']}}
    legacy_frames=ssd/'runs/tier8/tier8-8gb-v1/test/frames_summary.json';pin(legacy_frames)
    diagnostics['legacy_frames']={'data':read(legacy_frames),'source_sha256':digest(legacy_frames)}
    write(combined/'data/historical_diagnostics.json',diagnostics)
    catalogue=[]
    for path in sorted((ROOT/'research/tier8_v2/evidence').rglob('*')):
        if not path.is_file():continue
        d=read(path) if path.suffix=='.json' else {'status':'non_json_evidence_'+path.suffix.lstrip('.')}
        if not isinstance(d, dict):
            d={'status':'list_artifact','cases':len(d) if isinstance(d,list) else None}
        count=d.get('n',d.get('cases',d.get('cases_completed')))
        if not isinstance(count,(int,float,type(None))):
            count=len(count) if isinstance(count,(list,dict)) else None
        catalogue.append({'file':str(path.relative_to(ROOT)),'sha256':digest(path),
            'n':count,'status':str(d.get('status',d.get('pass','not_uniformly_encoded'))),
            'interpretation':'Historical diagnostic/exploratory artifact; not automatically a confirmatory independent experiment.'})
    write(combined/'data/tier8_evidence_catalog.json',catalogue)
    for path in [ROOT/'TIER_8_RESEARCH_REPORT.md',ROOT/'TIER_8_V2_STATISTICAL_EVALUATION_REPORT.pdf',Path(__file__)]:pin(path)
    write(output/'evidence/input_provenance.json',{'inputs':provenance,'model_hashes':'Retained from frozen manifest; weights were not rehashed for document creation.',
        'source_audit_sha256':digest(run/'analysis/summary.json'),'report_source_hash':digest(Path(__file__)),'date':'2026-10-30'})
    print('Analysis complete:',len(per_case),'16GB case outputs;',len(t8),'8GB natural conditions;',len(catalogue),'historical evidence artifacts')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ssd',default='/run/media/mutasim/Data/AGERE')
    args=p.parse_args();main(Path(args.ssd).resolve())
