# Abstaining temporal table rule

A deterministic baseline binds a narrowly specified financial
change question to an exact table row and two explicit year
columns. It supports absolute differences and relative change
from a positive reference value. It requires the row to appear
in the original lexical evidence packet and abstains on
ambiguous bindings, unsupported scales, or contradictory
direction. The program goes through the same cited executor.
No model, annotated answer, or annotated operand selects a
row, column, operation or delivery.

We developed the narrow template on the public development
split and inspected input formatting to handle currency and
accounting notation. It delivered on 22 of 883 questions from
13 reports. All 22 matched official FinQA execution, and 21
matched the reported-answer convention. This is low coverage
and a development result.

The prospective diagnostic uses the official FinQA test source,
excluding every development-source report and the reports already
used in the Windows verifier, candidate, endpoint and precision
cohorts. The frozen rule is applied once to every remaining
question. Primary outcomes are correct, wrong and withheld counts
using the official execution scorer. Secondary reported-answer
counts preserve unit and rounding sensitivity. Report both
question coverage and the number of reports with any delivery.
The scope is one template family and does not extend to open
financial QA or automated regulatory decisions.

## Report-disjoint test

After the rule was committed, it delivered three answers on 453
questions from 117 reports, withheld 450, and matched neither
official execution nor reported-answer scoring on any of the three.
This is a failed transfer result. All three cases are retained:

- `SNA/2007/page_49.pdf-4`: the displayed 2006 and 2007 dividends
  are 1.08 and 1.11. The rule gives about +2.78%. The reference
  program adds the values before dividing by 1.08, yielding 2.02778
  as its raw result, while the reported answer is 2.7%. The program
  and reported answer differ under both usual percent conventions.
- `ZBH/2007/page_67.pdf-1`: the displayed 2006 and 2007 fees are
  8.8 and 1.0. Forward change relative to 2006 is about −88.64%.
  The reference instead computes the reverse change relative to
  2007, +780%. The rule and annotation use opposite year ordering.
- `ETFC/2012/page_43.pdf-3`: the question asks for the change in
  net impairment. The rule interprets change as an absolute
  difference and gives −2.0. The annotation uses a relative
  magnitude of about 13.4%. The wording leaves the requested
  unit and sign convention unclear.

These are case audits by the study author. The primary benchmark
scores remain as recorded, with no label replacement. A second
reader would be needed for adjudicated labels. The rule's low
coverage and disagreement with benchmark conventions prevent using
it as a reliable delivery policy.

## Reference consistency screen

The follow-up replays every annotated program with the official
FinQA evaluator. All 883 development and 1,147 test reference
programs reproduced their stored execution label. We then compared
that raw label against a separately supplied simple numeric
reported answer, under the project's reported rounding rule.
For a percentage, we allow both raw fractional and raw percentage
point interpretations. This screen does not infer unit scaling
for free-form answers and leaves non-simple-numeric labels out
of the comparison.

Of 851 eligible development questions, 110 labels were incompatible
under those conventions. Of 1,100 eligible test questions, 129
were incompatible. Among test exceptions, 87 differed by more
than 1% and 77 by more than 10% of the reported magnitude, using
the closer allowed percent interpretation and a small denominator
floor. Twenty-one had opposite signs. These are reproducible
screening flags, not a count of adjudicated annotation errors.
The full exception list and source hashes are archived in
`reference-consistency.json`. Primary comparisons retain the
official labels and report the alternate metric separately.
