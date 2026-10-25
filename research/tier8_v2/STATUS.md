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

Live verifier trial: data/verifier3b-sequence-01.json, 73 frozen inputs; session
68919, controller PID 312283, monitor 312285, worker 312318. Four persisted cases
were observed with 4.818 GB sampled peak so far; quality remains unassessed until
all 24 finish. Launch evidence: evidence/verifier3b-launch-01.json. Do not duplicate
or restart on observation timeout; keep its code/data frozen until terminal.

## External evaluation transition, 25 October 2026

The 3B verifier trial completed: 11/24 draft successes, zero delivered answers,
24 withheld; peak combined RSS 4,820,619,264 bytes. This is a negative delivery
result, not improved reliability at useful coverage. The live-trial text above
is historical. All 24 cases and terminal summary are preserved.

User explicitly authorized the mounted SSD /run/media/mutasim/Data/AGERE.
New external baseline queue: scripts/tier8_external_eval.py, all 90 prepared
MortarBench questions and all 100 FRAMES control questions, original SAS 7B Q4
and distinct resident MAS 1.5B/0.5B/0.5B F16, CPU, same fixed host-adjusted
6.4 GB ceiling, 4096 context, maximum 2048 generated tokens per case.
MortarBench uses shared label-blind lexical retrieval with a 1700-token source
ceiling and local typed exact scoring, not official benchmark scoring.
FRAMES is closed book with original strict exact match plus a separate
punctuation-normalized sensitivity. These are exploratory external baselines,
not an adapted-system confirmation or a publication novelty result.
Outputs belong only on the SSD under runs/tier8_external/.

External queue is confirmed in actual inference, not merely planned: 3 MortarBench SAS cases persisted at this observation; sampled peak 5.18 GB under 6.4 GB. Run root: `/run/media/mutasim/Data/AGERE/runs/tier8_external/external_baselines_20261025_01`. Controller321561 / session46979. Full queue remains active; do not restart or edit the frozen runner. Launch pointer: evidence/external-evaluation-launch-01.json.

## Latest authoritative observation — supervisor audit

External queue INTERRUPTED: 26/380 case-arm evaluations saved, 14/26 local MortarBench
SAS matches, no completed arms or live evaluation process. Cause unknown; no
terminal summary. Original running SSD manifest backed up, interruption observation
saved. Do not repeat earlier live-status/ETA claims. See evidence/external-evaluation-
interruption-01.json and SUPERVISOR_UPDATE_2026-10-25.md. Raw outputs remain on SSD.

## Recovery and matched critic audit — latest

Recovery563f259 is implemented and175 tests passed, but its actual launch was
REFUSED by the original cap+reserve memory preflight. Available RAM6.5–6.7GB,
required7.4GB. No continuation worker is live;26 original cases remain preserved.
The host rebooted after the original run's last saved sample. Exact initial
termination cause remains unknown. Recovery uses the unchanged original worker
and separate immutable segments; no prompts/scoring/retrieval changed.

Offline critic audit now proves24/24 identical draft plans and verifier prompts.
0.5B critic is almost uniformly permissive;3B rejects all24 and emits repairNONE
with nonPASS checks in all24. Next critic work must establish balanced train-only
program discrimination and instruction consistency before renewed delivery gating.
Audit: evidence/matched-critic-behavior-audit-01.json. No new novelty claim or
accuracy gain follows from this diagnosis. Goal remains active.

## Active independent experiment — critic protocol probe

Full external queue remains stopped for insufficient host headroom; no user apps
were closed. A separate train-only component experiment is running from unchanged
source commitb6243fa, detached controllerPID23678 (verify identity/live state before
acting). SSD root: runs/tier8_critic_probe/critic_protocol_validation12_01.
12 report groups,24 reference/mutated programs, rich/binary protocols,96 calls
across sequential native0.5B and3B Q4 critics. Single-critic fixed cap5.453GB;
this is not a full MAS run or full-arm evaluation. Pinned legacy model copies are
now also on SSD. Launch metadata: evidence/critic-protocol-probe-launch-01.json.

0.5B completed48 calls at1.472GB peak: rich accepts6/12 references and7/12 wrong
mutations; binary accepts11/12 references AND11/12 wrong mutations. Higher acceptance
is not useful discrimination. 3B was still live at the last observation; do not
interpret partial3B output or restart it. Full paired analysis waits for completion.
184 tests pass, including report-cluster analysis and complete-pair discrimination.

## Latest authoritative result — critic probe complete

Detached critic probe finished96 calls, both profiles memory-valid.0.5B peak1.472GB,
3B2.376GB. Neither protocol/critic correctly separates either member of any of the
12 reference/mutation PAIRS (accept reference AND reject mutation).0.5B rich:
6/12 reference accepts and7/12 mutation accepts; binary11/12 and11/12.3B rich
FAIL24/24; binaryUNKNOWN24/24. Simpler protocol does not solve discrimination.
Aggregate: evidence/critic-protocol-validation12-results-01.json. Raw SSD run and
all hashes are preserved.184 tests pass. No new accuracy/novelty claim.

Full external queue is still stopped for headroom, not restarted; memory after the
probe was7.27–7.38GB available against7.4GB required. Original26 cases preserved.
Goal remains active. Next verifier development must address actual discrimination,
and SAS still needs comparably strong adaptation before architecture claims.

## Latest critic adaptation milestone

Corpus02 on SSD:3140 train /382 validation examples, balanced source/mutation
pairs;414/49 distinct report groups. Full HF/GGUF parity passes all3522 rows.
90 oversized pairs excluded together; operation959/operand802 retained mutations.
Legacy pinned NF4 training base/configs now also hash-verified on SSD. Raw data
and new weights/logs stay SSD; small provenance files are in evidence/critic-*.

Actual2-update critic fit passed (1023 tokens,504 changed tensors, GPU allocated
3.861GB/reserved4.226GB). Evidence: critic3b-fit-01.json. No trained critic quality
or adaptation accuracy result yet.191 tests pass. Trainer supports explicit role,
parity/data/base manifests and SSD artifacts; critic cannot silently load as actor.
Full epoch and subsequent application/QA evaluation remain outstanding at this
checkpoint. Goal remains active, novel useful contribution still unproven.

## Latest authoritative live state — full critic epoch

Full critic training is ACTUALLY RUNNING, detachedPID26043, launched fromb89d297.
Output SSD: runs/tier8_critic_training/critic3b-train-01; controller log:
runs/critic3b-train-01.log. At an observed checkpoint21/393 optimizer updates,
168 training examples had completed; GPU allocated3.912GB/reserved4.228GB.
Launch/observation pointers are in evidence/critic3b-training-*.json. Revalidate
PID/create-time and events; do not duplicate/restart on observation timeout.

Keep trainer, encoded corpus and pinned weights frozen until terminal. CPU
inference cannot overlap this training job. Validation loss, conversion,
role-specific application proof and actual verification gains are still pending.
This is established-method baseline strengthening, not a novelty claim.191 tests
pass. Full external recovery still waits for headroom and serialized model work.

## Prepared while critic trains

Critic-specific runtime/proof and binary review control implemented,200 tests at
that milestone. They have NOT yet been exercised with the unfinished adapter.
Binary review preserves UNKNOWN and cannot claim localized repair feedback.

Broader FinQA development packets are frozen on SSD at
`datasets/tier8_v2_finqa/dev_report100_01`:100 questions/100 reports, excluding all23
prior evaluated/planned reports and prepared SFT groups. Audit covers24 generation
manifests and saved cases. Same lexical retrieval; no model calls or answer-based
selection. Evidence: finqa-report100-development-selection-01.json. Explicit SSD
evaluation-source copy must match the pinned development hash.204 tests now pass.
This is broader development, not a sealed test or confirmed generalization.

User has freed memory and authorized continued scoped research with GitHub updates
for remote checks. Recheck actual headroom after the current GPU job exits; keep
model work serialized and source/data frozen. No new external accuracy claim yet.
