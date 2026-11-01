"""Descriptive follow-up to iteration 3b (not a new test): what a call-wall touch means for the rest of the day
(overshoot beyond the strike, close, time of touch), wall vs ordinary $5 strikes reweighted to the walls' distance x
roundness mix; plus era splits. Usage: python walls_exit.py <SPY 1m parquet> <QQQ 1m parquet> -> out/walls_exit.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; ET = "America/New_York"; TOL = 0.001
res = {}
for und, path in (("SPY", sys.argv[1]), ("QQQ", sys.argv[2])):
    m = pd.read_parquet(path, columns=["high", "close"]); m.index = m.index.tz_convert(ET)
    m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
    m["day"] = m.index.normalize().tz_localize(None)
    days = {d: (x.high.to_numpy(), x.close.to_numpy(), ((x.index.hour - 9) * 60 + x.index.minute - 30).to_numpy()) for d, x in m.groupby("day")}
    T = pd.read_csv(HERE / "out" / f"walls_b_events_{und}.csv", parse_dates=["day"]); T = T[T.side == "up"].copy()
    ov, cl, tm = [], [], []
    for d, K in zip(T.day, T.K):
        h, c, mi = days[d]; i0 = int(np.argmax(h >= K * (1 - TOL)))
        ov.append(100 * (h.max() / K - 1)); cl.append(100 * (c[-1] / K - 1)); tm.append(int(mi[i0]))
    T["over"], T["close_vs_K"], T["touch_min"] = ov, cl, tm
    # reweight controls to the walls' stratum mix (same strata as iteration 3)
    T["st"] = T.pbin.astype(str) + "_" + T.round10.astype(str)
    nw = T[T.wall == 1].st.value_counts(); nc = T[T.wall == 0].st.value_counts()
    T["w"] = np.where(T.wall == 1, 1.0, T.st.map(nw / nc).fillna(0.0))
    W, C = T[T.wall == 1], T[(T.wall == 0) & (T.w > 0)]

    def wq(x, w, q):
        o = np.argsort(x); cw = np.cumsum(w[o]) / w.sum(); return float(np.interp(q, cw, x[o]))

    def summ(S):
        x, w = S.over.to_numpy(), S.w.to_numpy()
        return {"n": int(len(S)), "P(high stops within +-0.1% of K)": round(float(np.average(x <= 0.1, weights=w)), 3),
                "P(runs > 0.25% past K)": round(float(np.average(x > 0.25, weights=w)), 3),
                "P(runs > 0.5% past K)": round(float(np.average(x > 0.5, weights=w)), 3), "P(runs > 1% past K)": round(float(np.average(x > 1.0, weights=w)), 3),
                "overshoot % quantiles 50/75/90": [round(wq(x, w, q), 3) for q in (.5, .75, .9)],
                "P(close below K)": round(float(np.average(S.close_vs_K.to_numpy() < 0, weights=w)), 3),
                "median close vs K %": round(wq(S.close_vs_K.to_numpy(), w, .5), 3),
                "share of first touches before 10:30": round(float(np.average(S.touch_min.to_numpy() < 60, weights=w)), 3)}
    R = {"call wall touches": summ(W), "ordinary $5 strikes (reweighted)": summ(C)}
    R["CDF of overshoot (% past K) for figure"] = {lab: np.round(np.sort(S.over.to_numpy()), 3).tolist() for lab, S in (("wall", W), ("ordinary", C))}
    R["ordinary weights for figure"] = np.round(C.w.to_numpy()[np.argsort(C.over.to_numpy())], 4).tolist()
    # era splits, iteration-3 design (raw stall rates + reweighted difference)
    for lab, lo, hi in (("R1 2020-21", "2020-01-01", "2022-01-01"), ("R2 2022+", "2022-01-01", "2027-01-01"), ("2024-26", "2024-01-01", "2027-01-01")):
        Wi = W[(W.day >= lo) & (W.day < hi)]; Ti = T[(T.day >= lo) & (T.day < hi)]
        nwi = Ti[Ti.wall == 1].st.value_counts(); nci = Ti[Ti.wall == 0].st.value_counts()
        Ci = Ti[Ti.wall == 0]; wi = Ci.st.map(nwi / nci).fillna(0.0)
        R[f"era {lab}"] = {"n walls": int(len(Wi)), "wall stall": round(float((Wi.over <= 0.1).mean()), 3),
                           "ordinary stall (reweighted)": round(float(np.average(Ci.over <= 0.1, weights=wi)), 3) if wi.sum() else None}
    res[und] = R
json.dump(res, open(HERE / "out" / "walls_exit.json", "w"), indent=1)
print(json.dumps({u: {k: v for k, v in R.items() if "figure" not in k} for u, R in res.items()}, indent=1))
