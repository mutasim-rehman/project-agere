# Configs

Load [`locked/`](./locked/). That tree matches [`../DEVELOPMENT_START.md`](../DEVELOPMENT_START.md): three physical-RAM tiers (8 / 16 / 32 GB), Qwen2.5-Instruct, SAS at GGUF Q4_K_M, and MAS as three F16 models. The nominal aggregate process RSS caps are 6.4 / 12.8 / 25.6 GB; measure idle host use before each run and lower the cap if needed to preserve OS/background memory. Caps are limits, not utilization targets.
