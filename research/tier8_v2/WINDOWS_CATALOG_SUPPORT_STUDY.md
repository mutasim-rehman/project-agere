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
