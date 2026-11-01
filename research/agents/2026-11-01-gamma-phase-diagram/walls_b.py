"""Iteration 3b (pre-registered @ 71d396c): are gamma walls barriers? Artefact checks (A1 volatility strata, A2 level
history + stale walls), QQQ replication (R), bunching of day extremes at the wall (B), pinning time after a touch (M2).
Usage: python walls_b.py <SPY 1m parquet> <QQQ 1m parquet> <VIX json> -> out/walls_b.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; ET = "America/New_York"; TOL = 0.001; MAXD = 0.03; B = 2000
rng = np.random.default_rng(31)
r = json.load(open(sys.argv[3]))["chart"]["result"][0]
vix = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC")
                .tz_convert(ET).normalize().tz_localize(None)).dropna()
vix = vix[~vix.index.duplicated(keep="last")]
PBINS = [0, 0.005, 0.01, 0.015, 0.02, 0.03]; SBINS = [0, 0.5, 1, 1.5, 2, 3]


def load(path, und):
    m = pd.read_parquet(path, columns=["open", "high", "low", "close"]); m.index = m.index.tz_convert(ET)
    m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
    m["day"] = m.index.normalize().tz_localize(None)
    D = m.groupby("day").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"), n=("close", "size"))
    D = D[D.n >= 200]
    D["prev_high"], D["prev_low"] = D.high.shift(1), D.low.shift(1)
    D["prev_high5"], D["prev_low5"] = D.high.rolling(5).max().shift(1), D.low.rolling(5).min().shift(1)
    g = pd.read_csv(HERE.parents[1] / "microstructure" / "out" / f"td_gamma_{und}.csv", parse_dates=["date"]).set_index("date")[["call_wall", "put_wall"]]
    D = D.join(pd.concat([g.shift(1).add_suffix("_prev"), g.shift(10).add_suffix("_stale")], axis=1), how="inner")
    D["vixp"] = vix.shift(1).reindex(D.index, method="ffill")
    D = D.dropna(subset=["call_wall_prev", "put_wall_prev", "vixp", "prev_high5"])
    D["sig"] = D.vixp / 100 / np.sqrt(252); D["vt"] = pd.qcut(D.vixp, 3, labels=False)
    mins = {d: (x.high.to_numpy(), x.low.to_numpy(), x.close.to_numpy()) for d, x in m[m.day.isin(D.index)].groupby("day")}
    return D, mins


def table(D, mins):
    rows = []
    for day, r in D.iterrows():
        o = r.open; h, l, c = mins[day]
        for side in ("up", "dn"):
            Ks = np.arange(np.ceil(o / 5) * 5, np.floor(o * (1 + MAXD) / 5) * 5 + 1, 5) if side == "up" else \
                np.arange(np.ceil(o * (1 - MAXD) / 5) * 5, np.floor(o / 5) * 5 + 1, 5)
            for K in Ks:
                dist = (K - o) / o if side == "up" else (o - K) / o
                if dist <= 0 or dist > MAXD: continue
                if side == "up":
                    if r.high < K * (1 - TOL): continue
                    stall = r.high <= K * (1 + TOL); wall = K == r.call_wall_prev
                    stale = K == r.call_wall_stale and r.call_wall_stale != r.call_wall_prev
                    hist = min(abs(K / r.prev_high - 1), abs(K / r.prev_high5 - 1)) <= 0.0025
                    i0 = int(np.argmax(h >= K * (1 - TOL)))
                else:
                    if r.low > K * (1 + TOL): continue
                    stall = r.low >= K * (1 - TOL); wall = K == r.put_wall_prev
                    stale = K == r.put_wall_stale and r.put_wall_stale != r.put_wall_prev
                    hist = min(abs(K / r.prev_low - 1), abs(K / r.prev_low5 - 1)) <= 0.0025
                    i0 = int(np.argmax(l <= K * (1 + TOL)))
                ds = dist / r.sig
                rows.append({"day": day, "side": side, "K": K, "pbin": int(np.digitize(dist, PBINS[1:-1])),
                             "sbin": int(np.digitize(ds, SBINS[1:-1])) if ds <= SBINS[-1] else -1, "vt": int(r.vt),
                             "round10": int(K % 10 == 0), "wall": int(wall), "stale": int(stale and not wall), "nearhist": int(hist), "dist": round(dist, 6), "ds": round(ds, 4),
                             "stall": int(stall), "pin": float(np.mean(np.abs(c[i0:] / K - 1) <= TOL))})
    return pd.DataFrame(rows)


def mh(sid, t, y, w):
    ns = sid.max() + 1
    n1, n0 = np.bincount(sid, w * t, ns), np.bincount(sid, w * (1 - t), ns)
    s1, s0 = np.bincount(sid, w * t * y, ns), np.bincount(sid, w * (1 - t) * y, ns)
    ok = (n1 > 0) & (n0 > 0)
    if not ok.any(): return np.nan
    wt = n1[ok] * n0[ok] / (n1[ok] + n0[ok])
    return float(np.sum(wt * (s1[ok] / n1[ok] - s0[ok] / n0[ok])) / np.sum(wt))


def weights(nd, block=20):
    W = np.empty((B, nd))
    for b in range(B):
        st = rng.integers(0, nd, nd // block + 1)
        W[b] = np.bincount(np.concatenate([np.arange(s, min(s + block, nd)) for s in st])[:nd], minlength=nd)
    return W


def test(T, mask, treat, y, cols, W, dix):
    S = T[mask]; t = treat[mask].astype(float); yy = S[y].to_numpy(float)
    sid = S.groupby(cols, sort=False).ngroup().to_numpy(); di = S.day.map(dix).to_numpy()
    est = mh(sid, t, yy, np.ones(len(S))); bs = np.array([mh(sid, t, yy, W[b, di]) for b in range(B)])
    return {"n treated": int(t.sum()), "treated mean": round(float(yy[t == 1].mean()), 3) if t.sum() else None,
            "control mean (raw)": round(float(yy[t == 0].mean()), 3), "MH diff": round(est, 3),
            "90% CI": np.round(np.nanquantile(bs, [.05, .95]), 3).tolist(),
            "p (diff<=0)": round(float(np.nanmean(bs <= 0)), 4), "p (diff>=0)": round(float(np.nanmean(bs >= 0)), 4)}


def bunch(x, lo=-2.5, hi=1.5, bw=0.05, win=0.15, deg=5):
    edges = np.round(np.arange(lo, hi + bw / 2, bw), 4); cen = (edges[:-1] + edges[1:]) / 2
    cnt = np.histogram(x, edges)[0].astype(float)

    def excess(c0):
        inw = np.abs(cen - c0) < win; p = np.polyfit(cen[~inw], cnt[~inw], deg); cf = np.polyval(p, cen)
        return (cnt[inw].sum() - cf[inw].sum()) / cf[inw].sum(), cf
    e0, cf0 = excess(0.0)
    pl = np.array([excess(c)[0] for c in np.round(np.arange(-2.0, 1.0 + 1e-9, 0.05), 2) if abs(c) >= 0.3 - 1e-9])
    return {"n days": int(len(x)), "in range": int(((x >= lo) & (x < hi)).sum()), "excess mass": round(float(e0), 3),
            "placebo positions": int(len(pl)), "p (share of placebos >= observed)": round(float((pl >= e0).mean()), 3),
            "p (share of placebos <= observed)": round(float((pl <= e0).mean()), 3), "placebo excess 5/50/95%": np.round(np.quantile(pl, [.05, .5, .95]), 3).tolist(),
            "_hist": {"centres": cen.round(3).tolist(), "counts": cnt.astype(int).tolist(), "cf": np.round(cf0, 2).tolist()}}


res = {}; S3 = ["side", "pbin", "round10"]
for und, path in (("SPY", sys.argv[1]), ("QQQ", sys.argv[2])):
    D, mins = load(path, und); T = table(D, mins); days = sorted(D.index); dix = {d: i for i, d in enumerate(days)}; W = weights(len(days))
    up, dn = (T.side == "up").to_numpy(), (T.side == "dn").to_numpy(); wall = T.wall.to_numpy()
    R = {"days": len(days), "reached strike-days": len(T)}
    o = D.open; cw_in = (D.call_wall_prev > o) & (D.call_wall_prev <= o * (1 + MAXD)); pw_in = (D.put_wall_prev < o) & (D.put_wall_prev >= o * (1 - MAXD))
    R["coverage: walls within 3% that are $5 multiples"] = {"call": round(float((D.call_wall_prev[cw_in] % 5 == 0).mean()), 3), "put": round(float((D.put_wall_prev[pw_in] % 5 == 0).mean()), 3)}
    R["iter3 design: call wall stall"] = test(T, up, wall, "stall", S3, W, dix)
    R["iter3 design: put wall stall"] = test(T, dn, wall, "stall", S3, W, dix)
    if und == "SPY":
        okS = (T.sbin >= 0).to_numpy(); SA = ["side", "sbin", "vt", "round10"]
        R["A1 sigma bins x VIX tercile: call wall stall"] = test(T, up & okS, wall, "stall", SA, W, dix)
        R["A1 sigma bins x VIX tercile: put wall stall"] = test(T, dn & okS, wall, "stall", SA, W, dix)
        nh = ~((T.wall == 1) & (T["nearhist"] == 1)).to_numpy()
        R["A2i call wall stall, walls near prior highs dropped"] = test(T, up & nh, wall, "stall", S3, W, dix) | {"wall cases dropped": int(((T.wall == 1) & (T["nearhist"] == 1) & up).sum())}
        R["A2i put wall stall, walls near prior lows dropped"] = test(T, dn & nh, wall, "stall", S3, W, dix) | {"wall cases dropped": int(((T.wall == 1) & (T["nearhist"] == 1) & dn).sum())}
        nw = (T.wall == 0).to_numpy(); st = T.stale.to_numpy()
        R["A2ii stale call wall (t-10, not current) stall"] = test(T, up & nw, st, "stall", S3, W, dix)
        R["A2ii stale put wall stall"] = test(T, dn & nw, st, "stall", S3, W, dix)
        R["M2 pinning share after first touch: call wall"] = test(T, up, wall, "pin", S3, W, dix)
        R["M2 pinning share after first touch: put wall (descriptive)"] = test(T, dn, wall, "pin", S3, W, dix)
        for lab, msk in (("R1 2020-21", (T.day < "2022-01-01").to_numpy()), ("R2 2022+", (T.day >= "2022-01-01").to_numpy())):
            R[f"era {lab}: A1 call wall stall"] = {k: v for k, v in test(T, up & okS & msk, wall, "stall", SA, W, dix).items() if k in ("n treated", "MH diff", "90% CI")}
    sd = D.sig * D.open
    dc = (D.call_wall_prev - D.open) / sd; dp = (D.open - D.put_wall_prev) / sd
    R["B bunching: call wall, x=(high-wall)/sigma"] = bunch(((D.high - D.call_wall_prev) / sd)[dc.between(0.5, 3)].to_numpy())
    R["B bunching: put wall, x=(wall-low)/sigma"] = bunch(((D.put_wall_prev - D.low) / sd)[dp.between(0.5, 3)].to_numpy())
    for off in (-5, 5):   # descriptive roundness placebo: a $5 strike next to the wall
        L = D.call_wall_prev + off; dl = (L - D.open) / sd
        R[f"B placebo (descriptive): call wall {off:+d}"] = {k: v for k, v in bunch(((D.high - L) / sd)[dl.between(0.5, 3)].to_numpy()).items() if not k.startswith("_")}
    res[und] = R
    T.to_csv(HERE / "out" / f"walls_b_events_{und}.csv", index=False)
json.dump(res, open(HERE / "out" / "walls_b.json", "w"), indent=1)
print(json.dumps({u: {k: ({kk: vv for kk, vv in v.items() if kk != "_hist"} if isinstance(v, dict) else v) for k, v in R.items()} for u, R in res.items()}, indent=1))
