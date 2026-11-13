"""Adapt the frozen research record for TMLR; do not perform inference."""
from pathlib import Path
import re,shutil

L=Path(__file__).resolve().parents[2];D=L/'26_TMLR';base=L/'06_NeurIPS'
D.mkdir(exist_ok=True)
kit=L/'shared/official_templates/tmlr/tmlr-style-file-main'
shutil.copytree(kit,D/'template',dirs_exist_ok=True)
shutil.copy2(kit.parent/'provenance.json',D/'template/provenance.json')
for name in ['tmlr.sty','tmlr.bst','fancyhdr.sty']:
 shutil.copy2(kit/name,D/name)
for p in base.glob('*.tex'):
 if p.name not in ['main.tex','checklist.tex']:shutil.copy2(p,D/p.name)
# Preserve prose while keeping this paragraph clear of the preceding figure/footer.
rp=D/'restored_analysis.tex'
rp.write_text(rp.read_text().replace('Among 126 SAS deliveries,',r'\newpage'+'\nAmong 126 SAS deliveries,',1),encoding='utf-8')
shutil.copytree(base/'figures',D/'figures',dirs_exist_ok=True)
shutil.copy2(L/'MASTER_REFERENCES.bib',D/'references.bib')
shutil.copy2(L/'19_short_extended_abstract/build.ps1',D/'build.ps1')
(D/'.gitignore').write_text('*.aux\n*.log\n*.blg\n*.out\n')
s=(base/'main.tex').read_text()
s=s.replace(r'\documentclass{article}',r'\documentclass[10pt]{article}').replace(r'\usepackage[preprint]{neurips_2026}',r'\usepackage{tmlr}')
s=re.sub(r'\\title\{[^}]+\}',lambda _:r'\title{Evidence, Candidate Generation and Selective Delivery in Memory-Constrained Financial Reasoning}',s,count=1)
s=s.replace(r'\maketitle',r'\maketitle'+'\n'+r'\lhead{TMLR-format author-review draft; not submitted}',1)
abstract=r'''We study the behavior of local financial-reasoning pipelines by separating available evidence, correct executable candidates and delivered answers. A paired 160-question FinQA deployment comparison yields 78 reported-correct deliveries for a quantized 14B recipe versus five for a resident F16 specialist team; raw execution matching changes the first count to 38. Separate Windows diagnostics show that reference-informed operation and operand constraints recover ten of 15 enriched cases, but these inputs contain unavailable answer information. An evidence-only planner on 96 TAT-QA contexts changes correct deliveries from six to ten and wrong deliveries from 23 to 25, failing its prespecified practical criterion. Correct candidates decrease from 26 to 25, exact paired correct-delivery $p=0.125$, and a secondary 28-context comparison shows no delivery gain. We retain stronger baselines, unsuccessful interventions, paired uncertainty, scoring sensitivity and qualified memory/latency evidence. A cache-only configuration change improves observed headroom without changing predictions. The results support a bounded account of the evaluated recipes, not a causal architecture ranking, universal planning failure or proof of physical 8 GB feasibility.'''
s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+abstract+r'\end{abstract}',s,count=1,flags=re.S)
intro=r'''A learning-based reasoning pipeline can fail in at least three observably different ways: relevant evidence may be absent, the generator may construct the wrong calculation, or a delivery gate may reject a useful candidate or accept an incorrect one. Collapsing these events into final-answer accuracy obscures what a planning or verification intervention actually changes. This paper studies those distinctions in completed, resource-constrained financial question-answering experiments.

The central contribution is an empirical account of the behavior of specific learned generators and reviewers. We ask: (1) does the tested resident F16 team retain useful correct delivery under a common application ceiling? (2) when an annotated calculation is executable from available evidence, what still prevents correct program construction? and (3) can an evidence-only planner realize the conditional recovery exposed by answer-key diagnostics? These questions concern observable failure transitions, not a newly proposed learning algorithm.

Two complementary studies answer these questions at different levels. Study A compares a quantized 14B single-model recipe and a resident 1.5B/3B/0.5B F16 team on 160 FinQA questions. Study B investigates smaller quantized systems and role adapters on Windows, culminating in a prospective planner comparison on 96 TAT-QA contexts and a secondary 28-context cohort. Their model scale, precision, adaptation, prompts, runtime and data differ, so they cannot identify a pure architectural effect or a memory-scaling law.

The findings are mixed and bounded. The resident team largely fails to produce useful candidate programs. Reference-informed constraints expose conditional recovery, but the evidence-only planner fails its practical adoption rule: it adds wrong deliveries and produces fewer correct candidates despite four additional correct deliveries. Stronger direct baselines and an output-preserving cache improvement remain part of the same record. The complete historical sequence, original hypotheses, statistical sensitivity analyses, conditional mathematical results and worked failures follow the references. No new model inference was performed for manuscript preparation.'''
s=re.sub(r'\\section\{Introduction\}.*?\\section\{Related Work\}',lambda _:r'\section{Introduction}'+intro+r'\section{Related Work}',s,count=1,flags=re.S)
conclusion=r'''The evaluated recipes demonstrate why evidence availability, candidate construction and selective delivery must be assessed separately. A resident F16 team does not retain useful correct coverage in the paired deployment. Reference-informed constraints reveal conditional potential, but the tested evidence-only planner reduces correct candidates, adds wrong deliveries and fails its practical criterion; the secondary cohort gives no delivery gain. These findings can inform evaluation of local program-generating and verification systems without establishing a universal architecture, precision or planning effect. Scorer conventions, paired uncertainty and the limits of resource measurements are essential parts of the result, not peripheral qualifications.'''
s=re.sub(r'\\section\{Conclusion\}.*?\\label\{main-content-end\}',lambda _:r'\section{Conclusion}'+conclusion+r'\label{main-content-end}',s,count=1,flags=re.S)
s=s.replace('The observed errors and withholding do not support autonomous financial decisions. Public benchmark agreement is not professional financial validity. The purpose is to expose failure modes and avoid unwarranted deployment claims; actual authors must confirm data/model licenses and release restrictions.', 'Incorrect calculations can misstate financial quantities, while extensive withholding can undermine the usefulness of an automated service. Public benchmark agreement does not establish professional financial validity or safe autonomous decisions. Human review of source values, periods, units and formulas is a potential mitigation; arithmetic execution and source-membership checks alone are insufficient. The tested gates themselves make acceptance errors, so we claim no validated safety mechanism. Actual authors must confirm dataset/model licenses, release rights and any institutional obligations before sharing an evidence package.')
s=s.replace(r'\section*{AI assistance and responsibility}',r'\section*{Research and manuscript transparency}')
s=s.replace(r'\bibliographystyle{plainnat}',r'\bibliographystyle{tmlr}')
s=s.replace(r'\clearpage\input{checklist.tex}', '')
statements=r'''\section*{Statement of Broader Impact}
The analysis can help evaluators distinguish evidence, generation and delivery failures and avoid overstating the benefits of planning. Incorrect calculations can misstate financial quantities, while extensive withholding can undermine the usefulness of an automated service. Public benchmark agreement does not establish professional financial validity or safe autonomous decisions. Human review of source values, periods, units and formulas is a potential mitigation; arithmetic execution and source-membership checks alone are insufficient. The tested gates themselves make acceptance errors, so we claim no validated safety mechanism. Actual authors must confirm dataset/model licenses, release rights and institutional obligations before sharing an evidence package.
\section*{Research and Manuscript Transparency}
Codex assisted manuscript adaptation, data-derived plotting and code-based numerical checks against preserved artifacts. No new experimental inference was performed for manuscript preparation. Human authors must review all scientific content, citations, provenance and applicable tool disclosures and assume responsibility for the paper. This draft does not attest to their approval, institutional review or originality/parallel-submission eligibility.
'''
s=s.replace(r'\bibliography{references}',statements+r'\bibliography{references}',1)
(D/'main.tex').write_text(s,encoding='utf-8')
print(D)
