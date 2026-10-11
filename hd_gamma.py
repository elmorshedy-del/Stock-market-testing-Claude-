"""Daily dealer-gamma history per underlying from end-of-day option chains in the
HistoricalData.net CSV format (one file per day: day_by_date/YYYY-MM-DD_options.csv,
34 columns incl. open_interest, iv, iv_flag). The data stays outside the repo;
pass its folder on the command line.

Per underlying and day: net GEX / vanna / charm under both dealer conventions
(see options_flow.py), gamma flip (classic), near-term call/put walls, share of
gamma expiring within 1 and 5 trading days, put/call OI ratio.
Open interest in these files is the prior day's close (one-day lag), so a row
dated t describes positioning going INTO session t.

Usage: python hd_gamma.py <folder with day_by_date/> [out.csv]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from options_flow import exposures

COLS = ["underlying", "expiration", "type", "strike", "quote_date", "open_interest", "volume",
        "underlying_close", "settlement_time", "iv", "iv_flag"]
GROUPS = {"TSLA": ["TSLA"], "SPY": ["SPY"], "SPX": ["SPX", "SPXW"], "KO": ["KO"]}


def load_day(path):
    d = pd.read_csv(path, usecols=COLS, parse_dates=["expiration", "quote_date"])
    d = d[d.expiration > d.quote_date]                       # same-day expiries are gone after the close
    hours = np.where(d.settlement_time == "AM", 9.5, 16.0)
    d["T"] = ((d.expiration - d.quote_date).dt.days * 24 + hours - 16.0) / (365 * 24)
    d["T"] = d["T"].clip(lower=1 / (365 * 24))
    d["cp"] = np.where(d.type == "call", "C", "P")
    d["K"], d["oi"], d["exp"] = d.strike, d.open_interest.fillna(0), d.expiration.dt.date
    good = (d.iv_flag <= 1) & d.iv.between(0.03, 4)
    d["iv"] = d.iv.where(good)
    d["iv"] = d.iv.fillna(d.groupby(["underlying", "exp"]).iv.transform("median"))
    d["iv"] = d.iv.fillna(d.groupby("underlying").iv.transform("median"))
    return d.dropna(subset=["iv"])


def flip(g, S, lo=0.8, hi=1.2, n=81):
    grid = np.linspace(lo * S, hi * S, n)
    tot = np.array([exposures(g, s, "classic").gex.sum() for s in grid])
    sgn = np.sign(tot)
    xs = [i for i in range(n - 1) if sgn[i] != sgn[i + 1]]
    if not xs:
        return np.nan
    i = min(xs, key=lambda i: abs(grid[i] - S))
    return grid[i] - tot[i] * (grid[i + 1] - grid[i]) / (tot[i + 1] - tot[i])


def day_metrics(d, day, groups=None):
    rows = []
    for name, unds in (groups or GROUPS).items():
        g = d[d.underlying.isin(unds) & (d.oi > 0)]
        if g.empty:
            continue
        S = float(g.underlying_close.median())
        row = {"date": day, "und": name, "spot": S, "contracts": len(g),
               "call_oi": int(g[g.cp == "C"].oi.sum()), "put_oi": int(g[g.cp == "P"].oi.sum())}
        for conv in ("classic", "short"):
            e = exposures(g, S, conv)
            row[f"gex_{conv}"], row[f"vanna_{conv}"], row[f"charm_{conv}"] = e.gex.sum(), e.vanna.sum(), e.charm.sum()
        e = exposures(g, S, "classic")
        absg = e.gex.abs()
        tdays = np.busday_count(np.full(len(g), np.datetime64(day.date())), g.expiration.values.astype("datetime64[D]"))
        row["gamma_share_1d"] = absg[tdays <= 1].sum() / absg.sum()
        row["gamma_share_5d"] = absg[tdays <= 5].sum() / absg.sum()
        near = g[(g["T"] * 365 <= 45) & g.K.between(0.75 * S, 1.25 * S)]   # walls: strikes that can matter
        cn, pn = near[near.cp == "C"].groupby("K").oi.sum(), near[near.cp == "P"].groupby("K").oi.sum()
        row["call_wall"] = float(cn.idxmax()) if len(cn) else np.nan
        row["put_wall"] = float(pn.idxmax()) if len(pn) else np.nan
        row["flip_classic"] = flip(g, S)
        rows.append(row)
    return rows


def build(folder):
    files = sorted(Path(folder, "day_by_date").glob("*_options.csv"))
    rows = []
    for f in files:
        day = pd.Timestamp(f.name[:10])
        rows += day_metrics(load_day(f), day)
        print(day.date(), end=" ", flush=True)
    print()
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = sys.argv[2] if len(sys.argv) > 2 else "out/hd_gamma_daily.csv"
    m = build(sys.argv[1])
    m.to_csv(out, index=False)
    print(m.groupby("und")[["gex_classic", "gex_short", "flip_classic", "gamma_share_5d"]].describe().T.round(2).to_string())
