"""Re-execute saved programs and rescore raw predictions; no inference."""
from pathlib import Path
import sys,json,argparse,io,contextlib,hashlib
from types import SimpleNamespace
from collections import Counter
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/final_aaai'
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(OUT/'vendor/tatqa'))
from tier8_v2_financial_pipeline import checked,evaluate_financial
from tier8_v2_finqa import packet
from tier8_windows_challenge import official_evaluator,official_result
from tier8_windows_planner_study import scores
import tatqa_metric
def load(p):return json.loads(Path(p).read_bytes())
def rows(p):return [json.loads(l) for l in Path(p).read_text(encoding='utf-8-sig').splitlines() if l.strip()]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True);args=ap.parse_args()
 expected={'finqa/test.json':'831dbfb2e785dbc227f895ce3f24046433467aec67b09db2bd6ac7692a8a30dc','finqa/evaluate.py':'845cd131cab843eceff256cf6d392978cc470a7da4a80107beb56027fdca5c13','tatqa/tatqa_metric.py':'2aeeac479f89f8c76300af1cc0e8d098eb86af84bc386b38b6ab4af484a6dea8','tatqa/tatqa_utils.py':'a84bb2f960737cf0a53733637a674cc4b20ef030a2be6a4b21dc2c4356f415ec','tatqa/tatqa_dataset_dev.json':'8da095a819af6db3c14877c6df2d4d29960e41d1a63dd1fa853507bd2a616af5','tatqa/tatqa_dataset_test.json':'c4d08418359c1d76468dec420ee748a37f48c06b63cb8ec2766f19d5d314b597'}
 for name,h in expected.items():assert hashlib.sha256((OUT/'vendor'/name).read_bytes()).hexdigest()==h,name
 gold={r['id']:r for r in load(args.evidence/'datasets/lab_tiers/finance_reports_v1/scoring-source.json')}
 packets={r['id']:r for r in rows(args.evidence/'datasets/lab_tiers/finance_reports_v1/public.jsonl')}
 n=0
 for p in (args.evidence/'runs/lab_tiers_v1/lab-16-ubuntu-noswap-v1').glob('tier16-*/cases.jsonl'):
  for r in rows(p):
   for prefix in ['initial_','']:
    ans=r[prefix+'answer'];execution=checked(ans,packets[r['case_id']]['evidence'])
    assert execution==r[prefix+'execution'],(p,r['case_id'])
    assert evaluate_financial(gold[r['case_id']],ans,execution)==r[prefix+'score'],(p,r['case_id'])
    n+=1
 gold={r['id']:r for r in load(OUT/'vendor/finqa/test.json')}
 evaluate=official_evaluator(OUT/'vendor/finqa/evaluate.py');audits=[]
 for p in sorted((ROOT/'research/tier8_v2/evidence').glob('windows*/*cases.jsonl')):
  rr=rows(p)
  if not rr or 'drafts' not in rr[0] or any(r['case_id'] not in gold for r in rr):continue
  counts=[Counter(),Counter()];candidate_n=0
  for r in rr:
   annotation=gold[r['case_id']];ev=packet(annotation)['evidence']
   for i,d in enumerate(r['drafts']):
    candidate=d['candidate'];execution=checked(candidate['program'],d.get('evidence') or ev)
    assert execution==candidate['execution'],(str(p),r['case_id'],i)
    try:official=not execution['issues'] and official_result(evaluate,annotation,candidate['program'])==annotation['qa']['exe_ans']
    except (ValueError,TypeError):official=False
    reported=evaluate_financial(annotation,candidate['program'],execution)['case_success']
    counts[i].update(official=int(official),reported=int(reported));candidate_n+=1
  # Reconcile headline summary counts where a matching summary is retained.
  summary=p.with_name(p.name.replace('-cases.jsonl','-summary.json'))
  if summary!=p and summary.exists():
   sm=load(summary)
   if 'official' in sm and 'first_draft_correct' in sm['official']:
    for i,k in enumerate(['first_draft_correct','second_draft_correct']):
     for metric in ['official','reported']:assert counts[i][metric]==sm[metric][k],(p,metric,k)
  audits.append(dict(path=str(p.relative_to(ROOT)),questions=len(rr),programs_reexecuted=candidate_n,arm_counts=counts))
 labels={q['uid']:q for split in ['dev','test'] for t in load(OUT/f'vendor/tatqa/tatqa_dataset_{split}.json') for q in t['questions']}
 tat=[]
 for p in sorted((ROOT/'research/tier8_v2/evidence').glob('windows*/*cases.jsonl')):
  rr=rows(p)
  if not rr or 'arms' not in rr[0] or any(r['case_id'] not in labels for r in rr):continue
  counts=Counter()
  for r in rr:
   for arm,d in r['arms'].items():
    if 'prediction' not in d:continue
    correct,_=scores(tatqa_metric,labels[r['case_id']],d['prediction']);counts[arm]+=int(correct)
  tat.append(dict(path=str(p.relative_to(ROOT)),questions=len(rr),correct=counts))
 import tier8_windows_finqa_formats as fm
 ext=ROOT/'research/tier8_v2/evidence/windows-extended'
 stream=io.StringIO()
 with contextlib.redirect_stdout(stream):
  fm.summarize(SimpleNamespace(ledger=ext/'finqa-format96-cases.jsonl',cohort=ext/'finqa-cohort.jsonl',source=OUT/'vendor/finqa/test.json',evaluator=OUT/'vendor/finqa/evaluate.py'))
 fmt=json.loads(stream.getvalue());assert fmt==load(ext/'finqa-format96-summary.json')
 result=dict(tier16_programs_reexecuted_and_scored=n,finqa_paired_ledgers=audits,tatqa_prediction_ledgers=tat,finqa_format96_exact_summary_match=True,input_sha256=expected,inference_calls=0)
 (OUT/'raw_score_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print('Verified',n,'Ubuntu initial/final programs;',len(audits),'FinQA paired ledgers;',len(tat),'TAT-QA prediction ledgers.')
if __name__=='__main__':main()
