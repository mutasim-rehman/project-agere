# 16 GB protocol snapshot

**Analysis date:** 30 October 2026. **Evaluation period:** 28-30 October 2026.
**Study status:** completed accuracy audit with retained resource failures.
**Nominal tier:** 16 GB; **physical host:** approximately 15.44 decimal GB available to Linux.
**Application ceiling:** 11,500,000,000 bytes of sampled controller-plus-worker RSS.
**Unique question set:** 160 FinQA questions, 50 company-year reports, 36 companies.
**Repeated outputs:** 960 = 160 questions x 2 arms x 3 profiles; these are not 960 independent questions.
**32 GB:** not evaluated. **New neural calls for these documents:** zero.

The experiment compares complete deployment recipes on the same questions, not isolated architecture, precision or parameter-count factors. SAS uses pretrained Qwen2.5-14B-Instruct Q4_K_M. Resident MAS uses pretrained Qwen2.5-1.5B-Instruct F16 for extraction/source suggestion, 3B F16 for drafting, and 0.5B F16 for verification. All declared MAS model instances stay loaded; there is no role-backbone sharing. Both arms are pretrained: the 8 GB trained adapters are not compatible with the larger SAS checkpoint and are not reused.

Both arms use CPU inference, eight threads, greedy decoding, seed 42, context 4,096 per call, `use_mmap=False`, no GPU layers, the same public evidence packets, and a 2,048 generated-token ceiling per case across stages. Equal ceilings do not mean equal expenditure or equal FLOPs. Prompt-token totals sum all calls and may exceed a single context window. The public packet uses lexical top-eight source-unit retrieval; MAS has the existing source-suggestion stage. Internal prompts/call counts therefore differ.

The primary profile uses the existing 128-token analysis allowance and two fixed training demonstrations, binary review, and no repair. Direct-control removes both analysis and demonstrations. Repair-ablation keeps primary prompting and adds the existing repair/review policy. These are bundled profile contrasts; they do not isolate demonstrations from analysis. No new source catalog, header materialization, adaptive repair method, training or routing was adopted for this evaluation.

All 50 reports were selected by fixed ID hash, excluding recorded earlier development/report exposure; all questions in a chosen report were retained. Scoring annotations were kept separate from sealed public packets. These are public FinQA development-source reports, not the official test split, bank client files, or a guarantee against model pretraining contamination. All output cases remain in denominators, including insufficient answers and withheld outputs.
