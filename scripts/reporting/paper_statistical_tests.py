"""Paired hypothesis tests for the <=16 GB research paper (no inference calls).

Recomputes, from committed case-level tables, every paired test reported in the paper's
"Mathematical and statistical testing standards" section:

* exact McNemar (conditional binomial), asymptotic and Edwards continuity-corrected chi-square;
* paired risk difference with Wald interval;
* cluster-robust (CR1) z test and Durkalski cluster-adjusted McNemar at report and company level;
* report-level exact sign test;
* whole-report cluster bootstrap percentile interval (10,000 draws, NumPy default_rng(42));
* Bowker symmetry and Stuart-Maxwell marginal homogeneity on the 3x3 C/W/H transition table;
* Holm adjustment over the four prespecified 16 GB primary endpoints.

Inputs:  research/tier16_v2/data/case_outcomes.csv, research/le16_v2/data/tier8_case_outcomes.csv,
         research/tier16_v2/data/statistical_analysis.json (published bootstrap/sign-flip results).
Outputs: research/paper/data/paper_statistical_tests.{json,csv}

Usage:
    python scripts/reporting/paper_statistical_tests.py
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
T16 = ROOT / "research" / "tier16_v2" / "data"
LE16 = ROOT / "research" / "le16_v2" / "data"
OUT = ROOT / "research" / "paper" / "data"

STATES = ["C", "W", "H"]
Z975 = 1.959963984540054
DRAWS, SEED = 10_000, 42


# ------------------------------------------------------------------ distributions


def chi2_sf(x: float, df: int) -> float:
    """Upper tail of the chi-square distribution for integer df (closed form)."""
    if df <= 0 or math.isnan(x):
        return math.nan
    if x <= 0:
        return 1.0
    h = x / 2.0
    if df % 2 == 0:
        term, total = 1.0, 1.0
        for i in range(1, df // 2):
            term *= h / i
            total += term
        return math.exp(-h) * total
    total = math.erfc(math.sqrt(h))
    term = math.sqrt(h) / math.gamma(1.5)
    for i in range(1, (df + 1) // 2):
        total += math.exp(-h) * term
        term *= h / (i + 0.5)
    return min(1.0, total)


def norm_sf2(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def binom_two_sided_half(k_small: int, n: int) -> float:
    """Exact two-sided p for Binomial(n, 1/2), doubling the smaller tail."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(0, k_small + 1)) / 2.0**n
    return min(1.0, 2.0 * tail)


def holm(pvals: list[float]) -> list[float]:
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj, running = [0.0] * len(pvals), 0.0
    for rank, i in enumerate(order):
        running = max(running, (len(pvals) - rank) * pvals[i])
        adj[i] = min(1.0, running)
    return adj


# ------------------------------------------------------------------ tests


def mcnemar_block(b: int, c: int, n: int) -> dict:
    nd = b + c
    delta = (b - c) / n
    var = ((b + c) - (b - c) ** 2 / n) / n**2
    se = math.sqrt(max(var, 0.0))
    chi = (b - c) ** 2 / nd if nd else math.nan
    chicc = (max(abs(b - c) - 1, 0)) ** 2 / nd if nd else math.nan
    return {
        "b_right_only": b, "c_left_only": c, "discordant": nd, "delta": delta, "se_wald": se,
        "wald95": [delta - Z975 * se, delta + Z975 * se],
        "exact_mcnemar_p": binom_two_sided_half(min(b, c), nd),
        "chi2": chi, "chi2_p": chi2_sf(chi, 1) if nd else 1.0,
        "chi2_cc": chicc, "chi2_cc_p": chi2_sf(chicc, 1) if nd else 1.0,
        "exact_preferred": nd < 25,
    }


def cluster_block(d: np.ndarray, groups: list[str]) -> dict:
    """CR1 cluster-robust z test and Durkalski adjusted McNemar for paired differences d_i in {-1,0,1}."""
    n = len(d)
    sums: dict[str, float] = defaultdict(float)
    sizes: dict[str, int] = defaultdict(int)
    for v, g in zip(d, groups):
        sums[g] += v
        sizes[g] += 1
    s = np.array(list(sums.values()))
    m = np.array(list(sizes.values()))
    G = len(s)
    delta = d.mean()
    resid = s - delta * m
    var_cr = G / (G - 1) * float((resid**2).sum()) / n**2
    se_cr = math.sqrt(var_cr)
    var_iid = float(((d - delta) ** 2).sum()) / n**2
    z = delta / se_cr if se_cr > 0 else math.nan
    denom = float((s**2).sum())
    durk = float(s.sum()) ** 2 / denom if denom > 0 else math.nan
    return {
        "clusters": G, "se_cr1": se_cr, "z_cr1": z, "p_cr1": norm_sf2(z) if se_cr > 0 else 1.0,
        "design_effect": var_cr / var_iid if var_iid > 0 else math.nan,
        "durkalski_chi2": durk, "durkalski_p": chi2_sf(durk, 1) if denom > 0 else 1.0,
        "clusters_right_higher": int((s > 0).sum()), "clusters_left_higher": int((s < 0).sum()),
        "clusters_tied": int((s == 0).sum()),
    }


def sign_test(pos: int, neg: int) -> float:
    return binom_two_sided_half(min(pos, neg), pos + neg)


def bootstrap(d: np.ndarray, groups: list[str]) -> list[float]:
    sums: dict[str, float] = defaultdict(float)
    sizes: dict[str, int] = defaultdict(int)
    for v, g in zip(d, groups):
        sums[g] += v
        sizes[g] += 1
    s = np.array(list(sums.values()))
    m = np.array(list(sizes.values()))
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(s), size=(DRAWS, len(s)))
    boot = s[idx].sum(axis=1) / m[idx].sum(axis=1)
    return [float(x) for x in np.quantile(boot, [0.025, 0.975])]


def symmetry_tests(t: np.ndarray) -> dict:
    """Bowker symmetry and Stuart-Maxwell marginal homogeneity for a kxk paired table."""
    k = t.shape[0]
    q, df = 0.0, 0
    for i in range(k):
        for j in range(i + 1, k):
            s = t[i, j] + t[j, i]
            if s > 0:
                q += (t[i, j] - t[j, i]) ** 2 / s
                df += 1
    d = t.sum(axis=1) - t.sum(axis=0)
    V = -(t + t.T).astype(float)
    np.fill_diagonal(V, t.sum(axis=1) + t.sum(axis=0) - 2 * np.diag(t))
    d2, V2 = d[: k - 1].astype(float), V[: k - 1, : k - 1]
    rank = int(np.linalg.matrix_rank(V2))
    qsm = float(d2 @ np.linalg.pinv(V2) @ d2) if rank else math.nan
    return {
        "bowker_q": q, "bowker_df": df, "bowker_p": chi2_sf(q, df) if df else 1.0,
        "stuart_maxwell_q": qsm, "stuart_maxwell_df": rank,
        "stuart_maxwell_p": chi2_sf(qsm, rank) if rank else 1.0,
    }


# ------------------------------------------------------------------ data


def outcome(row: dict, metric: str) -> str:
    return {"correct": "C", "wrong": "W", "withheld": "H"}[row[f"{metric}_outcome"]]


def load(path: Path, key: str) -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = defaultdict(dict)
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r[key]][r["case_id"]] = r
    return out


def compare(jobs, left: str, right: str, metric: str) -> dict:
    ids = list(jobs[left])
    assert set(ids) == set(jobs[right]), (left, right)
    L = [outcome(jobs[left][i], metric) for i in ids]
    R = [outcome(jobs[right][i], metric) for i in ids]
    reports = [jobs[left][i]["report"] for i in ids]
    companies = [jobs[left][i]["company"] for i in ids]
    n = len(ids)
    table = np.zeros((3, 3), dtype=int)
    for a, b in zip(L, R):
        table[STATES.index(a), STATES.index(b)] += 1
    res = {"n": n, "reports": len(set(reports)), "companies": len(set(companies)),
           "transition_left_rows_right_cols": table.tolist(), "symmetry": symmetry_tests(table), "endpoints": {}}
    for ev in ("C", "W", "H"):
        y_l = np.array([s == ev for s in L], dtype=float)
        y_r = np.array([s == ev for s in R], dtype=float)
        d = y_r - y_l
        b, c = int((d > 0).sum()), int((d < 0).sum())
        block = mcnemar_block(b, c, n)
        block["left_events"], block["right_events"] = int(y_l.sum()), int(y_r.sum())
        block["report"] = cluster_block(d, reports)
        block["company"] = cluster_block(d, companies)
        block["report_sign_test_p"] = sign_test(block["report"]["clusters_right_higher"],
                                                block["report"]["clusters_left_higher"])
        block["report_bootstrap95"] = bootstrap(d, reports)
        res["endpoints"][ev] = block
    return res


COMPARISONS_16 = [
    ("primary", "Primary: MAS vs SAS", "tier16-sas-primary", "tier16-mas-primary"),
    ("direct_arch", "Direct control: MAS vs SAS", "tier16-sas-direct_control", "tier16-mas-direct_control"),
    ("repair_arch", "Repair ablation: MAS vs SAS", "tier16-sas-repair_ablation", "tier16-mas-repair_ablation"),
    ("sas_bundle", "SAS: primary vs direct", "tier16-sas-direct_control", "tier16-sas-primary"),
    ("mas_bundle", "MAS: primary vs direct", "tier16-mas-direct_control", "tier16-mas-primary"),
    ("sas_repair", "SAS: repair vs primary", "tier16-sas-primary", "tier16-sas-repair_ablation"),
    ("mas_repair", "MAS: repair vs primary", "tier16-mas-primary", "tier16-mas-repair_ablation"),
]

S, R = "model_selection-", "diagnostic_audit-"
COMPARISONS_8 = [
    ("sel_baseline_arch", "Selection52: baseline MAS vs SAS", S + "baseline_sas-full-01", S + "baseline_mas-full-01"),
    ("sel_control_arch", "Selection52: control MAS vs SAS", S + "control_sas-full-01", S + "control_mas-full-01"),
    ("sel_crossed_arch", "Selection52: crossed MAS vs SAS", S + "crossed_sas-full-01", S + "crossed_mas-full-01"),
    ("res_control_arch", "Reserved49: control MAS vs SAS", R + "control_sas-full-01", R + "control_mas-full-01"),
    ("res_crossed_arch", "Reserved49: crossed MAS vs SAS", R + "crossed_sas-full-01", R + "crossed_mas-full-01"),
    ("sel_mas_crossed_control", "Selection52: crossed vs control MAS", S + "control_mas-full-01", S + "crossed_mas-full-01"),
    ("sel_mas_crossed_original", "Selection52: crossed vs original-critic MAS",
     S + "baseline_original_critic_common_actor-full-01", S + "crossed_mas-full-01"),
    ("res_mas_crossed_control", "Reserved49: crossed vs control MAS", R + "control_mas-full-01", R + "crossed_mas-full-01"),
    ("sel_sas_crossed_control", "Selection52: crossed vs control SAS", S + "control_sas-full-01", S + "crossed_sas-full-01"),
    ("sel_sas_crossed_control_reasoned", "Selection52: crossed vs control SAS (analysis128+demos)",
     S + "control_sas-analysis128-demos2-full-01", S + "crossed_sas-analysis128-demos2-full-01"),
    ("res_sas_crossed_control", "Reserved49: crossed vs control SAS", R + "control_sas-full-01", R + "crossed_sas-full-01"),
    ("sel_sas_bundle_baseline", "Selection52: baseline SAS, analysis128+demos vs direct",
     S + "baseline_sas-full-01", S + "baseline_sas-analysis128-demos2-full-01"),
    ("sel_sas_bundle_control", "Selection52: control SAS, analysis128+demos vs direct",
     S + "control_sas-full-01", S + "control_sas-analysis128-demos2-full-01"),
    ("sel_sas_bundle_crossed", "Selection52: crossed SAS, analysis128+demos vs direct",
     S + "crossed_sas-full-01", S + "crossed_sas-analysis128-demos2-full-01"),
]


def main() -> None:
    jobs16 = load(T16 / "case_outcomes.csv", "job")
    jobs8 = load(LE16 / "tier8_case_outcomes.csv", "condition")
    published = json.loads((T16 / "statistical_analysis.json").read_text(encoding="utf-8"))
    pub_primary = published["comparisons"]["primary"]["endpoints"]

    results: dict = {"tier16": {}, "tier8": {}, "settings": {
        "alpha": 0.05, "bootstrap_draws": DRAWS, "bootstrap_seed": SEED, "bootstrap_unit": "report",
        "direction": "right minus left; b = right-only events, c = left-only events",
        "exact_preferred_when_discordant_below": 25,
    }}
    for key, label, left, right in COMPARISONS_16:
        results["tier16"][key] = {"label": label, "left": left, "right": right,
                                  **{m: compare(jobs16, left, right, m) for m in ("reported", "raw")}}
    for key, label, left, right in COMPARISONS_8:
        results["tier8"][key] = {"label": label, "left": left, "right": right,
                                 **{m: compare(jobs8, left, right, m) for m in ("reported", "raw")}}

    prim = results["tier16"]["primary"]
    fam = [("reported", "C"), ("reported", "W"), ("raw", "C"), ("raw", "W")]
    pub_key = {"reported": "case_success", "raw": "raw_execution_match"}
    ev_name = {"C": "correct", "W": "wrong"}
    durk = [prim[m]["endpoints"][e]["report"]["durkalski_p"] for m, e in fam]
    signflip = [pub_primary[f"{pub_key[m]}/{ev_name[e]}"]["cluster_sign_flip"]["p"] for m, e in fam]
    results["primary_family"] = [
        {"metric": m, "event": e, "durkalski_report_p": dp, "durkalski_report_holm": dh,
         "published_sign_flip_p": sp, "published_sign_flip_holm": sh,
         "published_bootstrap95": pub_primary[f"{pub_key[m]}/{ev_name[e]}"]["bootstrap95"],
         "recomputed_bootstrap95": prim[m]["endpoints"][e]["report_bootstrap95"]}
        for (m, e), dp, dh, sp, sh in zip(fam, durk, holm(durk), signflip, holm(signflip))
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "paper_statistical_tests.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    rows = []
    for tier in ("tier16", "tier8"):
        for key, comp in results[tier].items():
            for metric in ("reported", "raw"):
                c = comp[metric]
                sym = c["symmetry"]
                for ev, e in c["endpoints"].items():
                    rows.append({
                        "tier": tier, "comparison": key, "label": comp["label"], "metric": metric, "event": ev,
                        "n": c["n"], "left_events": e["left_events"], "right_events": e["right_events"],
                        "b": e["b_right_only"], "c": e["c_left_only"], "delta": e["delta"], "se_wald": e["se_wald"],
                        "wald95_low": e["wald95"][0], "wald95_high": e["wald95"][1],
                        "boot95_low": e["report_bootstrap95"][0], "boot95_high": e["report_bootstrap95"][1],
                        "exact_mcnemar_p": e["exact_mcnemar_p"], "chi2": e["chi2"], "chi2_p": e["chi2_p"],
                        "chi2_cc": e["chi2_cc"], "chi2_cc_p": e["chi2_cc_p"],
                        "se_cr1_report": e["report"]["se_cr1"], "p_cr1_report": e["report"]["p_cr1"],
                        "deff_report": e["report"]["design_effect"],
                        "durkalski_report_chi2": e["report"]["durkalski_chi2"],
                        "durkalski_report_p": e["report"]["durkalski_p"],
                        "durkalski_company_p": e["company"]["durkalski_p"],
                        "reports_right_higher": e["report"]["clusters_right_higher"],
                        "reports_left_higher": e["report"]["clusters_left_higher"],
                        "report_sign_test_p": e["report_sign_test_p"],
                        "bowker_q": sym["bowker_q"], "bowker_df": sym["bowker_df"], "bowker_p": sym["bowker_p"],
                        "stuart_maxwell_q": sym["stuart_maxwell_q"], "stuart_maxwell_df": sym["stuart_maxwell_df"],
                        "stuart_maxwell_p": sym["stuart_maxwell_p"],
                    })
    with open(OUT / "paper_statistical_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} endpoint rows")


if __name__ == "__main__":
    main()
