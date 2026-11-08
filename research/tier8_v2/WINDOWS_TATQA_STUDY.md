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
