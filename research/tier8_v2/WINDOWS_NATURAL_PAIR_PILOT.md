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

## Results

All six questions produced two distinct executable programs. Neither
draft matched the official execution result on any question. The
reported-answer metric agreed on all 12 final programs. Even a
perfect selector could have delivered zero correct final candidates.

The first review order selected a wrong program on five questions
and withheld one. The reversed order selected a wrong program on
four and withheld two. Agreement withheld all six, filtering every
observed wrong selection. It showed no useful delivery on these
generated candidates. This differs from the constructed challenge,
where three pairs with a correct candidate produced a correct delivery.

The lexical evidence packet retained all annotated evidence spans
on three questions. Candidate failure occurred with and without all
annotated spans present. One wrong draft had an earlier prefix that
matched the official answer. This gold-aware check reproduces the
extra-operation failure on one new question. It cannot select an
endpoint at inference time.

Peak sampled working-set RSS was 2,464,538,624 bytes (2.46 GB).
The study leaves paging and unsampled peaks unverified. With no
correct final candidates, further tuning of the gate on these six
questions has no path to useful delivery. A future experiment would
need to improve retrieval or program generation first and validate
candidate availability on new reports. Keep the 16 GB tier gated.
