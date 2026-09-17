# Paper 45 — MortarBench: Evaluating Mortgage Loan Origination Agents

- **File:** [`../../sources/papers/45_MortarBench_Mortgage_Origination_Agents.pdf`](../../sources/papers/45_MortarBench_Mortgage_Origination_Agents.pdf)
- **arXiv:** 2606.19416 (2026)
- **Role:** **Primary empirical benchmark** for regulated document + policy reasoning

## Problem

Loan origination requires agents to answer questions over **bank statements, ULAD fields, and underwriting policy**—boolean, transaction-list, and account-list outputs.

## Method

Synthetic but distribution-faithful documents; SME-filtered question set; reports F1 (~81% strong baselines).

## Relevance to Agere

- Same **compliance-sensitive** domain as KYC (PII, auditable answers).
- Tool-like **document reasoning** where specialist MAS may beat one Q4 generalist.
- Does **not** enforce RAM or token parity between MAS and monolith—our contribution.

## Metrics to mirror

Per-question-type accuracy; confidence filtering gains.

## Cite in paper

Experiments (Track A), Application section (mortgage desk).
