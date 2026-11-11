"""Generate the complete comparative coverage audit with compiled page references."""
from pathlib import Path
from collections import Counter
import re,json,hashlib
import pymupdf
ROOT=Path(__file__).resolve().parents[2];PAPER=ROOT/'paper';OUT=PAPER/'revised_aaai'

def sections(path):
    text=path.read_text(encoding='utf-8');result=[];sec=sub=0
    for m in re.finditer(r'\\(section|subsection)\{([^\n]+?)\}',text):
        level,title=m.groups()
        if level=='section':sec+=1;sub=0;num=str(sec)
        else:sub+=1;num=f'{sec}.{sub}'
        result.append((num,title))
    return result
def page_map(path):
    # .toc records actual rendered pages (including the supplement navigation pages).
    out={}
    if path.exists():
        for line in path.read_text().splitlines():
            m=re.search(r'\\numberline \{([\d.]+)\}.*\}\{(\d+)\}\{',line)
            if m:out[m[1]]=int(m[2])
    return out
def main():
    s_pages=page_map(OUT/'supplement.toc')
    # Main style suppresses a TOC; locate headings in extracted PDF text.
    md=pymupdf.open(OUT/'main.pdf');m_pages={}
    for num,title in sections(OUT/'main.tex'):
        for i,page in enumerate(md):
            t=' '.join(page.get_text().split())
            if title in t:m_pages[num]=i+1;break
    def loc(dest):
        bits=[]
        for token in dest.split(','):
            token=token.strip();doc=token[0];num=token[1:];pages=s_pages if doc=='S' else m_pages
            bits.append(f'{doc} §{num} p{pages[num]}' if num in pages else token)
        return '; '.join(bits)
    # Every original numbered section/subsection. Each record describes the loss in M0/S0 and its final treatment.
    # Original pages were checked against the complete 37-page PDF, not inferred from source length.
    records=[
('1','1–2','Condensed without losing substance','Condensed without losing substance','M1','Motivation, scope and bounded contribution; avoid universal novelty or legal-locality claims.'),
('1.1','1–2','Condensed without losing substance','Condensed without losing substance','M1,S9.2','Memory-limited financial reasoning motivation retained; regulatory mandates not asserted.'),
('1.2','2','Partially omitted','Condensed without losing substance','M2,S14','Resource/precision precedents restored; no exhaustive first-ever gap claim.'),
('1.3','2','Partially omitted','Condensed without losing substance','M1,S10,S11,S12','Scientific contributions restored; historical commit/script/figure counts excluded as stale bookkeeping.'),
('1.4','2','Fully retained','Fully retained','M1,M5,S6','No 32 GB results, no factorial architecture or precision interpretation.'),
('2','2–3','Partially omitted','Condensed without losing substance','M3,S9.2,S11','Background reorganized around explicit methods and assumptions.'),
('2.1','2','Partially omitted','Moved to supplement','S9.2','Budget formula, host reserve, cap reduction and sampling limitations restored.'),
('2.2','2','Partially omitted','Moved to supplement','S9.2,S11.3','Model file bytes and precision accounting restored; disk/RSS/commit distinguished.'),
('2.3','2–3','Condensed without losing substance','Fully retained','M3.1,S10.1,S11.1','C/W/H, coverage and selected-risk denominators retained explicitly.'),
('3','3–5','Partially omitted','Condensed without losing substance','M2,S14','Focused verified related work plus restored closest financial/deployment antecedents.'),
('3.1','3','Condensed without losing substance','Condensed without losing substance','M2,S14','Equal-token comparison retained; token ceilings do not equalize actual compute.'),
('3.2','3','Partially omitted','Condensed without losing substance','S14','Positive small-agent/tool-access counterevidence restored; unrelated benchmark percentages excluded.'),
('3.3','3','Partially omitted','Condensed without losing substance','M2,S11.6,S14','Failure taxonomy and error-propagation limits retained; no measured Markov cascade asserted.'),
('3.4','3','Partially omitted','Condensed without losing substance','S14','AWQ and quantized-agent process-failure precedents restored; no claim GGUF Q4 is AWQ.'),
('3.5','3','Partially omitted','Condensed without losing substance','M2,S14','FinQA, TAT-QA and Bench360 context restored; no cross-paper performance imported.'),
('3.6','3–4','Partially omitted','Condensed without losing substance','M2,S14','FinMAN/DCRC restored alongside VeriFin/BudgetVerify; components not claimed novel.'),
('3.7','4–5','Completely omitted','Condensed without losing substance','M2,S9.1,S14','Comparison dimensions discussed; old categorical not-located novelty matrix excluded as incomplete literature evidence.'),
('4','4','Partially omitted','Fully retained','M1,S9.1','RQ1–RQ4 and H1–H4 restored with outcome dispositions; no retrospective confirmatory battery.'),
('5','4–8','Partially omitted','Fully retained','M3,S2,S9,S12','Methodology reconstructed across distinct studies and historical controls.'),
('5.1','4–5','Partially omitted','Fully retained','M1,M3,S9','Distinct regimes, frozen primary and synthetic-to-natural-task rationale restored.'),
('5.2','4','Partially omitted','Fully retained','M3.2,S2.1,S9.2','Reserve/context probes, runtime, ceilings and absent FLOP/energy measurement explicit.'),
('5.3','4,6','Condensed without losing substance','Fully retained','M3.2,S2,S9.2','Unadapted instruction checkpoints, sizes, precision, residency and adapter asymmetry explained.'),
('5.4','4','Condensed without losing substance','Fully retained','M3.1,S13','Program references, constants, allowed operations and execution/review/delivery requirements retained.'),
('5.5','6–7','Condensed without losing substance','Fully retained','M3.2,S2.1,S10.4','All three profiles and bundled-component confounding retained.'),
('5.6','6','Partially omitted','Fully retained','M3,S2.4,S9.3,S10.3','Report selection, cohort overlaps, public-source status, synthetic counts and gold step counts restored.'),
('5.7','6','Condensed without losing substance','Fully retained','M3.4,S3,S11.1','Scoring units, tolerance, unsupported labels, candidate/delivery definitions and official-score distinction retained.'),
('5.8','6','Partially omitted','Fully retained','M3.4,S10.2,S12','Primary estimand versus post-hoc testing, clustering, multiplicity and sensitivity restored.'),
('5.9','7–8','Partially omitted','Moved to supplement','S11,S12','All T1–T12 mathematical procedures, null assumptions, boundaries and decision standards restored/corrected.'),
('5.10','8','Partially omitted','Condensed without losing substance','S1,S2,S6,S14','Hash/replay lineage retained; inaccessible original SSD tarball not falsely released.'),
('6','8–29','Partially omitted','Fully retained','M4,S4,S5,S8,S9.3,S10,S12','Headline, historical, negative and detailed statistical evidence restored with distinct scopes.'),
('6.1','8–9','Completely omitted','Moved to supplement','S9.3,S13.6','175-case synthetic metrics, hardening failures, platform probes and sentinel caveat restored.'),
('6.2','10–11','Partially omitted','Moved to supplement','S5.1,S8,S9.3,S12.4','All 15 conditions including memory, adaptation, critic, serving and external controls retained.'),
('6.3','10,12','Fully retained','Fully retained','M4.1,S4,S10.4','All six accuracy conditions retained; original and Ubuntu timing/RSS kept separate.'),
('6.4','10,12–13','Partially omitted','Fully retained','M4.1,S10.1','Both full transition matrices and report-rate comparison restored; raw MAS-only correct case caveat added.'),
('6.5','10,14–15','Partially omitted','Moved to supplement','M4.1,S10.2,S12','All four interval endpoints, company/equal-report/deletion sensitivity and adjustments restored.'),
('6.6','10,15–16','Partially omitted','Fully retained','M4.1,S10.3,S11.1','Complete candidate/gate counts and q/p/a/b decomposition restored; causal interpretation bounded.'),
('6.7','10,16–17','Partially omitted','Fully retained','M4.1,S10.4,S12.4','All bundle/repair contrasts and intervals restored; run-specific time differences retained.'),
('6.8','10,16–17','Condensed without losing substance','Fully retained','M3.4,M4.1,S3,S10.3,S13.5','48 discordant delivery labels, 2x2 table and percent/fraction example restored.'),
('6.9','10,18–19','Partially omitted','Moved to supplement','M4.1,S10.3','Both complexity partitions and retrieval-completeness strata restored with reference dependence.'),
('6.10','18–21','Partially omitted','Moved to supplement','S10.4','Latency, prompt/output tokens, stage work and amortized work/correct restored for both runs.'),
('6.11','19,21','Partially omitted','Fully retained','M5,S6,S10.4','Reserve/context/swap/continuation chronology restored and separated from Ubuntu resource-qualified repeat.'),
('6.12','19,22–23','Completely omitted','Moved to supplement','S11.2','Loss-based utility, raw/reported switch points, abstention cost and always-withhold comparator restored.'),
('6.13','19,23–29','Partially omitted','Moved to supplement','S10.2,S12.4','All 21 comparisons, 126 endpoint rows and complete JSON test fields restored; overbroad interpretations corrected.'),
('7','29–30','Completely omitted','Moved to supplement','M4.1,S13','All five original examples plus score-disagreement case restored from saved traces.'),
('7.1','29','Completely omitted','Moved to supplement','S13.1','Shared ABMD success, source quantities and same program; historical timing not applied to Ubuntu.'),
('7.2','29','Completely omitted','Fully retained','M4.1,S13.2','AAPL evidence found but drafter abstains, exact program and source subtraction restored.'),
('7.3','29–30','Completely omitted','Moved to supplement','S13.3','AAPL max-grammar limitation, wrong SAS PASS and caught MAS operand error restored.'),
('7.4','30','Completely omitted','Fully retained','M4.1,S13.4','PNC incorrect team PASS restored; SAS reported/raw correctness distinction corrected.'),
('7.5','30','Completely omitted','Moved to supplement','S13.6','Synthetic NOT_PROVIDED versus MISSING contract error and malformed MAS denominator restored.'),
('8','30–32','Partially omitted','Moved to supplement','S11,S12','Every P1–P10 and J1–J12 reviewed individually below; valid substance restored with corrections.'),
('8.1','30–31','Partially omitted','Moved to supplement','S11','Conditional identities, utility/memory/uncertainty bounds and nonidentification restored.'),
('8.2','31–32','Partially omitted','Moved to supplement','S12','Paired likelihood, variance, null assumptions, multiplicity and interpretation restored/corrected.'),
('9','32–34','Condensed without losing substance','Condensed without losing substance','M5,S9.1,S11.6','Bounded empirical argument retained; causal capacity, universal precision and novelty overclaims excluded.'),
('9.1','32','Fully retained','Fully retained','M4.1,M6,S9.1','Operational H1 failure retained, with raw-score exception to no uniquely correct delivery.'),
('9.2','32–33','Condensed without losing substance','Fully retained','M4.1,M5,S10.3,S11.6,S13','Generation bottleneck and examples restored without identifying a unique causal mechanism.'),
('9.3','33','Condensed without losing substance','Fully retained','M4.1,M5,S10.1,S11.3','Resident footprint and weak precision-on-eight-answers interpretation retained.'),
('9.4','33–34','Partially omitted','Condensed without losing substance','S9.1','Four gap dispositions restored with baseline fairness left partly unresolved.'),
('9.5','33','Partially omitted','Condensed without losing substance','M5,S9.2,S14','Measured cautions retained; blanket largest-quantized-model and disable-mmap deployment prescriptions excluded.'),
('10','33','Condensed without losing substance','Fully retained','M5,S2.4,S6,S11,S12','Construct/internal/external/statistical/resource validity retained and expanded with current missing evidence.'),
('11','33','Condensed without losing substance','Condensed without losing substance','M5,S9.1,S14','Public/synthetic data and no autonomous financial-decision validation retained; no invented compliance certification.'),
('12','33–34','Condensed without losing substance','Condensed without losing substance','M6,S6,S9.1','Bounded conclusion and unresolved validity controls retained; stale future-run scheduling removed.'),
('A','36–37','Partially omitted','Moved to supplement','S1,S6,S14','Evidence/reproduction hierarchy rebuilt around available handoff; old missing SSD export paths treated historically.'),
('B','36','Moved to supplement','Moved to supplement','S7,S14','Analysis, restoration and known-value test commands retained; inaccessible SSD-specific path assumptions disclosed.'),
('C','36','Condensed without losing substance','Condensed without losing substance','M3,S14','Useful symbols and memory/quantization terminology defined; irrelevant compliance acronym expansion excluded.'),
]
    # Map original titles directly; appendices use source section numbers after 12.
    titles=dict(sections(ROOT/'output/aaai/main.tex'))
    original_keys=set(titles)-{'13','14','15'}|{'A','B','C'}
    assert original_keys=={r[0] for r in records},'Missing or duplicate original section mapping'
    for key,title in [('A','Artefact and Provenance Map'),('B','Reproduction'),('C','Glossary')]:titles[key]=title
    lines=['# Scientific coverage audit and restoration','',
      'Completed comparative reading, raw-evidence reconciliation and restoration. Page numbers below refer to PDF pages, including navigation pages.','',
      '## Versions and counting method','',
      'O = original `output/pdf/RESEARCH_PAPER_AAAI.pdf`; M0/S0 = preserved shortened `output/pdf/AGERE_FINAL_AAAI.pdf` and `AGERE_FINAL_SUPPLEMENT.pdf`; M/S = revised `paper/revised_aaai/main.pdf` and `supplement.pdf`. All originals remain unchanged, checked against `preserved_versions.json`. Word counts use whitespace-separated PyMuPDF extracted text, including tables, captions, references and navigation; they are approximate and not unique-prose counts.','']
    for name,path in [('O',ROOT/'output/pdf/RESEARCH_PAPER_AAAI.pdf'),('M0',ROOT/'output/pdf/AGERE_FINAL_AAAI.pdf'),('S0',ROOT/'output/pdf/AGERE_FINAL_SUPPLEMENT.pdf'),('M',OUT/'main.pdf'),('S',OUT/'supplement.pdf')]:
        d=pymupdf.open(path);lines.append(f'- {name}: {len(d)} pages; {len(" ".join(p.get_text() for p in d).split()):,} extracted words.')
    lines+=['','The original versus M0+S0 reduction was about 38%. The revised main remains concise; the expanded supplement restores supporting science. Added later Windows/planner evidence means this is not a verbatim recreation of the old manuscript.','',
    '## Classification rules','',
    'Each old numbered section/subsection is classified twice: its status in M0/S0 before this restoration, and its final disposition. “Fully retained” concerns scientific content, not exact wording. “Condensed without losing substance” merges equivalent exposition. “Moved to supplement” preserves supporting content with a main-paper summary where essential. Partial/complete omissions are named and justified; they are not hidden by an artifact inventory. Detailed subitems below override a broad parent classification.','',
    '## Complete section-by-section comparison','',
    '| Original item and PDF pages | Status in M0/S0 | Final disposition | Final location | Scientific treatment |','|---|---|---|---|---|']
    for key,pages,before,after,dest,note in records:
        lines.append(f'| O §{key} {titles.get(key,"")} pp{pages} | {before} | {after} | {loc(dest)} | {note} |')
    lines+=['','For the pre-restoration locations: M0 §1 pp1–2; §2 pp1–2; §3 pp2–3; §4.1 pp3–4, §4.2 p4, §4.3 pp4–5, §4.4 pp5–6; §5 pp6–7; §6 p7. S0 §1 p1; §2 pp1–3; §3 pp3–4; §4 pp4–5; §5.1 p6, §5.2 pp6–7, §5.3 p7, §5.4 pp7–8, §5.5 p8; §6 pp8–9; §7 p9; §8 pp9–10. These are the comparison locations for the classifications above.','',
    '## Every original table and figure','',
    '| Original asset and page | Before restoration | Final location or justified exclusion |','|---|---|---|']
    table_pages={1:'5',2:'5',3:'6',4:'7',5:'8',6:'9',7:'11',8:'11',9:'12',10:'12',11:'12',12:'14',13:'14',14:'15',15:'16',16:'16',17:'16',18:'18',19:'18',20:'24',21:'24',22:'24',23:'24',24:'25',25:'25',26:'25',27:'25',28:'26',29:'26',30:'26',31:'27',32:'27',33:'27',34:'28',35:'28',36:'34',37:'37',38:'37'}
    mappings={1:('Completely omitted','M2,S14','Old binary novelty matrix excluded; verified competing approaches compared in prose.'),2:('Partially omitted','M3,S2,S9','Distinct regimes reconstructed, no pooling.'),3:('Partially omitted','S9.2','Exact GGUF bytes restored.'),4:('Condensed without losing substance','M3.2,S2.1','Profiles retained.'),5:('Partially omitted','S12','Inferential hierarchy restored with post-hoc status corrected.'),6:('Completely omitted','S9.3','All synthetic denominators restored.'),7:('Partially omitted','S8','All 15 conditions and memory restored.'),8:('Partially omitted','S8','Continuation of condition census.'),9:('Fully retained','S4,S10.4','Accuracy retained; historical/Ubuntu resources distinct.'),10:('Partially omitted','S10.1','Conditional denominators and descriptive Wilson intervals restored.'),11:('Partially omitted','M4.1,S10.1','Full paired matrix restored.'),12:('Partially omitted','S10.2','All four intervals and family-width sensitivity restored.'),13:('Partially omitted','S10.2','Equal weighting, deletion range and adjusted testing restored.'),14:('Condensed without losing substance','S10.3','Exact candidate/gate table restored.'),15:('Completely omitted','S10.3,S11.1','q/p/a/b factorization restored.'),16:('Partially omitted','S10.4,S12.4','Every paired ablation interval restored.'),17:('Condensed without losing substance','S3,S10.3','2x2 score concordance partition printed.'),18:('Completely omitted','S10.3','Both reference strata partitions restored.'),19:('Partially omitted','S10.4','Prompt/output/stage/correct cost restored; run distinction.'),36:('Partially omitted','S9.1','Gap dispositions corrected, especially baseline confounding.'),37:('Moved to supplement','S1,S6,S14','Evidence map updated to available artifacts.'),38:('Moved to supplement','S14','Repository protocols/decisions included in map.')}
    for n,page in table_pages.items():
        before,dest,note=mappings.get(n,('Partially omitted','S10.2,S12.4','Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined.'))
        lines.append(f'| O Table {n} p{page} | {before} | {loc(dest)}. {note} |')
    figures=[('1','9','Completely omitted','S9.3','Synthetic graph replaced by exact numerator/denominator table; a percent-only graph would obscure unmatched invention denominators.'),('2','11','Moved to supplement','S8','All 15-condition results retained in table; duplicate stacked plot not restored.'),('3','12','Fully retained','M4.1','Main all-six-job figure retains both scores.'),('4','13','Partially omitted','S10.1','Both paired transition heatmaps restored.'),('5','13','Completely omitted','S10.3','Report-rate heterogeneity scatter restored.'),('6','14','Partially omitted','S10.2','All primary intervals restored as precise tables; no duplicate interval plot.'),('7','15','Completely omitted','S10.2,S12.2','Bootstrap percentile values, algorithm and assumptions retained; redundant distribution illustration excluded.'),('8','15','Completely omitted','S10.2','Company/report interval comparison retained in numerical table.'),('9','16','Condensed without losing substance','S10.3','Candidate/gate flow retained in complete table and formula.'),('10','17','Partially omitted','S10.4','Repair outcomes/time reconciled for both runs; duplicate cost plot excluded.'),('11','17','Condensed without losing substance','S10.3','Metric disagreement retained as exact counts and worked example.'),('12','18','Completely omitted','S10.3','Reference-step complexity figure restored; family counts in table.'),('13','19','Partially omitted','S10.3','All retrieval-stratum numerators/denominators printed; duplicate bar plot excluded.'),('14','20','Partially omitted','S10.4','All six median/summed inference measurements retained; full distributions newly retained in resource JSON.'),('15','20','Completely omitted','S10.4','Stage work chart and tokens/timing table restored.'),('16','21','Partially omitted','S9.2,S10.4','Model file sizes plus distinct run RSS values in tables.'),('17','21','Partially omitted','S6,S10.4','Swap failures and all Ubuntu sample checks retained; a subset-of-attempts trace plot excluded as potentially misleading.'),('18','22','Completely omitted','S11.2','Utility curve restored with always-withhold comparator.'),('19','22','Completely omitted','S11.2','Withholding-cost sensitivity restored; repair formula corrected.'),('20','23','Completely omitted','M4.1,S10.1,S11.2','All six C/W/H operating points retained in main figure and tables; no interpolated risk-coverage curve claimed.')]
    for n,page,before,dest,note in figures:lines.append(f'| O Figure {n} p{page} | {before} | {loc(dest)}. {note} |')
    lines+=['','## Formal propositions and derivations: validity decisions','',
    '| Original result | Validity and correction | Final treatment |','|---|---|---|']
    props=[('P1 (p30)','Valid partition identity; lower wrong count alone can mean more withholding.','S11.1'),('P2 (p30)','Valid for a fixed candidate accept/reject gate only; cannot generalize to repair, new generation or another candidate pool.','S11.1'),('P3 (p30)','Valid empirical chain rule without independence; conditional factors undefined when their denominator is zero.','S11.1'),('P4 (p30)','Valid sample utility switch algebra; preference weights are assumed, not learned safety thresholds; restore raw and always-withhold comparisons.','S11.2'),('P5 (p30)','Partially invalid as a general kappa formula: add +3*kappa for reduced withholding. Positive compute cost does not make repair universally worse for all loss choices.','S11.2'),('P6 (p30)','Conditional storage accounting only under full residency/disjoint allocations; cannot universally lower-bound physical RSS by entire file bytes.','S11.3'),('P7 (pp30–31)','Valid bounded-independent-contribution inequality with fixed weights; not a random-denominator/sampling-design guarantee. Effective clusters measure weight concentration.','S11.4'),('P8 (p30)','Valid partition identity for metric disagreement; does not adjudicate the correct scorer.','S11.5'),('P9 (p31)','Valid minimum p for the stated exact conditional McNemar procedure. Old “no test could be significant” statement excluded.','S11.5'),('P10 (pp31–32)','Cauchy–Schwarz bound valid for Q=(sum S)^2/sum S^2 and its chosen tail. Universal bound on all valid cluster-test p-values is false and excluded.','S11.5'),('Nonidentification (p30)','Valid design limitation; source-visible roles invalidate a message-only Markov information-loss premise.','S11.6')]
    for prop,note,dest in props:lines.append(f'| {prop} | {note} | {loc(dest)} |')
    js=[('J1','Paired covariance derivation valid; independent-arm testing inappropriate to this pairing.','S12.1'),('J2','Conditional binomial exactness requires independent pairs; conservative does not cure clustering.','S12.1'),('J3','Asymptotic chi-square conditional on adequate discordances; continuity correction uses max(abs(b-c)-1,0), matching code.','S12.1'),('J4','Wald variance formula retained with boundary failures; no favorable interval cherry-picking.','S12.1'),('J5','Bowker/SM formulas retained with rank handling and sparse/case-IID caveats.','S12.2'),('J6','Cluster-variance and CR1 formulas retained; normal/score tests asymptotic. Exclude implied measured ICC and literal effective-IID sample-size claims.','S12.2'),('J7','Cluster bootstrap ratio consistency requires exchangeability, regularity and nonzero denominator; same-sign resamples need not always touch zero.','S12.2'),('J8','Sign-flip exactness requires independent sign-symmetric cluster sums; report-sign needs equiprobable signs. Zero mean is insufficient.','S12.3'),('J9','Holm proof valid for valid marginal p-values under arbitrary dependence; cannot repair invalid input tests. Withholding-family exclusion is a design choice.','S12.3'),('J10','Wilson score formula retained as case-IID descriptive; no guarantee under clustered selected deliveries.','S12.3'),('J11','Finite risk difference and discordant odds separation retained. Old blanket dismissal of linear/clustered regression is excluded.','S12.3'),('J12','Scope, deterministic cohort, single seed, no equivalence and effect-size interpretation retained.','S12.3')]
    for key,note,dest in js:lines.append(f'| {key} (O pp31–32) | {note} | {loc(dest)} |')
    lines+=['','## Raw evidence, computational checks and remaining weaknesses','',
    'The restoration is not an audit only against prose. `coverage_evidence_checks.json` pins raw inputs. The reconciliation checks 960 historical 16 GB case rows against their raw ledgers and Ubuntu score/delivery records, independently executes/rescores all 768 earlier FinQA programs against their source packets, and independently rescores 350 synthetic answers from original documents and deterministic tools. It recomputes all 126 endpoint rows and 42 metric-specific transition/symmetry blocks, cross-checks probability tails with SciPy and reproduces report/company sensitivity. The established raw-score audit separately re-executes 1,920 Ubuntu programs, rescoring Windows FinQA/TAT-QA ledgers; all 668,817 memory samples across 16 attempts are checked. Ten existing known-value tests pass. These checks do not independently adjudicate financial truth or regenerate model/training trajectories.','',
    'Remaining evidentiary weaknesses: one Qwen2.5 family; confounded recipe comparisons; shared/reused exploratory cohorts; deterministic selection and possible pretraining overlap; no TAT-QA report grouping; sparse planner gains; no complete secondary 7B baseline; Windows commit does not prove physical 8 GB/no paging; Ubuntu interruptions and missing original tarball/bootstrap log; no independent financial-label adjudication; incomplete optimized/factorial baselines. None is filled with estimated data.','',
    'No negative result was intentionally removed. Intentional exclusions are repetitive prose/plots; irrelevant acronym and legal background; unverified external leaderboard numbers/venue claims; stale repository counts and future-run scheduling; universal deployment advice; unsupported causal capacity/Markov/precision conclusions; incorrect generalizations explicitly listed above. Historical artifacts remain available for inspecting every excluded formulation.','',
    '## Main-paper self-containment','',
    'The main document independently defines recipes, cohorts, resource controls, scoring conventions, candidate versus delivery, paired uncertainty, main baselines, oracle access, planner allocation/criterion and failure, interrupted comparison and validity limits. It states the original hypotheses and includes paired transitions and worked failure summaries. The supplement supplies detailed proofs, complete tests, historical controls and reproduction records; it is not required to discover a reversal, an undisclosed negative main result or the reason the planner criterion fails. This is an editorial/scientific assessment, not an external peer-review certification.','',
    'Official venue requirements and unresolved template authentication are recorded in `VENUE_REQUIREMENTS.md`. The public official pages do not specify a numeric supplement cap; portal/file-size rules and the separate checklist must be checked before actual submission. `LITERATURE_COVERAGE.md` additionally records the treatment of every original reference/group, including citations not retained in the revised bibliography.','']
    (PAPER/'COVERAGE_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')
    stats={'section_items':len(records),'old_tables':len(table_pages),'old_figures':len(figures),'formal_items':len(props)+len(js),'status_counts_before':dict(Counter(r[2] for r in records)),'status_counts_after':dict(Counter(r[3] for r in records)),'main_sections':m_pages,'supplement_sections':s_pages}
    (OUT/'coverage_mapping.json').write_text(json.dumps(stats,indent=2))
    print(json.dumps({k:v for k,v in stats.items() if 'sections' not in k},indent=2))
if __name__=='__main__':main()
