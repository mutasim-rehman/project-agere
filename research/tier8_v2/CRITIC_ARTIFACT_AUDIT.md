# Question-blind critic controls

26October2026. Measured development diagnosis, not a new algorithm, neural
shortcut-use proof, fresh validation or established publication contribution.

Fixed shallow decision trees fit only critic TRAINING reports. Features consume
only the compiled candidate program: operation/step counts, constants, source and
step-reference counts and literal magnitudes. They receive no question, source
text, source case ID, mutation label, tokenization or neural output. Labels are
the existing weak PASS/FAIL annotations. Greedy Gini splits, depth1 length-only
stump or depth3 program-feature tree, minimum leaf32; no hyperparameter search.
The audit was motivated by prior results; aggregate neural outcomes were already
known. Do not describe it as prospectively blind to the project's earlier results.

## Held-out-report synthetic classification

Both corpora have the same3140 training and382 validation rows, with49 validation
report groups disjoint from fitting. Each validation set has191 references and191
mutations; constant majority prediction scores50%.

| Train corpus / fixed classifier | Original validation | Extended validation |
|---|---:|---:|
| Original / length stump |50.0%|50.0%|
| Original / depth3 program tree |72.0% (275/382)|62.0%|
| Extended / length stump |50.0%|58.1%|
| Extended / depth3 program tree |67.5%|77.2% (295/382)|

The extended tree first splits on presence of CONST100. On extended validation,
it rejects all73 scaling negatives but also41/191 valid references; it accepts
12/20 bypass negatives. Even the length stump rejects all73 scaling negatives,
while rejecting77 valid references. Therefore rejecting that mutation family
does not by itself establish financial understanding. This is a shortcut
opportunity, not evidence that the neural model actually relies on it.

## Same previously selected controlled24

On the old12-report controlled probe, the original-trained tree classifies17/24
correctly and separates both members of5/12 report pairs; extended-trained tree
16/24 and4/12. The existing trained neural critic achieves23/24 and11/12. Probe
reports do not overlap tree-fitting reports. These cheap controls do not explain
away the neural result, but23/24 remains a small artificial-mutation diagnostic.

## Offline gate replay on reused natural24

Both trees use the exact saved adapted-actor drafts, with no changes or repairs.
All24 programs support the feature extractor; none is silently excluded. Fitting
reports do not overlap these23 natural report groups. Trees and thresholds were
fit BEFORE replay; natural scores enter only outcome computation. This is a gate
component replay, not another end-to-end measured model run.

| Gate | Reported correct / wrong / withheld | Raw correct / wrong / withheld |
|---|---|---|
| Original-trained structure tree |5 /8 /11|4 /9 /11|
| Extended-trained structure tree |5 /5 /14|4 /6 /14|
| Existing original-trained neural critic |11 /4 /9|9 /6 /9|

The neural gate descriptively improves on both shallow structure controls under
both metrics on these same drafts. This does not prove question understanding,
exclude richer shortcuts or establish out-of-sample superiority. All natural24
results are repeatedly used development evidence; numerical reference limitations
remain. The100-report evaluation is still required. Apply the same already-fit
four trees there without feature, depth, threshold or policy selection.

## Reproduction and evidence

Code: `scripts/tier8_v2_critic_artifact_audit.py`. Canonical raw output on SSD:
`runs/critic-question-blind-artifact-audit-05.json`. Earlier01–04 development outputs
are preserved, not independent replications. Run05 clarifies prior-outcome
awareness and fixes negative-family labels on the controlled probe; fitted trees
and validation scores exactly match02. Four targeted CPU checks pass.

[Aggregate evidence and frozen fitted trees](evidence/critic-question-blind-artifact-audit-01.json)
bind the exact datasets, source, saved neural files and canonical raw output.
No NN calls, active trainer modifications, new training data or queue changes
were involved. The fitted trees are additional cheap baselines, not a proposed
novel verifier or a reason to replace the stronger neural gate.


26October2026 NN qualification: the fully adapted shared7B SAS scores31/32 exact
labels and7/8 exact quartets in the fixed8-report training-source crossed probe.
Greedy question-switch decisions change correctly15/16 times with evidence/program
held fixed. This directly limits the earlier artifact interpretation: program-only
shortcut availability does not show this model relies only on that shortcut.
No held-out natural QA inference follows. See [baseline discovery](CRITIC_BASELINE_DISCOVERY.md).
