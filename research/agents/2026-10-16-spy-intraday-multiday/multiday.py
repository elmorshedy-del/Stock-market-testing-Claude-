"""Multi-day SPY test (design in README.md, pre-registered at cff84a9).
FL: does 0DTE signed flow lead SPY's next 5 minutes?  LG: do intraday turns land on live dealer-gamma strikes?
Usage: OMP_NUM_THREADS=1 python multiday.py [--days N] -> out/fl.json, out/lg.json, out/days.csv, out/multiday.png"""
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
OUT, MIN = HERE / "out", HERE / "data" / "min"
MICRO = HERE.parents[1] / "microstructure"
sys.path.insert(0, str(MICRO))
os.chdir(MICRO)
import td_gamma as t                               # noqa: E402  (original, imported unchanged)

YEAR = 365 * 24 * 60                               # minutes per year
BAND, NLEV, NSIM, MINSHIFT, COST, TOUCH, HALF, NBOOT = 0.015, 3, 1000, 6, 0.3, 0.10, 0.50, 2000
START, END = pd.Timestamp("2023-01-03"), pd.Timestamp("2026-10-15")
MINUTES = [f"{h:02d}:{m:02d}" for h in range(9, 16) for m in range(60) if (h, m) >= (9, 30)]


def gamma(S, K, T, iv):
    sq = np.sqrt(T)
    d1 = (np.log(S / K) + 0.5 * iv * iv * T) / (iv * sq)
    return norm.pdf(d1) / (S * iv * sq)


def bs_delta(S, K, T, iv, call):
    d1 = (np.log(S / K) + 0.5 * iv * iv * T) / (iv * np.sqrt(T))
    return np.where(call, norm.cdf(d1), norm.cdf(d1) - 1)


def roundness(k):
    return np.where(np.isclose(k % 10, 0), 2, np.where(np.isclose(k % 5, 0), 1, 0))


def load_day(day):
    m = pd.read_csv(MIN / f"{day:%Y%m%d}.csv.gz")
    m = m[m.ts.isin(MINUTES)]
    m["c"] = m.strike.astype(float).round(2).astype(str) + m.right
    cols = sorted(m.c.unique())
    piv = {k: m.pivot_table(index="ts", columns="c", values=k, aggfunc="last").reindex(index=MINUTES, columns=cols)
           for k in ("volume", "vwap", "bid", "ask")}
    strikes = np.array([float(c[:-1]) for c in cols])
    call = np.array([c.endswith("C") for c in cols])
    return piv, strikes, call, cols


def parity_spot(mid, strikes, call, s0):
    S = np.full(len(MINUTES), np.nan)
    prev, first = s0, None
    for i in range(len(MINUTES)):
        c = pd.Series(mid[i, call], index=strikes[call])
        p = pd.Series(mid[i, ~call], index=strikes[~call])
        both = (c - p).dropna()
        if len(both):
            k = both.index[np.argsort(np.abs(both.index - prev))[:3]]
            prev = float(np.median(k + both[k].to_numpy()))
            first = i if first is None else first
            S[i] = prev
    if first is None:
        return S
    S[:first] = S[first]                       # minutes before the first quote take the first parity value (no overnight gap)
    return pd.Series(S).ffill().to_numpy()


def day_work(args):
    day, eod_prev, oi_day = args
    try:
        piv, strikes, call, cols = load_day(day)
    except FileNotFoundError:
        return None
    bid, ask = piv["bid"].to_numpy(), piv["ask"].to_numpy()
    ok = (bid > 0) & (ask > 0)
    mid = np.where(ok, (bid + ask) / 2, np.nan)
    half = np.where(ok, (ask - bid) / 2, np.nan)
    if np.isfinite(mid[200:]).sum() < 100:         # early close or missing data
        return None
    # morning map: prior day's EOD chain (IVs) with today's OI (positions at the prior close)
    key = ["expiration", "strike", "cp"]
    g = eod_prev.merge(oi_day[key + ["oi"]], on=key, how="left").fillna({"oi": 0})
    g = t.chain_day(g)
    s0 = float(g.underlying_close.iloc[0])
    S = parity_spot(mid, strikes, call, s0)
    # signed flow
    vol, vwap = piv["volume"].to_numpy(), piv["vwap"].to_numpy()
    mid_avg = np.nanmean(np.stack([mid, np.vstack([mid[1:], mid[-1:]])]), axis=0)
    half_avg = np.nanmean(np.stack([half, np.vstack([half[1:], half[-1:]])]), axis=0)
    s = np.clip((vwap - mid_avg) / half_avg, -1, 1)
    s = np.where((vol > 0) & np.isfinite(s) & (half_avg > 0), s, 0.0)
    Tm = np.array([(390 - i - 1) / YEAR for i in range(390)]).clip(min=1 / YEAR)
    Smat = np.repeat(S[:, None], len(cols), axis=1)
    Kmat = np.repeat(strikes[None, :], 390, axis=0)
    Tmat = np.repeat(Tm[:, None], len(cols), axis=1)
    Cmat = np.repeat(call[None, :], 390, axis=0)
    has = np.isfinite(mid) & (mid > 0)
    ivm = np.full(mid.shape, np.nan)
    if has.any():
        ivm[has] = t.implied_vol(mid[has], Smat[has], Kmat[has], Tmat[has], Cmat[has])
    delta = np.where(np.isfinite(ivm), bs_delta(Smat, Kmat, Tmat, np.where(np.isfinite(ivm), ivm, 0.2), Cmat), 0.0)
    sv = s * np.nan_to_num(vol)                    # customer signed contracts per minute
    flow = (sv * delta * 100).sum(axis=1)
    cum_sv = np.cumsum(sv, axis=0)
    # static map restricted to the strikes and expiries that matter intraday
    g = g[(g.K >= s0 * (1 - 0.04)) & (g.K <= s0 * (1 + 0.04)) & ((g.expiration - pd.Timestamp(day)).dt.days <= 45)].copy()
    g["sign"] = np.where(g.cp == "C", 1.0, -1.0)
    g["pos"] = g.sign * g.oi
    g["is0"] = g.expiration.dt.date == day
    g["c"] = g.K.round(2).astype(str) + g.cp
    ci = {c: j for j, c in enumerate(cols)}
    g["j"] = g.c.map(ci).fillna(-1).astype(int)
    g["days_out"] = (g.expiration - pd.Timestamp(day)).dt.days
    def gex_by_strike(i, live):
        Si = S[i]
        T = np.where(g.is0, Tm[i], (g.days_out * 1440 + (390 - i)) / YEAR)
        iv = g.iv.to_numpy().copy()
        pos = g.pos.to_numpy().copy()
        j = g.j.to_numpy()
        z = g.is0.to_numpy() & (j >= 0)
        if live:
            iv[z] = np.where(np.isfinite(ivm[i, j[z]]), ivm[i, j[z]], iv[z])
            pos[z] = pos[z] - cum_sv[i, j[z]]
        gx = pos * gamma(Si, g.K.to_numpy(), T, iv) * 100 * Si * Si * 0.01
        return pd.Series(gx, index=g.K.to_numpy()).groupby(level=0).sum()
    day_gex = float(gex_by_strike(0, live=False).sum())
    # live and static maps at every minute (levels used at minute m come from minute m-1)
    levels = {}
    for v in ("live", "static"):
        pos_l, neg_l = [], []
        for i in range(390):
            gx = gex_by_strike(i, live=(v == "live"))
            gx = gx[(gx.index >= S[i] * (1 - BAND)) & (gx.index <= S[i] * (1 + BAND))]
            pos_l.append(set(gx[gx > 0].nlargest(NLEV).index))
            neg_l.append(set(gx[gx < 0].nsmallest(NLEV).index))
        levels[v] = (pos_l, neg_l)
    grid = np.arange(np.floor(S.min() * (1 - BAND)), np.ceil(S.max() * (1 + BAND)) + 1)
    rows = []
    for X in grid:
        busy_until = -1
        dX = S - X
        for m in range(1, 389):
            if m <= busy_until:
                continue
            side = np.sign(dX[m - 1])
            if side == 0 or not (np.sign(dX[m]) != side or abs(dX[m]) <= TOUCH):
                continue
            w = dX[m + 1:m + 31] * side
            rej, brk = np.where(w >= HALF)[0], np.where(w <= -HALF)[0]
            if not len(rej) and not len(brk):
                busy_until = m + 30
                continue
            r0 = rej[0] if len(rej) else 99
            b0 = brk[0] if len(brk) else 99
            busy_until = m + 1 + min(r0, b0)
            rows.append((X, int(roundness(np.array([X]))[0]), m, int(r0 < b0),
                         X in levels["live"][0][m - 1], X in levels["live"][1][m - 1],
                         X in levels["static"][0][m - 1], X in levels["static"][1][m - 1]))
    touches = rows
    # 5-minute buckets for FL
    fb = flow.reshape(78, 5).sum(axis=1)
    Se = S.reshape(78, 5)[:, -1]
    ret = 1e4 * np.diff(np.log(np.r_[S[0], Se]))
    return {"day": str(day), "type": "long" if day_gex > 0 else "short", "gex_open": day_gex, "touches": touches,
            "flow": fb.tolist(), "ret": ret.tolist(), "s0": s0, "S_first": float(S[0])}


def inputs(days):
    eod = t.read("SPY", "eod")
    eod = eod[eod.date >= START - pd.Timedelta(days=10)]
    eod["mid"] = (eod.bid + eod.ask) / 2
    oi = t.read("SPY", "oi")
    oi = oi[oi.date >= START - pd.Timedelta(days=10)]
    oic = next(c for c in oi.columns if "open_interest" in c)
    oi = oi.rename(columns={oic: "oi"})
    edates = np.array(sorted(eod.date.unique()))
    E, O = dict(tuple(eod.groupby("date"))), dict(tuple(oi.groupby("date")))
    out = []
    for d in days:
        ts = pd.Timestamp(d)
        prev = edates[edates < np.datetime64(ts)]
        if not len(prev) or ts not in O:
            continue
        out.append((d, E[pd.Timestamp(prev[-1])], O[ts]))
    return out


def fl_test(R):
    rows = []
    for k, r in enumerate(R):
        f, y = np.array(r["flow"]), np.array(r["ret"])
        if f.std() == 0:
            continue
        rows.append((k, (f - f.mean()) / f.std(), y, r["type"], r["day"][:4]))
    def beta(zs):
        X, Y = [], []
        for z, (_, _, y, _, _) in zip(zs, rows):
            X.append(np.column_stack([np.ones(77), z[:-1], y[:-1]]))
            Y.append(y[1:])
        X, Y = np.vstack(X), np.concatenate(Y)
        return np.linalg.lstsq(X, Y, rcond=None)[0][1]
    def subset(pred):
        sel = [r for r in rows if pred(r)]
        return sel
    res = {}
    rng = np.random.default_rng(20261016)
    for lab, pred in (("all days", lambda r: True), ("long-gamma days", lambda r: r[3] == "long"), ("short-gamma days", lambda r: r[3] == "short"),
                      ("2023", lambda r: r[4] == "2023"), ("2024", lambda r: r[4] == "2024"), ("2025", lambda r: r[4] == "2025"), ("2026", lambda r: r[4] == "2026")):
        sel = subset(pred)
        if len(sel) < 5:
            continue
        nonlocal_rows = sel
        X = lambda zs: np.vstack([np.column_stack([np.ones(77), z[:-1], r[2][:-1]]) for z, r in zip(zs, nonlocal_rows)])
        Y = np.concatenate([r[2][1:] for r in nonlocal_rows])
        b = np.linalg.lstsq(X([r[1] for r in sel]), Y, rcond=None)[0][1]
        nb = 300 if lab != "all days" else NSIM
        null = np.array([np.linalg.lstsq(X([np.roll(r[1], rng.integers(MINSHIFT, 78 - MINSHIFT)) for r in sel]), Y, rcond=None)[0][1] for _ in range(nb)])
        sig = np.concatenate([np.sign(r[1][:-1]) for r in sel])
        zz = np.concatenate([np.abs(r[1][:-1]) for r in sel])
        gross = sig * Y
        top = zz >= np.quantile(zz, 0.8)
        res[lab] = {"days": len(sel), "beta_bp_per_sd": float(b), "p": float((null >= b).mean()), "null_draws": nb,
                    "sign strategy gross bp/bucket": float(gross.mean()), "net bp/bucket": float(gross.mean() - COST),
                    "hit rate": float((gross > 0).mean()), "top fifth |flow| gross bp": float(gross[top].mean()),
                    "top fifth net bp": float(gross[top].mean() - COST), "top fifth hit": float((gross[top] > 0).mean())}
    return res


def lg_test(R):
    T = pd.DataFrame([(r["day"], r["type"]) + tuple(x) for r in R for x in r["touches"]],
                     columns=["day", "type", "X", "rc", "m", "reject", "live_pos", "live_neg", "static_pos", "static_neg"])
    T.to_csv(OUT / "touches.csv.gz", index=False)
    def diff(t, col):
        lev = t[t[col]]
        ctl = t[~(t.live_pos | t.live_neg | t.static_pos | t.static_neg)]
        if not len(lev):
            return np.nan, np.nan, np.nan
        w = lev.rc.value_counts(normalize=True)
        cr = sum(w[k] * ctl[ctl.rc == k].reject.mean() for k in w.index if (ctl.rc == k).any())
        return lev.reject.mean() - cr, lev.reject.mean(), cr
    res = {}
    rng = np.random.default_rng(20261016)
    for typ in ("long", "short", "all"):
        t = T if typ == "all" else T[T.type == typ]
        days = t.day.unique()
        if not len(days):
            continue
        by = {d: x for d, x in t.groupby("day")}
        for col in ("live_pos", "live_neg", "static_pos", "static_neg"):
            d0, lv, cr = diff(t, col)
            boot = []
            for _ in range(NBOOT):
                pick = rng.choice(days, len(days))
                boot.append(diff(pd.concat([by[d] for d in pick]), col)[0])
            boot = np.array(boot)
            res[f"{typ} days, {col}"] = {"days": int(len(days)), "level touches": int(t[col].sum()),
                                         "control touches": int((~(t.live_pos | t.live_neg | t.static_pos | t.static_neg)).sum()),
                                         "reject at levels": float(lv), "reject at controls (roundness-weighted)": float(cr),
                                         "difference": float(d0), "p (diff <= 0)": float(np.mean(boot <= 0)), "p (diff >= 0)": float(np.mean(boot >= 0)),
                                         "95% day-bootstrap": [float(np.nanquantile(boot, .025)), float(np.nanquantile(boot, .975))]}
    return res


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    files = sorted(p.stem.split(".")[0] for p in MIN.glob("*.csv.gz"))
    days = [pd.Timestamp(f).date() for f in files if START <= pd.Timestamp(f) <= END]
    if "--days" in sys.argv:
        days = days[-int(sys.argv[sys.argv.index("--days") + 1]):]
    jobs = inputs(days)
    with Pool(4) as p:
        R = [r for r in p.imap(day_work, jobs, chunksize=2) if r is not None]
    fl, lg = fl_test(R), lg_test(R)
    pd.DataFrame([{k: r[k] for k in ("day", "type", "gex_open", "s0", "S_first")} | {"touches": len(r["touches"])} for r in R]).to_csv(OUT / "days.csv", index=False)
    (OUT / "fl.json").write_text(json.dumps(fl, indent=1))
    (OUT / "lg.json").write_text(json.dumps(lg, indent=1))
    print(json.dumps({"days used": len(R), "FL": fl, "LG": lg}, indent=1))
