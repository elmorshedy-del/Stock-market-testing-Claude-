"""Re-check of the 2026-11-22 claim 'gold-S&P correlation rose from 0.11 to 0.46': confidence intervals, a test of the difference,
the volatility-bias adjustment (Forbes & Rigobon 2002), and weekly sampling to remove the asynchronous-close bias."""
import json
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parent
XA = H.parent / "2026-11-22-cross-asset" / "data" / "closes.csv"

def fz(r): return np.arctanh(r)
def ci(r, n): z = fz(r); s = 1 / np.sqrt(n - 3); return np.tanh(z - 1.96 * s), np.tanh(z + 1.96 * s)
def diff_p(r1, n1, r2, n2):
    z = (fz(r2) - fz(r1)) / np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3)); from math import erf, sqrt
    return z, 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))
def fr_adjust(r, var_ratio):
    """Forbes-Rigobon: correlation in a high-volatility window, rescaled to the calm window's volatility of the source market."""
    d = var_ratio - 1; return r / np.sqrt(1 + d * (1 - r ** 2))

if __name__ == "__main__":
    c = pd.read_csv(XA, index_col=0, parse_dates=True); c = c[c.SPX.notna()]
    out = {}
    for freq, lab in (("D", "daily"), ("W-FRI", "weekly")):
        x = c[["SPX", "GOLD", "BTC", "TLT"]].ffill().resample(freq).last() if freq != "D" else c[["SPX", "GOLD", "BTC", "TLT"]].ffill()
        r = np.log(x).diff().dropna()
        base, crisis = r.loc["2023-01-01":"2026-08-31"], r.loc["2026-10-06":"2026-11-20"]
        vr = crisis.SPX.var() / base.SPX.var()
        print(f"\n== {lab}: baseline n={len(base)}, phase 2 n={len(crisis)}; S&P variance ratio (phase 2 / baseline) = {vr:.2f}")
        for k in ["GOLD", "BTC", "TLT"]:
            r1 = base.SPX.corr(base[k]); r2 = crisis.SPX.corr(crisis[k]); radj = fr_adjust(r2, vr)
            z, p = diff_p(r1, len(base), r2, len(crisis)); za, pa = diff_p(r1, len(base), radj, len(crisis))
            lo1, hi1 = ci(r1, len(base)); lo2, hi2 = ci(r2, len(crisis))
            print(f"  {k:4s} baseline {r1:+.2f} [{lo1:+.2f},{hi1:+.2f}]   phase 2 {r2:+.2f} [{lo2:+.2f},{hi2:+.2f}]   diff p={p:.3f}"
                  f"   | volatility-adjusted phase 2 {radj:+.2f}, diff p={pa:.3f}")
            out[f"{lab}_{k}"] = dict(base=r1, base_ci=[lo1, hi1], n_base=len(base), crisis=r2, crisis_ci=[lo2, hi2], n_crisis=len(crisis),
                                     p_diff=p, vol_adjusted=radj, p_diff_adjusted=pa, var_ratio=vr)
    # how unusual is a 34-day gold-S&P correlation of +0.46? distribution of all 34-day windows since 2001
    x = c[["SPX", "GOLD"]].ffill(); r = np.log(x).diff().dropna()
    roll = r.SPX.rolling(34).corr(r.GOLD).dropna()
    full = pd.read_csv(H / "data" / "Y_SPX.csv", index_col=0, parse_dates=True).iloc[:, 0]
    g = pd.read_csv(H / "data" / "Y_GOLDF.csv", index_col=0, parse_dates=True).iloc[:, 0]
    rr = np.log(pd.concat([full, g], axis=1, keys=["SPX", "GOLD"]).dropna()).diff().dropna()
    roll_long = rr.SPX.rolling(34).corr(rr.GOLD).dropna()
    pct = (roll_long < out["daily_GOLD"]["crisis"]).mean()
    print(f"\nAll 34-day windows 2000-2026 (n={len(roll_long)}): gold-S&P correlation median {roll_long.median():+.2f}, 5-95% "
          f"[{roll_long.quantile(.05):+.2f}, {roll_long.quantile(.95):+.2f}]; phase 2's +0.46 is at the {100 * pct:.0f}th percentile")
    top = roll_long.resample("QE").max().nlargest(8)
    print("highest 34-day gold-S&P correlations by quarter:", {d.strftime("%Y-%m"): round(v, 2) for d, v in top.items()})
    out["percentile_34d_window"] = pct
    json.dump(out, open(H / "out" / "recheck.json", "w"), indent=1, default=float)
