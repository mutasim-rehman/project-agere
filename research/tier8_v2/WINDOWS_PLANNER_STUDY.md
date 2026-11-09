# Evidence-only planning under the Windows 8 GB application budget

## Motivation

The answer-key operation-structure intervention recovered 10/15
official matches with an answer-key operand shortlist, compared
with 0/15 from the shortlist alone. This study tests whether a
predictive structure stage helps with inputs available at inference.
[Earlier diagnostic and resource results](WINDOWS_EXTENDED_RESEARCH.md)

## Development and cohort audit

The prototype uses 12 existing FinQA development packets, one per
company-year report, ranked by SHA-256 with prefix
`agere-shape-dev-v1|`. These cases are for development and are
reported separately. Their public packet checksum with LF line endings is
`14abf004b6c0f3b652af174c2a3c0eb0d6e8f24b0569c7195112e2c89b47fe9f`.
The first prototype produced a usable structure on only one of 12
development reports. Eleven proposed steps with no source-dependent
operand. Before any held-out inference, we revised the planning grammar
to predict only the operations and dependencies. The binding pass
assigns quantities and standard constants. We retained the original
development outputs separately.

The remaining FinQA test inventory shrinks to one eligible question
on one report after excluding named project cohorts, prior Windows
cohorts, and the recorded common actor and control critic training
and validation report groups. We use TAT-QA for the held-out
arithmetic comparison. The primary cohort contains 96 contexts from
the benchmark's official development split, held out for this project.
The secondary cohort contains all 28 remaining eligible contexts
from the official test split. Both use one arithmetic question per
table and the existing SHA-256 order. Eligibility requires a numerical
catalog and excludes table IDs used by prior Agere TAT-QA comparisons.
Normalized exact table duplicates are excluded. The primary cohort
also excludes exact tables in the full official test split. The
published raw data provide table IDs but do not map these records to
company-year reports. Cross-context report overlap and checkpoint
pretraining exposure remain unknown.
[TAT-QA benchmark](https://aclanthology.org/2021.acl-long.254/)

Frozen checksums (LF line endings for cohorts):

- Primary cohort `e463671e33f56af56e6d8d1ad07720b3e75fa3c9a732746a541483fb44251ac0`
- Secondary cohort `f494a4268baa1623b8159dc2d428c0cfaeb3235e99df5e9831bf923dcaa1a802`
- Official development source `8da095a819af6db3c14877c6df2d4d29960e41d1a63dd1fa853507bd2a616af5`
- Official test source and evaluator hashes are recorded in [the prior TAT-QA protocol](WINDOWS_TATQA_STUDY.md).

## Prespecified comparison

- **Direct 7B** emits a number and display scale, with a short
  explanation. **Cited-program 7B** emits a source-referenced
  executable program with a display scale. Both use the same
  unadapted Qwen2.5 7B Q4 checkpoint, 960 generated tokens maximum
  per question and no review. Alternate which runs first.
- **Current MAS** runs the same common actor and control critic
  adapters on two resident 3B Q4 workers. It reserves 768 tokens
  for the draft and 192 for binary review.
- **Planner MAS** uses the same two resident workers and review
  instruction. The actor uses up to 192 tokens to predict operations,
  unbound value slots, and dependencies. A valid connected
  structure constrains a 576-token source-binding
  draft. An empty, invalid, or disconnected structure falls back
  to the ordinary grammar with the same 576-token cap. The critic
  sees the resulting program, its execution, and the original
  evidence. It gets up to 192 tokens. Both MAS arms deliver only
  executable answers that the critic passes.

All arms use the same evidence packets, 4,096-token context, eight
CPU threads per worker, b12202 Windows runtime, 6.1 GB job commit
limit and 6.4 GB sampled working-set guard. The resident pair uses
the disabled RAM prompt cache validated earlier. The 7B runs use
the sequential CLI. Their latency includes model load, so the
clean planner latency contrast is the two resident MAS arms.
These are application limits on the 16.39 GB Windows host.

**Primary outcome** is the paired difference in official exact-match
correct delivery between planner MAS and current MAS on the primary
cohort. A practical improvement needs a positive paired interval
and no observed increase in wrong deliveries. The secondary cohort
checks the direction. Direct 7B and cited-program 7B are competitive
comparators rather than matching controls for the planner. Report
correct, wrong and withheld counts, candidate correctness before
review, F1, elapsed time, peak memory and token counters. Resample
paired table contexts for 95% intervals and report exact paired
tests. Report-level clustering is unavailable from the source.

For a secondary diagnostic, compare the final program's operator
tree with the parseable benchmark derivation after replacing numeric
leaves with placeholders and sorting commutative operands. This
checks structural agreement without inspecting labels during
generation. It does not recognize every equivalent formula.
Unparseable derivations are excluded only from this diagnostic.

Run `tier8_windows_tatqa.py run --matched-large-formats ...
--generation-limit 960` for the 7B arms. Run
`tier8_windows_resident_probe.py --unit-mode tatqa
--disable-prompt-cache-ram` with `--planner direct` or
`--planner shape` for the two MAS arms. Score only complete
cohorts with `tier8_windows_planner_study.py`. Keep the two
benchmark splits separate in scoring.
