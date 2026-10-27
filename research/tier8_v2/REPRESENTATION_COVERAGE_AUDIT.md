# Offline reference coverage after the first natural control

This outcome-guided diagnostic uses the unchanged public packets and reference
annotations. It runs no models and does not filter, relabel or rescore cases.
The reserved diagnostic-audit partition is unopened. This is not preregistered.

| Existing source-binding parser outcome | Selection52 /15 reports | Fitting73 /32 reports |
|---|---:|---:|
| Directly mappable annotated program |23|41|
| Of those: unique numeric source mapping |5|19|
| Of those: ambiguous numeric source mapping |18|22|
| Unretrieved numeric operand |16|24|
| Unsupported operation |4|4|
| Numeric literal parsing failure |9|4|

All nine selection numeric parsing failures involve percentage literals. Four
selection programs use table_average/table_max/greater outside the four-operation
runtime. These are exact-reference/parser diagnostics, NOT a task solvability
ceiling: equivalent arithmetic may exist. Ambiguous numeric cells are not assigned
by first match or independently adjudicated for financial relevance.

Existing reported-reference rules classify selection12 as reported/executable
disagreements and7 as unsupported answer syntax; fitting has31 and2 respectively.
They classify33 selection and40 fitting references as number/fraction/percentage
conventions compatible under those rules. Do not interpret unsupported syntax as
semantic incorrectness. Neither answer channel is independently certified.

For example MO/2016/page_10.pdf-1 has reported answer19.8 versus executable122.875
for subtract(122.9,2.5%). This is a concrete unresolved reference conflict, not a
correction proposal. Percent normalization alone does not certify the question's
financial meaning. Preserve both metrics and every selected case.

Only5/52 selection programs have unique numeric bindings in the current catalog,
whereas the original source-binding SFT deliberately requires uniqueness. This
suggests an exposure-gap hypothesis; it does not establish that ambiguity-aware
supervision improves natural QA. Shared source values can have different roles.
Any future training change must use fitting/training reports and a matched control;
these selection annotations must not become new training examples or hand-coded
rules. The current critic comparison, original controls and audit remain unchanged.

[Source and count verification](evidence/representation-coverage-audit-01.json).
Raw per-case diagnostic records remain on SSD under runs/tier8_representation_audit.

Reference-convention clarification: the existing reported metric gives bare integer
answers exact tolerance1e-5, rather than nearest-integer rounding. Two of12
selection disagreements and four of31 fitting disagreements fall within0.5 of a
bare integer reported answer. Those may reflect rounding conventions; they are
not established annotation mistakes. No alternative model scores were computed,
no cases removed and no active metric changed. [Sensitivity evidence](evidence/reference-integer-rounding-sensitivity-01.json).

## First-row data loss and a negative fitting experiment

Inspection of all six changed natural deliveries identified a concrete pipeline
limitation: some first table rows contain data, not just column names. GRMN2008
has first row buildings/improvements39; DISCA2011 embeds subscriber213 inside a
header string. The serializer omits the first row as a unit; the quantity parser
also ignores numeric text on the header side of a colon. Therefore annotated
span coverage can coexist with missing quantities in the catalog. This is a
baseline limitation, not proof that every fully retrieved error has this cause.

Tested a generic variant on fitting73 only: serialize all first-row cells as
column-numbered content, add it to the candidate universe and rerun the same
question-only lexical top-eight selection. Direct-reference mapping stays41/73:
one unretrieved case becomes mappable, while one mappable case loses needed
evidence through displacement. Both transitions and every packet/hash are saved.
This is eight-unit matched, not token-matched; no model or QA gain was measured.
Do not adopt this naive variant or alter the active study. Lossless retention and
retrieval/context packing require a stronger controlled proposal.

[Negative fitting test](evidence/first-row-fitting-test-01.json) ·
[Reproducible offline experiment](experiments/first_row_preservation.py).

## Source-traced materialization prototype, fitting only

A separate prototype keeps the exact retrieved span keys/order, then materializes
raw first-row cells inside one selected table context group. Each appended cell
has its original row/column, normalized text and exact character offsets in a
provenance ledger. No answer/program is an input to the transformation. All73
candidate packets were sealed before reference-based coverage/token diagnostics.
This is outcome-guided exploratory fitting work; it is not blinded confirmation.

Direct reference mapping41→45/73; unique numeric bindings19→22. Four missing-operand
cases recover; no previously mappable case, selected span or old catalog fact is
lost. All source offsets and counts independently rechecked. This differs from
the earlier top-eight reranking variant's one gain/one loss.

Vocabulary-only counts, zero neural forwards: both3B/7B tokenizers show5418 extra
prompt tokens total, median72 and max337 per case. All73 old and new prompts fit
4096 context with the full768-token first-draft reserve plus8. This is NOT a
full-policy context proof, HF/GGUF training parity or a ready SFT dataset.

Eight selected span IDs are preserved, but spans are AUGMENTED CONTEXT GROUPS,
not unmodified original rows. Source origins are explicit in the ledger. Extra
source content/prompt tokens are not information/token matched. AIDs may renumber;
old reference targets/traces cannot be assumed valid for transformed packets.
Three tests cover real first-row recovery, original-fact/input preservation,
colon parsing/provenance, no fabricated column numbers and no text-only injection.

Do not adopt or call this novel: known preprocessing made testable, with potential
coverage benefit requiring fresh controlled neural training/QA. The active SAS/
MAS study and its packets remain unchanged. No selected or reserved-audit cases
were transformed. [Verified fitting result](evidence/header-materialization-fitting-01.json).

Completed MAS outcome join: the net four wrong-delivery reductions versus matched
control are entirely in the16 missing-reference-operand cases; the23 directly
mappable cases have equal aggregate outcomes but one prevented/one introduced
wrong delivery. This is post-hoc association, not a mechanism or semantic proof.
Only4/23 directly mappable initial drafts are reported-correct, so representation
repair alone cannot be assumed to solve generation. These reference-conditioned
categories are unavailable at deployment and must never be used as routing rules
or exclusions. All52 original cases remain in primary results. [Full strata](MATCHED_MAS_SELECTION.md).
