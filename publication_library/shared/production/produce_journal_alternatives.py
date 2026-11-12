"""Journal-specific alternatives; preserve original projects and audited science."""
from pathlib import Path
import re,shutil,json
L=Path(__file__).resolve().parents[2]
def copy_project(source,dest):
 dest.mkdir(exist_ok=True)
 for p in source.iterdir():
  if p.suffix in ['.aux','.log','.blg','.out','.bbl','.pdf'] or p.name=='quality_review':continue
  if p.is_dir():shutil.copytree(p,dest/p.name,dirs_exist_ok=True)
  else:shutil.copy2(p,dest/p.name)

configs=[('16_MDPI_Computers','computers','Application Budgets, Useful Delivery and Pipeline Overhead in Local Financial Reasoning',
'''Local language-model applications must account for memory headroom, latency and useful delivered output together. We analyze completed financial-reasoning deployments using saved predictions and measured application resources. On160 FinQA questions, a quantized14B recipe delivers78 reported-correct answers versus five for a resident F16 team. A separate evidence-only planner on96 TAT-QA contexts changes correct delivery six to ten and wrong delivery23 to25, failing its practical criterion; correct candidates decrease26 to25. A secondary28-context comparison gives no delivery gain. Disabling prompt caching on a fixed workload reduces peak worker commit approximately6.101 to5.264 GB while preserving predictions. We distinguish that engineering improvement from reasoning accuracy, and application commit from physical-memory feasibility. Paired uncertainty, scoring sensitivity, interrupted runs and full historical support bound the findings to evaluated recipes.''',
'''The operational question for a local reasoning system is how much useful output it delivers within measured resource ceilings. A system that withholds almost everything can consume less elapsed inference time without becoming a useful solver; a smaller set of separately resident models can also use more memory than a larger quantized model. This article examines these trade-offs in completed CPU-only financial-reasoning recipes. Its framing emphasizes measured memory, latency and coordination costs alongside correct, wrong and withheld deliveries. The studies retain different models/precision/runtimes and cannot identify a pure architecture or memory-scaling effect.''',
'''Measured headroom and reasoning performance are separate outcomes. The cache intervention preserves output while reducing observed commit; the planner adds cost and wrong deliveries without increasing correct candidates. The resident F16 team fails to retain useful correct coverage in the paired deployment. These results support explicit application-level accounting, not a universal allocation rule or proof of physical8 GB feasibility.'''),
('23_MDPI_Information','information','Evidence Provenance, Calculation Semantics and Selective Delivery in Financial Question Answering',
'''Source provenance and arithmetic execution constrain a numerical answer without establishing that it answers a financial question. We analyze this distinction in completed local language-model experiments. A160-question FinQA comparison yields78 reported-correct deliveries for a quantized14B pipeline and five for a resident F16 team; raw execution matching changes the first result to38. Reference-informed operation and operand constraints later recover ten of15 diagnostic cases, but an evidence-only planner on96 TAT-QA contexts increases wrong deliveries23 to25 while correct candidates decrease26 to25. Despite four additional correct deliveries, it fails its practical criterion; a secondary comparison gives no delivery gain. We retain paired uncertainty, stronger baselines, scorer sensitivity and resource limitations. The contribution is a bounded analysis of how available source information fails to become a semantically justified delivered calculation, not a new information-theoretic law or universal architecture ranking.''',
'''Information in a source document is not equivalent to a justified calculation. A pipeline must identify the right period, quantity, relation and unit, then decide whether to release the resulting answer. Our source-reference grammar checks membership and arithmetic, but those constraints leave financial semantics unresolved. This article organizes the completed evidence around the transition from source provenance to calculation meaning and selective delivery. It presents the failed evidence-only planner alongside favorable oracle diagnostics without treating the latter as a deployable algorithm. No new information-theoretic guarantee or autonomous financial validity is claimed.''',
'''Source membership and executable arithmetic remain weaker than financial semantic correctness. The evaluated planner fails its practical requirement while answer-key constraints reveal conditional recoverability. Correct-candidate generation and final delivery can move in opposite directions, so neither provenance nor aggregate delivery accuracy alone explains reliability. These conclusions concern the evaluated recipes and retain the limitations of scoring, resource measurement and public-data exposure.''')]
def spacing(s):
 s=re.sub(r'(?<=[a-z])(?=\d)',' ',s).replace('Qwen 2.5','Qwen2.5')
 return s
for folder,journal,title,abstract,intro,conclusion in configs:
 d=L/folder;copy_project(L/'15_MDPI_MAKE/official_mdpi',d)
 s=(d/'main.tex').read_text();s=s.replace('[make,article,submit,moreauthors]','['+journal+',article,submit,moreauthors]')
 s=re.sub(r'\\Title\{[^}]+\}',lambda _:r'\Title{'+title+'}',s,count=1)
 s=re.sub(r'\\abstract\{[^}]+\}',lambda _:r'\abstract{'+spacing(abstract)+'}',s,count=1)
 s=re.sub(r'\\section\{Introduction\}.*?\\section\{Related Work\}',lambda _:r'\section{Introduction}'+spacing(intro)+r'\section{Related Work}',s,count=1,flags=re.S)
 s=re.sub(r'\\section\{Conclusion\}.*?\\section\*\{Supplementary Materials\}',lambda _:r'\section{Conclusion}'+spacing(conclusion)+r'\section*{Supplementary Materials}',s,count=1,flags=re.S)
 (d/'main.tex').write_text(s)
 shutil.copy2(L/'07_ICML/build.ps1',d/'build.ps1');print(folder)

d=L/'14_SN_Computer_Science';copy_project(L/'13_Springer_journal',d)
s=(d/'main.tex').read_text()
s=re.sub(r'\\title\{[^}]+\}',lambda _:r'\title{Reproducible Failure Analysis of Resource-Constrained Financial Reasoning Systems}',s,count=1)
abstract=r'''\textbf{Purpose:} We examine why source evidence and executable arithmetic do not reliably yield useful financial answers under local inference ceilings, and whether evidence-only planning can realize diagnostic recovery potential. \textbf{Methods:} Saved predictions support a paired160-question FinQA deployment comparison and separate Windows candidate-generation and planning studies. We distinguish candidate correctness, delivered correctness, wrong delivery and withholding, with paired uncertainty and qualified resource measurements. \textbf{Results:} A quantized14B recipe delivers78 reported-correct answers versus five for a resident F16 team; raw scoring changes the first count to38. Reference-informed constraints recover ten of15 diagnostic cases. An evidence-only planner on96 TAT-QA contexts instead changes correct deliveries six to ten and wrong deliveries23 to25 while correct candidates decrease26 to25, failing its practical criterion. The exact paired correct-delivery p-value is0.125; a secondary28-context comparison gives no delivery gain. \textbf{Conclusion:} Evidence availability, calculation construction and selective delivery require separate evaluation. The findings concern specific recipes, not a universal architecture/precision effect or autonomous financial safety.'''
s=re.sub(r'\\abstract\{.*?\}\n\\keywords',lambda _:r'\abstract{'+spacing(abstract)+'}\n'+r'\keywords',s,count=1,flags=re.S)
intro='This systems study emphasizes reproducible failure attribution: which parts of a local financial-reasoning pipeline are supported by saved evidence, which conclusions depend on numerical scoring, and which resource claims remain unestablished? We retain the completed deployment comparison and separate quantized planning experiments as complementary investigations. The article supplies a trace-based empirical account, with the full historical condition census, statistical procedures, conditional mathematical results and worked examples preserved in comprehensive supporting material. It proposes no new algorithm and does not infer a pure architectural effect from confounded recipes.'
s=re.sub(r'\\section\{Introduction\}.*?\\section\{Related Work\}',lambda _:r'\section{Introduction}'+intro+r'\section{Related Work}',s,count=1,flags=re.S)
s=s.replace(r'\section*{Declarations}',r'\section*{Statements and Declarations}')
(d/'main.tex').write_text(s);shutil.copy2(L/'07_ICML/build.ps1',d/'build.ps1');print(d.name)
# Optional fields required by sn-jnl must come from verified primary metadata.
overrides=json.loads((L/'shared/bibliographic_location_overrides.json').read_text())
p=d/'references.bib';s=p.read_text()
for key,item in overrides.items():
 start=s.index('@InProceedings{'+key+',');end=s.index('\n}',start)+2
 block=s[start:end].replace('address={Online}','address={'+item['address']+'}')
 s=s[:start]+block+s[end:]
p.write_text(s)
