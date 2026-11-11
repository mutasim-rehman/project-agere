# Phase 3 submission: Project Agere

> **Post-submission preservation update, 11 November 2026:** the [Ubuntu 16 GB replication](research/tier16_v2/UBUNTU_COMPLETION.md) completed evaluation and replay. Its [SSD-free dashboard handoff](dashboard_handoff/README.md) is updated, with filesystem/export limitations recorded. The submitted paper, its figures, paper data and PDFs have not been revised.

Submission revision: 2 November 2026. Experiments completed through 30 October 2026.

## Submission contents

- **Main report:** [research paper PDF](output/pdf/RESEARCH_PAPER.pdf), with [editable manuscript](RESEARCH_PAPER.md).
- **Implementation:** `scripts/lab_tiers.py`, `scripts/tier8_v2_financial_pipeline.py`, `scripts/tier8_v2_finqa.py`, `scripts/evidence_atoms.py` and `scripts/evidence_calculator.py`. Frozen run snapshots are preserved in the evidence archives.
- **Configuration:** `configs/lab_tiers/{protocol,freeze,runtime_pin}.json`; model source revisions, hashes, dataset IDs and budgets are pinned there.
- **Results:** `research/tier16_v2/data/` (960 outputs, 160 unique questions); `research/le16_v2/data/` (separate historical regimes); `research/paper/data/` (supplemental analyses and gate ablation).
- **Figures:** `figures/tier16_v2/`, `figures/tier8/`, `figures/paper/`; 20 figures appear in the manuscript.
- **Evidence:** `dashboard_handoff/evidence/`, `source_inventory.json`, `export_summary.json` and `restore_evidence.py`; see [restoration instructions](dashboard_handoff/README.md).
- **Supporting reports:** [documentation index](RESEARCH_DOCUMENTATION_INDEX.md).

Use this entry point for the final submission. `PHASE_2_LAB_RUN.md`, `PHASE_3_LAB_RUN.md`, `DEVELOPMENT_START.md` and `ROADMAP.md` describe historical engineering stages; their phase numbers are internal development stages, not a statement that the academic Phase 3 evaluation remains unimplemented.

## Where each requirement is addressed

1. **Implementation and changes:** manuscript Sections 5.1-5.5 and 5.11; code/configuration above. A dated record of previous-class feedback was not available. Section 5.11 explicitly records that limitation rather than attributing development changes to an instructor. Actual class comments must be reconciled before claiming feedback incorporation.
2. **Dataset and preprocessing:** Sections 5.6 and 5.12; exact selections and hashes in the protocol/archived selection. No fitting is performed on the 16 GB evaluation cohort; demonstrations are training-source examples.
3. **Baselines and metrics:** Sections 5.7-5.9 and 6.1-6.5; quantized SAS is the principal baseline. Denominators include withholding, and both numerical scoring conventions are retained.
4. **Graphical results:** Figures 1-20 in the main report; PNG/SVG sources in the figure directories.
5. **Existing research comparison:** Sections 3 and 6.14; corrected author-reported FinQANet and published FinMAN results, with explicit dataset, scoring and resource mismatches. These are reference comparisons, not reproduced external baselines.
6. **Ablations:** Section 6.7; direct-control bundle, repair policy, and post-hoc final-review-gate removal on fixed candidates. Analysis and demonstrations have not been isolated from one another in fresh inference experiments.
7. **Analysis and discussion:** Sections 8-10 and conclusion; research-gap status, negative findings, threats to validity and future work.

## Verify and re-analyse without model inference

Python 3.12 is recommended. From the repository root, verify the portable evidence using the standard library:

```bash
python dashboard_handoff/restore_evidence.py
```

For numerical analysis, install the report dependencies into a virtual environment, or use an environment already providing them:

```bash
python -m pip install -r requirements-reporting.txt
python -m unittest discover -s tests -p test_reporting_statistics.py
python -m unittest discover -s tests -p test_paper_statistical_tests.py
python scripts/reporting/paper_statistical_tests.py
python scripts/reporting/gate_ablation.py
```

The gate ablation uses only the standard library. The statistical battery requires NumPy. The reporting requirements are separate from the frozen model-inference runtime and must not replace its dependency pins.

To restore all archived relative paths into a new directory:

```bash
python dashboard_handoff/restore_evidence.py --extract restored_agere
```

Set `AGERE_SSD_ROOT` to the restored root (or original AGERE SSD root) for analyses that need raw records. The following rebuilds supplementary paper figures and their JSON without model calls:

```bash
# Linux/macOS; PowerShell: $env:AGERE_SSD_ROOT = (Resolve-Path restored_agere).Path
export AGERE_SSD_ROOT="$PWD/restored_agere"
python scripts/reporting/paper_figures.py
python scripts/reporting/analyze_completed_tiers.py --ssd "$AGERE_SSD_ROOT"
```

These commands write derived outputs. The archives preserve source files and their checksums; model tensors, adapters, tokenizer assets and runtime installations are excluded. Some historical tools additionally require these omitted assets for vocabulary-level replay, as distinct from table-based re-analysis.

## Fresh inference reproduction

The completed run used Linux x86_64, Python 3.12, pinned `llama-cpp-python` 0.3.16, CPU inference with eight threads, greedy decoding, seed 42, 4,096 context, F16 KV cache and `use_mmap=False`. Each case has a common 2,048 generated-token ceiling; the nominal 16 GB deployment has an 11.5 decimal GB sampled process-tree RSS ceiling including the controller. See the [executed protocol](research/tier16_v2/PROTOCOL_SNAPSHOT.md) and [resource chronology](research/tier16_v2/RESOURCE_AUDIT.md).

Full inference additionally requires the original pinned model weights and offline runtime bundle, a suitable host, and the frozen code snapshot. Restore/provision these inputs using `LAB_TIERS_OFFLINE.md` and the runtime/model pins. On a provisioned Linux host, use a new run ID so the historical results stay intact:

```bash
export AGERE_SSD_ROOT=/path/to/AGERE
bash scripts/lab_tiers.sh preflight --tiers 16 --run-id phase3-independent-16
bash scripts/lab_tiers.sh run --tiers 16 --run-id phase3-independent-16
```

The portable archives alone cannot reproduce model inference. A clean clone does support the no-inference verification and table analyses above.

## Rebuild the main PDF

The committed PDF is ready to read. The renderer uses Edge/Chrome/Chromium, Playwright, and network access to pinned marked/KaTeX CDN versions. With a Node environment containing Playwright:

```bash
python scripts/reporting/render_paper_pdf.py --html-only
node scripts/reporting/render_paper_verified.cjs /absolute/path/to/node_modules /absolute/path/to/browser
```

Inspect the rebuilt PDF visually as well as checking `output/paper/render_audit.json`. The HTML uses repository-relative paths, so keep it in `output/paper/` with the figure directories available.

## Interpretation and remaining limitations

The result is a negative/trade-off finding, not a new inference algorithm or a claim that MAS must outperform SAS. Only evidence through 16 GB is complete; 32 GB is unexecuted. The primary cohort is selected from FinQA's development source and uses custom numerical scoring, not official benchmark program equivalence. Two swap failures remain in the record; audited continuation completed accuracy evaluation but did not establish an uninterrupted no-swap deployment pass. New component analysis is explicitly post hoc. No new model runs were made for this submission revision.

Repository: https://github.com/mutasim-rehman/project-agere. The repository is the submission access point; no archival DOI is claimed. Existing third-party attribution and usage terms continue to apply.
