# Walkthrough: Pivot to Finance / System RAM (Sept 2026)

## What changed

1. **Resource axis:** GPU VRAM → **peak system RAM** on analyst PCs (llama.cpp / Ollama).  
2. **Application:** [`APPLICATION.md`](./APPLICATION.md) — KYC/CDD, credit memo drafts, mortgage origination (MortarBench).  
3. **Headline comparison:** **MAS-FP16** vs **SAS-Quant** (not 15-tier GPU factorial).  
4. **Literature:** **16 active papers** in [`sources/papers/`](./sources/papers/); **27 excluded** — see [`sources/EXCLUDED_PAPERS.md`](./sources/EXCLUDED_PAPERS.md).  
5. **Protocol:** [`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md) v3.0 — **RUPP** (RAM Utilization Parity Protocol) + Tran token parity.

## RAM parity (replacing MUPP/VRAM)

- Match **peak RSS** per tier: **8 / 16 / 32 GB**.  
- **Primary tier:** 16 GB (standard compliance analyst workstation).  
- MAS: report **resident** (all agents loaded) vs **sequential** (load/unload per stage).

## Configs status

Existing YAML under `configs/hardware_tiers/` and `configs/systems/mas/*` still reflect the **old VRAM 15-tier** design. **Next implementation step:** regenerate configs for 3 RAM tiers and CPU inference—or treat legacy YAML as archived.

## New downloads

| File | Topic |
| :--- | :--- |
| `sources/papers/44_*` | Financial QA under SME local compute |
| `sources/papers/45_*` | MortarBench mortgage origination agents |

All active PDFs listed in [`sources/INDEX.md`](./sources/INDEX.md).

## Supervisor one-liner

> We tell **compliance IT** whether to install **one big quantized model** or a **team of small full-precision agents** on the same **16 GB RAM** and **token budget** when analysts prepare **KYC files** without cloud LLMs.
