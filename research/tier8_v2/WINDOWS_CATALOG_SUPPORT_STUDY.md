# Windows 8 GB source quantity catalog intervention

The existing [source-span catalog prototype](SOURCE_SPAN_CATALOG_BASELINE.md)
appends executor-supported numeric values that were visible in the
original evidence but missing from its selectable quantity IDs.
It preserves every original ID and leaves the evidence text unchanged.
An offline check using the pinned lexical8 evidence found that this
expansion raises numerical bindability of annotated programs from
703 to 718 out of 883 development questions and 891 to 919 out of
1,147 test questions. This is numerical representability, without
proof of correct source identity or semantic binding.

The neural diagnostic includes all five eligible test reports
where the annotated program becomes bindable after expansion.
We exclude preceding Windows FinQA cohorts and the inspected
initial and continuation actor training/validation records.
Two reports are from the same company in different years.
This is an annotation-enriched mechanism test, so its candidate
accuracy cannot estimate performance on unselected benchmark
questions. Gold information is used for inclusion and scoring.
Only question, source evidence and its corresponding catalog
enter inference.

Both arms use adapted 3B Q4, the same drafting prompt, 768
output-token cap and deterministic executor. The original
catalog is compared with the existing span-complete prototype.
Arm order alternates. The job limit is 6.1 GB with the
6.4 GB sampled RSS guard. There are no verifier calls.
Use `tier8_windows_natural_pairs.py run --complete-catalog`.
Frozen cohort SHA-256
`3548e4592a76d8628ac5187eda3b65eb5a9367ffae9cf25cf1727b3ed69de5fc`.

## Completed enriched diagnostic

The original catalog produced 0/5 correct final programs.
The span-complete catalog produced 2/5 under both execution
and reported-answer scoring, with two gains and no losses.
Both recovered programs referenced a newly selectable quantity.
A third incorrect program also used an added quantity, so
catalog expansion supplies possible operands without proving
their semantic relevance. These five cases were selected for
the representational defect, and the result cannot be read as
a 40-point improvement on general FinQA.

## Unselected 96-report follow-up

The same catalog change was tested with the unadapted 3B Q4
checkpoint on 96 frozen reports. The original catalog scored
2/96 and the span-complete catalog scored 1/96, with no gains
and one regression. Both scoring conventions agreed. Only
two questions in the cohort had annotated programs that became
representable under the complete catalog; neither was answered
correctly. The full-cohort comparison therefore did not support
adopting expansion as a general accuracy intervention. It also
differs from the targeted diagnostic in checkpoint adaptation
and case selection.

The expanded arm used 96,545 prompt-evaluation tokens versus
86,773, with median drafting time 24.2 versus 23.0 seconds.
Both peaked near 2.77 GB worker commit. See
`evidence/windows-extended/catalog96-summary.json`.
