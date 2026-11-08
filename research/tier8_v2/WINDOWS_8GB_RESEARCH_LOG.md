# Windows 8 GB research continuation

Window opened at 21:58 Pakistan time on November 8, 2026. The
three-hour window closes at approximately 00:58 on November 9.
All studies use native Windows CPU inference. The 16 GB tier
remains gated. Commits are pushed to the current research branch.
The host is Windows 11 on a Ryzen 5 8645HS with 16.39 decimal GB
of physical memory. The 8 GB tier is simulated by the worker
limits, not by restricting the whole host to 8 GB. The current
Windows CPU differs from the host in the historical study, so
elapsed times should not be compared across those hosts. Exact
runtime and package metadata are in
`evidence/windows-endpoint-study/windows-environment.json`.

The research question is which intervention raises correct
candidate or answer delivery under the 8 GB tier, and where
generation or verification fails. Candidate-only results cannot
be counted as deployment delivery.

1. [Endpoint study](WINDOWS_ENDPOINT_STUDY.md). The retrospective
   selector made no changes. Prospective count planning yielded
   three recoveries and one regression across 16 paired reports.
2. [Retrieval and resource controls](WINDOWS_RETRIEVAL_AND_RESOURCE_STUDY.md).
   Wider evidence improved annotated coverage in the development
   screen and recovered three correct candidates on 16 test
   reports. A separate 21-report replication is frozen. The native
   process job commit guard passed an allocation and inference probe.
3. [Matched precision study](WINDOWS_MATCHED_PRECISION_STUDY.md).
   Both quantizations were derived from one F16 source. The
   evidence-only 24-report cohort is frozen.
4. [TAT-QA transfer check](WINDOWS_TATQA_STUDY.md). Direct and
   program output each scored 1/16 on distinct questions. The
   larger direct-model comparison is frozen at 40 contexts.
5. [Temporal rule and reference audit](WINDOWS_TEMPORAL_RULE_BASELINE.md).
   The rule failed to match any of its three report-disjoint
   test deliveries. The full consistency screen flagged 129 of
   1,100 eligible test references under the tested conventions.
6. [Trained critics](WINDOWS_TRAINED_CRITIC_STUDY.md). A matched
   replay and an independent 7B solve are frozen on the same
   sixteen naturally generated candidates.
7. [Catalog support](WINDOWS_CATALOG_SUPPORT_STUDY.md). The
   existing prototype made 28 additional annotated test programs
   numerically bindable. Five eligible reports form an enriched
   neural diagnostic.

After these comparisons, select a confirmation or mechanism
experiment based on observed paired gains and losses. Freeze any
new cohort before inference. Record wrong selections and resource
failures, and preserve unfavorable results alongside gains.

## Metric sensitivity on the shared 16-report pilot

Two reports have incompatible raw/reported labels under the
reference screen. A secondary analysis excludes them without
changing the primary result. Each intervention still recovers
three official execution matches with no losses across the
remaining 14 reports. This does not turn the shared cohort into
two independent studies. The two interventions are correct on
two of the same reports. The annotated execution oracle across
the two intervention outputs could answer five distinct reports
out of 16, including one reference-flagged case. A deployment
policy has no access to the oracle.

## Cross-study failure diagnosis

We replayed 100 saved draft records across five Windows
comparisons, including repeated questions and repeated controls.
An answer-key search found 15 wrong final drafts with an earlier
exactly correct endpoint. It found zero wrong final drafts on
percentage questions that could be made correct by multiplying or
dividing the final result by 100 alone. This separates the observed
endpoint problem from a simple final percent-conversion problem
on these specific drafts. It does not imply that units are
unimportant or that the draft records are independent observations.
The original scores remain unchanged.
