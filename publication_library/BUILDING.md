# Building and refreshing the publication library

Each compiled project contains its own source, bibliography, figures and required class/BST assets. No model weights, external SSD, inference server or original-run replay is needed to typeset a manuscript. IEEE Access is the explicit exception: authentic journal class/assets are still missing, and no main.pdf is claimed.

## Portable build

Install a TeX distribution and put pdflatex/bibtex on PATH. From the repository root:

    python publication_library/shared/production/build_library.py --folder 14_SN_Computer_Science

Build the produced new projects with:

    python publication_library/shared/production/build_library.py

The default preserves the original six PDFs; --include-original-six explicitly rebuilds them. Use the separately corrected generic Springer project at13_Springer_journal/verified_citations. Place a PUBLICATION_LOCK file in any submitted/accepted project to prevent automatic rebuilding. Never blindly run production/generation scripts over edited, submitted or accepted snapshots.

On Windows, each project's build.ps1 resolves its own directory and stops immediately on compiler/BibTeX errors, even when launched from another working directory. Root-directory invocation verified with the short paper; Access correctly returns failure at its absent class.

The tested environment is PDFLaTeX/BibTeX, TeX Live2026/TinyTeX. Standard packages include AMS tools, graphics, booktabs, longtable, natbib/cite, url/hyperref, seqsplit, newtx/courier, microtype and template dependencies. MDPI additionally needs its official Definitions assets, mathpazo/Palatino and CM-Super fonts, lineno, lastpage, enumitem, titlesec, tabto-ltx, soul, colortbl, pgf, changepage, frankenstein(attrib), was(upgreek), pbox, ragged2e, tocloft, marginnote, marginfix, enotez/translations, subfig, alphalph, ulem, wasysym, mathcomp, bbm-macros, verse, cleveref, koma-script, newfloat and draftwatermark. ICLR requires eso-pic; ICML forloop; LNCS aliascnt. Install missing dependencies through the TeX distribution, not by modifying publisher styles.

## Scientific/format audit

    python publication_library/shared/production/audit_adaptations.py

This checks bibliography identities and figure bytes, maps expanded canonical headings to actual PDF/support pages, and reports overfull/unresolved-reference warnings. It does not replace raw-outcome verification or visual inspection. The raw verification record and original37-page scientific coverage audit remain centralized in shared/verified_results and shared/source_inventory. Style-specific verified citation-location fields are in shared/bibliographic_location_overrides.json; the frozen canonical export is not overwritten.

## Requirements refresh

    python publication_library/shared/production/refresh_requirements.py

The script reads official sources from venue_manifest.json, checks HTTP availability/content hashes and writes requirements_refresh.json. It never rewrites a manuscript or interprets a policy automatically. Known blocked binary/authentication/ranking routes are skipped unless --include-blocked is explicitly supplied. A changed hash can reflect navigation changes; a successful HTTP response does not establish policy compliance. Compare current official instructions manually, update the verification date and create a new reviewed snapshot. Do not automatically modify accepted/submitted manuscripts or submit anything.

All PDF counts use whitespace extraction, including captions/references and sometimes line numbers/appendix/checklist. They are not journal word-limit calculations. Final human every-page inspection and administrative declarations remain mandatory before any submission-ready claim.
