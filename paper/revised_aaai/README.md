# Coverage-restored manuscript release

This separate revision preserves both the original 37-page manuscript and the prior 7-page main/10-page supplement. Their byte fingerprints are in `../preserved_versions.json`; the complete comparison is `../COVERAGE_AUDIT.md`.

## Read

- `main.pdf`: concise AAAI-27 submission-style main paper. Its content ends on page seven; the final page contains references only.
- `supplement.pdf`: comprehensive technical supplement with navigation, original hypotheses, historical controls, complete paired statistics, mathematical assumptions and proofs, failure examples, resource reconciliation and reproducibility.
- `../COVERAGE_AUDIT.md`: classifications for every old section/subsection, all 38 tables and 20 figures, and every P1–P10/J1–J12 item. It distinguishes pre-restoration coverage from the final disposition and explains exclusions.

The scientific conclusion is unchanged: the tested F16 team loses correct delivery; the evidence-only planner fails its practical criterion; oracle constraints are diagnostic answer-key interventions. Additional supporting science is restored without new inference or changed experimental outputs. Corrected theoretical/statistical interpretations are identified explicitly.

## Evidence and verification

- `coverage_evidence_checks.json`: raw input fingerprints and reconciliation results.
- `raw_score_verification.json`: fresh execution/scoring of 1,920 Ubuntu initial/final programs and Windows FinQA/TAT-QA checks.
- `restored_test_battery.json`: all 126 historical endpoints and transition/test fields. Undefined statistics use JSON `null`, not a fabricated value.
- `restored_primary_sensitivity.json`: report/company bootstrap, weighting/influence and sign-flip analyses.
- `restored_resources.json`: both historical and Ubuntu durations, stage costs, per-case latency lists and sampled peaks; the runs are not pooled.
- `restored_synthetic.json`: 350 synthetic answers independently rescored from source documents and deterministic tools, with honest denominators.
- `worked_example_traces.json`: original saved records for the worked examples, including both run versions.
- `verified_tier16.json`, `verified_planner.json`, `audit_summary.json`: fresh core analysis, including all 668,817 saved memory samples.
- `citation_coverage.json`: final bibliography key/source coverage and the corrected Qwen Team authorship. Existing primary-source audit records remain preserved under `output/final_aaai/` in the full repository.
- `compilation_checks.json`, `visual_review.json`, `quality_review/`: final rendering checks and contact sheets.

Original raw model responses and training histories are not newly generated. Statistical tests are conditional on their stated sampling assumptions; numerical reconciliation does not validate every financial label or prove external generality.

## Reproduce from the full repository

Use the existing repository dependencies plus `output/final_aaai/requirements-paper.txt`. Scripts import existing evaluation/statistical modules, so the portable LaTeX package is not a substitute for a full repository checkout when recomputing analysis.

```sh
python dashboard_handoff/restore_evidence.py --extract PATH
python scripts/reporting/reverify_coverage.py --evidence PATH
python scripts/reporting/coverage_evidence.py --evidence PATH
python -m unittest tests.test_reporting_statistics tests.test_paper_statistical_tests
python scripts/reporting/compile_coverage_revision.py --tex-bin TEX_BIN
python scripts/reporting/coverage_audit_report.py
```

The two PDF sources compile with PDFLaTeX/BibTeX; `main.tex` uses unchanged AAAI-2027 style files. Compilation requires current TeX packages listed in the preambles. Figure PDFs are vector graphics generated from the checked ledgers. Citation metadata refresh is separate (`coverage_sources.py`) and requires network access; it is not needed for offline compilation.

## Venue and release qualifications

The official main-track call/instructions permit seven pages of non-reference content and nine total; critical evidence must be in the main paper because reviewers need not read the supplement. Those public pages state no numeric technical-supplement page cap. The current extended supplement is an archival technical document; portal/file-size and intended-year requirements still need checking before upload. See `../VENUE_REQUIREMENTS.md` for verified official URLs and dates.

The official author-kit download returned HTTP 403 in the prior preparation; these unchanged mirror style files have recorded provenance but remain unauthenticated against the official ZIP. Authorship, deadline eligibility and the separate reproducibility checklist need author/venue confirmation. No actual conference submission has been made.

The main manuscript is anonymous. This repository/source package retains original provenance paths and is not certified as an anonymized code submission. Main and supplementary PDFs are independently readable; full reproduction still depends on the preserved experimental evidence and repository code.
