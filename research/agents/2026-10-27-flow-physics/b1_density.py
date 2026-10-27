"""B1: risk-neutral distributions (Breeden-Litzenberger) from the Oct 27 closing chains, SPY and TSLA.
IVs: engine chain_day (OTM mids); smile smoothed in log-moneyness; density = e^{rT} d2C/dK2 on a fine grid.
Usage: python b1_density.py <live27/td>  -> out/b1.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm as normz, t                     # noqa: E402

R = t.R
LEVELS = {"SPY": [750, 760, 765, 770, 775, 780, 790, 800], "TSLA": [350, 375, 389, 400, 420, 450]}


def bs_call(S, K, T, s):
    d1 = (np.log(S / K) + (R + 0.5 * s * s) * T) / (s * np.sqrt(T)); d2 = d1 - s * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-R * T) * norm.cdf(d2)


def density(g, S, exp, width):
    x = g[(g.expiration == exp)].dropna(subset=["iv_otm"])
    T = float(x["T"].iloc[0]); F = S * np.exp(R * T)
    k = np.log(x.strike / F); m = (k.abs() <= width)
    pts = pd.DataFrame({"k": k[m], "iv": x.iv_otm[m]}).groupby("k").iv.median()
    spl = UnivariateSpline(pts.index, pts.values, k=3, s=len(pts) * (0.004 ** 2))
    K = np.linspace(F * np.exp(-width), F * np.exp(width), 2001)
    iv = np.clip(spl(np.log(K / F)), 0.03, 3.0)
    C = bs_call(S, K, T, iv)
    pdf = np.exp(R * T) * np.gradient(np.gradient(C, K), K); pdf = np.clip(pdf, 0, None)
    cdf = np.cumsum(pdf) * (K[1] - K[0]); mass = cdf[-1]; cdf = cdf / mass
    q = {f"q{int(100*p):02d}": float(np.interp(p, cdf, K)) for p in (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)}
    atm = float(np.interp(0.0, pts.index, pts.values))
    return T, F, atm, mass, q, K, cdf


if __name__ == "__main__":
    td = Path(sys.argv[1]); res = {}
    for sym, width in (("SPY", 0.15), ("TSLA", 0.45)):
        e = normz(pd.read_csv(td / f"{sym}_eod_20261027.csv.gz")); e["mid"] = (e.bid + e.ask) / 2
        g = t.chain_day(e.assign(oi=0.0)); S = float(g.underlying_close.median())
        out = {"spot (parity, Oct 27 close)": round(S, 2)}
        for exp in sorted(g.expiration.unique()):
            ex = pd.Timestamp(exp)
            if ex.strftime("%Y-%m-%d") not in ("2026-10-30", "2026-11-06", "2026-11-20"):
                continue
            T, F, atm, mass, q, K, cdf = density(g, S, ex, width)
            out[ex.strftime("%Y-%m-%d")] = {"days": round(T * 365, 1), "ATM IV": round(atm, 4), "implied 1-sd move %": round(100 * atm * np.sqrt(T), 2),
                                            "density mass (should be ~1)": round(mass, 3), "quantiles": {k: round(v, 2) for k, v in q.items()},
                                            "P(below level)": {str(L): round(float(np.interp(L, K, cdf)), 3) for L in LEVELS[sym]}}
        res[sym] = out
    (HERE / "out" / "b1.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
