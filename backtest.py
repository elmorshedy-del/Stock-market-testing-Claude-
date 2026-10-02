"""Brute-force tests across the universe.

1. Do channel lines matter?  Rolling log channels (fit on past bars only) ->
   fresh touches of a line -> does price reject (return to mid) or break
   (close 0.5 half-widths through) vs reject (close 0.5 half-widths back inside) within H bars?  Same pipeline on
   stationary-block-bootstrap paths of each stock's own returns (keeps
   drift, fat tails, vol clustering; destroys any memory of price LEVELS).
   If lines are real, real reject rates exceed the null.
2. Breakout model: walk-forward logistic regression on touch features.
3. Options-calendar tests that only need prices: opex pinning to strikes,
   and the vanna/charm window (return/vol drift into vs out of monthly opex).
"""
import json
import sys
import zlib
from multiprocessing import Pool

import numpy as np
import pandas as pd

from channels import fit_channel
from common import OUT, clv_delta, load_bars
from fetch import UNIVERSE

WINDOWS = (126, 252)
REFIT = 5
H = 20
Q = 0.15
R2_MIN = 0.75
BREAK_Z = 1.5
REJECT_Z = 0.5
N_NULL = 12
SPLIT = pd.Timestamp("2021-01-01")


def rolling_channels(o, h, l, c, L):
    """Per bar t: channel params fitted on bars [r-L+1, r], r <= t-1."""
    n = len(c)
    P = np.full((n, 5), np.nan)  # a, b, lo, hi, r2  (t measured in absolute bars)
    lh, ll, lc = np.log(h), np.log(l), np.log(c)
    for r in range(L - 1, n - 1, REFIT):
        s = r - L + 1
        t = np.arange(s, r + 1, dtype=float)
        P[r + 1: r + 1 + REFIT] = fit_channel(lh[s:r + 1], ll[s:r + 1], lc[s:r + 1], t, Q)
    return P


def zpos(P, t, logx):
    a, b, lo, hi = P[..., 0], P[..., 1], P[..., 2], P[..., 3]
    return (logx - (a + b * t + (hi + lo) / 2)) / ((hi - lo) / 2)


def events(df, L, with_features=True):
    o, h, l, c, v = (df[k].to_numpy(float) for k in ("open", "high", "low", "close", "volume"))
    n = len(c)
    P = rolling_channels(o, h, l, c, L)
    t = np.arange(n, dtype=float)
    zh, zl, zc = zpos(P, t, np.log(h)), zpos(P, t, np.log(l)), zpos(P, t, np.log(c))
    ret = np.diff(np.log(c), prepend=np.nan)
    clv = clv_delta(df).to_numpy() if with_features else None
    out = []
    last_touch = {1: -99, -1: -99}
    touch_hist = {1: [], -1: []}
    for i in range(L + 60, n - H):
        if not np.isfinite(P[i, 0]) or P[i, 4] < R2_MIN:
            continue
        for side, z in ((1, zh[i]), (-1, -zl[i])):
            if z < 1:
                continue
            fresh = i - last_touch[side] > 5
            last_touch[side] = i
            touch_hist[side].append(i)
            if not fresh:
                continue
            # walk forward with the channel frozen as known at bar i
            fz = zpos(P[i], t[i + 1:i + 1 + H], np.log(c[i + 1:i + 1 + H])) * side
            brk = np.argmax(fz >= BREAK_Z) if (fz >= BREAK_Z).any() else H + 1
            rej = np.argmax(fz <= REJECT_Z) if (fz <= REJECT_Z).any() else H + 1
            label = "break" if brk < rej else ("reject" if rej < brk else "none")
            ev = {"i": i, "date": df.index[i], "side": side, "label": label, "L": L,
                  "fwd": float(np.log(c[i + H] / c[i]) * side)}
            if with_features:
                s20 = np.nanstd(ret[i - 19:i + 1])
                s10, s60 = np.nanstd(ret[i - 9:i + 1]), np.nanstd(ret[i - 59:i + 1])
                atr = np.mean(h[i - 20:i] - l[i - 20:i])
                vol50 = v[i - 49:i + 1].mean()
                sma20 = c[i - 19:i + 1].mean()
                ev.update(
                    r2=P[i, 4],
                    slope=P[i, 1] * 252 * side,  # + means touch is in trend direction
                    width_vol=(P[i, 3] - P[i, 2]) / 2 / (s20 * np.sqrt(20)),
                    compress=s10 / s60,
                    vol_ratio=v[i - 4:i + 1].mean() / vol50,
                    clv5=clv[i - 4:i + 1].sum() / vol50 * side,
                    n_touch=sum(1 for j in touch_hist[side] if i - 60 <= j < i),
                    approach=(zc[i] - zc[i - 5]) * side,
                    zclose=zc[i] * side,
                    tr_atr=(h[i] - l[i]) / atr,
                    gap=abs(np.log(o[i] / c[i - 1])) / s20,
                    ext=np.log(c[i] / sma20) / s20 * side,
                )
            out.append(ev)
    return out


def bootstrap(df, rng, block=10):
    """Stationary block bootstrap of daily bars (returns + intrabar shape)."""
    c = df["close"].to_numpy(float)
    prev = np.r_[c[0], c[:-1]]
    rel = np.log(df[["open", "high", "low", "close"]].to_numpy(float) / prev[:, None])
    n = len(c)
    idx = np.empty(n, int)
    j = rng.integers(1, n)
    for k in range(n):
        if rng.random() < 1 / block:
            j = rng.integers(1, n)
        idx[k] = j
        j = j + 1 if j + 1 < n else 1
    r = rel[idx]
    lc = np.log(c[0]) + np.cumsum(r[:, 3])
    base = np.r_[np.log(c[0]), lc[:-1]]
    ohlc = np.exp(base[:, None] + r)
    sim = pd.DataFrame(ohlc, columns=["open", "high", "low", "close"], index=df.index)
    sim["volume"] = df["volume"].to_numpy()[idx]
    return sim


def run_ticker(sym):
    df = load_bars(sym)
    real = [e for L in WINDOWS for e in events(df, L)]
    for e in real:
        e["sym"] = sym
    rng = np.random.default_rng(zlib.crc32(sym.encode()))
    null = []
    for k in range(N_NULL):
        sim = bootstrap(df, rng)
        for L in WINDOWS:
            null += [{"side": e["side"], "label": e["label"], "L": L, "fwd": e["fwd"]}
                     for e in events(sim, L, with_features=False)]
    return real, null


# ---------------------------------------------------------------- options calendar
def third_fridays(idx):
    days = pd.date_range(idx[0], idx[-1], freq="WOM-3FRI")
    # holiday: use the last trading day on/before the third Friday
    pos = idx.searchsorted(days, side="right") - 1
    return set(idx[pos[pos >= 0]])


def strike_step(p):
    return 1 if p < 50 else 2.5 if p < 100 else 5 if p < 300 else 10 if p < 1000 else 25


def calendar_tests():
    """Per-date cross-sectional means, then stats across dates (stocks are
    highly correlated on a given day, so dates are the independent unit)."""
    pin, wk = [], []
    for sym in UNIVERSE:
        df = load_bars(sym)
        df = df[df.index >= "2018-01-01"]
        opex = third_fridays(df.index)
        c = df["close"].to_numpy()
        r = np.diff(np.log(c), prepend=np.nan)
        for i, d in enumerate(df.index):
            if i and (d.weekday() == 4 or d in opex):
                st = strike_step(c[i - 1])
                frac = (c[i] / st) % 1
                pin.append((d, d in opex, min(frac, 1 - frac)))
            if 5 <= i < len(c) - 5 and d.weekday() == 4:
                wk.append((d, d in opex, np.log(c[i] / c[i - 5]), np.log(c[i + 5] / c[i]),
                           np.std(r[i - 4:i + 1]), np.std(r[i + 1:i + 6])))
    pin = pd.DataFrame(pin, columns=["d", "opex", "dist"]).groupby(["d", "opex"]).dist.mean().reset_index()
    wk = pd.DataFrame(wk, columns=["d", "opex", "into", "after", "rv_in", "rv_out"]).groupby(["d", "opex"]).mean().reset_index()

    def stat(x):
        return {"mean": float(x.mean()), "se": float(x.std() / np.sqrt(len(x))), "n_dates": int(len(x))}
    o, f = wk[wk.opex], wk[~wk.opex]
    return {
        "pin_dist_opex": stat(pin[pin.opex].dist), "pin_dist_other_fri": stat(pin[~pin.opex].dist),
        "week_into_opex_bp": stat(1e4 * o.into), "week_after_opex_bp": stat(1e4 * o.after),
        "week_into_other_fri_bp": stat(1e4 * f.into),
        "into_minus_after_bp": stat(1e4 * (o.into - o.after)),
        "rv_after_over_into_opex": stat(o.rv_out / o.rv_in),
        "rv_after_over_into_other_fri": stat(f.rv_out / f.rv_in),
    }


def month_cluster_ci(ev, label="reject", n=2000, seed=0):
    """Bootstrap over calendar months (events in a month are correlated)."""
    rng = np.random.default_rng(seed)
    ev = ev.assign(m=pd.to_datetime(ev.date).dt.to_period("M"), y=(ev.label == label))
    g = ev.groupby("m").y.agg(["sum", "size"])
    k = rng.integers(0, len(g), (n, len(g)))
    sims = g["sum"].to_numpy()[k].sum(1) / g["size"].to_numpy()[k].sum(1)
    return float(ev.y.mean()), float(np.quantile(sims, 0.025)), float(np.quantile(sims, 0.975))


# ---------------------------------------------------------------- model
FEATS = ["r2", "slope", "width_vol", "compress", "vol_ratio", "clv5", "n_touch",
         "approach", "zclose", "tr_atr", "gap", "ext"]


def logit_fit(X, y, lam=1.0):
    from scipy.optimize import minimize

    def f(w):
        z = X @ w[1:] + w[0]
        p = 1 / (1 + np.exp(-z))
        eps = 1e-9
        loss = -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))
        g = p - y
        grad = np.r_[g.mean(), X.T @ g / len(y) + lam * w[1:] / len(y)]
        return loss + 0.5 * lam * (w[1:] ** 2).sum() / len(y), grad
    return minimize(f, np.zeros(X.shape[1] + 1), jac=True, method="L-BFGS-B").x


def auc(y, s):
    order = np.argsort(s)
    ranks = np.empty(len(s))
    ranks[order] = np.arange(1, len(s) + 1)
    pos = y == 1
    return (ranks[pos].sum() - pos.sum() * (pos.sum() + 1) / 2) / (pos.sum() * (~pos).sum())


def model(ev, feats=None):
    FEATS = feats or globals()["FEATS"]
    d = ev.dropna(subset=FEATS).copy()
    d["y"] = (d["label"] == "break").astype(int)
    tr, te = d[d.date < SPLIT], d[d.date >= SPLIT]
    mu, sd = tr[FEATS].mean(), tr[FEATS].std()
    X = lambda x: ((x[FEATS] - mu) / sd).clip(-5, 5).to_numpy()
    w = logit_fit(X(tr), tr.y.to_numpy())
    s_te = X(te) @ w[1:] + w[0]
    te = te.assign(p=1 / (1 + np.exp(-s_te)))
    te["dec"] = pd.qcut(te.p, 5, labels=False, duplicates="drop")
    single = {f: float(auc(te.y.to_numpy(), te[f].to_numpy())) for f in FEATS}
    return {
        "n_train": len(tr), "n_test": len(te), "base_break_rate_test": float(te.y.mean()),
        "auc_test": float(auc(te.y.to_numpy(), te.p.to_numpy())),
        "coef": dict(zip(FEATS, map(float, w[1:]))), "intercept": float(w[0]),
        "mu": mu.to_dict(), "sd": sd.to_dict(),
        "single_feature_auc_test": single,
        "quintiles": te.groupby("dec").agg(p=("p", "mean"), break_rate=("y", "mean"),
                                           fwd=("fwd", "mean"), n=("y", "size")).reset_index().to_dict("records"),
    }


def rates(rows):
    d = pd.DataFrame(rows)
    g = d.groupby("side")["label"].value_counts(normalize=True).unstack().fillna(0)
    g["n"] = d.groupby("side").size()
    g["fwd_bp"] = d.groupby("side")["fwd"].mean() * 1e4
    return g


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    syms = sys.argv[1:] or UNIVERSE
    with Pool(4) as pool:
        res = pool.map(run_ticker, syms)
    real = pd.DataFrame([e for r, _ in res for e in r])
    null = [e for _, n in res for e in n]
    real.to_csv(OUT / "events.csv", index=False)
    rr, nr = rates(real.to_dict("records")), rates(null)
    print("REAL\n", rr, "\nNULL (block bootstrap)\n", nr)
    m = model(real)
    m_noz = model(real, [f for f in FEATS if f != "zclose"])
    ci = {side: month_cluster_ci(real[real.side == side]) for side in (-1, 1)}
    print("reject rate real [95% month-cluster CI]:", ci)
    print("AUC full %.3f   without zclose %.3f" % (m["auc_test"], m_noz["auc_test"]))
    cal = calendar_tests()
    print(json.dumps({k: v for k, v in m.items() if k != "quintiles"}, indent=1, default=float))
    print(pd.DataFrame(m["quintiles"]))
    print(json.dumps(cal, indent=1))
    summary = {"real": rr.reset_index().to_dict("records"), "null": nr.reset_index().to_dict("records"),
               "reject_ci": ci, "model": m, "model_no_zclose": m_noz, "calendar": cal}
    (OUT / "backtest.json").write_text(json.dumps(summary, indent=1, default=float))
