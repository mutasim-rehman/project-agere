# Tier 8 redevelopment: working protocol

Status: development, not a finished experiment or established novelty claim.

## Scope and storage

Storage update, 25 October 2026: code, environments and runtime builds remain
in the repository. New external evaluations read weights and datasets from
`AGERE_SSD_ROOT=/run/media/mutasim/Data/AGERE`; packets, case outputs, logs and
reports stay on that SSD, following the original project storage policy and
the user’s explicit authorization. Historical redevelopment artifacts remain
at their recorded paths; do not rewrite their provenance.
The historical 18–20 October experiment remains unchanged. Its existing test data
is development evidence now; a new sealed evaluation is required for confirmation.

## Candidate contribution

Transactional evidence repair under a joint memory and token ceiling: verified
claims cannot be changed by a repair of unrelated claims. Unsupported patches
are rejected atomically. Study whether this reduces repair-induced regressions
relative to whole-answer regeneration at matched ceilings and actual expenditure.
This is a candidate distinction, not a claim of priority.

## Literature screening, 24 October 2026

Primary-source abstracts inspected:

- Self-Refine: https://arxiv.org/abs/2303.17651 — iterative self-feedback is prior art.
- CRITIC: https://arxiv.org/abs/2305.11738 — tool-feedback correction is prior art.
- CLR: https://arxiv.org/abs/2608.11994 — claim-level verification and compute allocation are prior art.
- BRA-Audit: https://arxiv.org/abs/2608.14668 — budgeted audits and localized recovery are prior art.

Full-method comparison remains necessary, especially BRA-Audit's trusted audit
points. Do not call claim locking novel on the basis of abstracts alone.

## Experiment ladder

1. Verify support checker, patch isolation, token ledger, and runtime constraints.
2. Reconstruct original synthetic development data; add a deterministic-only baseline.
3. Strong compact SAS and functional MAS: constrained structure, source-visible
   verifier, actual delivery gate, deterministic calculator, missing-field resolver.
4. Compare no repair, whole-answer repair, transactional repair, and adaptive routing.
5. Equal development search budgets; paired same-case evaluation; report actual
   tokens, prompt tokens, latency, memory, truncation and repair-induced regressions.
6. Expand beyond fixed key-value templates before claiming practical usefulness.
7. Freeze systems and dataset recipe, evaluate unseen layouts and values, compute
   paired uncertainty, and assess novelty against full papers before completion.

## Guardrails

- Nominal decimal RSS ceiling 6,400,000,000 bytes, lowered if host resources require it.
- CPU inference, native F16 KV, same context and 2,048 total output-token ceiling.
- Simulated 8 GB tier on the current larger host; do not claim physical 8 GB validation.
- Support checker receives source evidence, never labels or evaluation truth.
- Support is weaker than correctness: quoting a valid value for the wrong field
   can pass lexical support. Independent semantic evaluation is mandatory.
- Missing status without evidence of absence remains unresolved, not verified.
- Unit tests and synthetic fault injection do not constitute model research results.
