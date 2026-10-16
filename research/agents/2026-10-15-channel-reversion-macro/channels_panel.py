"""Ex-ante monthly channels and forward outcomes for every (symbol, window W, month t).

For each month t the channel is fit on the trailing W monthly bars ending at t (bars <= t only), then FROZEN and
extrapolated forward. Stored per row:
  z         close position at t: -1 lower line, 0 centre, +1 upper line
  valid     slope > 0 and R^2 >= 0.80
  t_rev     months after t until a monthly LOW first reaches the frozen lower line (NaN if never, within 36 months)
  t_brk     months after t until a monthly CLOSE first reaches z >= 1.5 on the frozen channel
  n_fwd     complete months observed after t (for censoring)
The current partial month gets a row (for scoring today) but is never used as a forward month.

Usage: python channels_panel.py            real data  -> data/channels.pkl
       python channels_panel.py --boot N   N block-bootstrap paths per stock (W=84 only) -> data/channels_boot.pkl
       python channels_panel.py --boot 80 --seed 2 --out channels_boot_extra.pkl   (post-hoc precision run)
"""
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from channel_fit import fit_channel

HERE = Path(__file__).parent
DATA = HERE / "data"
WINDOWS = (60, 84, 120)
Q = 0.05
R2_MIN = 0.80
MAX_FWD = 36
BRK_Z = 1.5


def channel_rows(lh, ll, lc, n_complete, W, q=Q):
    """lh/ll/lc: log high/low/close arrays (consecutive months). n_complete: number of leading complete months."""
    n = len(lc)
    t_all = np.arange(n, dtype=float)
    rows = []
    for i in range(W - 1, n):
        t = t_all[i - W + 1:i + 1]
        a, b, lo, hi, r2 = fit_channel(lh[i - W + 1:i + 1], ll[i - W + 1:i + 1], lc[i - W + 1:i + 1], t, q)
        hw = (hi - lo) / 2
        z = (lc[i] - (a + b * i)) / hw
        j1, j2 = i + 1, min(n_complete, i + 1 + MAX_FWD)
        t_rev = t_brk = np.nan
        if j2 > j1:
            s = t_all[j1:j2]
            centre = a + b * s
            hit_r = np.nonzero(ll[j1:j2] <= centre + lo)[0]
            hit_b = np.nonzero((lc[j1:j2] - centre) / hw >= BRK_Z)[0]
            t_rev = hit_r[0] + 1 if len(hit_r) else np.nan
            t_brk = hit_b[0] + 1 if len(hit_b) else np.nan
        rows.append((i, a, b, lo, hi, r2, z, t_rev, t_brk, max(0, j2 - j1)))
    return rows


def frame_for(sym, mo, W, path=-1):
    mo = mo.sort_index()
    n_complete = int((~mo.partial).sum())
    lh, ll, lc = (np.log(mo[c].to_numpy(float)) for c in ("high", "low", "close"))
    rows = channel_rows(lh, ll, lc, n_complete, W)
    df = pd.DataFrame(rows, columns=["i", "a", "b", "lo", "hi", "r2", "z", "t_rev", "t_brk", "n_fwd"])
    df["month"] = mo.index[df.i.to_numpy()]
    df["partial"] = mo.partial.to_numpy()[df.i.to_numpy()]
    df["symbol"], df["W"], df["path"] = sym, W, path
    df["valid"] = (df.b > 0) & (df.r2 >= R2_MIN)
    df["growth_yr"] = np.exp(12 * df.b) - 1
    df["width"] = np.exp(df.hi - df.lo) - 1
    return df.drop(columns="i")


def _job(args):
    return frame_for(*args)


def bootstrap_path(mo, rng, mean_block=6):
    """Stationary block bootstrap of monthly (close return, high and low vs prior close) triples."""
    mo = mo[~mo.partial].sort_index()
    c = np.log(mo.close.to_numpy(float))
    h = np.log(mo.high.to_numpy(float))[1:] - c[:-1]
    l = np.log(mo.low.to_numpy(float))[1:] - c[:-1]
    r = np.diff(c)
    n = len(r)
    idx = np.empty(n, dtype=int)
    k = rng.integers(n)
    for j in range(n):
        if j > 0 and rng.random() < 1 / mean_block:
            k = rng.integers(n)
        idx[j] = k
        k = (k + 1) % n
    cc = np.concatenate([[c[0]], c[0] + np.cumsum(r[idx])])
    hh = np.concatenate([[np.log(mo.high.iloc[0])], cc[:-1] + h[idx]])
    ll = np.concatenate([[np.log(mo.low.iloc[0])], cc[:-1] + l[idx]])
    out = pd.DataFrame({"high": np.exp(np.maximum(hh, cc)), "low": np.exp(np.minimum(ll, cc)),
                        "close": np.exp(cc)}, index=mo.index)
    out["partial"] = False
    return out


def main():
    prices = pd.read_pickle(DATA / "monthly_prices.pkl")
    from fetch_data import STOCKS, INDICES
    syms = [s for s in STOCKS + INDICES if s in set(prices.symbol)]
    by = {s: prices[prices.symbol == s] for s in syms}
    if "--boot" in sys.argv:
        npaths = int(sys.argv[sys.argv.index("--boot") + 1])
        seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 20261015
        fname = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "channels_boot.pkl"
        rng = np.random.default_rng(seed)
        jobs = []
        for s in syms:
            if s.startswith("^"):
                continue
            for p in range(npaths):
                jobs.append((s, bootstrap_path(by[s], rng), 84, p))
        with Pool(2) as pool:
            out = pd.concat(pool.map(_job, jobs, chunksize=4))
        out.to_pickle(DATA / fname)
        print("bootstrap rows", len(out), "paths", npaths)
        return
    jobs = [(s, by[s], W) for s in syms for W in WINDOWS if len(by[s]) > W]
    with Pool(2) as pool:
        out = pd.concat(pool.map(_job, jobs))
    out.to_pickle(DATA / "channels.pkl")
    print("rows", len(out), "symbols", out.symbol.nunique())


if __name__ == "__main__":
    main()
