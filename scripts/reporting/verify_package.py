"""Numerical, provenance, link and PDF-boundary checks (no inference)."""
import csv
import hashlib
import json
from pathlib import Path
import re
import pdfplumber
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]


def main():
    data=json.loads((ROOT/'research/tier16_v2/data/statistical_analysis.json').read_text())
    assert data['case_outputs']==960 and data['unique_questions']==160
    assert data['unique_reports']==50 and data['unique_companies']==36
    assert data['resource_no_swap_pass'] is False and data['inference_calls_made_by_analysis']==0
    for name,s in data['summaries'].items():
        assert s['peak_rss_bytes']<=11500000000
        for m in s['metrics'].values():
            assert sum(m[k] for k in ['correct','wrong','withheld'])==160
            if m['correct_acceptance_a'] is not None:
                assert abs(m['candidate_validity_q']*m['candidate_correctness_p']*m['correct_acceptance_a']-m['correct']/160)<1e-12
    for contrast in data['comparisons'].values():
        for metric in ['case_success','raw_execution_match']:
            assert sum(contrast['endpoints'][metric+'/'+v]['delta_count'] for v in ['correct','wrong','withheld'])==0
            assert sum(contrast['transitions'][metric].values())==160
    cases=list(csv.DictReader((ROOT/'research/tier16_v2/data/case_outcomes.csv').open()))
    assert len(cases)==960 and len({v['case_id'] for v in cases})==160
    cross=json.loads((ROOT/'research/le16_v2/data/cross_tier_analysis.json').read_text())
    assert not cross['comparability']['overlapping_question_ids'] and not cross['comparability']['overlapping_reports']
    assert sum(v['n'] for v in cross['tier8_natural'].values())==768
    assert len(json.loads((ROOT/'research/le16_v2/data/tier8_evidence_catalog.json').read_text()))==197
    provenance=json.loads((ROOT/'research/tier16_v2/evidence/input_provenance.json').read_text())
    for name in ['TIER_8_RESEARCH_REPORT.md','TIER_8_V2_STATISTICAL_EVALUATION_REPORT.pdf']:
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==provenance['inputs'][name]['sha256']
    docs=[ROOT/n for n in json.loads((ROOT/'research/tier16_v2/data/document_index.json').read_text())['reports']]
    docs+=list((ROOT/'research/tier16_v2').glob('*.md'))+list((ROOT/'research/le16_v2').glob('*.md'))
    broken=[]
    for doc in docs:
        for path in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            if path.startswith(('http:','https:','#')):continue
            if not (doc.parent/path.split('#')[0]).exists():broken.append((str(doc.relative_to(ROOT)),path))
    assert not broken,broken
    pages={};boundaries=[]
    for pdf in sorted((ROOT/'output/pdf').glob('TIER_*.pdf')):
        reader=PdfReader(pdf);pages[pdf.name]=len(reader.pages)
        assert len(reader.pages)>=10
        extracted='\n'.join(p.extract_text() for p in reader.pages)
        assert 'RESOURCE' in extracted and 'no-swap' in extracted and 'References' in extracted
        assert 'placeholder' not in extracted.lower() and 'TODO' not in extracted
        with pdfplumber.open(pdf) as parsed:
            for i,page in enumerate(parsed.pages):
                assert len(page.chars)>100
                for c in page.chars:
                    if c['x0']<0 or c['x1']>page.width+.1 or c['top']<0 or c['bottom']>page.height+.1:
                        boundaries.append((pdf.name,i+1,c['text'],c['x0'],c['top']))
    assert not boundaries,boundaries[:10]
    assert len(list((ROOT/'figures/tier16_v2').glob('*.png')))==12
    assert len(list((ROOT/'figures/tier16_v2').glob('*.svg')))==12
    result={'status':'passed','pdf_pages':pages,'case_outputs':960,'unique_questions':160,
        'historical_evidence_files':197,'old_reports_unchanged':True,'broken_links':0,'out_of_page_text':0,
        'png_figures':12,'svg_figures':12,'new_neural_calls':0,
        'visual_review':'Separate mandatory human/model image review of rendered pages; this check alone does not prove layout quality.'}
    (ROOT/'research/tier16_v2/evidence/package_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
