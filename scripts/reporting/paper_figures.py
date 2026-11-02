"""Supplementary figures and post-hoc analyses for the <=16 GB research paper.

Reads committed derived tables (research/tier16_v2/data, research/le16_v2/data) and,
for gold-program strata and memory traces, the immutable SSD run. No inference calls.

Usage:
    AGERE_SSD_ROOT=H:\\AGERE python scripts/reporting/paper_figures.py
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SSD = Path(os.environ.get("AGERE_SSD_ROOT", r"H:\AGERE"))
RUN = SSD / "runs" / "lab_tiers_v1" / "lab-16-115gb-recovery-02"
GOLD = SSD / "datasets" / "lab_tiers" / "finance_reports_v1" / "scoring-source.json"
T16 = ROOT / "research" / "tier16_v2" / "data"
LE16 = ROOT / "research" / "le16_v2" / "data"
FIG = ROOT / "figures" / "paper"
OUT = ROOT / "research" / "paper" / "data"

NAVY, TEAL, AMBER, GREY, RED = "#16324f", "#007b7f", "#d4932a", "#8a96a3", "#b5473a"
STATES = ["C", "W", "H"]
STATE_NAME = {"C": "Correct delivered", "W": "Wrong delivered", "H": "Withheld"}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.edgecolor": NAVY,
        "axes.labelcolor": NAVY,
        "xtick.color": NAVY,
        "ytick.color": NAVY,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#d5dbe1",
        "grid.linewidth": 0.7,
        "axes.axisbelow": True,
    }
)


def title(ax_or_fig, main: str, sub: str | None = None) -> None:
    fig = ax_or_fig if isinstance(ax_or_fig, plt.Figure) else ax_or_fig.figure
    fig.text(0.015, 0.975, main, fontsize=14, fontweight="bold", color=NAVY, va="top")
    if sub:
        fig.text(0.015, 0.915, sub, fontsize=9.5, color=NAVY, va="top")


def save(fig: plt.Figure, name: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=200)
    fig.savefig(FIG / f"{name}.svg")
    plt.close(fig)


def load_cases() -> list[dict]:
    with open(T16 / "case_outcomes.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def state(row: dict, metric: str) -> str:
    col = "reported_outcome" if metric == "reported" else "raw_outcome"
    return {"correct": "C", "wrong": "W", "withheld": "H"}[row[col]]


def by_job(cases: list[dict]) -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in cases:
        out[r["job"]][r["case_id"]] = r
    return out


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


# ---------------------------------------------------------------- analyses


def wilson_table(jobs) -> list[dict]:
    rows = []
    for job, cases in sorted(jobs.items()):
        n = len(cases)
        for metric in ("reported", "raw"):
            counts = Counter(state(r, metric) for r in cases.values())
            for s in STATES:
                lo, hi = wilson(counts[s], n)
                rows.append(
                    {"job": job, "metric": metric, "state": s, "count": counts[s], "n": n,
                     "rate": counts[s] / n, "wilson95_low": lo, "wilson95_high": hi}
                )
            delivered = counts["C"] + counts["W"]
            lo, hi = wilson(counts["C"], delivered) if delivered else (math.nan, math.nan)
            rows.append(
                {"job": job, "metric": metric, "state": "precision", "count": counts["C"], "n": delivered,
                 "rate": counts["C"] / delivered if delivered else math.nan, "wilson95_low": lo, "wilson95_high": hi}
            )
    return rows


def transitions(jobs, left: str, right: str, metric: str) -> np.ndarray:
    m = np.zeros((3, 3), dtype=int)
    for cid, r in jobs[left].items():
        m[STATES.index(state(r, metric)), STATES.index(state(jobs[right][cid], metric))] += 1
    return m


def report_bootstrap(jobs, left: str, right: str, metric: str, event: str, draws: int = 10000, seed: int = 42):
    by_report: dict[str, list[float]] = defaultdict(list)
    for cid, r in jobs[left].items():
        a = state(r, metric) == event
        b = state(jobs[right][cid], metric) == event
        by_report[r["report"]].append(float(b) - float(a))
    sums = np.array([sum(v) for v in by_report.values()])
    sizes = np.array([len(v) for v in by_report.values()])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(sums), size=(draws, len(sums)))
    boot = sums[idx].sum(axis=1) / sizes[idx].sum(axis=1)
    point = sums.sum() / sizes.sum()
    return point, boot, np.quantile(boot, [0.025, 0.975])


def program_strata(jobs) -> tuple[dict, dict]:
    gold = {item["id"]: item["qa"] for item in json.loads(GOLD.read_text(encoding="utf-8"))}
    info = {}
    for cid, qa in gold.items():
        prog = qa.get("program", "")
        ops = re.findall(r"([a-z_]+)\(", prog)
        n_steps = len(ops)
        if any(o.startswith("table_") for o in ops):
            family = "table aggregate"
        elif n_steps == 1 and ops[0] in ("add", "subtract"):
            family = "single add/subtract"
        elif n_steps == 1 and ops[0] in ("divide", "multiply", "exp", "greater"):
            family = "single ratio/product"
        else:
            family = "multi-step arithmetic"
        info[cid] = {"steps": n_steps, "family": family, "program": prog}
    strata: dict = {}
    for job in ("tier16-sas-primary", "tier16-mas-primary"):
        for key in ("steps_bucket", "family"):
            for cid, r in jobs[job].items():
                g = info[cid]
                label = (("1 step" if g["steps"] == 1 else "2 steps" if g["steps"] == 2 else "3+ steps")
                         if key == "steps_bucket" else g["family"])
                cell = strata.setdefault(key, {}).setdefault(label, {}).setdefault(job, Counter())
                cell[state(r, "reported")] += 1
    return info, strata


# ----------------------------------------------------------------- figures


def fig_transitions(jobs) -> dict:
    out = {}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, metric in zip(axes, ("reported", "raw")):
        m = transitions(jobs, "tier16-sas-primary", "tier16-mas-primary", metric)
        out[metric] = m.tolist()
        ax.imshow(m, cmap="Blues", vmin=0, vmax=m.max() * 1.15)
        ax.grid(False)
        for i in range(3):
            for j in range(3):
                ax.text(j, i, str(m[i, j]), ha="center", va="center", fontsize=13,
                        color="white" if m[i, j] > m.max() * 0.55 else NAVY, fontweight="bold")
        ax.set_xticks(range(3), [STATE_NAME[s] for s in STATES], fontsize=8.5)
        ax.set_yticks(range(3), [STATE_NAME[s] for s in STATES], fontsize=8.5)
        ax.set_xlabel("MAS (resident F16 team)")
        ax.set_ylabel("SAS (14B Q4 monolith)")
        ax.set_title(f"{metric.capitalize()} metric", color=NAVY, fontsize=11)
    title(fig, "Paired per-question delivery transitions (primary profile)",
          "Each cell counts the same question under both recipes; N = 160. Diagonal = same state.")
    fig.subplots_adjust(top=0.80, bottom=0.14, wspace=0.55, left=0.12, right=0.97)
    save(fig, "P01_paired_transitions")
    return out


def fig_bootstrap(jobs) -> dict:
    res = {}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, (event, col) in zip(axes, (("C", TEAL), ("W", AMBER))):
        point, boot, ci = report_bootstrap(jobs, "tier16-sas-primary", "tier16-mas-primary", "reported", event)
        res[event] = {"point": point, "ci95": ci.tolist(), "sd": float(boot.std())}
        ax.hist(boot * 100, bins=60, color=col, alpha=0.85)
        for v in ci:
            ax.axvline(v * 100, color=NAVY, ls="--", lw=1)
        ax.axvline(point * 100, color=NAVY, lw=2)
        ax.axvline(0, color=RED, lw=1)
        ax.set_xlabel("MAS - SAS (percentage points)")
        ax.set_ylabel("Bootstrap draws")
        ax.set_title(f"{STATE_NAME[event]}: {point*100:+.2f} pp  [95% {ci[0]*100:+.2f}, {ci[1]*100:+.2f}]",
                     color=NAVY, fontsize=10)
    title(fig, "Report-cluster bootstrap distributions of primary contrasts",
          "10,000 resamples of 50 whole reports, question-weighted, NumPy default_rng(42). Red line = zero.")
    fig.subplots_adjust(top=0.78, bottom=0.14, wspace=0.3, left=0.07, right=0.98)
    save(fig, "P02_bootstrap_distributions")
    return res


def fig_report_scatter(jobs) -> dict:
    agg: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for cid, r in jobs["tier16-sas-primary"].items():
        a = agg[r["report"]]
        a[0] += 1
        a[1] += state(r, "reported") == "C"
        a[2] += state(jobs["tier16-mas-primary"][cid], "reported") == "C"
    n = np.array([v[0] for v in agg.values()])
    s = np.array([v[1] for v in agg.values()]) / n
    m = np.array([v[2] for v in agg.values()]) / n
    fig, ax = plt.subplots(figsize=(7.2, 6))
    rng = np.random.default_rng(7)
    jit = rng.uniform(-0.012, 0.012, size=(2, len(n)))
    ax.scatter(s + jit[0], m + jit[1], s=n * 45, color=TEAL, alpha=0.55, edgecolor=NAVY, lw=0.6)
    ax.plot([0, 1], [0, 1], color=GREY, ls="--", lw=1)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel("SAS correct-delivered rate within report")
    ax.set_ylabel("MAS correct-delivered rate within report")
    sas_better = int((s > m).sum())
    mas_better = int((m > s).sum())
    ties = int((s == m).sum())
    ax.text(0.62, 0.1, f"SAS higher: {sas_better} reports\nMAS higher: {mas_better}\nTied: {ties}",
            color=NAVY, fontsize=10, transform=ax.transAxes)
    title(fig, "Report-level correct delivery (reported metric)",
          "50 company-year reports; bubble area = questions per report; small jitter added. Dashed = parity.")
    fig.subplots_adjust(top=0.86, bottom=0.1, left=0.12, right=0.97)
    save(fig, "P03_report_scatter")
    return {"sas_higher": sas_better, "mas_higher": mas_better, "tied": ties,
            "questions_per_report": {"min": int(n.min()), "median": float(np.median(n)), "max": int(n.max())}}


def fig_strata(strata) -> dict:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [3, 4]})
    out = {}
    for ax, key, order in (
        (axes[0], "steps_bucket", ["1 step", "2 steps", "3+ steps"]),
        (axes[1], "family", ["single add/subtract", "single ratio/product", "multi-step arithmetic", "table aggregate"]),
    ):
        labels = [o for o in order if o in strata[key]]
        x = np.arange(len(labels))
        for k, (job, col, name) in enumerate(
            (("tier16-sas-primary", TEAL, "SAS"), ("tier16-mas-primary", AMBER, "MAS"))
        ):
            rates, ns = [], []
            for lab in labels:
                c = strata[key][lab][job]
                tot = sum(c.values())
                rates.append(c["C"] / tot)
                ns.append(tot)
                out.setdefault(key, {}).setdefault(lab, {})[name] = {"C": c["C"], "W": c["W"], "H": c["H"], "n": tot}
            bars = ax.bar(x + (k - 0.5) * 0.38, np.array(rates) * 100, width=0.38, color=col, label=name)
            for b, r in zip(bars, rates):
                ax.text(b.get_x() + b.get_width() / 2, r * 100 + 1.5, f"{r*100:.0f}%", ha="center", fontsize=8.5, color=NAVY)
        ax.set_xticks(x, [f"{lab}\n(n={sum(strata[key][lab]['tier16-sas-primary'].values())})" for lab in labels], fontsize=8.5)
        ax.set_ylim(0, 100)
        ax.set_ylabel("Correct delivered (%)")
    axes[0].legend(frameon=False)
    title(fig, "Correct delivery by gold-program complexity (post hoc, exploratory)",
          "Strata use the reference FinQA program, which deployment never sees. Primary profile, reported metric.")
    fig.subplots_adjust(top=0.8, bottom=0.17, wspace=0.25, left=0.06, right=0.98)
    save(fig, "P04_program_complexity")
    return out


def fig_latency(jobs) -> dict:
    order = [
        ("tier16-sas-direct_control", "SAS direct"), ("tier16-sas-primary", "SAS primary"),
        ("tier16-sas-repair_ablation", "SAS repair"), ("tier16-mas-direct_control", "MAS direct"),
        ("tier16-mas-primary", "MAS primary"), ("tier16-mas-repair_ablation", "MAS repair"),
    ]
    data = [[float(r["inference_seconds"]) for r in jobs[j].values()] for j, _ in order]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    bp = ax.boxplot(data, orientation="vertical", patch_artist=True, widths=0.55, showfliers=True,
                    flierprops={"markersize": 3, "markerfacecolor": GREY, "markeredgecolor": GREY})
    for patch, (j, _) in zip(bp["boxes"], order):
        patch.set_facecolor(TEAL if "sas" in j else AMBER)
        patch.set_alpha(0.75)
    for med in bp["medians"]:
        med.set_color(NAVY)
    ax.set_xticks(range(1, 7), [n for _, n in order])
    ax.set_ylabel("Inference seconds per case (sum of stages)")
    ax.set_yscale("log")
    title(fig, "Per-case CPU inference latency across all six 16 GB jobs",
          "Committed-case stage seconds; excludes model loading and waiting. Log scale.")
    fig.subplots_adjust(top=0.82, bottom=0.1, left=0.08, right=0.98)
    save(fig, "P05_latency_distributions")
    return {n: {"median": float(np.median(d)), "p90": float(np.quantile(d, 0.9)), "max": float(np.max(d))}
            for (_, n), d in zip(order, data)}


def read_memory(path: Path, stride: int = 25) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t, rss, swap = [], [], []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            r = json.loads(line)
            if i % stride and not r["tree_swap_bytes"]:
                continue
            t.append(r["time"])
            rss.append(r["tree_rss_bytes"])
            swap.append(r["tree_swap_bytes"])
    t = np.array(t)
    return (t - t[0]) / 3600, np.array(rss) / 1e9, np.array(swap) / 1e6


def fig_memory() -> dict:
    traces = [
        ("SAS repair-ablation (complete 160-case attempt)", RUN / "tier16-sas-repair_ablation" / "attempt-0001" / "memory.jsonl", TEAL),
        ("MAS primary (complete 160-case attempt)", RUN / "tier16-mas-primary" / "attempt-0001" / "memory.jsonl", AMBER),
        ("SAS primary, failed attempt (swap at case 146)",
         RUN / "continuation-evidence" / "tier16-sas-primary" / "attempt-0001" / "memory.jsonl", RED),
    ]
    fig, axes = plt.subplots(3, 1, figsize=(11, 8.2), sharey=True)
    out = {}
    for ax, (name, path, col) in zip(axes, traces):
        if not path.exists():
            ax.text(0.5, 0.5, f"missing: {path}", transform=ax.transAxes, ha="center")
            continue
        h, rss, swap = read_memory(path)
        ax.plot(h, rss, color=col, lw=0.8)
        ax.axhline(11.5, color=NAVY, ls="--", lw=1)
        ax.text(h[-1], 11.6, "11.5 GB application ceiling", ha="right", va="bottom", fontsize=8, color=NAVY)
        if swap.max() > 0:
            first = np.argmax(swap > 0)
            ax.axvline(h[first], color=RED, lw=1)
            ax.text(h[first], 2, f"first swap sample after case 145 \n({swap.max():.1f} MB max swap) ",
                    color=RED, fontsize=8, ha="right")
        ax.set_ylim(0, 12.5)
        ax.set_ylabel("Tree RSS (GB)")
        ax.set_title(name, color=NAVY, fontsize=10, loc="left")
        out[name] = {"hours": float(h[-1]), "peak_rss_gb_plotted_samples": float(rss.max()),
                     "max_swap_mb": float(swap.max())}
    axes[-1].set_xlabel("Hours since attempt start")
    title(fig, "Sampled process-tree memory during 16 GB evaluation",
          "Controller-plus-worker RSS sampled every 0.2 s (every 25th sample plotted). Swap failure retained, not hidden.")
    fig.subplots_adjust(top=0.85, bottom=0.07, hspace=0.5, left=0.08, right=0.98)
    save(fig, "P06_memory_timelines")
    return out


def fig_stage_costs() -> dict:
    with open(T16 / "stage_metrics.csv", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["job"].endswith("primary")]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    palette = {"select_evidence": "#7fb7be", "analyze_question": TEAL, "program": NAVY, "verify_program": AMBER}
    out = defaultdict(dict)
    for ax, field, lab in ((axes[0], "inference_seconds", "Inference hours"), (axes[1], "generated_tokens", "Generated tokens (thousands)")):
        totals = []
        for k, job in enumerate(("tier16-sas-primary", "tier16-mas-primary")):
            bottom = 0.0
            for r in (x for x in rows if x["job"] == job):
                v = float(r[field]) / (3600 if field == "inference_seconds" else 1000)
                out[job][f"{r['role']}/{r['stage']}/{field}"] = float(r[field])
                ax.bar(k, v, bottom=bottom, color=palette.get(r["stage"], GREY), width=0.55)
                bottom += v
            totals.append(bottom)
            ax.text(k, bottom * 1.02, f"{bottom:.2f}" if field == "inference_seconds" else f"{bottom:.1f}k",
                    ha="center", va="bottom", fontsize=9, color=NAVY)
        ax.set_xticks([0, 1], ["SAS primary\n(one 14B Q4 model)", "MAS primary\n(1.5B / 3B / 0.5B F16)"])
        ax.set_ylabel(lab)
        ax.set_ylim(0, max(totals) * 1.15)
    from matplotlib.patches import Patch
    names = {"select_evidence": "Evidence selection (MAS extractor)", "analyze_question": "128-token analysis",
             "program": "Program generation", "verify_program": "Binary review"}
    fig.legend([Patch(color=c) for c in palette.values()], [names[k] for k in palette], frameon=False,
               ncol=4, loc="lower center", fontsize=8.5)
    title(fig, "Where primary-profile compute is spent, by stage",
          "Committed-case stage totals over 160 questions. MAS stages run on different role models.")
    fig.subplots_adjust(top=0.8, bottom=0.2, wspace=0.3, left=0.07, right=0.98)
    save(fig, "P07_stage_costs")
    return out


def fig_tier8_inventory() -> list[dict]:
    with open(LE16 / "tier8_condition_inventory.csv", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["metric"] == "case_success"]
    rows.sort(key=lambda r: (r["job"].split("-")[0], "sas" in r["job"], r["job"]))
    labels = [r["job"].replace("-full-01", "").replace("diagnostic_audit-", "Reserved: ")
              .replace("model_selection-", "Selection: ").replace("_", " ") for r in rows]
    c = np.array([int(r["correct"]) for r in rows])
    w = np.array([int(r["wrong"]) for r in rows])
    h = np.array([int(r["withheld"]) for r in rows])
    n = c + w + h
    fig, ax = plt.subplots(figsize=(11, 6.2))
    y = np.arange(len(rows))
    ax.barh(y, c / n * 100, color=TEAL, label="Correct delivered")
    ax.barh(y, w / n * 100, left=c / n * 100, color=RED, alpha=0.8, label="Wrong delivered")
    ax.barh(y, h / n * 100, left=(c + w) / n * 100, color="#c9d2da", label="Withheld")
    for i in range(len(rows)):
        ax.text(101, i, f"{c[i]}/{w[i]}/{h[i]}  (n={n[i]})", va="center", fontsize=8, color=NAVY)
    ax.set_yticks(y, labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 125)
    ax.set_xlabel("Share of questions (%)")
    ax.legend(frameon=False, ncol=3, loc="lower right", bbox_to_anchor=(1.0, 1.0), fontsize=8.5)
    title(fig, "Redeveloped 8 GB FinQA inventory: 15 completed configurations",
          "Reported metric, C/W/H. Selection (52 q / 15 reports) and reserved (49 q / 15 reports) cohorts; 6.4 GB cap.")
    fig.subplots_adjust(top=0.84, bottom=0.08, left=0.3, right=0.98)
    save(fig, "P08_tier8_inventory")
    return [{"job": r["job"], "C": int(r["correct"]), "W": int(r["wrong"]), "H": int(r["withheld"])} for r in rows]


def fig_utility_kappa() -> dict:
    lam = np.linspace(0, 3, 301)
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    out = {}
    for kappa, ls in ((0.0, "-"), (0.1, "--"), (0.25, ":")):
        u_sas = (78 - lam * 48 - kappa * 34) / 160
        u_mas = (5 - lam * 3 - kappa * 152) / 160
        ax.plot(lam, u_sas, color=TEAL, ls=ls, lw=1.8, label=f"SAS, kappa={kappa}")
        ax.plot(lam, u_mas, color=AMBER, ls=ls, lw=1.8, label=f"MAS, kappa={kappa}")
        ax.axhline(-kappa, color=GREY, ls=ls, lw=0.9)
        out[str(kappa)] = {"switch_lambda_reported": (73 + 118 * kappa) / 45}
    ax.axhline(0, color=NAVY, lw=0.6)
    ax.set_xlabel("lambda: cost of one wrong delivery (benefit of one correct = 1)")
    ax.set_ylabel("Utility per question")
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="lower left")
    title(fig, "Utility sensitivity with a cost for human review of withheld cases",
          "U = (C - lambda*W - kappa*H)/N, reported metric, primary profile. Grey = always-withhold (-kappa). Illustrative only.")
    fig.subplots_adjust(top=0.83, bottom=0.12, left=0.09, right=0.98)
    save(fig, "P09_utility_kappa")
    return out


def main() -> None:
    cases = load_cases()
    jobs = by_job(cases)
    assert len(cases) == 960 and all(len(v) == 160 for v in jobs.values())
    info, strata = program_strata(jobs)
    results = {
        "source": "research/tier16_v2/data/case_outcomes.csv + SSD lab-16-115gb-recovery-02 (read-only)",
        "status": "post-hoc supplementary analyses for the paper; no new inference",
        "wilson_case_iid": wilson_table(jobs),
        "paired_transitions_sas_rows_mas_cols": fig_transitions(jobs),
        "bootstrap_replication": fig_bootstrap(jobs),
        "report_level": fig_report_scatter(jobs),
        "program_complexity_strata": fig_strata(strata),
        "gold_program_step_counts": dict(Counter(v["steps"] for v in info.values())),
        "latency": fig_latency(jobs),
        "memory": fig_memory(),
        "stage_costs": fig_stage_costs(),
        "tier8_inventory": fig_tier8_inventory(),
        "utility_kappa": fig_utility_kappa(),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "paper_supplementary_analysis.json").write_text(json.dumps(results, indent=2, default=float), encoding="utf-8")
    print(json.dumps({k: v for k, v in results.items() if k not in ("wilson_case_iid", "stage_costs", "tier8_inventory")},
                     indent=1, default=float))


if __name__ == "__main__":
    main()
