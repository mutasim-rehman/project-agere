"""
Pre-processes all data for the Project Agere Dashboard.
Extracts data from dashboard_handoff, evidence ZIPs, configs, figures, and manifests.
Generates optimized JSON files for the browser-based dashboard.
"""

import os
import sys
import json
import csv
import glob
import shutil
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
HANDOFF_DIR = ROOT_DIR / "dashboard_handoff"
DATA_IN_DIR = HANDOFF_DIR / "data"
EVIDENCE_DIR = HANDOFF_DIR / "evidence"
CONFIGS_DIR = ROOT_DIR / "configs"
FIGURES_DIR = ROOT_DIR / "figures"
MANIFESTS_DIR = ROOT_DIR / "manifests"

OUT_DIR = ROOT_DIR / "dashboard"
OUT_DATA_DIR = OUT_DIR / "data"
OUT_FIG_DIR = OUT_DIR / "figures"

def log(msg):
    print(f"[prepare_data] {msg}")

def ensure_dirs():
    OUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FIG_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DATA_DIR / "tier16_v2").mkdir(parents=True, exist_ok=True)
    (OUT_DATA_DIR / "le16_v2").mkdir(parents=True, exist_ok=True)
    (OUT_DATA_DIR / "paper").mkdir(parents=True, exist_ok=True)

def copy_handoff_tables():
    log("Copying handoff tables from dashboard_handoff/data/...")
    count = 0
    for root, dirs, files in os.walk(DATA_IN_DIR):
        rel = Path(root).relative_to(DATA_IN_DIR)
        dest_parent = OUT_DATA_DIR / rel
        dest_parent.mkdir(parents=True, exist_ok=True)
        for f in files:
            src = Path(root) / f
            dst = dest_parent / f
            shutil.copy2(src, dst)
            count += 1
    log(f"Copied {count} handoff data files.")

def copy_figures():
    log("Copying figures...")
    count = 0
    for category in ["paper", "tier16_v2", "tier8"]:
        src_cat = FIGURES_DIR / category
        dst_cat = OUT_FIG_DIR / category
        dst_cat.mkdir(parents=True, exist_ok=True)
        if src_cat.exists():
            for f in src_cat.iterdir():
                if f.is_file():
                    shutil.copy2(f, dst_cat / f.name)
                    count += 1
    log(f"Copied {count} figures.")

def extract_hardware_benchmarks():
    log("Extracting conversion & quantization benchmarks from phase2-001.zip...")
    zpath = EVIDENCE_DIR / "phase2-001.zip"
    benchmarks = []
    if zpath.exists():
        with zipfile.ZipFile(zpath) as zf:
            for n in zf.namelist():
                if n.endswith(".memory.json"):
                    try:
                        data = json.loads(zf.read(n).decode("utf-8"))
                        fname = Path(n).name
                        op_type = "quantize" if "quantize" in fname else "convert"
                        model_size = fname.replace("convert_", "").replace("quantize_", "").replace(".memory.json", "")
                        benchmarks.append({
                            "file": n,
                            "operation": op_type,
                            "model_size": model_size,
                            "peak_rss_bytes": data.get("peak_rss_bytes", 0),
                            "peak_rss_gb": round(data.get("peak_rss_bytes", 0) / (1024**3), 3),
                            "cap_bytes": data.get("cap_bytes", 0),
                            "cap_gb": round(data.get("cap_bytes", 0) / (1024**3), 2),
                            "recorded_at_utc": data.get("recorded_at_utc"),
                            "oom_events": 0 if "oom 0" in data.get("cgroup_memory_events", "") else 1
                        })
                    except Exception as e:
                        pass
    out_file = OUT_DATA_DIR / "hardware_benchmarks.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(benchmarks, f, indent=2)
    log(f"Saved {len(benchmarks)} hardware benchmark points.")

def extract_model_architectures():
    log("Extracting model metadata from weights-001.zip...")
    zpath = EVIDENCE_DIR / "weights-001.zip"
    models = []
    if zpath.exists():
        with zipfile.ZipFile(zpath) as zf:
            for n in zf.namelist():
                if n.endswith("config.json") and "weights/hf/Qwen" in n:
                    try:
                        data = json.loads(zf.read(n).decode("utf-8"))
                        model_id = Path(n).parent.name
                        models.append({
                            "model_id": model_id,
                            "architecture": data.get("architectures", ["Qwen2ForCausalLM"])[0],
                            "hidden_size": data.get("hidden_size"),
                            "num_hidden_layers": data.get("num_hidden_layers"),
                            "num_attention_heads": data.get("num_attention_heads"),
                            "num_key_value_heads": data.get("num_key_value_heads"),
                            "vocab_size": data.get("vocab_size"),
                            "max_position_embeddings": data.get("max_position_embeddings"),
                            "torch_dtype": data.get("torch_dtype", "bfloat16")
                        })
                    except Exception:
                        pass
    # Sort by model size
    models.sort(key=lambda x: x.get("hidden_size") or 0)
    out_file = OUT_DATA_DIR / "model_architectures.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(models, f, indent=2)
    log(f"Saved {len(models)} model architecture specs.")

def extract_memory_timelines():
    log("Extracting and downsampling memory timelines from runs ZIPs...")
    timelines = {}
    
    # We will search runs-003 and runs-004 for the main 16 GB recovery runs
    target_zips = [EVIDENCE_DIR / f"runs-{i:03d}.zip" for i in range(1, 11)]
    
    for zpath in target_zips:
        if not zpath.exists():
            continue
        with zipfile.ZipFile(zpath) as zf:
            for n in zf.namelist():
                if n.endswith("memory.jsonl") and "lab-16-115gb" in n:
                    # e.g. runs/lab_tiers_v1/lab-16-115gb-recovery-02/tier16-sas-direct_control/attempt-0002/memory.jsonl
                    parts = n.split("/")
                    job_name = ""
                    attempt = ""
                    for p in parts:
                        if p.startswith("tier16-"):
                            job_name = p
                        if p.startswith("attempt-"):
                            attempt = p
                    if not job_name:
                        continue
                    key = f"{job_name}/{attempt}"
                    if key in timelines:
                        continue
                    
                    # Read lines
                    samples = []
                    with zf.open(n) as mf:
                        for line in mf:
                            try:
                                d = json.loads(line.decode("utf-8"))
                                samples.append((d.get("time", 0), d.get("tree_rss_bytes", 0), d.get("tree_swap_bytes", 0)))
                            except Exception:
                                pass
                    if not samples:
                        continue
                    
                    # Downsample to ~80 evenly spaced points
                    t0 = samples[0][0]
                    t_end = samples[-1][0]
                    duration = max(t_end - t0, 1.0)
                    
                    target_points = 80
                    step = max(1, len(samples) // target_points)
                    downsampled = []
                    for i in range(0, len(samples), step):
                        t, rss, swap = samples[i]
                        downsampled.append({
                            "rel_sec": round(t - t0, 1),
                            "rss_gb": round(rss / (1024**3), 3),
                            "swap_mb": round(swap / (1024**2), 2),
                            "rss_bytes": rss,
                            "swap_bytes": swap
                        })
                    
                    peak_rss_gb = round(max((s[1] for s in samples), default=0) / (1024**3), 3)
                    max_swap_mb = round(max((s[2] for s in samples), default=0) / (1024**2), 2)
                    swap_breach = max_swap_mb > 0.0
                    
                    timelines[key] = {
                        "job": job_name,
                        "attempt": attempt,
                        "total_samples": len(samples),
                        "duration_sec": round(duration, 1),
                        "peak_rss_gb": peak_rss_gb,
                        "max_swap_mb": max_swap_mb,
                        "swap_breach": swap_breach,
                        "data": downsampled
                    }
                    log(f"  Processed memory for {key}: {len(samples)} samples -> {len(downsampled)} points (peak: {peak_rss_gb} GB, swap: {max_swap_mb} MB)")

    out_file = OUT_DATA_DIR / "memory_timelines.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(timelines, f, indent=2)
    log(f"Saved {len(timelines)} memory timeline series.")

def extract_case_details():
    log("Extracting rich case drill-down samples from cases.jsonl in runs ZIPs...")
    case_samples = {}
    
    # Check runs-004 and runs-003
    for zi in [4, 3, 5]:
        zpath = EVIDENCE_DIR / f"runs-{zi:03d}.zip"
        if not zpath.exists():
            continue
        with zipfile.ZipFile(zpath) as zf:
            for n in zf.namelist():
                if n.endswith("cases.jsonl") and "lab-16-115gb-recovery-02" in n:
                    parts = n.split("/")
                    job_name = [p for p in parts if p.startswith("tier16-")]
                    job = job_name[0] if job_name else "tier16"
                    
                    count = 0
                    with zf.open(n) as cf:
                        for line in cf:
                            if count >= 30: # keep up to 30 rich cases per job
                                break
                            try:
                                c = json.loads(line.decode("utf-8"))
                                cid = c.get("case_id")
                                if not cid:
                                    continue
                                
                                # Extract clean answer structure
                                ans = c.get("answer", {})
                                steps = ans.get("steps", []) if isinstance(ans, dict) else []
                                formula = ""
                                if steps:
                                    step_strs = []
                                    for s in steps:
                                        op = s.get("op", "")
                                        l_val = s.get("left", {}).get("value", "") if isinstance(s.get("left"), dict) else str(s.get("left"))
                                        r_val = s.get("right", {}).get("value", "") if isinstance(s.get("right"), dict) else str(s.get("right"))
                                        step_strs.append(f"{l_val} {op} {r_val}")
                                    formula = " -> ".join(step_strs)
                                
                                key = f"{job}/{cid}"
                                case_samples[key] = {
                                    "job": job,
                                    "case_id": cid,
                                    "active_roles": c.get("active_roles", []),
                                    "decision": ans.get("decision") if isinstance(ans, dict) else "UNKNOWN",
                                    "answer_unit": ans.get("answer_unit") if isinstance(ans, dict) else "",
                                    "formula": formula,
                                    "steps_count": len(steps),
                                    "steps": steps[:4], # first 4 steps
                                    "analysis_notes": c.get("analysis_notes")
                                }
                                count += 1
                            except Exception:
                                pass
    
    out_file = OUT_DATA_DIR / "case_predictions_sample.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(case_samples, f, indent=2)
    log(f"Saved {len(case_samples)} rich case prediction details.")

def extract_configs_and_manifests():
    log("Processing configs, manifests, and documentation index...")
    
    # 1. Configs
    configs_summary = {
        "tiers": {
            "t1_8gb": {
                "name": "8 GB Tier",
                "physical_ram_gb": 8,
                "nominal_cap_gb": 6.4,
                "os_reserve_gb": 1.6,
                "sas_model": "Qwen2.5-7B-Instruct (GGUF Q4_K_M)",
                "mas_models": [
                    "Qwen2.5-0.5B-Instruct (F16)",
                    "Qwen2.5-1.5B-Instruct (F16)",
                    "Qwen2.5-3B-Instruct (F16)"
                ]
            },
            "t2_16gb": {
                "name": "16 GB Tier (Primary)",
                "physical_ram_gb": 16,
                "nominal_cap_gb": 12.8,
                "os_reserve_gb": 3.2,
                "sas_model": "Qwen2.5-14B-Instruct (GGUF Q4_K_M)",
                "mas_models": [
                    "Qwen2.5-1.5B-Instruct (F16 - Extractor)",
                    "Qwen2.5-7B-Instruct (F16 - Drafter)",
                    "Qwen2.5-3B-Instruct (F16 - Verifier)"
                ]
            },
            "t3_32gb": {
                "name": "32 GB Tier (Unevaluated)",
                "physical_ram_gb": 32,
                "nominal_cap_gb": 25.6,
                "os_reserve_gb": 6.4,
                "sas_model": "Qwen2.5-32B-Instruct (GGUF Q4_K_M)",
                "mas_models": [
                    "Qwen2.5-3B-Instruct (F16)",
                    "Qwen2.5-14B-Instruct (F16)",
                    "Qwen2.5-7B-Instruct (F16)"
                ]
            }
        },
        "profiles": {
            "primary": "Standard deployment: Drafter generates program, Verifier audits, conditional repair.",
            "direct_control": "Negative control: No verifier audit, program drafted directly without repair step.",
            "repair_ablation": "Ablation: Verifier audits and flags errors, but Drafter repair is disabled."
        },
        "protocol": {
            "ram_parity": "Strict host-adjusted process-tree RSS cap (RUPP protocol).",
            "token_parity": "Matched thinking-token budget per task instance (Tran & Kiela 2026 cap).",
            "eval_framework": "Dual correctness (Reported-answer match + Raw execution match)."
        }
    }
    with open(OUT_DATA_DIR / "configs_summary.json", "w", encoding="utf-8") as f:
        json.dump(configs_summary, f, indent=2)

    # 2. Manifests
    manifests = {}
    for mf in ["downloaded_datasets.json", "hf_snapshots.json", "synthetic_datasets.json"]:
        mpath = MANIFESTS_DIR / mf
        if mpath.exists():
            try:
                with open(mpath, "r", encoding="utf-8") as f:
                    manifests[mf.replace(".json", "")] = json.load(f)
            except Exception:
                pass
    with open(OUT_DATA_DIR / "manifests_summary.json", "w", encoding="utf-8") as f:
        json.dump(manifests, f, indent=2)

    # 3. Source inventory & archive stats
    inv_path = HANDOFF_DIR / "source_inventory.json"
    if inv_path.exists():
        with open(inv_path, "r", encoding="utf-8") as f:
            inv = json.load(f)
            cat_counts = {}
            cat_bytes = {}
            for item in inv:
                c = item.get("category", "other")
                b = item.get("bytes", 0)
                cat_counts[c] = cat_counts.get(c, 0) + 1
                cat_bytes[c] = cat_bytes.get(c, 0) + b
            
            inv_stats = {
                "total_files": len(inv),
                "total_bytes": sum(cat_bytes.values()),
                "total_mb": round(sum(cat_bytes.values()) / (1024**2), 2),
                "by_category": [
                    {"category": k, "count": cat_counts[k], "mb": round(cat_bytes[k] / (1024**2), 2)}
                    for k in sorted(cat_counts.keys())
                ]
            }
            with open(OUT_DATA_DIR / "archive_stats.json", "w", encoding="utf-8") as f:
                json.dump(inv_stats, f, indent=2)

    # 4. Docs Index
    doc_files = [
        ("RESEARCH_PAPER.md", "Final Research Paper (<=16 GB)", "Full formal manuscript covering hypothesis, setup, results and proof"),
        ("METHODOLOGY.md", "Master Methodology Specification", "Tiers, models, Q4_K_M, fine-tune, judgement, and storage policy"),
        ("APPLICATION.md", "Application & Beneficiary Framing", "Why regulated banks & funds require local LLMs under strict RAM caps"),
        ("DEVELOPMENT_START.md", "Locked Spec for Coding", "Model families, quant recipes, prompt templates, and problem sets"),
        ("DECISIONS.md", "Project Decision Log", "Chronological record of every methodology and experimental decision"),
        ("FINANCE_DOMAIN_CONTEXT.md", "Domain Glossary & Context", "KYC / CDD / EDD workflows, credit memo drafting, mortgage origination"),
        ("EXPERIMENT_PROTOCOL.md", "RAM & Token Parity Study Spec", "RUPP protocol, cgroup monitoring, thinking-token caps"),
        ("TIER_16_RESEARCH_REPORT.md", "16 GB Empirical Research Report", "Primary 16 GB evaluation, audit results, and failure analysis"),
        ("TIER_LE_16_RESEARCH_REPORT.md", "Combined <=16 GB Research Report", "Integrated pre-paper dossier combining 8 GB and 16 GB results")
    ]
    docs = []
    for fname, title, desc in doc_files:
        p = ROOT_DIR / fname
        if p.exists():
            docs.append({
                "filename": fname,
                "title": title,
                "description": desc,
                "size_kb": round(p.stat().st_size / 1024, 1)
            })
    with open(OUT_DATA_DIR / "docs_index.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)
    log("Saved configs, manifests, inventory stats, and docs index.")

def compute_derived_aggregates():
    log("Computing comprehensive derived analytics for dashboard...")
    
    # 1. Load 16 GB case outcomes
    cases_16gb_file = OUT_DATA_DIR / "tier16_v2" / "case_outcomes.json"
    cases_8gb_file = OUT_DATA_DIR / "le16_v2" / "tier8_case_outcomes.json"
    
    cases_16 = []
    if cases_16gb_file.exists():
        with open(cases_16gb_file, "r", encoding="utf-8") as f:
            cases_16 = json.load(f)
            
    cases_8 = []
    if cases_8gb_file.exists():
        with open(cases_8gb_file, "r", encoding="utf-8") as f:
            cases_8 = json.load(f)
            
    # Key Metrics by Job/Profile
    jobs_16 = {}
    for c in cases_16:
        j = c.get("job")
        if j not in jobs_16:
            jobs_16[j] = {
                "job": j,
                "arm": c.get("arm"),
                "profile": c.get("profile"),
                "total": 0,
                "delivered": 0,
                "reported_correct": 0,
                "raw_correct": 0,
                "withheld": 0,
                "wrong": 0,
                "execution_valid": 0,
                "tokens_generated": 0,
                "tokens_prompt": 0,
                "inference_seconds": 0.0,
                "repairs_attempted": 0,
                "repairs_successful": 0
            }
        d = jobs_16[j]
        d["total"] += 1
        if c.get("delivered"):
            d["delivered"] += 1
        if c.get("reported_correct"):
            d["reported_correct"] += 1
        if c.get("raw_correct"):
            d["raw_correct"] += 1
        if c.get("reported_outcome") == "withheld":
            d["withheld"] += 1
        elif not c.get("reported_correct"):
            d["wrong"] += 1
        if c.get("execution_valid"):
            d["execution_valid"] += 1
        d["tokens_generated"] += c.get("generated_tokens", 0)
        d["tokens_prompt"] += c.get("prompt_tokens", 0)
        d["inference_seconds"] += c.get("inference_seconds", 0.0)
        if c.get("repair_attempted"):
            d["repairs_attempted"] += 1
            if c.get("reported_correct") and not c.get("initial_reported_correct"):
                d["repairs_successful"] += 1

    for j, d in jobs_16.items():
        n = max(d["total"], 1)
        d["reported_acc"] = round(d["reported_correct"] / n * 100, 2)
        d["raw_acc"] = round(d["raw_correct"] / n * 100, 2)
        d["delivery_rate"] = round(d["delivered"] / n * 100, 2)
        d["withheld_rate"] = round(d["withheld"] / n * 100, 2)
        d["avg_tokens_per_case"] = round(d["tokens_generated"] / n, 1)
        d["avg_seconds_per_case"] = round(d["inference_seconds"] / n, 2)
        corr = max(d["reported_correct"], 1)
        d["tokens_per_correct"] = round(d["tokens_generated"] / corr, 1) if d["reported_correct"] > 0 else None
        d["seconds_per_correct"] = round(d["inference_seconds"] / corr, 2) if d["reported_correct"] > 0 else None

    # Company Breakdown
    company_stats = {}
    for c in cases_16:
        comp = c.get("company", "UNKNOWN")
        arm = c.get("arm", "unknown")
        if comp not in company_stats:
            company_stats[comp] = {
                "company": comp,
                "mas_total": 0, "mas_correct": 0, "mas_withheld": 0, "mas_wrong": 0,
                "sas_total": 0, "sas_correct": 0, "sas_withheld": 0, "sas_wrong": 0
            }
        cs = company_stats[comp]
        if arm == "mas":
            cs["mas_total"] += 1
            if c.get("reported_correct"):
                cs["mas_correct"] += 1
            elif c.get("reported_outcome") == "withheld":
                cs["mas_withheld"] += 1
            else:
                cs["mas_wrong"] += 1
        elif arm == "sas":
            cs["sas_total"] += 1
            if c.get("reported_correct"):
                cs["sas_correct"] += 1
            elif c.get("reported_outcome") == "withheld":
                cs["sas_withheld"] += 1
            else:
                cs["sas_wrong"] += 1

    company_list = []
    for comp, cs in company_stats.items():
        m_tot = max(cs["mas_total"], 1)
        s_tot = max(cs["sas_total"], 1)
        company_list.append({
            "company": comp,
            "mas_total": cs["mas_total"],
            "mas_correct_pct": round(cs["mas_correct"] / m_tot * 100, 1),
            "mas_withheld_pct": round(cs["mas_withheld"] / m_tot * 100, 1),
            "mas_wrong_pct": round(cs["mas_wrong"] / m_tot * 100, 1),
            "sas_total": cs["sas_total"],
            "sas_correct_pct": round(cs["sas_correct"] / s_tot * 100, 1),
            "sas_withheld_pct": round(cs["sas_withheld"] / s_tot * 100, 1),
            "sas_wrong_pct": round(cs["sas_wrong"] / s_tot * 100, 1)
        })
    company_list.sort(key=lambda x: x["sas_total"], reverse=True)

    # Overall KPIs
    kpis = {
        "total_cases_16gb": len(cases_16),
        "total_cases_8gb": len(cases_8),
        "total_cases_combined": len(cases_16) + len(cases_8),
        "unique_questions_16gb": 160,
        "unique_questions_8gb": 101,
        "total_eval_jobs": len(jobs_16),
        "primary_mas_accuracy": jobs_16.get("tier16-mas-primary", {}).get("reported_acc", 0.0),
        "primary_sas_accuracy": jobs_16.get("tier16-sas-primary", {}).get("reported_acc", 0.0),
        "accuracy_delta": round(
            jobs_16.get("tier16-mas-primary", {}).get("reported_acc", 0.0) - 
            jobs_16.get("tier16-sas-primary", {}).get("reported_acc", 0.0), 2
        ),
        "primary_mas_withheld": jobs_16.get("tier16-mas-primary", {}).get("withheld_rate", 0.0),
        "primary_sas_withheld": jobs_16.get("tier16-sas-primary", {}).get("withheld_rate", 0.0),
        "p_value_primary": 1.53e-5,
        "total_evidence_files": 2598,
        "unique_evidence_files": 1629,
        "swap_breach_detected": True,
        "swap_failure_details": "Historical swap failure in tier16-sas-primary attempt-0001 (44 MB swap peak) triggered invalidation; attempt-0002 completed under strict no-swap isolation."
    }

    aggregates = {
        "kpis": kpis,
        "jobs_16gb": jobs_16,
        "company_breakdown": company_list
    }
    
    with open(OUT_DATA_DIR / "derived_aggregates.json", "w", encoding="utf-8") as f:
        json.dump(aggregates, f, indent=2)
    log("Computed and saved derived aggregates.")

def main():
    log("Starting Project Agere dashboard data preparation...")
    ensure_dirs()
    copy_handoff_tables()
    copy_figures()
    extract_hardware_benchmarks()
    extract_model_architectures()
    extract_memory_timelines()
    extract_case_details()
    extract_configs_and_manifests()
    compute_derived_aggregates()
    log("All dashboard data pre-processing finished successfully!")

if __name__ == "__main__":
    main()

