# Phase 2 on the lab PC

Phase 2 converts the existing official Hugging Face snapshots on the external SSD into four CPU GGUF files, quantizes the untouched 14B model to Q4_K_M, and smoke loads the SAS and resident MAS arms under the 16 GB tier's memory limit. It does not train or score datasets.

The project checkout, Python environment, llama.cpp source, and CPU build stay on the lab PC. **Every Phase 2 product** goes under the mounted SSD root: models in `weights/gguf/`, and logs, hashes, runtime metadata, and smoke results in `phase2/`.

## Prerequisites

- Mount the Agere SSD. Its root must contain `weights/hf/Qwen--Qwen2.5-{14B,3B,1.5B,0.5B}-Instruct` from Phase 1. The drive letter or mount path may differ from the development laptop.
- Install Python 3.11 or 3.12 with `venv` and `pip`, Git, CMake, and a C++ compiler on the lab PC. On Windows, install Visual Studio Build Tools with the C++ desktop workload. On Linux, install a C++ compiler and its standard build tools.
- Linux smoke runs also require a writable delegated cgroup v2 memory controller so the three resident model processes share an OS enforced cap. The runner reports a clear error if that controller is unavailable. Windows uses a Job Object for the same purpose.
- Keep at least approximately **60 GiB free on the SSD** before a fresh conversion. The runner recalculates the space needed if it resumes partway through. Allow local space for the Python environment and llama.cpp build; the converter's PyTorch dependency is installed locally.
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
.venv/bin/python scripts/phase2.py convert
.venv/bin/python scripts/phase2.py smoke
```

The runner prints the resolved checkout and SSD paths at the start of every command and refuses to run if the SSD path is absent or is on the checkout device. The `convert` step requires the Phase 1 source weights and hashes the 0.5B, 1.5B, 3B, and 14B snapshots against the committed Phase 1 manifest before it writes GGUF files. It resumes completed GGUF outputs on a rerun; an interrupted partial output is removed before retrying that model. The intermediate 14B F16 GGUF is removed after the Q4 output and all four final hashes are recorded.

The `smoke` step loads 14B Q4_K_M alone, then loads 3B, 1.5B, and 0.5B F16 together. All inference is CPU only. It computes an effective process cap from **12.8 GB nominal**, measured idle host use, and a **1 GB host safety reserve**, monitors process tree RSS and host available memory, and terminates the model processes if either limit is crossed. It starts with the locked 8192 token context for each model. If memory does not fit, rerun the smoke command with `--context 4096` or `--context 2048`; record the resulting context in the later experiment configuration before using those models for paper results. You can rerun a single arm with `--arm sas` or `--arm mas`.

Do not call Phase 2 complete until both SSD smoke JSON files report `passed` at the **same context** and `phase2/phase2_summary.json` reports `complete`.

## SSD deliverables

```text
AGERE_SSD_ROOT/
  weights/gguf/
    qwen2.5-14b-instruct-q4_k_m.gguf
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
      smoke_sas_16gb.json
      smoke_mas_16gb.json
    phase2_summary.json
```

The `phase2/` directory travels with the SSD to other computers. The `manifests/` directory in the cloned repository contains the earlier Phase 1 input records and is read for source verification; the new Phase 2 records are written to the SSD.
