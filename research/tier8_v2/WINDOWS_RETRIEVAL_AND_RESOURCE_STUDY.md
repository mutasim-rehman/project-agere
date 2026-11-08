# Windows 8 GB evidence retrieval and resource controls

## Development retrieval screen

Across the public FinQA development split (883 questions from 224
reports), the baseline top-eight lexical packet contained every
annotated evidence span for 750 questions. BM25 under the same
per-question evidence-plus-catalog token allowance covered 748.
Reciprocal rank fusion of the original ranking, BM25 over full
spans, and BM25 over table row labels covered 733. We measured
token costs using the local Qwen tokenizer. [BM25](https://doi.org/10.1561/1500000019)
[Reciprocal rank fusion](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)

Keeping up to 16 lexical spans, bounded by twice the original
budget and ordinarily by 2,300 evidence-plus-catalog tokens,
covered 827 questions. It added 77 and lost none. The median
evidence-plus-catalog length grew from 711 to 1,225 tokens.
The paired report-cluster bootstrap interval for the coverage
gain was +6.6 to +10.9 percentage points. This is a larger
input budget and an annotated-evidence retrieval result.
It does not measure answer correctness.

A second offline screen added local BGE-small-en-v1.5 and a
BGE/lexical rank fusion at the original token allowance. Dense
retrieval covered 728 questions and hybrid covered 748, versus
750 for lexical8. The hybrid recovered 18 complete packets and
lost 20, and its report-cluster difference interval ran from
−1.9 to +1.4 points. We did not adopt either method.
[BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5)

The annotated arithmetic program's numeric operands could be
bound to retrieved source values on 703 lexical8 questions and
767 wider lexical questions. This is numerical bindability under
the current arithmetic operator and constant set. It does not
prove the source identity is unique or that the model finds it.

## Candidate-generation test

The wider lexical packet was selected using the development
retrieval screen and frozen for the same 16 test reports as the
count-planning comparison. The baseline and wider arms use the
same adapted 3B checkpoint, drafting prompt, 768-token allowance
and 4,096-token context. Each arm receives its own evidence
packet and source catalog. We keep all 16 paired questions and
measure official execution accuracy and annotated evidence coverage.
This is a new intervention on the same test questions rather than
an independent replication of the count-planning comparison.

Frozen wider packet SHA-256
`c3d6e58b2b182ee95f3ca15d263511897c515ddfeefe81c0720f3006fa705cb4`.
The audit script can regenerate it with `--cohort` and
`--method lexical16_bounded`. The paired runner takes it as
`--retrieval-cohort`.

## Native hard commit guard

The runner can create each inference process suspended, assign it to
a Windows Job Object with a 6.1 GB aggregate commit limit, then
resume it. This leaves room within 6.4 GB for the Python controller.
The sampled RSS guard remains separate. Job commit limits constrain
virtual memory committed by the process group. They are distinct
from RSS and do not demonstrate zero Windows paging.
[Windows Job Object limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)

A deliberately oversized 96 MiB Python allocation failed inside
a 64 MiB job with MemoryError. The job peak counter on that failed
probe exceeded the limit, so failed-allocation peaks should not be
interpreted as committed memory successfully consumed. A separate
7B CPU inference preflight completed under the 6.1 GB guard with
5.42 GB reported peak commit and 5.01 GB sampled RSS. The resource
probe does not validate the earlier sampled-only studies retroactively.
Later Windows runner events also record the operating system's worker
working-set high-water mark and sampled minimum host available memory.
Those measurements are separate from the job's peak commit.

## Completed candidate comparison

All 32 drafts executed under the 6.1 GB job limit. Official
execution correctness rose from 1/16 to 4/16, with three
recoveries, zero regressions and thirteen ties. The exact
two-sided paired McNemar p-value is 0.25. The secondary
reported-answer count rose from 0/16 to 3/16. Candidate
accuracy does not measure downstream delivery.

Annotated evidence coverage rose from 14/16 to 15/16. All
three recovered programs already had their annotated spans
in the narrower packet. The one newly covered question
remained incorrect. The data therefore do not support
attributing the candidate gain to recovery of missing
annotated evidence. Extra context can also change operand
binding or decoding.

Peak sampled RSS was 2.52 GB in both arms and peak job commit
was 2.93 GB. Median drafting elapsed time rose from 19.8 s
to 25.0 s. The paired signal warrants a larger frozen-cohort
replication. The 16 GB tier remains gated.

## Frozen replication

We found 21 eligible additional test reports after excluding all
previous Windows FinQA cohorts and the archived actual inputs to
adapter fitting, adapter validation, prior 8 GB evaluations and
the 16 GB evaluation. The exclusions are listed with hashes in
`replication-exclusions.json`. Unlike the first pilot, this
selection excludes recorded development inputs rather than every
company-year in the public development-source archive. The
cohort therefore tests transfer beyond recorded project exposure,
without making a claim about pretraining or every development
artifact.

Use all 21 with one question per report in the fixed hash order.
Keep both arms and the primary official execution metric identical
to the 16-report retrieval comparison. No template, observed outcome
or annotation can affect inclusion. The paired gains/losses and
exact two-sided McNemar result are evaluated separately from the
first pilot. The narrow and expanded evidence manifests are
archived before inference, with SHA-256 values
`e69c0a16d9fd602a853c0e5a91ebb0b694bce8f49b7860adfa81382cb8905e39`
and `62a4ccf71a96caf0937019877d33b6dfe9b5adca8bd32ee75241634e4c50aecb`.

The 21-report replication is a directional check. Under an
optimistic paired model of 18.75% gains and zero losses, the
two-sided exact test has about 19% power at 21 independent
report pairs and needs 41 for 80%. With 15% gains and 5%
losses, it needs 168 pairs for 80%. With 10% gains and 5%
losses, it needs 498. These are sensitivity scenarios under
independent pairs and fixed transition probabilities, not
estimates of the actual effect or an assumption that
company-year reports are always independent. The calculations
are archived in `prospective-power.json`.
