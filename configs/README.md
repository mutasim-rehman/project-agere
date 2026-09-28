# Configs

**Load [`locked/`](./locked/).** That tree matches [`../DEVELOPMENT_START.md`](../DEVELOPMENT_START.md): three system-RAM tiers (8 / 16 / 32 GB), Qwen2.5-Instruct, SAS at GGUF Q4_K_M, MAS as three F16 models.

`hardware_tiers/`, `systems/mas/quant/`, `systems/mas/ahds/`, and `benchmarks/gaia_tool_slice.yaml` were generated for the superseded GPU VRAM 15-tier factorial. They disagree with the locked model sizes. Do not point a runner at them.
