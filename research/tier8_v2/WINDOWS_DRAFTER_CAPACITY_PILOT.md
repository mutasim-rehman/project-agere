# Windows 8 GB drafter capacity pilot

The matched adapter pilot recovered one correct program, but the
order-agreement reviewer withheld it and accepted two wrong programs.
This follow-up checks the candidate ceiling before spending tokens on
verification.

We compare the existing adapted 3B Q4 drafter with an unadapted
Qwen2.5-7B-Instruct Q4_K_M drafter, using the same evidence, prompt,
grammar, 4,096-token context, CPU thread count and 768-token output
allowance. We alternate which recipe executes first. The common
actor LoRA applies only to the 3B checkpoint. This is a comparison
between two drafting recipes, with model size and adaptation differing.
It does not isolate model size or test a resident team.

One question from each of six additional FinQA test reports was frozen
with the natural-pair hash rule. The three prior source exclusions and
all four prior verifier, natural-pair and adapter cohorts were excluded.
The six exact case IDs had no tracked research, configuration or manifest
matches before archiving. Their report IDs had no matches in the
inspected common actor continuation data and initial adapter train and
validation files. Frozen evidence-only cohort SHA-256
`4b66b085ef95bd1e12e12f4a6b79c232a4b1ca6a3a9f778f9bbaded934a4b98d`.

Use the native Windows CPU runtime and adapter documented in
[the matched adapter pilot](WINDOWS_ADAPTER_PILOT.md). Run
`scripts/tier8_windows_natural_pairs.py run` with that adapter and
`--capacity-control qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf`.
Both GGUF shards must be in the weights directory. The first draft in
the summary is the adapted 3B condition. The second is the unadapted 7B
condition. The 6.4 GB working-set guard applies to sequential CPU
inference. Scoring is post-inference using the pinned official
execution evaluator and secondary reported-answer scoring. This
experiment records candidate correctness, not answer delivery.

7B shard SHA-256:

- Shard 1: `dfce12e3862a5283ccfb88221b48480e58745165de856439950d0f22590580db`
- Shard 2: `539cf93f78e887edea1c04e2d7d8cdaca9d01dae9c9025bcb8accbe29df3d72a`
