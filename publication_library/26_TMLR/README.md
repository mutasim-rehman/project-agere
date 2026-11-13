# Transactions on Machine Learning Research adaptation

Title: **Evidence, Candidate Generation and Selective Delivery in Memory-Constrained Financial Reasoning**.

Actual manuscript: [main.tex](main.tex); compiled [main.pdf](main.pdf), **40 pages / 19,192 extracted words**. The core scientific argument ends on page 9; impact/transparency and references occupy pages 9–12, with the complete technical appendix on pages 13–40. Word counts include PDF headers, tables and references. This is a substantive empirical/failure-analysis adaptation, not a new experiment or an acceptance claim.

The introduction states three questions about useful correct delivery, candidate construction with available evidence and transfer from oracle constraints to deployable planning. The abstract and conclusion explicitly retain the failed planner rule, wrong deliveries, reduced correct candidates, secondary null, stronger baselines and confounded deployment recipes. All extended methods, historical controls, paired statistics, conditional mathematics and worked failures are embedded after the references. See [COVERAGE_AUDIT.md](COVERAGE_AUDIT.md).

The unmodified official JmlrOrg style, bibliography style and bundled fancyhdr are included with source provenance and license under `template/`. No fixed page limit was assumed; supporting detail is separated from the nine-page core. A local header honestly says author-review draft/not submitted instead of the template's default under-review claim.

Build with PDFLaTeX/BibTeX on PATH: `powershell -ExecutionPolicy Bypass -File publication_library/26_TMLR/build.ps1`. It builds from its own folder and stops on failure. On this host the TeX binaries are `D:\project-agere\.local\texlive\TinyTeX\bin\windows`. The source-production script is `../shared/production/produce_tmlr.py`; do not run new inference. After editing, rerun compilation, coverage checks and visual review before refreshing `build_status.json`.

**HUMAN-REVIEW-REQUIRED; not submitted or submission-ready.** See [VENUE_REQUIREMENTS.md](VENUE_REQUIREMENTS.md) and [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md). No publication, acceptance, archival submission or authorship status is inferred from the existence of other library drafts. Their overlap makes choosing one archival destination essential.
