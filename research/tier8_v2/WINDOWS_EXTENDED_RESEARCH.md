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
