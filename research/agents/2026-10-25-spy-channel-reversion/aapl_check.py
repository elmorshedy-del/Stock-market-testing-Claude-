"""Post-hoc (not pre-registered): pullback odds when AAPL decouples from SPY, with a circular-shift luck check.
Usage: python aapl_check.py <data folder>  -> out/aapl_check.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import fingerprint as F

OUT = Path(__file__).resolve().parent / "out"
RNG = np.random.default_rng(20261026)


def main(folder):
    spx, S, P = F.signals(folder)
    m = (P.index >= F.START) & (P.index <= F.END)
    P, spxc, S = P[m], spx[m], S[m]
    idx = P.index
    F.MINOR = F.minor_tops(spxc)
    inside, ahead = np.zeros(len(idx), bool), np.zeros(len(idx), bool)
    for t, l in F.TOPS + F.MINOR:
        ti = idx.get_loc(pd.Timestamp(t))
        inside[ti + 1:idx.get_loc(pd.Timestamp(l)) + 1] = True
        ahead[max(0, ti - 29):ti + 1] = True
    ok = ~inside
    k = "A4 AAPL decoupling (20d corr with SPY low)"
    on = (P[k] >= 0.8).to_numpy()
    diff = lambda o: ahead[ok & o].mean() - ahead[ok & ~o].mean()
    obs = diff(on)
    null = np.array([diff(np.roll(on, s)) for s in RNG.integers(60, len(on) - 60, 2000)])
    corr = -S[k]
    res = {"pullback tops counted (3 major + 3 minor)": [t for t, _ in F.TOPS + F.MINOR],
           "share of non-reversion days with the alarm on": float(on[ok].mean()),
           "P(top within 30 sessions | on)": float(ahead[ok & on].mean()), "P(top within 30 | off)": float(ahead[ok & ~on].mean()),
           "base rate": float(ahead[ok].mean()), "difference": float(obs), "p (circular shift, one-sided)": float((null >= obs).mean()),
           "AAPL-SPY 20-day correlation in the 30 sessions before each top (min)": {
               t: float(corr.iloc[idx.get_loc(pd.Timestamp(t)) - 29:idx.get_loc(pd.Timestamp(t)) + 1].min()) for t, _ in F.TOPS + F.MINOR},
           "AAPL-SPY 20-day correlation, channel median": float(corr.median()), "today": float(corr.iloc[-1]),
           "today's percentile (past year)": float(P[k].iloc[-1])}
    (OUT / "aapl_check.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1))
