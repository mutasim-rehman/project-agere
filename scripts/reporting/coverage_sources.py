"""Verify additional primary sources needed by the restored scientific material."""
from pathlib import Path
import json,re,hashlib,urllib.request
from concurrent.futures import ThreadPoolExecutor
from final_paper_sources import one
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'paper/revised_aaai'

def main():
    items={'bench360':('2511.16682',2026),'dcrc':('2605.31064',2026),
           'smallagents':('2601.11327',2026),'quantfail':('2607.27275',2026),
           'awq':('2306.00978',2026)}
    bib=[];audit=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for b,a in pool.map(one,items.items()):bib.append(b);audit.append(a)
    u='https://aclanthology.org/2025.findings-emnlp.225.bib'
    b=urllib.request.urlopen(u,timeout=45).read().decode()
    b=re.sub(r'(@\w+\{)[^,]+',r'\g<1>finman',b,count=1);bib.append(b)
    audit.append({'key':'finman','url':u,'sha256':hashlib.sha256(b.encode()).hexdigest(),'verified':'publisher BibTeX'})
    stats=r'''
@article{hoeffding,
 author={Hoeffding, Wassily}, title={Probability Inequalities for Sums of Bounded Random Variables},
 year={1963}, journal={Journal of the American Statistical Association}, volume={58}, number={301}, pages={13--30}, doi={10.1080/01621459.1963.10500830}}
@article{holm,
 author={Holm, Sture}, title={A Simple Sequentially Rejective Multiple Test Procedure},
 year={1979}, journal={Scandinavian Journal of Statistics}, volume={6}, number={2}, pages={65--70}, url={https://www.jstor.org/stable/4615733}}
@article{cameron,
 author={Cameron, A. Colin and Miller, Douglas L.}, title={A Practitioner's Guide to Cluster-Robust Inference},
 year={2015}, journal={Journal of Human Resources}, volume={50}, number={2}, pages={317--372}, doi={10.3368/jhr.50.2.317}}
@article{fagerland,
 author={Fagerland, Morten W. and Lydersen, Stian and Laake, Petter},
 title={The {McNemar} Test for Binary Matched-Pairs Data: Mid-p and Asymptotic Are Better than Exact Conditional},
 year={2013}, journal={BMC Medical Research Methodology}, volume={13}, pages={91}, doi={10.1186/1471-2288-13-91}}
@article{mcnemar,
 author={McNemar, Quinn}, title={Note on the Sampling Error of the Difference between Correlated Proportions or Percentages},
 year={1947}, journal={Psychometrika}, volume={12}, number={2}, pages={153--157}, doi={10.1007/BF02295996}}
'''
    for key,url in [('hoeffding','https://www.tandfonline.com/doi/abs/10.1080/01621459.1963.10500830'),('holm','https://www.jstor.org/stable/4615733'),('cameron','https://escholarship.org/uc/item/1jq5d0pq'),('fagerland','https://link.springer.com/article/10.1186/1471-2288-13-91'),('mcnemar','https://link.springer.com/article/10.1007/BF02295996')]:
        audit.append({'key':key,'url':url,'verified':'primary article/publisher or author institutional record inspected via browser; metadata transcribed, formulas derived explicitly in supplement'})
    original=(ROOT/'output/final_aaai/references.bib').read_text(encoding='utf-8')
    # arXiv's header has a team separator ':' which was incorrectly parsed as an author.
    # The report's actual first-page author is Qwen Team, verified in the v1 full text.
    original=re.sub(r'@misc\{qwen,.*?\n\}',r'''@misc{qwen,
 title={{Qwen2.5 Technical Report}}, author={{Qwen Team}}, year={2024},
 eprint={2412.15115v1}, archivePrefix={arXiv}, url={https://arxiv.org/abs/2412.15115v1}
}''',original,flags=re.S)
    audit.append({'key':'qwen','url':'https://arxiv.org/html/2412.15115v1','verified':'Full-text title page names Qwen Team; removed punctuation-only pseudo-author from prior metadata parser','year':2024})
    audit.append({'key':'awq','note':'Cite current arXiv version v6 (2026), matching retrieved author list; original MLSys publication was 2024. No venue metadata is invented.'})
    (OUT/'references.bib').write_text(original+'\n'+'\n'.join(bib)+stats,encoding='utf-8')
    (OUT/'restored_citation_audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Verified 11 additional sources and corrected Qwen team authorship; original bibliography untouched.')
if __name__=='__main__':main()
