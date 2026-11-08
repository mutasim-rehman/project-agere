# Windows 8 GB transfer check on TAT-QA arithmetic

This experiment asks whether the same 3B Q4 checkpoint answers
numerical questions better with a direct numeric response or
with a cited arithmetic program on a second benchmark.
Both arms receive the same top-eight evidence spans and a
768-token generation ceiling. The direct arm may show a brief
calculation then emits a value and scale. The program arm
receives a source-quantity catalog, emits an executable program,
and uses its declared output scale. Both must attempt an answer.
We alternate arm order and use sequential native Windows CPU
inference with the sampled RSS and 6.1 GB job commit guards.

The cohort contains 16 questions labeled arithmetic by the
benchmark, at most one per table context. A fixed hash order
and presence of a numerical evidence catalog determined inclusion.
No answer values, scales or derivations were used to select
questions or shown to the model. Model outputs are scored with
the official exact match and F1 functions. This is a small
arithmetic-only comparison rather than a test-set leaderboard
result. [TAT-QA benchmark and evaluator](https://github.com/NExTplusplus/TAT-QA)

The frozen cohort SHA-256 is
`51662f5f9b2903be529dd1daa0febd4f31b3282d25bb155a136dd728f2e3608a`.
The author's test gold JSON, metric and utility file hashes are
respectively
`c4d08418359c1d76468dec420ee748a37f48c06b63cb8ec2766f19d5d314b597`,
`2aeeac479f89f8c76300af1cc0e8d098eb86af84bc386b38b6ab4af484a6dea8`
and
`a84bb2f960737cf0a53733637a674cc4b20ef030a2be6a4b21dc2c4356f415ec`.
The source dataset is CC BY 4.0. [Dataset card](https://huggingface.co/datasets/next-tat/TAT-QA)

Use `scripts/tier8_windows_tatqa.py freeze`, `run` and
`summarize`. The official evaluator requires SciPy, pandas and NumPy.
The scorer's gold self-match was tested separately before inference.

## Completed format comparison

Both arms returned valid numeric predictions on all 16 questions.
Both achieved exact match and arithmetic F1 of 1/16 (6.25%).
Their only correct answers were on different questions. The
program format therefore demonstrated no net accuracy gain in
this pilot. It used 13,587 prompt-evaluation tokens and 2,018
decode evaluations across the cohort, versus 8,105 and 790 for
direct output. Decode evaluations are runtime counters and do
not equal the reserved generation ceilings.

Median time including model load was 19.2 seconds for programs
and 10.2 seconds for direct output. Peak sampled working-set
RSS was 2.46 GB in both arms and peak job commit was 2.77 GB.
The direct arm matched the reference scale label on 9/16 and
the program arm on 10/16. An answer-key diagnostic supplying
the correct scale did not rescue any wrong numeric prediction
in either arm. The main accuracy shortfall therefore cannot be
explained by choosing the wrong scale field alone.

## Frozen direct capacity comparison

The next TAT-QA comparison uses 40 additional table contexts
selected by the same hash and arithmetic-tag rule, excluding
all 16 previous table IDs. The 3B and 7B Q4 checkpoints both
use the same direct numeric prompt, evidence packet, scale schema,
runtime and limits. The 7B checkpoint is the two-shard model
documented in [the FinQA capacity pilot](WINDOWS_DRAFTER_CAPACITY_PILOT.md).
No adapters are used. This tests capacity at a fixed output
format on a second benchmark, with size and checkpoint differing.
The primary outcome is official exact match over all 40 questions.

The frozen capacity cohort SHA-256 is
`8091b5c09698c60d0e1c842ac9b593de53e582055243b79f1255fd90b9462d6d`.
Use `freeze --count 40 --exclude-cohort` with the 16-case cohort,
then `run --larger-direct qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf`.
The same summary route reports the paired exact-match transitions.

The completed 40-context run scored 5/40 for 3B and 6/40 for
7B. Four questions were correct only with 3B and five only
with 7B. The observed gain was one answer, with median time
rising from 14.2 to 34.8 seconds and peak worker commit from
2.76 to 5.43 GB. Supplying the gold scale in a separate
diagnostic recovered five wrong 3B predictions and one wrong
7B prediction. This comparison provides no clear accuracy
advantage for the larger direct model.

## 120-context replication on main

With the same direct prompt, evidence budget, runtime, and two
checkpoints on 120 additional arithmetic table contexts, the
3B model scored 12/120 (10.0%) and the 7B scored 29/120
(24.2%). Five contexts were correct only at 3B, 22 only at
7B, and 93 tied. The paired increase was 14.2 percentage
points, with two-sided exact McNemar p = 0.00151 using table
contexts as pairs. The earlier 40-context comparison was
inconclusive, so effect size should remain cohort-specific.

The 7B model used 5.43 GB peak job commit versus 2.76 GB at
3B. Median elapsed time including weight load rose from
14.1 to 33.5 seconds. Both consumed 60,934 prompt tokens
over the full cohort. Replacing predicted scale with the
gold scale rescued 11 wrong 3B answers and five wrong 7B
answers, so scale mistakes were more frequent at 3B but do
not account for the full difference. The comparison changes
checkpoint size at fixed direct output format. It does not
attribute the gain to a multi-agent arrangement. The
resource measurements come from the Windows job limit and
sampled RSS on the host, without a paging measurement.

See `evidence/windows-extended/tatqa120-summary.json` and
`evidence/windows-extended/tatqa120-cases.jsonl`.
