"""Preserve manuscript fingerprints and initialize a separate restoration workspace."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
paper = ROOT / 'paper'
out = paper / 'revised_aaai'
out.mkdir(parents=True, exist_ok=True)
files = [ROOT / s for s in ['output/pdf/RESEARCH_PAPER_AAAI.pdf', 'output/aaai/main.tex',
    'RESEARCH_PAPER.md', 'output/pdf/AGERE_FINAL_AAAI.pdf', 'output/pdf/AGERE_FINAL_SUPPLEMENT.pdf']]
files += [f for f in (ROOT/'output/final_aaai').rglob('*') if f.is_file()
          and f.suffix not in {'.aux','.log','.blg','.out','.pyc'} and '__pycache__' not in f.parts]
manifest = paper / 'preserved_versions.json'
if not manifest.exists():
    manifest.write_text(json.dumps({str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest()
                                   for f in files}, indent=2))
for name in ['main.tex','supplement.tex','references.bib','aaai2027.sty','aaai2027.bst','historical_inventory.tex']:
    if not (out/name).exists(): shutil.copy2(ROOT/'output/final_aaai'/name, out/name)
if not (out/'figures').exists(): shutil.copytree(ROOT/'output/final_aaai/figures',out/'figures')
(out/'.gitignore').write_text('*.aux\n*.log\n*.out\n*.blg\n*.toc\n__pycache__/\n')
(out/'.gitattributes').write_text('* -text\n')
print('Initialized separate paper workspace; original files untouched.')
