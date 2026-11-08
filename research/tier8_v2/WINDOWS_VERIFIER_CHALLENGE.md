# Windows 8 GB fixed-candidate verifier challenge

The previous five-case pilot found that the 0.5B verifier accepted all
programs with a verdict-only schema, while the 3B reviewer withheld all.
This follow-up tests the same reviewers on new questions and adds a
forced comparison between a reference program and a plausible error.

Four company-year reports were selected from the public FinQA test
source by a fixed SHA-256 order, with one eligible question per report.
Report IDs from the two audited SSD development and training sources
and the repository's archived FinQA development data were excluded.
The four exact question IDs also had no matches in the tracked
research, configuration, or manifest files before archiving this run.
This checks recorded project exposure. It does not check model
pretraining exposure or prove independent replication.

Each question pairs a source-bound reference with a single edited
operand or operation. Both programs execute on the same evidence.
The translated reference matches the official FinQA execution result
and the near miss fails official execution matching and both historical
numeric metrics. This is a controlled discrimination task with
reference programs and constructed errors. It does not estimate
accuracy on naturally generated candidates or official test-set accuracy.

The 0.5B F16 and 3B Q4 models each review eight candidates individually,
with the same verdict prompt and output schema. The 3B model also
chooses between the programs with both presentation orders. It sees
the question, evidence, programs and executions, without label keys.
The two orders are repeated measurements on the same four questions.
Report how many are correct in both orders, as well as the pooled
choice count. A model that always selects one position scores four of
eight choices and zero questions correct in both orders.

Inference uses the same native Windows llama.cpp b12202 CPU runtime,
token allowance and sampled 6.4 GB working-set guard as the original
pilot. Each call allows 192 generated tokens. The pairwise comparison
has two candidates in context and assumes a valid candidate is
available, so it cannot directly replace a delivery gate.

Inputs and SHA-256:

- [FinQA test source](https://github.com/czyssrs/FinQA/blob/main/dataset/test.json)
  `831dbfb2e785dbc227f895ce3f24046433467aec67b09db2bd6ac7692a8a30dc`
- [FinQA evaluator](https://github.com/czyssrs/FinQA/blob/main/code/evaluate/evaluate.py)
  `845cd131cab843eceff256cf6d392978cc470a7da4a80107beb56027fdca5c13`
- SSD development source
  `a847fb7e0d61a3125a1e2909852df6b89f1ee64d2c5ff1bf689e332214deee51`
- SSD training source
  `49f237eb9779b569473b26b08048867d04635a7cc39ad6a7a5664c55bb428db6`
- Repository development source
  `27cc6c57487bbaba73041f93dba831a39b1cabe999c2ec0ddebc6f1200ff85bd`
- Frozen cohort
  `2b6893f736dc51881bfefe2ea5134d4ff9ff6ac6dc4aa330256e0b4d0a2d2651`

The runner is `scripts/tier8_windows_challenge.py`. The `freeze`
command takes the test source, evaluator and three `--exclude` files.
Use `replay` with the archived cohort, the same native CLI and SSD
weights as the initial pilot, and a fresh output directory. Run
`summarize` on the resulting replay ledger.
