# Frozen higher-tier lab comparison: finance-deployment-lab-v1

This prospective specification reconciles the original memory-allocation question
with the actually available models/data. Execution is gated on completion and
paired audit of the two remaining 8 GB prompt runs. No new algorithm is introduced.

## Question and scope amendment

Compare resident, smaller F16 financial-QA specialists against one larger Q4_K_M
model under the same process-tree RSS and generated-token ceilings. **16 GB is
primary; 32 GB is a prespecified scaling check.** A 32 GB Ubuntu host simulates
the 16 GB deployment cap. These are resource-capped runs, not validation on a
physically separate 16 GB workstation. CPU is primary; the 10 GB GPU is unused.

The task is source-grounded numerical financial QA. Report both existing numerical
score conventions, correct/wrong deliveries, and withholding over ALL cases.
Do not label these as KYC/credit invention rate or conflict recall. Earlier
rule-solvable synthetic packs do not determine the paper winner.

The main arms use PRETRAINED checkpoints in both systems. There are no matching
trained 14B/32B adapters on the SSD; 7B adapters cannot be relabelled or applied to
them. Existing 8 GB adaptation findings remain a separate experiment. This is a
bounded deployment comparison, not a claim of optimal or equally extensive SFT.

## Fixed model and method matrix

| Tier | SAS | Resident MAS |
|---|---|---|
| 16 GB | Qwen2.5-14B-Instruct Q4_K_M | 1.5B F16 extractor + 3B F16 drafter + 0.5B F16 verifier |
| 32 GB | Qwen2.5-32B-Instruct Q4_K_M | 3B F16 extractor + 7B F16 drafter + 0.5B F16 verifier |

Model files, source revisions, sizes and SHA256 come from the existing Phase2
artifact manifest and are pinned in `configs/lab_tiers/protocol.json`. The runner
checks file type (F16 versus Q4_K_M), size and full hashes. No silent model fallback.
All declared MAS instances remain loaded; `use_mmap=False`, native KV state, CPU
only. There is no role-backbone sharing or sequential swap-mode substitution.

Both tiers use context8192, eight CPU threads, seed42, greedy decoding, and the
existing 2048 generated-token ledger. Same public evidence/retrieval, four-op
executor, compact quantity references, question-unit rules and causal grammar.
Fixed demonstrations are training-only. The existing MAS source-suggestion agent
is used; SAS receives the same evidence and reasoning opportunity. Agent call
counts and actual expenditure differ and are reported, not called compute-equal.

Prespecified profiles, run for BOTH arms at BOTH tiers:

1. **Primary:** existing128-token analysis + two fixed demonstrations, binary
   review, no repair. This is not claimed to be optimal for every checkpoint.
2. **Direct control:** zero analysis/demos, binary review, no repair.
3. **Repair ablation:** same primary prompting, existing full retry + re-review.

No header materialization, expanded catalog, new repair controller, adaptive
routing, extra training or outcome-selected per-question profile. These excluded
prototypes are future work. Existing generated tokens, prompt tokens, latency,
truncation, source support and withheld answers stay visible.

## Data and isolation

The sealed SSD dataset contains **160 questions from50 whole reports** in the
existing FinQA development-source file. Selection uses a fixed report-ID hash,
retains all questions in each chosen report, and excludes the earlier prepared
100-report selection,23 original development reports and natural-research reports.
All public packets are sealed before separate scoring payloads are written.
No answer, reference program, annotated retrieval or outcome selects cases.

This is a prospective report-held-out evaluation relative to the recorded project
development exposure, not a guarantee of absence from model pretraining or all
unrecorded human exposure. Public/source hashes, exact report and question IDs,
exclusion provenance and original scoring annotations remain available on SSD.
No failed/unsupported case is dropped or rescaled after results. No favorable
subset becomes the primary test. A single benchmark limits generalization.

## Resources, execution and interruption

Nominal caps are12.8/25.6 decimal GB. Effective cap is the smaller of nominal and
available RAM minus1GB before a tier starts. That same cap is saved and reused by
every arm/profile in that tier, including resume; a shortage later stops the run
until RAM is freed. Physical-memory checks reject a 32 GB run on this laptop.

Every0.2 seconds, the controller samples its own plus worker/descendant RSS and
swap. It terminates the worker on observed cap violation or any swap usage; such
an attempt invalidates the run and cannot silently resume as a passing result.
**This is sampled RSS/no-swap enforcement, not a hard cgroup-limit claim.**
All raw samples are retained. Equal ceilings are not equal compute or utilization.

One workload lock is inherited by each worker. A worker watchdog stops on loss
of its controller identity. Completed cases/stages are flushed to SSD. Resume
requires identical frozen code/config/data/runtime/host and the exact unique
completed-case prefix; it starts only the unfinished cases. Torn trailing writes
are preserved before recovery. Failed/interrupted attempt logs are never erased.
Completed-job hashes and per-attempt memory proofs are checked before reuse.

All code needed for the evaluation is snapshotted into its SSD run. Workers and
later replay use that snapshot. No `.env`, credentials, model weights or training
environment are copied into result archives. The self-contained CPU runtime on
SSD is copied to a local ignored cache so an SSD mounted noexec is supported.
No pip/apt/model download, agent application or root installation is required.

## Analysis and claim limits

The16 GB primary profile SAS/MAS pair is the main comparison. Direct/repair
profiles and32 GB are declared secondary, not additional chances to pick a winner.
The completed8GB supporting runs used an earlier native CPU build; the lab16/32
runs share the portable AVX2 build. Do not attribute8-to16 differences solely to
RAM without acknowledging that implementation/configuration difference.
Both numerical metrics are mandatory; wrong-delivery reduction cannot hide lost
correct answers or additional withholding. Always-withhold is included as a
zero-utility reference. Prefix ablations are measured trajectories, not fresh
independent model runs.

After evaluation, replay every prompt, output budget, program, score, delivery
decision and memory record using the pinned vocabulary and frozen pipeline.
Estimate paired MAS-minus-SAS differences with10,000 whole-report bootstrap
resamples, seed42; report all outcomes and costs. The displayed95% intervals are
marginal estimates, not a family-wise multiplicity guarantee. An observed sample
Pareto flag is descriptive; it does not prove population superiority, practical
equivalence, safety or H0. Degenerate intervals do not prove equivalence. No
post-hoc negligible-effect margin or selective p-value is permitted.

One family/checkpoint configuration/seed and changed capacity/precision across
tiers limit causal architecture claims. The comparison is between deployments,
not an isolated architecture mechanism. No new method may be introduced after
sealing; a behavior-changing bug fix requires explicit versioning and rerunning
affected controls. Originality or publication readiness is not automatic.
