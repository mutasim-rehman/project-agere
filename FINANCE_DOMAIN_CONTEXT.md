# Financial Domain Context for Project Agere

**Purpose:** Shared glossary and workflow knowledge so experiments, prompts, metrics, and papers stay grounded in **regulated finance document work**—not generic chat benchmarks.

**Audience:** Anyone building or evaluating **SAS-Quant** vs **MAS-FP16** for local analyst workstations.

**Related:** [`APPLICATION.md`](./APPLICATION.md) · [`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md) · [`sources/regulatory/README.md`](./sources/regulatory/README.md) · [`SYSTEM_GAPS_AND_IMPROVEMENTS.md`](./SYSTEM_GAPS_AND_IMPROVEMENTS.md)

---

## 1. What this project is actually about

Banks, funds, and RIAs often **cannot send KYC files, credit packs, or client PII to cloud LLM APIs**. The default local install is: **one large quantized model** (e.g. 7B–14B Q4) on a **16 GB analyst PC**.

Agere asks whether a **team of smaller full-precision agents** is a better use of the **same RAM and thinking-token budget** for:

1. **KYC / CDD / EDD** case-file preparation  
2. **Credit memo** narrative drafting (from pre-computed numbers)  
3. **Mortgage origination** document Q&A (MortarBench-style)

**Hard rule:** The LLM **drafts and flags**. A human **approves**. The system never onboards a customer, assigns risk rating, files a SAR, or issues credit.

---

## 2. Core acronyms (must know)

| Term | Meaning | Why it matters here |
| :--- | :--- | :--- |
| **KYC** | Know Your Customer | Identity + ownership checks before / during onboarding |
| **CDD** | Customer Due Diligence | Baseline KYC: who they are, what they do, expected activity |
| **EDD** | Enhanced Due Diligence | Extra scrutiny for high-risk customers (PEP, high-risk country, complex ownership) |
| **AML** | Anti-Money Laundering | Detect / report suspicious activity; LLM may **summarise evidence**, not file |
| **SAR / STR** | Suspicious Activity / Transaction Report | Regulatory filing — **human / MLRO only** |
| **MLRO** | Money Laundering Reporting Officer | Compliance owner for SAR decisions |
| **UBO** | Ultimate Beneficial Owner | Natural person who ultimately owns / controls the entity |
| **PEP** | Politically Exposed Person | Higher corruption / bribery risk → usually EDD |
| **CIP** | Customer Identification Program | Collect / verify name, DOB, address, ID number (US framing) |
| **MNPI** | Material Non-Public Information | Insider-type info; AI systems must **segregate** client / deal data |
| **PII** | Personally Identifiable Information | Must stay on-prem; drives local-LLM constraint |
| **RAG** | Retrieval-Augmented Generation | Pull policy / prior case snippets; must be **permissioned** per client |
| **SAS** | Single-Agent System | One generalist model does the whole case |
| **MAS** | Multi-Agent System | Specialists (extract → retrieve → draft → verify) |
| **SAS-Quant** | Quantized monolith | Industry default on analyst RAM |
| **MAS-FP16** | Full-precision specialist team | Agere’s competing deployment |
| **RUPP** | RAM Utilization Parity Protocol | Match peak RSS across arms |

---

## 3. Actors and what they need from the system

| Actor | Job | What “good LLM help” looks like |
| :--- | :--- | :--- |
| **KYC / onboarding analyst** | Assemble case file, flag mismatches | Extracted fields with **source quotes**; discrepancy list; no invented IDs |
| **Credit analyst** | Draft memo narrative | Story that cites **pre-computed** ratios and document lines; human edits and signs |
| **Mortgage underwriter** | Check docs vs policy | Answers to deposit / employment / ULAD-style questions with citations |
| **Compliance / MLRO** | Sample, audit, supervise | Immutable logs of prompts/outputs; clear refusal when data missing |
| **IT / platform** | Deploy local stack | Fits **8 / 16 / 32 GB** RAM; Ollama or llama.cpp; audit trail |

---

## 4. Workflow A — KYC / CDD / EDD case file

### 4.1 Typical inputs (case pack)

- Government ID (passport, national ID, driver’s licence)  
- Proof of address  
- Corporate registry extract / articles  
- Ownership chart / UBO declaration  
- Screening results (sanctions, PEP, adverse media) — often from a **deterministic** screener, not the LLM  
- CRM / application form fields  
- Prior case notes (if any)

### 4.2 What the analyst must produce

1. **Structured profile** — name variants, DOB, nationality, addresses, IDs  
2. **Entity / ownership summary** — who owns whom; UBO % if available  
3. **Screening summary** — hits, false-positive rationale (if policy allows)  
4. **Discrepancy register** — e.g. ID name ≠ registry name; address mismatch  
5. **Risk narrative draft** — for human review (not auto-rating)

### 4.3 Failure modes that matter in exams

| Failure | Example | Metric in Agere |
| :--- | :--- | :--- |
| **Invention** | Model fills missing DOB or invents a registry number | Invention rate |
| **Wrong grounding** | Claims “passport says X” but span is wrong | Grounding accuracy |
| **Missed mismatch** | ID vs registry conflict not flagged | Mismatch recall |
| **Scope creep** | Model “approves” or assigns risk rating | Policy violation (hard fail) |
| **Cross-client bleed** | RAG mixes Client A docs into Client B | Segregation incident |

### 4.4 LLM vs non-LLM responsibilities

| Keep **deterministic / tool** | Allow **LLM** |
| :--- | :--- |
| Sanctions / PEP list match algorithms | Summarise hit text for analyst |
| Exact string / fuzzy ID compare rules | Explain *why* two names may be same person (still cite) |
| Date parsing / field schemas | Narrative CDD summary |
| Risk score engines (if firm has one) | Draft language for human override |

---

## 5. Workflow B — Credit memo drafting

### 5.1 Typical inputs

- Borrower financial statements / spreads  
- **Pre-computed ratios** (DSCR, leverage, liquidity — calculated in Python/Excel, not by the LLM)  
- Collateral description  
- Covenant / facility terms  
- Prior memo templates  

### 5.2 What the system may do

- Draft **Background**, **Business**, **Financial performance**, **Risks**, **Recommendation** sections  
- Insert **cited** figures from the spread sheet / tool output  
- Flag missing sections (“no FY2023 cash flow provided”)  

### 5.3 What the system must not do

- Invent EBITDA, revenue, or covenant headroom  
- Change numeric truth in prose without the calculator tool  
- Auto-approve credit  

### 5.4 Domain terms used in memos

| Term | Plain meaning |
| :--- | :--- |
| **Spread** | Normalised financials (P&L, BS, cash flow) lined up by year |
| **DSCR** | Debt Service Coverage Ratio — cash available vs debt service |
| **Leverage** | Debt / EBITDA or similar |
| **Covenant** | Contractual financial / operational limit |
| **Facility** | The loan / credit line being documented |
| **Collateral** | Assets pledged |
| **Credit officer** | Human who signs the memo |

---

## 6. Workflow C — Mortgage origination document Q&A

Aligned with **MortarBench**-style tasks (Paper 45):

| Question type | Example | Expected output shape |
| :--- | :--- | :--- |
| Boolean | “Does payroll employer match the application?” | Yes/No + citation |
| Transaction list | “List large deposits > $X in period” | Structured list from bank PDF |
| Account / field list | ULAD-style field extraction | Named fields + values + spans |
| Policy check | “Does this deposit pattern violate policy §Y?” | Pass/Fail + policy quote |

**Eval focus:** F1 / accuracy **per question type**, plus confidence filtering — not MMLU.

---

## 7. Why cloud is blocked (compliance framing)

Use this language in Application / Threat Model sections:

1. **Data sensitivity** — KYC IDs, UBO graphs, borrower financials, screening hits, draft SAR text.  
2. **Supervision & records** — FINRA 24-09: GenAI is supervised; third-party models do **not** transfer firm responsibility; prompts/outputs may need retention.  
3. **Segregation** — Shared vector stores across clients / deals create MNPI-like and privacy exam findings.  
4. **Deployment response** — Inference and logs **inside the perimeter** (Ollama / llama.cpp on analyst machines or on-prem GPU).

Official pointers: [`sources/regulatory/README.md`](./sources/regulatory/README.md).

---

## 8. Hardware reality (product constraint)

| Tier | Hardware | Typical deployment |
| :--- | :--- | :--- |
| **8 GB** | Legacy laptop | Small Q4 monolith **or** tiny sequential MAS |
| **16 GB** | Standard bank PC | **Primary study tier** |
| **32 GB** | Power user | Larger Q4 monolith vs bigger FP16 team |

Runtime assumption: **CPU-first** llama.cpp / Ollama. GPU is sensitivity analysis only.

---

## 9. What “good” looks like for Agere metrics

Prefer these over generic accuracy:

| Metric | Definition (finance lens) |
| :--- | :--- |
| **Grounding accuracy** | % of claims with a correct source span |
| **Invention rate** | % of cases with hallucinated amount / date / name / ID |
| **Mismatch recall** | % of planted ID–registry (or doc–form) conflicts flagged |
| **Refusal correctness** | When field missing → system says missing (not “guesses”) |
| **Token efficiency** | Success under fixed thinking-token budget |
| **Latency** | Wall-clock per case (secondary; report, don’t optimise alone) |

**Negative control:** Closed-book multi-hop QA (e.g. FRAMES slice) where a **larger quantized monolith** is *expected* to win — proves we are not cherry-picking only MAS-friendly tasks.

---

## 10. Synthetic data rules (study ethics)

- **No real customer PII** in the repo or training dumps.  
- Use synthetic KYC packs, public templates, and MortarBench-style synthetic docs.  
- Inject controlled mismatches for mismatch-recall measurement.  
- Paper must state: **not a compliance certification**.

---

## 11. Suggested mental model of a correct system

```
Case documents (client-scoped)
        │
        ▼
┌───────────────────┐
│ Extract fields     │  → JSON schema (IDs, dates, names, amounts)
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Deterministic      │  → ratios, string/ID compare, screening APIs
│ tools / calculators│
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Policy RAG         │  → permissioned snippets only
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Draft narrative    │  → cited claims only
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Verify / refuse    │  → quote-check; block inventions
└─────────┬─────────┘
          ▼
   Human analyst / credit officer / MLRO
```

**SAS-Quant:** same stages inside **one** model + tools.  
**MAS-FP16:** same stages as **separate agents** under equal RAM/tokens.

---

## 12. Quick “do we understand the domain?” checklist

- [ ] Can explain CDD vs EDD in one sentence each  
- [ ] Know UBO and why ownership charts matter  
- [ ] Know why SAR filing is never automated  
- [ ] Know why ratios are computed outside the LLM  
- [ ] Know inventing an amount is worse than leaving a blank  
- [ ] Know client-scoped RAG is a hard requirement  
- [ ] Know 16 GB CPU workstation is the primary deployment target  

If any box fails, re-read §§2–8 before writing prompts or claiming results.
