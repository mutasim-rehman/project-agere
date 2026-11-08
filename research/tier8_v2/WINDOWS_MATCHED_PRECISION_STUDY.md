# Windows 8 GB matched quantization comparison

The earlier 3B/7B comparison changed both size and adaptation.
This follow-up fixes the base checkpoint and changes weight
quantization only. Both arms are unadapted and use the same source
evidence, drafting prompt, grammar, CPU runtime, thread count,
4,096 context and 768 generated-token ceiling. We alternate which
arm runs first. There are no review calls.

Both weights were produced directly from the same SSD F16 3B GGUF
with the native llama.cpp b12202 quantizer, `--max-buffer-size 64`
and two threads. No importance matrix or requantization was used.
The original 16-bit file is retained as the source checkpoint.
The outputs are reproducible local weights and are not committed.

- Source F16 SHA-256
  `7861b68729de6c1c00828a54688b76a7dbdd20f8f87b4147de222554a70708d4`
- Q4_K_M SHA-256
  `1680982035e7d3311e02546afdf1a80486cdd9a05479ec4169bd4f0f98c20a82`
- Q8_0 SHA-256
  `d2e5338e24402f95f0a4f08cc8941b8f546fe809348ab75abad6366edff9458e`

Twenty-four FinQA test questions, one per company-year report,
were selected by the existing evidence-only hash rule. We
excluded both development sources and all six preceding Windows
cohorts. Because both checkpoints are unadapted, the source-only
filter does not exclude the whole raw FinQA training source.
Pretraining exposure cannot be audited here. Frozen cohort SHA-256
`3a21930ab6502f5ddedee95793fe19a13d025e59eb7c49ff6545f09d124abfbf`.

Use `tier8_windows_natural_pairs.py run --precision-control Q4.gguf Q8.gguf`
with the actual files, the native runtime and `--job-commit-limit
6100000000`. The first and second columns in the resulting
summary refer to Q4 and Q8. Primary outcome is official FinQA
execution correctness on all cases. Report paired gains and
losses, evidence sufficiency, resource use, and reported-answer
sensitivity. This tests weight quantization in one model family,
without making a comparison to full precision or resident teams.

## Results

All 48 drafts executed under the job commit guard. Official
execution correctness was 3/24 for Q4 and 5/24 for Q8. The
matched contrast has three Q8-only correct reports, one
Q4-only correct report and twenty ties, with exact two-sided
McNemar p = 0.625. Reported-answer scoring counted 2/24 and
4/24, with two gains and no losses. This is a small estimated
gain rather than evidence of a reliable accuracy difference.
Resampling the 22 companies as clusters gives a descriptive
95% interval of −8 to +25 percentage points for the official
paired difference. This retains company-level dependence but
has limited resolution with four discordant reports.

Peak sampled RSS was 2.29 GB for Q4 and 3.64 GB for Q8. Peak
worker commit was 2.59 and 3.94 GB. Median elapsed time including
model load was 19.2 and 34.5 seconds. Both arms consumed 21,216
prompt-evaluation tokens. Q4 made 2,987 decode evaluations and
Q8 made 3,073. These counters distinguish observed computation
from the shared 768-token ceiling.

Both quantizations fit this sequential Windows configuration.
The study isolates weight quantization for this checkpoint and
runtime. It does not establish an 8 GB accuracy advantage from
full precision, a 16 GB result, or a MAS/SAS architecture effect.
Both arms matched 3/24 normalized symbolic reference programs
after backward slicing. The two extra Q8 execution matches
therefore did not translate into a higher symbolic-match count.
This secondary diagnostic distinguishes numerical result
agreement from expression equivalence.
