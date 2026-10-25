# Research checkpoint — 25 October 2026

Goal remains active. A useful original method and publication-quality confirmation
are unproven. Implementation, known-method tuning and real adaptation have advanced;
an adapted QA gain on the reused development slice is now observed. Confirmation
and novelty remain unproven.

## Best completed development results

- SAS 7B Q4, 128-token analysis + two fixed demos: 13/24 reported-answer matches,
  13 correct deliveries, 5 wrong deliveries, 6 withheld; 8 raw execution matches.
- Trained MAS 3B + 0.5B critic, no analysis/demos: 11/24 matches, 10 correct
  deliveries, 11 wrong deliveries, 3 withheld; 9 raw matches; peak RSS 3.899 GB.
- Prior MAS 3B Q4 drafter + 0.5B F16 critic, 128 analysis/demos: 4/24 matches,
  3 correct deliveries, 1 wrong delivery, 20 withheld; 2 raw matches.
- Longer 256 analysis did not help: SAS 11/24 with 9 wrong deliveries; MAS 4/24
  with 10 wrong deliveries. Both ablations are complete. More table coverage also
  left SAS at 13/24. Exact cancellation feedback corrected no answers beyond plain
  retry; do not expand that negative pilot into a novelty claim.
- All are reused first-24 FinQA development results. Original rule-solvable synthetic
  and KYC suites are regression checks, not publication evidence. Test split unopened.

## Adaptation and actual application

- Valid source-binding corpus revision 02: 1653 train / 198 train-only validation,
  disjoint annual-report groups, excluding all development report groups. Revision
  01 has invalid persisted quantity-ID mappings and is superseded; never train it.
- Exactly 761 examples fit 1024 full tokens: 661 train / 100 validation. Official
  HF and GGUF token sequences/mask boundaries agree. Numerical source uniqueness
  is not semantic adjudication; annotation-consistency limitations are logged.
- Full 3B NF4 QLoRA epoch completed: 83 updates, 504 changed tensors, 14.967M
  trainable parameters, 1198 seconds. GPU peak allocated 4.051 GB / reserved 4.228 GB.
  Teacher-forced validation loss 0.03475 is not QA accuracy. Selective supervised-
  suffix logits preserve all context/targets and match full-loss gradients; the
  initial full-logit fit OOM and successful revised fit are both retained.
- GGUF conversion passed: 504 finite paired tensors, 59.90 MB F16 adapter. Training
  NF4 and deployment Q4_K_M are different quantizations, explicitly labelled.
- Real application proof 03 passed: scale 0 -> 1 -> 0 changes logprobs reversibly,
  zero-repeat drift 0, peak RSS 4.337 GB under cap. It proves effect, not QA gain.
- Runtime now validates trained adapter provenance/profile/hash and attaches it
  only to the MAS drafter (or SAS 7B when available). Actual case records include
  backend initialization. Original training sequence 02 is terminally complete.

## Runtime and current next experiment

CPU 8 threads, F16 KV, context 4096, 2048 generated tokens/case, sampled combined
parent+worker RSS cap 6.40 decimal GB on a larger host. This simulates an 8 GB tier;
physical 8 GB validation is still absent. Training resources are separate.

New prompt accounting matches completion special-token/BOS/EOS behavior and asserts
actual engine usage. Historical manual counts remain labelled estimates. Skipped
calls cost zero prefill. All 168 contract tests pass; tests do not prove QA quality.

Matched no-analysis/no-demo evaluation completed: unadapted 0/24 (all abstained),
adapted 11/24; V2 unit sensitivity unchanged. This establishes development
adaptation benefit, not novelty or superiority over best SAS (13/24). All paired
artifacts are in evidence/finqa-mas-3b-adaptation-*.

The weak 0.5B critic accepts 11 wrong answers. Next, test a 3B Q4 verifier under the
same caps and verify unchanged draft plans. No inference worker is currently live.

## Still required

- Measure actual adapted QA, wrong deliveries, withheld answers, cost and memory.
- Strengthen verifier and SAS, then test a genuinely useful mechanism against strong
  matched retry/tool baselines. Cell identities/partial binding domains exist but
  are not yet an empirically useful repair method or part of current model prompts.
- Broader development, fresh report-group confirmation and a second realistic task;
  original synthetic KYC/credit coverage remains insufficient. Close prior work is
  tracked in RELATED_WORK_MATRIX.md and NOVELTY_AUDIT.md.

All milestones are committed/pushed with DECISIONS.md and raw evidence. Model and
adapter binaries remain local/ignored with hashes. Redundant original F16 caches
and unused native 1.5B were reclaimed; restore the pinned source/native conversion
before any future 1.5B run. Native 0.5B and Q4 3B/7B remain available.
Leave the user-owned .GITIGNORE untouched. Push through the local askpass helper.

Larger-verifier control is implemented: optional 3B Q4 critic. A trained drafter
and plain critic have separate resident instances despite the same base file.
The next actual trial measures fit and delivery changes over all 24 cases and
checks draft identity against the completed 0.5B-critic condition. No new inference
has been launched at this exact source checkpoint.
