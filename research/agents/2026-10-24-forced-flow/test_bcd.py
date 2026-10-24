"""Tests B, C, D (README.md, pre-registered at 852dfff).
B expiry release; C volatility-target window drop-out echo; D leverage as fuel.
Usage: python test_bcd.py <GSPC_max.json>  -> out/b.json, out/c.json, out/d.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
PANEL = HERE.parent / "2026-10-15-channel-reversion-macro" / "out" / "macro_monthly.csv"
sys.path.insert(0, str(MICRO))
from common import load_bars                       # noqa: E402  (original, imported unchanged)

END = pd.Timestamp("2026-10-14")
TICKERS = ["TSLA", "MSFT", "NVDA", "SPY", "QQQ", "MU"]
NPERM = 5000
RNG = np.random.default_rng(20261024)


def gspc(path):
    d = json.loads(Path(path).read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    c = pd.Series(d["indicators"]["quote"][0]["close"], index=idx).dropna()
    c = c[~c.index.duplicated(keep="last")].sort_index()
    return c[c.index <= END]


# ---------------- B ----------------
def monthly_expiries(idx):
    out = []
    for (y, m), _ in pd.Series(index=idx, dtype=float).groupby([idx.year, idx.month]):
        fr = pd.date_range(f"{y}-{m:02d}-01", periods=31, freq="D")
        fr = fr[(fr.month == m) & (fr.weekday == 4)]
        if len(fr) < 3:
            continue
        third = fr[2]
        cand = idx[idx <= third]
        if len(cand) and (third - cand[-1]).days <= 1:      # holiday Friday: the expiry is the Thursday before
            out.append(cand[-1])
    return out


def test_b():
    rows = []
    for sym in TICKERS:
        g = pd.read_csv(MICRO / "out" / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date")
        b = load_bars(sym)
        b = b[b.index <= END]
        a = np.log(b.close).diff().abs()
        for E in monthly_expiries(b.index[b.index >= g.index[0]]):
            i = b.index.get_loc(E)
            if i < 6 or i + 5 >= len(b):
                continue
            prev = b.index[i - 1]
            if prev not in g.index:
                continue
            before, after = a.iloc[i - 5:i].mean(), a.iloc[i + 1:i + 6].mean()
            rows.append({"sym": sym, "expiry": E, "x": float(g.loc[prev, "gamma_share_1d"]), "y": float(np.log(after / before)),
                         "x5": float(g.loc[prev, "gamma_share_5d"])})
    B = pd.DataFrame(rows).dropna()
    dm = lambda s: s - B.groupby("sym")[s.name].transform("mean")
    x, y = dm(B.x).to_numpy(), dm(B.y).to_numpy()
    sl = lambda xx: float((xx * y).sum() / (xx ** 2).sum())
    obs = sl(x)
    null = np.empty(NPERM)
    groups = [np.nonzero((B.sym == s).to_numpy())[0] for s in TICKERS]
    for k in range(NPERM):
        xx = x.copy()
        for gi in groups:
            xx[gi] = RNG.permutation(x[gi])
        null[k] = sl(xx)
    q = pd.qcut(B.x.rank(method="first"), 3, labels=["low", "mid", "high"])
    res = {"events": int(len(B)), "slope (within ticker)": obs, "p (one-sided, permutation)": float((null >= obs).mean()),
           "mean y by expiring-share third": {str(k): float(v) for k, v in B.y.groupby(q, observed=False).mean().items()},
           "mean expiring share by third": {str(k): float(v) for k, v in B.x.groupby(q, observed=False).mean().items()},
           "mean y all (vol change into the week after expiry, log)": float(B.y.mean()),
           "per ticker slope": {s: float(np.polyfit(B.x[B.sym == s], B.y[B.sym == s], 1)[0]) for s in TICKERS}}
    res["verdict"] = "pass" if (obs > 0 and res["p (one-sided, permutation)"] < 0.05) else "fail"
    B.to_csv(OUT / "b_events.csv", index=False)
    return res


# ---------------- C ----------------
def echo(c, window, eras):
    r = np.log(c).diff()
    a = r.abs().to_numpy()
    sd = r.rolling(20).std().shift(1).to_numpy()
    rv = r.to_numpy()
    lc = np.log(c.to_numpy())
    rows = []
    n = len(a)
    for s in range(21, n - window - 4):
        if not np.isfinite(sd[s]) or a[s] < 2.5 * sd[s]:
            continue
        if a[s] <= a[s + 1:s + window].max():                 # the shock must be the largest move until it leaves the window
            continue
        e0 = s + window - 1                                    # close of the last session with the shock still inside the window
        rows.append({"date": c.index[s], "shock": float(rv[s]), "echo3": float(lc[e0 + 3] - lc[e0])})
    E = pd.DataFrame(rows).set_index("date")
    base3 = pd.Series(lc[3:] - lc[:-3], index=c.index[:-3])
    out = {}
    for lab, (a0, a1) in eras.items():
        m = (E.index >= a0) & (E.index <= a1)
        bm = (base3.index >= a0) & (base3.index <= a1)
        ex = E.echo3[m] - base3[bm].mean()
        bs = np.array([RNG.choice(ex.to_numpy(), len(ex)).mean() for _ in range(NPERM)]) if len(ex) > 2 else np.array([np.nan])
        out[lab] = {"events": int(m.sum()), "excess 3-session return %": float(100 * ex.mean()), "share positive": float((ex > 0).mean()),
                    "p (one-sided, bootstrap: excess <= 0)": float((bs <= 0).mean()), "_boot": bs}
    return out, E


def test_c(c):
    eras = {"1960-2007": ("1960-01-01", "2007-12-31"), "2008-2026": ("2008-01-01", "2026-12-31")}
    res = {}
    for w in (21, 63):
        o, E = echo(c, w, eras)
        post, pre = o["2008-2026"], o["1960-2007"]
        diff = post["_boot"] - RNG.choice(pre["_boot"], len(post["_boot"]))
        res[f"{w}-session echo"] = {k: {kk: vv for kk, vv in v.items() if kk != "_boot"} for k, v in o.items()}
        res[f"{w}-session echo"]["post minus pre %"] = float(100 * (post["_boot"].mean() - pre["_boot"].mean()))
        res[f"{w}-session echo"]["p (post <= pre)"] = float((diff <= 0).mean())
        E.to_csv(OUT / f"c_events_{w}.csv")
    p = res["21-session echo"]
    res["verdict (21-session, pre-registered)"] = "pass" if (p["2008-2026"]["excess 3-session return %"] > 0 and
                                                           p["2008-2026"]["p (one-sided, bootstrap: excess <= 0)"] < 0.05 and
                                                           p["post minus pre %"] > 0) else "fail"
    return res


# ---------------- D ----------------
def test_d(c):
    v = load_bars("^VIX").close
    v = v[v.index <= END]
    p = pd.read_csv(PANEL, parse_dates=["month"]).set_index("month").margin_yoy.dropna()
    lev = lambda d: p[p.index <= (d - pd.offsets.MonthEnd(2))].iloc[-1] if (p.index <= (d - pd.offsets.MonthEnd(2))).any() else np.nan
    cc = c.reindex(v.index).ffill()
    jump = v / v.shift(5) - 1
    rows, last = [], None
    idx = v.index
    for i in range(5, len(idx) - 21):
        d = idx[i]
        if d < pd.Timestamp("1998-04-01") or jump.iloc[i] < 0.40:
            continue
        if last is not None and i - last < 40:
            continue
        last = i
        seg = cc.iloc[i + 1:i + 21].to_numpy()
        rows.append({"date": d, "vix": float(v.iloc[i]), "vix 5d change %": float(100 * jump.iloc[i]), "margin yoy %": float(lev(d)),
                     "max drawdown 20d %": float(100 * (seg.min() / cc.iloc[i] - 1)), "return 20d %": float(100 * (seg[-1] / cc.iloc[i] - 1))})
    Dv = pd.DataFrame(rows).set_index("date").dropna()
    x, y = Dv["margin yoy %"].to_numpy(), Dv["max drawdown 20d %"].to_numpy()
    sl = lambda xx: float(np.polyfit(xx, y, 1)[0])
    obs = sl(x)
    null = np.array([sl(RNG.permutation(x)) for _ in range(NPERM)])
    hi = x >= np.median(x)
    res = {"events": int(len(Dv)), "slope of drawdown on margin yoy (pts per 1pt)": obs, "p (one-sided, permutation: slope >= 0)": float((null <= obs).mean()),
           "corr": float(np.corrcoef(x, y)[0, 1]),
           "mean drawdown, high-leverage half %": float(y[hi].mean()), "mean drawdown, low-leverage half %": float(y[~hi].mean()),
           "mean 20d return, high half %": float(Dv["return 20d %"][hi].mean()), "mean 20d return, low half %": float(Dv["return 20d %"][~hi].mean())}
    # control: all days, next 20-session return by lagged leverage half
    days = cc[cc.index >= "1998-04-01"]
    f20 = (days.shift(-20) / days - 1).dropna() * 100
    L = pd.Series([lev(d) for d in f20.index], index=f20.index)
    hiL = L >= L.median()
    res["control: all days next 20d return %, high vs low leverage half"] = [float(f20[hiL].mean()), float(f20[~hiL].mean())]
    m = f20.index.to_period("M")
    mon = pd.DataFrame({"r": f20, "h": hiL}).groupby(m).agg({"r": "mean", "h": "first"})
    diffs = []
    for _ in range(2000):
        s = mon.sample(len(mon), replace=True, random_state=int(RNG.integers(1e9)))
        diffs.append(s.r[s.h].mean() - s.r[~s.h].mean())
    res["control p (two-sided, month bootstrap)"] = float(2 * min((np.array(diffs) <= 0).mean(), (np.array(diffs) >= 0).mean()))
    res["verdict"] = "pass" if (obs < 0 and res["p (one-sided, permutation: slope >= 0)"] < 0.05) else "fail"
    Dv.round(3).to_csv(OUT / "d_events.csv")
    return res


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    c = gspc(sys.argv[1])
    for name, fn in (("b", test_b), ("c", lambda: test_c(c)), ("d", lambda: test_d(c))):
        r = fn()
        (OUT / f"{name}.json").write_text(json.dumps(r, indent=1, default=float))
        print(name.upper(), json.dumps(r, indent=1, default=float))
