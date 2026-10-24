# Adaptation corpus revisions

Use **finqa-cell-adaptation-train-02.jsonl** and **validation-02.jsonl** for
structured examples. Revision 01 is invalid: JSON serialization reordered evidence
keys after quantity-ID targets were assigned. It remains only as historical proof;
see evidence/cell-adaptation-data-01-superseded.json. No model was trained on it.

Revision 02 canonicalizes evidence order before target construction and validates
every row again after loading the saved JSON. Its 1,851 examples are numerically
source-unambiguous; semantic source/formula correctness is not independently
adjudicated. Train/validation and development annual-report groups are disjoint.

**deployment-sft-1024-02.jsonl** contains 761 prompt-fitted examples (661 train,
100 validation), captured from the actual no-analysis/no-demo deployment draft
path for both SAS and MAS. It is distinct from the stronger analysis configurations.
The pinned Qwen GGUF tokenizers agree on every retained complete sequence. These
are training annotations and tokenizer checks, not generated answers or model gains.

Training must tokenize the raw prompt plus target response, preserve the recorded
prefix masking and reject any mismatch with the stored token-ID SHA. Validate the
HF tokenizer against these GGUF token sequences before fitting. Do not apply a
second chat template, truncate targets, train a verifier on invented PASS labels,
or evaluate without proving that the trained adapter is actually loaded.

## Execution gates

The official HF tokenizer parity audit passes all 761 examples for both profiles.
The inference environment remains separate from `.venv-training`. After the frozen
CPU sequence completes and the pinned training base is downloaded, the first real
model step is:

```bash
.venv-training/bin/python scripts/tier8_v2_adapt.py --profile 3b --mode fit --out research/tier8_v2/runs/adapter-3b-fit-01
```

This diagnostic performs two updates on the longest training example and saves
weight-change/gradient/memory proof. It is not an accuracy experiment. Only after
it succeeds should a separate `--mode train` run execute the 661-example epoch.
Use a new output directory. The trainer refuses overlap, existing outputs, changed
inputs and tokenizer mismatches. The 7B path still needs its own actual fit check.

Training loss and saved adapter files do not prove deployment behavior. Convert
the adapter for the measured runtime, prove it is applied, then evaluate each arm
against its matched unadapted no-analysis baseline and the best existing baseline.
