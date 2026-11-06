# Project Agere - AAAI LaTeX conversion

This is a full-length formatting conversion of the exact paper requested by the user:

`output/paper/pre_supervisor_review/RESEARCH_PAPER.pdf`

Its matching Markdown source from the same directory was used for faithful text, equation and table extraction. The newer root manuscript and Phase 3 report were not substituted. The source PDF and Markdown remain unchanged; their SHA-256 hashes are in `conversion_audit.json`.

## Compile

Use PDFLaTeX and BibTeX with a current TeX Live distribution:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

`main.tex` contains the complete paper. `references.bib` contains only metadata present in the original references. The original undated grouped regulatory reference is retained as a regulatory-context paragraph; no author or year was guessed. The included `.bbl` is the compiled bibliography.

## Template and scope

- Uses `article` on US Letter with the unmodified `aaai2027.sty` and `aaai2027.bst`, two-column layout, template-managed text fonts, author-year bibliography, and no page numbers or running headers.
- Uses the template's `preprint` option. This retains the supplied author names without asserting AAAI acceptance or transferring copyright. The source supplied only "Project Agere" as the project identification; no university, email, grant, affiliation or author contribution was invented.
- The official AAAI author-kit pages returned HTTP 403 during retrieval. The style and bibliography files were downloaded unchanged from https://github.com/tabbycat7/aaai_2027_latex . Their hashes and retrieval provenance are recorded in the conversion audit. The associated author-instructions document was consulted for layout requirements.
- This is the complete original paper, not a shortened conference submission. The original 20 figures, 24 source tables, equations, examples, statistical discussion and appendices are retained. Very wide tables are split into readable panels/chunks with identifying columns repeated; values are not rounded or recalculated.
- The original text architecture diagram is reflowed into native LaTeX using the same model/stage/decision labels. Code examples soft-wrap for column width. Long formulae break at existing separators or use full-width placement.
- No new experiments, results, scientific claims, references or missing bibliographic metadata were added. Existing scientific assertions and limitations were not revised or independently re-reviewed as part of this formatting task.
- Formatting alone does not establish compliance with a particular AAAI track's page limit, anonymization, checklist or submission rules. No checklist answers, publication declarations or signature claims have been fabricated. The paper was intentionally not condensed or anonymized without a request to do so.

The ZIP contains the compilation sources, cited graphics, compiled bibliography, this note and the content-preservation audit. Compiler executables and the original paper are not bundled.
