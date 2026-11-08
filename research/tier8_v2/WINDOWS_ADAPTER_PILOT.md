# Windows 8 GB matched drafter adapter pilot

The earlier natural-pair pilot yielded no correct final candidates.
This follow-up isolates a change to candidate generation. The same
3B Q4 checkpoint receives the same shortest-complete-calculation
prompt, evidence packet, reference grammar and token cap, with and
without the existing common actor LoRA. We alternate which condition
executes first. The base checkpoint reviews both programs in both
orders with NEITHER enabled. The adapter is loaded only for drafting.

One question from each of six new FinQA test reports was selected by
the natural-pair hash rule before inference. The three prior source
exclusions and the three earlier challenge cohorts were used. The
six report IDs were absent from the inspected common actor continuation
data and the tracked initial adapter train and validation files.
This checks the named project artifacts and does not rule out other
model exposure. The evidence-only cohort SHA-256 is
`71f2ff428ca6ee0ec6216312436faa504f536d546e291e392e53de8e8f5e016c`.

The attached SSD adapter is
`runs/tier8_matched_continuation/common-actor-converted-01/adapter-f16.gguf`
with SHA-256
`4e21beca69dcf7bf2b9e89df7d189c74740d98acebe08501fd7e848bb7155d3e`,
matching its conversion manifest. This is the continued common actor
adapter, which differs from the adapter used in the historical dev24
comparison.

Run the [natural-pair runner](../../scripts/tier8_windows_natural_pairs.py)
using the archived cohort and add `--adapter` with the SSD GGUF path.
In the summary, first draft denotes the base condition and second
denotes the adapted condition. Candidate correctness under the official
FinQA execution evaluator is primary, with reported-answer scoring
secondary. The Windows resource guard and 1,920-token reservation match
the previous natural-pair pilot.

## Results

Both conditions generated executable programs on all six questions.
The base drafter produced zero correct final programs and the adapted
drafter produced one. The official execution and reported-answer
metrics agreed on all 12 candidates. All six evidence packets
contained the annotated evidence spans. One wrong candidate contained
an earlier prefix that matched the official result.

The adapted programs had a median of two operations, compared with
3.5 for base programs. Median drafting elapsed time including model
load was 19.7 seconds with the adapter and 22.5 seconds without it.
Peak sampled RSS was 2.52 GB with the adapter versus 2.46 GB for base
drafting. These descriptive comparisons cover six paired questions,
and Windows paging was not measured.

The agreement rule delivered zero correct and two wrong answers
and withheld four. Both orders selected the same wrong program on
two reports, one from each draft condition. On the report with a
correct adapted program, one order selected it and the other picked
the wrong base program, so the rule withheld.

This provides a counterexample to treating order agreement as a
safety check by itself. The clean constructed result did not transfer
to these naturally generated candidates. The adapter shows a local
candidate recovery and shorter programs, with no observed gain in
correct final delivery. Further order changes would not resolve the
underlying candidate scarcity and consistently wrong selections.
The 16 GB tier remains gated.
