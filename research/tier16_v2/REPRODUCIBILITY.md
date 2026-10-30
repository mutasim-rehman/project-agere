# Reproduce analysis and documents

No neural inference/training is performed. Keep the original SSD connected; source hashes and the original result archive are verified. The code reads existing public/scoring artifacts and preserves original outputs.

```bash
cd /home/mutasim/Desktop/project-agere
export AGERE_SSD_ROOT="/run/media/mutasim/Data/AGERE"
export AGERE_REPORT_PYTHON="/home/mutasim/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
"$AGERE_REPORT_PYTHON" scripts/reporting/analyze_completed_tiers.py --ssd "$AGERE_SSD_ROOT"
"$AGERE_REPORT_PYTHON" scripts/reporting/build_research_documents.py
"$AGERE_REPORT_PYTHON" scripts/reporting/render_statistical_reports.py
```

The bundled runtime supplies NumPy and ReportLab; no new installation was required. Plotting uses ReportLab graphics, exporting SVG and publication-ready PNG. PDF pages are rendered with Poppler for visual verification. The two final PDFs are under `output/pdf/`; editable Markdown and machine-readable CSV/JSON stay separate.

Parameters: bootstrap10000 draws; supplemental sign flips up to 65536; seed42. Primary family has 4 correct/wrong contrasts. The source audit uses a different random generator/quantile convention; it is retained unchanged. Supplemental plan is post hoc. CIs are not guaranteed under arbitrary dependent or nonrepresentative reports.

Source archive: `/run/media/mutasim/Data/AGERE/runs/lab_tiers_v1/exports/lab-16-115gb-recovery-02-results.tar.gz`. Expected SHA256: `82391e38eb522ec9c0f3721ba39d9543999011bfa8c8c0f4e019a6ba1152f7b8`. Full input hashes: `evidence/input_provenance.json`. Raw weights are not copied into Git or the documentation bundle; model hashes remain pinned in the evaluation manifest. No tokens or credentials enter outputs.
