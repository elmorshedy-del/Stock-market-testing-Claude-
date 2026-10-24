"""Test A (README.md, pre-registered at 852dfff): dealer sign flip and size law.
A1 daily: slope of the next-day return on today's return, by quintile of H = dealer gamma / 20-day dollar volume.
A2 intraday: slope of SPY's last-half-hour return on its return from the prior close to 15:30, by SPY's own H.
Usage: OMP_NUM_THREADS=1 python test_a.py [--a2]  -> out/a1.json, out/a2.json, out/a2_days.csv
A2 reads the private SPY 1-minute option files (Market_Data minute/ or the multiday agent's data/min)."""
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
MULTI = HERE.parent / "2026-10-16-spy-intraday-multiday"
sys.path.insert(0, str(MICRO))
from common import DATA, load_bars                 # noqa: E402  (original, imported unchanged)

END = pd.Timestamp("2026-10-14")
TICKERS = ["TSLA", "MSFT", "NVDA", "SPY", "QQQ", "MU"]
NBOOT, BLOCK = 2000, 20
RNG = np.random.default_rng(20261024)


def pct(s, n=252, minp=120):
    return s.rolling(n, min_periods=minp).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)


def slope(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    xc = x - x.mean()
    return float((xc * (y - y.mean())).sum() / (xc ** 2).sum())


def quintile_betas(D, xcol="x", ycol="y", qcol="q"):
    return [slope(D[xcol][D[qcol] == k], D[ycol][D[qcol] == k]) for k in range(5)]


def block_boot(D, stat, groups=None):
    """Moving-block bootstrap over consecutive rows (within each group if given)."""
    out = np.empty(NBOOT)
    parts = [D] if groups is None else [g for _, g in D.groupby(groups)]
    for b in range(NBOOT):
        pieces = []
        for g in parts:
            n = len(g)
            starts = RNG.integers(0, n - BLOCK, int(np.ceil(n / BLOCK)))
            idx = np.concatenate([np.arange(s, s + BLOCK) for s in starts])[:n]
            pieces.append(g.iloc[idx])
        out[b] = stat(pd.concat(pieces))
    return out


def spearman(v):
    r = pd.Series(v).rank().to_numpy()
    return float(np.corrcoef(r, np.arange(len(v)))[0, 1])


def a1_sp():
    g = pd.read_csv(DATA / "DIX.csv", parse_dates=["date"]).set_index("date")
    spy = load_bars("SPY")
    spx = load_bars("^GSPC").close
    dv = (spy.close * spy.volume).rolling(20).mean()
    D = pd.DataFrame({"gex": g.gex}).join(dv.rename("dv"), how="inner")
    D["H"] = D.gex / D.dv
    D["p"] = pct(D.H)
    r = np.log(spx).diff()
    D["x"], D["y"] = r.reindex(D.index), r.shift(-1).reindex(D.index)
    D = D[(D.index <= END)].dropna()
    D["q"] = np.minimum((D.p * 5).astype(int), 4)
    return D


def a1_names():
    rows = []
    for sym in TICKERS:
        g = pd.read_csv(MICRO / "out" / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date")
        b = load_bars(sym)
        b = b[b.index <= END]
        dv = (b.close * b.volume).rolling(20).mean()
        r = np.log(b.close).diff()
        sd = r.rolling(20).std()
        D = pd.DataFrame({"H": g.gex_classic / dv.reindex(g.index)})
        D["p"] = pct(D.H)
        D["x"] = (r / sd).reindex(D.index)                       # z-returns: pooled names are not dominated by TSLA's size
        D["y"] = (r.shift(-1) / sd).reindex(D.index)              # tomorrow scaled by today's known volatility
        D["sym"] = sym
        rows.append(D.dropna())
    D = pd.concat(rows)
    D["q"] = np.minimum((D.p * 5).astype(int), 4)
    return D


def summarize(D, groups=None):
    b = quintile_betas(D)
    diff = b[0] - b[4]
    bs = block_boot(D, lambda X: (lambda bb: bb[0] - bb[4])(quintile_betas(X)), groups)
    return {"days": int(len(D)), "beta by quintile (Q1 low gamma .. Q5 high)": [round(v, 4) for v in b],
            "Q1 - Q5": diff, "p (one-sided, block bootstrap)": float((bs <= 0).mean()),
            "ci95": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))], "spearman(beta, quintile)": spearman(b),
            "days per quintile": [int((D.q == k).sum()) for k in range(5)]}


def a1():
    S = a1_sp()
    res = {"S&P (SqueezeMetrics GEX / SPY dollar volume), 2011-2026": summarize(S)}
    r = res["S&P (SqueezeMetrics GEX / SPY dollar volume), 2011-2026"]
    r["verdict"] = "pass" if (r["p (one-sided, block bootstrap)"] < 0.05 and r["spearman(beta, quintile)"] < -0.7) else "fail"
    for lab, m in (("2011-2018", S.index < "2019-01-01"), ("2019-2026", S.index >= "2019-01-01")):
        res[f"S&P {lab}"] = {k: v for k, v in summarize(S[m]).items() if k != "ci95"}
    N = a1_names()
    res["6 names pooled (own gamma / own dollar volume, z-returns), 2020-2026"] = summarize(N, "sym")
    for sym in TICKERS:
        x = N[N.sym == sym]
        res[f"name {sym}"] = {"beta by quintile": [round(v, 3) for v in quintile_betas(x)], "Q1 - Q5": quintile_betas(x)[0] - quintile_betas(x)[4]}
    (OUT / "a1.json").write_text(json.dumps(res, indent=1))
    S.to_csv(OUT / "a1_sp_days.csv")
    return res


# ---------------- A2: intraday ----------------
def _day(args):
    path, s0 = args
    sys.path.insert(0, str(MULTI))
    import multiday as M                           # parity spot and loaders from the multiday agent (imported unchanged)
    M.MIN = path.parent
    try:
        piv, strikes, call, cols = M.load_day(pd.Timestamp(path.name[:8]))
    except Exception:
        return None
    bid, ask = piv["bid"].to_numpy(), piv["ask"].to_numpy()
    ok = (bid > 0) & (ask > 0)
    mid = np.where(ok, (bid + ask) / 2, np.nan)
    if np.isfinite(mid[350:]).sum() < 50:          # early close or missing afternoon quotes
        return None
    S = M.parity_spot(mid, strikes, call, s0)
    i1530, iend = M.MINUTES.index("15:30"), M.MINUTES.index("15:59")
    return {"date": pd.Timestamp(path.name[:8]), "open": float(S[0]), "s1530": float(S[i1530]), "close": float(S[iend])}


def a2_days():
    src = Path("/home/user/spy-options-data/minute")
    if not src.exists():
        src = MULTI / "data" / "min"
    files = sorted(src.glob("*.csv.gz"))
    spy = load_bars("SPY").close
    args = []
    for f in files:
        d = pd.Timestamp(f.name[:8])
        prev = spy[spy.index < d]
        args.append((f, float(prev.iloc[-1]) if len(prev) else np.nan))
    with Pool(4) as p:
        rows = [r for r in p.map(_day, args, chunksize=8) if r]
    return pd.DataFrame(rows).set_index("date").sort_index()


def a2():
    D = a2_days()
    D.to_csv(OUT / "a2_days.csv")
    D["prev_close"] = D.close.shift(1)
    D = D[D.index.to_series().diff().dt.days.fillna(1) <= 4]  # consecutive sessions only (prior close from the same source)
    D["x"] = np.log(D.s1530 / D.prev_close)
    D["y"] = np.log(D.close / D.s1530)
    g = pd.read_csv(MICRO / "out" / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")
    spy = load_bars("SPY")
    dv = (spy.close * spy.volume).rolling(20).mean()
    H = (g.gex_classic / dv.reindex(g.index))
    hp = pct(H).shift(1)                                       # the map known before the session: previous close
    sm = pd.read_csv(DATA / "DIX.csv", parse_dates=["date"]).set_index("date")
    sq = pct(sm.gex / dv.reindex(sm.index)).shift(1)
    D["p"], D["sign"], D["p_sq"] = hp.reindex(D.index), np.sign(g.gex_classic.shift(1)).reindex(D.index), sq.reindex(D.index)
    D = D.dropna(subset=["x", "y", "p"])
    D = D[D.index <= END]
    D["q"] = np.minimum((D.p * 5).astype(int), 4)
    half = lambda X: slope(X.x[X.p < 0.5], X.y[X.p < 0.5]) - slope(X.x[X.p >= 0.5], X.y[X.p >= 0.5])
    bs = block_boot(D, half)
    res = {"days": int(len(D)), "slope all days": slope(D.x, D.y),
           "slope low-H half": slope(D.x[D.p < 0.5], D.y[D.p < 0.5]), "slope high-H half": slope(D.x[D.p >= 0.5], D.y[D.p >= 0.5]),
           "low - high": half(D), "p (one-sided, block bootstrap)": float((bs <= 0).mean()),
           "slope by quintile": [round(v, 4) for v in quintile_betas(D)],
           "slope when SPY gex_classic < 0": slope(D.x[D.sign < 0], D.y[D.sign < 0]), "days gex<0": int((D.sign < 0).sum()),
           "slope when SPY gex_classic > 0": slope(D.x[D.sign > 0], D.y[D.sign > 0]), "days gex>0": int((D.sign > 0).sum())}
    Dq = D.dropna(subset=["p_sq"])
    res["by SqueezeMetrics S&P gamma: slope low half / high half"] = [slope(Dq.x[Dq.p_sq < 0.5], Dq.y[Dq.p_sq < 0.5]),
                                                                       slope(Dq.x[Dq.p_sq >= 0.5], Dq.y[Dq.p_sq >= 0.5])]
    res["verdict"] = "pass" if (res["low - high"] > 0 and res["p (one-sided, block bootstrap)"] < 0.05) else "fail"
    (OUT / "a2.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    if "--a2" in sys.argv:
        print(json.dumps(a2(), indent=1))
    else:
        print(json.dumps(a1(), indent=1))
