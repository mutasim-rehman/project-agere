"""Verify preservation/citations and package the reviewed coverage restoration.

Run only after compilation, audit generation and final visual inspection.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,zipfile,platform
import pymupdf
ROOT=Path(__file__).resolve().parents[2];PAPER=ROOT/'paper';OUT=PAPER/'revised_aaai'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--visual-review-complete',action='store_true',required=True);a=ap.parse_args()
    preserved=json.loads((PAPER/'preserved_versions.json').read_bytes())
    for s,h in preserved.items():assert digest(ROOT/s)==h,s
    prior=json.loads((ROOT/'output/final_aaai/citation_audit.json').read_bytes())
    new=json.loads((OUT/'restored_citation_audit.json').read_bytes())
    refs={x['key']:x for x in prior if 'key' in x}
    for x in new:
        if 'verified' in x:refs[x['key']]=x
    keys=set(re.findall(r'@\w+\{([^,]+)',(OUT/'references.bib').read_text(encoding='utf-8')))
    assert keys==set(refs)
    sources='\n'.join((OUT/s).read_text(encoding='utf-8') for s in ['main.tex','supplement.tex','restored_analysis.tex'])
    cited={k.strip() for g in re.findall(r'\\cite\w*\{([^}]+)\}',sources) for k in g.split(',')}
    assert cited==keys,(cited-keys,keys-cited)
    (OUT/'citation_coverage.json').write_text(json.dumps({'entries':len(keys),'cited_entries':len(cited),'missing_entries':[],
        'sources':list(refs.values()),'version_note':'Bench360 cites its 2026 arXiv revision; AWQ cites its 2026 revision; Qwen uses Qwen Team from the 2024 v1 title page, correcting prior punctuation-only pseudo-author'},indent=2,ensure_ascii=False),encoding='utf-8')
    checks=json.loads((OUT/'compilation_checks.json').read_bytes());fonts={};bounds=[];counts={}
    for name in ['main','supplement']:
        p=OUT/(name+'.pdf');assert digest(p)==checks[name]['sha256']
        doc=pymupdf.open(p);texts=[page.get_text() for page in doc]
        assert not checks[name]['problems'] and not checks[name]['undefined_markers']
        counts[name]={'pages':len(doc),'words':len(' '.join(texts).split())}
        for i,page in enumerate(doc):
            for block in page.get_text('dict')['blocks']:
                if block['type']!=0:continue
                x0,y0,x1,y1=block['bbox']
                if x0<-.5 or y0<-.5 or x1>612.5 or y1>792.5:bounds.append([name,i+1,block['bbox']])
            for f in page.get_fonts():
                if f[0] not in fonts:
                    embedded=doc.extract_font(f[0])[3]
                    fonts[f[0]]={'document':name,'font':f[3],'type':f[2],'embedded_bytes':len(embedded)}
        if name=='main':
            assert all('Figure ' not in t and 'Table ' not in t and 'Conclusion' not in t for t in texts[7:]),'Content beyond page seven'
        assert '??' not in '\n'.join(texts)
    assert not bounds,bounds
    style=json.loads((ROOT/'output/final_aaai/template_provenance.json').read_bytes())
    for f in style['mirror_files']:
        if (OUT/f['template_file']).exists():assert digest(OUT/f['template_file'])==f['sha256']
    review={'pdf_sha256':{n:checks[n]['sha256'] for n in checks},'pages_visually_reviewed':counts,
        'method':'All pages rendered at 1.7x via PyMuPDF; all contact sheets reviewed; enlarged checks of figures, formal mathematics, dense statistical tables and CLI examples',
        'corrections':['Kept short outcome tables together','Moved a stranded subsection heading with its table','Kept reproduction CLI commands together with spaces preserved','Corrected Qwen bibliography punctuation and verified version years'],
        'observed_clipping_overlap_or_unreadable_glyphs':False,'text_blocks_outside_page':bounds,
        'main_content_limit':'Non-reference content ends on page seven; page eight contains references only',
        'limits':'Document QA is not independent financial adjudication or official-template authentication; supplement portal limits and checklist remain author checks'}
    (OUT/'visual_review.json').write_text(json.dumps(review,indent=2))
    tests=subprocess.run([sys.executable,'-m','unittest','tests.test_reporting_statistics','tests.test_paper_statistical_tests'],cwd=ROOT,capture_output=True,text=True)
    assert tests.returncode==0,tests.stdout+tests.stderr
    (OUT/'final_verification.json').write_text(json.dumps({'original_files_preserved':len(preserved),'all_preserved_hashes_match':True,
        'citations':len(keys),'counts':counts,'statistical_tests':tests.stderr.strip(),'text_within_pages':True,
        'compiled_pdf_hashes':review['pdf_sha256'],'analysis_environment':{'python':platform.python_version()},
        'no_new_inference':True},indent=2))
    # Include every supporting source/audit in the portable source archive. Full repo needed for raw analysis.
    target=OUT/'AGERE_COVERAGE_RESTORED_SOURCE.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob('*')):
            if not p.is_file() or p==target or p.suffix in {'.aux','.log','.out','.blg','.toc','.pyc'} or '__pycache__' in p.parts:continue
            z.write(p,str(p.relative_to(OUT)))
        for s in ['COVERAGE_AUDIT.md','VENUE_REQUIREMENTS.md','LITERATURE_COVERAGE.md','preserved_versions.json']:z.write(PAPER/s,s)
        for s in ['requirements-paper.txt','template_provenance.json','citation_audit.json']:z.write(ROOT/'output/final_aaai'/s,'prior_audit/'+s)
        for p in sorted((ROOT/'scripts/reporting').glob('*coverage*.py')):z.write(p,'reproduction_scripts/'+p.name)
        for s in ['build_final_paper.py','verify_final_scores.py','paper_statistical_tests.py','analyze_completed_tiers.py']:
            z.write(ROOT/'scripts/reporting'/s,'reproduction_scripts/'+s)
    with zipfile.ZipFile(target) as z:assert z.testzip() is None
    print(json.dumps({'original_files_preserved':len(preserved),'citations':len(keys),'counts':counts,'archive_bytes':target.stat().st_size},indent=2))
if __name__=='__main__':main()
