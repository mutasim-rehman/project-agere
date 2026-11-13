"""Record the compiled TMLR adaptation and verify frozen evidence; no inference."""
from pathlib import Path
import hashlib, json, re
import pymupdf

L=Path(__file__).resolve().parents[2]
D=L/'26_TMLR'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def write(name,s):(D/name).write_text(s.strip()+'\n',encoding='utf-8')
def read_legacy(p):
 # Preserve pre-existing mixed-encoding bytes in historical logs.
 return p.read_text(encoding='utf-8',errors='surrogateescape')
def addendum(p,heading,s):
 text=read_legacy(p);text=text.split('\n'+heading)[0]
 p.write_text(text.rstrip()+'\n\n'+heading+'\n\n'+s.strip()+'\n',encoding='utf-8',errors='surrogateescape')

row=next(x for x in json.loads((L/'shared/qa/adaptation_checks.json').read_text()) if x['folder']=='26_TMLR')
assert row['pages']==40 and not row['undefined'] and row['overfull_boxes']==0
assert len(row['figure_bytes_verified'])==8 and row['bibliography_keys']==28
assert all(x['locations'] for x in row['mapping'])
inv=json.loads((L/'shared/source_inventory/canonical_scientific_inventory.json').read_text())
frozen={k:sha(L/'shared'/k)==v for k,v in inv['files'].items()}
assert all(frozen.values()),'Frozen scientific evidence changed'
previous=json.loads((L/'production_status.json').read_text())
preserved={x['folder']:sha(L/x['folder']/'main.pdf')==x['sha256'] for x in previous if x['folder']!='26_TMLR'}
assert all(preserved.values()),'Existing PDF changed'
kit=L/'shared/official_templates/tmlr/tmlr-style-file-main'
styles={n:sha(D/n)==sha(kit/n) for n in ['tmlr.sty','tmlr.bst','fancyhdr.sty']}
assert all(styles.values())
support={p.name:(D/p.name).read_text().replace('\\newpage\nAmong 126 SAS deliveries,','Among 126 SAS deliveries,')==p.read_text() for p in (L/'06_NeurIPS').glob('*.tex') if p.name not in ['main.tex','checklist.tex']}
assert all(support.values()),'Scientific support changed'
assert (D/'references.bib').read_bytes()==(L/'MASTER_REFERENCES.bib').read_bytes()
doc=pymupdf.open(D/'main.pdf');text='\n'.join(p.get_text() for p in doc)
assert all(term in text for term in ['Statement of Broader Impact','Research and Manuscript Transparency','0.125','668,817'])
fonts={str(f) for page in doc for f in page.get_fonts() if 'Type3' in str(f)}
assert not fonts and '??' not in text
aux=(D/'main.aux').read_text()
main_end=int(re.search(r'\\newlabel\{main-content-end\}\{\{[^}]*\}\{(\d+)\}',aux)[1])
qa=dict(verified='2026-11-13',pages=len(doc),words=row['words'],word_method='Whitespace-separated PyMuPDF extracted words, including references, captions, page/header text and appendices; not a venue word limit',core_scientific_endpoint=main_end,appendix_start=13,sha256=sha(D/'main.pdf'),overfull_boxes=0,undefined_references=False,type3_fonts=0,bibliography_keys=28,master_bibliography_byte_match=True,canonical_figures=8,canonical_evidence_hashes=frozen,previous_pdfs_unchanged=preserved,official_styles_byte_match=styles,scientific_support_unchanged=support,visual_review='All 40 pages inspected in contact sheets; enlarged results, references, impact and repaired footer pages checked; no observed overlap/clipping',experimental_inference_performed=False,submission_ready=False,policy_status='HUMAN-REVIEW-REQUIRED',remaining=['Human scientific and citation review','Actual authors, tool versions/disclosures and institutional/license declarations','Confirm no archival publication, acceptance or parallel submission of overlapping results','OpenReview profiles, conflicts, action-editor recommendations and quotas','Anonymous reproducibility package and final current-policy/portal check'])
dump(D/'build_status.json',qa)

write('README.md',f'''# Transactions on Machine Learning Research adaptation

Title: **Evidence, Candidate Generation and Selective Delivery in Memory-Constrained Financial Reasoning**.

Actual manuscript: [main.tex](main.tex); compiled [main.pdf](main.pdf), **40 pages / {row['words']:,} extracted words**. The core scientific argument ends on page {main_end}; impact/transparency and references occupy pages 9–12, with the complete technical appendix on pages 13–40. Word counts include PDF headers, tables and references. This is a substantive empirical/failure-analysis adaptation, not a new experiment or an acceptance claim.

The introduction states three questions about useful correct delivery, candidate construction with available evidence and transfer from oracle constraints to deployable planning. The abstract and conclusion explicitly retain the failed planner rule, wrong deliveries, reduced correct candidates, secondary null, stronger baselines and confounded deployment recipes. All extended methods, historical controls, paired statistics, conditional mathematics and worked failures are embedded after the references. See [COVERAGE_AUDIT.md](COVERAGE_AUDIT.md).

The unmodified official JmlrOrg style, bibliography style and bundled fancyhdr are included with source provenance and license under `template/`. No fixed page limit was assumed; supporting detail is separated from the nine-page core. A local header honestly says author-review draft/not submitted instead of the template's default under-review claim.

Build with PDFLaTeX/BibTeX on PATH: `powershell -ExecutionPolicy Bypass -File publication_library/26_TMLR/build.ps1`. It builds from its own folder and stops on failure. On this host the TeX binaries are `D:\\project-agere\\.local\\texlive\\TinyTeX\\bin\\windows`. The source-production script is `../shared/production/produce_tmlr.py`; do not run new inference. After editing, rerun compilation, coverage checks and visual review before refreshing `build_status.json`.

**HUMAN-REVIEW-REQUIRED; not submitted or submission-ready.** See [VENUE_REQUIREMENTS.md](VENUE_REQUIREMENTS.md) and [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md). No publication, acceptance, archival submission or authorship status is inferred from the existence of other library drafts. Their overlap makes choosing one archival destination essential.
''')
write('VENUE_REQUIREMENTS.md','''# TMLR requirements — verified 2026-11-13

Use the current canonical `jmlr.org/tmlr/` instructions. The user-linked `jmlr.csail.mit.edu/tmlr/` mirror displayed older information; it is not the controlling version for this verification.

## Primary sources and template provenance

- [Author guide](https://jmlr.org/tmlr/author-guide.html): anonymous PDF using official LaTeX; justified length, no fixed page cap; appendix after references in the same PDF; optional anonymous supporting PDF/ZIP up to 100 MB. Appendix/support review is discretionary. CC BY 4.0 applies from submission; authors retain copyright. Preprints are permitted but do not link an identified preprint from the anonymous submission.
- [Editorial policies](https://jmlr.org/tmlr/editorial-policies.html): empirical studies and analyses of learning-system behavior are in scope. Rolling submissions; no author fees. Evidence and reader interest are assessed without requiring a winning algorithm. This is not an assessment that the draft will meet the acceptance standard.
- [Acceptance criteria](https://jmlr.org/tmlr/acceptance-criteria.html), [ethics](https://jmlr.org/tmlr/ethics.html), [code of conduct](https://jmlr.org/tmlr/code.html): authors must read the complete current policies. Include concrete broader impacts where harm is plausible; this manuscript includes financial-error/withholding risks and qualified mitigations.
- Author-guide-linked official [JmlrOrg template](https://github.com/JmlrOrg/tmlr-style-file). Downloaded via legitimate GitHub codeload, commit `7bf90efe3a0debbba703c05c43f3ff7e4d4a2992`; ZIP SHA256 `48f9f972cc812d2cfc8032a78578c2f5d8939b92fbd4f61095e8cbeb3394f92d`. See `template/provenance.json` and Apache-2.0 `template/LICENSE`. `tmlr.sty`, `tmlr.bst`, `fancyhdr.sty` match the official kit byte-for-byte. Article 10pt/default TMLR typography and author-year references retained; no margin/style modifications.

## Authorship and policy gates

LLMs may be general-purpose assistive tools; human authors remain responsible for factual accuracy, plagiarism and scientific integrity. This policy does not prohibit all assisted prose, but generated content is not independently validated by its existence. Human scientific/citation review and applicable disclosures/tool-version checks remain outstanding. Codex assistance and the absence of new inference are stated in the PDF; it does not attest to author approval. No AI is listed as an author.

TMLR does not permit reuse of text, figures or results from an archival paper already published, accepted or submitted in parallel, including expanded conference papers. Preprints and explicitly non-archival work may overlap. **Actual prior publication/submission status must be confirmed by the authors**; the library itself is a set of alternative drafts, not proof of eligibility. Do not submit this and another overlapping archival version simultaneously.

All authors need complete active OpenReview profiles, conflicts and publication histories; action-editor recommendations and IRB/human-subjects, funding and competing-interest information are required in the submission process. Generalized harmonic authorship quotas currently use N1=2/N9=9, doubled for reviewers/action editors; each author's available budget must be checked, including desk-rejected submissions. No author budget or eligibility is assumed here.

The PDF is anonymous at the name/metadata level, but the actual release package and identifying links must receive human anonymity review. The truthful draft header override must only be removed when preparing an actual submission; the default official under-review header is not evidence of submission. Confirm the live portal and all rules again on the chosen submission date. No submission was performed.
''')
write('SUBMISSION_CHECKLIST.md','''# TMLR author-review checklist

## Completed production checks

- [x] Substantive TMLR framing, three explicit research questions and bounded claims.
- [x] Authentic official style/bibliography assets, provenance, license and strict build script.
- [x] Core is scientifically interpretable without the appendix; full methods/history/statistics follow references.
- [x] Failed planner criterion, candidate/delivery distinction, oracle leakage, stronger baselines, secondary null, scorer sensitivity and resource limitations explicit.
- [x] Eight canonical figure byte matches, 28 master bibliography entries, all 60 canonical headings located in compiled PDF; original audit remains available.
- [x] Compile passes; zero overfull boxes, undefined citations/references or Type 3 fonts; all pages contact-sheet inspected and selected pages enlarged.
- [x] Broader impact and manuscript-assistance statements included; draft is honestly labelled not submitted.

## Required actual-author actions

- [ ] Independently review every claim, numerical result, statistical interpretation, citation, example and source artifact; approve responsibility for the complete paper.
- [ ] Confirm no overlapping archival publication, acceptance or parallel submission. Do not treat TMLR as an expanded-conference-paper destination.
- [ ] Confirm actual authors/contributions, exact AI tools/versions/disclosures, data/model licenses, distribution rights, funding, conflicts, IRB/institutional applicability and CC BY 4.0 agreement.
- [ ] Complete every author's OpenReview profile and verify individual submission quotas; provide action-editor recommendations and current portal declarations.
- [ ] Prepare and inspect a genuinely anonymous reproducibility PDF/ZIP (at most 100 MB); remove identifying links/path traces. Existing repository access is not an anonymous submission package.
- [ ] Recheck current policies, metadata, figure readability at normal zoom and final packaging; remove the draft-header override only for actual submission. Do not set accepted status.
- [ ] Choose one archival destination and perform the submission personally. No submission has been authorized or carried out by this production task.
''')
write('MANUSCRIPT_NOTES.md','''# TMLR scientific/editorial adaptation

The destination's emphasis on supported claims and insight into learning-system behavior motivates a failure-analysis narrative. The new title, abstract, introduction, explicit three-question formulation and conclusion focus on transitions between available evidence, executable correct candidates and delivered answers. A new algorithm, general planning theorem, causal architecture superiority and acceptance probability are not claimed.

The scientific methods/results/discussion are reused from the audited canonical record through the complete NeurIPS adaptation. All supporting TeX is unchanged except a page break before one paragraph to avoid footer overlap. The NeurIPS-specific checklist is omitted because it is an event form, not scientific evidence; research transparency and a concrete financial broader-impact statement are included instead. No experiment was rerun or outcome edited. The official style files are unmodified; local header text prevents falsely implying review status.

Study A's original 16 GB F16-team/Q4-monolith comparison and Study B's Windows nominal-8 GB quantized diagnostics remain separate, complementary studies with different data/runtime/model/prompt conditions. Worker commit is not physical-8 GB feasibility. Ubuntu sampled no-swap evidence is qualified by interruptions, sample coverage and missing packaging artifacts. Oracle constraints are answer-key diagnostics, not deployable improvements or a universal attainable upper bound.

The four extra correct planner deliveries remain paired and uncertain (exact p=0.125); two extra wrong deliveries fail the practical rule regardless of the positive bootstrap interval. Correct candidates fall 26 to 25, secondary delivery ties and incomplete 7B runs are visible. Cache headroom improvement is output-preserving and is not an accuracy or no-paging result. Detailed cohort history, corrected scoring, all paired batteries, mathematical assumptions and failures remain in the appendix. This does not resolve the limited generality, grouping/seed/family gaps or other evidentiary weaknesses.

The PDF's 19,192 whitespace-extracted words include captions, headers, references and 28 appendix pages; it is not a word-count-compliant claim because TMLR specifies no such fixed cap. Nine core pages are followed by impact/transparency/references through page 12 and appendix pages 13–40. Human authors can further edit prose after reviewing this evidence-preserving draft, but must not remove unfavorable results to improve the narrative.
''')
mapping=['# TMLR scientific coverage audit','',
 'The original 37-page item audit is preserved at `../shared/source_inventory/COVERAGE_AUDIT.md` (64 sections, 38 tables, 20 historical figures and 23 formal items). Its justified exclusions/corrections remain controlling; unsupported propositions or redundant plots are not restored merely for length. `../ADAPTED_COVERAGE_MAP.md` links every canonical heading to actual destination pages. This document records the new TMLR adaptation, not a claim that heading detection alone validates the research.','',
 '## Retention and intentional changes','',
 '- Fully retained: original hypotheses, Study A/B setup, baselines, metrics, candidate/gate accounting, complete experiment sequence, negative/null controls, uncertainty, resource failures, conditional formal results, worked examples and reproducibility map. All 60 canonical headings have PDF locations below.',
 '- Condensed/reframed: abstract/introduction/conclusion center supported behavioral insights and three explicit questions; scientific findings unchanged. Main core ends page 9.',
 '- Moved/retained in appendix: complete supporting evidence on pages 13–40, after references. Appendix review is discretionary under TMLR, so essential negative results and validity limits are also in the core.',
 '- Intentionally excluded: NeurIPS-specific submission checklist and accepted/preprint conference labels. These contain no unique experiment. Replaced with venue requirements, broader impact and human-author responsibility materials. Prior audit exclusions of unsupported theory and redundant prose remain justified, not silently reversed.',
 '- No additional research: all eight local vector figures match canonical bytes; master bibliography matches byte-for-byte (28 entries). Frozen evidence inventory hashes and all 21 existing main PDFs remain unchanged. Full support TeX matches the existing complete adaptation except one purely typographical page break.','',
 '## Canonical section destinations','']
for x in row['mapping']:mapping.append('- `'+x['source']+'` / '+x['heading']+': '+', '.join(loc.split(':')[-1] for loc in x['locations']))
mapping+=['','## Remaining evidentiary limitations','',
 'Finite task/model/prompt cohorts, sparse paired gains, no multi-seed/family generality, unavailable TAT-QA report clustering, incomplete secondary 7B baselines, scorer/reference ambiguities, confounded recipes and incomplete physical-memory/packaging evidence remain unresolved. They are not filled with estimates or new claims. See PDF discussion and resource-failure appendix, canonical verified-results JSON and `build_status.json`.']
write('COVERAGE_AUDIT.md','\n'.join(mapping))

status=dict(folder='26_TMLR',pages=40,words=row['words'],compiled=True,undefined_references=False,overfull_boxes=0,sha256=sha(D/'main.pdf'),visual_review=qa['visual_review'],scientific_coverage='Complete core and embedded technical appendix; 60 canonical headings, 8 figure byte matches, 28 master references; no changed outcomes',policy_status='HUMAN-REVIEW-REQUIRED',template_status='Official JmlrOrg TMLR kit commit 7bf90efe; unmodified style/bst/fancyhdr')
dump(L/'production_status.json',[x for x in previous if x['folder']!='26_TMLR']+[status])
manifest=json.loads((L/'venue_manifest.json').read_text())
venue=dict(folder='26_TMLR',venue='Transactions on Machine Learning Research (TMLR)',publisher='TMLR/JMLR',type='journal',ranking='No quartile claimed or needed for this user-selected destination',topic_fit='Empirical behavior/failure analysis of learned reasoning and delivery systems',competitiveness='Evidence and reader-interest standard; no acceptance prediction',limits='No fixed page limit; justify length',template='Official TMLR article 10pt / tmlr.sty, tmlr.bst; 7bf90efe',citation_style='Author-year',supplement='Full appendix after references, pp13–40; optional anonymous PDF/ZIP <=100 MB',fees='No author fees',deadline='Rolling; confirm live portal',official_sources=['https://jmlr.org/tmlr/author-guide.html','https://jmlr.org/tmlr/editorial-policies.html','https://jmlr.org/tmlr/acceptance-criteria.html','https://jmlr.org/tmlr/ethics.html','https://github.com/JmlrOrg/tmlr-style-file'],manuscript='26_TMLR/main.tex',pdf='26_TMLR/main.pdf',pages=40,words=row['words'],compilation='COMPILED',scientific_coverage=status['scientific_coverage'],policy='HUMAN-REVIEW-REQUIRED; not submitted or submission-ready',human_actions='Scientific/originality/authorship/license/CC BY review; OpenReview profiles, quotas, declarations and anonymous reproducibility package',last_verified='2026-11-13')
dump(L/'venue_manifest.json',[x for x in manifest if x['folder']!='26_TMLR']+[venue])
report=json.loads((L/'shared/qa/final_pdf_checks.json').read_text())
report['pdfs']=[x for x in report['pdfs'] if x['path']!='publication_library/26_TMLR/main.pdf']+[dict(path='publication_library/26_TMLR/main.pdf',pages=40,sha256=sha(D/'main.pdf'),type3_fonts=0,unresolved_questionmarks=False)]
dump(L/'shared/qa/final_pdf_checks.json',report)
for file in ['README.md','VENUE_MATRIX.md','CHECKPOINT.md','RELEASE_REPORT.md']:
 p=L/file;s=read_legacy(p);s=s.replace('21 compiled main PDFs','22 compiled main PDFs').replace('21compiled main PDFs','22compiled main PDFs').replace('21actual main PDFs','22actual main PDFs').replace('19scientific versions','20scientific versions').replace('in21PDFs','in22PDFs');p.write_text(s,encoding='utf-8',errors='surrogateescape')
addendum(L/'README.md','## TMLR addition — 2026-11-13','[26_TMLR/main.pdf](26_TMLR/main.pdf): 40 pages, 19,192 extracted words; authentic official template, nine-page core and complete supporting appendix. See its requirements, coverage audit and submission checklist. Compiled and visually reviewed, human review/originality gates remain. All earlier manuscripts preserved.')
addendum(L/'VENUE_MATRIX.md','## TMLR addition — 2026-11-13','| Venue | Format and limits | Fees / schedule | Evidence and policy status | Official sources |\n|---|---|---|---|---|\n| TMLR | Official TMLR kit; no fixed cap; 40-page PDF, core9 + declarations/references + appendix pp13–40; anonymous support PDF/ZIP <=100 MB | No author fees; rolling | Complete adapted draft, compiled/visually checked; human review, originality/no overlapping archival publication or parallel submission, profiles/quotas/declarations required | [Author guide](https://jmlr.org/tmlr/author-guide.html), [editorial policies](https://jmlr.org/tmlr/editorial-policies.html), [official kit](https://github.com/JmlrOrg/tmlr-style-file) |\n\nMachine-readable full row: venue_manifest.json. No journal quartile or acceptance probability is asserted.')
addendum(L/'RELEASE_REPORT.md','## TMLR addition — 2026-11-13','Added [26_TMLR/main.pdf](26_TMLR/main.pdf) and [main.tex](26_TMLR/main.tex): 40 pages / 19,192 extracted words, official TMLR style commit7bf90efe. Nine-page core; impact/transparency/references throughp12; complete technical appendix pp13–40. All40pages reviewed, 0overfull/undefined/Type3. Eight canonical figures, 28 master references, 60 canonical headings retained; all prior21mainPDF hashes unchanged. Library now22mainPDFs /20scientific versions plus two format/citation alternatives. Human author and originality review remains; no submission performed. Access/policy-based blocks elsewhere unchanged.')
addendum(L/'SUBMISSION_ROADMAP.md','## TMLR addition — 2026-11-13','TMLR is a possible author-review destination for the bounded empirical behavior/failure-analysis contribution. It has no author fees or fixed page cap and evaluates evidence and reader interest; this does not establish acceptance prospects. The full supported result sequence is in26_TMLR/main.pdf. Its stricter originality rule disallows expanded archival conference papers and overlapping archival publication/acceptance/parallel submission; authors must verify actual status before selecting it. Preprints and explicitly non-archival work can overlap under the current policy. Review its venue-specific checklist before choosing one destination.')
addendum(L/'CHECKPOINT.md','## User-requested TMLR completed — 2026-11-13','Actual40-page manuscript/PDF and complete supporting appendix now in26_TMLR. Official template provenance, requirements, coverage, buildstatus and human-action checklist recorded; all scientific support preserved and prior21mainPDFs unchanged. No inference. This request is implemented; next TMLR step is human scientific/citation/originality and submission-package review. Earlier Access/policy blocks remain unchanged; do not confuse them with a TMLR build failure.')
addendum(L/'PROGRESS_LOG.md','## TMLR completed — 2026-11-13','Verified canonical current TMLR rules and official JmlrOrg kit. Adapted full evidence into a40-page empirical failure-analysis manuscript with explicit questions, fair negative/positive findings and full technical appendix. Added broader impact/transparency; repaired one footer overlap using a page break. All40pages visually checked; zero overfull/undefined/Type3, 8canonicalfigures/28references/60headings checked. Retried a local OpenBLAS allocation failure with one analysis thread; audit completed without experimental inference or changing user processes. Prior21mainPDFs/frozen evidence unchanged. No submission or readiness claim; actual authors must complete review/originality/declarations/anonymity/portal gates.')
addendum(L.parent/'DECISIONS.md','### 2026-11-13 — User-requested TMLR adaptation','Created26_TMLR/main.tex and40-page compiled PDF with a nine-page core, current official unmodified TMLR kit7bf90efe, all28references and8canonicalfigures, full technical appendix and no changed experimental outcomes. Framing targets supported insights into candidate generation/selective delivery; failed planner criterion, secondary null, oracle leakage, stronger baselines, scorer sensitivity and qualified memory evidence remain explicit. All60canonicalheadings mapped, all40pages visually checked, one footer overlap fixed by local page break. Frozen evidence and all21prior mainPDFs unchanged. Current canonicaljmlr.orgrules allow assistive LLM tools with human responsibility and no fixed page cap; TMLR strict archival-overlap policy requires actual-author verification. Not submitted or submission-ready. Added requirements, reproducible build, scientific coverage and human-action checklist; library22mainPDFs/20scientificversions. No research rerun.')
print(json.dumps({k:qa[k] for k in ['pages','words','sha256','core_scientific_endpoint','overfull_boxes','submission_ready']},indent=2))
