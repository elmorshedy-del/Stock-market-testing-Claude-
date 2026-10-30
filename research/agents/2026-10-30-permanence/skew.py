"""Daily 30-day 25-delta risk reversal (call IV - put IV) and ATM IV from the local end-of-day chains (TSLA, NVDA, QQQ, MSFT, MU).
Engine smile (td_gamma.chain_day) on expiries 2-60 days; the expiry nearest 30 days (20-45); deltas from Black-Scholes at each strike's smile IV.
Usage: python skew.py -> out/skew.csv"""
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm as N

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm, t      # noqa: E402


def one_month(arg):
    sym, f = arg; out = []
    try:
        e = norm(pd.read_csv(f)); e["mid"] = (e.bid + e.ask) / 2
    except Exception:
        return out
    for d, g in e.groupby("date"):
        try:
            dte = (g.expiration - d).dt.days; g = g[(dte >= 2) & (dte <= 60)]
            c = t.chain_day(g); S = float(c.underlying_close.iloc[0]); dd = (c.expiration - d).dt.days
            cand = sorted(set(dd[(dd >= 20) & (dd <= 45)]), key=lambda x: abs(x - 30))
            if not cand: continue
            x = c[dd == cand[0]].copy(); T = cand[0] / 365
            d1 = (np.log(S / x.strike) + 0.5 * x.iv ** 2 * T) / (x.iv * np.sqrt(T))
            x["delta"] = np.where(x.cp == "C", N.cdf(d1), N.cdf(d1) - 1)
            cl = x[x.cp == "C"]; pu = x[x.cp == "P"]
            if not len(cl) or not len(pu): continue
            c25 = cl.iloc[(cl.delta - 0.25).abs().argsort()[:1]]; p25 = pu.iloc[(pu.delta + 0.25).abs().argsort()[:1]]
            atm = x.iloc[(x.strike - S).abs().argsort()[:2]].iv.mean()
            out.append({"sym": sym, "date": d, "spot": S, "iv_c25": float(c25.iv.iloc[0]), "iv_p25": float(p25.iv.iloc[0]), "rr25": float(c25.iv.iloc[0] - p25.iv.iloc[0]), "atm_iv": float(atm)})
        except Exception:
            continue
    return out


if __name__ == "__main__":
    jobs = [(s, f) for s in ("TSLA", "NVDA", "QQQ", "MSFT", "MU") for f in sorted(t.DIR.glob(f"{s}_*_eod.csv.gz"))]
    with Pool(3) as p:
        res = [r for L in p.imap_unordered(one_month, jobs, chunksize=2) for r in L]
    R = pd.DataFrame(res).sort_values(["sym", "date"]); R.to_csv(HERE / "out" / "skew.csv", index=False)
    print(R.groupby("sym").size().to_dict(), R.rr25.describe().round(3).to_dict())
