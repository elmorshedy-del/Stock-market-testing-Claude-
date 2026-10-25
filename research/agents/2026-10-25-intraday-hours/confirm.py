"""Part B confirmations (pre-registered at 6b78abc) on the HELD-OUT 365 sessions: F1-F5, Holm-corrected.
Usage: python confirm.py <hourly folder>  -> out/confirm.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import explore as X
import segments as G

NB = 4000
RNG = np.random.default_rng(20261102)
SEMIS = ["NVDA", "AVGO", "AMD", "MU", "AMAT", "QCOM", "TXN", "INTC", "SMH"]


def main(folder):
    syms = sorted(p.name.split("_")[0] for p in Path(folder).glob("*_60m.json"))
    explore, held = X.split_days(folder)
    stocks = [s for s in syms if s not in ("SPY", "QQQ", "SMH", "IWM", "RSP", "XLK")]
    full = {s: G.segments(folder, s) for s in syms}
    P = {s: full[s].reindex(held) for s in syms}
    E = {s: full[s].reindex(explore) for s in syms}
    n = len(held)
    res = {"held-out sessions": n, "dates": [str(held[0].date()), str(held[-1].date())]}
    bsets = [G.blocks(RNG, n) for _ in range(NB)]
    # F1
    def f1(ii):
        xs, ys = [], []
        for s in stocks:
            x, y = P[s]["first"].to_numpy()[ii], P[s]["last"].to_numpy()[ii]
            m = np.isfinite(x) & np.isfinite(y)
            xs.append(x[m] - x[m].mean()); ys.append(y[m] - y[m].mean())
        x, y = np.concatenate(xs), np.concatenate(ys)
        return (x * y).sum() / (x ** 2).sum()
    o = f1(np.arange(n)); b = np.array([f1(ii) for ii in bsets])
    res["F1 first hour -> last half hour, pooled stocks"] = {"slope": float(o), "p (one-sided)": float((b <= 0).mean()),
                                                            "SPY": G.slope(P["SPY"]["first"].to_numpy(), P["SPY"]["last"].to_numpy()),
                                                            "QQQ": G.slope(P["QQQ"]["first"].to_numpy(), P["QQQ"]["last"].to_numpy())}
    # F2
    me = X.cal_flags(held)["month end"]
    L = np.nanmean(np.array([P[s]["last"].to_numpy() for s in stocks]), axis=0)
    v = L[me]
    bb = np.array([RNG.choice(v, len(v)).mean() for _ in range(NB)])
    Ls = P["SPY"]["last"].to_numpy()
    res["F2 month-end last half hour, stock average"] = {"days": int(me.sum()), "mean bp": float(1e4 * v.mean()), "p (one-sided)": float((bb <= 0).mean()),
                                                         "SPY mean bp": float(1e4 * np.nanmean(Ls[me])), "all days stock mean bp": float(1e4 * np.nanmean(L))}
    # F3
    x, y = P["AAPL"]["on"].to_numpy(), P["AAPL"]["last"].to_numpy()
    o = G.slope(x, y); b = np.array([G.slope(x[ii], y[ii]) for ii in bsets])
    res["F3 AAPL overnight -> last half hour"] = {"slope": o, "p (one-sided)": float((b >= 0).mean())}
    # F4
    sig = lambda F, s: float(np.nanmean(F[s]["first"] - F[s]["on"]))
    a = np.array([sig(E, s) for s in syms]); h = np.array([sig(P, s) for s in syms])
    rk = lambda z: pd.Series(z).rank().to_numpy()
    rho = np.corrcoef(rk(a), rk(h))[0, 1]
    null = np.array([np.corrcoef(rk(a), rk(RNG.permutation(h)))[0, 1] for _ in range(10000)])
    res["F4 persistence of (first hour - overnight) across 51 tickers"] = {
        "spearman exploration vs held-out": float(rho), "p (one-sided, permutation)": float((null >= rho).mean()),
        "held-out top 6 (bp/day)": sorted(zip(syms, (1e4 * h).round(1)), key=lambda kv: -kv[1])[:6],
        "held-out bottom 6 (bp/day)": sorted(zip(syms, (1e4 * h).round(1)), key=lambda kv: kv[1])[:6],
        "AAPL rank held-out (1 = highest)": int(pd.Series(h, index=syms).rank(ascending=False)["AAPL"])}
    # F5
    rest = [s for s in syms if s not in SEMIS]
    M = {s: (P[s]["first"] - P[s]["on"]).to_numpy() for s in syms}
    f5 = lambda ii: np.nanmean([np.nanmean(M[s][ii]) for s in SEMIS]) - np.nanmean([np.nanmean(M[s][ii]) for s in rest])
    o = f5(np.arange(n)); b = np.array([f5(ii) for ii in bsets])
    res["F5 semis minus rest, (first hour - overnight)"] = {"difference bp/day": float(1e4 * o), "p (one-sided)": float((b >= 0).mean()),
                                                           "exploration difference bp/day": float(1e4 * (np.mean([sig(E, s) for s in SEMIS]) - np.mean([sig(E, s) for s in rest])))}
    keys = [k for k in res if k.startswith("F")]
    ps = np.array([res[k]["p (one-sided)"] if "p (one-sided)" in res[k] else res[k]["p (one-sided, permutation)"] for k in keys])
    order = np.argsort(ps)
    holm = np.empty(len(ps))
    running = 0
    for rank, i in enumerate(order):
        running = max(running, min(1, (len(ps) - rank) * ps[i]))
        holm[i] = running
    sign_ok = {keys[0]: res[keys[0]]["slope"] > 0, keys[1]: res[keys[1]]["mean bp"] > 0, keys[2]: res[keys[2]]["slope"] < 0,
               keys[3]: res[keys[3]]["spearman exploration vs held-out"] > 0, keys[4]: res[keys[4]]["difference bp/day"] < 0}
    res["confirmations"] = {k: {"raw p": float(ps[i]), "Holm p": float(holm[i]), "confirmed": bool(sign_ok[k] and holm[i] < 0.05)} for i, k in enumerate(keys)}
    (G.OUT / "confirm.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=float))
