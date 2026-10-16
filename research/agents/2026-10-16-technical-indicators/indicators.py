"""Technical indicators on daily / weekly / monthly bars for TSLA and MSFT: alone (Part A) and added to the
microstructure setups (Part B), exactly as pre-registered in README.md (commit e91f147).
Reads data/{SYM}_1d.json (Yahoo, fetched once; --refetch to refresh). Writes out/part_a.csv, out/part_b.csv,
out/classic.csv, out/today.csv, out/results.json.
Usage: OMP_NUM_THREADS=1 python indicators.py
"""
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA, OUT = HERE / "data", HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
END = "2026-10-15"
ASSETS = ("TSLA", "MSFT")
TFS = {"daily": dict(rule=None, H=10, win=252, minp=120, sma=200, minshift=60, nshift=1000),
       "weekly": dict(rule="W-FRI", H=4, win=52, minp=26, sma=40, minshift=13, nshift=None),
       "monthly": dict(rule="ME", H=3, win=60, minp=36, sma=10, minshift=6, nshift=None)}
IND = ["RSI", "Momentum", "ATR%", "MACD", "%B", "Stochastic", "ADX", "Trend distance"]
STATS = ["S1 direction (mean R high - low)", "S2 entry (P(UP) high - low)", "S3 exit (P(DOWN) high - low)"]
ALPHA_A, ALPHA_B = 0.05 / 6, 0.05 / 12
RNG = np.random.default_rng(20261016)


# ---------- data ----------
def load(sym):
    path = DATA / f"{sym}_1d.json"
    if not path.exists() or "--refetch" in sys.argv:
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=0&period2=9999999999"
               "&interval=1d&includePrePost=false&events=div%2Csplit")
        DATA.mkdir(exist_ok=True)
        path.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
    d = json.loads(path.read_text())["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    df = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=idx)
    df["adj"] = d["indicators"]["adjclose"][0]["adjclose"]
    df = df.dropna()
    df = df[~df.index.duplicated(keep="last") & (df.index <= END)]
    f = df.adj / df.close                                   # dividend (and split) adjustment applied to the whole bar
    return pd.DataFrame({"open": df.open * f, "high": df.high * f, "low": df.low * f, "close": df.adj})


def bars(df, rule):
    if rule is None:
        return df
    g = df.groupby(df.index.to_period(rule[0]))
    b = pd.DataFrame({"open": g.open.first(), "high": g.high.max(), "low": g.low.min(), "close": g.close.last(),
                      "last_day": g.apply(lambda x: x.index.max())})
    b = b[b.index.to_timestamp(how="end").normalize() <= pd.Timestamp(END)]     # complete bars only
    return b.set_index("last_day")


# ---------- indicators ----------
def wilder(s, n=14):
    return s.ewm(alpha=1 / n, adjust=False).mean()


def indicators(b, sma):
    c, h, l = b.close, b.high, b.low
    d = c.diff()
    rsi = 100 - 100 / (1 + wilder(d.clip(lower=0)) / wilder(-d.clip(upper=0)))
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = wilder(tr)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = (macd - macd.ewm(span=9, adjust=False).mean()) / c
    m, sd = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
    pb = (c - (m - 2 * sd)) / (4 * sd)
    lo14, hi14 = l.rolling(14).min(), h.rolling(14).max()
    stoch = (100 * (c - lo14) / (hi14 - lo14)).rolling(3).mean()
    up, dn = h.diff(), -l.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index)
    ndm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index)
    pdi, ndi = 100 * wilder(pdm) / atr, 100 * wilder(ndm) / atr
    adx = wilder(100 * (pdi - ndi).abs() / (pdi + ndi))
    return pd.DataFrame({"RSI": rsi, "Momentum": c / c.shift(12) - 1, "ATR%": atr / c, "MACD": hist, "%B": pb,
                         "Stochastic": stoch, "ADX": adx, "Trend distance": c / c.rolling(sma).mean() - 1})


def frame(sym, tf):
    p = TFS[tf]
    b = bars(load(sym), p["rule"])
    raw = indicators(b, p["sma"])
    pct = raw.rolling(p["win"], min_periods=p["minp"]).rank(pct=True)
    lc = np.log(b.close)
    R = lc.shift(-p["H"]) - lc
    return b, raw, pct, R


# ---------- Part A ----------
def stats(hi, lo, R, up, dn):
    """hi, lo: (k, n) bool; R, up, dn: (n,). Returns (k, 3)."""
    nh, nl = hi.sum(1), lo.sum(1)
    out = np.empty((hi.shape[0], 3))
    for j, y in enumerate((R, up, dn)):
        out[:, j] = hi @ y / nh - lo @ y / nl
    return out


def offsets(n, p):
    allowed = np.arange(p["minshift"], n - p["minshift"] + 1)
    return RNG.choice(allowed, p["nshift"], replace=True) if p["nshift"] else allowed


def part_a(sym, tf):
    p = TFS[tf]
    b, raw, pct, R = frame(sym, tf)
    ok = pct.notna().all(axis=1) & R.notna()
    P, r = pct[ok].to_numpy().T, R[ok].to_numpy()
    up, dn = (r >= np.quantile(r, 0.8)).astype(float), (r <= np.quantile(r, 0.2)).astype(float)
    hi, lo = (P >= 2 / 3).astype(float), (P <= 1 / 3).astype(float)
    real = stats(hi, lo, r, up, dn)
    offs = offsets(len(r), p)
    null = np.stack([stats(np.roll(hi, o, axis=1), np.roll(lo, o, axis=1), r, up, dn) for o in offs])   # (N, k, 3)
    mu, sd = null.mean(0), null.std(0)
    z, zn = (real - mu) / sd, (null - mu) / sd
    flat_z, flat_zn = np.abs(z).ravel(), np.abs(zn).reshape(len(offs), -1)
    raw_p = ((flat_zn >= flat_z).sum(0) + 1) / (len(offs) + 1)
    order = np.argsort(-flat_z)                                  # Westfall-Young step-down maxT
    adj, running = np.empty_like(flat_z), 0.0
    for i, k in enumerate(order):
        mx = flat_zn[:, order[i:]].max(1)
        running = max(running, (np.sum(mx >= flat_z[k]) + 1) / (len(offs) + 1))
        adj[k] = running
    idx = R[ok].index
    era = {}
    for lab, m in (("early", idx < "2021-01-01"), ("2021+", idx >= "2021-01-01")):
        era[lab] = stats(hi[:, m], lo[:, m], r[m], up[m], dn[m])
    rows = []
    for i, ind in enumerate(IND):
        for j, st in enumerate(STATS):
            k = i * 3 + j
            rows.append({"asset": sym, "timeframe": tf, "indicator": ind, "statistic": st, "value": real[i, j], "z": z[i, j],
                         "p raw": raw_p[k], "p family (step-down)": adj[k], "early": era["early"][i, j], "2021+": era["2021+"][i, j],
                         "n bars": len(r), "n high": int(hi[i].sum()), "n low": int(lo[i].sum()), "null draws": len(offs),
                         "first": str(idx[0].date()), "last": str(idx[-1].date())})
    fam_p = (np.sum(flat_zn.max(1) >= flat_z.max()) + 1) / (len(offs) + 1)
    return pd.DataFrame(rows), fam_p, (b, pct, R, ok, up, dn, r, hi, lo, offs)


def classic(sym, tf, cache):
    b, pct, R, ok, up, dn, r, _, _, offs = cache
    raw = indicators(b, TFS[tf]["sma"])[ok]
    rows = []
    for ind, top, bot in (("RSI", 70, 30), ("Stochastic", 80, 20)):
        hi, lo = (raw[ind].to_numpy() > top)[None].astype(float), (raw[ind].to_numpy() < bot)[None].astype(float)
        real = stats(hi, lo, r, up, dn)[0]
        null = np.stack([stats(np.roll(hi, o, 1), np.roll(lo, o, 1), r, up, dn)[0] for o in offs])
        pr = ((np.abs(null - null.mean(0)) >= np.abs(real - null.mean(0))).sum(0) + 1) / (len(offs) + 1)
        for j, st in enumerate(STATS):
            rows.append({"asset": sym, "timeframe": tf, "rule": f"{ind} >{top} vs <{bot}", "statistic": st, "value": real[j], "p raw": pr[j],
                         "n high": int(hi.sum()), "n low": int(lo.sum())})
    return rows


# ---------- Part B ----------
def daily_aligned(sym, idx):
    """Daily RSI, daily ATR%, weekly momentum percentiles (plus every indicator x timeframe) aligned to daily dates,
    each value as known at that day's close (weekly/monthly = last completed bar)."""
    out = {}
    for tf in TFS:
        _, _, pct, _ = frame(sym, tf)
        for ind in IND:
            out[(tf, ind)] = pct[ind].reindex(pct.index.union(idx)).ffill().reindex(idx)
    return out


def setups():
    import os
    sys.path.insert(0, str(MICRO))
    here = os.getcwd()
    os.chdir(MICRO)                                     # the original scripts read some files by relative path
    try:
        return _setups()
    finally:
        os.chdir(here)


def _setups():
    from burst_gamma import state
    from common import load_bars
    from held_back import frame as hb_frame, outcomes as hb_outcomes
    from own_multiverse import within
    from stock_gamma import START, frame as sg_frame
    from stock_now import burst_days
    x = sg_frame("TSLA").join(state("TSLA")[["near_pct"]])
    x = x[(x.index >= START) & (x.index <= END)]
    c = load_bars("TSLA").close
    c = c[c.index <= END]
    nxt = lambda m, h: pd.Series(within(np.asarray(m, bool), h), index=c.index).reindex(x.index)
    tsla = pd.DataFrame({"setup": (x.near_pct <= 1 / 3) & x.below.astype(bool),
                         "up-burst within 3": nxt(burst_days(c, 1), 3), "down-burst within 3": nxt(burst_days(c, -1), 3)})
    X = hb_frame("MSFT")
    X = X[X.index <= END]
    Y = hb_outcomes(X)
    msft = pd.DataFrame({"setup": X.lead20.astype(bool) & (X.gex <= 1 / 3),
                         "up-leg within 10": Y[("up-leg", 10)], "down-leg within 10": Y[("down-leg", 10)]}, index=X.index)
    return {"TSLA": tsla, "MSFT": msft}


def episodes(m):
    m = np.asarray(m, bool)
    return int((m & ~np.r_[False, m[:-1]]).sum())


def part_b(survivors):
    S = setups()
    rows = []
    for sym, F in S.items():
        A = daily_aligned(sym, F.index)
        tests = [("fixed", ("daily", "RSI")), ("fixed", ("daily", "ATR%")), ("fixed", ("weekly", "Momentum"))]
        tests += [("Part A survivor", k) for k in survivors.get(sym, []) if ("fixed", k) not in tests]
        for kind, key in tests:
            v = A[key].to_numpy()
            for out in [c for c in F.columns if c != "setup"]:
                y = F[out].to_numpy(float)
                ok = F.setup.to_numpy() & np.isfinite(y)
                def stat(vv):
                    hi, lo = ok & (vv >= 2 / 3), ok & (vv <= 1 / 3)
                    return np.nanmean(y[hi]) - np.nanmean(y[lo]) if hi.sum() and lo.sum() else np.nan
                real = stat(v)
                allowed = np.arange(60, len(v) - 59)
                null = np.array([stat(np.roll(v, o)) for o in RNG.choice(allowed, 1000)])
                null = null[np.isfinite(null)]
                pv = (np.sum(np.abs(null) >= abs(real)) + 1) / (len(null) + 1) if np.isfinite(real) else np.nan   # empty cell: not testable
                hi, lo = ok & (v >= 2 / 3), ok & (v <= 1 / 3)
                rows.append({"asset": sym, "kind": kind, "indicator": f"{key[0]} {key[1]}", "outcome": out,
                             "setup days": int(ok.sum()), "setup episodes": episodes(F.setup.to_numpy() & np.isfinite(y)),
                             "P(out | setup)": float(np.nanmean(y[ok])), "P(out | setup & high)": float(np.nanmean(y[hi])) if hi.sum() else np.nan,
                             "P(out | setup & low)": float(np.nanmean(y[lo])) if lo.sum() else np.nan,
                             "high days / episodes": f"{int(hi.sum())} / {episodes(hi)}", "low days / episodes": f"{int(lo.sum())} / {episodes(lo)}",
                             "difference": real, "p": pv, "passes (p < 0.0042)": bool(kind == "fixed" and np.isfinite(pv) and pv < ALPHA_B),
                             "period": f"{F.index[ok][0].date()} .. {F.index[ok][-1].date()}" if ok.any() else ""})
    return pd.DataFrame(rows)


def today():
    rows = []
    for sym in ASSETS:
        for tf in TFS:
            b, raw, pct, _ = frame(sym, tf)
            for ind in IND:
                v = pct[ind].dropna()
                rows.append({"asset": sym, "timeframe": tf, "bar": str(v.index[-1].date()), "indicator": ind,
                             "value": float(raw[ind].loc[v.index[-1]]), "percentile": float(v.iloc[-1]),
                             "state": "high" if v.iloc[-1] >= 2 / 3 else ("low" if v.iloc[-1] <= 1 / 3 else "middle")})
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(exist_ok=True)
    A, fam, cl = [], {}, []
    for sym in ASSETS:
        for tf in TFS:
            t, fp, cache = part_a(sym, tf)
            A.append(t)
            fam[f"{sym} {tf}"] = fp
            cl += classic(sym, tf, cache)
            print(f"{sym} {tf}: n={t['n bars'].iloc[0]} ({t['first'].iloc[0]}..{t['last'].iloc[0]}), family p {fp:.4f}", flush=True)
    A = pd.concat(A, ignore_index=True)
    A["survivor"] = A["p family (step-down)"] < ALPHA_A
    A["robust"] = A.survivor & (np.sign(A.early) == np.sign(A["2021+"])) & (np.sign(A.early) == np.sign(A.value))
    survivors = {}
    for _, r in A[A.robust].iterrows():
        survivors.setdefault(r.asset, [])
        if (r.timeframe, r.indicator) not in survivors[r.asset]:
            survivors[r.asset].append((r.timeframe, r.indicator))
    B = part_b(survivors)
    T = today()
    A.to_csv(OUT / "part_a.csv", index=False)
    B.to_csv(OUT / "part_b.csv", index=False)
    pd.DataFrame(cl).to_csv(OUT / "classic.csv", index=False)
    T.to_csv(OUT / "today.csv", index=False)
    res = {"family p (single-step)": fam, "survivors": int(A.survivor.sum()), "robust survivors": int(A.robust.sum()),
           "robust list": A[A.robust][["asset", "timeframe", "indicator", "statistic", "value", "z", "p family (step-down)", "early", "2021+"]].to_dict("records"),
           "part B passes": int(B["passes (p < 0.0042)"].sum())}
    (OUT / "results.json").write_text(json.dumps(res, indent=1, default=float))
    return A, B, T, res


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    A, B, T, res = main()
    cols = ["asset", "timeframe", "indicator", "statistic", "value", "z", "p raw", "p family (step-down)", "early", "2021+", "survivor", "robust"]
    print("\nPart A, strongest 25 by |z|\n" + A.reindex(A.z.abs().sort_values(ascending=False).index)[cols].head(25).round(4).to_string(index=False))
    print("\nPart B\n" + B.drop(columns=["period"]).round(3).to_string(index=False))
    print(json.dumps({k: v for k, v in res.items() if k != "robust list"}, indent=1, default=float))
