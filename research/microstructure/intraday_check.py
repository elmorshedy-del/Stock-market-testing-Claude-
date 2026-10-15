"""Today-so-far snapshot from Yahoo's live option chains (REPORT 4ae, intraday block).
End-of-day option data (ThetaData) only exists after the close; during the session this uses Yahoo's
chain: live quotes and today's volume per contract. Its open interest is the prior close's positions,
the same as ThetaData's same-day OI.
For each symbol:
  * own gamma flip and dealer gamma at the live price, now and with the next monthly expiry removed
  * near-price OI share (+-5%, expiries <= 45 days) against the stock's own trailing year
  * 30-day ATM IV now vs the last close
  * where today's volume is going: top strikes, call/put volume, volume vs open interest
Snapshots are written to the scratch folder given (never over data/*_options.json, which is tracked).
Usage: python intraday_check.py SCRATCH_DIR 2026-10-16 TSLA MSFT SPY
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import fetch
import options_flow as of
from common import OUT


def snapshot(sym, folder):
    fetch.DATA = Path(folder)
    fetch.options(sym)
    of.DATA = Path(folder)
    return of.load_chain(sym)


def profile_flip(df, S):
    grid, tot, flips = of.gex_profile(df, S, "classic", lo=0.8, hi=1.2, n=161)
    near = [f for f in flips if abs(f / S - 1) <= 0.2]
    return (min(near, key=lambda f: abs(f - S)) if near else np.nan), float(np.interp(S, grid, tot))


def check(sym, folder, expiry):
    S, t0, q, df = snapshot(sym, folder)
    df = df[(df["T"] * 365 <= 120) & (df.oi > 0)].copy()
    out = {"sym": sym, "price": S, "time": pd.Timestamp(t0, unit="s", tz="UTC").tz_convert("America/New_York").strftime("%H:%M ET")}
    exp = pd.Timestamp(expiry).date()
    for lab, x in (("now", df), (f"after {expiry}", df[df.exp > exp])):
        f, g = profile_flip(x, S)
        near = x[(x["T"] * 365 <= 45) & (np.abs(x.K / S - 1) <= 0.05)].oi.sum() / x.oi.sum()
        out[lab] = {"flip": f, "% vs flip": 100 * (S / f - 1) if f == f else np.nan, "dealer gamma $M per 1%": g / 1e6, "near-OI share": near}
    try:
        m = pd.read_csv(OUT / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date")
        if "near_oi_share" in m:
            h = m.near_oi_share.iloc[-251:]
            for lab in ("now", f"after {expiry}"):
                out[lab]["near-OI pct"] = float((h < out[lab]["near-OI share"]).mean())
            a30 = df[(df["T"] * 365).between(20, 45)]
            out["ATM IV 30d now"] = float(a30.iloc[(a30.K - S).abs().argsort()[:4]].iv.median())
            out["ATM IV 30d last close"] = float(m.atm_iv_30d.iloc[-1])
    except FileNotFoundError:
        pass
    v = df[df.vol > 0]
    out["call volume"], out["put volume"] = int(v[v.cp == "C"].vol.sum()), int(v[v.cp == "P"].vol.sum())
    out[f"share of volume expiring by {expiry}"] = float(v[v.exp <= exp].vol.sum() / max(v.vol.sum(), 1))
    top = v.groupby(["K", "cp"]).agg(vol=("vol", "sum"), oi=("oi", "sum")).sort_values("vol", ascending=False).head(8)
    top["vol/oi"] = top.vol / top.oi.replace(0, np.nan)
    out["top strikes by volume"] = [f"{int(k) if k == int(k) else k}{cp}: vol {int(r.vol):,} (oi {int(r.oi):,}, {r['vol/oi']:.2f}x)"
                                    for (k, cp), r in top.iterrows()]
    return out


if __name__ == "__main__":
    folder, expiry, *syms = sys.argv[1:]
    res = [check(s, folder, expiry) for s in syms]
    (Path(folder) / "intraday_check.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))
