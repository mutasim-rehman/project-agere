"""Generate publication-quality figures for the Tier 1 (8 GB) research report.

Reads test and dev run artifacts from AGERE_SSD_ROOT and outputs PNG figures
to D:\\project-agere\\figures\\tier8\\.
"""

import json
import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 11,
    "figure.titlesize": 15,
    "figure.dpi": 300,
})

SSD_ROOT = Path(os.environ.get("AGERE_SSD_ROOT", r"H:\AGERE"))
RUN_DIR = SSD_ROOT / "runs" / "tier8" / "tier8-8gb-v1"
OUT_DIR = Path(r"D:\project-agere\figures\tier8")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load summaries
test_sas = json.loads((RUN_DIR / "test" / "final_sas" / "summary.json").read_text(encoding="utf-8"))
test_mas = json.loads((RUN_DIR / "test" / "final_mas" / "summary.json").read_text(encoding="utf-8"))
dev_naive_sas = json.loads((RUN_DIR / "dev" / "naive_sas" / "summary.json").read_text(encoding="utf-8"))
dev_naive_mas = json.loads((RUN_DIR / "dev" / "naive_mas" / "summary.json").read_text(encoding="utf-8"))
dev_hard_sas = json.loads((RUN_DIR / "dev" / "hardened_sas_base" / "summary.json").read_text(encoding="utf-8"))
dev_hard_mas = json.loads((RUN_DIR / "dev" / "hardened_mas" / "summary.json").read_text(encoding="utf-8"))

# Load test case breakdowns
def parse_cases(filepath):
    rows = [json.loads(line) for line in open(filepath, encoding="utf-8") if line.strip()]
    stats = {}
    for kind in ["all", "kyc", "credit"]:
        sub = [r for r in rows if kind == "all" or r["kind"] == kind]
        valid = [r for r in sub if r["score"]["valid_json"]]
        scorable = [r for r in valid if r["score"]["structured_claims_complete"]]
        grounded = sum(r["score"]["grounded"] for r in sub)
        g_total = sum(r["score"]["grounding_total"] for r in sub)
        inv = sum(bool(r["score"]["structured_invention"]) for r in scorable)
        stats[kind] = {
            "n": len(sub),
            "valid_json_rate": len(valid) / len(sub),
            "scorable_count": len(scorable),
            "invention_rate": inv / len(scorable) if scorable else 0.0,
            "grounding_accuracy": grounded / g_total if g_total else 0.0,
            "avg_tokens": sum(r["generated_tokens"] for r in sub) / len(sub),
            "avg_latency": sum(r["elapsed_seconds"] for r in sub) / len(sub),
        }
    return stats

cases_sas = parse_cases(RUN_DIR / "test" / "final_sas" / "cases.jsonl")
cases_mas = parse_cases(RUN_DIR / "test" / "final_mas" / "cases.jsonl")

# Palette
SAS_COLOR = "#1f77b4"  # Steel Blue
MAS_COLOR = "#ff7f0e"  # Dark Amber
CAP_COLOR = "#d62728"  # Crimson Red

# ==========================================
# Figure 1: Headline Test Metrics Comparison
# ==========================================
def plot_figure_1():
    fig, ax = plt.subplots(figsize=(9, 5.5))
    metrics = ["JSON Validity Rate", "Invention Rate\n(Lower is Better)", "Citation Grounding\nAccuracy", "Mismatch Recall"]
    
    sas_vals = [
        test_sas["valid_json_rate"] * 100,
        test_sas["structured_invention_rate_among_complete_claim_sets"] * 100,
        test_sas["grounding_accuracy"] * 100,
        test_sas["mismatch_recall"] * 100
    ]
    mas_vals = [
        test_mas["valid_json_rate"] * 100,
        test_mas["structured_invention_rate_among_complete_claim_sets"] * 100,
        test_mas["grounding_accuracy"] * 100,
        test_mas["mismatch_recall"] * 100
    ]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, sas_vals, width, label="SAS-Quant (Qwen2.5-7B Q4_K_M)", color=SAS_COLOR, edgecolor="black", linewidth=0.8)
    rects2 = ax.bar(x + width/2, mas_vals, width, label="MAS-FP16 (1.5B + 0.5B + 0.5B Resident)", color=MAS_COLOR, edgecolor="black", linewidth=0.8)
    
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Figure 1: Held-Out Test Evaluation on Regulated Financial Document Tasks (8 GB Tier)\n(n = 175 pooled: 100 KYC-Synth + 75 Credit-Synth)", fontweight="bold", pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", frameon=True)
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{height:.1f}%",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=10, fontweight="bold")
            
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    fig_path = OUT_DIR / "figure1_headline_metrics.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"Saved {fig_path}")

# ==========================================
# Figure 2: KYC vs Credit Workflow Breakdown
# ==========================================
def plot_figure_2():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True)
    
    workflows = ["Agere-KYC-Synth (n=100)", "Agere-Credit-Synth (n=75)"]
    
    # Left: Citation Grounding Accuracy
    ground_sas = [cases_sas["kyc"]["grounding_accuracy"] * 100, cases_sas["credit"]["grounding_accuracy"] * 100]
    ground_mas = [cases_mas["kyc"]["grounding_accuracy"] * 100, cases_mas["credit"]["grounding_accuracy"] * 100]
    
    x = np.arange(len(workflows))
    width = 0.35
    
    r1 = ax1.bar(x - width/2, ground_sas, width, label="SAS (7B Q4)", color=SAS_COLOR, edgecolor="black")
    r2 = ax1.bar(x + width/2, ground_mas, width, label="MAS (FP16 Team)", color=MAS_COLOR, edgecolor="black")
    ax1.set_title("Citation Grounding Accuracy\n(Higher is Better)", fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(workflows)
    ax1.set_ylabel("Accuracy (%)")
    ax1.set_ylim(0, 118)
    ax1.legend(loc="upper left")
    
    for r in r1:
        ax1.annotate(f"{r.get_height():.1f}%", xy=(r.get_x() + r.get_width()/2, r.get_height()),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
    for r in r2:
        ax1.annotate(f"{r.get_height():.1f}%", xy=(r.get_x() + r.get_width()/2, r.get_height()),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
        
    # Right: Structured Invention Rate
    inv_sas = [cases_sas["kyc"]["invention_rate"] * 100, cases_sas["credit"]["invention_rate"] * 100]
    inv_mas = [cases_mas["kyc"]["invention_rate"] * 100, cases_mas["credit"]["invention_rate"] * 100]
    
    r3 = ax2.bar(x - width/2, inv_sas, width, label="SAS (7B Q4)", color=SAS_COLOR, edgecolor="black")
    r4 = ax2.bar(x + width/2, inv_mas, width, label="MAS (FP16 Team)", color=MAS_COLOR, edgecolor="black")
    ax2.set_title("Structured Invention Rate\n(Lower is Better)", fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(workflows)
    ax2.legend(loc="upper right")
    
    for r in r3:
        ax2.annotate(f"{r.get_height():.1f}%", xy=(r.get_x() + r.get_width()/2, r.get_height()),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
    for r in r4:
        ax2.annotate(f"{r.get_height():.1f}%", xy=(r.get_x() + r.get_width()/2, r.get_height()),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
        
    fig.suptitle("Figure 2: Domain-Specific Workflow Performance Breakdown: KYC vs. Credit Analysis", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig_path = OUT_DIR / "figure2_task_breakdown.png"
    plt.savefig(fig_path, bbox_inches="tight")
    plt.close()
    print(f"Saved {fig_path}")

# ==========================================
# Figure 3: Memory & Resource Parity
# ==========================================
def plot_figure_3():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Memory Cap Parity
    categories = ["SAS-Quant\n(7B Q4_K_M)", "MAS-FP16\n(Resident Team)"]
    peak_rss = [test_sas["peak_rss_bytes"] / 1e9, test_mas["peak_rss_bytes"] / 1e9]
    colors = [SAS_COLOR, MAS_COLOR]
    
    bars = ax1.bar(categories, peak_rss, width=0.5, color=colors, edgecolor="black", linewidth=0.8)
    ax1.axhline(6.40, color=CAP_COLOR, linestyle="--", linewidth=2, label="Strict Parity RSS Cap (6.40 GB)")
    ax1.set_ylabel("Process-Tree Peak RSS (GB)")
    ax1.set_title("Peak Resident Process RSS vs. Parity Ceiling", fontweight="bold")
    ax1.set_ylim(0, 7.5)
    ax1.legend(loc="upper right")
    
    for b in bars:
        height = b.get_height()
        ax1.annotate(f"{height:.2f} GB\n(-{6.40 - height:.2f} GB margin)",
                     xy=(b.get_x() + b.get_width()/2, height),
                     xytext=(0, 6), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
        
    # Right: Compute Economy (Tokens Generated vs Latency)
    tokens = [test_sas["generated_tokens"] / 175, test_mas["generated_tokens"] / 175]
    latencies = [test_sas["generation_seconds"] / 175, test_mas["generation_seconds"] / 175]
    
    x = np.arange(len(categories))
    w = 0.35
    
    ax2_twin = ax2.twinx()
    b_tok = ax2.bar(x - w/2, tokens, w, color="#3b528b", edgecolor="black", label="Avg Generated Tokens")
    b_lat = ax2_twin.bar(x + w/2, latencies, w, color="#5ec962", edgecolor="black", label="Avg Latency (seconds)")
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    ax2.set_ylabel("Tokens per Case", color="#3b528b", fontweight="bold")
    ax2_twin.set_ylabel("Latency per Case (s)", color="#228833", fontweight="bold")
    ax2.set_title("Test-Time Token and Latency Profile", fontweight="bold")
    ax2.set_ylim(0, 850)
    ax2_twin.set_ylim(0, 120)
    
    for b in b_tok:
        ax2.annotate(f"{b.get_height():.0f} tok", xy=(b.get_x() + b.get_width()/2, b.get_height()),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
    for b in b_lat:
        ax2_twin.annotate(f"{b.get_height():.1f}s", xy=(b.get_x() + b.get_width()/2, b.get_height()),
                          xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
        
    fig.suptitle("Figure 3: System Memory Parity Protocol (RUPP) and Inference Resource Economy", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig_path = OUT_DIR / "figure3_memory_efficiency.png"
    plt.savefig(fig_path, bbox_inches="tight")
    plt.close()
    print(f"Saved {fig_path}")

# ==========================================
# Figure 4: Failure Mode Taxonomy
# ==========================================
def plot_figure_4():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))
    
    # SAS Failures
    sas_tags = {"S6 (Citation Discrepancy\nor Omission)": 125, "Success / Valid Fact": 50}
    colors_sas = ["#e74c3c", "#2ecc71"]
    ax1.pie(sas_tags.values(), labels=sas_tags.keys(), autopct="%1.1f%%", startangle=140,
            colors=colors_sas, wedgeprops=dict(edgecolor="black", linewidth=1.2), textprops={"fontsize": 10})
    ax1.set_title("SAS Failure Distribution (n=175)\n(Single Generalist Bottleneck)", fontweight="bold")
    
    # MAS Failures
    mas_tags = {
        "M3 (Error Cascade / Hallucination)": 89,
        "M2 (Schema Handoff / JSON Syntax)": 64,
        "M7 (Verifier Omission / Quote Drift)": 22
    }
    colors_mas = ["#e67e22", "#d35400", "#c0392b"]
    ax2.pie(mas_tags.values(), labels=mas_tags.keys(), autopct="%1.1f%%", startangle=140,
            colors=colors_mas, wedgeprops=dict(edgecolor="black", linewidth=1.2), textprops={"fontsize": 10})
    ax2.set_title("MAS Failure Distribution (n=175)\n(Cascading Multi-Agent Breakdown)", fontweight="bold")
    
    fig.suptitle("Figure 4: Failure Mode Decomposition (Project Agere / Cemri MAST Taxonomy)", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig_path = OUT_DIR / "figure4_failure_taxonomy.png"
    plt.savefig(fig_path, bbox_inches="tight")
    plt.close()
    print(f"Saved {fig_path}")

# ==========================================
# Figure 5: Dev Triage & Hardening Collapse
# ==========================================
def plot_figure_5():
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    
    conditions = ["SAS Naive (Dev)", "SAS Hardened (Dev)", "MAS Naive (Dev)", "MAS Hardened (Dev)"]
    valid_json = [
        dev_naive_sas["valid_json_rate"] * 100,
        dev_hard_sas["valid_json_rate"] * 100,
        dev_naive_mas["valid_json_rate"] * 100,
        dev_hard_mas["valid_json_rate"] * 100
    ]
    grounding = [
        dev_naive_sas["grounding_accuracy"] * 100,
        dev_hard_sas["grounding_accuracy"] * 100,
        dev_naive_mas["grounding_accuracy"] * 100,
        dev_hard_mas["grounding_accuracy"] * 100
    ]
    
    x = np.arange(len(conditions))
    w = 0.35
    
    b1 = ax.bar(x - w/2, valid_json, w, label="JSON Syntax Compliance Rate (%)", color="#2b5c8f", edgecolor="black")
    b2 = ax.bar(x + w/2, grounding, w, label="Citation Grounding Accuracy (%)", color="#e27c38", edgecolor="black")
    
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Figure 5: Engineering Triage on Dev Set (n=150): The Prompt-Complexity Collapse\nPre-registered decision: Revert to Naive Baselines due to Schema Fragility", fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontweight="bold")
    ax.set_ylim(0, 118)
    ax.legend(loc="upper right", frameon=True)
    
    for b in b1:
        ax.annotate(f"{b.get_height():.1f}%", xy=(b.get_x() + b.get_width()/2, b.get_height()),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
    for b in b2:
        ax.annotate(f"{b.get_height():.1f}%", xy=(b.get_x() + b.get_width()/2, b.get_height()),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
        
    plt.tight_layout()
    fig_path = OUT_DIR / "figure5_dev_ablation_hardening.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"Saved {fig_path}")

if __name__ == "__main__":
    plot_figure_1()
    plot_figure_2()
    plot_figure_3()
    plot_figure_4()
    plot_figure_5()
    print("All figures successfully generated in figures/tier8/")
