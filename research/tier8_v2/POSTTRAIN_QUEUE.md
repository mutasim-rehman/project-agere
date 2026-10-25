# Frozen critic post-training queue

Plan02: `/run/media/mutasim/Data/AGERE/runs/tier8_posttrain/critic3b-posttrain-02/plan.json`.
Copy: `evidence/critic3b-posttrain-plan-02.json`. Ten jobs,54 frozen inputs.
Plan01 was superseded before launch after dependency coverage was tightened.

The controller waits for the existing training PID/create-time/output identity.
It requires all3140 examples,393 updates, finite validation and unchanged saved
adapter/base/input hashes. It never restarts or retrains on observation timeout.

| Order | Required result |
|---|---|
| 1 | Full trained critic converted to GGUF, purpose/hash/tensor checks |
| 2 | Reversible scale0→1→0 actual application proof |
| 3–4 | Plain and applied3B binary reviews on identical controlled inputs |
| 5 | Paired report-group analysis of acceptance and discrimination |
| 6–7 | Plain and applied3B critics on identical adapted-actor QA, reused dev24 |
| 8 | Exact initial-draft/critic-prompt equality guard and paired QA analysis |
| 9 | Offline unit sensitivity, preserving recorded primary results |
| 10 | Recover original unadapted MortarBench90/FRAMES100 baseline queue |

The complete queue+subprocess tree is sampled at0.2s, under6.4GB decimal RSS
and1GB host reserve, retaining each runner's own memory evidence. A1.25GB launch
headroom allowance prevents the inner runner from silently lowering the common
cap. This is a monitored simulated8GB tier, not physical8GB or hard-cgroup proof.
Each stage has its own process group and immutable output/log path. Failure of
any identity/hash/runtime/completion/memory gate stops later stages. No retries
or overwrite. JSON analyses and all raw outputs remain on SSD.

Rich review remains a separate earlier control; the queued critic effect uses
matched binary protocol before/after adaptation. Both cases share the same actor,
inputs, code, model hashes, token allowances and cap. A changed actor draft
invalidates causal attribution to its critic. UNKNOWN is nonacceptance, not a
proof that a program is incorrect. Controlled mutations are weak training-
validation labels, not natural errors or independent semantic adjudication.

The natural24 cases are reused development. The100 additional reports remain
uninferred. Original external baselines use original unadapted models, local
exploratory scoring and partial JSON/XML retrieval; they are not an official
complete MortarBench replication or an adapted-system confirmation. Preserve the
26 original cases and report interrupted/recovery timing segments separately.

No queue completion implies novelty or completion of the research goal. Comparable
SAS adaptation, stronger semantic validation, a useful differentiated mechanism
and publication-quality confirmation remain required.209 tests passed at freeze.
GitHub progress is a dated snapshot; live journal/state/memory files are on SSD.
