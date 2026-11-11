"""Compile and inspect the separately saved coverage-restored manuscripts."""
from pathlib import Path
import argparse,subprocess,json,re,hashlib
import pymupdf
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'paper/revised_aaai'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tex-bin',type=Path,required=True);ap.add_argument('--draft',action='store_true');a=ap.parse_args()
    reports={}
    for name in ['main','supplement']:
        commands=[['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],['bibtex',name]]
        commands.extend([commands[0]]*3)
        for cmd in commands:
            cmd=[str(a.tex_bin/(cmd[0]+'.exe'))]+cmd[1:]
            r=subprocess.run(cmd,cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            if r.returncode:raise RuntimeError(r.stdout.decode(errors='replace')[-5000:])
        log=(OUT/(name+'.log')).read_text(errors='replace')
        problems=re.findall(r'(?:Overfull[^\n]*|[^\n]*undefined[^\n]*|[^\n]*LaTeX Error[^\n]*)',log)
        doc=pymupdf.open(OUT/(name+'.pdf'));pages=[p.get_text() for p in doc];text='\n'.join(pages)
        references=next(i+1 for i,t in enumerate(pages) if re.search(r'(?m)^References$',t))
        report={'pages':len(doc),'words_pdf_extraction':len(text.split()),'references_start_page':references,'problems':problems,
                'letter_size':all(abs(p.rect.width-612)<.1 and abs(p.rect.height-792)<.1 for p in doc),
                'undefined_markers':('??' in text or '\ufffd' in text),
                'type3_fonts':any(f[2]=='Type3' for p in doc for f in p.get_fonts()),
                'sha256':hashlib.sha256((OUT/(name+'.pdf')).read_bytes()).hexdigest()}
        reports[name]=report
        print(name,json.dumps(report))
        if not a.draft:
            assert not problems and not report['undefined_markers'] and report['letter_size'] and not report['type3_fonts'],report
            if name=='main':
                assert references<=8 and len(doc)<=9,report
                # Content must end on page 7; if references begin on 8, ensure page 8 precedes no content.
                content_end=next(i+1 for i,t in enumerate(pages) if re.search(r'(?m)^\d+\s*\nConclusion$',t) or re.search(r'(?m)^Conclusion$',t))
                assert content_end<=7,content_end
    (OUT/'compilation_checks.json').write_text(json.dumps(reports,indent=2))
if __name__=='__main__':main()
