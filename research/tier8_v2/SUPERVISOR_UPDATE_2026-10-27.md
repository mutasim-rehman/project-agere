# Research checkpoint — 27 October 2026

We have completed real adaptation, deployment checks and three controlled MAS
evaluations. We have useful negative findings and a generation bottleneck to
address. **We have not yet demonstrated a novel method that improves on the
stronger original baseline.** The SAS natural comparison is still running.

The completed MAS comparison covers 52 questions from 15 reports. All three critics
receive exactly the same common actor's initial plans, prompts and responses.
Results are correct deliveries / wrong deliveries / withheld:

| Critic | Reported-answer convention | Raw-execution convention |
|---|---|---|
| Matched control |3 /19 /30|5 /17 /30|
| Cross-question negative training |3 /15 /34|5 /13 /34|
| Stronger original critic |4 /22 /26|6 /20 /26|

Cross-question training reduces wrong deliveries relative to the matched control,
but report-level uncertainty includes no improvement or harm. Against the original
critic it withholds one previously correct answer, so it fails our predeclared
no-correct-loss adoption rule. We have not adopted it. These are exploratory
public training-source report holdouts, not untouched publication confirmation.
[Complete paired evidence](MATCHED_MAS_SELECTION.md).

Two measured findings guide the next iteration:

- The net four fewer wrong deliveries versus control occur entirely among cases
  where the current catalog lacks an annotated operand. This post-hoc association
  does not prove a learned semantic mechanism. The identical initial actor gets
  only 4/52 reported answers correct: stricter verification alone cannot fix that
  generation bottleneck.
- Both matched MAS policies spend another 13–15 minutes on repair across this
  sample, with no per-case delivery or correctness change versus their measured
  no-repair prefixes. That is a measured cost without demonstrated repair benefit
  in this configuration, not evidence that all MAS repair is ineffective.

Both SAS continuation policies have completed 64 updates / 512 examples from the
same original joint 7B initializer, with identical 448-row validation. Crossed
training lowers aggregate teacher-forced loss 0.03346→0.01770, but worsens mutation
and replay-critic losses. Drafter loss also changes despite fixed drafter data,
consistent with shared-task transfer. Generated-answer improvements remain
unproven. Training used a separate 10.5 GB allowance; native deployment proofs stay
below 6.4 GB. **This is not a claim of training within 8 GB.**
[SAS evidence and limits](MATCHED_SAS_CONTINUATION.md).

Engineering progress includes a separate shared-backbone 3B serving proof:
sampled RSS 4.831→2.571 GB with matching outputs on two prompts/four role switches.
This known technique is not yet used by the natural MAS runs, which load two
specialist instances. A first-row source-retention prototype also improves
reference operand mapping 41→45/73 fitting cases without losing old catalog facts.
All 2,105 resulting quantities pass source/executor support checks. Its controlled
neural comparison is prepared but unrun; this is known preprocessing, with extra
source content/tokens, not demonstrated QA improvement or novelty.
[Prepared test](HEADER_MATERIALIZATION_STUDY.md).

If stopped here, we could write a preliminary reproducible evaluation/limitations
report. A convincing novel-method paper is not supported yet. The remaining SAS
comparisons, stronger baselines, reserved audits and prompt controls are needed
before claiming either architecture is optimized or freezing methods for 16/32 GB.
Older unadapted MAS analysis-prompt results do not establish the best prompt after
actor adaptation. No cross-tier method freeze or architecture winner is declared.
