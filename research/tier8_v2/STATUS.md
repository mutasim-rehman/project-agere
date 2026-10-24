# Research checkpoint — 24 October 2026

Goal remains active. No defensible novelty or architecture winner is established.

## Verified infrastructure

- Local Python 3.12; source-built llama-cpp-python 0.3.16 imports and generates.
- All official weights, including both 7B Q4 shards, pass revision-pinned SHA-256.
- Small-model native-F16 conversions preserve full precision but did not reduce size.
- 31 tests pass. Code, decisions, raw completed runs and paired analyses are committed.
- Milestone pushes use the project .env token through the ignored askpass helper.
- Leave the user's unrelated .GITIGNORE file untouched.

## Measured results

| Condition | Cases correct | Correct deliveries | Incorrect deliveries | Observed peak RSS |
|---|---:|---:|---:|---:|
| Original v1 rules | 150/150 | Not assessed | Not assessed | Not assessed |
| Temporal KYC rules | 24/24 | Not assessed | Not assessed | Not assessed |
| MAS initial four-case pilot | 1/4 | 0 | 0 | 5.787 GB |
| MAS independent/field, distinct instances | Invalid memory | — | — | 6.411 GB |
| Free-citation distinct-instance control | Invalid memory | — | — | 6.405 GB |
| MAS shared weights, independent/field | 1/4 | 1 | 0 | 5.145 GB |
| MAS shared weights, patch repair | 1/4 | 1 | 0 | 5.145 GB |

The shared setup uses three roles and two resident model instances; identical
0.5B weights are reused serially with KV reset before each call. Memory sharing
is engineering, not a novelty claim. Sampled RSS cannot establish an unobserved
absolute peak. Invalid runs are excluded from accuracy comparisons.

Patch repair spent 1,709 tokens versus 1,321 without repair and yielded no gains
in this four-case pilot. All runs are development diagnostics, not confirmation.

## Live work at checkpoint

SAS pilot: research/tier8_v2/runs/sas-field-smoke-01, launched by exec session
17710. Revalidate that handle or the actual process before deciding it stopped.
A partial case file is not a completed result. All weight downloads have finished.

## Next research work

1. Inspect the completed SAS pilot and verifier errors, then commit/push the result.
2. Evaluate stronger independent re-extraction against anchored repair; recognize
   Chain-of-Verification as prior art. Do not keep tuning only a rule-solvable toy.
3. Connect the bounded cited arithmetic executor to the non-oracle FinQA packets.
   The fixed first-24 dev slice retrieves all gold evidence in 19/24 cases; never
   use gold retrieval or programs in model prompts.
4. Expand credit and independent source layouts, compare strong SAS/MAS with equal
   development effort, and measure actual tokens, false locks, regressions and cost.
5. Develop and ablate a narrower useful contribution, complete full-paper novelty
   review, and freeze new confirmatory data/systems before any publication claim.

The existing test split remains unopened during redevelopment. No new frozen
confirmatory evaluation exists yet. See DECISIONS.md and NOVELTY_AUDIT.md.
