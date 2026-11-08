# 8 GB candidate generation follow-up

## Retrospective matched comparison

Run `node scripts/tier8_candidate_audit.cjs` from the repository. It checks
case pairing and recomputes stage outcomes from the two saved dev24 case
ledgers. The existing paired audit records identical public evidence packets
and zero truncated stages. These are 24 development cases from 23 reports.

- Without the drafter adapter, 24 refused and zero produced executable candidates.
- With the adapter, all 24 produced executable candidates. Under reported-answer
  scoring, 11 were correct before review, one correct candidate was withheld,
  and final delivery was 10 correct, 11 wrong, and three withheld.
- Under raw execution scoring, nine candidates were correct, all nine were
  delivered, and 12 wrong answers were delivered. Neither score is official FinQA.
- Historical sampled process-tree RSS was 3.82 GB without and 3.90 GB with
  the adapter against the 6.4 decimal GB ceiling. This comparison supplies
  development evidence that candidate generation can recover at 8 GB.
  Adaptation changes more than refusal policy, and 11 of 21 reported-answer
  deliveries were wrong. The result does not qualify the system for escalation.

## Prospective protocol draft

Use a matched design: each condition processes every eligible question in
the same report cohort. Use the historical runs for diagnosis, fresh
development reports for configuration selection, and a sealed report-disjoint
confirmation cohort. Record overlap with prior demonstrations, fitting,
and evaluation before generating any outcomes.

1. Validate translation of saved programs against the pinned official FinQA
   evaluator. Document unsupported operations and withholds explicitly. Report
   official execution accuracy over all cases and preserve both historical metrics.
2. Run an unadapted baseline and a forced-attempt variant using the same 3B
   checkpoint, evidence, budgets, and verifier. Change the drafter instruction
   and allowed decision only. Compare correct candidates before the gate.
3. If testing a handoff, compare the same selector-enabled system with its
   suggestion passed versus masked. The historical matched pair already has
   selector disabled. Keep selector execution, drafter allowance, evidence,
   and verifier fixed for this contrast.
4. Use the adapted drafter as the existing competitive alternative. Only
   add a drafter-heavy allocation if it fits the common ceiling and addresses
   a remaining capacity question. Log precision and model size as properties
   of the recipe.
5. Preflight each arm under a Linux cgroup with `memory.max=6400000000`
   and `memory.swap.max=0`, with the same 2,048 generated-token ceiling.
   Record cgroup memory peak and events separately from sampled RSS.
   Retain incomplete arms and resource failures in the run record.
6. Freeze the primary contrast before opening confirmation data. Evaluate
   correct candidates, correct and wrong delivery, and withholding on all
   assigned questions. Use paired report-cluster intervals. Before sealing
   the run, set the minimum useful gain and maximum acceptable error increase
   from the downstream cost of wrong delivery and human review. Size the
   confirmation cohort to resolve those margins.

Hold 16 GB work until an 8 GB result reproduces a practically meaningful
improvement on the untouched cohort, meets the prespecified wrong-delivery
margin, and completes under the enforced resource limits. The retrospective
comparison alone does not meet that gate.
