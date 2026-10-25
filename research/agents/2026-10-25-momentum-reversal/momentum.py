"""Momentum and reversal by regime (README.md, pre-registered at f8629cf): M1 TSMOM (S&P), M2 cross-sectional momentum, M3 weekly reversal,
M4 own-stock autocorrelation by phase, M5 same-hour persistence. Usage: OMP_NUM_THREADS=1 python momentum.py <long> <breadth> <hourly>
-> out/momentum.json, out/cells.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
AG = HERE.parent
sys.path.insert(0, str(AG / "2026-10-25-channel-correction-theory"))
import dossier as Dz                               # noqa: E402
sys.path.insert(0, str(AG / "2026-10-25-intraday-hours"))
import segments as Sg                              # noqa: E402

NB = 4000
RNG = np.random.default_rng(20261110)
EXTRA = ["AVGO", "TSLA", "CRM", "NFLX", "BRK-B", "V", "MA", "ABBV", "TMO", "ACN", "LIN", "NKE", "AMGN", "HON", "UPS", "LOW", "SBUX", "GS", "MS", "BLK",
         "SPGI", "INTU", "NOW", "ISRG", "BKNG", "ADP", "DE", "CVS", "MDT", "GILD", "NEE", "DUK", "PM", "CMCSA", "LMT", "RTX", "UNP", "COP", "AXP", "SCHW"]
CH0 = pd.Timestamp("2022-10-13")


def eras(idx):
    e = np.full(len(idx), "", dtype=object)
    for lab, a, b in (("1928-49", "1900", "1949-12-31"), ("1950-79", "1950", "1979-12-31"), ("1980-99", "1980", "1999-12-31"),
                      ("2000-22", "2000", "2022-10-12"), ("channel 2022-26", "2022-10-13", "2100")):
        e[(idx >= pd.Timestamp(a)) & (idx <= pd.Timestamp(b))] = lab
    return e


def market_regimes(spx):
    r = np.log(spx).diff()
    vol = r.rolling(63).std()
    vp = vol.rolling(2520, min_periods=756).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
    R = pd.DataFrame(index=spx.index)
    R["vol"] = pd.cut(vp, [-0.01, 1 / 3, 2 / 3, 1.01], labels=["low vol", "mid vol", "high vol"]).astype(object)
    R["trend"] = np.where(spx > spx.rolling(200).mean(), "above 200d", "below 200d")
    R["state"] = np.where(np.log(spx).diff(504) > 0, "bull (24m up)", "bear (24m down)")
    R["era"] = eras(spx.index)
    return R


def blocks(n, L):
    st = RNG.integers(0, max(1, n - L), int(np.ceil(n / L)))
    return np.concatenate([np.arange(s, s + L) for s in st])[:n]


def cells_mean(v, labels, L, name):
    """Mean of v per regime label, with a block-bootstrap 90% interval; labels travel with rows."""
    v = np.asarray(v, float); out = []
    ok = np.isfinite(v)
    bsets = [blocks(len(v), L) for _ in range(NB)]
    for reg, lab in labels.items():
        lab = np.asarray(lab, object)
        for c in sorted(set(lab[ok & (lab != "") & pd.notna(lab)])):
            m = ok & (lab == c)
            bs = [np.nanmean(v[ii][m[ii]]) if m[ii].any() else np.nan for ii in bsets[:1000]]
            out.append({"test": name, "regime": reg, "cell": c, "n": int(m.sum()), "mean": float(np.mean(v[m])),
                        "lo90": float(np.nanpercentile(bs, 5)), "hi90": float(np.nanpercentile(bs, 95))})
    return out


def contrast(v, lab, a, b, L, side):
    v, lab = np.asarray(v, float), np.asarray(lab, object)
    f = lambda vv, ll: np.nanmean(vv[ll == a]) - np.nanmean(vv[ll == b])
    obs = f(v, lab)
    bs = np.array([f(v[ii], lab[ii]) for ii in (blocks(len(v), L) for _ in range(NB))])
    p = float((bs <= 0).mean()) if side > 0 else float((bs >= 0).mean())
    return {"contrast": f"{a} minus {b}", "value": float(obs), "predicted sign": "+" if side > 0 else "-", "p": p, "supported": bool(np.sign(obs) == side and p < 0.05)}


def primary(v, L, side):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    bs = np.array([v[ii].mean() for ii in (blocks(len(v), L) for _ in range(NB))])
    return {"mean": float(v.mean()), "n": int(len(v)), "p": float((bs <= 0).mean()) if side > 0 else float((bs >= 0).mean())}


def monthly(s):
    return s.resample("ME").last()


def main(long, bfold, hourly):
    OUT.mkdir(exist_ok=True)
    spx = Dz.close(long, "GSPC")
    R = market_regimes(spx)
    res, cells = {}, []
    # ---------------- M1 ----------------
    P = monthly(spx)
    rn = np.log(P).diff().shift(-1)
    Rm = R.reindex(P.index, method="ffill")
    trend10 = np.where(P > P.rolling(10).mean(), "above 10m avg", "below 10m avg")
    Rm["trend"] = trend10
    rm1 = np.log(P).diff()
    for lb in (12, 3, 1):
        sig = np.sign(np.log(P).diff(lb))
        strat = (sig * rn).to_numpy()
        lab = {"all": np.full(len(P), "all", object), "vol": Rm.vol.to_numpy(), "state": Rm.state.to_numpy(), "trend": Rm.trend.to_numpy(), "era": Rm.era.to_numpy()}
        if lb == 12:
            edge = strat - rn.to_numpy()                                       # timing value vs buy-and-hold: 0 when long, -2r when short
            res["M1 PRIMARY: 12m TSMOM, mean monthly strategy return minus buy-and-hold (%)"] = {k: (v * 100 if k == "mean" else v) for k, v in primary(edge[np.isfinite(sig.to_numpy())], 12, 1).items()}
            res["M1 strategy vs buy-and-hold, mean monthly %"] = {"TSMOM": float(100 * np.nanmean(strat)), "buy and hold": float(100 * np.nanmean(rn)),
                                                                 "share of months long": float((sig > 0).mean())}
            cells += cells_mean(100 * edge, lab, 12, "M1 TSMOM 12m: strategy minus buy-and-hold, %/month")
            res["M1 contrasts"] = [contrast(edge, Rm.vol.to_numpy(), "high vol", "low vol", 12, 1), contrast(edge, Rm.state.to_numpy(), "bear (24m down)", "bull (24m up)", 12, 1)]
        res[f"M1 lookback {lb}m: strategy mean %/month, sharpe-like"] = {"mean": float(100 * np.nanmean(strat)), "t": float(np.nanmean(strat) / np.nanstd(strat) * np.sqrt(np.isfinite(strat).sum()))}
    # ---------------- panel ----------------
    names = Dz.PANEL + EXTRA
    C = pd.DataFrame({s: (Dz.close(long, s) if s in Dz.PANEL else Dz.close(bfold, s)) for s in names})
    C = C[C.index >= "1985-01-01"].reindex(spx.index[spx.index >= "1985-01-01"]).ffill(limit=3)
    # ---------------- M2 ----------------
    M = monthly(C)
    rn2 = np.log(M).diff().shift(-1)
    sig2 = np.log(M.shift(1)) - np.log(M.shift(12))
    wml, months = [], []
    for t in M.index[M.index >= "1990-01-01"]:
        s, r = sig2.loc[t], rn2.loc[t]
        ok = s.notna() & r.notna()
        if ok.sum() < 15:
            continue
        q = s[ok].rank(pct=True)
        wml.append(r[ok][q > 2 / 3].mean() - r[ok][q <= 1 / 3].mean()); months.append(t)
    W = pd.Series(wml, index=pd.DatetimeIndex(months))
    Rw = R.reindex(W.index, method="ffill")
    spx_m = np.log(monthly(spx)).diff().reindex(W.index)
    reb = np.where((Rw.state == "bear (24m down)").to_numpy() & (spx_m > 0).to_numpy(), "rebound month", "not rebound")
    trend_m = np.where((monthly(spx) > monthly(spx).rolling(10).mean()).reindex(W.index), "above 10m avg", "below 10m avg")
    lab2 = {"all": np.full(len(W), "all", object), "state": Rw.state.to_numpy(), "rebound": reb, "vol": Rw.vol.to_numpy(), "trend": trend_m, "era": Rw.era.to_numpy()}
    res["M2 PRIMARY: XS momentum WML mean %/month"] = {k: (v * 100 if k == "mean" else v) for k, v in primary(W.to_numpy(), 12, 1).items()}
    cells += cells_mean(100 * W.to_numpy(), lab2, 12, "M2 XS momentum (top - bottom third), %/month")
    res["M2 contrasts"] = [contrast(W.to_numpy(), Rw.state.to_numpy(), "bear (24m down)", "bull (24m up)", 12, -1)]
    rb = W.to_numpy()[reb == "rebound month"]
    res["M2 rebound months: mean %/month, n, share negative"] = [float(100 * rb.mean()) if len(rb) else None, int(len(rb)), float((rb < 0).mean()) if len(rb) else None]
    res["M2 universe size (median stocks per month)"] = float(np.median([int((sig2.loc[t].notna() & rn2.loc[t].notna()).sum()) for t in W.index]))
    # ---------------- M3 ----------------
    D = C[C.index >= "1990-01-01"]
    lp = np.log(D)
    step = np.arange(0, len(D) - 10, 5)
    rev, wk = [], []
    for i in step:
        if i < 5:
            continue
        past = lp.iloc[i] - lp.iloc[i - 5]
        nxt = lp.iloc[i + 5] - lp.iloc[i]
        ok = past.notna() & nxt.notna()
        if ok.sum() < 15:
            continue
        q = past[ok].rank(pct=True)
        rev.append(nxt[ok][q <= 1 / 3].mean() - nxt[ok][q > 2 / 3].mean()); wk.append(D.index[i])
    V = pd.Series(rev, index=pd.DatetimeIndex(wk))
    Rv = R.reindex(V.index)
    lab3 = {"all": np.full(len(V), "all", object), "vol": Rv.vol.to_numpy(), "trend": Rv.trend.to_numpy(), "state": Rv.state.to_numpy(), "era": Rv.era.to_numpy()}
    res["M3 PRIMARY: weekly reversal gross mean bp/week"] = {k: (v * 1e4 if k == "mean" else v) for k, v in primary(V.to_numpy(), 20, 1).items()}
    res["M3 net of 20 bp/week (10 bp per leg), mean bp/week"] = float(1e4 * (V.mean() - 0.002))
    cells += cells_mean(1e4 * V.to_numpy(), lab3, 20, "M3 weekly reversal (losers - winners), bp/week gross")
    res["M3 contrasts"] = [contrast(V.to_numpy(), Rv.vol.to_numpy(), "high vol", "low vol", 20, 1), contrast(V.to_numpy(), Rv.trend.to_numpy(), "below 200d", "above 200d", 20, 1)]
    # ---------------- M4 ----------------
    r = lp.diff()
    sd = r.rolling(20).std().shift(1)
    z = r / sd
    x = z.rolling(5).sum()
    y = z[::-1].rolling(5).sum()[::-1].shift(-1)
    ma50, ma200 = D.rolling(50).mean(), D.rolling(200).mean()
    up = (D > ma50) & (ma50 > ma200)
    dn = (D < ma50) & (ma50 < ma200)
    hi = D / D.rolling(252, min_periods=200).max()
    xs, ys = x.sub(x.mean()), y.sub(y.mean())                                   # within-stock demeaning
    valid = xs.notna() & ys.notna()
    def agg(mask):
        m = (valid & mask).to_numpy()
        Sxy = np.where(m, xs.to_numpy() * ys.to_numpy(), 0).sum(axis=1)
        Sxx = np.where(m, xs.to_numpy() ** 2, 0).sum(axis=1)
        return Sxy, Sxx, int(m.sum())
    phases = {"phase: uptrend": up, "phase: downtrend": dn, "phase: mixed": ~up & ~dn & ma200.notna(),
              "52w: near high (>=95%)": hi >= 0.95, "52w: far (<80%)": hi < 0.80, "all": valid}
    Rd = R.reindex(D.index)
    for k in ("vol", "trend"):
        for c in sorted(set(Rd[k].dropna())):
            phases[f"market {k}: {c}"] = pd.DataFrame(np.repeat((Rd[k] == c).to_numpy()[:, None], D.shape[1], axis=1), index=D.index, columns=D.columns)
    A = {k: agg(m) for k, m in phases.items()}
    n = len(D)
    bsets = [blocks(n, 20) for _ in range(NB)]
    m4 = {}
    for k, (sxy, sxx, cnt) in A.items():
        b = np.array([sxy[ii].sum() / sxx[ii].sum() for ii in bsets[:1500]])
        m4[k] = {"slope": float(sxy.sum() / sxx.sum()), "lo90": float(np.percentile(b, 5)), "hi90": float(np.percentile(b, 95)), "stock-days": cnt}
        cells.append({"test": "M4 own-stock 5d->5d slope (z)", "regime": k.split(":")[0], "cell": k, "n": cnt, "mean": m4[k]["slope"], "lo90": m4[k]["lo90"], "hi90": m4[k]["hi90"]})
    sxy, sxx, _ = A["all"]
    b = np.array([sxy[ii].sum() / sxx[ii].sum() for ii in bsets])
    res["M4 PRIMARY: pooled 5d->5d slope"] = {"slope": float(sxy.sum() / sxx.sum()), "p": float((b >= 0).mean())}
    def con4(a, c, side):
        f = lambda ii: A[a][0][ii].sum() / A[a][1][ii].sum() - A[c][0][ii].sum() / A[c][1][ii].sum()
        obs = f(np.arange(n)); bb = np.array([f(ii) for ii in bsets])
        p = float((bb <= 0).mean()) if side > 0 else float((bb >= 0).mean())
        return {"contrast": f"{a} minus {c}", "value": float(obs), "predicted sign": "+", "p": p, "supported": bool(obs > 0 and p < 0.05)}
    res["M4 cells"] = m4
    res["M4 contrasts"] = [con4("phase: uptrend", "phase: downtrend", 1), con4("52w: near high (>=95%)", "52w: far (<80%)", 1)]
    # ---------------- M5 ----------------
    H = {}
    for p in sorted(Path(hourly).glob("*_60m.json")):
        s = p.name.split("_")[0]
        f = Sg.bars(hourly, s)
        f["day"] = f.index.tz_localize(None).normalize(); f["lab"] = f.index.strftime("%H:%M")
        g = f.groupby("day")
        rows = {}
        for d, x_ in g:
            if list(x_.lab) != Sg.LABELS:
                continue
            c_ = x_.close.to_numpy(); o0 = x_.open.iloc[0]
            rows[d] = np.log(np.r_[c_[0] / o0, c_[1:] / c_[:-1]])
        H[s] = pd.DataFrame(rows).T
    days = sorted(set.intersection(*[set(v.index) for v in H.values()]))
    syms = list(H)
    Ar = np.stack([H[s].reindex(days).to_numpy() for s in syms])               # stock x day x slot
    sig5 = np.full(Ar.shape, np.nan)
    for t in range(20, len(days)):
        sig5[:, t, :] = np.nanmean(Ar[:, t - 20:t, :], axis=1)
    spread = np.full((len(days), 7), np.nan)
    for t in range(20, len(days)):
        for k in range(7):
            s_, r_ = sig5[:, t, k], Ar[:, t, k]
            ok = np.isfinite(s_) & np.isfinite(r_)
            q = pd.Series(s_[ok]).rank(pct=True).to_numpy()
            spread[t, k] = r_[ok][q > 2 / 3].mean() - r_[ok][q <= 1 / 3].mean()
    dd = pd.DatetimeIndex(days)
    Rh = R.reindex(dd)
    daily_spread = np.nanmean(spread, axis=1)
    res["M5 PRIMARY: same-hour persistence, mean bp per slot"] = {k: (v * 1e4 if k == "mean" else v) for k, v in primary(daily_spread[20:], 20, 1).items()}
    slot_names = ["09:30-10:30", "10:30-11:30", "11:30-12:30", "12:30-13:30", "13:30-14:30", "14:30-15:30", "15:30-close"]
    for k in range(7):
        cells += cells_mean(1e4 * spread[20:, k], {"slot": np.full(len(days) - 20, slot_names[k], object)}, 20, "M5 same-hour persistence, bp per slot")
    cells += cells_mean(1e4 * daily_spread[20:], {"vol": Rh.vol.to_numpy()[20:]}, 20, "M5 same-hour persistence, bp per slot")
    # ---------------- Holm ----------------
    ps = {"M1": res["M1 PRIMARY: 12m TSMOM, mean monthly strategy return minus buy-and-hold (%)"]["p"], "M2": res["M2 PRIMARY: XS momentum WML mean %/month"]["p"],
          "M3": res["M3 PRIMARY: weekly reversal gross mean bp/week"]["p"], "M4": res["M4 PRIMARY: pooled 5d->5d slope"]["p"],
          "M5": res["M5 PRIMARY: same-hour persistence, mean bp per slot"]["p"]}
    order = sorted(ps, key=ps.get); holm, run = {}, 0
    for i, k in enumerate(order):
        run = max(run, min(1, (len(ps) - i) * ps[k])); holm[k] = run
    res["Holm-adjusted primary p"] = holm
    res["today"] = {"S&P trend": R.trend.iloc[-1], "state": R.state.iloc[-1], "vol third": R.vol.iloc[-1], "S&P 12m return %": float(100 * (spx.iloc[-1] / spx.iloc[-253] - 1))}
    ph = {}
    last = D.index[-1]
    for s in ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "JPM", "XOM", "UNH", "LLY"]:
        ph[s] = {"phase": "uptrend" if up.loc[last, s] else ("downtrend" if dn.loc[last, s] else "mixed"), "% of 52w high": float(100 * hi.loc[last, s]),
                 "12-1m momentum %": float(100 * (np.exp(sig2.iloc[-1][s]) - 1)) if pd.notna(sig2.iloc[-1][s]) else None,
                 "past 5d %": float(100 * (D[s].iloc[-1] / D[s].iloc[-6] - 1))}
    res["today: stock phases"] = ph
    res["today: share of 81 stocks in uptrend / downtrend / mixed"] = [float(up.loc[last].mean()), float(dn.loc[last].mean()), float(1 - up.loc[last].mean() - dn.loc[last].mean())]
    pd.DataFrame(cells).to_csv(OUT / "cells.csv", index=False)
    (OUT / "momentum.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:4]), indent=1, default=float))
