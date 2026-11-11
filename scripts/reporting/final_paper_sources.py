"""Fetch primary bibliographic metadata and pin evaluation dependencies.
No model inference. Network retrieval is separate from the offline analysis.
"""
from pathlib import Path
import urllib.request
import re, json, hashlib, html, concurrent.futures, shutil
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/final_aaai'
ARXIV={
 'pot':('2211.12588',2023),'selfcorrect':('2310.01798',2024),
 'critic':('2305.11738',2024),'selfrefine':('2303.17651',2023),
 'mast':('2503.13657',2025),'equalbudget':('2604.02460',2026),
 'verifin':('2608.10213',2026),'budgetverify':('2609.33052',2026),
 'qwen':('2412.15115',2024),'lora':('2106.09685',2021),
 'qlora':('2305.14314',2023),'selfconsistency':('2203.11171',2023)}
def get(url):return urllib.request.urlopen(url,timeout=45).read()
def one(item):
 key,(ident,year)=item;url='https://arxiv.org/abs/'+ident;s=get(url).decode()
 def meta(name):return [html.unescape(x) for x in re.findall(r'<meta\s+name="'+name+r'"\s+content="([^"]+)"',s)]
 title=meta('citation_title')[0];authors=meta('citation_author')
 assert authors and title
 # arXiv metadata is complete; do not guess journal pagination or author lists.
 bib='@misc{'+key+',\n title={{'+title+'}},\n author={'+ ' and '.join(authors)+'},\n year={'+str(year)+'},\n eprint={'+ident+'},\n archivePrefix={arXiv},\n url={'+url+'}\n}\n'
 return bib,dict(key=key,url=url,title=title,authors=authors,year=year,metadata_sha256=hashlib.sha256(s.encode()).hexdigest(),verified='primary arXiv metadata',retrieved='2026-11-11')
def main():
 OUT.mkdir(parents=True,exist_ok=True);bib=[];audit=[]
 for b,a in concurrent.futures.ThreadPoolExecutor(max_workers=4).map(one,ARXIV.items()):bib.append(b);audit.append(a)
 for key,ident in [('finqa','2021.emnlp-main.300'),('tatqa','2021.acl-long.254')]:
  u='https://aclanthology.org/'+ident+'.bib';s=get(u).decode();s=re.sub(r'(@\w+\{)[^,]+',r'\g<1>'+key,s,count=1);bib.append(s)
  audit.append(dict(key=key,url=u,sha256=hashlib.sha256(s.encode()).hexdigest(),verified='publisher BibTeX',retrieved='2026-11-11'))
 for key,vol,slug in [('pal','202','gao23f'),('debate','235','du24e'),('selective','97','geifman19a')]:
  u=f'https://proceedings.mlr.press/v{vol}/{slug}.html';s=get(u).decode();m=re.search(r'(@InProceedings\{.*?\n\})',html.unescape(re.sub('<[^>]+>','',s)),re.S)
  if not m:raise ValueError('Publisher BibTeX missing: '+u)
  b=re.sub(r'(@\w+\{)[^,]+',r'\g<1>'+key,m.group(1),count=1)
  # Drop large abstract field without changing bibliographic metadata.
  b=re.sub(r',?\s*abstract\s*=\s*\{.*?\}\s*(?=\n\})','',b,flags=re.S)
  bib.append(b);audit.append(dict(key=key,url=u,verified='publisher BibTeX',retrieved='2026-11-11'))
 (OUT/'references.bib').write_text('\n'.join(bib),encoding='utf-8');(OUT/'citation_audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
 for name in ['aaai2027.sty','aaai2027.bst','CameraReady2027.tex']:
  u='https://raw.githubusercontent.com/tabbycat7/aaai_2027_latex/main/'+name;b=get(u);(OUT/name).write_bytes(b)
  audit_entry=dict(url=u,sha256=hashlib.sha256(b).hexdigest())
  audit.append(dict(template_file=name,**audit_entry))
 (OUT/'template_provenance.json').write_text(json.dumps({'official_page':'https://aaai.org/authorkit27/','official_zip':'https://aaai.org/wp-content/uploads/2026/05/AuthorKit27.zip','official_fetch':'HTTP 403; direct authenticity comparison unavailable','mirror_files':audit[-3:],'status':'unmodified 2027 files from retained author-kit mirror; official-byte verification remains unresolved'},indent=2))
 print('Verified',len(bib),'primary bibliography entries; saved template provenance.')
if __name__=='__main__':main()
