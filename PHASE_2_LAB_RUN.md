# Phase 2 on the lab PC

Phase 2 converts the existing official Hugging Face snapshots on the external SSD into **seven CPU GGUF files** for the 8 GB, 16 GB, and 32 GB tiers. It quantizes the untouched 7B, 14B, and 32B single models to Q4_K_M, retains the team models at F16, and smoke loads both arms under each tier's memory limit. It does not train or score datasets; the 16 GB scored comparison remains the primary research result.

The project checkout, Python environment, llama.cpp source, and CPU build stay on the lab PC. **Every Phase 2 product** goes under the mounted SSD root: models in `weights/gguf/`, and logs, hashes, runtime metadata, and smoke results in `phase2/`.

## Prerequisites

- Mount the Agere SSD. Its `weights/hf/` directory must contain the official 0.5B, 1.5B, 3B, 7B, 14B, and 32B Qwen2.5 Instruct snapshots recorded in the committed source manifest. The drive letter or mount path may differ from the development laptop.
- Install Python 3.11 or 3.12 with `venv` and `pip`, Git, CMake, and a C++ compiler on the lab PC. On Windows, install Visual Studio Build Tools with the C++ desktop workload. On Linux, install a C++ compiler and its standard build tools.
- Ubuntu conversion, smoke, and evaluation runs must use `scripts/lab_run.py`: it creates a bounded systemd user service and delegates its memory controller. See [lab recovery](LAB_RECOVERY.md) for crash evidence, diagnostics, live progress, and logout survival. Windows uses a Job Object.
- Keep at least approximately **133 GiB free on the SSD** before a fresh all-tier conversion. This includes a 10 GiB safety allowance and assumes the 14B and 32B F16 intermediates are removed after their Q4 checksums. The runner recalculates the space needed if it resumes partway through. Allow local space for the Python environment and llama.cpp build; the converter's PyTorch dependency is installed locally. Conversion uses lazy processing but is not guaranteed to fit every host; a guarded failure may require more RAM. A successful 32 GB smoke requires enough actual host memory to load its 32B SAS and resident team below the 25.6 GB process cap while preserving OS headroom.
- Connect the lab PC to the network for the first setup command. It clones pinned llama.cpp `v0.5.0` at commit `7fe450e19305b828c199d602c23a8337aaa1f03b` and installs its conversion requirements. The runner verifies this exact commit before conversion and smoke checks.

## Windows PowerShell commands

Run these in a terminal **on the lab PC**. Replace `X:\AGERE` with the actual mounted SSD path shown on that PC.

```powershell
git clone https://github.com/mutasim-rehman/project-agere.git
Set-Location project-agere
python -m venv .venv
$env:AGERE_SSD_ROOT = 'X:\AGERE'
.\.venv\Scripts\python.exe scripts\phase2.py setup
.\.venv\Scripts\python.exe scripts\phase2.py convert
.\.venv\Scripts\python.exe scripts\phase2.py smoke
```

## Linux commands

Replace `/media/your-user/AGERE` with the actual mount path.

```bash
git clone https://github.com/mutasim-rehman/project-agere.git
cd project-agere
python3 -m venv .venv
export AGERE_SSD_ROOT=/media/your-user/AGERE
.venv/bin/python scripts/phase2.py setup
.venv/bin/python scripts/lab_run.py run -- phase2.py convert
# Wait for the conversion job to finish; check lab_run.py status.
.venv/bin/python scripts/lab_run.py run -- phase2.py smoke
```

The runner prints the resolved checkout and SSD paths at the start of every command and refuses to run if the SSD path is absent or is on the checkout device. The `convert` step hashes all six source snapshots against the committed manifest before it writes GGUF files. It checks tensor extents before reusing GGUF outputs on a rerun; an interrupted partial output is removed before retrying that model. The 14B and 32B F16 intermediates are each removed after their Q4 outputs are checksummed. The 7B F16 file is retained for the 32 GB team.

The `smoke` step runs the 16 GB, 8 GB, then 32 GB tiers. It loads each tier's Q4 SAS alone and each tier's three F16 MAS model **instances together**. The 8 GB MAS deliberately runs two separate 0.5B processes. All inference is CPU only. Nominal process caps are **6.4 / 12.8 / 25.6 GB**; each is lowered by measured idle host use, the configured host reserve (Ubuntu launcher default **4 GiB**, direct Windows minimum **1 GB**), 0.5 GiB fluctuation room, and the outer Ubuntu job ceiling minus 1 GiB runner allowance. The runner applies an aggregate OS cap, monitors process tree RSS and host available memory, and terminates model processes on a breach. Default contexts are **4096 / 8192 / 8192** tokens for the 8 / 16 / 32 GB tiers. If a tier does not fit, rerun that tier with `--tier 8`, `--tier 16`, or `--tier 32` and a lower `--context`; record the resulting context in the later experiment configuration. You can rerun a single arm with `--arm sas` or `--arm mas`. If the lab PC cannot physically hold the 32 GB tier, finish its smoke on a suitably provisioned computer with the same SSD and cloned repository; a restricted cap on a larger computer is only a preparation check, so confirm the final tier on its target hardware during Phase 8.

Do not call Phase 2 complete until all **six** SSD smoke JSON files report `passed`, both arms of each tier use the same context, and `phase2/phase2_summary.json` reports `complete`. Scored 8 GB and 32 GB comparisons remain in Phase 8 after the 16 GB research result is frozen.

## SSD deliverables

```text
AGERE_SSD_ROOT/
  weights/gguf/
    qwen2.5-14b-instruct-q4_k_m.gguf
    qwen2.5-32b-instruct-q4_k_m.gguf
    qwen2.5-7b-instruct-q4_k_m.gguf
    qwen2.5-7b-instruct-f16.gguf
    qwen2.5-3b-instruct-f16.gguf
    qwen2.5-1.5b-instruct-f16.gguf
    qwen2.5-0.5b-instruct-f16.gguf
  phase2/
    logs/                         # setup, conversion, quantization, smoke, and session logs
    manifests/
      runtime.json                # pinned llama.cpp and project revisions
      pip-freeze.txt
      source_verification.json
      gguf_artifacts.json         # final GGUF sizes and SHA-256 checksums
      weights.sha256
    runs/
      smoke_sas_8gb.json
      smoke_mas_8gb.json
      smoke_sas_16gb.json
      smoke_mas_16gb.json
      smoke_sas_32gb.json
      smoke_mas_32gb.json
    phase2_summary.json
```

The `phase2/` directory travels with the SSD to other computers. The `manifests/` directory in the cloned repository contains the earlier Phase 1 input records and is read for source verification; the new Phase 2 records are written to the SSD.
