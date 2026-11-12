"""Venue adaptations using official ICML/NeurIPS kits; no new experiments."""
from pathlib import Path
import shutil,re
L=Path(__file__).resolve().parents[2]; S=L/'shared/scientific_source'
s=(S/'main.tex').read_text()
related=s.split(r'\section{Related Work}',1)[1].split(r'\section{Methods and Evaluation}',1)[0]
core=s.split(r'\section{Methods and Evaluation}',1)[1].split(r'\section{Discussion and Limitations}',1)[0]
discussion=s.split(r'\section{Discussion and Limitations}',1)[1].split(r'\section{Conclusion}',1)[0]
sup=(S/'supplement.tex').read_text().split(r'\section{Scope and Evidence Status}',1)[1].split(r'\bibliographystyle',1)[0]
sup=r'\section{Scope and Evidence Status}'+sup
# Scope of these manuscript statements is the archived audited source, not the destination draft.
sup=sup.replace('The main paper uses unmodified AAAI-2027 style/BibTeX files; this separate technical supplement uses one column for audit readability.', 'The archived audited source uses AAAI-2027 style/BibTeX files. This adaptation retains the same scientific evidence in the destination template; the appendix uses one column for readability.')
configs={
'06_NeurIPS':dict(kit='neurips2026',title='Diagnosing Failure Beyond Evidence Availability in Local Financial Reasoning',
intro=r'''Negative results can be informative when they distinguish the condition under which a plausible intervention fails from a claim that an entire method family cannot work. We examine a specific sequence in local financial reasoning: evidence retrieval, executable candidate generation, selective verification, and an evidence-only planning intervention. The sequence is evaluated through saved predictions rather than a proposed new winning algorithm.

Two complementary studies supply boundary conditions. A resident F16 team delivers only five reported-correct answers on 160 FinQA questions, versus 78 for a larger quantized single-model recipe. Later, answer-key structure and operand constraints recover ten of 15 enriched diagnostic cases. That potential does not transfer to the tested evidence-only planner: on 96 TAT-QA contexts correct delivery increases six to ten, wrong delivery increases 23 to 25, and correct candidates decrease 26 to 25. The prospective practical criterion therefore fails; a secondary cohort gives no delivery gain.

The contribution is a trace-based diagnosis with explicit scoring sensitivity and uncertainty, including stronger baselines and unsuccessful interventions. These studies neither isolate a causal architectural effect nor establish universal multiagent failure. Their value is the distinction between available evidence, constructing the requested calculation and authorizing delivery under measured resource limits.''',
abstract=r'''We report a bounded negative-result sequence in memory-constrained financial reasoning. On 160 FinQA questions, a resident F16 specialist team delivers five reported-correct answers versus 78 for a larger quantized single-model recipe. Reference-informed operation and operand constraints later recover ten of 15 enriched diagnostic cases, but an evidence-only planner fails its prespecified practical criterion. On 96 TAT-QA contexts it changes correct deliveries from six to ten and wrong deliveries from 23 to 25 while correct candidates fall from 26 to 25. The exact paired correct-delivery p-value is 0.125; a secondary 28-context comparison gives no delivery gain. We retain stronger baselines, scoring sensitivity, paired uncertainty, failed interventions and qualified resource measurements. The findings separate evidence availability, candidate construction and delivery without claiming a universal architecture ranking.''',
conclusion='The evaluated interventions expose separate bottlenecks rather than a successful new algorithm. Reference-informed potential does not establish deployable recovery, and the evidence-only planner fails its adoption rule despite four additional correct deliveries. Candidate quality, wrong delivery, withholding and measured resources must be examined jointly. Generalization beyond these model/prompt/task recipes remains unresolved.'),
'07_ICML':dict(kit='icml2026',title='Evaluating Candidate Quality and Selective Delivery Under Local Inference Budgets',
intro=r'''Resource-limited inference recipes are often compared using a single delivered-answer score. That score mixes candidate construction with the decision to release an answer. A pipeline can reduce wrong answers by withholding most useful output, or increase correct delivery by accepting different candidates without improving generation. We study these distinctions using executable financial calculations and saved acceptance decisions.

Our evaluation treats candidate correctness, delivered correctness, wrong delivery and withholding as different observables. A larger-budget comparison on 160 FinQA questions finds five versus 78 reported-correct deliveries for a resident F16 team and a larger quantized single-model recipe. Later Windows experiments show reference-executable evidence alongside wrong candidate generation. Answer-key constraints recover ten of 15 diagnostic cases, while a practical evidence-only planner on 96 TAT-QA contexts decreases correct candidates and adds wrong deliveries, failing its prespecified adoption rule.

We analyze paired transitions, scorer sensitivity, stronger direct/program baselines and resource cost. The contribution is evaluation and failure analysis of specific recipes, not a new learning algorithm or a causal scaling law. Different tiers change models, precision and runtime, so they must remain complementary studies. The complete historical evidence and conditional mathematical analyses follow the references.''',
abstract=r'''We evaluate candidate generation and selective delivery separately in local financial reasoning. Under common application ceilings, a resident F16 team delivers five reported-correct answers on 160 FinQA questions versus 78 for a larger quantized recipe. Reference-informed constraints recover ten of 15 later diagnostic cases, but an evidence-only planner on 96 TAT-QA contexts changes correct deliveries from six to ten and wrong deliveries from 23 to 25 while correct candidates fall from 26 to 25. It fails its prespecified practical criterion; the exact paired correct-delivery p-value is 0.125 and a secondary cohort gives no delivery gain. Paired analysis, stronger baselines, scoring sensitivity and resource qualifications bound the conclusions to evaluated recipes.''',
conclusion='Useful delivery cannot be inferred from candidate generation, a low wrong-answer rate or an oracle diagnostic alone. In these recipes the resident team largely withholds, and evidence-only planning fails its practical requirement despite a favorable correct-delivery count. Paired transitions and resource/scoring qualifications provide a more defensible evaluation than a single aggregate accuracy. These observations do not establish a general architectural or precision effect.')}
for folder,c in configs.items():
 d=L/folder;d.mkdir(exist_ok=True);kit=L/'shared/official_templates'/c['kit']
 shutil.copytree(kit,d/'template',dirs_exist_ok=True)
 for f in kit.iterdir():
  if f.suffix in ['.sty','.bst']:shutil.copy2(f,d/f.name)
 for f in S.glob('*.tex'):
  if f.name not in ['main.tex','supplement.tex']:shutil.copy2(f,d/f.name)
 shutil.copytree(S/'figures',d/'figures',dirs_exist_ok=True);shutil.copy2(L/'MASTER_REFERENCES.bib',d/'references.bib')
 # Only tabular supporting content uses smaller table typography, not body text.
 for f in d.glob('*.tex'):
  if f.name=='main.tex':continue
  t=f.read_text();t=t.replace(r'\begin{longtable}',r'{\small\setlength{\tabcolsep}{3pt}\begin{longtable}').replace(r'\end{longtable}',r'\end{longtable}}')
  f.write_text(t)
 if folder=='06_NeurIPS':
  front=r'''\documentclass{article}
\usepackage[preprint]{neurips_2026}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,graphicx,booktabs,longtable,seqsplit}
\usepackage[hyphens]{url}
\usepackage{hyperref}
\sloppy
\title{'''+c['title']+r'''}
\author{Anonymous Authors}
\begin{document}
\maketitle
'''
  bst='plainnat';end=r'\clearpage\input{checklist.tex}'
 else:
  front=r'''\documentclass{article}
\usepackage{microtype,graphicx,booktabs,longtable,seqsplit}
\usepackage{hyperref}
\usepackage[preprint]{icml2026}
\usepackage{amsmath,amssymb}
\sloppy
\icmltitlerunning{Candidate Quality and Selective Delivery}
\begin{document}
\twocolumn[
\icmltitle{'''+c['title']+r'''}
\begin{icmlauthorlist}
\icmlauthor{Anonymous Authors}{anon}
\end{icmlauthorlist}
\icmlaffiliation{anon}{Author details withheld for review draft}
\icmlkeywords{financial reasoning, selective prediction, evaluation}
\vskip 0.3in
]
\printAffiliationsAndNotice{}
'''
  bst='icml2026';end=''
 text=front+r'\begin{abstract}'+c['abstract']+r'''\end{abstract}
\section{Introduction}
'''+c['intro']+r'\section{Related Work}'+related+r'\section{Methods and Evaluation}'+core+r'\section{Discussion and Limitations}'+discussion+r'\section{Conclusion}'+c['conclusion']+r'''
\label{main-content-end}
\section*{Impact Statement}
The observed errors and withholding do not support autonomous financial decisions. Public benchmark agreement is not professional financial validity. The purpose is to expose failure modes and avoid unwarranted deployment claims; actual authors must confirm data/model licenses and release restrictions.
\section*{AI assistance and responsibility}
Codex assisted manuscript adaptation, data-derived plotting and code-based numerical checks against preserved artifacts. No new experimental inference was performed for manuscript preparation. Actual authors must review all content and complete applicable disclosures; this draft does not attest to their approval or originality review.
\bibliography{references}
\bibliographystyle{'''+bst+r'''}
\clearpage\appendix\onecolumn
'''+sup+end+r'\end{document}'
 (d/'main.tex').write_text(text)
 (d/'.gitignore').write_text('*.aux\n*.log\n*.blg\n*.out\n')
 (d/'build.ps1').write_text("$ErrorActionPreference='Stop'\npdflatex -interaction=nonstopmode -halt-on-error main.tex\nif($LASTEXITCODE){throw 'LaTeX failed'}\nbibtex main\nif($LASTEXITCODE){throw 'BibTeX failed'}\npdflatex -interaction=nonstopmode -halt-on-error main.tex\nif($LASTEXITCODE){throw 'LaTeX failed'}\npdflatex -interaction=nonstopmode -halt-on-error main.tex\nif($LASTEXITCODE){throw 'LaTeX failed'}\n")
 print(d)
