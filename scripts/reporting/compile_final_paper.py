"""Compile both paper PDFs, check layout/citations, and make a portable package.

python scripts/reporting/compile_final_paper.py --tex-bin /path/to/tex/bin
Requires PDFLaTeX, BibTeX, PyMuPDF. Does not run experimental analysis or inference.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, zipfile
import pymupdf
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/final_aaai'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--tex-bin',type=Path);a=ap.parse_args()
 def exe(name):
  if a.tex_bin:
   p=a.tex_bin/name
   return str(p if p.exists() else p.with_suffix('.exe'))
  p=shutil.which(name)
  if not p:raise RuntimeError(name+' not found; supply --tex-bin')
  return p
 reports={}
 for name in ['main','supplement']:
  commands=[[exe('pdflatex'),'-interaction=nonstopmode','-halt-on-error',name+'.tex'],[exe('bibtex'),name]]
  commands.extend([commands[0]]*2)
  for command in commands:
   r=subprocess.run(command,cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   if r.returncode:raise RuntimeError(r.stdout.decode(errors='replace')[-4000:])
  log=(OUT/(name+'.log')).read_text(errors='replace')
  problems=re.findall(r'(?:Overfull[^\n]*|[^\n]*undefined[^\n]*|[^\n]*LaTeX Error[^\n]*)',log)
  assert not problems,problems
  doc=pymupdf.open(OUT/(name+'.pdf'));text='\n'.join(p.get_text() for p in doc)
  assert '??' not in text and '\ufffd' not in text
  assert all(abs(p.rect.width-612)<.1 and abs(p.rect.height-792)<.1 for p in doc)
  fonts={f[3]:f[2] for p in doc for f in p.get_fonts()};assert 'Type3' not in fonts.values(),fonts
  references=next(i+1 for i,p in enumerate(doc) if re.search(r'(?m)^References$',p.get_text()))
  if name=='main':assert references<=7 and len(doc)<=9
  reports[name]=dict(pages=len(doc),references_start_page=references,letter_size=True,overfull_boxes=0,undefined_references=0,type3_fonts=False,sha256=hashlib.sha256((OUT/(name+'.pdf')).read_bytes()).hexdigest())
  dest=ROOT/'output/pdf'/('AGERE_FINAL_AAAI.pdf' if name=='main' else 'AGERE_FINAL_SUPPLEMENT.pdf');dest.parent.mkdir(exist_ok=True);shutil.copy2(OUT/(name+'.pdf'),dest)
 (OUT/'compilation_checks.json').write_text(json.dumps(reports,indent=2))
 target=OUT/'AGERE_FINAL_SOURCE.zip'
 excluded={'.aux','.log','.blg','.out','.pyc'}
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(OUT.rglob('*')):
   if not p.is_file() or p==target or p.suffix in excluded or '__pycache__' in p.parts or p.name.startswith('build-'):continue
   z.write(p,str(p.relative_to(OUT)))
  for p in sorted((ROOT/'scripts/reporting').glob('*final*.py')):z.write(p,'reproduction_scripts/'+p.name)
 print(json.dumps(reports,indent=2))
if __name__=='__main__':main()
