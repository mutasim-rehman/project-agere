"""Focused workshop and extended abstract; evidence is unchanged."""
from pathlib import Path
import shutil,re
L=Path(__file__).resolve().parents[2];S=L/'shared/scientific_source'
base=r'''
\section{Question and Scope}
Can an evidence-only planner realize the recovery suggested by answer-key diagnostic interventions? We examine this question in completed financial program-generation experiments. Our contribution is a failure analysis of specific local recipes, not a new winning algorithm. Financial programs can execute correctly while selecting the wrong period, row, unit or operation. A verifier can also reduce wrong delivery by withholding most answers. Candidate construction and delivered correctness must therefore remain distinct.

\section{Design and Measurements}
The planning comparison uses four completed arms on 96 project-held-out TAT-QA contexts: direct 7B, program-generating 7B, a smaller multi-role pipeline (MAS), and planner MAS. Models belong to Qwen2.5; the full record specifies model hashes, adapters, prompts and decoding \citep{qwen}. Evidence packets do not expose answer labels. Programs refer to source quantities and arithmetic steps; deterministic execution establishes arithmetic/provenance constraints, not financial semantic validity. The planner predicts operations, dependencies and VALUE placeholders from question/evidence without answer-key supervision. Its token allocation also changes the actor budget, so this is a pipeline intervention rather than an isolated planning-stage causal effect.

Let $K_i$ indicate a correct executable candidate and $D_i$ delivery. Correct delivery is $n^{-1}\sum_i K_iD_i$; wrong delivery is $n^{-1}\sum_i(1-K_i)D_i$. Withholding is $n^{-1}\sum_i(1-D_i)$. These observables distinguish generation from acceptance \citep{selective}. The prespecified practical requirement combines a positive paired correct-delivery interval with no observed increase in wrong delivery. A secondary 28-context cohort tests the direction again.

The Windows experiment is a nominal 8 GB \emph{application-budget tier} on a 16.39 GB host. A 6.1 GB worker commit ceiling and sampled working-set guard do not establish physical 8 GB feasibility or absence of paging. Greedy single-seed runs do not measure training/decoding variation. FinQA and arithmetic TAT-QA are public financial reasoning benchmarks \citep{finqa,tatqa}; project-held-out filtering does not exclude pretraining contamination.

\section{Results: Recovery Does Not Establish Improvement}
\begin{table}[t]\centering\small
\caption{All primary planner arms, $n=96$. C/W/H are correct delivered, wrong delivered and withheld.}\label{tab:planner}
\begin{tabular}{lrrr}\toprule Recipe&C&W&H\\\midrule Direct 7B&19&76&1\\Program 7B&15&80&1\\MAS&6&23&67\\Planner MAS&10&25&61\\\bottomrule\end{tabular}\end{table}
The planner gains four correct deliveries and loses none, but adds two wrong deliveries (Table~\ref{tab:planner}). The correct-delivery change is $+4.2$ percentage points, with paired context-bootstrap 95\% interval approximately $[+1.0,+8.3]$; exact paired $p=0.125$. Sparse discordant pairs and the bootstrap/exact-test disagreement preclude an established accuracy improvement. More importantly, the practical conjunction fails because wrong delivery increases. Correct executable candidates decrease from 26 to 25: the delivered gain is not a net generation gain.

On the secondary 28-context cohort both MAS arms deliver 2 correct, 10 wrong and withhold16; correct candidates decrease5 to3. The attempted 7B comparison stops after a two-context prefix because of allocation failure, leaving that baseline incomplete. Planner median resident request time rises25.2 to33.9 seconds; generated tokens rise6672 to9863. Commit remains about5.26 GB. Cross-arm direct/program timings include model loading and are not matched resident-latency comparisons.

The oracle diagnostic supplies reference operation structure and an operand shortlist on15 enriched FinQA cases. Official execution matches change0/0/4/10 across neither/operands/structure/both. These answer-key inputs supply unavailable solution information and are neither a deployable planner nor a universal reasoning upper bound. Even the combined intervention yields only7 reported-answer matches; numerical scoring conventions are not interchangeable.
'''
extended=r'''
\section{Complementary Deployment Evidence}
A separate nominal16 GB deployment study compares a quantized14B recipe with a resident1.5B/3B/0.5B F16 team on160 FinQA questions from50 reports. Reported C/W/H is78/48/34 versus5/3/152; raw execution matching is38/88/34 versus5/3/152. The team produces only10 executable candidates and150 INSUFFICIENT drafts. All annotated evidence spans are present in138 packets; the team still delivers only5 correct there versus74 for the larger recipe. This rules out missing annotated spans as the sole descriptive explanation, not model/prompt confounding.

The completed Ubuntu replication preserves the recorded outcomes. Across668817 memory samples and16 attempts, sampled process swap is zero and peak application RSS is10.946 GB below the11.5 GB guard. Interruptions and missing original export/log artifacts prevent an uninterrupted-deployment claim. Windows commit and Linux RSS/swap evidence are different measurements, not a cross-tier causal scaling curve.

Other observations prevent a one-sided interpretation. Direct7B outperforms direct3B on120 fresh TAT-QA contexts29 versus12 ($p=0.00151$), but direct-versus-program effects depend on task/scorer. Matched Q4/Q8 FinQA conditions each achieve2/96 official matches, with two gains and two losses. Retrieval expansion and repair do not supply a robust practical gain; critic-pilot advantages fail transfer criteria. Disabling prompt caching preserves fixed-workload predictions while reducing peak worker commit approximately6.101 to5.264 GB, an engineering improvement rather than a reasoning gain. Complete overlapping historical cohorts and all adverse/null outcomes remain in the supplement.

\section{Relation to Prior Work and Limitations}
Program-aided methods separate generation from execution \citep{pal,pot}; that separation does not solve semantic binding. Equal-thinking-budget comparisons and broader multiagent failure taxonomies already question simple collaboration advantages \citep{equalbudget,mast}. We do not claim novelty for decomposition, verification or resource-aware evaluation, and do not reproduce every published baseline.

Generality remains limited by one model family, selected prompts/grammar, public financial subsets and recipe confounding. Report/company clustering is available for FinQA but report mapping is unavailable for TAT-QA. Enriched oracle cases and overlapping development cohorts are exploratory, not independent replications. Numerical benchmark agreement is not expert financial adjudication or operational safety. The full supplement retains paired uncertainty, scorer sensitivity, conditional mathematical assumptions, historical baselines and worked failures.
'''
short_extra=r'''
\section{Boundary Conditions and Implications}
The complementary160-question FinQA deployment study yields78/48/34 reported C/W/H for a14B quantized recipe versus5/3/152 for a resident F16 team; raw scoring changes the first arm to38/88/34. Model size, precision, pipeline and runtime differ, so the studies cannot establish a pure architectural effect. Stronger direct baselines, null precision/retrieval/repair results and a favorable cache-only memory change remain in the full support, not independent confirmations of the planner.

The defensible implication is to measure evidence availability, candidate correctness, wrong/correct delivery and resource cost separately. Sparse gains, model/prompt dependence, missing TAT-QA report clusters, public-data exposure and incomplete baselines limit generality. No professional financial validity or autonomous-deployment safety follows.
'''
for folder,title,is_short in [
 ('17_general_workshop','Why Oracle Recoverability Did Not Become a Practical Planning Gain',False),
 ('19_short_extended_abstract','Candidate Quality and Delivered Accuracy Can Move in Opposite Directions',True)]:
 d=L/folder;d.mkdir(exist_ok=True)
 shutil.copytree(S/'figures',d/'figures',dirs_exist_ok=True);shutil.copy2(L/'MASTER_REFERENCES.bib',d/'references.bib')
 shutil.copytree(L/'01_general_conference/supplementary',d/'supplementary',dirs_exist_ok=True)
 abstract=('An evidence-only planner adds four correct deliveries but two wrong deliveries on96 TAT-QA contexts, while correct candidates decrease26 to25. It therefore fails its practical adoption rule despite conditional recovery in answer-key diagnostics. A secondary comparison gives no delivery gain. This short report separates candidate generation from selective delivery and retains resource, scoring and statistical qualifications.' if is_short else 'We analyze a failed transfer from answer-key diagnostic potential to evidence-only financial planning. On96 TAT-QA contexts, a planner changes correct delivery6 to10 and wrong delivery23 to25, while correct candidates decrease26 to25. It fails its prespecified practical requirement; a secondary28-context comparison gives no delivery gain. We place these findings alongside a complementary resident-team deployment comparison, stronger baselines, scoring sensitivity and resource limits. Complete historical and statistical support is retained separately.')
 text=r'''\documentclass[10pt,twocolumn,letterpaper]{article}
\usepackage[margin=.75in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{courier}
\usepackage{newtxtext,amsmath,amssymb,graphicx,booktabs,natbib}
\usepackage[hyphens]{url}
\sloppy
\title{'''+title+r'''}
\author{}\date{}
\begin{document}\maketitle
\begin{abstract}'''+abstract+r'''\end{abstract}
'''+base+(short_extra if is_short else extended)+r'''
\section{Conclusion}
The planner fails its practical criterion. Four additional correct deliveries do not establish a generation gain when correct candidates decrease and wrong delivery increases. Oracle recoverability and deployable improvement must remain distinct.
\section*{Support and AI Assistance}
The accompanying29-page audited supplement preserves complete methods, all cohorts, historical outcomes, statistical derivations and examples. Codex assisted this adaptation and code-based checks of preserved evidence; no new inference was run. Human authors must review correctness, originality, declarations and destination-specific rules before submission. This generic draft is not certified for any named workshop.
\bibliographystyle{plainnat}\bibliography{references}
\end{document}
'''
 text=re.sub(r'(?<=[a-z])(?=\d)',' ',text).replace('Qwen 2.5','Qwen2.5')
 if is_short:
  text=re.sub(r'\\begin\{table\}\[t\].*?\\end\{table\}',lambda _:r'\begin{figure*}[t]\centering\includegraphics[width=.80\textwidth]{figures/planner_outcomes.pdf}\caption{All96-context arms: delivered outcomes and correct candidates. Planner delivery gains coexist with lower correct-candidate count.}\label{tab:planner}\end{figure*}',text,flags=re.S).replace(r'Table~\ref{tab:planner}',r'Figure~\ref{tab:planner}')
 else:
  text=text.replace(r'\section{Complementary Deployment Evidence}',r'\begin{figure*}[t]\centering\includegraphics[width=.60\textwidth]{figures/planner_effects.pdf}\caption{Planner-minus-MAS changes with paired context-bootstrap95\% intervals. Sparse exact-test evidence and the no-wrong-increase criterion remain essential.}\end{figure*}\section{Complementary Deployment Evidence}')
 (d/'main.tex').write_text(text)
 shutil.copy2(L/'07_ICML/build.ps1',d/'build.ps1');(d/'.gitignore').write_text('*.aux\n*.log\n*.blg\n*.out\n')
 print(d)
