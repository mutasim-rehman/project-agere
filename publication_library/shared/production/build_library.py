"""Compile local drafts independently; stop on errors, skip missing Access kit."""
from pathlib import Path
import subprocess,shutil,json,argparse
L=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser();p.add_argument('--folder',help='One library-relative project directory');p.add_argument('--include-original-six',action='store_true');args=p.parse_args()
    protected={'00_master_research','01_general_conference','02_general_journal','03_preprint_arxiv','13_Springer_journal','15_MDPI_MAKE'}
    for tool in ['pdflatex','bibtex']:
        if not shutil.which(tool):raise SystemExit(f'{tool} must be on PATH; install a TeX distribution first.')
    dirs=[L/args.folder] if args.folder else sorted({p.parent for p in L.glob('*/main.tex')}|{p.parent for p in L.glob('*/official_mdpi/main.tex')}|{p.parent for p in L.glob('*/verified_citations/main.tex')})
    results=[]
    for d in dirs:
        if not (d/'main.tex').exists():continue
        if (d/'PUBLICATION_LOCK').exists():
            results.append(dict(folder=str(d.relative_to(L)),status='LOCKED; submitted/accepted snapshot not rebuilt'));continue
        if not args.folder and d.name in protected and not args.include_original_six:
            results.append(dict(folder=str(d.relative_to(L)),status='PRESERVED; use --include-original-six to rebuild'));continue
        if d.name=='09_IEEE_Access' and not (d/'ieeeaccess.cls').exists():
            results.append(dict(folder=str(d.relative_to(L)),status='TEMPLATE-BLOCKED; authentic ieeeaccess.cls absent'));continue
        for cmd in [['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],['bibtex','main'],['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex']]:
            run=subprocess.run(cmd,cwd=d,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            if run.returncode:
                print(run.stdout.decode(errors='replace')[-4000:]);raise SystemExit(f'Build failed: {d} / {cmd[0]}')
        results.append(dict(folder=str(d.relative_to(L)),status='COMPILED; final scientific/visual QA still required'))
        print(d.relative_to(L),'COMPILED',flush=True)
    (L/'last_build.json').write_text(json.dumps(results,indent=2))
if __name__=='__main__':main()
