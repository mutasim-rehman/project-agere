# Application Area: Regulated Finance on Analyst Workstations

## Who uses this

| Stakeholder | Role | Constraint |
| :--- | :--- | :--- |
| **Compliance / IT (buyer)** | Commercial banks, emerging market institutions (e.g., Pakistani banks under SBP/FATF rules), private-credit funds, RIAs, fintech onboarding teams | Cannot send KYC files, credit packs, or client PII to public cloud LLM APIs (GDPR, DORA, Reg S-P, SBP BPRD/Cybersecurity directives, FINRA 24-09, MNPI policies) |
| **KYC / credit analyst (user)** | Prepares case files and memo drafts; **human signs off** | Standard **16 GB RAM** office PC, often **CPU-only** (llama.cpp / Ollama), no datacenter GPU |
| **MLRO / supervisor** | Reviews audit trail and sampling | Needs cited evidence, refusal on missing data, immutable logs—not leaderboard accuracy |

## What problem they face today

The default local install is: **quantize the largest single model that fits in RAM** (e.g., 14B Q4 on 16 GB). That model drafts KYC summaries and credit narratives but:

- **Invents amounts** and fills gaps when documents are incomplete (finance-specific hallucination risk).
- **Mixes extraction and judgment** in one generalist, so errors are hard to attribute in an exam.
- **Competes with multi-agent designs** (extract → retrieve policy → draft → verify) that use the **same RAM** but split roles—**no published RAM + thinking-token parity study** in this workflow.

## Research question (original Agere formulation)

> **Can a multi-agent system of smaller, full-precision LLMs outperform a single larger, quantized LLM when both use the same host-adjusted process-tree RSS cap—after reserving physical RAM for the OS/background tasks—and the same thinking-token budget?**

Domain glossary: [`FINANCE_DOMAIN_CONTEXT.md`](./FINANCE_DOMAIN_CONTEXT.md). Gap list and improve-then-compare loop: [`SYSTEM_GAPS_AND_IMPROVEMENTS.md`](./SYSTEM_GAPS_AND_IMPROVEMENTS.md).

## Primary workflow under study

**KYC/CDD case-file preparation** (primary) and **credit-memo narrative drafting** (secondary): multi-document ingest, structured extraction, discrepancy flags, **citation-grounded draft**, verifier pass. The LLM **does not** approve customers, assign risk ratings, or file SARs.

## Evaluation focus (not generic benchmarks)

- Uncited or wrong field values vs. source documents  
- Invented currency amounts / dates  
- Missed ID–registry mismatches  
- Analyst time-to-review (optional)  
- **Negative control:** closed-book factual QA where a larger quantized monolith should win  

## Deployment stack (study assumption)

- **Runtime:** llama.cpp or Ollama on Windows/Linux analyst machines  
- **Parity:** equal process-tree peak RSS cap (weights + KV + runtime) per physical RAM tier, after an OS/background reserve; equal **thinking tokens** per case (Tran & Kiela protocol)
- **MAS modes:** (1) all agents resident; (2) sequential load/unload (real laptop behavior)—reported separately  

## RAM tiers (study design)

| Tier | Physical RAM / nominal job RSS ceiling | Example locked comparison | Typical use |
| :--- | :--- | :--- | :--- |
| **8 GB** | 8 GB / **6.4 GB** | 7B Q4 SAS vs. resident 1.5B + 0.5B + 0.5B FP16 MAS | Legacy analyst laptop; smoke-test and reduce context/team if needed |
| **16 GB** | 16 GB / **12.8 GB** | 14B Q4 SAS vs. resident 3B + 1.5B + 0.5B FP16 MAS | Standard bank workstation; **primary research tier** |
| **32 GB** | 32 GB / **25.6 GB** | 32B Q4 SAS vs. resident 7B + 3B + 0.5B FP16 MAS | Power user / team lead; secondary tier |

These are ceilings, not targets: reserve at least 20% of physical RAM for the OS and background work, then lower the job cap if the host's measured idle use plus a 1 GB safety margin requires it. The full inference process tree, including runtime and KV cache, must fit under that effective cap.
