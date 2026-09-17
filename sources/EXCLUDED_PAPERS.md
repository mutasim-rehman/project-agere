# Excluded Papers (Former 43-Paper Corpus)

The project **narrowed** from a GPU VRAM 2×2 factorial (15 tiers, GAIA/SWE-bench heavy) to **regulated finance on analyst RAM**. Papers below were **removed from the active bibliography** (`INDEX.md`). Legacy Markdown summaries under `literature_review/summaries/` are **archival** only.

## Exclusion criteria

- GPU serving / VRAM saturation / multi-GPU (not analyst RAM)  
- Pure topology benchmarks (debate, ChatDev, SWE-bench) without finance or local deployment link  
- Redundant quantization methods (keep **AWQ** + Bench360 only)  
- Generic knowledge benchmarks (MMLU-Pro) replaced by **workflow grounding** metrics  
- MoE / $q_s$ micro-theory weakly tied to KYC pipelines  

## Dropped papers (former IDs)

| ID | Paper | Reason |
| :---: | :--- | :--- |
| 04 | Mixture-of-Agents | Redundant MAS baseline; MetaGPT + Kim cover orchestration |
| 05 | Rethinking Multi-Agent Discussions (ACL) | Subsumed by Tran token-parity |
| 06 | More Agents Is All You Need | Ensemble sampling; not document workflow |
| 08 | MAS-Orchestra | Orchestration leaderboard; no finance/RAM |
| 09 | AgentVerse | Framework demo |
| 10 | ChatEval | Debate evaluator |
| 12 | ChatDev | Software pipeline |
| 13 | DyLAN | Dynamic pruning; GPU KV focus |
| 14 | ReConcile | Debate |
| 17 | Large Language Monkeys | Inference sampling scale |
| 18 | ToolOrchestra | Cloud cost model |
| 19 | $q_s$ Inequality (MoE) | Micro MoE; marginal for finance app |
| 20 | vLLM | Datacenter GPU serving |
| 21 | Frugal-MoE | MoE routing |
| 23–26, 28–29 | QuaRot, SpinQuant, AQLM, AutoRound, BitNet, QuIP# | Redundant quant stack |
| 30 | SGLang | GPU RadixAttention |
| 31 | GAIA | Replaced by **MortarBench + KYC packs** for application fit |
| 32 | SWE-bench | Wrong domain |
| 33 | FRAMES | **Optional negative control only**—not in active core; download if needed |
| 35 | MMLU-Pro | Wrong metric for grounding |
| 39 | AgentAsk | Edge clarification; not core |
| 40–41, 43 | PolyKV, QKVShare, Warp-Cortex | GPU KV / million-agent scaling |

## Still relevant but not re-downloaded

Papers 33 (FRAMES) and others remain citable from arXiv if the negative-control arm is run; they are omitted from `sources/papers/` to keep the corpus lean.
