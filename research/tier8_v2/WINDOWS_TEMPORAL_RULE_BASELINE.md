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
