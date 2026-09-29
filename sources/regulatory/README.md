# Regulatory & Industry Context (Not Peer-Review PDFs)

Use these to justify **why cloud LLMs are blocked** and **who the end user is**. Cite official sources in the paper’s Application / Threat Model section.

| Source | URL | Relevance |
| :--- | :--- | :--- |
| FINRA Regulatory Notice 24-09 | https://www.finra.org/rules-guidance/notices/24-09 | GenAI governance, supervision, records; third-party LLM does not transfer responsibility |
| FINRA 2026 Oversight Report (GenAI) | https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/gen-ai | Prompt/output logging, model versioning |
| SEC/FINRA books & records (17a-4, 4511) | https://www.finra.org/rules-guidance/key-topics/books-records | Retention and audit of AI-assisted communications |
| SBP AML/CFT/CPF Regulations | https://www.sbp.org.pk/bprd/2022/CL33-Annex-B.pdf | Core CDD, UBO, PEP, sanctions, reporting, and record-keeping source; issued 2022 and subject to later circulars |
| SBP Consolidated Customer Onboarding Framework | https://www.sbp.org.pk/bprd/2025/C1-Consolidated-Customer-Onboarding-Framework.pdf | Current onboarding requirements for individuals and entities; issued July 25, 2025 |
| SBP Prudential Regulations for SME Financing | https://www.sbp.org.pk/laws-regulations#Regulations | Use the current consolidated file and amendments from SBP's laws-and-regulations index; verify the effective date before building the policy index |
| SBP Prudential Regulations for Corporate / Commercial Banking | https://www.sbp.org.pk/publications/prudential/PRs-IPF-June-24.pdf | Risk Management and Operations (updated June 2024); AML/KYC is covered separately by AML/CFT/CPF regulations |
| FATF Recommendations | https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Fatf-recommendations.html | International AML/CFT/CPF standard; use the version amended June 2026 |
| Skadden (2026) MNPI & AI models | https://www.skadden.com/insights/publications/2026/07/when-ai-models-access-nonpublic-information | MNPI segregation for research/trading AI—analogous firewall logic for deal rooms |

**Implication for Agere:** The **buyer** is a firm that must keep **inference and logs inside the perimeter**. The study assumes **on-prem Ollama/llama.cpp**, not a vendor API.

**Acquisition note:** The policy documents are retrieval inputs and belong under `AGERE_SSD_ROOT/datasets/policy/`; their URLs, source/version dates, and SHA-256 hashes belong in repository manifests. The old `bprd/2020/C1.htm` URL redirected to an unrelated board-minutes circular and has been removed. SBP's and FATF's file hosts returned anti-bot pages to direct downloads during the current staging run, so these policy PDFs still need a successful download before policy-grounded evaluation. The synthetic bank SOP must be authored in the repository and copied to the SSD only as a dataset artifact after review.
