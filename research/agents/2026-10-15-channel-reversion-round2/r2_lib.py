"""Shared machinery for round 2 (panels, signals, shift null, min-p family test, episodes, barrier model)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).parent
PREV = HERE.parent / "2026-10-15-channel-reversion-macro"
sys.path.insert(0, str(PREV))
import tests as T                 # noqa: E402  (round-1 ShiftIndex, delta, trailing_pct)
import fetch_data as FD           # noqa: E402
from build import STOCKS as NONTECH  # noqa: E402

DATA, OUT = HERE / "data", HERE / "out"
TECH = FD.STOCKS
SEED = 20261016
NDRAW = 1000


def load_monthly_panels():
    """Round-1 tech channels + round-2 non-tech channels, with ex-ante vol merged in."""
    tech = pd.read_pickle(PREV / "data" / "channels.pkl")
    tech = tech[tech.symbol.isin(TECH)]
    non = pd.read_pickle(DATA / "channels.pkl")
    ch = pd.concat([tech.assign(panel="tech"), non.assign(panel="nontech")], ignore_index=True)
    vol = pd.read_pickle(DATA / "vol_monthly.pkl")
    ch = ch.merge(vol, on=["symbol", "month"], how="left")
    ch["hw"] = (ch.hi - ch.lo) / 2
    ch["x0"] = (ch.z + 1) * ch.hw            # log distance from close to the lower line
    return ch


def p_barrier(x0, sigma, H):
    """Driftless Brownian motion (relative to the rising line): P(touch within H) = 2 Phi(-x0 / (sigma sqrt H))."""
    x0 = np.asarray(x0, float)
    p = 2 * norm.cdf(-x0 / (np.asarray(sigma, float) * np.sqrt(H)))
    return np.where(x0 <= 0, 1.0, p)


def rows(ch, symbols, W, ztop, H, outcome="rev", key="month", top_only=True):
    c = ch[(ch.W == W) & ch.symbol.isin(symbols) & ch.valid & ~ch.partial].copy()
    if top_only:
        c = c[c.z >= ztop]
    tcol = "t_rev" if outcome == "rev" else "t_brk"
    hit = c[tcol] <= H
    c = c[hit | (c.n_fwd >= H)].copy()
    c["y"] = (c[tcol] <= H).astype(float)
    c["t"] = c[key]
    return c.reset_index(drop=True)


def signal(raw, win=120, minp=36, cut=2 / 3):
    p = T.trailing_pct(raw, win, minp)
    return pd.Series(np.where(p.isna(), np.nan, (p >= cut).astype(float)), index=raw.index)


def binary(raw):
    return raw.astype(float)


class Shifter:
    """Signal values for panel rows under a circular shift fraction f (0 = real). Works for a time-indexed series
    (macro) or a DataFrame with one column per symbol (stock-specific)."""

    def __init__(self, sig, rows_):
        self.rows = rows_
        if isinstance(sig, pd.Series):
            si = T.ShiftIndex(sig)
            self.plan = [(np.arange(len(rows_)), si, si.positions(rows_.t.to_numpy()) if si.L else None)]
        else:
            self.plan = []
            for s, idx in rows_.groupby("symbol").indices.items():
                if s in sig.columns:
                    si = T.ShiftIndex(sig[s])
                    if si.L:
                        self.plan.append((idx, si, si.positions(rows_.t.to_numpy()[idx])))

    def values(self, f):
        out = np.full(len(self.rows), np.nan)
        for idx, si, pos in self.plan:
            if pos is not None:
                out[idx] = si.values(pos, f)
        return out


def shift_deltas(rows_, sig, fracs, stat=None):
    """[observed, null draws...] of stat(y, s) (default: rate difference on minus off)."""
    stat = stat or T.delta
    sh = Shifter(sig, rows_)
    y = rows_.y.to_numpy()
    return np.array([stat(y, sh.values(0))] + [stat(y, sh.values(f)) for f in fracs])


def p_one_sided(arr):
    obs, null = arr[0], arr[1:]
    null = null[~np.isnan(null)]
    if np.isnan(obs) or len(null) == 0:
        return np.nan
    return float((1 + (null >= obs).sum()) / (1 + len(null)))


def minp_family(arrs):
    """Westfall-Young min-p over a dict name -> [obs, null...]."""
    p_obs, p_null = [], []
    for a in arrs.values():
        obs, nul = a[0], a[1:]
        ok = ~np.isnan(nul)
        if np.isnan(obs) or ok.sum() < 50:
            continue
        srt = np.sort(nul[ok])
        p_obs.append((1 + (srt >= obs).sum()) / (1 + len(srt)))
        pd_ = 1 - np.searchsorted(srt, nul, side="left") / len(srt)
        pd_[~ok] = np.nan
        p_null.append(pd_)
    if not p_obs:
        return np.nan
    m = np.nanmin(np.array(p_null), axis=0)
    return float((1 + (m <= min(p_obs)).sum()) / (1 + (~np.isnan(m)).sum()))


def episodes(ch, symbols, W, ztop, H, outcome="rev", key="month", wave_gap_days=366):
    c = ch[(ch.W == W) & ch.symbol.isin(symbols) & ~ch.partial].sort_values(["symbol", key]).copy()
    c["top"] = c.valid & (c.z >= ztop)
    tcol = "t_rev" if outcome == "rev" else "t_brk"
    step = pd.Timedelta(days=40 if key == "month" else 9)
    out = []
    for s, g in c.groupby("symbol"):
        g = g.reset_index(drop=True)
        run = []
        for k in range(len(g) + 1):
            on = k < len(g) and g.top[k]
            if on and (not run or g[key][k] - g[key][run[-1]] <= step):
                run.append(k)
                continue
            if run:
                last = g.iloc[run[-1]]
                hit = last[tcol] <= H
                if hit or last.n_fwd >= H:
                    out.append({"symbol": s, "start": g[key][run[0]], "end": last[key], "bars": len(run),
                                "z_max": float(g.z[run].max()), "event": bool(hit)})
            run = [k] if on else []
    ep = pd.DataFrame(out).sort_values("end").reset_index(drop=True)
    wave, w0, n = [], None, 0
    for _, r in ep.iterrows():
        if not r.event:
            wave.append(np.nan)
            continue
        if w0 is None or (r.end - w0).days > wave_gap_days:
            n += 1
            w0 = r.end
        wave.append(n)
    ep["wave"] = wave
    return ep


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else round(float(o), 5)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, pd.Timestamp):
        return str(o.date())
    return o
