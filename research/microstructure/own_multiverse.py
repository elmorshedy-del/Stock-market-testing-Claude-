"""Multiverse test on a stock's OWN option positioning (REPORT 4z): do the own-gamma findings of
4s/4t survive every reasonable analyst choice, or was each one a lucky specification?
4j did this for S&P gamma; 4k found S&P gamma says nothing about TSLA. This uses the stock's own chain.

Every choice is a dimension and all combinations are run:
  signal      below flip   % above own gamma flip <= d,     d in {+2, 0, -3, -6}
              put-heavy    own gamma percentile <= q,        q in {0.1, 0.2, 0.3, 0.4}
              freed        OI-near-price percentile <= q,    q in {0.1, 0.2, 0.3, 0.4}
  move        fixed burst  +-5% in a day or +-9% in two (4l)
              vol burst    a day beyond 2x the stock's own prior 60-day sigma
              leg          a 10-day return in the stock's own top / bottom decile
  direction   up | down    (a move of that kind starts within H), plus the plain forward return
  horizon     H in {3, 5, 10, 20} sessions (3 = the window 4s used)
  days        turn-on (first day on, >= 10 sessions apart, as 4j) | in state (every day on, as 4s)
  era         2021+ | 2021-23 | 2024+
Per spec: mean outcome on the signal's days minus the era's all-day mean.
Null: slide the whole positioning frame in time against prices (keeps persistence, kills timing),
rerun every spec, 300 times. Per family (signal x direction x days): share of specs beyond the null's 5%
tails each way, and one joint p from the median standardized effect.
Then the controlled logits of 4s/4t, strictly forward.
Usage: python own_multiverse.py TSLA [MSFT ...]
"""
import itertools
import sys

import numpy as np
import pandas as pd

from burst_gamma import state
from common import OUT, load_bars
from stock_now import burst_days

SIGNALS = {"below flip": ("to_flip_pct", (2, 0, -3, -6)), "put-heavy": ("g_pct", (0.1, 0.2, 0.3, 0.4)),
           "freed": ("near_pct", (0.1, 0.2, 0.3, 0.4))}
HS, GAP, N_NULL = (3, 5, 10, 20), 10, 300
EVENTS = ("turn-on", "in state")
ERAS = {"2021+": ("2021-01-01", "2100-01-01"), "2021-23": ("2021-01-01", "2023-12-31"), "2024+": ("2024-01-01", "2100-01-01")}


def first_on(c, gap=GAP):
    out, last = np.zeros(len(c), bool), -10**9
    for i in np.where(c & ~np.r_[False, c[:-1]])[0]:
        if i - last >= gap:
            out[i], last = True, i
    return out


def within(mark, h):
    """1 if a move marked on day t+1..t+h, NaN where the window runs past the data."""
    m = np.r_[mark.astype(float), np.full(h, np.nan)]
    w = np.lib.stride_tricks.sliding_window_view(m[1:], h)[:len(mark)]
    return np.where(np.isnan(w).any(axis=1), np.nan, w.max(axis=1))


def outcomes(c):
    lc = np.log(c.to_numpy())
    r = np.r_[np.nan, np.diff(lc)]
    sig = pd.Series(r).rolling(60).std().shift(1).to_numpy()
    f10 = np.r_[lc[10:] - lc[:-10], np.full(10, np.nan)]
    lo, hi = np.nanquantile(f10, [0.1, 0.9])
    marks = {("fixed burst", "up"): burst_days(c, 1), ("fixed burst", "down"): burst_days(c, -1),
             ("vol burst", "up"): np.nan_to_num(r >= 2 * sig), ("vol burst", "down"): np.nan_to_num(r <= -2 * sig),
             ("leg", "up"): np.nan_to_num(f10 >= hi), ("leg", "down"): np.nan_to_num(f10 <= lo)}
    Y = {(mv, dr, h): within(np.asarray(m, bool), h) for (mv, dr), m in marks.items() for h in HS}
    for h in HS:
        Y[("return", "return", h)] = np.r_[lc[h:] - lc[:-h], np.full(h, np.nan)]
    return Y


def run(S, Y, eras):
    rows = []
    for sname, (col, ths) in SIGNALS.items():
        x = S[col]
        for th, (era, m), evt in itertools.product(ths, eras.items(), EVENTS):
            on = (x <= th) & m
            ev = first_on(on) if evt == "turn-on" else on
            for (mv, dr, h), y in Y.items():
                ok = ev & ~np.isnan(y)
                base = np.nanmean(y[m])
                eff = (y[ok].mean() - base) if ok.sum() >= 5 else np.nan
                rows.append((sname, th, era, evt, mv, dr, h, int(ok.sum()), eff))
    return pd.DataFrame(rows, columns=["signal", "threshold", "era", "days", "move", "direction", "H", "n", "effect"])


def study(sym, seed=0):
    st = state(sym)
    c = load_bars(sym).close
    idx = st.index.intersection(c.index)
    st, c = st.loc[idx], c.loc[idx]
    keep = st.index >= "2021-01-01"
    st, c = st[keep], c[keep]
    Y = outcomes(c)
    S = {col: st[col].to_numpy() for col, _ in SIGNALS.values()}
    eras = {k: np.asarray((st.index >= a) & (st.index <= b)) for k, (a, b) in ERAS.items()}
    real = run(S, Y, eras)
    rng = np.random.default_rng(seed)
    null = np.array([run({k: np.roll(v, s) for k, v in S.items()}, Y, eras).effect.to_numpy()
                     for s in rng.integers(60, len(st) - 60, N_NULL)])
    e = real.effect.to_numpy()
    real["p_hi"] = (null >= e).mean(axis=0)
    real["p_lo"] = (null <= e).mean(axis=0)
    real.loc[real.effect.isna(), ["p_hi", "p_lo"]] = np.nan
    mu, sd = np.nanmean(null, 0), np.nanstd(null, 0)
    z, zn = (e - mu) / sd, (null - mu) / sd
    real["z"] = z
    fam = []
    for (sg, dr, dy), g in real.groupby(["signal", "direction", "days"], sort=False):
        i = g.index.to_numpy()
        med, nmed = np.nanmedian(z[i]), np.nanmedian(zn[:, i], axis=1)
        fam.append({"signal": sg, "direction": dr, "days": dy, "specs": int(g.effect.notna().sum()),
                    "share_higher": (g.effect > 0).mean(), "beyond_hi_5%": (g.p_hi < 0.05).mean(),
                    "beyond_lo_5%": (g.p_lo < 0.05).mean(), "median_effect": g.effect.median(),
                    "joint_p": float(np.mean(np.abs(nmed - np.nanmean(nmed)) >= abs(med - np.nanmean(nmed))))})
    fam = pd.DataFrame(fam)
    now = {k: (float(st[col].iloc[-1]), k_on) for k, (col, ths) in SIGNALS.items()
           for k_on in [[t for t in ths if st[col].iloc[-1] <= t]]}
    return real, fam, now, st.index[-1]


def controlled(sym, n=300):
    """The 4s/4t logits, strictly forward (bursts in sessions t+1..t+3) with controls known at the
    close of t: 5/20-day vol, |5-day| move, 20-day return, S&P gamma. Freed adds own gamma and IV."""
    from stock_gamma import CTRL, burst_logit, frame
    st = state(sym)
    x = frame(sym).join(st[[c for c in ("near_pct", "iv_pct") if c in st]])
    x["below"], x["put_heavy"] = x.below.astype(float), (x.g_pct <= 1 / 3).astype(float)
    feats = [("below", CTRL), ("put_heavy", CTRL)]
    if "near_pct" in x:
        x["freed"] = (x.near_pct <= 1 / 3).astype(float)
        feats.append(("freed", CTRL + ["g_pct", "iv_pct"]))
    rows = []
    z = x[x.index >= "2021-01-01"].dropna(subset=["g_pct"])
    for feat, ctrl in feats:
        for tgt in ("up3", "dn3", "sup3", "sdn3"):
            r = burst_logit(x, tgt, feat, n=n, ctrl=ctrl)
            rows.append({"feature": feat, "burst": tgt, "rate_if": z.loc[z[feat] == 1, tgt].mean(),
                         "rate_else": z.loc[z[feat] == 0, tgt].mean(), "odds_ratio": r["odds_ratio"], "p": r["shifted_null_p"]})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    for sym in sys.argv[1:] or ["TSLA"]:
        real, fam, now, day = study(sym)
        real.to_csv(OUT / f"own_multiverse_{sym}.csv", index=False)
        print(f"\n=== {sym}: {len(real)} specs, {N_NULL} shifted nulls, own data 2021-01 .. {day.date()}")
        print("shares are of specs; by luck about 5% land beyond each 5% tail")
        print(fam.round(3).to_string(index=False))
        sub = real[real.direction != "return"]
        print("\nmedian effect (probability points) by move definition and horizon:")
        for dim in ("move", "H", "era"):
            print((100 * sub.groupby(["signal", "direction", "days", dim]).effect.median()).unstack().round(1).to_string())
        print("\nreturn (pct points) by horizon:")
        print((100 * real[real.direction == "return"].groupby(["signal", "days", "H"]).effect.median()).unstack().round(2).to_string())
        print("\ntoday:", {k: f"{v:.2f} -> on at {on}" for k, (v, on) in now.items()})
        cc = controlled(sym)
        cc.to_csv(OUT / f"own_controlled_{sym}.csv", index=False)
        print("\ncontrolled logits, bursts in sessions t+1..t+3 (up3/dn3 fixed, sup3/sdn3 vol-scaled):")
        print(cc.round(3).to_string(index=False))
