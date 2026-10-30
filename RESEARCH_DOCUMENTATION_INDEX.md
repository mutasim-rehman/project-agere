# Completed research documentation: nominal tiers up to 16 GB

Prepared 30 October 2026. The 16 GB accuracy audit, all six evaluation jobs and result export are complete. Historical swap failures remain recorded; the recovered study is not an uninterrupted no-swap deployment pass. The 32 GB tier has not been evaluated.

## Main reports

| Purpose | Editable report | Statistical PDF |
| --- | --- | --- |
| 16 GB empirical study | [16 GB research report](TIER_16_RESEARCH_REPORT.md) | [16 GB v2 statistical evaluation](output/pdf/TIER_16_V2_STATISTICAL_EVALUATION_REPORT.pdf) |
| Integrated pre-paper dossier | [Research at or below 16 GB](TIER_LE_16_RESEARCH_REPORT.md) | [Advanced statistical evaluation and framework](output/pdf/TIER_LE_16_ADVANCED_STATISTICAL_EVALUATION_REPORT.pdf) |

The statistical reports also have full editable Markdown sources: [16 GB](TIER_16_V2_STATISTICAL_EVALUATION_REPORT.md) and [integrated](TIER_LE_16_ADVANCED_STATISTICAL_EVALUATION_REPORT.md).

## Data analysis and supporting documentation

- [16 GB analysis package](research/tier16_v2/README.md): complete results, frozen protocol snapshot, methods, failure analysis, resource chronology, data dictionary, supervisor update and reproduction commands.
- [Integrated analysis package](research/le16_v2/README.md): cross-tier comparability, hypothesis/claim ledger, eight conditional mathematical propositions and publication-readiness assessment.
- [16 GB derived data](research/tier16_v2/data): 960 case-output rows on 160 unique questions, report-level totals, paired contrasts, stage costs, resource events and scoring disagreements.
- [8 GB and cross-tier derived data](research/le16_v2/data): 768 natural case-output rows on 101 unique questions, 15-condition inventory, supporting diagnostic summaries and 197-file historical evidence catalog.
- [Graphs](figures/tier16_v2): 12 high-resolution PNGs plus editable SVG versions. The PDFs use vector graphics.
- [Evidence and validation](research/tier16_v2/evidence): original audited summary, input checksums and package checks.
- [Reproduction scripts](scripts/reporting) and [known-value statistical tests](tests/test_reporting_statistics.py).

## How to interpret the package

Keep reported-answer and raw-execution metrics together. Keep wrong delivery, correct delivery and withholding together. The three core evidence regimes differ in task/cohort, model adaptation and precision/serving recipe; do not pool them into a causal RAM-scaling claim. Supplemental tests are post hoc. Mathematical bounds are conditional and are not a proof of universal architecture superiority or a new algorithm.

The original [8 GB empirical report](TIER_8_RESEARCH_REPORT.md) and [8 GB statistical PDF](TIER_8_V2_STATISTICAL_EVALUATION_REPORT.pdf) are preserved as historical references. The new dossier qualifies stronger earlier claims and incorporates later completed results.

Raw authority: `AGERE/runs/lab_tiers_v1/lab-16-115gb-recovery-02/`, with its original results archive under `AGERE/runs/lab_tiers_v1/exports/`. Model weights, raw prompts/responses and full memory traces remain on SSD.

A portable documentation/data/figure/source bundle is stored at `AGERE/runs/reporting/tier16-le16-20261030/AGERE_LE16_RESEARCH_DOCUMENTATION_2026-10-30.zip`, with a SHA256 sidecar. It excludes model weights, runtimes and credentials. Original SSD inputs are still required to rebuild the raw-response audit; derived tables can be analysed separately.
