# TASK: BUILD A COMPLETE MULTI-VENUE RESEARCH PUBLICATION LIBRARY

The research is finished. I now want you to build a **comprehensive collection of publication-specific manuscripts**, so that I can choose a journal, conference, or workshop later without having to rewrite or reformat the entire research paper.

This is NOT a request to merely change document classes or rename PDFs.

I want genuinely venue-adapted academic manuscripts, each with its own scientific presentation, appropriate depth, section structure, bibliography formatting, figures, supplementary materials, and official publisher templates.

Work autonomously. Research the publication requirements online, implement them, compile the manuscripts, and organize everything into one directory.

## 1. Establish the authoritative research source

Start by examining the entire repository, particularly:

- The original 37-page research manuscript.
- The newer AAAI manuscript and supplement.
- The coverage audit and DECISIONS.md.
- All experiment logs, results, evaluation files, statistics, and figures.
- The existing bibliography and reproducibility documents.

Create a canonical scientific content inventory containing the research questions, experimental designs, baselines, hypotheses, numerical results, uncertainty estimates, interpretations, limitations, references, and supplementary analyses.

Treat experimental artifacts as authoritative over manuscript prose.

Never change numerical findings between venue versions. Never invent results, citations, statistical significance, experiments, or theoretical justification.

The research concerns smaller full-precision multi-agent LLM systems compared against larger quantized models under strict RAM and generation-token budgets, evaluated on financial-document reasoning, with particular emphasis on failure analysis, verification, reliability, abstention, and planning interventions.

Preserve both successful and unsuccessful findings.

## 2. Research target publication venues

Perform an up-to-date online investigation of suitable publication venues. Do not assume IEEE or Springer is itself a single journal or conference.

Start with the following mandatory publication targets:

### A. General scientific manuscripts
1. Comprehensive master research paper, with no arbitrary length restriction.
2. General conference paper, approximately 6–10 pages unless evidence warrants otherwise.
3. General full-length journal paper.
4. Public technical report / preprint, suitable for future arXiv preparation.

### B. Major AI/ML conferences
5. AAAI — latest official author kit.
6. ICLR — latest official author guidelines and LaTeX style.
7. NeurIPS — current official conference template.
8. ICML — official proceedings template.
9. IJCAI — official conference author instructions.

Do not assume the research is competitive for every one of these conferences. Prepare truthful, properly adapted versions and separately evaluate scientific fit and competitiveness.

### C. IEEE
10. Generic IEEE conference manuscript using IEEEtran in conference mode.
11. IEEE Access journal-specific research article.
12. Another real IEEE conference that fits resource-constrained LLM inference, system evaluation, or applied AI, selected after checking its official call for papers.

### D. Springer Nature
13. Springer LNCS/LNAI conference-proceedings version.
14. Springer Nature journal version using the appropriate journal authoring template.
15. A specifically targeted Springer journal, such as SN Computer Science or Discover Artificial Intelligence, subject to verifying its scope, current publication status, submission rules, and research fit.

### E. MDPI and MAKE
16. Machine Learning and Knowledge Extraction (MAKE) — full research article using the official MDPI template and the journal's required reference style.
17. One additional suitable MDPI journal, selected only after checking scope, quartile, indexing, publication fees, and relevance.

### F. Workshops
18. General AI/ML workshop paper, concise and focused.
19. ICLR-style workshop contribution, using a real workshop's instructions if a relevant one is available.
20. A short extended-abstract / position-paper version where appropriate.

### G. Alternative publication venues
Research credible, less-selective journals and conferences, including options outside Q1.

Identify at least:
- 3 reasonable journal alternatives, preferably spanning verified Q2, Q3, or Q4 classifications where available.
- 3 legitimate conference alternatives with attainable submission requirements.
- 2 realistic workshop opportunities.

Only create venue-specific versions for credible, sufficiently relevant outlets with verifiable author instructions.

Do not invent quartiles, acceptance rates, indexing claims, or conferences. Quartiles apply to journal ranking systems and categories, not universally to conferences. Distinguish JCR from SCImago rankings and record their years.

Avoid questionable or predatory venues.

## 3. Verify every venue's actual requirements

Visit OFFICIAL conference, journal, or publisher websites.

For each target, investigate:

1. Publication name, publisher, ISSN/series where applicable.
2. Scope and research-topic suitability.
3. Official template download page and version.
4. Permitted article types.
5. Page limits, word limits, abstract limits.
6. Column format, margins, fonts, section conventions.
7. Bibliography and citation style.
8. Anonymous or non-anonymous submission requirements.
9. Supplementary material and appendix policies.
10. Data/code availability expectations.
11. Ethics, disclosure, and AI-assisted writing policies.
12. Publication charges/APCs and any page fees.
13. Indexing, quartile, and classification where verified.
14. Next relevant submission window or rolling-submission status.
15. Dual-submission and prior-publication restrictions.

For all venue-specific requirements, record the source URL, access date, and applicable conference year or journal guideline version.

Use official downloadable LaTeX templates, class files, bibliography styles, and author kits. Do not simulate official layouts manually.

Important: If a future conference edition has not published its instructions, use the latest available official edition as a clearly labeled provisional template.

If instructions are unavailable or contradictory, mark the version as provisional and document the uncertainty.

Check these starting sources:

- AAAI: https://aaai.org/
- ICLR: https://iclr.cc/
- IEEE conference templates: https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/
- IEEE Access: https://ieeeaccess.ieee.org/authors/preparing-your-article/
- Springer LNCS: https://www.springer.com/gp/computer-science/lncs/forthcoming-proceedings
- Springer Nature journal LaTeX support: https://www.springernature.com/
- MDPI LaTeX: https://www.mdpi.com/authors/latex
- MAKE: https://www.mdpi.com/journal/make

These links are starting points, not substitutes for checking the particular venue's latest official requirements.

## 4. Write truly different versions

The scientific findings must remain identical, but the presentation should be optimized for each readership.

**AAAI:** Emphasize the AI research problem, experimentally supported contribution, comparison fairness, generalizable failure mechanisms, and concise analysis.

**ICLR:** Emphasize research hypotheses, experimental rigor, controlled comparisons, uncertainty, limitations, and broader implications for LLM reasoning and inference efficiency.

**IEEE Conference:** Emphasize system architecture, engineering constraints, reproducible benchmarks, latency, memory, and operational reliability.

**IEEE Access:** Present comprehensive methodology, full results, system design, statistical evaluation, failure taxonomy, limitations, and reproducibility.

**Springer LNCS:** Follow proceedings conventions, with a coherent technical argument and appropriate formal definitions.

**Springer Journal:** Develop the longer scientific analysis, extended experimentation, theoretical discussion where supported, and methodology in substantial detail.

**MAKE:** Produce a comprehensive original research article, retaining meaningful experiments, statistical interpretation, analysis of failure modes, and reproducibility details. Preserve depth rather than compressing everything into a conference-style paper.

**Workshops:** Develop a focused contribution suitable for constructive research discussion, concentrating on the strongest supported finding or unresolved question. Do not exaggerate novelty.

**General Master:** Preserve the complete, nonredundant scientific contribution from the original 37-page manuscript and the final experimental artifacts.

Every version needs its own properly edited abstract, introduction, contribution summary, discussion, and conclusion, appropriate to its audience.

Do not merely copy the exact same text into different templates.

However, do not create artificial differences between versions to make them appear to describe distinct research.

## 5. Respect publication and AI-writing policies

This is critical.

Check the current AI-use policy for every target BEFORE generating or rewriting manuscript text.

For example, AAAI-27 prohibits LLM-generated manuscript text except when it is part of the experimental analysis, while permitting LLM editing or polishing of human-authored text.

For such venues, prepare the correct template, structure, source-content mapping, compliance analysis, and permitted editorial revisions, but do not claim an autonomously generated manuscript is eligible for submission.

Mark versions requiring additional human authorship or rewriting as HUMAN-AUTHORING-REQUIRED.

ICLR requires an AI-use statement. Other journals may require disclosure in acknowledgments or elsewhere. Follow the specific venue's requirements.

Always preserve human author responsibility. Do not invent author names, affiliations, funding information, approvals, conflicts of interest, or contribution statements.

Document exactly how automated assistance was used.

## 6. Supplementary material

Prepare appropriate supplementary material for each version when permitted.

Use the comprehensive original research as the evidence source.

Include scientifically useful extensions such as:

- Additional evaluation tables and uncertainty estimates.
- Failure-case analyses.
- Formal derivations and propositions that are actually supported.
- Experimental configuration and prompts.
- Model precision and inference settings.
- Resource measurements.
- Dataset selection and processing.
- Ablations and historical experiment context.
- Verification and abstention analysis.
- Planner experiment details.
- Reproducibility instructions.

Do not assume every venue accepts a separate supplement, unlimited appendices, or the same file organization.

Check and implement each venue's policy.

Ensure the main manuscripts remain scientifically self-contained.

## 7. Data visualization

Use a shared collection of source-verified, publication-quality figures.

Create consistent, readable graphics using Matplotlib, export in vector PDF format when supported, and preserve the scripts used to generate them.

Choose figures individually for each venue according to the research narrative and page constraints.

Do not make up visualizations or duplicate plots merely to fill pages.

All numerical claims and figure inputs must trace back to real experimental artifacts.

## 8. Create a clean publication library

Place ALL outputs inside one root directory called `publication_library/`.

Use the following structure:

publication_library/
  README.md
  VENUE_MATRIX.md
  SUBMISSION_ROADMAP.md
  CONTENT_COVERAGE.md
  COMPLIANCE_AUDIT.md
  MASTER_REFERENCES.bib

  shared/
    figures/
    figure_generation/
    statistics/
    verified_results/
    source_inventory/

  00_master_research/
  01_general_conference/
  02_general_journal/
  03_preprint_arxiv/
  04_AAAI/
  05_ICLR/
  06_NeurIPS/
  07_ICML/
  08_IJCAI/
  09_IEEE_conference/
  10_IEEE_Access/
  11_IEEE_targeted_conference/
  12_Springer_LNCS/
  13_Springer_journal/
  14_Springer_targeted_journal/
  15_MDPI_MAKE/
  16_MDPI_alternative/
  17_general_workshop/
  18_ICLR_workshop/
  19_short_position_paper/
  20_alternative_journals/
  21_alternative_conferences/
  22_alternative_workshops/

Create relevant venue-specific subdirectories where multiple actual targets are selected.

For EACH manuscript directory, provide:

- `main.tex`
- `main.pdf` if compilation succeeds.
- `references.bib`
- `figures/`
- `supplementary/` if applicable.
- `template/` with legitimately obtained official template assets, subject to redistribution terms.
- `VENUE_REQUIREMENTS.md`
- `MANUSCRIPT_NOTES.md`
- `SUBMISSION_CHECKLIST.md`
- `README.md`

Also prepare a build script or Makefile so every manuscript can be compiled independently.

Use relative paths and do not depend on inaccessible files elsewhere in the repository.

Do not write fabricated PDFs or empty placeholders. Any unfinished or noncompliant version must be clearly flagged.

## 9. Prepare a master venue comparison

Create `VENUE_MATRIX.md` containing a comprehensive table of every target.

Columns should include:

- Venue and publisher
- Journal, conference, workshop, or preprint
- Current classification/ranking, if verified
- Topic fit (high, medium, low)
- Estimated competitiveness based on the actual manuscript, not invented acceptance odds
- Manuscript page/word limit
- Official template version
- Citation format
- Supplement rules
- Publication fees
- Applicable deadlines
- Official source links
- Manuscript folder
- Compilation status
- Policy compliance status
- Human review required
- Last verification date

Also create `SUBMISSION_ROADMAP.md`, ranking targets into:

1. Highly ambitious venues.
2. Realistic primary targets.
3. Reasonable fallback venues.
4. Workshops and early-feedback opportunities.

Justify your ranking based on the actual evidence, novelty, limitations, and venue scope.

Remember that this is one research contribution represented in multiple formats, not multiple independent papers.

## 10. Scientific and editorial quality control

For every manuscript:

- Verify its claims against raw experiment data.
- Compare content against the canonical scientific inventory.
- Check all bibliography entries.
- Verify exact LaTeX class and template usage.
- Validate page limits where verifiable.
- Check anonymization where required.
- Inspect generated PDFs for broken tables, unreadable figures, overlapping text, reference errors, and formatting defects.
- Confirm all important results remain represented.
- Check scientific limitations and negative results.
- Confirm the manuscript complies with the publication's AI-writing and disclosure requirements.
- Record the status honestly.

Do not add unsupported experiments, hide negative outcomes, claim equivalence without evidence, or exaggerate novelty.

Do not claim a paper is ready for submission merely because it compiles.

Distinguish between:
- TEMPLATE-VERIFIED
- MANUSCRIPT-DRAFTED
- COMPILED
- SCIENTIFICALLY-AUDITED
- HUMAN-REVIEW-REQUIRED
- HUMAN-AUTHORING-REQUIRED
- NEEDS-GUIDELINE-REFRESH
- SUBMISSION-READY-PENDING-FINAL-CHECKS

A version should only receive the last status when all necessary checks have passed.

## 11. Future maintainability

I want this directory to remain useful even in 2027, 2028, or later.

Record template years and guideline verification dates.

Provide a `refresh_requirements` script or documented procedure that can recheck official venue instructions and flag versions needing updates.

Keep scientific content conceptually centralized so that a corrected result can be propagated across all manuscripts.

Avoid maintaining independent, contradictory copies of scientific data.

Do not automatically modify accepted or submitted manuscripts.

Do not automatically submit papers anywhere.

## 12. Workflow and final delivery

Work autonomously through the repository.

Do not restart completed experiments.

Keep existing manuscripts and logs unchanged.

Maintain DECISIONS.md, recording significant research, editorial, formatting, and venue-selection decisions.

Commit meaningful milestones rather than individual file changes.

Prioritize scientific correctness and official-template compliance over speed and the number of generated PDFs.

At completion, provide:

1. Total manuscript versions produced.
2. Directory tree.
3. Page and word count for each version.
4. Official formatting source and verification date for each venue.
5. Successful versus unsuccessful compilations.
6. Scientific coverage verification.
7. Venue-fit recommendations.
8. Manuscripts requiring human authorship or disclosure review.
9. A recommended publication submission sequence.
10. Remaining issues preventing any version from being genuinely submission-ready.

**The objective is a permanent, professionally organized research publication library. I should be able to open a folder, select a version for a specific publication venue, review it, refresh any changed requirements, and proceed with minimal additional formatting work.**

Do not optimize for the number of versions at the expense of scientific integrity. Complete genuine, well-supported versions and clearly document anything unfinished.