"""Three named conference adaptations; no invented open deadlines/selectivity."""
from pathlib import Path
import re,shutil
L=Path(__file__).resolve().parents[2];source=L/'10_IEEE_conference'
configs=[
('11_IEEE_ICTAI','Auditing Program-Generation and Verification Tools for Local Financial Reasoning',
'Financial-reasoning tools combine evidence retrieval, program generation, deterministic execution and learned review. The reliability of this composition cannot be inferred from the validity of any one component. This paper evaluates specific CPU-only tools and their interfaces through saved candidate programs and delivery decisions. We emphasize failure localization, scorer sensitivity and reproducible deployment constraints. A resident full-precision team and a later quantized planning pipeline belong to different studies; neither comparison identifies a universal architectural effect.',
'Tool composition does not by itself establish useful delivery. In the evaluated deployment the resident team largely withholds, while the evidence-only planner decreases correct candidates and adds wrong deliveries. Conditional answer-key recovery identifies a diagnostic opportunity rather than a deployable tool improvement. The defensible contribution is an auditable account of these interfaces and their limitations, with complete historical support.'),
('24_FLLM','Local Language-Model Reasoning Beyond Evidence Access: Costs and Failure Transitions',
'Local foundation-model applications must convert retrieved evidence into a semantically appropriate calculation within limited inference resources. We examine this conversion in financial question answering, separating candidate correctness from selective delivery. The analysis retains stronger direct/program baselines, unsuccessful precision/retrieval/repair changes and a failed evidence-only planner. The central question is where the evaluated recipes lose useful answers, not whether all multiagent or program-aided systems fail. Different models, precision and runtimes prevent a causal cross-tier scaling interpretation.',
'The financial reasoning recipes expose separate limitations of evidence access, program construction and acceptance. More planning does not yield a net correct-candidate gain here and fails the practical delivery criterion, while a cache configuration change improves measured headroom without changing predictions. These bounded findings inform evaluation of local language-model pipelines without implying a universal architecture rule or safe autonomous financial deployment.'),
('25_IEEE_CAI','Useful Delivery and Reliability Limits of Local AI for Financial Calculations',
'An AI application that executes arithmetic correctly can still answer the wrong financial question. An application that withholds nearly every answer can also appear cautious while providing little useful output. We study these deployment-relevant distinctions in specific local financial-reasoning recipes, using saved programs, explicit delivery gates and measured resources. The resulting evidence is a qualified reliability analysis, not a validated financial product. We preserve unsuccessful interventions and incomplete comparisons alongside favorable diagnostic or engineering observations.',
'For the evaluated applications, the resident F16 team does not retain useful correct coverage and the evidence-only planner fails its practical requirement. Wrong deliveries, withholding, scorer conventions and resource accounting materially affect interpretation. The findings do not establish professional financial validity or a universal architecture effect. Deployment claims must remain narrower than conditional oracle recovery or a low wrong-answer count alone.')]
for folder,title,intro,conclusion in configs:
 d=L/folder;d.mkdir(exist_ok=True)
 for p in source.iterdir():
  if p.suffix in ['.aux','.log','.out','.blg','.bbl','.pdf']:continue
  if p.is_dir():shutil.copytree(p,d/p.name,dirs_exist_ok=True)
  else:shutil.copy2(p,d/p.name)
 s=(d/'main.tex').read_text()
 s=re.sub(r'\\title\{[^}]+\}',lambda _:r'\title{'+title+'}',s,count=1)
 s=re.sub(r'\\section\{Introduction\}.*?\\section\{Related Work\}',lambda _:r'\section{Introduction}'+intro+r'\section{Related Work}',s,count=1,flags=re.S)
 s=re.sub(r'\\section\{Conclusion\}.*?\\section\*\{Supporting Material and Reproducibility\}',lambda _:r'\section{Conclusion}'+conclusion+r'\section*{Supporting Material and Reproducibility}',s,count=1,flags=re.S)
 if folder=='24_FLLM':
  related=s.split(r'\section{Related Work}',1)[1].split(r'\section{Methods and Evaluation}',1)[0]
  s=s.replace(r'\section{Related Work}'+related,'').replace(r'\section{Conclusion}',r'\section{Related Work}'+related+r'\section{Conclusion}',1)
 if folder=='11_IEEE_ICTAI':s=s.replace(r'\section{Methods and Evaluation}',r'\section{Tools, Protocols and Evaluation}')
 if folder=='25_IEEE_CAI':
  k=L/'shared/official_templates/cai_ieeeconf'
  shutil.copytree(k,d/'template/cai_papercept',dirs_exist_ok=True);shutil.copy2(k/'ieeeconf.cls',d/'ieeeconf.cls')
  s=s.replace(r'\documentclass[conference]{IEEEtran}',r'\documentclass[letterpaper,10pt,conference]{ieeeconf}'+'\n'+r'\IEEEoverridecommandlockouts'+'\n'+r'\overrideIEEEmargins'+'\n'+r'\usepackage{times}')
  s=s.replace(r'\author{\IEEEauthorblockN{Anonymous Authors}}',r'\author{Anonymous Authors}')
  s=re.sub(r'\\begin\{IEEEkeywords\}.*?\\end\{IEEEkeywords\}','',s,flags=re.S)
 # Identify all AI-adapted numbered sections with a common tool citation, not a fictitious research reference.
 s=re.sub(r'(\\section\{[^}]+\})',lambda m:m[1]+r'\footnotemark[1]',s)
 s=s.replace(r'\section{Introduction}\footnotemark[1]',r'\section{Introduction}\footnotemark[1]'+r'\footnotetext[1]{OpenAI Codex, manuscript-adaptation assistant. Exact tool/model version requires confirmation from author records; see the AI-assistance acknowledgment.}',1)
 (d/'main.tex').write_text(s)
 print(folder)
