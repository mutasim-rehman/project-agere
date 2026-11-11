"""Render all final pages for visual QA, with labeled eight-page contact sheets."""
from pathlib import Path
import pymupdf
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'paper/revised_aaai';temp=ROOT/'tmp/pdfs/coverage'
temp.mkdir(parents=True,exist_ok=True);qa=out/'quality_review';qa.mkdir(exist_ok=True)
for name in ['main','supplement']:
    doc=pymupdf.open(out/(name+'.pdf'))
    for i,p in enumerate(doc):p.get_pixmap(matrix=pymupdf.Matrix(1.7,1.7)).save(temp/f'{name}-{i+1}.png')
    for start in range(0,len(doc),8):
        sheet=Image.new('RGB',(1480,1020),'#dddddd');draw=ImageDraw.Draw(sheet)
        for k in range(start,min(start+8,len(doc))):
            im=Image.open(temp/f'{name}-{k+1}.png');im.thumbnail((370,480));j=k-start
            sheet.paste(im,((j%4)*370,(j//4)*510))
            draw.text(((j%4)*370+4,(j//4)*510+482),f'{name} PDF page {k+1}',fill='black')
        sheet.save(qa/f'{name}-{start+1}-{min(start+8,len(doc))}.png')
print('Rendered',len(pymupdf.open(out/'main.pdf'))+len(pymupdf.open(out/'supplement.pdf')),'pages.')
