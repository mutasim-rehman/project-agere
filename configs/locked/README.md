# Locked configs

These files are the machine-readable copy of [`../../DEVELOPMENT_START.md`](../../DEVELOPMENT_START.md).

Load these. Do not load `../hardware_tiers/` or `../systems/mas/`.

| File | Contents |
| :--- | :--- |
| `models.yaml` | Hugging Face ids and the GGUF type for each checkpoint |
| `finetune.yaml` | QLoRA hyperparameters and the SAS mixture |
| `problems.yaml` | S*, M*, and X* gaps with the fix to implement |
| `tiers/t1_8gb.yaml` | SAS and MAS at 8 GB |
| `tiers/t2_16gb.yaml` | SAS and MAS at 16 GB. Build this tier first |
| `tiers/t3_32gb.yaml` | SAS and MAS at 32 GB |
