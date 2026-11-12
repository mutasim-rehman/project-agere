"""Create the ICLR-specific diagnostic-transfer manuscript, preserving audited data."""
from pathlib import Path
import shutil

L=Path(__file__).resolve().parents[2];S=L/'shared/scientific_source';D=L/'05_ICLR'
D.mkdir(exist_ok=True)
kit=L/'shared/official_templates/iclr2027/iclr2027'
shutil.copytree(kit,D/'template',dirs_exist_ok=True)
for name in ['iclr2027_conference.sty','iclr2027_conference.bst']:
    shutil.copy2(kit/name,D/name)
for p in S.glob('*.tex'):
    if p.name not in ['main.tex','supplement.tex']:shutil.copy2(p,D/p.name)
shutil.copytree(S/'figures',D/'figures',dirs_exist_ok=True)
shutil.copy2(L/'MASTER_REFERENCES.bib',D/'references.bib')
shutil.copytree(L/'01_general_conference/supplementary',D/'supplementary',dirs_exist_ok=True)
s=(S/'main.tex').read_text()
related=s.split(r'\section{Related Work}',1)[1].split(r'\section{Methods and Evaluation}',1)[0]
methods_results=s.split(r'\section{Methods and Evaluation}',1)[1].split(r'\section{Discussion and Limitations}',1)[0]
discussion=s.split(r'\section{Discussion and Limitations}',1)[1].split(r'\section{Conclusion}',1)[0]
intro=r'''A reference-informed diagnostic can show that a pipeline has recoverable errors without showing how to recover them at deployment. This distinction is especially consequential for program-generating language models: relevant values may be present, arithmetic may be executable, and a verifier may still deliver the wrong quantity. We examine the gap between diagnostic recoverability and evidence-only planning in financial reasoning under local resource ceilings.

The primary planning question is deliberately practical: can a planner improve correct delivery without increasing wrong delivery? On 96 TAT-QA contexts, it fails that prespecified conjunction. Correct delivery rises from six to ten, but wrong delivery rises from 23 to 25 and correct candidates fall from 26 to 25. A secondary 28-context comparison gives no delivery gain. We report the favorable delivery transitions alongside their uncertainty and adverse changes, rather than treating an oracle diagnostic as a learned planning result.

A complementary deployment study establishes why selective delivery must be measured alongside candidate construction. On 160 FinQA questions, a resident F16 specialist team delivers five reported-correct answers and withholds 152; a quantized 14B recipe delivers 78 and withholds 34. Model scale, precision and pipeline design differ, preventing a causal architectural interpretation. Likewise, the Windows planning study is not a controlled cross-tier scaling experiment.

Our contribution is a bounded empirical diagnosis of these evaluated recipes: evidence availability, candidate construction and delivery are distinct observables. The full development sequence, conditional mathematical analyses and worked failures remain in the comprehensive supplement. No new inference was performed in preparing this manuscript.
'''
abstract=r'''Can planning realize the recovery suggested by answer-key diagnostics? We study financial program generation and selective delivery under local memory and token ceilings. Reference operation structure and operand constraints recover ten of 15 enriched diagnostic cases, but these interventions supply unavailable answer information. An evidence-only planner on 96 TAT-QA contexts changes correct deliveries from six to ten and wrong deliveries from 23 to 25, failing its prespecified practical criterion. Correct candidates decrease from 26 to 25; the exact paired correct-delivery p-value is 0.125, and a secondary 28-context comparison gives no delivery gain. A complementary 160-question deployment comparison finds five versus 78 reported-correct deliveries for a resident F16 team and a larger quantized single-model recipe. We retain scoring sensitivity, stronger baselines, unsuccessful interventions and resource qualifications. The results support a recipe-specific failure analysis rather than a general claim against planning or multiagent reasoning.'''
conclusion=r'''Reference-informed recoverability is not a deployable planning improvement. Here, an evidence-only planner increases wrong delivery, reduces correct candidates and fails its practical adoption rule, despite four additional correct deliveries. The complementary deployment comparison exposes an extreme generation/coverage shortfall in one resident-team recipe. Evaluation should therefore keep candidate quality, selective delivery and measured resource feasibility distinct. Broader transfer to other models, prompts, grammars and distributions remains unestablished.'''
text=r'''\documentclass{article}
\usepackage{iclr2027_conference,times}
\usepackage{amsmath,amssymb,graphicx,booktabs,longtable,seqsplit}
\usepackage[hyphens]{url}
\usepackage{hyperref}
\sloppy
\title{When Diagnostic Recoverability Fails to Transfer to Evidence-Only Planning}
\author{}
\begin{document}
\maketitle
\lhead{ICLR 2027 format: unsubmitted author-review draft}
\begin{abstract}
'''+abstract+r'''
\end{abstract}
\section{Introduction}
'''+intro+r'''
\section{Methods and Evaluation}
'''+methods_results+r'''
\section{Discussion and Limitations}
'''+discussion+r'''
\section{Related Work}
'''+related+r'''
\section{Conclusion}
'''+conclusion+r'''
\label{main-content-end}
\subsection*{AI use statement}
An AI assistant (Codex) was used to adapt this manuscript, check numerical consistency through code, and prepare data-derived plots from the preserved research artifacts. The evaluated Qwen systems and role-adapter experiments are described in Methods and the comprehensive supplement. No additional model inference was run for manuscript preparation. Human authors must review all AI-assisted content, verify its originality and correctness, and complete the submission-form disclosures; this draft does not attest that their review has occurred. The exact assistant version and any earlier research assistance require confirmation from author records.
\subsection*{Ethics statement}
These benchmark results do not establish safe financial automation. Incorrect calculations, source binding and excessive withholding can all cause harm if treated as operational financial advice. The analysis uses preserved public-benchmark evidence; authors must confirm applicable dataset/model licenses and any release restrictions before distribution.
\subsection*{Reproducibility statement}
Methods specifies models, budgets, scoring and paired comparisons. The separate comprehensive supplement retains prompts, decoding/runtime details, historical condition tables, uncertainty procedures, trace examples and artifact hashes, including unavailable original artifacts. Saved predictions support analysis without new inference. The final anonymous code/data package and all administrative declarations remain subject to human review.
\bibliography{references}
\bibliographystyle{iclr2027_conference}
\end{document}
'''
(D/'main.tex').write_text(text,encoding='utf-8')
(D/'build.ps1').write_text('pdflatex -interaction=nonstopmode -halt-on-error main.tex\nbibtex main\npdflatex -interaction=nonstopmode -halt-on-error main.tex\npdflatex -interaction=nonstopmode -halt-on-error main.tex\n')
(D/'.gitignore').write_text('*.aux\n*.log\n*.blg\n*.out\n')
print(D)
