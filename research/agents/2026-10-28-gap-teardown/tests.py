"""T2 (before-open separation, VF vs SC) and T3 (09:35 early warning) as pre-registered. Usage: python tests.py -> out/tests.json
T2: rank-sum AUC, p from 10,000 bootstrap resamples by event (two-sided). Holm over every before-open measure tested
    (10 here: M0, M1 drift, M1 high time, M2a, M2b, M3, M4, M5a-c), stricter than the pre-registered 8.
T3: Spearman of the within-stock percentile of each 09:35 measure with the 09:35->10:30 return in sigma, on VF + SC + middle.
    Holm over the 7 first-5-minute measures (pre-registration said 6; 7 is stricter). Sensitivity: inverse-sampling-weight version
    (VF and SC are over-sampled relative to the middle, and the class is defined on the first hour)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
F = pd.read_csv(HERE / "out" / "features.csv", parse_dates=["date"])
m5 = HERE / "out" / "options_m5.csv"
if m5.exists(): F = F.merge(pd.read_csv(m5, parse_dates=["date"]), on=["sym", "date"], how="left")
ev = pd.read_csv(HERE / "out" / "events.csv", parse_dates=["date"])
F["M0 prior 2-day return (sig)"] = F.r2 / F.sig
F["M4 gap (sig)"] = F.gap_sig
rng = np.random.default_rng(0)


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); adj = np.empty_like(ps); run = 0
    for i, k in enumerate(o):
        run = max(run, (len(ps) - i) * ps[k]); adj[k] = min(1, run)
    return adj


def auc(a, b): return stats.mannwhitneyu(a, b).statistic / (len(a) * len(b))


def t2(df, cols):
    out = []
    for c in cols:
        a = df[df.cls == "VF"][c].dropna().to_numpy(); b = df[df.cls == "SC"][c].dropna().to_numpy()
        if len(a) < 8 or len(b) < 8: out.append({"measure": c, "n_vf": len(a), "n_sc": len(b)}); continue
        A = auc(a, b); bs = np.array([auc(rng.choice(a, len(a)), rng.choice(b, len(b))) for _ in range(2000)])
        p = min(1, 2 * min((bs <= 0.5).mean(), (bs >= 0.5).mean()) + 1 / 2000)
        out.append({"measure": c, "n_vf": len(a), "n_sc": len(b), "median_vf": float(np.median(a)), "median_sc": float(np.median(b)), "auc_vf_gt_sc": A, "p_boot": p,
                    "p_ranksum": float(stats.mannwhitneyu(a, b).pvalue)})
    ok = [r for r in out if "p_boot" in r]
    for r, h in zip(ok, holm([r["p_boot"] for r in ok])): r["p_holm"] = float(h); r["pass"] = bool(h < 0.05)
    return out


def wspearman(x, y, w):
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    mx, my = np.average(rx, weights=w), np.average(ry, weights=w)
    return np.sum(w * (rx - mx) * (ry - my)) / np.sqrt(np.sum(w * (rx - mx) ** 2) * np.sum(w * (ry - my) ** 2))


def t3(df, cols, y="ret 09:35->10:30 (sig)"):
    pop = ev.cls.value_counts(); smp = df.cls.value_counts(); w = df.cls.map(pop / smp).to_numpy()
    out = []
    for c in cols:
        x = df.groupby("sym")[c].rank(pct=True); ok = x.notna() & df[y].notna()
        rho, p = stats.spearmanr(x[ok], df[y][ok])
        wr = wspearman(x[ok].to_numpy(), df[y][ok].to_numpy(), w[ok.to_numpy()])
        dd = df[ok].assign(x=x[ok]); dates = dd.date.unique()
        boot = []
        for _ in range(1000):
            pick = dd[dd.date.isin(rng.choice(dates, len(dates)))]
            boot.append(stats.spearmanr(pick.x, pick[y])[0])
        out.append({"measure": c, "n": int(ok.sum()), "rho": float(rho), "p": float(p), "rho_weighted": float(wr),
                    "ci95_date_boot": [float(np.nanpercentile(boot, 2.5)), float(np.nanpercentile(boot, 97.5))]})
    for r, h in zip(out, holm([r["p"] for r in out])): r["p_holm"] = float(h); r["pass"] = bool(h < 0.05)
    return out


PRE = ["M0 prior 2-day return (sig)", "M1 premarket drift (last vs high, sig)", "pm_high_min_after_4am", "M2a premarket buy share", "M2b premarket retail-size share",
       "M3 opening imbalance / paired", "M4 gap (sig)", "M5a open above biggest +gamma strike", "M5b dealer gamma at open >0", "M5c distance to big +gamma support below (sig)"]
EARLY = ["M6 first-5m delta %", "M7 first-5m book imbalance", "M7b first-5m ask depth $", "M7c first-5m bid depth $", "M8 first-5m progress per 1k bought (sig)",
         "M9 first-5m spread bp", "M10 first-5m retail-size share"]
PRE = [c for c in PRE if c in F]
res = {"n": F.cls.value_counts().to_dict(), "T2_all": t2(F, PRE), "T3_all": t3(F, EARLY)}
for sc in ("market-wide", "single-name"):
    sub = F[(F.scope == sc) | (F.cls == "mid")]
    res[f"T2_{sc}"] = t2(sub[sub.cls != "mid"], PRE)
    res[f"T3_{sc}"] = t3(sub, EARLY)
json.dump(res, open(HERE / "out" / "tests.json", "w"), indent=1, default=float)
for k in ("T2_all", "T3_all"):
    print(k); print(pd.DataFrame(res[k]).drop(columns=[c for c in ("ci95_date_boot",) if c in pd.DataFrame(res[k])]).round(3).to_string(index=False))
