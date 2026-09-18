# Financial Domain Context for Project Agere

**Purpose:** Comprehensive glossary, compliance frameworks, regulatory directives, and operational workflows for **regulated finance document work** on resource-constrained analyst workstations, specifically featuring **Pakistan's banking and financial sector** as an exemplar of emerging market constraints alongside global standards.

**Audience:** AI researchers, software engineers, compliance officers, and IT architects building or evaluating **SAS-Quant** (Single-Agent Quantized monolith) vs **MAS-FP16** (Multi-Agent Full-Precision team) under strict RAM and token parity.

**Related Documentation:** [`APPLICATION.md`](./APPLICATION.md) · [`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md) · [`sources/regulatory/README.md`](./sources/regulatory/README.md) · [`SYSTEM_GAPS_AND_IMPROVEMENTS.md`](./SYSTEM_GAPS_AND_IMPROVEMENTS.md)

---

## 1. What This Project Is Actually About

Banks, asset managers, non-banking financial institutions (NBFCs), and microfinance lenders deal with non-public, high-liability data: national identity records, tax filings, audited financial statements, credit bureau feeds, and sanctions screening hits. They **cannot transmit customer Personally Identifiable Information (PII) or confidential corporate packs to public cloud LLM APIs** due to strict legal, jurisdictional, and regulatory data sovereignty mandates.

The standard local deployment default is: **download the largest open-weights model that can fit into analyst workstation RAM when quantized** (e.g., 7B to 14B parameters compressed to 4-bit integer weights like GGUF `Q4_K_M`) and run it via local runtimes such as `llama.cpp` or `Ollama` on standard **16 GB RAM** office desktops without enterprise GPUs.

**Project Agere** challenges this default:
> **Does a multi-agent team of smaller, full-precision models (MAS-FP16) outperform a single larger quantized generalist model (SAS-Quant) when both systems are constrained to the exact same peak resident RAM (RSS) and the exact same thinking-token budget?**

**Cardinal Rule of the System:**
The AI system **drafts, extracts, flags discrepancies, and cites evidence**. A licensed **human officer (credit underwriter, compliance officer, or MLRO) retains sole decision-making authority**. The AI system must **never** autonomously approve credit, assign regulatory risk ratings, clear sanction alerts, or generate and file regulatory suspicious transaction filings without human sign-off.

---

## 2. Core Financial & Compliance Acronyms

| Term | Full Name | Operational Meaning in Regulated Banking | Relevance to Project Agere |
| :--- | :--- | :--- | :--- |
| **KYC** | Know Your Customer | Mandatory statutory process of identifying and verifying customer identity before opening accounts or conducting ongoing business. | Ingestion and cross-verification of identity documents, addresses, and corporate authorities. |
| **CDD** | Customer Due Diligence | Baseline screening and risk profiling: identifying the customer, verifying identity using independent sources, and understanding business purpose. | Extracting stated turnover, business nature, and validating against registry disclosures. |
| **EDD** | Enhanced Due Diligence | Heightened investigation required for high-risk accounts (PEPs, high-net-worth cross-border flows, sanctioned regions, non-face-to-face entities). | Complex multihop corporate hierarchy resolution and adverse media reconciliation. |
| **AML / CFT** | Anti-Money Laundering / Countering Financing of Terrorism | Legal and regulatory regimes designed to prevent criminals from disguising illegally obtained funds or financing terror networks. | Ensuring trace evidence and screening hits are preserved without hallucinated clearances. |
| **STR / CTR** | Suspicious Transaction Report / Currency Transaction Report | Statutory filings mandated when transactions are suspected of illicit origin, or cash transactions exceed legal thresholds. | AI prepares factual evidence summaries for human compliance review; **never auto-files**. |
| **MLRO** | Money Laundering Reporting Officer | The designated officer within a financial institution legally responsible for regulatory compliance and AML reporting. | Primary consumer of the audit trail, citation verification, and compliance refusal outputs. |
| **UBO** | Ultimate Beneficial Owner | The natural person(s) who ultimately own or control ≥10% to 25% of shares, voting rights, or control of a legal entity. | Multi-tier entity graph resolution (e.g., Company A owned by HoldCo B, owned by Person C). |
| **PEP** | Politically Exposed Person | Individuals entrusted with prominent public functions, their family members, and close associates, presenting elevated corruption risk. | Mandatory discrepancy checks between declared background and public screening databases. |
| **MNPI** | Material Non-Public Information | Confidential financial or strategic information not yet disclosed to the public that could impact securities valuation or creditworthiness. | Requires strict local firewalling; multi-tenant vector databases risk cross-deal data leakage. |
| **PII** | Personally Identifiable Information | Any data identifying an individual (national identity numbers, tax IDs, biometric data, home addresses, salary details). | Core justification for running local LLMs on-premise instead of commercial cloud APIs. |
| **SBP** | State Bank of Pakistan | The central bank and apex regulator of banking, payment systems, and foreign exchange in Pakistan. | Issues AML/CFT regulations, Enterprise Risk Management frameworks, and BPRD circulars. |
| **SECP** | Securities and Exchange Commission of Pakistan | The apex regulator of non-banking finance, capital markets, corporate registries, and insurance in Pakistan. | Governs corporate disclosures, beneficial ownership registers, and NBFC lending. |
| **FMU** | Financial Monitoring Unit | Pakistan's autonomous Financial Intelligence Unit (FIU) established under the AML Act 2010 to receive and analyze STRs/CTRs. | Regulated recipient of STRs prepared by bank compliance departments. |
| **CNIC / SNIC** | Computerized / Smart National Identity Card | The 13-digit unique national identity document issued by NADRA (Pakistan). | Key anchor for identity verification, credit bureau inquiries, and registry matches. |
| **e-CIB** | Electronic Credit Information Bureau | The central credit reporting bureau managed by the State Bank of Pakistan recording historical credit defaults and facilities. | Primary credit bureau report referenced in Pakistani credit approval memos. |
| **NTN** | National Tax Number | Unique tax identification number issued by the Federal Board of Revenue (FBR) in Pakistan. | Verification field reconciling tax returns with declared loan application income. |
| **PRs** | Prudential Regulations | Specific regulatory rulebooks issued by SBP governing corporate, SME, consumer, and housing finance. | Hard regulatory limits (e.g., maximum debt-burden ratios, margin requirements) checked by AI. |
| **FATF** | Financial Action Task Force | Global money laundering and terrorist financing watchdog setting international standards (40 Recommendations). | Drives rigorous audit, documentation, and PEP/AML record-keeping compliance in Pakistan. |
| **SAS-Quant** | Single-Agent System (Quantized) | A single monolithic model (e.g., 7B–14B) compressed to 4-bit integer precision running end-to-end tasks. | The prevailing industry baseline for local deployment on 16 GB analyst machines. |
| **MAS-FP16** | Multi-Agent System (Full Precision) | A coordinated team of smaller specialized models (e.g., 1.5B–3B) running at native 16-bit precision. | The focal experimental architecture tested by Project Agere. |
| **RUPP** | RAM Utilization Parity Protocol | Strict memory benchmarking standard matching peak Resident Set Size (RSS) between competing architectures. | Prevents architectural comparisons from being confounded by unequal hardware allocations. |

---

## 3. The Regulated Banking Context of Pakistan

To understand why Project Agere is transformative for emerging and developing economies, consider Pakistan's banking sector as a premier real-world case study.

### 3.1 Regulatory Landscape & Key Authorities

1. **State Bank of Pakistan (SBP):**
   - **AML/CFT/CPF Regulations:** Mandate stringent Customer Due Diligence, Beneficial Ownership identification, and Continuous Transaction Monitoring for all commercial, Islamic, and microfinance banks.
   - **Prudential Regulations (PRs):** Separate rulebooks exist for Corporate & Commercial Banking, Small & Medium Enterprises (SME), Consumer Financing, and Infrastructure/Housing Finance. Each specifies strict ratios such as the **Debt Burden Ratio (DBR)** (typically capped at 50% for consumers), minimum **Current Ratios**, and clean **e-CIB** requirements.
   - **Framework on Enterprise Risk Management & Outsourcing:** Prohibits sharing customer core banking data and sensitive PII with unregulated external entities or offshore data centers without explicit SBP clearance.
2. **Securities and Exchange Commission of Pakistan (SECP):**
   - Regulates corporate formation (Form 29 / Form A / Form 45 for company directors, shareholding, and UBO declarations).
   - Oversees Non-Banking Financial Companies (NBFCs), Modarabas, mutual funds, and digital nano-lenders.
   - Enforces the **Companies (Substantial Acquisition of Voting Shares and Takeovers) Regulations** and Anti-Money Laundering Regulations across capital markets.
3. **Financial Monitoring Unit (FMU):**
   - The central national FIU receiving Suspicious Transaction Reports (STRs) and Currency Transaction Reports (CTRs) under the Anti-Money Laundering Act (AMLA) 2010.
4. **National Database and Registration Authority (NADRA):**
   - Maintains the centralized civil registry of Pakistan. Banks perform digital biometric and demographic verification (Verisys / Bio-Verisys) using the 13-digit CNIC format `XXXXX-XXXXXXX-X`.
5. **Federal Board of Revenue (FBR):**
   - Generates the Active Taxpayers List (ATL) and verifies National Tax Numbers (NTN), wealth statements, and sales tax returns required in credit packaging.

### 3.2 FATF Legacy and the Scrutiny on Compliance

Pakistan’s historical placement on the FATF "Grey List" (and subsequent exit after extensive reforms) permanently institutionalized hyper-vigilance across Pakistani compliance divisions:
- Banks face severe penalties for missed PEP connections, obscured UBO chains, or unverified documentation.
- The volume of documentary scrutiny increased by orders of magnitude: every onboarding now requires multi-source verification across NADRA Verisys, NACTA (National Counter Terrorism Authority) proscribed person lists (Fourth Schedule of Anti-Terrorism Act 1997), United Nations Security Council (UNSC) consolidated sanctions lists, and SBP circular directives.
- Consequently, compliance departments spend hundreds of thousands of human-hours manually reading scanned CNICs, salary slips, tax forms, and company registration certificates to detect discrepancies.

### 3.3 Data Sovereignty & Cross-Border Cloud Bans

Under SBP banking regulations and Pakistan's **Personal Data Protection Bill / National Cyber Security Policy**, commercial banks are strictly restrained from routing customer PII across geographical borders:
- Transmitting bank statements, salary certificates, CNICs, or credit history to public hyperscaler APIs (such as OpenAI, Anthropic, or Google Cloud endpoints hosted in Europe or North America) constitutes a major regulatory breach.
- Public cloud infrastructure costs in USD impose an unsustainable foreign exchange burden on domestic financial institutions given local currency depreciation.
- Hence, **local on-premise deployment within the bank's internal intranet or on the compliance analyst's desktop PC is the only legally and financially viable path for GenAI adoption**.

### 3.4 Hardware Realities in Pakistani Bank Branches & Head Offices

Unlike Silicon Valley research labs or Wall Street investment banks equipped with multi-GPU clusters, the technological infrastructure of a Pakistani bank's branch or credit hub looks very different:
- **Analyst Workstations:** Typically standard corporate business desktops (e.g., Intel Core i5/i7 10th–12th Gen, 8 GB to 16 GB of DDR4 RAM, integrated or low-end OEM graphics cards, spinning HDDs or modest SSDs).
- **Core Server Rooms / On-Prem Private Cloud:** Central IT departments manage virtualized blade servers (VMware/Nutanix), where provisioning dedicated enterprise GPUs (e.g., NVIDIA H100 or A100) requires scarce USD capex allocations.
- **Inference Runtime:** Execution must rely heavily on **CPU-first inference** using quantized or small model engines (`llama.cpp`, `Ollama`, or CPU-optimized ONNX/OpenVINO runtimes) fitting squarely within **8 GB, 16 GB, or at most 32 GB of system RAM**.

---

## 4. Key Banking Workflows & How Local LLMs Operate

```
Case Documents (CNIC, FBR, e-CIB, Financials)
                   │
                   ▼
       ┌────────────────────────┐
       │   Field Extraction     │  → Strict JSON Schema (NADRA, NTN, amounts)
       └───────────┬────────────┘
                   ▼
       ┌────────────────────────┐
       │ Deterministic Tools    │  → SBP PR Check (DBR ≤ 50%), Ratio Engine,
       │ & Rule Calculators     │    NADRA check-digit, Sanctions String Match
       └───────────┬────────────┘
                   ▼
       ┌────────────────────────┐
       │ Institutional Policy   │  → Bank Credit Policy, SBP Circulars,
       │ Retrieval (RAG)        │    FATF/FMU Typologies (Scoped Index)
       └───────────┬────────────┘
                   ▼
       ┌────────────────────────┐
       │ Narrative Drafting     │  → Cited Credit Proposal / KYC Case File
       └───────────┬────────────┘
                   ▼
       ┌────────────────────────┐
       │ Independent Verifier   │  → Strict Quote Match, Anti-Hallucination,
       │ & Refusal Gate         │    Missing-Document Flagging
       └───────────┬────────────┘
                   ▼
     Human Analyst / Underwriter / Credit Committee (Mandatory Sign-off)
```

### 4.1 Workflow A: Account Opening & KYC / CDD / EDD Case-File Assembly

#### The Real-World Task:
An applicant requests a current or commercial account at a bank branch in Karachi or Lahore. The onboarding desk receives:
1. Copy of CNIC / SNIC / NICOP (Overseas Pakistani).
2. Proof of income or business engagement (Salary slip, employer letter, or business letterhead).
3. Utility bill (Electricity/Gas) for residential verification.
4. For corporate accounts: SECP Certificate of Incorporation, Memorandum & Articles of Association, SECP Form 29 / Form A (list of officers/directors), and Form 45 (Declaration of Ultimate Beneficial Ownership).
5. Deterministic screening outputs: NADRA Verisys response slip, NACTA 4th Schedule match log, UN sanctions hit sheet, and internal cautionary/black-list queries.

#### What the Local System Produces:
- A standardized **KYC Summary Sheet** compiling verified identity parameters.
- An **Ownership Hierarchy Tree** calculating cumulative direct and indirect equity to identify any individual controlling ≥25% (or SBP's stricter 10% threshold for sensitive structures) as the UBO.
- A **Discrepancy Register**: flagging if the director name on Form 29 differs slightly in spelling from the NADRA CNIC, or if the residential address on the utility bill belongs to a different postal jurisdiction.
- A **Case Narrative Draft**: summarizing the economic rationale of the account and source of funds for final review by the Branch Manager and Branch Compliance Officer (BCO).

#### Catastrophic AI Failure Modes:
- **Inventing National IDs / Tax Numbers:** A quantized generalist model hallucinations an arbitrary 13-digit CNIC when a scanned image is blurry.
- **Hallucinating PEP Clearance:** Claiming a customer is "cleared of PEP exposure" when the screening document was actually absent from the file.
- **Missing Inconsistent Dates:** Failing to catch that a passport expired prior to the date on an authorization resolution.

### 4.2 Workflow B: Corporate & SME Credit Memo Drafting (Credit Proposal / e-Credit Application)

#### The Real-World Task:
An SME textile manufacturer in Faisalabad applies for a PKR 100 Million Working Capital (Running Finance) facility. The credit underwriting team processes:
1. Three years of audited financial statements (Balance Sheet, Profit & Loss, Cash Flow).
2. Recent 12-month bank statements from all operational accounts across commercial banks.
3. SBP **e-CIB** report detailing existing funded and non-funded exposures, past overdue payments, write-offs, or clean payment histories across the entire financial sector.
4. Collateral evaluation report from an SBP-approved third-party surveyor (hypothecation of plant & machinery, mortgage of industrial property).
5. Tax compliance records: FBR Active Taxpayer verification and Income Tax return acknowledgments.

#### Division of Labor: Deterministic Engine vs. LLM:
- **Deterministic Python Calculator (Never the LLM):** Computes financial ratios with zero floating-point error:
  - Current Ratio, Quick Ratio, Debt-to-Equity, Debt Service Coverage Ratio (DSCR), Interest Coverage.
  - SBP Prudential Regulation checks: verifying the customer’s total clean exposure across all banks does not breach regulatory ceilings and verifying borrower equity contribution.
- **Local LLM Drafter:**
  - Ingests the computed ratios and synthesizes the qualitative credit memo narrative: **Company Background**, **Industry Analysis**, **Historical Operational Performance**, **Key Financial Strengths & Weaknesses**, **Collateral Adequacy Narrative**, and **Facility Structuring Conditions**.
  - Must insert explicit citations: `[Audited Financials 2024, Page 12, Note 8]` or `[e-CIB Report dated 12-Aug-2026, Section 3.1]`.

#### Catastrophic AI Failure Modes:
- **Hallucinating Ratios / Figures:** Stating in the text that "the borrower maintains a healthy DSCR of 1.85x" when the verified calculator output was 1.12x (violating bank covenants).
- **Inventing Prior Defaults or Clean Records:** Overlooking an active 60-day overdue remark in the e-CIB report, exposing the bank to non-performing loan (NPL) provisioning.
- **Fabricating Collateral Appraisals:** Claiming the forced sale value (FSV) of the mortgaged property covers 150% of the facility when the appraisal report only covered 90%.

### 4.3 Workflow C: Housing Finance & Consumer Credit Origination

#### The Real-World Task:
A salaried individual in Rawalpindi applies for a PKR 15 Million home construction loan under SBP’s housing finance prudential framework (such as the Mera Pakistan Mera Ghar initiative or commercial home loans).

#### Document Checks (MortarBench Style):
- Employment confirmation letter and salary slips vs bank statement deposits.
- Calculation of Debt Burden Ratio (DBR): `(Proposed Monthly Installment + Existing Loan Installments) / Net Monthly Disposable Income`. SBP PR-Consumer mandates DBR must not exceed 50%.
- Title deed / allotment letter verification and legal search report from the bank's panel advocate confirming non-encumbrance.

#### What the Local System Produces:
- Step-by-step verification answers:
  1. *Did the monthly salary credit of PKR 350,000 reflect consistently on the 1st week of each month over the last 6 months?*
  2. *What is the exact calculated DBR under SBP PR-Consumer criteria?*
  3. *Does the legal opinion report contain any adverse title remarks?*

---

## 5. Why Project Agere’s Research Is Specifically Useful for Pakistan

The primary scientific dilemma of Project Agere—**MAS-FP16 (Specialized Small Model Teams) vs. SAS-Quant (Monolithic Quantized Model) on Fixed RAM**—directly solves five existential technological and operational problems faced by Pakistani financial institutions:

### 5.1 Financial Inclusion & SME Lending Acceleration
Over 90% of enterprises in Pakistan are SMEs, yet they receive less than 7% of total private sector credit. Why?
- Traditional credit appraisal is slow, paper-heavy, and manually intensive. Lending to a small enterprise requires analyzing messy, unstandardized tax returns, ledger photos, and bank slips.
- Large banks cannot afford to allocate dedicated credit analysts to PKR 5–20 Million SME loan files because manual underwriting costs exceed the interest margin.
- If a bank can deploy a robust, hallucination-resistant **local AI assistant on standard 16 GB branch PCs**, the turnaround time for SME credit appraisal drops from 21 days to 48 hours. By providing clear evidence-grounded drafts, junior loan officers can process 5x the volume while remaining compliant with SBP SME Prudential Regulations.

### 5.2 Democratizing Enterprise AI Under FX & Currency Constraints
Pakistani commercial banks operate under strict foreign currency reserves and capital expenditure controls:
- Licensing cloud LLM enterprise APIs (such as Azure OpenAI or AWS Bedrock) costs tens of thousands of USD per month in subscription and token consumption fees. With currency exchange volatility, cloud-dependent AI creates unpredictable operating expenditures.
- Purchasing datacenter AI GPUs (e.g., NVIDIA H100/A100 server clusters) requires hundreds of thousands of USD in hard equipment imports subject to import duties and letters of credit.
- **Agere’s research shows banks how to maximize existing capital equipment:** If Agere proves that a structured multi-agent team of 1.5B–3B native full-precision models running on standard 16 GB desktop CPUs achieves superior grounding compared to expensive monolithic models, **banks can deploy state-of-the-art document intelligence using hardware already sitting on their desks**.

### 5.3 Anti-Money Laundering (AML) & FATF Compliance Defense
Regulators do not accept "the AI told us so" as a defense:
- Under SBP and FMU guidelines, every compliance decision must have an accountable, verifiable audit trail.
- If a bank uses an unconstrained single quantized generalist model, the model may exhibit **"sycophancy"** or **"citation theatre"**—generating convincing prose that cites imaginary sections of the Anti-Terrorism Act or fabricates NADRA match dates.
- Agere’s **MAS-FP16 architecture** enforces separation of concerns: an **Extractor Agent** structures raw facts; a **Policy RAG Agent** retrieves strict regulatory clauses; a **Drafter Agent** writes the summary; and a dedicated **Verifier Agent** cross-checks every single claim against source quotes before the human officer ever sees it. This structural boundary verification drastically reduces compliance liability.

### 5.4 Islamic Banking & Shariah Compliance Verification
Pakistan possesses one of the fastest-growing Islamic banking sectors globally (commanding over 20% of banking system assets under institutions like Meezan Bank, Faysal Bank, and Islamic windows of conventional banks):
- Islamic finance requires specialized transaction structures (Murabaha, Ijarah, Diminishing Musharakah, Salam, Istisna) governed by SBP Shariah Governance Frameworks and AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions) standards.
- In Murabaha transactions, the bank must physically or constructively purchase goods before selling them to the customer on deferred payment; execution sequence errors render the contract *Shariah-non-compliant*.
- A monolithic generalist LLM frequently confuses conventional interest-bearing terminology with Islamic financing terms (e.g., referring to "interest rates" instead of "profit rates", or confusing loan schedules with lease rentals).
- A multi-agent framework allows dedicated sub-agents: an **AAOIFI Shariah Checklist Agent** that validates transaction execution milestones and document sequencing independently of the commercial drafter.

### 5.5 Resilience in Low-Connectivity and Regional Branch Networks
A significant portion of Pakistan's banking branches (spanning secondary and tertiary cities such as Gujranwala, Sukkur, Mardan, or Rahim Yar Khan) experience periodic internet outages, high-latency satellite connections, or restricted wide-area network (WAN) bandwidth:
- Cloud-hosted AI architectures fail completely when regional connectivity drops.
- A local LLM architecture running entirely on the branch office local area network (LAN) ensures **uninterrupted business continuity**, allowing credit origination and account onboarding to continue regardless of external connectivity.

---

## 6. Key SBP & Pakistani Banking Regulatory References

Researchers and developers working on Project Agere should cite and align prompts/validations with the following official Pakistani banking frameworks:

1. **State Bank of Pakistan (SBP) AML/CFT/CPF Regulations:**
   - *Regulation 1 (Customer Due Diligence):* Prescribes mandatory identification parameters for individuals, sole proprietors, partnerships, and legal persons.
   - *Regulation 2 (Enhanced Due Diligence):* Defines mandatory conditions for domestic and foreign PEPs and complex high-risk trusts.
   - *Regulation 4 (Record Retention):* Mandates preservation of all identification and transaction records for a minimum of 5 years following account closure.
2. **SBP Prudential Regulations for Corporate / Commercial Banking:**
   - *Regulation G-1 (Governance & Management):* Responsibilities of Board and senior management in credit approval and internal controls.
   - *Regulation R-1 (Limit on Exposure to Single / Group Borrowers):* Maximum limits on clean and collateralized facilities relative to bank equity.
   - *Regulation R-8 (Financial Indicators):* Minimum benchmarks for Current Ratio, Leverage, and Debt Service Coverage Ratios.
3. **SBP Prudential Regulations for Consumer Financing:**
   - *Regulation CF-4 (Debt Burden Ratio - DBR):* Mandatory formula requiring total monthly loan installments across all banks not to exceed 50% of the applicant's verifiable net monthly income.
4. **Securities and Exchange Commission of Pakistan (SECP) Regulations:**
   - *SECP (Anti Money Laundering and Countering Financing of Terrorism) Regulations 2020.*
   - *Companies Act 2017 (Section 452 & Companies (Investment in Associated Companies or Undertakings) Regulations):* Beneficial ownership and related-party disclosure mandates.
5. **Anti-Money Laundering Act 2010 (Pakistan):**
   - *Section 7 (Obligation to file Suspicious Transaction Reports):* Mandates prompt reporting of transactions with no apparent economic justification to the Financial Monitoring Unit (FMU).
6. **NADRA Ordinance 2000 & Verisys Guidelines:**
   - Governs the verification of 13-digit Computerized National Identity Cards (CNIC) and Family Registration Certificates (FRC).

---

## 7. Operational Guidelines for Agere Experiments

When designing synthetic case packs, prompts, and evaluation harnesses under Project Agere, adhere to the following rules:

1. **Synthetic Data Integrity:**
   - **Never use real Pakistani CNICs, tax returns, or bank account statements.**
   - Generate synthetic Pakistani case packs following realistic distributions:
     - 13-digit CNIC format: `35201-XXXXXXX-1` (Province/Division codes for Punjab/Sindh/etc.).
     - 7-digit NTN format: `1234567-8`.
     - Standard bank statement formats mirroring major domestic banks (e.g., HBL, Meezan, MCB, UBL, Bank Alfalah).
     - Financial figures denominated in PKR (Millions / Billions) using South Asian notation or standard international formatting.
2. **Deterministic Computation Separation:**
   - Never allow either SAS or MAS to compute DBR, DSCR, or tax brackets internally in prose. Always route through a deterministic Python helper and require the model to cite the helper's JSON output.
3. **Evaluation Metric Priority for Finance:**
   - **Invention Rate (Hallucination of amounts/IDs):** The single most punitive metric. In an SBP or SECP audit, one fabricated CNIC or falsified financial figure is an instant regulatory finding.
   - **Mismatch Recall:** The system's ability to catch planted discrepancies between documents (e.g., applicant stated income = PKR 400,000; bank statement average inflow = PKR 180,000; or CNIC name = "Muhammad Usman Khan"; utility bill = "Usman Ahmed").
   - **Refusal Correctness:** When a required document (e.g., tax return or Form 29) is omitted from the file, the system must explicitly emit a `MISSING_MANDATORY_DOCUMENT` code rather than fabricating plausibility.
