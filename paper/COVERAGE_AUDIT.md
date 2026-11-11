# Scientific coverage audit and restoration

Status: all three manuscripts read; raw-data reconciliation and restoration in progress. Final page references will follow compilation.

O: original 37-page AAAI manuscript, `output/pdf/RESEARCH_PAPER_AAAI.pdf`, 16,802 extracted words.
M0: shortened main, `output/pdf/AGERE_FINAL_AAAI.pdf`, 7 pages, 5,130 words.
S0: shortened supplement, `output/pdf/AGERE_FINAL_SUPPLEMENT.pdf`, 10 pages, 5,346 words.
Source/PDF/package fingerprints are frozen in `preserved_versions.json`. Revised outputs are separate under `paper/revised_aaai/`.

## Initial comparative findings

- O §4 p4: explicit RQ1–RQ4 and H1–H4 partially omitted from M0 §1 pp1–2; restore operational hypotheses and distinguish pre/post-hoc status.
- O §5.2–5.10 pp4–8: protocol largely retained in M0 §3 pp2–3 and S0 §2–3 pp1–4; reserve/context rationale, statistical formulas and inference hierarchy partially omitted.
- O §6.1 pp8–9: 175-case synthetic outcomes completely omitted. S0 §5.1 p6 retains rule-solvability only; restore outcomes with denominator and measurement caveats.
- O §6.2 pp10–11: outcomes moved to S0 §8 pp9–10; memory columns and shared-backbone engineering result omitted.
- O §6.3–6.5 pp10–15: headline accuracy retained, but paired transitions, per-report comparisons and four-endpoint sensitivity omitted. Historical timing must remain separate from Ubuntu replication timing.
- O §6.6–6.9 pp10–18: candidate bottleneck, repair and scoring sensitivity condensed; stage-factorization table, paired ablation intervals and gold-complexity strata omitted.
- O §6.10–6.12 pp18–22: stage costs and resource chronology partially omitted; utility and always-withhold comparator completely omitted.
- O §6.13 pp23–29: complete 21-comparison/126-endpoint battery largely omitted; a pointer to archived files does not replace reader-facing results.
- O §7 pp29–30: five worked examples completely omitted, including the synthetic sentinel-label caveat.
- O §8 pp30–32: P1–P3 condensed; P4–P10 and J1–J12 largely omitted. Restore valid arguments with corrected qualifications.
- O §9–12 pp32–34: bounded conclusion retained; hypothesis/gap dispositions and grammar/nonidentification explanations partially omitted. Universal deployment recommendations are not supported.
- O references pp34–36: focused bibliography retained; relevant antecedents need verification and restoration, peripheral exclusions require explanation.
- O appendices pp36–37: reproduction material moved/reconstructed; useful definitions and accessible evidence map need restoration, without claiming missing SSD exports exist.

## Corrections identified during complete reading

1. P5 omits the +3*kappa repair benefit when withholding carries cost; its old formula holds only at kappa=0.
2. P10 bounds one score statistic, not every valid cluster-test p-value.
3. Few discordances constrain the two-sided exact McNemar procedure, not every possible test.
4. Post-hoc tests must not be retrospectively described as confirmatory.
5. Equal ceilings do not measure or equalize FLOPs; O p4 incorrectly says both quantities were measured.
6. INSUFFICIENT does not causally identify a capacity floor or exclude prompt, grammar and coordination causes.
7. Identical tools do not remove recipe confounding. Extensive statistical analysis was post hoc, as recorded in DECISIONS.md.
