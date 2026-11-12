"""Prepare IEEE/LNCS proceedings drafts using verified class distributions."""
from pathlib import Path
import shutil
L=Path(__file__).resolve().parents[2];S=L/'shared/scientific_source'
s=(S/'main.tex').read_text();body=r'\section{Related Work}'+s.split(r'\section{Related Work}',1)[1].split(r'\section{Conclusion}',1)[0]
cfg={
'10_IEEE_conference':('Measured Resource Costs and Delivery Failures in Local Financial Reasoning',
'Engineering a local reasoning pipeline requires accounting for both useful delivered answers and the work spent producing them. This paper examines CPU-only financial-reasoning recipes using saved predictions and measured application resources. We distinguish a resident full-precision team from a larger quantized model, and a separate quantized planning intervention from answer-key diagnostic controls. The engineering contribution is a qualified comparison of specific deployments, including resource failures and negative reasoning results; it is not a universal architecture rule.',
'The resident team does not provide useful correct coverage in the evaluated deployment, and the tested evidence-only planner fails its practical criterion. A cache configuration change improves measured memory headroom while preserving outputs, illustrating why resource improvements must be distinguished from reasoning gains. Application memory samples and interrupted runs support bounded operational claims, not uninterrupted deployment or physical 8 GB feasibility.'),
'12_Springer_LNCS':('From Source Evidence to Delivered Calculations: A Failure Analysis of Local Reasoning Pipelines',
'This paper studies the boundary between finding numerical evidence and delivering the calculation requested by a financial question. It organizes completed experiments as a failure analysis of generation, verification and selective delivery. The deployment comparison and later quantized diagnostics use different model and runtime conditions and remain complementary studies. The proceedings version emphasizes the observable pipeline decisions and the failure of an evidence-only intervention to realize answer-key diagnostic potential.',
'The saved traces distinguish three obstacles: availability of source evidence, construction of the requested program and authorization of delivery. The selected resident team largely fails to construct useful programs, while an evidence-only planner adds wrong deliveries and does not increase correct candidates. Conditional oracle recovery therefore cannot be interpreted as deployable improvement. The complete historical and mathematical support is retained separately, with its assumptions and limitations.')}
abstracts={
'10_IEEE_conference':'We evaluate the useful delivery and resource costs of CPU-only financial-reasoning recipes. A paired 160-question comparison yields 78 reported-correct deliveries for a quantized 14B single-model pipeline and five for a resident F16 team. A separate evidence-only planner on 96 TAT-QA contexts changes correct deliveries from six to ten and wrong deliveries from 23 to 25, failing its prespecified practical requirement; correct candidates decrease from 26 to 25. The exact paired correct-delivery p-value is 0.125, and a secondary 28-context comparison gives no delivery gain. We retain stronger baselines, scoring sensitivity, inference time and qualified memory measurements. Cache configuration improves observed memory headroom without changing predictions. These findings concern specific recipes, not a universal architectural ranking or proof of physical 8 GB feasibility.',
'12_Springer_LNCS':'We analyze source selection, executable program construction and selective delivery in local financial reasoning. On 160 FinQA questions, a quantized 14B recipe delivers 78 reported-correct answers versus five for a resident F16 team. Later reference-informed constraints recover ten of 15 diagnostic cases, but an evidence-only planner on 96 TAT-QA contexts increases wrong delivery and reduces correct candidates, failing its practical criterion despite four additional correct deliveries. A secondary comparison shows no delivery gain. Paired uncertainty, scoring sensitivity, historical controls and resource qualifications remain explicit. The contribution is a recipe-specific empirical failure analysis, not a general architecture or precision effect.'}
for folder,(title,intro,conclusion) in cfg.items():
 d=L/folder;d.mkdir(exist_ok=True);ieee=folder.startswith('10_');k=L/'shared/official_templates'/('ieeetran' if ieee else 'lncs')
 shutil.copytree(k,d/'template',dirs_exist_ok=True)
 cls=next(k.rglob('IEEEtran.cls' if ieee else 'llncs.cls'));shutil.copy2(cls,d/cls.name)
 bst=next(k.rglob('IEEEtran.bst' if ieee else 'splncs04.bst'));shutil.copy2(bst,d/bst.name)
 for f in S.glob('*.tex'):
  if f.name not in ['main.tex','supplement.tex']:shutil.copy2(f,d/f.name)
 shutil.copytree(S/'figures',d/'figures',dirs_exist_ok=True);shutil.copy2(L/'MASTER_REFERENCES.bib',d/'references.bib')
 shutil.copytree(L/'01_general_conference/supplementary',d/'supplementary',dirs_exist_ok=True)
 b=body.replace(r'\citep',r'\cite').replace(r'\citet',r'\cite')
 if ieee:
  front=r'''\documentclass[conference]{IEEEtran}
\usepackage{cite,amsmath,amssymb,graphicx,booktabs,longtable,seqsplit}
\usepackage[hyphens]{url}
\sloppy
\title{'''+title+r'''}
\author{\IEEEauthorblockN{Anonymous Authors}}
\begin{document}\maketitle
\begin{abstract}'''+abstracts[folder]+r'''\end{abstract}
\begin{IEEEkeywords}financial question answering, program generation, resource measurement, selective verification\end{IEEEkeywords}
'''
 else:
  front=r'''\documentclass[runningheads]{llncs}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,graphicx,booktabs,longtable,seqsplit}
\usepackage[hyphens]{url}
\sloppy
\begin{document}
\title{'''+title+r'''}
\titlerunning{Source Evidence and Delivered Calculations}
\author{Anonymous Authors}
\authorrunning{Anonymous Authors}
\institute{Author details withheld for review draft}
\maketitle
\begin{abstract}'''+abstracts[folder]+r'''\keywords{Financial reasoning \and Program generation \and Selective verification}\end{abstract}
'''
 text=front+r'\section{Introduction}'+intro+b+r'\section{Conclusion}'+conclusion+r'''
\section*{Supporting Material and Reproducibility}
The comprehensive supplement preserves all historical cohorts, uncertainty and sensitivity analyses, conditional propositions, worked failures and reproduction details. It includes missing-artifact and interrupted-run qualifications. The scientific record and original manuscript versions are unchanged.
\section*{Acknowledgment of AI Assistance}
All manuscript sections were adapted with Codex assistance from preserved research evidence. Assistance included prose adaptation, code-based numerical checks and data-derived plotting; no new experimental inference was performed. The experimental Qwen systems are described in Methods. Actual authors must confirm the assistant version, review every section and supply final authorship, funding, conflicts and availability declarations. This draft does not attest to completed human approval.
\bibliographystyle{'''+bst.stem+r'''}
\bibliography{references}
\end{document}
'''
 (d/'main.tex').write_text(text)
 (d/'.gitignore').write_text('*.aux\n*.log\n*.blg\n*.out\n')
 shutil.copy2(L/'07_ICML/build.ps1',d/'build.ps1')
 print(d)
