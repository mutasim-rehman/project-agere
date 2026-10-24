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
