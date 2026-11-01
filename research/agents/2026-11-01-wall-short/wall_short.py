"""Pre-registered @ 611b2f5: short at the prior day's call wall. 32-config grid, select on 2020-23, test 2024-26 (T1),
QQQ (T2), placebo ordinary strike (T3), persistence. Usage: python wall_short.py <SPY 1m> <QQQ 1m> -> out/wall_short.json"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; ET = "America/New_York"; COST = 1e-4; TICK = 0.01
rng = np.random.default_rng(7)
STOPS = [0.0015, 0.0025, 0.0040, 0.0060]; EXITS = ["t0.25", "t0.50", "close", "60m"]; FILTERS = ["all", "above_flip"]


def load(path, und):
    m = pd.read_parquet(path, columns=["open", "high", "low", "close"]); m.index = m.index.tz_convert(ET)
    m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
    day = m.index.normalize().tz_localize(None); mins = (m.index.hour - 9) * 60 + m.index.minute - 30
    bars = {}
    for d, idx in pd.Series(np.arange(len(m)), index=day).groupby(level=0):
        ii = idx.to_numpy()
        if len(ii) < 200: continue
        bars[d] = (m.open.to_numpy()[ii], m.high.to_numpy()[ii], m.low.to_numpy()[ii], m.close.to_numpy()[ii], np.asarray(mins[ii]))
    g = pd.read_csv(HERE.parents[1] / "microstructure" / "out" / f"td_gamma_{und}.csv", parse_dates=["date"]).set_index("date")
    p = g[["call_wall", "spot", "flip_classic"]].shift(1)
    return bars, p


def sim(b, K, s, ex):
    o, h, l, c, mi = b
    hit = np.nonzero((h >= K + TICK) & (mi < 360))[0]
    if not len(hit): return None
    i = hit[0]; stop = K * (1 + s); tgt = K * (1 - float(ex[1:]) / 100) if ex.startswith("t") else None
    end = min(i + 60, len(c) - 1) if ex == "60m" else len(c) - 1
    if h[i] >= stop: return (K - (stop + TICK)) / K - COST, i, "stop"
    for j in range(i + 1, end + 1):
        if h[j] >= stop: return (K - (max(stop, o[j]) + TICK)) / K - COST, i, "stop"
        if tgt is not None and l[j] <= tgt - TICK: return (K - tgt) / K - COST, i, "target"
    return (K - c[end]) / K - COST, i, "time"


def run(bars, P, s, ex, flt, level="wall"):
    out = []
    for d, b in bars.items():
        if d not in P.index or d > pd.Timestamp("2026-10-09"): continue
        r = P.loc[d]
        if not np.isfinite(r.call_wall): continue
        o = b[0][0]
        if level == "wall":
            K = r.call_wall
        else:   # placebo: nearest ordinary $5 strike above the open, not the wall
            K = np.ceil(o / 5) * 5
            if K == r.call_wall or K <= o: K += 5
            if K == r.call_wall: K += 5
        if not (0 < (K - o) / o <= 0.01): continue
        if flt == "above_flip" and not (np.isfinite(r.flip_classic) and r.spot > r.flip_classic): continue
        x = sim(b, K, s, ex)
        if x is not None: out.append((d, x[0], x[2]))
    return pd.DataFrame(out, columns=["day", "ret", "how"])


def summ(T):
    if len(T) == 0: return {"n": 0}
    x = T.ret.to_numpy(); bs = rng.choice(x, (5000, len(x))).mean(1); yrs = T.groupby(T.day.dt.year).ret.sum()
    eq = np.cumsum(x)
    return {"n": int(len(x)), "mean % per trade": round(100 * x.mean(), 4), "win rate": round(float((x > 0).mean()), 3),
            "avg win %": round(100 * x[x > 0].mean(), 3) if (x > 0).any() else None, "avg loss %": round(100 * x[x <= 0].mean(), 3) if (x <= 0).any() else None,
            "total % (sum)": round(100 * x.sum(), 2), "max drawdown % (sum)": round(100 * float((np.maximum.accumulate(eq) - eq).max()), 2),
            "p (mean<=0)": round(float((bs <= 0).mean()), 4), "exits": T.how.value_counts().to_dict(),
            "by year %": {int(k): round(100 * v, 2) for k, v in yrs.items()}}


res = {}
bars, P = load(sys.argv[1], "SPY")
grid = []
for s, ex, flt in itertools.product(STOPS, EXITS, FILTERS):
    T = run(bars, P, s, ex, flt); ins = T[T.day < "2024-01-01"]; oos = T[T.day >= "2024-01-01"]
    grid.append({"stop %": 100 * s, "exit": ex, "filter": flt, "IS n": len(ins), "IS mean %": round(100 * ins.ret.mean(), 4) if len(ins) else None,
                 "OOS n": len(oos), "OOS mean %": round(100 * oos.ret.mean(), 4) if len(oos) else None, "full mean %": round(100 * T.ret.mean(), 4) if len(T) else None})
G = pd.DataFrame(grid); res["grid (all 32, IS=2020-23, OOS=2024-26)"] = G.to_dict("records")
best = G[G["IS n"] >= 30].sort_values("IS mean %", ascending=False).iloc[0]
s, ex, flt = best["stop %"] / 100, best["exit"], best["filter"]
res["chosen on 2020-23"] = {"stop %": best["stop %"], "exit": ex, "filter": flt}
T = run(bars, P, s, ex, flt)
res["in-sample 2020-23"] = summ(T[T.day < "2024-01-01"])
res["T1 SPY out-of-sample 2024-26"] = summ(T[T.day >= "2024-01-01"])
res["SPY full 2020-26"] = summ(T)
res["eras"] = {"R1 2020-21": summ(T[T.day < "2022-01-01"]), "R2 2022+": summ(T[T.day >= "2022-01-01"])}
Pl = run(bars, P, s, ex, flt, level="placebo"); res["T3 placebo ordinary strike, SPY 2020-26"] = summ(Pl)
days = sorted(set(T.day) | set(Pl.day)); wm = T.groupby("day").ret.sum().reindex(days); wn = T.groupby("day").size().reindex(days).fillna(0)
pm = Pl.groupby("day").ret.sum().reindex(days); pn = Pl.groupby("day").size().reindex(days).fillna(0)
A = np.c_[wm.fillna(0), wn, pm.fillna(0), pn]; diffs = []
for _ in range(5000):
    k = A[rng.integers(0, len(A), len(A))].sum(0); diffs.append(k[0] / k[1] - k[2] / k[3])
res["T3 wall minus placebo mean %"] = {"diff": round(100 * (T.ret.mean() - Pl.ret.mean()), 4), "p (diff<=0)": round(float((np.array(diffs) <= 0).mean()), 4)}
qb, qP = load(sys.argv[2], "QQQ"); Q = run(qb, qP, s, ex, flt); res["T2 QQQ 2020-26 (same config)"] = summ(Q)
yrs = res["SPY full 2020-26"]["by year %"]; res["persistence: SPY years positive"] = f"{sum(v > 0 for v in yrs.values())} of {len(yrs)}"
# robustness: how many of the 32 configs are positive out-of-sample / full
res["grid summary"] = {"configs with IS mean > 0": int((G["IS mean %"] > 0).sum()), "configs with OOS mean > 0": int((G["OOS mean %"] > 0).sum()),
                       "configs with full mean > 0": int((G["full mean %"] > 0).sum())}
T.to_csv(HERE / "out" / "trades_spy_chosen.csv", index=False); Q.to_csv(HERE / "out" / "trades_qqq_chosen.csv", index=False)
json.dump(res, open(HERE / "out" / "wall_short.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if not k.startswith("grid (")}, indent=1, default=str))
print(G.to_string())
