"""Permanence study (pre-registered @ e2971b7): stock runs (42-stock panel, 1990-2025) and S&P runs; footprints X1-X3, X5, X6; X4 from skew.csv.
Spearman of within-stock footprint rank with P20; month-cluster bootstrap (10,000); Holm across X1-X6. Usage: python runs.py <scratchpad> -> out/runs.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; CX = S / "ctx"
rng = np.random.default_rng(0); B = 10000


def load(p):
    r = json.load(open(p))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return d[~d.index.duplicated(keep="last")].dropna()


def run_events(d, lo, hi, gap=20):
    d = d[(d.close > 0)]; c, o, v = d.close.to_numpy(), d.open.to_numpy(), d.volume.to_numpy().astype(float); idx = d.index
    n = len(c); r10 = np.full(n, np.nan); r10[10:] = c[10:] / c[:-10] - 1
    inwin = (idx >= lo) & (idx <= hi); thr = np.nanpercentile(r10[inwin], 90); out = []; nxt = 0
    lr = np.r_[np.nan, np.log(c[1:] / c[:-1])]; on = np.r_[np.nan, np.log(o[1:] / c[:-1])]
    amih = np.abs(lr) / np.where(c * v > 0, c * v, np.nan)
    for i in range(70, n - 20):
        if not inwin[i] or i < nxt or not (r10[i] >= thr and c[i] >= c[i - 10:i + 1].max()): continue
        run = c[i] - c[i - 10]
        if run <= 0: continue
        w, base = slice(i - 9, i + 1), slice(i - 69, i - 9)
        e = {"date": idx[i], "run_pct": 100 * r10[i], "P20": (c[i + 20] - c[i - 10]) / run, "P10": (c[i + 10] - c[i - 10]) / run,
             "G10": (c[i] - c[i + 1:i + 11].min()) / run, "X1_abvol": np.nanmean(v[w]) / np.nanmean(v[base]),
             "X2_amihud": np.nanmean(amih[w]) / np.nanmean(amih[base]), "X3_overnight": float(np.clip(np.nansum(on[w]) / np.nansum(lr[w]), -1, 2)), "i": i}
        e["cliff"] = int(e["G10"] >= 0.5); out.append(e); nxt = i + gap
    return pd.DataFrame(out), thr


def spear_boot(D, x, y="P20"):
    D = D[D[x].notna() & D[y].notna() & np.isfinite(D[x])].copy(); D["xr"] = D.groupby("sym")[x].rank(pct=True) if D.sym.nunique() > 1 else D[x].rank(pct=True)
    est = stats.spearmanr(D.xr, D[y])[0]; D["m"] = D.date.dt.to_period("M"); ms = D.m.unique(); idx = {m: np.flatnonzero(D.m.to_numpy() == m) for m in ms}
    xr, yy = D.xr.to_numpy(), D[y].to_numpy(); bs = np.empty(B)
    for k in range(B):
        j = np.concatenate([idx[m] for m in rng.choice(ms, len(ms))]); bs[k] = stats.spearmanr(xr[j], yy[j])[0]
    bs = bs[~np.isnan(bs)]
    return {"n": int(len(D)), "rho": float(est), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "p": float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / len(bs)))}


# stock panel
panel = {}
for p in sorted((S / "long").glob("*.json")):
    if p.stem == "GSPC": continue
    panel[p.stem] = load(p)
EV = []
for s, d in panel.items():
    e, thr = run_events(d, pd.Timestamp("1990-01-01"), pd.Timestamp("2025-12-31"))
    if len(e): EV.append(e.assign(sym=s))
EV = pd.concat(EV, ignore_index=True)
R = {}
for x, nm in (("X1_abvol", "X1 abnormal volume during the run"), ("X2_amihud", "X2 thinning liquidity (Amihud ratio)"), ("X3_overnight", "X3 overnight share of the run")):
    o = spear_boot(EV, x); o["rho_1990_2007"] = float(stats.spearmanr(EV[EV.date < "2008-01-01"].groupby("sym")[x].rank(pct=True), EV[EV.date < "2008-01-01"].P20, nan_policy="omit")[0])
    o["rho_2008_2025"] = float(stats.spearmanr(EV[EV.date >= "2008-01-01"].groupby("sym")[x].rank(pct=True), EV[EV.date >= "2008-01-01"].P20, nan_policy="omit")[0])
    o["rho_vs_G10"] = float(stats.spearmanr(EV.groupby("sym")[x].rank(pct=True), EV.G10, nan_policy="omit")[0])
    tq = EV.groupby("sym")[x].rank(pct=True); o["P20_median_top_tercile"] = float(EV[tq > 2 / 3].P20.median()); o["P20_median_bottom_tercile"] = float(EV[tq <= 1 / 3].P20.median())
    o["cliff_top_tercile"] = float(EV[tq > 2 / 3].cliff.mean()); o["cliff_bottom_tercile"] = float(EV[tq <= 1 / 3].cliff.mean())
    R[nm] = o
# X4 call skew on the 5 option names
sk = HERE / "out" / "skew.csv"
if sk.exists():
    K = pd.read_csv(sk, parse_dates=["date"]); E4 = []
    for s in ("TSLA", "NVDA", "QQQ", "MSFT", "MU"):
        d = load(CX / "daily" / f"{s}.json"); e, _ = run_events(d, pd.Timestamp("2020-02-01"), pd.Timestamp("2026-10-14"))
        if not len(e): continue
        k = K[K.sym == s].set_index("date"); idx = d.index
        e["X4_rr_chg"] = [k.rr25.get(idx[i]) - k.rr25.get(idx[i - 10]) if (idx[i] in k.index and idx[i - 10] in k.index) else np.nan for i in e.i]
        e["atm_chg"] = [k.atm_iv.get(idx[i]) - k.atm_iv.get(idx[i - 10]) if (idx[i] in k.index and idx[i - 10] in k.index) else np.nan for i in e.i]
        E4.append(e.assign(sym=s))
    E4 = pd.concat(E4, ignore_index=True)
    R["X4 call-skew (25-delta risk reversal) change during the run"] = spear_boot(E4, "X4_rr_chg") | {"old proxy, ATM IV change": spear_boot(E4, "atm_chg")}
# S&P runs: X5 dealer gamma, X6 breadth
spx = load(S / "ladder28" / "data" / "^GSPC_1d.json"); spx["volume"] = spx.volume.replace(0, np.nan).fillna(1.0)
E5, _ = run_events(spx, pd.Timestamp("1990-01-01"), pd.Timestamp("2025-12-31")); idx = spx.index
dix = pd.read_csv(S / "late28" / "DIX.csv", parse_dates=["date"]).set_index("date"); dix["low"] = dix.gex < dix.gex.rolling(252).quantile(0.2)
E5["X5_lowgamma_share"] = [dix.low.reindex(idx[i - 9:i + 1]).mean() if idx[i] >= pd.Timestamp("2011-06-01") else np.nan for i in E5.i]
r10p = pd.DataFrame({s: d.close.pct_change(10) for s, d in panel.items()})
E5["X6_breadth"] = [float((r10p.loc[idx[i]].dropna() > 0).mean()) if idx[i] in r10p.index else np.nan for i in E5.i]
E5["sym"] = "SPX"
R["X5 share of run sessions with low dealer gamma (S&P, 2011+)"] = spear_boot(E5, "X5_lowgamma_share")
x6 = spear_boot(E5.assign(X6n=-E5.X6_breadth), "X6n"); R["X6 narrowness = minus breadth (S&P runs)"] = x6
pred = {"X1": -1, "X2": -1, "X3": -1, "X4": -1, "X5": -1, "X6": -1}
ps = [v["p"] for v in R.values()]; o = np.argsort(ps); adj = np.empty(len(ps)); run = 0
for j, k in enumerate(o): run = max(run, (len(ps) - j) * ps[k]); adj[k] = min(1, run)
for (k, v), h in zip(R.items(), adj):
    v["p_holm"] = float(h); v["sign_as_predicted"] = bool(np.sign(v["rho"]) == pred[k[:2]])
    v["pass"] = bool(h < 0.05 and v["sign_as_predicted"] and (k[:2] not in ("X1", "X2", "X3") or (np.sign(v["rho_1990_2007"]) == np.sign(v["rho_2008_2025"]) == np.sign(v["rho"]))))
desc = {"stock runs": int(len(EV)), "stocks": int(EV.sym.nunique()), "P20 median": float(EV.P20.median()), "cliff rate": float(EV.cliff.mean()), "S&P runs": int(len(E5))}
json.dump({"tests": R, "describe": desc}, open(HERE / "out" / "runs.json", "w"), indent=1, default=float)
EV.drop(columns="i").to_csv(HERE / "out" / "stock_runs.csv", index=False); E5.drop(columns="i").to_csv(HERE / "out" / "spx_runs.csv", index=False)
print(json.dumps(desc)); pd.set_option("display.width", 250)
for k, v in R.items(): print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items() if a != "old proxy, ATM IV change"})
if "X4 call-skew (25-delta risk reversal) change during the run" in R: print("old proxy:", R["X4 call-skew (25-delta risk reversal) change during the run"]["old proxy, ATM IV change"])
