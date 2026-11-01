"""Iteration 3 (pre-registered @ 12fbfb2, control corrected before running): are SPY's prior-day call/put walls barriers,
beyond round numbers? Usage: python walls.py <SPY 1m parquet> -> out/walls.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; ET = "America/New_York"; rng = np.random.default_rng(3); TOL = 0.001
m = pd.read_parquet(sys.argv[1], columns=["open", "high", "low", "close"]); m.index = m.index.tz_convert(ET)
m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
m["day"] = m.index.normalize().tz_localize(None)
D = m.groupby("day").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"), n=("close", "size"))
D = D[D.n >= 200]
g = pd.read_csv(HERE.parents[1] / "microstructure" / "out" / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")[["call_wall", "put_wall"]]
D = D.join(g.shift(1).rename(columns=lambda c: c + "_prev"), how="inner").dropna()
BINS = [0, 0.005, 0.01, 0.015, 0.02, 0.03]
rows = []
for day, r in D.iterrows():
    o = r.open
    for side in ("up", "dn"):
        lo_k = np.ceil(o * (1 if side == "up" else 1 - BINS[-1]) / 5) * 5; hi_k = np.floor(o * (1 + BINS[-1] if side == "up" else 1) / 5) * 5
        for K in np.arange(lo_k, hi_k + 5, 5):
            dist = (K - o) / o if side == "up" else (o - K) / o
            if dist <= 0 or dist > BINS[-1]: continue
            if side == "up":
                reached = r.high >= K * (1 - TOL); stall = reached and r.high <= K * (1 + TOL); inside = reached and r.close < K; wall = K == r.call_wall_prev
            else:
                reached = r.low <= K * (1 + TOL); stall = reached and r.low >= K * (1 - TOL); inside = reached and r.close > K; wall = K == r.put_wall_prev
            if not reached: continue
            rows.append({"day": day, "side": side, "K": K, "dist": dist, "bin": int(np.digitize(dist, BINS[1:-1])), "round10": int(K % 10 == 0), "wall": int(wall),
                         "stall": int(stall), "inside": int(inside)})
T = pd.DataFrame(rows)


def mh(df, col):
    """Mantel-Haenszel weighted difference wall - nonwall in P(col) across strata (side x bin x round10)."""
    num = den = 0.0
    for _, s in df.groupby(["side", "bin", "round10"]):
        w, nw = s[s.wall == 1], s[s.wall == 0]
        if len(w) == 0 or len(nw) == 0: continue
        n1, n0 = len(w), len(nw); wt = n1 * n0 / (n1 + n0); num += wt * (w[col].mean() - nw[col].mean()); den += wt
    return num / den if den else np.nan


days = T.day.unique(); dix = {d: i for i, d in enumerate(sorted(days))}; T["di"] = T.day.map(dix)
def boot(df, col, B=1000, block=20):
    nd = len(days); out = []; groups = {i: g for i, g in df.groupby("di")}
    for _ in range(B):
        starts = rng.integers(0, nd, nd // block + 1); idx = np.concatenate([np.arange(s, min(s + block, nd)) for s in starts])[:nd]
        out.append(mh(pd.concat([groups[i] for i in idx if i in groups]), col))
    return np.array(out)


res = {"days": int(D.shape[0]), "reached strike-days": int(len(T)), "wall cases": int(T.wall.sum())}
for side in ("up", "dn"):
    S = T[T.side == side]
    for col in ("stall", "inside"):
        est = mh(S, col); b = boot(S, col)
        res[f"{'call wall (highs)' if side == 'up' else 'put wall (lows)'} {col}"] = {
            "wall rate": round(float(S[S.wall == 1][col].mean()), 3), "non-wall rate (raw)": round(float(S[S.wall == 0][col].mean()), 3),
            "MH diff (matched distance x roundness)": round(float(est), 3), "90% CI": np.round(np.quantile(b, [.05, .95]), 3).tolist(),
            "p (diff <= 0)": round(float((b <= 0).mean()), 4), "n wall": int(S.wall.sum())}
for lab, msk in (("R1 2020-21", T.day < "2022-01-01"), ("R2 2022+", T.day >= "2022-01-01")):
    res[f"era {lab}"] = {f"{s} stall MH diff": round(float(mh(T[msk & (T.side == s)], "stall")), 3) for s in ("up", "dn")} | {f"{s} n wall": int(T[msk & (T.side == s)].wall.sum()) for s in ("up", "dn")}
res["round-number check (non-walls): stall rate $10 vs other $5"] = {s: [round(float(T[(T.side == s) & (T.wall == 0) & (T.round10 == 1)].stall.mean()), 3), round(float(T[(T.side == s) & (T.wall == 0) & (T.round10 == 0)].stall.mean()), 3)] for s in ("up", "dn")}
json.dump(res, open(HERE / "out" / "walls.json", "w"), indent=1)
print(json.dumps(res, indent=1))
