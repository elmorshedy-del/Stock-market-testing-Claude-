"""Tests C1-C12 as pre-registered @ 1696818. Outcomes demeaned within stock (over the rows each test uses).
Contrast = mean(context) - mean(rest) [C2: after vs before; C10: top vs bottom tercile]; C4, C11 = Spearman.
Date-block bootstrap (5,000), two-sided p; Holm across the 12. Usage: python tests_ctx.py -> out/tests_ctx.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
C = pd.read_csv(HERE / "out" / "context.csv", parse_dates=["date"])
O = HERE / "out" / "options_ctx.csv"
if O.exists(): C = C.merge(pd.read_csv(O, parse_dates=["date"]), on=["sym", "date"], how="left")
rng = np.random.default_rng(0); B = 5000


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); adj = np.empty_like(ps); run = 0
    for i, k in enumerate(o):
        run = max(run, (len(ps) - i) * ps[k]); adj[k] = min(1, run)
    return adj


def boot_p(bs):
    return float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / B))


def contrast(df, a, b, y):
    df = df[a | b].copy(); df["yd"] = df[y] - df.groupby("sym")[y].transform("mean"); df["g"] = a[a | b].astype(int)
    est = df[df.g == 1].yd.mean() - df[df.g == 0].yd.mean()
    dates = df.date.unique(); idx = {d: np.flatnonzero(df.date.to_numpy() == d) for d in dates}
    yd, g = df.yd.to_numpy(), df.g.to_numpy(); bs = np.empty(B)
    for i in range(B):
        k = np.concatenate([idx[d] for d in rng.choice(dates, len(dates))])
        bs[i] = yd[k][g[k] == 1].mean() - yd[k][g[k] == 0].mean() if (g[k] == 1).any() and (g[k] == 0).any() else np.nan
    bs = bs[~np.isnan(bs)]
    return {"n_context": int(df.g.sum()), "n_rest": int((df.g == 0).sum()), "estimate": float(est),
            "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "p": boot_p(bs),
            "vf_rate_context": float((df[df.g == 1].cls == "VF").mean()), "vf_rate_rest": float((df[df.g == 0].cls == "VF").mean()),
            "sc_rate_context": float((df[df.g == 1].cls == "SC").mean()), "sc_rate_rest": float((df[df.g == 0].cls == "SC").mean())}


def spear(df, x, y):
    df = df[df[x].notna() & df[y].notna()].copy()
    df["xr"] = df.groupby("sym")[x].rank(pct=True); df["yd"] = df[y] - df.groupby("sym")[y].transform("mean")
    est = stats.spearmanr(df.xr, df.yd)[0]
    dates = df.date.unique(); idx = {d: np.flatnonzero(df.date.to_numpy() == d) for d in dates}
    xr, yd = df.xr.to_numpy(), df.yd.to_numpy(); bs = np.empty(B)
    for i in range(B):
        k = np.concatenate([idx[d] for d in rng.choice(dates, len(dates))]); bs[i] = stats.spearmanr(xr[k], yd[k])[0]
    return {"n": len(df), "estimate": float(est), "ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))], "p": boot_p(bs[~np.isnan(bs)])}


stk = C.sym != "QQQ"; opt = C.sym.isin(["TSLA", "NVDA", "QQQ"]) & (C.date >= "2020-01-15") & (C.date <= "2026-10-14") & C.C1_pin.notna() if "C1_pin" in C else None
T = {}
if opt is not None:
    T["C1 pin pull (Y1, -)"] = contrast(C[opt], C[opt].C1_pin == 1, C[opt].C1_pin == 0, "Y1")
T["C2 gamma release: 5 days after vs 5 up to monthly expiry (Y2, +)"] = contrast(C, C.C2_after == 1, C.C2_before == 1, "Y2")
T["C3 turn of month (Y1, +)"] = contrast(C, C.C3_turn == 1, C.C3_turn == 0, "Y1")
T["C4 month-end rebalance: MTD SPY-TLT vs Y1, last 4 days (rho, -)"] = spear(C[C.C4_window == 1], "mtd_spy_tlt", "Y1")
T["C5 extended, top tercile vs 20-day mean (Y1, -)"] = contrast(C, C.ext_top == 1, C.ext_top == 0, "Y1")
T["C6 breakout from a base (Y1, +)"] = contrast(C, C.C6_breakout == 1, C.C6_breakout == 0, "Y1")
T["C7 own earnings reaction (Y1, +)"] = contrast(C[stk], C[stk].C7_earn == 1, C[stk].C7_earn == 0, "Y1")
T["C8 CPI / jobs / post-FOMC (Y1, +)"] = contrast(C, C.C8_macro == 1, C.C8_macro == 0, "Y1")
T["C9 own (idiosyncratic) gap, top tercile (Y1, -)"] = contrast(C[stk], C[stk].idio_top == 1, C[stk].idio_top == 0, "Y1")
T["C10 market GEX top vs bottom tercile (Y2, -)"] = contrast(C, C.gex_pct >= 2 / 3, C.gex_pct <= 1 / 3, "Y2")
if opt is not None:
    T["C11 own-dealer hedge pressure vs Y1 (rho, -)"] = spear(C[opt], "C11_pressure", "Y1")
bb = C.sym.isin(["AAPL", "NVDA"])
T["C12 buyback blackout, AAPL+NVDA (Y1, -)"] = contrast(C[bb], C[bb].blackout == 1, C[bb].blackout == 0, "Y1")
pred = {k: (-1 if k.endswith("-)") else 1) for k in T}
for (k, v), h in zip(T.items(), holm([v["p"] for v in T.values()])):
    v["p_holm"] = float(h); v["pass"] = bool(h < 0.05); v["predicted_sign"] = pred[k]; v["sign_as_predicted"] = bool(np.sign(v["estimate"]) == pred[k])
# placebo and sensitivity (outside the family)
ts = C.sym == "TSLA"
X = {"C12 placebo TSLA (no buybacks)": contrast(C[ts], C[ts].blackout == 1, C[ts].blackout == 0, "Y1"),
     "C12 sensitivity, earnings-reaction days removed": contrast(C[bb & (C.C7_earn == 0)], C[bb & (C.C7_earn == 0)].blackout == 1, C[bb & (C.C7_earn == 0)].blackout == 0, "Y1")}
# Family F (Amendment 1 @ 0ac6f73): fragility, Holm across the 7
FR = HERE / "out" / "fragility.csv"; TF = {}
if FR.exists():
    G = C.merge(pd.read_csv(FR, parse_dates=["date"]), on=["sym", "date"], how="inner")
    tert = lambda col, top: (G.groupby("sym")[col].rank(pct=True) > 2 / 3) if top else (G.groupby("sym")[col].rank(pct=True) <= 1 / 3)
    has = lambda col: G[col].notna()
    m = has("F1_tow"); TF["F1 clientele tug-of-war, top tercile (Y1, -)"] = contrast(G[m], tert("F1_tow", True)[m], ~tert("F1_tow", True)[m], "Y1")
    m = has("F2_illiq_ratio"); TF["F2 thinning liquidity, top tercile (Y2, +)"] = contrast(G[m], tert("F2_illiq_ratio", True)[m], ~tert("F2_illiq_ratio", True)[m], "Y2")
    m = has("F3_vol_below"); TF["F3 air pocket below, bottom tercile (Y1, -)"] = contrast(G[m], tert("F3_vol_below", False)[m], ~tert("F3_vol_below", False)[m], "Y1")
    if "F4_near_share" in G:
        m = has("F4_near_share"); TF["F4 no dealer cushion, bottom tercile (Y2, +)"] = contrast(G[m], tert("F4_near_share", False)[m], ~tert("F4_near_share", False)[m], "Y2")
        m = has("F5_call_oi_chg"); TF["F5 fresh call crowding, top tercile (Y1, -)"] = contrast(G[m], tert("F5_call_oi_chg", True)[m], ~tert("F5_call_oi_chg", True)[m], "Y1")
    m = has("F6_dpi5"); TF["F6 off-exchange short share, top tercile (Y1, +)"] = contrast(G[m], tert("F6_dpi5", True)[m], ~tert("F6_dpi5", True)[m], "Y1")
    m = has("breadth50"); nar = (G.breadth50 <= G.loc[m, "breadth50"].quantile(1 / 3)) & (G.qqq_near_high == 1)
    TF["F7 narrow market near the QQQ high (Y1, -)"] = contrast(G[m], nar[m], ~nar[m], "Y1")
    for (k, v), h in zip(TF.items(), holm([v["p"] for v in TF.values()])):
        v["p_holm"] = float(h); v["pass"] = bool(h < 0.05); v["sign_as_predicted"] = bool(np.sign(v["estimate"]) == (-1 if k.endswith("-)") else 1))
json.dump({"family": T, "outside_family": X, "fragility": TF}, open(HERE / "out" / "tests_ctx.json", "w"), indent=1)
pd.set_option("display.width", 250)
R = pd.DataFrame(T).T[["n_context", "n_rest", "n", "estimate", "ci95", "p", "p_holm", "pass", "sign_as_predicted", "vf_rate_context", "vf_rate_rest", "sc_rate_context", "sc_rate_rest"]] if True else None
R["ci95"] = R.ci95.apply(lambda c: f"[{c[0]:+.2f}, {c[1]:+.2f}]")
print(R.to_string()); print(pd.DataFrame(X).T[["n_context", "n_rest", "estimate", "p"]].to_string())
if TF:
    R2 = pd.DataFrame(TF).T[["n_context", "n_rest", "estimate", "ci95", "p", "p_holm", "pass", "sign_as_predicted", "vf_rate_context", "vf_rate_rest", "sc_rate_context", "sc_rate_rest"]]
    R2["ci95"] = R2.ci95.apply(lambda c: f"[{c[0]:+.2f}, {c[1]:+.2f}]"); print(R2.to_string())
