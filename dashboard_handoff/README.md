# Dashboard developer handoff

Prepared 30 October 2026 from `H:\AGERE`. This is a portable research-data handoff for the partner building the web dashboard. No SSD, model download, inference server, Python packages or API keys are needed to use the dashboard inputs. The dashboard itself has not been implemented.

## Start here

1. Read [the research documentation index](../RESEARCH_DOCUMENTATION_INDEX.md), [16 GB data dictionary](../research/tier16_v2/DATA_DICTIONARY.md), [cross-tier comparability](../research/le16_v2/COMPARABILITY_MATRIX.md), and [claim ledger](../research/le16_v2/HYPOTHESES_AND_CLAIMS.md).
2. Load [data/index.json](data/index.json). It lists every copied derived input, its repository source, checksum, columns and row count where applicable. CSV inputs also have adjacent JSON arrays with native numbers, booleans and `null` for empty CSV cells. Identifiers remain strings; integers beyond JavaScript's safe range remain strings.
3. Use `data/tier16_v2/case_outcomes.json` for the completed 16 GB case explorer and `data/le16_v2/tier8_case_outcomes.json` for 8 GB results. Use the accompanying statistical JSON for aggregate estimates, uncertainty and assumptions rather than reconstructing inferential statistics in the frontend.
4. Use [source_inventory.json](source_inventory.json) to find supporting SSD files by original relative path. Each entry identifies the archive and member, original size and SHA256. Exact duplicate content is stored once, with all original paths retained in the inventory.

Example frontend loading, when the handoff directory is exposed as a static directory:

```js
const catalog = await fetch('/dashboard_handoff/data/index.json').then(r => r.json());
const input = catalog.find(x => x.id === 'tier16_v2/case_outcomes');
const cases = await fetch('/dashboard_handoff/' + input.browser_json).then(r => r.json());
```

Copy this directory into the chosen framework's static/public directory or configure a static mount. The JSON files work with any web stack. Use an HTTP development server; browser `file://` fetches are commonly restricted. Avoid shipping the evidence archives as part of the deployed frontend: keep them as developer/research inputs and publish only the tables required by the interface.

## Data available for dashboard features

- **Experiment comparison and scorecards:** `data/tier16_v2/statistical_analysis.json`, `paired_effects.json`, `report_outcomes.json`, and `data/le16_v2/cross_tier_analysis.json`. The 16 GB table contains 960 model/profile outputs on 160 unique questions. The 8 GB table contains 768 outputs on 101 unique questions; these are repeated conditions, not 768 independent questions.
- **Case and failure explorer:** the two case-outcome tables, `metric_disagreements.json`, and archived `cases.jsonl` files for predictions, calculation programs, source references, retrieval choices, verifier decisions and repair traces. Case IDs recur across jobs; use `(tier, job, case_id)` for 16 GB rows and inspect the 8 GB column catalog for its condition key. Do not join on question ID alone.
- **Cost and pipeline charts:** `stage_metrics.json` supplies calls, tokens and inference seconds by stage and role. Archived stage traces and manifests provide finer detail. Latency fields are inference measurements, not dashboard HTTP response time or dollar cost.
- **Resource timeline:** `resource_events.json`, archived `memory.jsonl`, job summaries, cap files, continuation evidence and retained failure notes. The main 16 GB authority is `runs/lab_tiers_v1/lab-16-115gb-recovery-02/`; read its `RESOURCE_FAILURE_RETAINED.md` and attempt history alongside completed summaries.
- **Condition and provenance browser:** `data/le16_v2/tier8_condition_inventory.json`, `tier8_evidence_catalog.json`, `historical_diagnostics.json`, manifests, audit outputs and [export summary](export_summary.json). The historical evidence catalog describes 197 artifacts; the SSD inventory is broader and also contains smoke tests, diagnostics, failed attempts and training runs. File count is not experiment count.
- **Hypothesis and statistical views:** paired effects and full analysis JSON; `data/paper/` contains the supplementary paper analysis and hypothesis-test exports as a snapshot of the paper work present locally at export time. These supplemental tests are post hoc. The original paper work in the repository was already uncommitted; this handoff does not change those source files.
- **Question, evidence and dataset views:** archives retain synthetic KYC/credit splits, policy SOP data, FinQA selections and source report material, FRAMES slices, MortarBench questions/documents, training examples, selection manifests and parity audits. For final FinQA inputs start with `datasets/lab_tiers/finance_reports_v1/{public.jsonl,scoring-source.json,selection.json,demonstrations.json}`. `scoring-source.json` and gold-answer fields are evaluation references; keep them separate from model-visible input when illustrating the protocol. Dataset source attribution and upstream usage terms continue to apply; copying an artifact does not create a new license.
- **Existing figures and explanatory text:** [16 GB PNG/SVG figures](../figures/tier16_v2), [16 GB report](../TIER_16_RESEARCH_REPORT.md), [integrated report](../TIER_LE_16_RESEARCH_REPORT.md), and methodology documents in the repository. The archived reporting bundle also preserves the completed documentation package from the SSD.

## Interpretation rules to carry into the interface

- Keep the 8 GB synthetic, adapted 8 GB FinQA, and pretrained 16 GB FinQA regimes separate. Task cohorts, model adaptation and serving recipes differ. The study does not establish a causal RAM-scaling curve, universal MAS superiority or a 32 GB result.
- Show reported-answer and raw-execution correctness together. For delivered correctness use the outcome labels, or `delivered && reported_correct` / `delivered && raw_correct`; a candidate correctness flag alone can count a withheld answer incorrectly.
- Show correct, wrong and withheld counts together and label denominators. Do not present withholding as success, or execution validity as numerical correctness.
- Preserve report/company clustering for uncertainty. Do not treat repeated questions, companies, profiles or stage calls as independent samples. Use the supplied intervals and their documented assumptions.
- Historical swap failures remain resource-invalid even though later jobs completed. Completion is not proof of an uninterrupted no-swap deployment. Do not label every archived experiment as a valid final result.
- GB means decimal `10^9` bytes; GiB means `2^30`. `completed_time` in the 16 GB case table is Unix seconds in UTC. A zero correct count makes seconds-per-correct undefined; show missing/undefined, not zero.
- Input JSON exports preserve the research tables; they do not introduce new scores or silently reconcile metric disagreements. The CSVs and source hashes remain available for audit.

## SSD evidence coverage and restoration

Research data, text logs, code snapshots, reports, manifests, small model configuration metadata, numerical arrays and original result/documentation archives are preserved from `datasets`, `phase2`, `runs`, and useful `weights` metadata. See [export_summary.json](export_summary.json) for exact counts and sizes and [excluded_files.json](excluded_files.json) for individually excluded files in these roots. Environment installations (`.venv`), runtime builds (`runtime`) and scratch (`tmp`) are excluded at the root. Model tensors, adapters, incomplete downloads, tokenizer assets, cache files and locks are unnecessary for dashboard development and are excluded. Their exclusion does not remove reported results or recorded memory/token measurements.

Archives use standard ZIP compression and are divided into manageable Git files. One unusually large source JSON may occupy its own archive. Every unique archived member was read back and SHA256 checked. Recognizable credential token/private-key signatures were checked in source files; this is not a claim that benchmark text was anonymized or that all possible secret formats were detected. Nested historical archives are preserved as original artifacts.

With Python 3 installed, from the repository root:

```powershell
py dashboard_handoff/restore_evidence.py
py dashboard_handoff/restore_evidence.py --extract restored_agere
```

The first command verifies every archived file and checksum. The second reconstructs every original relative path, including duplicates. The restore tool refuses to replace an existing file with different content. On macOS/Linux use `python3` in place of `py`. Simply unzipping every archive recovers the unique stored files; use the restore tool to also recreate duplicate paths.

The historical scripts/manifests may contain original absolute SSD or Linux paths. Those are provenance, not a requirement for the dashboard. Use `data/` directly, or pass the restored root to a research script that supports an explicit SSD-root option. Rebuilding model inference would still require the omitted weights and runtime.

To create a fresh export with the SSD attached, choose a new output directory:

```powershell
py scripts/reporting/export_dashboard_handoff.py --ssd H:/AGERE --output dashboard_handoff_new
```
