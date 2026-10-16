"""Round 2 fresh universe (non-tech large caps): download daily bars, build monthly bars and ex-ante channels.

Reuses the code of research/agents/2026-10-15-channel-reversion-macro (imported by path, not edited):
Yahoo download and monthly bars (fetch_data.curl, build_panel.load_yahoo/to_monthly), channel fit and
forward outcomes (channels_panel.frame_for, which uses the owner's fit_channel copied verbatim).

Usage: python build.py          -> data/yahoo/*.json, data/monthly_prices.pkl, data/channels.pkl, out/coverage.csv
"""
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
PREV = HERE.parent / "2026-10-15-channel-reversion-macro"
sys.path.insert(0, str(PREV))
import build_panel as BP          # noqa: E402
import channels_panel as CP       # noqa: E402
import fetch_data as FD           # noqa: E402

DATA, OUT = HERE / "data", HERE / "out"

# Frozen before any outcome was computed: large US non-tech names with long Yahoo histories, no overlap with the
# tech universe of the earlier study. Survivors only.
UNIVERSE = {
    "financials": ["JPM", "BAC", "WFC", "C", "GS", "MS", "AXP", "USB", "PNC", "BK", "AIG", "MET", "TRV", "ALL", "CB"],
    "industrials": ["CAT", "DE", "GE", "HON", "MMM", "BA", "LMT", "RTX", "UNP", "CSX", "NSC", "UPS", "FDX", "EMR",
                    "ETN", "ITW", "GD", "NOC"],
    "consumer_disc": ["HD", "LOW", "MCD", "NKE", "SBUX", "TGT", "TJX", "F", "MAR", "AZO", "DIS", "ROST"],
    "staples": ["KO", "PEP", "PG", "WMT", "COST", "CL", "KMB", "MO", "GIS", "SYY", "KR", "HSY"],
    "health": ["JNJ", "PFE", "MRK", "LLY", "ABT", "BMY", "AMGN", "UNH", "CVS", "MDT", "TMO", "DHR", "SYK", "BDX", "GILD"],
    "energy": ["XOM", "CVX", "COP", "SLB", "EOG", "OXY", "HAL"],
    "materials": ["APD", "SHW", "ECL", "NEM", "NUE", "PPG"],
    "utilities": ["NEE", "DUK", "SO", "D", "AEP"],
    "telecom_reit": ["T", "VZ", "SPG", "O"],
}
STOCKS = [s for v in UNIVERSE.values() for s in v]
assert not set(STOCKS) & set(FD.STOCKS), "overlap with the tech universe"


def _job(args):
    return CP.frame_for(*args)


def main():
    BP.DATA = DATA                     # point the reused loaders at this study's data/
    bad = []
    for s in STOCKS:
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?period1=0"
               f"&period2={int(time.time())}&interval=1d&includePrePost=false&events=div%2Csplit")
        try:
            FD.curl(url, DATA / "yahoo" / f"{s}.json")
        except RuntimeError as e:
            bad.append((s, str(e)[:60]))
        time.sleep(0.2)
    today = BP.load_yahoo("JPM").index[-1]
    frames, cov = [], []
    for s in STOCKS:
        if not (DATA / "yahoo" / f"{s}.json").exists():
            continue
        d = BP.load_yahoo(s)
        mo = BP.to_monthly(d, today)
        # dividend/distribution-adjusted bars: Yahoo's close is split-adjusted only, so spin-offs and special
        # dividends (MO 2008, KR 1988) show up as fake crashes; adjclose removes them
        f = mo.adjclose / mo.close
        mo[["high", "low", "close"]] = mo[["high", "low", "close"]].mul(f, axis=0)
        mo["symbol"] = s
        frames.append(mo)
        r = np.log(mo.close).diff()
        cov.append({"symbol": s, "first": d.index[0].date(), "last": d.index[-1].date(), "months": len(mo),
                    "max_abs_monthly_logret": round(float(r.abs().max()), 3)})
    prices = pd.concat(frames)
    prices.index.name = "month"
    prices.to_pickle(DATA / "monthly_prices.pkl")
    pd.DataFrame(cov).to_csv(OUT / "coverage.csv", index=False)
    by = {s: prices[prices.symbol == s] for s in prices.symbol.unique()}
    jobs = [(s, by[s], W) for s in by for W in CP.WINDOWS if len(by[s]) > W]
    with Pool(2) as pool:
        ch = pd.concat(pool.map(_job, jobs))
    ch.to_pickle(DATA / "channels.pkl")
    print("as of", today.date(), "| symbols", len(by), "| channel rows", len(ch), "| failed downloads", bad)


if __name__ == "__main__":
    main()
