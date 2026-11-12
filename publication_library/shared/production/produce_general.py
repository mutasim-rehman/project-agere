"""Build substantive general-purpose manuscripts from the preserved scientific sources."""
from pathlib import Path
import re,shutil,subprocess,json,hashlib
import pymupdf
ROOT=Path(__file__).resolve().parents[3];LIB=ROOT/'publication_library';SRC=LIB/'shared/scientific_source'
TEX=ROOT.parent/'texlive/TinyTeX/bin/windows'
TEX=Path('D:/project-agere/.local/texlive/TinyTeX/bin/windows')
main=(SRC/'main.tex').read_text();supp=(SRC/'supplement.tex').read_text()
body=main.split(r'\section{Related Work}',1)[1].split(r'\section{Conclusion}',1)[0]
body=r'\section{Related Work}'+body
config={
'00_master_research':('A Complete Empirical Account of Resource-Constrained Financial Reasoning','master',
'This report consolidates the completed research sequence around a single question: what prevents reliable numerical delivery when a local inference budget is divided among reasoning roles? The record includes a larger-budget deployment comparison, earlier synthetic and adapted-model controls, and later Windows planning diagnostics. These studies are complementary and cannot identify a causal effect of RAM or architecture alone. The purpose of this master manuscript is to retain the complete nonredundant evidence needed to inspect those limits.',
'The complete record supports a bounded failure analysis. Generation, semantic binding and selective delivery remain separate obstacles, and neither executable arithmetic nor model review establishes financial correctness. The value of the record lies in the observable transitions and qualified interventions, including failed ones; it does not establish a universal model-allocation rule.'),
'02_general_journal':('Generation, Verification and Abstention in Memory-Constrained Financial Question Answering','journal',
'Reliable financial question answering requires more than a correct arithmetic interpreter. A system must choose the relevant source values, compose a calculation and decide whether to deliver it. This article examines these decisions jointly through two complementary empirical studies. We organize the evidence around construct validity, paired comparisons and failure mechanisms, while retaining the broader development sequence as a technical appendix. The claim is an empirical diagnosis of evaluated recipes rather than a new inference algorithm.',
'The observed errors cannot be summarized by one accuracy number. The F16 team loses useful coverage; reference-informed constraints reveal conditional recovery; evidence-only planning fails its practical requirement. Research on local financial reasoning should therefore measure candidate quality and delivery together, preserve scorer sensitivity, and treat resource feasibility as a separate empirical claim.'),
'01_general_conference':('Evidence, Programs and Delivery: A Controlled Study of Local Financial Reasoning','conference',
'Can a memory-limited financial reasoning pipeline turn available evidence into correct delivered answers? We examine that question through a frozen deployment comparison and a later evidence-only planning intervention. The central contribution is the separation of evidence access, executable candidate construction and selective delivery. We report negative as well as positive transitions, use paired uncertainty, and distinguish equal generation ceilings from equal compute expenditure.',
'Across the measured recipes, more roles or stages do not reliably improve useful delivery. The tested team is generation-limited, while planning changes acceptance without a net increase in correct candidates. These observations motivate sharper evaluation of planning and verification under measured budgets, with broader generality left unresolved.'),
'03_preprint_arxiv':('Project Agere: Audited Results and Reproducibility for Memory-Constrained Financial Reasoning','preprint',
'This public technical report documents completed experiments and the evidence needed to interpret them. It is intended as an archival account of resource-constrained financial reasoning, including historical controls, unsuccessful interventions and missing evidence. No new inference is introduced here. The report separates benchmark numerical agreement from financial semantic validity and keeps the original and Ubuntu resource records distinct.',
'The preserved evidence establishes the reported outcomes for these specific systems. It does not establish physical 8 GB feasibility on Windows, uninterrupted deployment reliability or a general multiagent architecture effect. Future versions should preserve this distinction and update provenance transparently rather than reinterpret exploratory gains as confirmed improvements.')}
abstracts={
'master':'We consolidate completed financial-reasoning experiments under application memory and generation-token ceilings. On 160 FinQA questions, a 14B Q4 single-model recipe delivers 78 reported-correct answers versus five for a resident F16 team. A separate 96-context TAT-QA planner comparison changes correct deliveries from six to ten but wrong deliveries from 23 to 25, failing its practical criterion; correct candidates fall from 26 to 25. A secondary 28-context comparison shows no delivery gain. The report preserves historical controls, uncertainty, scoring sensitivity, source traces and resource qualifications. Reference-informed diagnostic recoverability is separated from deployable improvement.',
'journal':'We investigate the interaction of evidence availability, executable program generation and selective verification in local financial question answering. A paired 160-question FinQA comparison finds 78 versus five reported-correct deliveries for a quantized 14B pipeline and a resident smaller F16 team. Later reference-informed constraints recover ten of 15 diagnostic cases, but an evidence-only planner on 96 TAT-QA contexts increases wrong deliveries and reduces correct candidates, failing its prespecified practical requirement. We analyze paired transitions, resource measurements, scoring conventions and unsuccessful replications. The findings concern specific recipes and support no universal causal ranking of architectures.',
'conference':'Memory-constrained financial reasoning can fail after relevant evidence has been retrieved. We compare a quantized 14B pipeline with a resident F16 team on 160 FinQA questions, obtaining 78 versus five reported-correct deliveries. An evidence-only planner on 96 TAT-QA contexts increases correct delivery from six to ten but wrong delivery from 23 to 25; candidate correctness falls from 26 to 25. The exact paired correct-delivery p-value is 0.125, and a 28-context secondary comparison gives no delivery gain. We distinguish candidate construction from verification and oracle diagnostics from practical improvement.',
'preprint':'This technical report archives completed Project Agere research on financial-document reasoning under local resource ceilings. It records paired model comparisons, generation and verification failures, oracle diagnostics, an unsuccessful evidence-only planner, historical controls and reproducibility details. The primary 160-question FinQA recipes deliver 78 versus five reported-correct answers; the 96-context planner comparison delivers six versus ten correct and 23 versus 25 wrong answers. Both positive and negative outcomes are retained. The evidence is bounded by recipe confounding, public-data exposure, sparse gains, incomplete baselines and qualified resource measurements.'}
preamble=r'''\documentclass[10pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{newtxtext,courier}
\usepackage{amsmath,amssymb,graphicx,booktabs,longtable,seqsplit}
\usepackage[hyphens]{url}
\usepackage{natbib,caption}
\sloppy
'''
report=[]
for folder,(title,kind,intro,conclusion) in config.items():
 d=LIB/folder;d.mkdir(exist_ok=True)
 for p in SRC.glob('*.tex'):
  if p.name not in ['main.tex','supplement.tex']:shutil.copy2(p,d/p.name)
 shutil.copytree(SRC/'figures',d/'figures',dirs_exist_ok=True)
 shutil.copy2(LIB/'MASTER_REFERENCES.bib',d/'references.bib')
 appendix=''
 if kind!='conference':
  support=supp.split(r'\section{Scope and Evidence Status}',1)[1].split(r'\bibliographystyle',1)[0]
  support=r'\section{Scope and Evidence Status}'+support
  appendix='\n\\appendix\n'+support
 else:
  sd=d/'supplementary';sd.mkdir(exist_ok=True)
  for p in SRC.glob('*.tex'):shutil.copy2(p,sd/p.name)
  for p in [SRC/'aaai2027.bst',SRC/'references.bib']:shutil.copy2(p,sd/p.name)
  shutil.copytree(SRC/'figures',sd/'figures',dirs_exist_ok=True)
  shutil.copy2(SRC/'supplement.pdf',sd/'supplement.pdf')
 text=preamble+'\n\\title{'+title+'}\n\\author{}\n\\date{Technical draft: 12 November 2026}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\n'+abstracts[kind]+'\n\\end{abstract}\n\\section{Introduction}\n'+intro+'\n'+body+'\n\\section{Conclusion}\n'+conclusion+appendix+r'''
\section*{Automated assistance and author responsibility}
This draft was prepared with AI-assisted manuscript adaptation, code-based numerical checking and plotting using the preserved research record. Human authors must review the scientific text, establish authorship and complete applicable disclosures before submission. No new research-model inference was performed during manuscript preparation.
\bibliographystyle{plainnat}
\bibliography{references}
\end{document}
'''
 (d/'main.tex').write_text(text,encoding='utf-8')
 (d/'.gitignore').write_text('*.aux\n*.log\n*.blg\n*.out\n')
 (d/'build.ps1').write_text("pdflatex -interaction=nonstopmode -halt-on-error main.tex\nbibtex main\npdflatex -interaction=nonstopmode -halt-on-error main.tex\npdflatex -interaction=nonstopmode -halt-on-error main.tex\n")
 (d/'VENUE_REQUIREMENTS.md').write_text('# General-purpose '+kind+' manuscript\n\nNo specific venue is selected. Uses the standard LaTeX article class, not an authenticated conference/journal template. No publisher page limit or eligibility is claimed. Human review and target-specific refresh are required. Preprint is not uploaded or endorsed by arXiv.\n')
 (d/'MANUSCRIPT_NOTES.md').write_text('# Editorial adaptation\n\n'+intro+'\n\n'+conclusion+'\n\nVerified methods/results are reused centrally from the audited source. Supporting detail is '+('included in a separate supplement.' if kind=='conference' else 'included as extended appendices.')+' Original manuscripts are unchanged.\n')
 (d/'SUBMISSION_CHECKLIST.md').write_text('# Human checks\n\n- Select actual destination and refresh its requirements.\n- Confirm authors, affiliations, contributions, funding and conflicts.\n- Review all AI-assisted prose and complete destination-specific disclosures.\n- Check anonymization, supplemental limits and rights.\n- Do not submit overlapping versions simultaneously.\n')
 (d/'README.md').write_text('# '+title+'\n\nmain.tex and main.pdf are the manuscript. Compile locally with PDFLaTeX, BibTeX and two more PDFLaTeX passes (see build.ps1). All compilation inputs are local. This is a general-purpose research draft; it is not submission-ready for a particular venue.\n')
 for command in [['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],['bibtex','main'],['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex']]:
  r=subprocess.run([str(TEX/(command[0]+'.exe'))]+command[1:],cwd=d,capture_output=True)
  if r.returncode:raise RuntimeError(folder+' '+r.stdout.decode(errors='replace')[-2000:])
 pdf=pymupdf.open(d/'main.pdf');txt=' '.join(p.get_text() for p in pdf)
 log=(d/'main.log').read_text(errors='replace')
 item={'folder':folder,'pages':len(pdf),'words':len(txt.split()),'sha256':hashlib.sha256((d/'main.pdf').read_bytes()).hexdigest(),'undefined_references':bool(re.search(r'undefined',log)),'overfull_boxes':len(re.findall('Overfull',log)),'status':'COMPILED; HUMAN-REVIEW-REQUIRED; visual QA pending'}
 (d/'build_status.json').write_text(json.dumps(item,indent=2));report.append(item);print(item,flush=True)
(LIB/'general_build_status.json').write_text(json.dumps(report,indent=2))
