"""Amendment A1/A2 confirmation: E1 (regime-aligned), E2 (Monday), E3 (high VIX) on SPY 2020-23 (primary), QQQ, TSLA;
plus the S1 shift null and the 24-variant grid (joint max-t) per set. Usage: python confirm.py -> out/confirm.json"""
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"; O = HERE / "out"
K = "S0_5_10R"; VIXCUT = 17.86
VAR = [f"{s}_{m}_{e}" for s in ("S0", "S1") for m in (1, 5, 15, 30) for e in ("close", "10R", "2R")]
u = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?period1=1575158400&period2=1793750400&interval=1d"
r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["chart"]["result"][0]
vix = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").tz_localize(None).normalize())
vix = vix[~vix.index.duplicated(keep="last")].dropna(); vix_prev = vix.shift(1)
pl = pd.read_csv(HERE.parent / "2026-10-27-flip-wicks" / "out" / "preopen_levels.csv", parse_dates=["date"]).set_index("date")
spy_px = pd.concat([pd.read_parquet(O / "days_SPY2020_d2.parquet").px935, pd.read_parquet(O / "days_SPY_d2.parquet").px935])
below = (spy_px < pl.flip_incl.reindex(spy_px.index)).where(pl.flip_incl.reindex(spy_px.index).notna())   # SPY's own regime, used cross-asset for QQQ/TSLA


def pnl(df, k, dirs=None):
    d = df[k + "_dir"].to_numpy() if dirs is None else dirs
    return np.where(d > 0, df[k + "_L"].fillna(0).to_numpy(), np.where(d < 0, df[k + "_S"].fillna(0).to_numpy(), 0.0))


tstat = lambda p: p.mean() / (p.std(ddof=1) / np.sqrt(len(p))) if p.std() > 0 else 0.0


def label_test(p, lab, side):
    """diff of mean pnl (lab==1 minus lab==0); null = circular shift of the label; side=+1 predicts >0, -1 predicts <0."""
    lab = np.asarray(lab, bool); N = len(p); f = lambda L: p[L].mean() - p[~L].mean()
    a = f(lab); null = np.array([f(np.roll(lab, s)) for s in range(20, N - 20)])
    pv = (null >= a).mean() if side > 0 else (null <= a).mean()
    return {"n flag": int(lab.sum()), "mean flag": round(float(p[lab].mean()), 2), "mean other": round(float(p[~lab].mean()), 2), "diff": round(float(a), 2), "p one-sided": round(float(pv), 4)}


def e1(df, bl):
    ok = bl.reindex(df.index).notna().to_numpy(); b = bl.reindex(df.index).fillna(False).to_numpy().astype(bool)[ok]
    d = df[K + "_dir"].to_numpy()[ok]; p = pnl(df, K)[ok]
    al = lambda B: np.where((B & (d > 0)) | (~B & (d < 0)), p, 0.0)
    a = al(b).mean(); null = np.array([al(np.roll(b, s)).mean() for s in range(20, len(b) - 20)])
    take = (b & (d > 0)) | (~b & (d < 0))
    return {"days": int(ok.sum()), "aligned trades": int(take.sum()), "aligned mean bp/day": round(float(a), 2), "aligned mean bp/trade": round(float(p[take].mean()), 2),
            "counter-aligned mean bp/trade": round(float(p[~take & (d != 0)].mean()), 2), "p one-sided (aligned > 0 vs shifted regime)": round(float((null >= a).mean()), 4),
            "by cell bp/trade [n]": {f"{'below' if B else 'above'} {'long' if s > 0 else 'short'}": [round(float(p[(b == B) & (d == s)].mean()), 2), int(((b == B) & (d == s)).sum())] for B in (True, False) for s in (1, -1)}}


def grid(df):
    N = len(df); act = {v: pnl(df, v) for v in VAR}; t = {v: tstat(act[v]) for v in VAR}
    nmax = np.array([max(tstat(pnl(df, v, np.roll(df[v + "_dir"].to_numpy(), s))) for v in VAR) for s in range(20, N - 20)])
    best = max(t, key=t.get)
    s1 = "S1_5_close"; d1 = df[s1 + "_dir"].to_numpy(); a1 = act[s1].mean()
    n1 = np.array([pnl(df, s1, np.roll(d1, s)).mean() for s in range(20, N - 20)])
    top = sorted(VAR, key=lambda v: -t[v])[:6]
    return {"best variant": best, "best t": round(float(t[best]), 2), "joint p (max-t over 24)": round(float((nmax >= t[best]).mean()), 4),
            "S1_5_close mean bp/day, shift p": [round(float(a1), 2), round(float((n1 >= a1).mean()), 4)],
            "top 6 [mean bp/day, t, hit]": {v: [round(float(act[v].mean()), 2), round(float(t[v]), 2), round(float((act[v][act[v] != 0] > 0).mean()), 3)] for v in top}}


res = {}
for lab in ["SPY2020", "SPY2020_d2", "QQQ", "QQQ_d2", "TSLA", "TSLA_d2", "SPY", "SPY_d2"]:
    df = pd.read_parquet(O / f"days_{lab}.parquet"); p = pnl(df, K)
    vp = vix_prev.reindex(df.index); okv = vp.notna().to_numpy()
    out = {"sessions": len(df), "S0 mean bp/day": round(float(p.mean()), 2),
           "E1 regime-aligned (SPY flip)": e1(df, below),
           "E2 Monday minus other": label_test(p, df.index.dayofweek == 0, +1),
           "E3 VIX>17.86 minus other": label_test(p[okv], (vp[okv] > VIXCUT).to_numpy(), -1),
           "grid": grid(df)}
    res[lab] = out
    print(lab, "| S0", out["S0 mean bp/day"], "| E1", out["E1 regime-aligned (SPY flip)"]["aligned mean bp/day"], out["E1 regime-aligned (SPY flip)"]["p one-sided (aligned > 0 vs shifted regime)"],
          "| E2", out["E2 Monday minus other"]["diff"], out["E2 Monday minus other"]["p one-sided"], "| E3", out["E3 VIX>17.86 minus other"]["diff"], out["E3 VIX>17.86 minus other"]["p one-sided"],
          "| grid best", out["grid"]["best variant"], out["grid"]["best t"], "joint p", out["grid"]["joint p (max-t over 24)"], "| S1", out["grid"]["S1_5_close mean bp/day, shift p"])
json.dump(res, open(O / "confirm.json", "w"), indent=1, default=str)
