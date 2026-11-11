# Scientific coverage audit and restoration

Completed comparative reading, raw-evidence reconciliation and restoration. Page numbers below refer to PDF pages, including navigation pages.

## Versions and counting method

O = original `output/pdf/RESEARCH_PAPER_AAAI.pdf`; M0/S0 = preserved shortened `output/pdf/AGERE_FINAL_AAAI.pdf` and `AGERE_FINAL_SUPPLEMENT.pdf`; M/S = revised `paper/revised_aaai/main.pdf` and `supplement.pdf`. All originals remain unchanged, checked against `preserved_versions.json`. Word counts use whitespace-separated PyMuPDF extracted text, including tables, captions, references and navigation; they are approximate and not unique-prose counts.

- O: 37 pages; 16,802 extracted words.
- M0: 7 pages; 5,130 extracted words.
- S0: 10 pages; 5,346 extracted words.
- M: 8 pages; 5,520 extracted words.
- S: 28 pages; 14,975 extracted words.

The original versus M0+S0 reduction was about 38%. The revised main remains concise; the expanded supplement restores supporting science. Added later Windows/planner evidence means this is not a verbatim recreation of the old manuscript.

## Classification rules

Each old numbered section/subsection is classified twice: its status in M0/S0 before this restoration, and its final disposition. “Fully retained” concerns scientific content, not exact wording. “Condensed without losing substance” merges equivalent exposition. “Moved to supplement” preserves supporting content with a main-paper summary where essential. Partial/complete omissions are named and justified; they are not hidden by an artifact inventory. Detailed subitems below override a broad parent classification.

## Complete section-by-section comparison

| Original item and PDF pages | Status in M0/S0 | Final disposition | Final location | Scientific treatment |
|---|---|---|---|---|
| O §1 Introduction pp1–2 | Condensed without losing substance | Condensed without losing substance | M §1 p1 | Motivation, scope and bounded contribution; avoid universal novelty or legal-locality claims. |
| O §1.1 Motivation pp1–2 | Condensed without losing substance | Condensed without losing substance | M §1 p1; S §9.2 p12 | Memory-limited financial reasoning motivation retained; regulatory mandates not asserted. |
| O §1.2 Status quo pp2 | Partially omitted | Condensed without losing substance | M §2 p2; S §14 p27 | Resource/precision precedents restored; no exhaustive first-ever gap claim. |
| O §1.3 Contributions pp2 | Partially omitted | Condensed without losing substance | M §1 p1; S §10 p13; S §11 p18; S §12 p20 | Scientific contributions restored; historical commit/script/figure counts excluded as stale bookkeeping. |
| O §1.4 Scope pp2 | Fully retained | Fully retained | M §1 p1; M §5 p6; S §6 p10 | No 32 GB results, no factorial architecture or precision interpretation. |
| O §2 Background pp2–3 | Partially omitted | Condensed without losing substance | M §3 p2; S §9.2 p12; S §11 p18 | Background reorganized around explicit methods and assumptions. |
| O §2.1 Workstation memory as the binding constraint pp2 | Partially omitted | Moved to supplement | S §9.2 p12 | Budget formula, host reserve, cap reduction and sampling limitations restored. |
| O §2.2 Quantization and storage arithmetic pp2 | Partially omitted | Moved to supplement | S §9.2 p12; S §11.3 p18 | Model file bytes and precision accounting restored; disk/RSS/commit distinguished. |
| O §2.3 Selective answering pp2–3 | Condensed without losing substance | Fully retained | M §3.1 p2; S §10.1 p13; S §11.1 p18 | C/W/H, coverage and selected-risk denominators retained explicitly. |
| O §3 Literature Review pp3–5 | Partially omitted | Condensed without losing substance | M §2 p2; S §14 p27 | Focused verified related work plus restored closest financial/deployment antecedents. |
| O §3.1 Test-time compute parity pp3 | Condensed without losing substance | Condensed without losing substance | M §2 p2; S §14 p27 | Equal-token comparison retained; token ceilings do not equalize actual compute. |
| O §3.2 When teams help: scaling and tool access pp3 | Partially omitted | Condensed without losing substance | S §14 p27 | Positive small-agent/tool-access counterevidence restored; unrelated benchmark percentages excluded. |
| O §3.3 How multi-agent systems fail pp3 | Partially omitted | Condensed without losing substance | M §2 p2; S §11.6 p20; S §14 p27 | Failure taxonomy and error-propagation limits retained; no measured Markov cascade asserted. |
| O §3.4 Quantization in agentic settings pp3 | Partially omitted | Condensed without losing substance | S §14 p27 | AWQ and quantized-agent process-failure precedents restored; no claim GGUF Q4 is AWQ. |
| O §3.5 Local inference and financial reasoning pp3 | Partially omitted | Condensed without losing substance | M §2 p2; S §14 p27 | FinQA, TAT-QA and Bench360 context restored; no cross-paper performance imported. |
| O §3.6 Closest prior work on financial agents and verification pp3–4 | Partially omitted | Condensed without losing substance | M §2 p2; S §14 p27 | FinMAN/DCRC restored alongside VeriFin/BudgetVerify; components not claimed novel. |
| O §3.7 Synthesis table and remaining gap pp4–5 | Completely omitted | Condensed without losing substance | M §2 p2; S §9.1 p12; S §14 p27 | Comparison dimensions discussed; old categorical not-located novelty matrix excluded as incomplete literature evidence. |
| O §4 Research Questions and Hypotheses pp4 | Partially omitted | Fully retained | M §1 p1; S §9.1 p12 | RQ1–RQ4 and H1–H4 restored with outcome dispositions; no retrospective confirmatory battery. |
| O §5 Methodology pp4–8 | Partially omitted | Fully retained | M §3 p2; S §2 p3; S §9 p12; S §12 p20 | Methodology reconstructed across distinct studies and historical controls. |
| O §5.1 Design overview: three evidence regimes pp4–5 | Partially omitted | Fully retained | M §1 p1; M §3 p2; S §9 p12 | Distinct regimes, frozen primary and synthetic-to-natural-task rationale restored. |
| O §5.2 Resource parity protocol pp4 | Partially omitted | Fully retained | M §3.2 p2; S §2.1 p3; S §9.2 p12 | Reserve/context probes, runtime, ceilings and absent FLOP/energy measurement explicit. |
| O §5.3 Systems under comparison pp4,6 | Condensed without losing substance | Fully retained | M §3.2 p2; S §2 p3; S §9.2 p12 | Unadapted instruction checkpoints, sizes, precision, residency and adapter asymmetry explained. |
| O §5.4 Program representation and stages pp4 | Condensed without losing substance | Fully retained | M §3.1 p2; S §13 p26 | Program references, constants, allowed operations and execution/review/delivery requirements retained. |
| O §5.5 Prompt profiles pp6–7 | Condensed without losing substance | Fully retained | M §3.2 p2; S §2.1 p3; S §10.4 p16 | All three profiles and bundled-component confounding retained. |
| O §5.6 Data pp6 | Partially omitted | Fully retained | M §3 p2; S §2.4 p5; S §9.3 p13; S §10.3 p15 | Report selection, cohort overlaps, public-source status, synthetic counts and gold step counts restored. |
| O §5.7 Outcomes and metrics pp6 | Condensed without losing substance | Fully retained | M §3.4 p3; S §3 p5; S §11.1 p18 | Scoring units, tolerance, unsupported labels, candidate/delivery definitions and official-score distinction retained. |
| O §5.8 Statistical analysis pp6 | Partially omitted | Fully retained | M §3.4 p3; S §10.2 p14; S §12 p20 | Primary estimand versus post-hoc testing, clustering, multiplicity and sensitivity restored. |
| O §5.9 Mathematical and statistical testing standards pp7–8 | Partially omitted | Moved to supplement | S §11 p18; S §12 p20 | All T1–T12 mathematical procedures, null assumptions, boundaries and decision standards restored/corrected. |
| O §5.10 Provenance and reproducibility pp8 | Partially omitted | Condensed without losing substance | S §1 p3; S §2 p3; S §6 p10; S §14 p27 | Hash/replay lineage retained; inaccessible original SSD tarball not falsely released. |
| O §6 Results pp8–29 | Partially omitted | Fully retained | M §4 p3; S §4 p6; S §5 p7; S §8 p11; S §9.3 p13; S §10 p13; S §12 p20 | Headline, historical, negative and detailed statistical evidence restored with distinct scopes. |
| O §6.1 Historical 8 GB synthetic study (175 held-out cases) pp8–9 | Completely omitted | Moved to supplement | S §9.3 p13; S §13.6 p27 | 175-case synthetic metrics, hardening failures, platform probes and sentinel caveat restored. |
| O §6.2 Redeveloped 8 GB FinQA programme (15 configurations) pp10–11 | Partially omitted | Moved to supplement | S §5.1 p7; S §8 p11; S §9.3 p13; S §12.4 p21 | All 15 conditions including memory, adaptation, critic, serving and external controls retained. |
| O §6.3 Primary 16 GB results pp10,12 | Fully retained | Fully retained | M §4.1 p3; S §4 p6; S §10.4 p16 | All six accuracy conditions retained; original and Ubuntu timing/RSS kept separate. |
| O §6.4 Paired transitions pp10,12–13 | Partially omitted | Fully retained | M §4.1 p3; S §10.1 p13 | Both full transition matrices and report-rate comparison restored; raw MAS-only correct case caveat added. |
| O §6.5 Statistical inference for the primary contrasts pp10,14–15 | Partially omitted | Moved to supplement | M §4.1 p3; S §10.2 p14; S §12 p20 | All four interval endpoints, company/equal-report/deletion sensitivity and adjustments restored. |
| O §6.6 Where the team loses useful answers pp10,15–16 | Partially omitted | Fully retained | M §4.1 p3; S §10.3 p15; S §11.1 p18 | Complete candidate/gate counts and q/p/a/b decomposition restored; causal interpretation bounded. |
| O §6.7 Prompt bundle and repair ablations pp10,16–17 | Partially omitted | Fully retained | M §4.1 p3; S §10.4 p16; S §12.4 p21 | All bundle/repair contrasts and intervals restored; run-specific time differences retained. |
| O §6.8 Scoring-convention sensitivity pp10,16–17 | Condensed without losing substance | Fully retained | M §3.4 p3; M §4.1 p3; S §3 p5; S §10.3 p15; S §13.5 p27 | 48 discordant delivery labels, 2x2 table and percent/fraction example restored. |
| O §6.9 Post-hoc strata: reasoning complexity and retrieval pp10,18–19 | Partially omitted | Moved to supplement | M §4.1 p3; S §10.3 p15 | Both complexity partitions and retrieval-completeness strata restored with reference dependence. |
| O §6.10 Memory, latency and cost per useful answer pp18–21 | Partially omitted | Moved to supplement | S §10.4 p16 | Latency, prompt/output tokens, stage work and amortized work/correct restored for both runs. |
| O §6.11 Resource validity chronology pp19,21 | Partially omitted | Fully retained | M §5 p6; S §6 p10; S §10.4 p16 | Reserve/context/swap/continuation chronology restored and separated from Ubuntu resource-qualified repeat. |
| O §6.12 Utility and decision analysis pp19,22–23 | Completely omitted | Moved to supplement | S §11.2 p18 | Loss-based utility, raw/reported switch points, abstention cost and always-withhold comparator restored. |
| O §6.13 Numerical hypothesis-test battery pp19,23–29 | Partially omitted | Moved to supplement | S §10.2 p14; S §12.4 p21 | All 21 comparisons, 126 endpoint rows and complete JSON test fields restored; overbroad interpretations corrected. |
| O §7 Example Outputs pp29–30 | Completely omitted | Moved to supplement | M §4.1 p3; S §13 p26 | All five original examples plus score-disagreement case restored from saved traces. |
| O §7.1 Both arms correct: ABMD/2007/page\_52.pdf-1 pp29 | Completely omitted | Moved to supplement | S §13.1 p26 | Shared ABMD success, source quantities and same program; historical timing not applied to Ubuntu. |
| O §7.2 SAS correct, MAS abstains: AAPL/2003/page\_24.pdf-1 pp29 | Completely omitted | Fully retained | M §4.1 p3; S §13.2 p26 | AAPL evidence found but drafter abstains, exact program and source subtraction restored. |
| O §7.3 SAS wrong (accepted by its reviewer), MAS operand error caught: AAPL/2003/page\_24.pdf-2 pp29–30 | Completely omitted | Moved to supplement | S §13.3 p26 | AAPL max-grammar limitation, wrong SAS PASS and caught MAS operand error restored. |
| O §7.4 Team reviewer passes a nonsensical program: PNC/2018/page\_171.pdf-1 pp30 | Completely omitted | Fully retained | M §4.1 p3; S §13.4 p27 | PNC incorrect team PASS restored; SAS reported/raw correctness distinction corrected. |
| O §7.5 Historical 8 GB credit pack: CR-TEST-0001 (synthetic) pp30 | Completely omitted | Moved to supplement | S §13.6 p27 | Synthetic NOT_PROVIDED versus MISSING contract error and malformed MAS denominator restored. |
| O §8 Formal Framework (Conditional Propositions) pp30–32 | Partially omitted | Moved to supplement | S §11 p18; S §12 p20 | Every P1–P10 and J1–J12 reviewed individually below; valid substance restored with corrections. |
| O §8.1 Decision and accounting propositions pp30–31 | Partially omitted | Moved to supplement | S §11 p18 | Conditional identities, utility/memory/uncertainty bounds and nonidentification restored. |
| O §8.2 Theoretical justification of the testing standards pp31–32 | Partially omitted | Moved to supplement | S §12 p20 | Paired likelihood, variance, null assumptions, multiplicity and interpretation restored/corrected. |
| O §9 Discussion pp32–34 | Condensed without losing substance | Condensed without losing substance | M §5 p6; S §9.1 p12; S §11.6 p20 | Bounded empirical argument retained; causal capacity, universal precision and novelty overclaims excluded. |
| O §9.1 Answer to the research question pp32 | Fully retained | Fully retained | M §4.1 p3; M §6 p7; S §9.1 p12 | Operational H1 failure retained, with raw-score exception to no uniquely correct delivery. |
| O §9.2 Why the team underperformed pp32–33 | Condensed without losing substance | Fully retained | M §4.1 p3; M §5 p6; S §10.3 p15; S §11.6 p20; S §13 p26 | Generation bottleneck and examples restored without identifying a unique causal mechanism. |
| O §9.3 What precision bought pp33 | Condensed without losing substance | Fully retained | M §4.1 p3; M §5 p6; S §10.1 p13; S §11.3 p18 | Resident footprint and weak precision-on-eight-answers interpretation retained. |
| O §9.4 Status of the proposed research gaps pp33–34 | Partially omitted | Condensed without losing substance | S §9.1 p12 | Four gap dispositions restored with baseline fairness left partly unresolved. |
| O §9.5 Practical guidance for on-premise deployment pp33 | Partially omitted | Condensed without losing substance | M §5 p6; S §9.2 p12; S §14 p27 | Measured cautions retained; blanket largest-quantized-model and disable-mmap deployment prescriptions excluded. |
| O §10 Threats to Validity and Limitations pp33 | Condensed without losing substance | Fully retained | M §5 p6; S §2.4 p5; S §6 p10; S §11 p18; S §12 p20 | Construct/internal/external/statistical/resource validity retained and expanded with current missing evidence. |
| O §11 Ethics and Responsible Use pp33 | Condensed without losing substance | Condensed without losing substance | M §5 p6; S §9.1 p12; S §14 p27 | Public/synthetic data and no autonomous financial-decision validation retained; no invented compliance certification. |
| O §12 Conclusion and Future Work pp33–34 | Condensed without losing substance | Condensed without losing substance | M §6 p7; S §6 p10; S §9.1 p12 | Bounded conclusion and unresolved validity controls retained; stale future-run scheduling removed. |
| O §A Artefact and Provenance Map pp36–37 | Partially omitted | Moved to supplement | S §1 p3; S §6 p10; S §14 p27 | Evidence/reproduction hierarchy rebuilt around available handoff; old missing SSD export paths treated historically. |
| O §B Reproduction pp36 | Moved to supplement | Moved to supplement | S §7 p10; S §14 p27 | Analysis, restoration and known-value test commands retained; inaccessible SSD-specific path assumptions disclosed. |
| O §C Glossary pp36 | Condensed without losing substance | Condensed without losing substance | M §3 p2; S §14 p27 | Useful symbols and memory/quantization terminology defined; irrelevant compliance acronym expansion excluded. |

For the pre-restoration locations: M0 §1 pp1–2; §2 pp1–2; §3 pp2–3; §4.1 pp3–4, §4.2 p4, §4.3 pp4–5, §4.4 pp5–6; §5 pp6–7; §6 p7. S0 §1 p1; §2 pp1–3; §3 pp3–4; §4 pp4–5; §5.1 p6, §5.2 pp6–7, §5.3 p7, §5.4 pp7–8, §5.5 p8; §6 pp8–9; §7 p9; §8 pp9–10. These are the comparison locations for the classifications above.

## Every original table and figure

| Original asset and page | Before restoration | Final location or justified exclusion |
|---|---|---|
| O Table 1 p5 | Completely omitted | M §2 p2; S §14 p27. Old binary novelty matrix excluded; verified competing approaches compared in prose. |
| O Table 2 p5 | Partially omitted | M §3 p2; S §2 p3; S §9 p12. Distinct regimes reconstructed, no pooling. |
| O Table 3 p6 | Partially omitted | S §9.2 p12. Exact GGUF bytes restored. |
| O Table 4 p7 | Condensed without losing substance | M §3.2 p2; S §2.1 p3. Profiles retained. |
| O Table 5 p8 | Partially omitted | S §12 p20. Inferential hierarchy restored with post-hoc status corrected. |
| O Table 6 p9 | Completely omitted | S §9.3 p13. All synthetic denominators restored. |
| O Table 7 p11 | Partially omitted | S §8 p11. All 15 conditions and memory restored. |
| O Table 8 p11 | Partially omitted | S §8 p11. Continuation of condition census. |
| O Table 9 p12 | Fully retained | S §4 p6; S §10.4 p16. Accuracy retained; historical/Ubuntu resources distinct. |
| O Table 10 p12 | Partially omitted | S §10.1 p13. Conditional denominators and descriptive Wilson intervals restored. |
| O Table 11 p12 | Partially omitted | M §4.1 p3; S §10.1 p13. Full paired matrix restored. |
| O Table 12 p14 | Partially omitted | S §10.2 p14. All four intervals and family-width sensitivity restored. |
| O Table 13 p14 | Partially omitted | S §10.2 p14. Equal weighting, deletion range and adjusted testing restored. |
| O Table 14 p15 | Condensed without losing substance | S §10.3 p15. Exact candidate/gate table restored. |
| O Table 15 p16 | Completely omitted | S §10.3 p15; S §11.1 p18. q/p/a/b factorization restored. |
| O Table 16 p16 | Partially omitted | S §10.4 p16; S §12.4 p21. Every paired ablation interval restored. |
| O Table 17 p16 | Condensed without losing substance | S §3 p5; S §10.3 p15. 2x2 score concordance partition printed. |
| O Table 18 p18 | Completely omitted | S §10.3 p15. Both reference strata partitions restored. |
| O Table 19 p18 | Partially omitted | S §10.4 p16. Prompt/output/stage/correct cost restored; run distinction. |
| O Table 20 p24 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 21 p24 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 22 p24 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 23 p24 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 24 p25 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 25 p25 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 26 p25 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 27 p25 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 28 p26 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 29 p26 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 30 p26 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 31 p27 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 32 p27 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 33 p27 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 34 p28 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 35 p28 | Partially omitted | S §10.2 p14; S §12.4 p21. Complete recomputed 126-row battery plus JSON retains exact/asymptotic/Wald/cluster/sign/symmetry fields; redundant panels combined. |
| O Table 36 p34 | Partially omitted | S §9.1 p12. Gap dispositions corrected, especially baseline confounding. |
| O Table 37 p37 | Moved to supplement | S §1 p3; S §6 p10; S §14 p27. Evidence map updated to available artifacts. |
| O Table 38 p37 | Moved to supplement | S §14 p27. Repository protocols/decisions included in map. |
| O Figure 1 p9 | Completely omitted | S §9.3 p13. Synthetic graph replaced by exact numerator/denominator table; a percent-only graph would obscure unmatched invention denominators. |
| O Figure 2 p11 | Moved to supplement | S §8 p11. All 15-condition results retained in table; duplicate stacked plot not restored. |
| O Figure 3 p12 | Fully retained | M §4.1 p3. Main all-six-job figure retains both scores. |
| O Figure 4 p13 | Partially omitted | S §10.1 p13. Both paired transition heatmaps restored. |
| O Figure 5 p13 | Completely omitted | S §10.3 p15. Report-rate heterogeneity scatter restored. |
| O Figure 6 p14 | Partially omitted | S §10.2 p14. All primary intervals restored as precise tables; no duplicate interval plot. |
| O Figure 7 p15 | Completely omitted | S §10.2 p14; S §12.2 p20. Bootstrap percentile values, algorithm and assumptions retained; redundant distribution illustration excluded. |
| O Figure 8 p15 | Completely omitted | S §10.2 p14. Company/report interval comparison retained in numerical table. |
| O Figure 9 p16 | Condensed without losing substance | S §10.3 p15. Candidate/gate flow retained in complete table and formula. |
| O Figure 10 p17 | Partially omitted | S §10.4 p16. Repair outcomes/time reconciled for both runs; duplicate cost plot excluded. |
| O Figure 11 p17 | Condensed without losing substance | S §10.3 p15. Metric disagreement retained as exact counts and worked example. |
| O Figure 12 p18 | Completely omitted | S §10.3 p15. Reference-step complexity figure restored; family counts in table. |
| O Figure 13 p19 | Partially omitted | S §10.3 p15. All retrieval-stratum numerators/denominators printed; duplicate bar plot excluded. |
| O Figure 14 p20 | Partially omitted | S §10.4 p16. All six median/summed inference measurements retained; full distributions newly retained in resource JSON. |
| O Figure 15 p20 | Completely omitted | S §10.4 p16. Stage work chart and tokens/timing table restored. |
| O Figure 16 p21 | Partially omitted | S §9.2 p12; S §10.4 p16. Model file sizes plus distinct run RSS values in tables. |
| O Figure 17 p21 | Partially omitted | S §6 p10; S §10.4 p16. Swap failures and all Ubuntu sample checks retained; a subset-of-attempts trace plot excluded as potentially misleading. |
| O Figure 18 p22 | Completely omitted | S §11.2 p18. Utility curve restored with always-withhold comparator. |
| O Figure 19 p22 | Completely omitted | S §11.2 p18. Withholding-cost sensitivity restored; repair formula corrected. |
| O Figure 20 p23 | Completely omitted | M §4.1 p3; S §10.1 p13; S §11.2 p18. All six C/W/H operating points retained in main figure and tables; no interpolated risk-coverage curve claimed. |

## Formal propositions and derivations: validity decisions

| Original result | Validity and correction | Final treatment |
|---|---|---|
| P1 (p30) | Valid partition identity; lower wrong count alone can mean more withholding. | S §11.1 p18 |
| P2 (p30) | Valid for a fixed candidate accept/reject gate only; cannot generalize to repair, new generation or another candidate pool. | S §11.1 p18 |
| P3 (p30) | Valid empirical chain rule without independence; conditional factors undefined when their denominator is zero. | S §11.1 p18 |
| P4 (p30) | Valid sample utility switch algebra; preference weights are assumed, not learned safety thresholds; restore raw and always-withhold comparisons. | S §11.2 p18 |
| P5 (p30) | Partially invalid as a general kappa formula: add +3*kappa for reduced withholding. Positive compute cost does not make repair universally worse for all loss choices. | S §11.2 p18 |
| P6 (p30) | Conditional storage accounting only under full residency/disjoint allocations; cannot universally lower-bound physical RSS by entire file bytes. | S §11.3 p18 |
| P7 (pp30–31) | Valid bounded-independent-contribution inequality with fixed weights; not a random-denominator/sampling-design guarantee. Effective clusters measure weight concentration. | S §11.4 p19 |
| P8 (p30) | Valid partition identity for metric disagreement; does not adjudicate the correct scorer. | S §11.5 p19 |
| P9 (p31) | Valid minimum p for the stated exact conditional McNemar procedure. Old “no test could be significant” statement excluded. | S §11.5 p19 |
| P10 (pp31–32) | Cauchy–Schwarz bound valid for Q=(sum S)^2/sum S^2 and its chosen tail. Universal bound on all valid cluster-test p-values is false and excluded. | S §11.5 p19 |
| Nonidentification (p30) | Valid design limitation; source-visible roles invalidate a message-only Markov information-loss premise. | S §11.6 p20 |
| J1 (O pp31–32) | Paired covariance derivation valid; independent-arm testing inappropriate to this pairing. | S §12.1 p20 |
| J2 (O pp31–32) | Conditional binomial exactness requires independent pairs; conservative does not cure clustering. | S §12.1 p20 |
| J3 (O pp31–32) | Asymptotic chi-square conditional on adequate discordances; continuity correction uses max(abs(b-c)-1,0), matching code. | S §12.1 p20 |
| J4 (O pp31–32) | Wald variance formula retained with boundary failures; no favorable interval cherry-picking. | S §12.1 p20 |
| J5 (O pp31–32) | Bowker/SM formulas retained with rank handling and sparse/case-IID caveats. | S §12.2 p20 |
| J6 (O pp31–32) | Cluster-variance and CR1 formulas retained; normal/score tests asymptotic. Exclude implied measured ICC and literal effective-IID sample-size claims. | S §12.2 p20 |
| J7 (O pp31–32) | Cluster bootstrap ratio consistency requires exchangeability, regularity and nonzero denominator; same-sign resamples need not always touch zero. | S §12.2 p20 |
| J8 (O pp31–32) | Sign-flip exactness requires independent sign-symmetric cluster sums; report-sign needs equiprobable signs. Zero mean is insufficient. | S §12.3 p21 |
| J9 (O pp31–32) | Holm proof valid for valid marginal p-values under arbitrary dependence; cannot repair invalid input tests. Withholding-family exclusion is a design choice. | S §12.3 p21 |
| J10 (O pp31–32) | Wilson score formula retained as case-IID descriptive; no guarantee under clustered selected deliveries. | S §12.3 p21 |
| J11 (O pp31–32) | Finite risk difference and discordant odds separation retained. Old blanket dismissal of linear/clustered regression is excluded. | S §12.3 p21 |
| J12 (O pp31–32) | Scope, deterministic cohort, single seed, no equivalence and effect-size interpretation retained. | S §12.3 p21 |

## Raw evidence, computational checks and remaining weaknesses

The restoration is not an audit only against prose. `coverage_evidence_checks.json` pins raw inputs. The reconciliation checks 960 historical 16 GB case rows against their raw ledgers and Ubuntu score/delivery records, and all 768 historical FinQA rows against 15 raw ledgers. It recomputes all 126 endpoint rows and 42 metric-specific transition/symmetry blocks, cross-checks probability tails with SciPy, reproduces report/company sensitivity and re-aggregates 350 synthetic saved-score rows. The established raw-score audit separately re-executes 1,920 Ubuntu programs, rescoring Windows FinQA/TAT-QA ledgers; all 668,817 memory samples across 16 attempts are checked. Ten existing known-value tests pass. These checks do not independently adjudicate financial truth or regenerate model/training trajectories.

Remaining evidentiary weaknesses: one Qwen2.5 family; confounded recipe comparisons; shared/reused exploratory cohorts; deterministic selection and possible pretraining overlap; no TAT-QA report grouping; sparse planner gains; no complete secondary 7B baseline; Windows commit does not prove physical 8 GB/no paging; Ubuntu interruptions and missing original tarball/bootstrap log; no independent financial-label adjudication; incomplete optimized/factorial baselines. None is filled with estimated data.

No negative result was intentionally removed. Intentional exclusions are repetitive prose/plots; irrelevant acronym and legal background; unverified external leaderboard numbers/venue claims; stale repository counts and future-run scheduling; universal deployment advice; unsupported causal capacity/Markov/precision conclusions; incorrect generalizations explicitly listed above. Historical artifacts remain available for inspecting every excluded formulation.

## Main-paper self-containment

The main document independently defines recipes, cohorts, resource controls, scoring conventions, candidate versus delivery, paired uncertainty, main baselines, oracle access, planner allocation/criterion and failure, interrupted comparison and validity limits. It states the original hypotheses and includes paired transitions and worked failure summaries. The supplement supplies detailed proofs, complete tests, historical controls and reproduction records; it is not required to discover a reversal, an undisclosed negative main result or the reason the planner criterion fails. This is an editorial/scientific assessment, not an external peer-review certification.

Official venue requirements and unresolved template authentication are recorded in `VENUE_REQUIREMENTS.md`. The public official pages do not specify a numeric supplement cap; portal/file-size rules and the separate checklist must be checked before actual submission.
