# Regulatory & Industry Context (Not Peer-Review PDFs)

Use these to justify **why cloud LLMs are blocked** and **who the end user is**. Cite official sources in the paper’s Application / Threat Model section.

| Source | URL | Relevance |
| :--- | :--- | :--- |
| FINRA Regulatory Notice 24-09 | https://www.finra.org/rules-guidance/notices/24-09 | GenAI governance, supervision, records; third-party LLM does not transfer responsibility |
| FINRA 2026 Oversight Report (GenAI) | https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/gen-ai | Prompt/output logging, model versioning |
| SEC/FINRA books & records (17a-4, 4511) | https://www.finra.org/rules-guidance/key-topics/books-records | Retention and audit of AI-assisted communications |
| Skadden (2026) MNPI & AI models | https://www.skadden.com/insights/publications/2026/07/when-ai-models-access-nonpublic-information | MNPI segregation for research/trading AI—analogous firewall logic for deal rooms |

**Implication for Agere:** The **buyer** is a firm that must keep **inference and logs inside the perimeter**. The study assumes **on-prem Ollama/llama.cpp**, not a vendor API.
