# From architecture comparison to a testable contribution

The research question is whether a repair controller can improve correct delivered
answers under the same memory and inference budgets in both SAS and MAS. The
architecture comparison remains a controlled experiment, not the contribution.
No useful novel method has yet been established.

## 1. Strengthen both systems before judging repair

Use the same source packets, numerical executor, quantity catalog and training-only
demonstrations. Optimize each arm on development data rather than forcing identical
prompts or role allocations. Record the tuning configurations and costs.

Evaluate formula-first analysis before program generation, source measure/year
selection, explicit units and independent verification. Test the MAS 1.5B verifier
as well as its 0.5B verifier; label shared checkpoints accurately. Investigate
retrieval misses separately from reasoning failures. Give SAS the same reasoning,
verification, retry and tool opportunities. These are baseline improvements.

Current checkpoints are an experimental starting point, not proof that either
architecture is optimized. Compare suitable alternative checkpoints/quantizations
and train-only adaptation if feasible before making a broad architecture claim.
Keep a fixed-checkpoint comparison separate from a best-found-system comparison.

## 2. Test a narrow repair hypothesis

Candidate: repair a wrong dependency without regenerating unaffected reasoning.
For example, a model computes gain, divides it by the starting value, then wrongly
scales the unnormalized gain. A reconnection can make the last step consume the
normalized intermediate while preserving the other decisions.

The implemented first version detects unused intermediate computations, enumerates
single-edge alternatives, asks the model to select or KEEP, reexecutes the graph,
and verifies the selected result. The deployment policy never sees gold. Offline
oracle coverage measures only whether the candidate set could contain a solution;
it is not achieved accuracy. Unused work can be legitimate, so measure harmful
changes and KEEP decisions. This mechanism cannot fix a missing correct formula.

## 3. Isolate the effect

Compare no repair, whole-program retry, step patching and bounded reconnection in
both arms. Include a candidate-selection control with the same call/output budget
and a graph-pruning control that preserves the original numerical result. Report
actual generated tokens, prompt processing, latency and sampled memory, alongside
the common 2048-output-token and 6.40 GB process-tree RSS ceilings. Equal ceilings
do not imply equal compute; add cost-matched comparisons where feasible.

Primary outcomes: correct answers over all cases, correct delivered coverage,
incorrect deliveries, withheld answers, corrections and regressions. Never judge
only accepted-answer precision. Audit verifier mistakes and local semantic errors;
numerical agreement alone does not label every program step correct.

Stop expanding this mechanism if natural errors lack useful intermediates or
selection harms offset repairs. Current MAS graph diagnostics already warn that
bounded reconnection may have little coverage. Do not manufacture errors to
create the main result; label any injected-fault experiment separately.

## 4. Establish originality and generalization

Distinguish the final mechanism from FinMAN, CRITIC, independent verification,
graph rollback and execution-trace program repair. Existing components combined
under a RAM cap are not automatically a methodological contribution. Preserve
negative findings and revise the hypothesis when the evidence contradicts it.

After development, freeze code, checkpoint identities, prompts, controller and
metrics. Evaluate on untouched documents grouped by report/company, include a
second task/source and realistic KYC/credit evidence where possible, and report
paired uncertainty plus contamination limits. The current 24 FinQA cases are
development only; neither they nor the rule-solvable synthetic suites establish
publication-quality generalization.

All milestones retain manifests, raw stages, memory traces, decisions, tests and
Git commits. A publishable claim requires a useful measured distinction that
survives strong baselines and held-out evaluation; success is not guaranteed.

## Updated implementation order after the negative proof pilot

1. Finish the frozen 128-versus-256 analysis ablation for SAS and MAS 3B. Judge
   correct deliveries, wrong deliveries, abstention, latency and total budget,
   not longer reasoning by itself. No automatic increase beyond 256 is planned.
2. Audit representation burden with a less restrictive program/literal control
   before blaming model capacity. Keep evidence access, executor and model budgets
   comparable; disclose any demonstrations or grammar changes explicitly.
3. Improve source identity: expose table cell coordinates, row measure and column
   period separately from the numerical token. Keep equal-valued cells distinct.
   Existing partial binding domains are the starting implementation. Neither a
   matching value nor a unique numeric mapping certifies the intended source.
4. Replace silently chosen ambiguous training bindings with resolved, audited
   targets or an explicitly ambiguous training subset. Capture exactly the prompts
   used at deployment. Use train-only, report-group-disjoint adaptation and verify
   that the resulting adapter is actually applied during measured inference.
   Preserve unadapted controls for both systems. Training setup is not implemented.
5. Only after binding improves, test a bounded source-binding repair against
   whole-plan retry and blind independent rebinding. Preserve formula and unrelated
   bindings only when the controller has evidence to do so; provide KEEP/abstain.
   Count false locks and formula errors that this repair cannot solve. Retire it
   if natural-error headroom or measured benefit remains absent.

Items 2–5 are proposed work, not completed features. The possible contribution is
an empirically useful treatment of uncertain source identity and safe revision;
its originality is unestablished. Compare against VeriFin's independent fact/formula
verification as well as existing local repair and compiler baselines. A simpler
known method that wins should become the baseline, not be renamed as novelty.
