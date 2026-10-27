"""Pre-open SPY gamma map for day D, built only from what is known before D's open:
positions = OI dated D (the prior close's positions), IVs and spot = the prior session P's closing chain.
Same-day (0DTE) expiries are kept, with T measured from a chosen time of day to the 16:00 expiry.
Engine code imported unchanged (td_gamma.chain_day, options_flow.exposures, hd_gamma.flip); the only addition is a
fine search ($0.05) inside the engine's coarse flip interval, because the engine grid is 0.5% (~$3.85) wide."""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MICRO = Path(__file__).resolve().parents[2] / "microstructure"
sys.path.insert(0, str(MICRO))
_c = os.getcwd(); os.chdir(MICRO)
import td_gamma as t                               # noqa: E402
from hd_gamma import flip as engine_flip           # noqa: E402
from options_flow import exposures                 # noqa: E402
os.chdir(_c)
KEY = ["expiration", "strike", "cp"]


def norm(d):
    dcol = next(c for c in ("date", "created", "timestamp") if c in d.columns)
    d = d.copy()
    d["date"] = pd.to_datetime(d[dcol].astype(str).str[:10])
    d["expiration"] = pd.to_datetime(d.expiration)
    d["cp"] = np.where(d.right.str.upper().str.startswith("C"), "C", "P")
    return d


def preopen(eod_P, oi_D, D, hours_left=6.5, keep_0dte=True):
    """eod_P: prior session's closing chain (normalized); oi_D: OI rows dated D. Returns the engine chain for day D."""
    e = eod_P.copy(); e["mid"] = (e.bid + e.ask) / 2
    g = t.chain_day(e.assign(oi=0.0)).drop(columns=["oi"])          # expiries > P, IVs from P's close
    oc = next(c for c in oi_D.columns if "open_interest" in c)
    g = g.merge(oi_D[KEY + [oc]].rename(columns={oc: "oi"}), on=KEY, how="left").fillna({"oi": 0})
    g = g[(g.expiration >= D) & ((g.expiration - D).dt.days <= t.MAX_DTE) & (g.oi > 0)].copy()
    if not keep_0dte:
        g = g[g.expiration > D]
    g["date"] = D
    g["T"] = (((g.expiration - D).dt.days + hours_left / 24) / 365).clip(lower=1 / (365 * 24 * 12))
    return g


def gex_at(g, s):
    return exposures(g, s, "classic").gex.sum()


def fine_flip(g, S, step=0.05):
    f0 = engine_flip(g, S)
    if not np.isfinite(f0):
        return np.nan
    grid = np.arange(f0 - 4.0, f0 + 4.0 + step, step)
    tot = np.array([gex_at(g, s) for s in grid])
    x = np.where(np.sign(tot[:-1]) != np.sign(tot[1:]))[0]
    if not len(x):
        return f0
    i = x[np.argmin(np.abs(grid[x] - f0))]
    return float(grid[i] - tot[i] * (grid[i + 1] - grid[i]) / (tot[i + 1] - tot[i]))
