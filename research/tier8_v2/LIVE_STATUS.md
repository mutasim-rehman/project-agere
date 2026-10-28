# Research checkpoint — 8GB closure and tier handoff, 28 October 2026

**All queued8GB evaluations and both secondary paired audits are complete.**
The final reasoned/full-repair crossed SAS delivered9 correct/10wrong/33withheld
on52 cases; matched control9/20/23, original9/24/19. Raw delivered correct changes
11→10 versus matched control: the candidate still fails both-metric adoption.
No novel-method superiority is established. The portable runtime and real
SAS/MAS engineering workflow/replay passed; the higher-tier prospective protocol
is sealed separately. These are not completed16/32GB model evaluations.

[Offline tier commands and limits](../../LAB_TIERS_OFFLINE.md) ·
[Prospective tier protocol](../lab_tiers/PROTOCOL.md).

| Completed result | Reported correct/wrong/withheld |
|---|---|
| SAS original, selection52 |8 /25 /19|
| SAS matched control, selection52 |8 /23 /21|
| SAS crossed, selection52 |10 /16 /26|
| SAS control, reserved49 |8 /20 /21|
| SAS crossed, reserved49 |9 /20 /20|
| MAS control, reserved49 |4 /17 /28|
| MAS crossed, reserved49 |4 /9 /36|

SAS selection versus original has an exploratory error-reduction interval excluding
zero, but the large error reduction does not repeat in the reserved matched pair.
MAS reserved raw results are8/13/28→7/6/36: one lost correct delivery, so candidate
adoption still fails. Keep both metrics; no architecture winner/equivalence claim.
[Latest direction and hypothesis audit](RESEARCH_DIRECTION_AUDIT_2026-10-27.md) ·
[Reconciled completed evidence](evidence/research-direction-audit-20261027-01.json).

The control-SAS full replay also finds two rejected numerically correct drafts
repaired into wrong accepted answers, both in one report;19.1 minutes extra
recorded stage work and no correct-delivery gain. This is a conditional failure
finding, not a universal or first-use claim. [SAS detail](MATCHED_SAS_SELECTION.md) ·
[MAS detail](MATCHED_MAS_SELECTION.md).

## Scope and next-step recommendation

Original headline: smaller FP16 resident MAS versus larger Q4 SAS, **16 GB primary**.
Current redevelopment uses Q4 MAS/Q4 SAS numerical QA and is supporting evidence,
not a direct test of every original precision/task claim. Stop expanding8GB
features, finish the two queued prompt checks, reconcile the prospective tier
matrix/tasks/precision/adaptation/metrics, then freeze and prioritize16GB.
The current host has15.44GB RAM;32GB validation needs suitable hardware.
No live job stopped or restarted, no larger-tier job launched by this review.

Header/materialization and catalog-only variants remain unadopted offline fitting
prototypes (41→45/73 reference mapping); no neural QA gain. Do not automatically
launch them merely to force novelty before moving tiers. Training used10.5GB
allowance, distinct from6.4GB deployment. Shared-backbone serving parity is a
separate two-prompt engineering result, not used in current natural MAS.

One-shot user service agere-matched-study-02-20261027, PID90142/create-time
1793071505.0, was verified live with actual inference children during this review.
It recovered the original metadata-only interruption without repeating completed
model jobs. Check real service/PID/state before reporting future progress.
Raw datasets/weights/logs/full paired audits stay on the authorized SSD;
code, aggregate evidence and decisions are pushed for remote inspection.
