# Recovery log — 2026-11-12

## MAKE recovered

Public publisher-linked ACS ZIP https://res.mdpi.com/data/MDPI_template_ACS.zip?v=20260911 downloaded successfully with ordinary User-Agent/Accept/Referer headers after the earlier default request returned 403. No authentication/access control bypass. Archive SHA-256 and date are in shared/official_templates/mdpi_public/provenance.json. Official class v6.5d 2026-10-19. Also obtained publisher-owned MDPI-AG/luatex-template repository as an alternative; standard ZIP is used for production.

Initial build failures: absent lineno, colortbl, attrib (frankenstein), translations and mathpazo metrics; installed dependencies. CM-Super download stalled on tlnet.yihui.org; switched to legitimate RIT CTAN mirror and installed. First all-in-one 41-page build had oversized support tables; separated the complete audited supplement (29 pages) and compiled 11-page journal main with zero overfull/undefined entries. Added explicit month strings for MDPI bibliography; removed default dummy DOI and marked unsubmitted.

## IEEE Access remains template-blocked

Current official preparation-page link https://ieeeaccess.ieee.org/wp-content/uploads/2026/05/ACCESS_latex_template_20260513-1-1.zip returned HTTP403 in direct downloads (default and browser-compatible request headers). Web reader recognizes application/zip but cannot expose ZIP bytes. Legacy official https://ieeeaccess.ieee.org/wp-content/uploads/2022/01/LaTeX.zip also returned403. These URLs are not retried repeatedly.

Official template-selector.ieee.org returned418. CTAN search did not identify an IEEE Access class distribution; IEEEtran is a different template and is not substituted silently. IEEE-author-credited Overleaf gallery is accessible: https://www.overleaf.com/latex/templates/ieee-access-latex-template/cdxrhtbjgszv ; its listed template is seven years old. Open-as-template redirects to login, so source export was not attempted past authentication. Public guessed .zip and /zip gallery endpoints returned404. Browser automation initialization failed with missing kernel assets; no browser credentials or login were accessed. Third-party GitHub copies lack publisher-authenticated provenance and are not labelled verified.

Compliant fallback: retain existing canonical engineering evidence; obtain the ZIP through an ordinary authorized publisher/Overleaf session or refresh publisher download availability. IEEE Access remains INCOMPLETE, not a policy-based exemption or a submission-ready PDF. No access-control circumvention.

## Existing versions

Recomputed all seven available main PDFs: bibliography key sets match all 28 canonical entries, eight local vector figure files each match canonical bytes, no overfull boxes/unresolved citations. Detailed heading/page mapping produced in ADAPTED_COVERAGE_MAP.md, including the Springer main and its comprehensive supplement. New MDPI and existing Springer contact sheets/enlarged results inspected; other existing forms still require enlarged final inspection. No old PDFs overwritten.

Native computer-use @oai/sky runtime also failed initialization with the same missing kernel-assets path error. No browser UI or authenticated service was accessed. New ICLR/NeurIPS/ICML PDFs compiled, all pages contact-sheet inspected and selected numerical pages enlarged. AAAI/IJCAI prose production is policy-blocked, not silently waived.
