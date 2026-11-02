"""TSLA per-session implied moves around the election from the Oct 30 close (same method as election.py A1).
Usage: python tsla_event.py <TSLA eod Oct30 csv.gz> <IRX json> -> out/tsla_event.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent; HOL = ["2026-11-26"]
irx = json.load(open(sys.argv[2]))["chart"]["result"][0]; irx = pd.Series(irx["indicators"]["quote"][0]["close"], index=pd.to_datetime(irx["timestamp"], unit="s").normalize()).dropna() / 100
def b76(F, K, T, s, c):
    d1 = (np.log(F / K) + s * s * T / 2) / (s * np.sqrt(T)); d2 = d1 - s * np.sqrt(T)
    return np.where(c, F * norm.cdf(d1) - K * norm.cdf(d2), K * norm.cdf(-d2) - F * norm.cdf(-d1))
def iv(p, F, K, T, c):
    lo, hi = np.full(len(p), .01), np.full(len(p), 4.)
    for _ in range(50):
        m = (lo + hi) / 2; h = b76(F, K, T, m, c) > p; hi, lo = np.where(h, m, hi), np.where(h, lo, m)
    return (lo + hi) / 2
e = pd.read_csv(sys.argv[1]); e["date"] = pd.to_datetime(e.created.astype(str).str[:10]); e["expiration"] = pd.to_datetime(e.expiration)
e["cp"] = np.where(e.right.astype(str).str.upper().str.startswith("C"), "C", "P"); e["mid"] = (e.bid + e.ask) / 2
d = pd.Timestamp("2026-10-30"); e = e[e.date == d]; r = float(irx.asof(d)); W = {}
for ex, x in e.groupby("expiration"):
    if ex <= d or ex > pd.Timestamp("2026-11-30"): continue
    T = (ex - d).days / 365; x = x[(x.bid > 0) & (x.ask > 0)]; pv = x.pivot_table(index="strike", columns="cp", values="mid").dropna()
    if len(pv) < 4: continue
    k = (pv.C - pv.P).abs().idxmin(); F = k + np.exp(r * T) * (pv.loc[k, "C"] - pv.loc[k, "P"])
    near = pv.iloc[(pv.index - F).to_series().abs().argsort()[:2].to_numpy()]
    s = np.nanmean(iv(np.r_[near.C, near.P] * np.exp(r * T), F, np.r_[near.index, near.index], T, np.r_[np.ones(len(near), bool), np.zeros(len(near), bool)]))
    W[ex] = s * s * T
ex = sorted(W); sess = lambda a, b: int(np.busday_count((a + pd.Timedelta(days=1)).date(), (b + pd.Timedelta(days=1)).date(), holidays=HOL))
rows = [{"pair": f"{d.date()}->{ex[0].date()}", "sessions": sess(d, ex[0]), "per-session move %": round(100 * np.sqrt(W[ex[0]] / sess(d, ex[0])), 2)}]
for a, b in zip(ex[:-1], ex[1:]):
    n = sess(a, b); rows.append({"pair": f"{a.date()}->{b.date()}", "sessions": n, "per-session move %": round(100 * np.sqrt(max((W[b] - W[a]) / n, 0)), 2)})
base = [ (W[b] - W[a]) / sess(a, b) for a, b in zip(ex[:-1], ex[1:]) if a >= pd.Timestamp("2026-11-06") and b <= pd.Timestamp("2026-11-20")]
bl = float(np.median(base)); a, b = max(x for x in ex if x < pd.Timestamp("2026-11-04")), min(x for x in ex if x >= pd.Timestamp("2026-11-04"))
n = sess(a, b); excess = (W[b] - W[a]) - n * bl
res = {"sessions": rows, "baseline session move % (Nov 6-20 pairs)": round(100 * np.sqrt(bl), 2), "election pair": f"{a.date()}->{b.date()}", "sessions in pair": n,
       "excess variance (move-equivalent %)": round(100 * np.sign(excess) * np.sqrt(abs(excess)), 2), "excess as % of one normal session's variance": round(100 * excess / bl, 1)}
json.dump(res, open(HERE / "out" / "tsla_event.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
