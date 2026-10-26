# Experimental shared-backbone specialist serving

This is baseline engineering, not the novel research claim. It addresses one
avoidable MAS cost before the common method is frozen: two role policies using
the same pretrained backbone currently retain two copies of the base weights.
The existing baseline deliberately does this to prevent adapter contamination.

`shared_role_models.py` instead retains one actual backbone and two independently
validated, fully trained native LoRA handles. Every call resets the token position,
clears ALL context adapters, activates exactly the requested adapter, and performs
a fresh prefill. No prefix/KV state is reused across roles. Native activation
failure leaves no active adapter and raises; no silent unadapted fallback.
Cleanup clears context references before freeing adapters. Calls must be serial.

This is established shared-backbone serving; see the existing
[LRAgent prior review](RELATED_WORK_MATRIX.md). Do not claim new role adaptation,
new cache sharing, agent independence, parallel execution or model quality gains.
Our implementation reuses no cross-role cache. Different learned policies still
share a pretrained base and can make correlated errors.

Both3B and7B pinned backbone names are parameterized. Actual preparation currently
uses the existing3B actor and3B critic only. A7B critic requires its own valid full
critic-purpose training artifact; the joint SAS adapter CANNOT be relabeled as an
independent critic. No7B role pair or serving gain is demonstrated.

## Evidence required before adopting it

The prepared `tier8_v2_shared_role_proof.py` first loads the existing two-instance
MAS reference, then frees it and loads the one-backbone backend. Under the same
4096 context and6.4GB complete-tree cap it compares actual full-vocabulary final
logits and32-token deterministic continuations on bound actor/critic training-
validation prompts, including repeated actor→critic→actor→critic switches. Maximum
absolute logit tolerance is1e-5, text and usage must match exactly. Every prefill
and generated token is recorded; raw vectors, logs and phase-specific sampled RSS
stay SSD. Failure preserves evidence; no blind retry. Test only after other NN
work is terminal and the shared hardware lock is available.

Three CPU activation-contract tests pass: no policy accumulation or cached prefix,
failure clears state without fallback, missing handles cannot alter active state.
Metadata preflight verifies the actual actor661/83-update and critic3140/393-update
epochs with finite validation. These are not native switching or memory results.
The NN proof is **prepared, not run or queued**. The frozen baseline queue remains
untouched. Run serving proof afterward, then a small full-case replay if it passes;
short continuation parity does not prove full natural QA equivalence.

Adopt this backend into the cross-tier base only after measured proof. Predeclare
per-tier backbone/adapter sizes and context budgets separately; do not add a new
switching or cache method only after moving to16/32GB. Memory savings, if measured,
are a known-method baseline improvement and cannot substitute for useful novelty.


26October2026 priority update: both ordinary critics are near the fixed crossed-
family ceiling, and the unchanged local pool has zero wrong-case rescue within
its four-check allocation even with perfect numerical selection. This redirects
attention from extra classifier/deduplication tuning to proposal quality and fair
model capacity under RAM constraints. The prepared3B serving proof is now a
next diagnostic AFTER the currently active8-job discovery queue completes.
[Plan02](evidence/shared-role-serving-plan-02.json) corrects the old plan01 reference
to a deliberately superseded10-job queue; the command, caps, source hashes,
prompts and parity conditions are unchanged. It is still NOT launched or queued.

If native3B parity/memory proof succeeds, investigate whether the saved backbone
memory can support a stronger same-budget MAS actor, with an explicitly labelled
role-adapter/shared-backbone variant. Such a7B experiment would require ACTUAL
separate critic-purpose training, fit/conversion/native application and serving
proofs before evaluation. It cannot reuse joint-SAS weights under a renamed critic
label. A same-base role study must retain the classic3B MAS, single-policy7B SAS,
matched task exposure/optimization controls, and trainable-capacity differences.
This is a conditional next research direction, not an implemented7B role method
or a new algorithm claim. LRAgent remains a close established serving prior.


The new `tier8_v2_shared_role_dispatch.py` can wait on the exact declared discovery
controller identity, then require its final successful state, ordered completion
of every job and independent result verification. All command/source/data inputs
are frozen and rechecked after waiting. It exec-replaces the waiter with the
unchanged proof runner, leaving no extra controller outside that runner's complete-
tree monitor. The proof retains its own hardware lock,6.4GB cap and fresh-output
checks. No retries/resume. Two targeted completion-gate checks pass. This dispatcher
adds no serving-policy feature or quality claim; launch status is recorded separately.
