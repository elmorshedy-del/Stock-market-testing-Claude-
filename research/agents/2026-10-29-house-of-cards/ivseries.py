"""Daily 30-day ATM implied vol and call/put contract volume from the local end-of-day chains (TSLA, NVDA, QQQ, MSFT, MU; 2020-01 to 2026-10).
ATM IV: expiry nearest 30 days (20-45), strikes within +-3% of the parity spot, median IV of OTM-or-ATM calls and puts with two-sided quotes.
Usage: python ivseries.py -> out/ivseries.csv"""
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm, t      # noqa: E402


def one_month(arg):
    sym, f = arg; out = []
    try:
        e = norm(pd.read_csv(f)); e["mid"] = (e.bid + e.ask) / 2
    except Exception as ex:
        return [{"sym": sym, "err": str(ex)[:60], "file": f.name}]
    for d, g in e.groupby("date"):
        try:
            S = t.spot_from_parity(g)
            if not np.isfinite(S): continue
            dte = (g.expiration - d).dt.days
            cand = sorted(set(dte[(dte >= 20) & (dte <= 45)]), key=lambda x: abs(x - 30))
            iv = np.nan
            if cand:
                x = g[(dte == cand[0]) & g.strike.between(0.97 * S, 1.03 * S) & (g.bid > 0) & (g.ask > g.bid)]
                if len(x):
                    v = t.implied_vol(x.mid.to_numpy(), S, x.strike.to_numpy(), np.full(len(x), cand[0] / 365), (x.cp == "C").to_numpy())
                    iv = float(np.nanmedian(v)) if np.isfinite(v).any() else np.nan
            out.append({"sym": sym, "date": d, "spot": S, "atm_iv30": iv, "call_vol": float(g[g.cp == "C"].volume.sum()), "put_vol": float(g[g.cp == "P"].volume.sum())})
        except Exception:
            continue
    return out


if __name__ == "__main__":
    jobs = [(s, f) for s in ("TSLA", "NVDA", "QQQ", "MSFT", "MU") for f in sorted(t.DIR.glob(f"{s}_*_eod.csv.gz"))]
    with Pool(3) as p:
        res = [r for L in p.imap_unordered(one_month, jobs, chunksize=2) for r in L]
    R = pd.DataFrame(res); R = R[R.get("err").isna()] if "err" in R else R
    R.drop(columns=[c for c in ("err", "file") if c in R], errors="ignore").sort_values(["sym", "date"]).to_csv(HERE / "out" / "ivseries.csv", index=False)
    print(R.groupby("sym").size().to_dict(), R.atm_iv30.notna().mean())
