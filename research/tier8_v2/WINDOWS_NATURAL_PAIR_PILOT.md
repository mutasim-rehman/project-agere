# Windows 8 GB pilot with generated candidate pairs

The earlier order-agreement gate filtered every observed wrong choice
in a six-report test that used reference programs and constructed errors.
This follow-up uses candidates generated solely from report evidence.

We froze one question from each of six new FinQA test reports by hashed
question ID. We excluded the same three audited data sources and the ten
reports used in the preceding verifier challenges. The six exact question
IDs were absent from tracked research, configuration and manifest files
before archiving. Selection required a numerical evidence catalog and
did not use the gold program, answer, or observed model performance.
The public cohort SHA-256 is
`eb0181eab853f0f4089334937e557462b0b6d61e41dfdddc96ec264e9844b8a1`.

The 3B Q4 checkpoint generates two programs on the same evidence.
The first prompt checks that the final operation answers the question.
The second requests the shortest complete calculation. Both require
an answer attempt and allow one to eight operations. An executable
pair goes to the same checkpoint for comparison in both orders,
with NEITHER allowed. The agreement gate delivers only if both
orders select the same program. Identical programs count as the same
program even if the displayed candidate letters differ. A missing
executable pair is withheld and retained in every denominator.

Each question has two draft allowances of 768 tokens and two review
allowances of 192, totaling 1,920, within the 2,048-token cap. The
native Windows runner monitors sampled working-set RSS against
6.4 GB. The roles run sequentially.

Scoring happens after inference. The primary outcome is exact
execution matching via the pinned official FinQA evaluator and
translated arithmetic programs. Reported-answer scoring is secondary.
Report the correct-candidate ceiling, first- and second-draft
correctness, single-order choices, and agreement-gate delivery
outcomes. This pilot uses one checkpoint for drafting and review and
cannot identify a general architecture or quantization effect.

Use `scripts/tier8_windows_natural_pairs.py freeze` with the FinQA
test source, the three prior source exclusions and the two prior
frozen cohorts as `--exclude-cohort` inputs. Use `run` with the
frozen cohort and the same Windows CPU executable and SSD weights
as the prior challenge, then `summarize` with the official
evaluator and gold source. The source and evaluator hashes are
listed in [the prior challenge](WINDOWS_VERIFIER_CHALLENGE.md).
