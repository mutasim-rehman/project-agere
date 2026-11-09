# Extended Windows 8 GB study on main

The dashboard branch was merged into main at `a973bb8`.
All dashboard conflicts were resolved using its complete dashboard
tree. The tree hash is `cf8041cd70389804fe1c99533eb8a723edc1ad52`.
New experiments and evidence are committed to main.

The extended window began shortly after 00:14 Pakistan time on
November 9, 2026. The Windows 8 GB CPU tier remains the active scope.
The worker commit ceiling is 6.1 decimal GB and the sampled
process-plus-controller RSS guard is 6.4 GB. Resource eligibility
does not certify absence of Windows paging.

## Frozen comparisons

1. Replay both trained critics on the 21 narrow candidates from
   the earlier report-disjoint retrieval comparison. Compare correct,
   wrong and withheld with accepting every executable draft.
2. Repeat the matched Q4/Q8 FinQA experiment on 96 additional
   company-year reports. The previous Windows cohorts and named
   project evaluation packets are excluded. The checkpoints are
   unadapted, so this does not exclude every report in the public
   raw training corpus. Use official execution matching, reported
   answer sensitivity and company-cluster uncertainty.
3. Compare the original and span-complete quantity catalogs on those
   same 96 FinQA reports. Both arms use the same unadapted SSD 3B
   Q4 model, prompt and evidence. This tests whether the result from
   the five annotation-enriched cases translates to an unselected
   cohort. The precision and catalog comparisons share cases and
   should not be treated as independent samples.
4. Repeat the direct 3B/7B TAT-QA arithmetic comparison on 120
   new table contexts, excluding the original 16 and follow-up
   40 table IDs. The official exact-match scorer remains primary.
   Use paired gains/losses and report compute and memory.

The FinQA cohort SHA-256 is
`20771d2617431fd7042cfa1103f80efb5eda2b17ec8df8162ec84929b485004d`.
It was selected by the fixed hash rule with one question per report.
Exclusions include the archived Windows verifier, reject-both,
natural-pair, adapter, capacity, precision, catalog, length and
retrieval replication cohorts. They also include the FinQA dev24
and dev100 packet files, the earlier natural 8 GB fitting,
selection and diagnostic packets, and the 16 GB public packets.
No scoring result affects inclusion.

The TAT-QA cohort SHA-256 is
`511eab7a44064fdb903a38f41fd6b057cd096067b5ca3746f13dad59dbd9b8a8`.
Both larger cohorts and the 21-candidate replay are frozen before
the extended runs. The smaller numerical studies are pilots.
All conclusions remain specific to the studied recipes and
benchmarks. The 16 GB tier remains gated.

## Frozen cross-benchmark adaptation and review

A separate set of 72 TAT-QA arithmetic contexts excludes all
176 contexts used or frozen in the previous TAT-QA comparisons.
Frozen SHA-256
`e22b617e9d483d6721399e7c471627fbe157bd642b47e39753b56ffef710dff7`.
Compare the same 3B cited-program drafter with and without the
FinQA common actor adapter. Use the same scale schema and
evidence. Score the adapted draft before review and again after
the existing control critic's binary gate. Only PASS delivers.
Generation has a 768-token ceiling and review adds up to 192.
Both roles are sequential under the Windows cap.

Primary analysis compares unadapted and adapted exact matches,
then reports how many correct and wrong candidates the gate
retains. Use the official TAT-QA scorer with no FinQA label
substitution. This tests transfer to a second task representation.
No corpus-level company-year mapping is available between the
two benchmarks, so source overlap across them remains unverified.
Use `tier8_windows_tatqa.py run --actor-adapter ... --critic-adapter ...`
with the common actor and matched control critic artifacts.

## Completed preliminary controls

Forcing the annotated operation count in the 16-report
diagnostic scored 3/16 official matches versus 1/16 for its
unrestricted control. The three correct reports are exactly
the three recovered by the earlier model-predicted count.
This gold-informed control therefore adds no correct question
over predicted-count planning on this slice. It does not show
that operation counts are always sufficient, and it uses no
gold operands or answer values.

The resident probe loaded two separate 3B Q4 workers with the
actor and control critic adapters. Both answered a short
loopback request while both remained resident. Peak shared
worker commit was 5.26 GB and sampled worker-plus-controller
RSS was 4.81 GB, with no observed cap breach. This establishes
fit for a short inference probe under the shared 6.1 GB job.
It does not measure sustained workload memory, paging, or
end-to-end accuracy. The raw samples and summary are in the
extended evidence directory.

## Resident workload follow-up

Use the same 21 frozen narrow-evidence reports as the critic
transfer replay, but generate and review each candidate while
both adapted roles remain resident. This checks sustained
resource feasibility and end-to-end delivery. Both local
workers use one 4,096-token slot, CPU only, a shared 6.1 GB
job limit and sampled 6.4 GB guard. The JSON-constrained chat
endpoint records actual completion tokens, prompt tokens,
and elapsed time per stage.

Use `tier8_windows_resident_probe.py --cohort` and score the
ledger only if the frozen cohort and resource trace complete.
The earlier Windows CLI replay uses a different prompting
entry point and frozen candidates. Any accuracy difference
between it and this run combines prompt/runtime and drafting
differences with residency. This is a workload preflight,
not a matched residency-only causal comparison.

The 21-report workload completed with both workers alive.
The actor produced six official matches (five reported
matches). The gate delivered five correct and four wrong,
with 12 withheld under either metric. Median combined request
time was 22.5 seconds. Sampled worker-plus-controller RSS
peaked at 5.85 GB. The job peak counter read 6,100,828,160
bytes versus the 6,100,000,000-byte configured limit. The
actor server logged a failed prompt-cache allocation and
reduced its cache limit before continuing. The peak counter
does not resolve how many bytes the failed allocation actually
committed. This is a workload completion with a cache fallback,
and provides no evidence of headroom at default cache settings.
[Windows job memory limit](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)

Repeat the same frozen workload with `--disable-prompt-cache-ram`,
which passes `--cache-ram 0` to both llama.cpp workers. Keep
context, adapters, job limits, requests and scoring unchanged.
Record memory peaks, allocator failures and paired answers.
Run after the benchmark comparisons if time permits.
[llama.cpp b12202 server options](https://github.com/ggml-org/llama.cpp/blob/b12202/tools/server/README.md)

With the RAM prompt cache disabled, both workers completed all
21 reports and logged zero prompt-cache allocation failures.
The job peak counter fell to 5.264 GB and sampled combined RSS
fell from 5.852 GB to 5.013 GB. The peak counter now leaves
0.836 GB below the configured 6.1 GB limit on this workload.
Every draft, verdict and delivery decision matched the
default-cache run. Median request time was 22.1 seconds
versus 22.5 in the earlier session. This is resource evidence
for the specified context and workload on the current Windows
host. Paging and whole-machine operation on 8 GB RAM remain
unverified. See `resident-no-cache-summary.json`,
`resident-no-cache-comparison.json` and the memory trace.

## Matched FinQA output-format control

On the frozen 96-report FinQA cohort, run the same unadapted
7B Q4 checkpoint with two output formats. The direct arm emits
brief arithmetic, a number and a unit. The program arm emits
source-bound executable operations and a unit. Both use the
same evidence, unit choices and 768-token output ceiling.
Report the shared reported-answer score and official execution
matching for the program arm separately. FinQA's official
program evaluator is not applied to direct text answers.

For a secondary decision rule, accept the program only when
the independently generated direct number agrees under the
existing frozen unit conversion and numeric tolerance. This
shares one checkpoint and source packet across arms. Errors
can correlate. Report correct, wrong and withheld separately.
The format comparison reuses the frozen 96 reports from the
precision and catalog work and is not an independent benchmark
sample. The study runs under the 6.1 GB worker job limit.

### FinQA output-format results

Both 7B formats delivered an answer on all 96 reports. Under
the shared reported-answer metric, direct scored 35/96 and
program scored 20/96. Direct alone matched 21 reports and
program alone matched six, for a paired difference of 15.6
percentage points (two-sided exact McNemar p = 0.00592 at
the report level). Median time was 32.0 seconds for direct
and 48.9 for programs. Both used about 5.44 GB peak job
commit. The agreement gate delivered three correct and two
wrong, and withheld 91. That gate lost 17 of the 20
reported-correct programs.

The unmodified official execution match count was 1/96 for
programs. A separate audit added a fixed divide-by-100 step
only to programs declaring percentage points, then reran
the same evaluator. This recovered 18 official matches,
raising the unit-converted sensitivity score to 19/96.
All 18 were already correct under the reported metric.
One additional reported-correct program had a percent label
and a conflicting official execution value. The original
official score remains available, and the sensitivity
analysis makes the unit convention explicit.

The format difference was 23/53 versus 19/53 on percentage
labels and 12/40 versus 1/40 on other supported numeric labels.
Three references were outside the supported reported-answer
syntax and neither arm received a match on them. These
subgroups are descriptive. The direct advantage is for this
task and shared answer score. The program arm also provides a
cited execution trace that the direct arm does not supply.

See `finqa-format96-summary.json` and
`finqa-format96-metric-sensitivity.json` in the extended
evidence directory. The original outputs and official scores
are preserved.

## Gold-informed operand-choice diagnostic

Compare the unadapted SSD 3B Q4 drafter under its ordinary
causal grammar and a grammar whose source IDs are restricted
to values used by the annotated program. Both receive the
same complete catalog in the prompt and the same evidence,
instructions, unit options, 768 generated tokens and native
Windows cap. The restriction retains every original catalog ID
matching an annotated source value. It does not disclose which
equal-valued cell is intended. Constants, operators, legal
intermediate references and the one-to-eight step range remain
available. Only the output grammar changes. The contrast
measures the effect of ruling out other numerical operands,
which can also block valid alternative formulas.

The diagnostic includes all 15 remaining eligible reports
after the named FinQA exclusions above and the 96-report
cohort. Eligible reports have an executable reference that
matches the official score under the same original catalog,
at least two distinct cited numerical values in the reference,
and a strictly smaller masked catalog. Selection does not use
the drafter's outputs. It is an enriched diagnostic, with
limited sample size and no claim of population-wide accuracy.

Cohort SHA-256
`737eea62bb15d17abf5df7b041a742d653d2d29380e0f5e2edb346017d4debec`.
Gold mask SHA-256
`b6b01a55f9d718b685d393148592ef16e415183a8f2d12a16fb971b4975548be`.
Run `tier8_windows_natural_pairs.py run --oracle-operands ...`
without an adapter and with `--job-commit-limit 6100000000`.
Score all paired official execution and reported-answer outcomes
against the frozen cohort. This is an answer-key intervention,
outside the deployable accuracy comparisons.

### Operand-choice diagnostic results

All 30 drafts executed. Both conditions scored 0/15 under
official execution and reported-answer scoring, despite an
executable official-match reference on every report. The
median number of selectable source IDs fell from 23 to two.
Both arms used 11,542 prompt tokens. Median draft length fell
from eight operations to three, and median time from 23.1 to
19.7 seconds, with the same approximately 2.77 GB peak job
commit.

With the mask, eight final graphs contained all distinct
reference source values, versus two without the mask. All
eight still produced wrong answers. A correct earlier
endpoint existed in three masked drafts and one control
draft. Restricting operand values reduced extra calculation
and improved reference-value coverage, yet left formula
construction and endpoint selection unresolved on this
cohort. The zero scores leave little room for a precise
effect estimate. These are gold-informed diagnostics on
15 eligible reports, and the control and masked score
distributions provide no evidence of accuracy equivalence.

See `finqa-operand-oracle-summary.json` and
`finqa-operand-oracle-cases.jsonl` in the extended evidence
directory.

### Operation-structure diagnostic

On the same 15 reports, compare two drafts with the same
gold-informed operand mask. In the second arm, the grammar
also fixes the operation sequence, constants, operand types,
intermediate references, and final endpoint from the annotated
program. Source-ID slots remain open across the full masked
menu and the model still chooses the display unit. Both arms
receive the original unmodified prompt and full catalog. This
supplies a large part of the solution, so the contrast only
measures what remains after providing the reference structure.

Shape SHA-256
`6896f0774bc6019af11b31fcd31a71c3845a532d9de4e6e056ff3f087a8536a5`.
Use `run --oracle-operands ... --oracle-shape ...` under the
same Windows worker limit. This is a follow-up on the same
reports and provides no independent sample of method accuracy.

With both arms using the operand mask, the operation scaffold
raised official matches from 0/15 to 10/15 and reported-answer
matches from 0/15 to 7/15. All drafts executed. There were no
regressions under either metric. Median time fell from 20.1 to
13.9 seconds and both arms peaked at about 2.77 GB of worker
commit. The structural intervention fixes several variables
together. This comparison does not attribute the effect to any
one of operation count, operation type, constant placement,
dependency edges, or endpoint choice.

### Operation structure without the operand mask

Complete the two-by-two diagnostic by repeating the shape
comparison with the original unrestricted catalog in both arms.
Use the same 15 reports and operation structures. The first
arm repeats unrestricted drafting. The second fixes the shape
while leaving all original source IDs eligible in every source
slot. Run `--oracle-shape ...` without `--oracle-operands`.
This separates the contribution of the scaffold from the
shortlist on these cases. Both remain answer-key interventions.

With the unrestricted catalog, the scaffold raised both scores
from 0/15 to 4/15. All four correct reports remained correct
with the operand mask. Adding the mask to the scaffold recovered
six additional official matches and three additional reported
matches. The mask on its own recovered none. Both repeated
control arms reproduced their saved plans on all 15 reports and
all 30 scaffolded drafts obeyed the frozen operation structure.

The remaining five official failures with both constraints
assigned at least one source slot a different numerical value
from the reference. Three other programs matched official
execution but declared percentage points for a fractional
result and failed reported-answer scoring. The pattern identifies
separate limitations in constructing the calculation, assigning
values to its slots, and labeling the output unit. The fixed
scaffold supplies the annotated calculation and cannot establish
an accuracy gain for a learned planner. The 15 reports are an
enriched diagnostic sample and both unconstrained scores are at
the floor. See `finqa-shape-oracle-summary.json` and
`finqa-shape-unmasked-summary.json`.

## Research conclusion

Candidate generation is a measurable limitation even where a
correct annotated program can execute from the available evidence.
On 82 of 96 FinQA reports, both matched 3B quantizations had an
executable reference witness and each still missed 80. The
operand and structure controls show where performance recovers on
the enriched diagnostic. Evidence expansion, denser catalogs,
and Q8 weight quantization did not yield a reliable accuracy gain
on their broader paired comparisons. The result is strongest as
a mechanism study alongside the original comparison.

The 7B direct model is a stronger comparator on the 120-context
TAT-QA replication under the same Windows job budget. At fixed
7B capacity, FinQA favored direct output under the common
reported-answer metric, while the TAT-QA point estimate favored
cited programs with substantial uncertainty. Program traces
provide provenance, and the answer-only results depend on the
benchmark and scorer. The critic reduces some wrong deliveries,
withholds some correct drafts, and accepts wrong answers in the
transfer and resident workloads.

Disabling the resident RAM prompt cache yields the clearest
engineering improvement. The two adapted roles ran all 21
reports with the same outputs and lower measured peak job
memory. These experiments use application-level limits on a
16.39 GB Windows host. They leave physical 8 GB operation and
paging unverified. The Windows continuation stays at the 8 GB
tier. A deployable, evidence-only generation improvement would
need an independent paired test against the stronger direct
baseline before advancing to the 16 GB tier.
