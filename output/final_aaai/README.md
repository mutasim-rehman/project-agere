# Final research manuscript

This is a new evidence-audited paper, not a revision of the historical formatting conversion in `output/aaai/`. Original experimental records, `DECISIONS.md`, previous papers and scores are unchanged. No new model inference was performed.

## Deliverables

- `main.pdf` / `main.tex`: anonymous AAAI-style main paper, including references.
- `supplement.pdf` / `supplement.tex`: separate readable one-column technical supplement, including the negative development sequence, full exported historical condition census, statistical definitions and reproduction details.
- `references.bib`: 17 primary-source-verified references; `citation_audit.json` and `LITERATURE_AUDIT.md` record provenance and the limits of comparisons.
- `figures/`: four vector figures generated from checked experimental data. Correct/wrong/withheld, candidate/delivery, uncertainty, latency and memory are all represented.
- `AGERE_FINAL_SOURCE.zip`: self-contained LaTeX compilation sources, figures, PDFs, bibliography, analysis exports and audit documentation. It does **not** contain model weights or the repository's full evidence ZIPs. Run raw-data analysis from the full repository checkout.
- `CLAIM_EVIDENCE.md`, `raw_score_verification.json`, `verified_tier16.json`, `verified_planner.json`: traceability and recomputation.
- `artifact_inventory.json`, `all_result_summaries.json`: hashes and retained result census, including negative/incomplete history. An inventory is not independent expert adjudication of every record.
- `reproducibility/`: model/runtime/training identities, representative recorded Ubuntu prompts and Windows prompt/template source snapshots. Windows rendered prompts are reconstructible from code/packets rather than all being present in the ledgers.

Stable final PDF copies are also written to `output/pdf/AGERE_FINAL_AAAI.pdf` and `output/pdf/AGERE_FINAL_SUPPLEMENT.pdf`.

## Reproduce analysis without inference

Use the repository Python environment, with the additional versions in `requirements-paper.txt`. The analysis imports existing repository evaluation helpers and therefore also needs the repository's normal dependencies. The vendored FinQA/TAT-QA data and official evaluator bytes are checked against recorded experiment hashes before raw-score verification. Upstream sources: [FinQA](https://github.com/czyssrs/FinQA), [TAT-QA](https://github.com/NExTplusplus/TAT-QA/tree/870accc41953dcde885aabeb963d94aabdc0fbc3). Their upstream licenses/provenance apply; these files are not newly authored paper code.

```sh
python dashboard_handoff/restore_evidence.py --extract /path/to/restored_evidence
python scripts/reporting/build_final_paper.py --evidence /path/to/restored_evidence
python scripts/reporting/verify_final_scores.py --evidence /path/to/restored_evidence
```

The first command verifies 20 archives and 2,930 mapped source files. The paper audit verifies all six 160-case Ubuntu jobs, 1,920 initial/final program executions/scores, 668,817 memory samples, primary and secondary planner outcomes, 14 FinQA paired ledgers, seven TAT-QA prediction ledgers and the exact FinQA 96-case format summary. Other historical studies retain their archived audits; this is not a claim that every historical neural/training trajectory has been regenerated.

## Compile

Use **PDFLaTeX**, not XeLaTeX/Tectonic, because the 2027 style enforces the PDFTeX engine. A current TeX Live with the fonts/packages declared in the sources is sufficient.

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Repeat for `supplement.tex`. From a repository checkout, `python scripts/reporting/compile_final_paper.py --tex-bin /path/to/tex/bin` compiles both, rejects unresolved references/overfull boxes/Type 3 fonts, checks US Letter and main-paper page limits, copies the final PDFs, and packages the sources. Compilation checks do not replace the recorded visual inspection.

## AAAI format status and final author checks

The intended format is AAAI-27, consistent with the repository's 2027 materials. The [official main-track call](https://aaai.org/conference/aaai/aaai-27/main-technical-track-call/) specifies at most seven pages of main content and nine pages total, with pages beyond seven reserved for references. The current paper satisfies these length limits; the technical supplement is separate. No margins, font sizes or style files were modified to force a fit.

**Unresolved official-template authentication:** the [official kit page](https://aaai.org/authorkit27/) and official ZIP URL returned HTTP 403, including direct download attempts. Unmodified `aaai2027.sty` and `.bst` were retrieved from the same retained [author-kit mirror](https://github.com/tabbycat7/aaai_2027_latex) as the historical conversion, alongside its instructions. `template_provenance.json` records URLs/hashes. We cannot truthfully certify byte identity against the inaccessible official download. Replace/check these files against the official kit when accessible and recompile before an actual submission. Do not call this an authenticated official-kit validation.

The manuscript is anonymous; no author names, affiliations, grants, acceptance status or signatures were invented. `SUBMISSION_CHECKS.md` identifies remaining author-only/venue-specific declarations. The evidence/source package contains original provenance paths and is **not** certified as an anonymized code submission. The paper can be circulated for scientific review now; portal eligibility, intended conference year, official checklist and final authorship remain submission decisions. Preparing AAAI-27 style does not imply its main-track deadline is still open.

## Scientific limits deliberately retained

The planner fails the prespecified no-wrong-increase requirement; its positive sparse bootstrap interval is shown alongside exact p=0.125. Oracle constraints disclose answer-key access. The stronger direct baseline, failed replications, raw/reported metric disagreements, wrong candidate acceptance and loss of correct candidates remain visible. Windows physical 8 GB/no-paging operation is unverified. Ubuntu is a checkpointed swap-disabled repeat with missing original export/log artifacts, not an uninterrupted deployment certification. The secondary 7B comparison is incomplete. No 32 GB results or general architecture/precision causal conclusions are claimed.
