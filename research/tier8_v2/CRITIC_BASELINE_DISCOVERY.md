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
| Original3B MAS critic |Pending|Pending|Pending|Pending|
| Extended3B MAS critic |Pending|Pending|Pending|Pending|

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
and6/8 exact quartets). Wait for the EXTENDED MAS result: if BOTH meet it, do not
add a continuation merely to manufacture a gain on this family. The original MAS
critic is a separate strong reference, not the rule's target MAS policy. Otherwise
only the already prepared matched continuation can be considered, and natural
report-disjoint utility must decide adoption. No new method has been trained yet,
no natural QA gain follows, and useful novelty remains unestablished.

[Audited SAS diagnostic and single error](evidence/sas7b-joint-quartet-probe-01.json).
Raw responses, policy, source selection, memory and paired-switch diagnostic stay
on SSD under `runs/tier8_quartet_probe/sas-joint-train8-01`.
