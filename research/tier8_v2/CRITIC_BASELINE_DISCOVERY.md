# Baseline critic discovery before the matched intervention

The fixed probe contains8 whole training-source quartets from8 reports,32 greedy
JSON reviews. Both questions share exactly the same union evidence and both
programs have the same answer unit. For each question, its reference program is
PASS and the other question's program is FAIL under both audited numerical metrics.
Source question/program combinations for positives are familiar from SFT; crossed
negatives are new combinations. This is NOT held-out-report natural QA.

| Policy | Exact labels | Entirely exact quartets | Reference accepts | Crossed negatives accepted |
|---|---:|---:|---:|---:|
| Full joint7B SAS baseline |31/32|7/8|16/16|1/16|
| Original3B MAS critic |30/32|6/8|15/16|1/16|
| Extended3B MAS critic |27/32|4/8|15/16|4/16|

SAS metrics independently replay from raw responses and exact frozen inputs.
All reviews parse as explicit PASS/FAIL, no truncation. Sampled process-tree peak
5.188GB is below6.4GB; all3185 memory samples replay. Actual work27814 prefill tokens,
224 generated tokens and644.7 recorded inference seconds, with4096 context,
192-token review caps and deterministic greedy decoding. One critic call per row;
this is not a complete SAS draft/verify/retry deployment or a full MAS memory test.

Holding evidence/program/execution fixed, the greedy verdict changes correctly
with the question in15/16 paired switches. Holding evidence/question fixed gives
15/16 correct program-switch pairs too. Under this declared deterministic protocol,
a decision depending only on evidence+program, or only evidence+question, would
score50% on these balanced complete quartets. Therefore the program-only shortcut
shown possible in older synthetic data does NOT explain this7B model's results.
Joint question/program shortcuts and incomplete financial understanding remain
possible. Do not promote shallow artifact availability into a claim that all
neural critics ignore their questions.

The sole false accept is concrete: the requested quantity is the percentage change
in NON interest income from2011 to2012; the accepted program computes the change
in NET interest income instead. The other question explicitly asks for net interest
income. Arithmetic/source support can be valid while the requested financial metric
is wrong. This is a diagnostic example, not independent semantic adjudication or
a reason to hand-code this exact case into the method.

SAS meets its component of the predeclared ceiling rule (at least30/32 exact labels
and6/8 exact quartets). The EXTENDED MAS result is now below this threshold. If BOTH had met it, do not
add a continuation merely to manufacture a gain on this family. The original MAS
critic is a separate strong reference, not the rule's target MAS policy. Otherwise
only the already prepared matched continuation can be considered, and natural
report-disjoint utility must decide adoption. No new method has been trained yet,
no natural QA gain follows, and useful novelty remains unestablished.

[Audited SAS diagnostic and single error](evidence/sas7b-joint-quartet-probe-01.json).
Raw responses, policy, source selection, memory and paired-switch diagnostic stay
on SSD under `runs/tier8_quartet_probe/sas-joint-train8-01`.


## Original3B critic and annotation caveat

Original MAS critic completes the SAME32 inputs:30/32 exact labels,6/8 whole
quartets,15/16 references accepted,15/16 crossed negatives rejected. All224 output
tokens are parsed PASS/FAIL, no truncation;27814 prompt tokens,294.97 recorded
inference seconds and2.490GB sampled critic-only resident tree. These are not full
MAS pipeline costs. Correct question switches14/16; one unchanged PASS and one
unchanged FAIL. Original3B and7B SAS false accepts occur on DIFFERENT cases; do not
claim shared error correlation from this tiny diagnostic. No new training method.

The3B false accept substitutes OTHER PURCHASE COMMITMENTS for NONCANCELABLE
OPERATING LEASES. Its rejected positive is UNP/2016/page_21.pdf-1. Post-disagreement
source inspection reveals a possible reference mismatch: the question asks total
shares bought in December, table gives3,296,652 shares, but official answer34% and
program divide(3296652,9699127) give the fraction of quarterly repurchases. The
binary FAIL does not tell us the model's reason. Do not assert it independently
caught an annotation error, or that SAS is semantically superior for accepting it.
This is one outcome-guided inspected case, not a prevalence estimate. Preserve
all official scores/data; independent adjudication remains needed. Agreement under
both numerical metrics is NOT independent proof of question/program semantics.

[Original MAS diagnostic](evidence/mas3b-original-quartet-probe-01.json) ·
[Unresolved reference case](evidence/critic-reference-label-issue-unp2016-01.json).
The original MAS also meets the numerical threshold, but the predefined target
stop rule targets the extended MAS result, which now fails its ceiling. As that extension regresses,
never claim novelty by beating only a weakened baseline; retain original MAS and
natural-error comparisons. The strong original results are reason to be cautious
about adding another curriculum solely for this small artificial family.


## Completed extended critic

Full393-update training/conversion/native application proof completed. The same
fixed32 inputs yield27/32 labels,4/8 whole quartets,15/16 reference accepts and4/16
crossed-negative accepts. All reviews parse with no truncation. Raw prompt hashes,
verdicts, usage and every memory sample independently replay; sampled critic-only
peak2,490,101,760 bytes,27814 prefill/224 generated tokens,293.47 inference seconds.

This is worse than original30/32 on this tiny fixed training-source diagnostic.
It permits the predeclared matched continuation; it does not prove universal harm
or justify claiming a contribution against a weakened baseline. Natural studies
retain the original critic with the same continued actor, plus original actor and
critic. No natural matched result exists at this checkpoint.

[Audited extended probe](evidence/mas3b-extended-quartet-probe-01.json).
