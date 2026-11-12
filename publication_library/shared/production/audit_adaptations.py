"""Map preserved scientific sections into compiled adaptations (no inference)."""
from pathlib import Path
import re, json, hashlib
import pymupdf

LIB = Path(__file__).resolve().parents[2]
SRC = LIB / 'shared/scientific_source'

def expand(path):
    s = path.read_text(encoding='utf-8')
    return re.sub(r'\\input\{([^}]+)\}', lambda m: expand(path.parent / (m[1] if m[1].endswith('.tex') else m[1]+'.tex')), s)

def norm(s):
    return re.sub('[^a-z0-9]', '', s.lower())

def run():
    rows=[]
    for source in ['main.tex','supplement.tex']:
        s=expand(SRC/source)
        for kind,title in re.findall(r'\\(section|subsection|subsubsection)\*?\{([^}]+)\}',s):
            if title not in ['References']: rows.append((source,kind,title))
    output=['# Adapted scientific-section and page mapping','',
            'Generated from expanded canonical TeX and actual compiled PDF text. Page matches locate headings; they do not independently validate a financial answer. Missing heading matches are explicit. Original 37-page item-level mapping remains in shared/source_inventory/COVERAGE_AUDIT.md.','']
    report=[]
    for main in sorted(LIB.glob('*/main.pdf')) + sorted(LIB.glob('*/official_mdpi/main.pdf')):
        d=main.parent
        pdfs=[main]
        sup=d/'supplementary/supplement.pdf'
        if sup.exists():pdfs.append(sup)
        pages=[(str(p.relative_to(LIB)),i+1,norm(page.get_text())) for p in pdfs for i,page in enumerate(pymupdf.open(p))]
        output+=['## '+str(d.relative_to(LIB)),'']
        matches=[]
        for source,kind,title in rows:
            found=[f'{p}:p{n}' for p,n,t in pages if norm(title) in t]
            matches.append(dict(source=source,heading=title,locations=found))
            output.append(f'- `{source}` / {title}: '+('; '.join(found) if found else 'HEADING NOT MATCHED; inspect condensed/replaced framing.'))
        fig=[]
        for f in (SRC/'figures').glob('*.pdf'):
            local=d/'figures'/f.name
            if local.exists():
                same=hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256(local.read_bytes()).digest()
                if not same:raise ValueError('Figure diverged: '+str(local))
                fig.append(f.name)
        bib=(d/'references.bib').read_text(encoding='utf-8')
        key_pattern=r'@(?:article|inproceedings|misc|book|techreport|incollection)\s*\{\s*([^,]+),'
        keys=set(re.findall(key_pattern,bib,re.I))
        master=set(re.findall(key_pattern,(LIB/'MASTER_REFERENCES.bib').read_text(),re.I))
        if keys!=master:raise ValueError('Bibliography key divergence: '+str(d))
        log=(d/'main.log').read_text(errors='replace') if (d/'main.log').exists() else ''
        doc=pymupdf.open(main)
        item=dict(folder=str(d.relative_to(LIB)),pages=len(doc),words=sum(len(p.get_text().split()) for p in doc),
                  sha256=hashlib.sha256(main.read_bytes()).hexdigest(),figure_bytes_verified=fig,bibliography_keys=len(keys),
                  overfull_boxes=log.count('Overfull'),undefined=bool(re.search(r'(?:undefined references|undefined citations|Citation.*undefined|Reference.*undefined)',log)),
                  mapping=matches)
        report.append(item)
        output+=['',f"Verified {len(fig)} local figure files against canonical bytes; {len(keys)} bibliography keys. PDF: {len(doc)} pages. Supplement retained: {sup.exists()}.",'']
    out=LIB/'shared/qa';out.mkdir(exist_ok=True)
    (out/'adaptation_checks.json').write_text(json.dumps(report,indent=2))
    (LIB/'ADAPTED_COVERAGE_MAP.md').write_text('\n'.join(output),encoding='utf-8')
    print(json.dumps([{k:v for k,v in x.items() if k not in ['mapping','figure_bytes_verified','sha256']} for x in report],indent=2))

if __name__=='__main__':run()
