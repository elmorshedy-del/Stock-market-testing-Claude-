"""B4 first-passage (reflection principle) calibration test; B5 lasting-burst confirmation test. Pre-registered @ bdc698c.
Usage: python b4_b5.py <ladder27 folder> <flipw folder (SPY_1d.json)>  -> out/b4.json, out/b5.json"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
MICRO = HERE.parents[1] / "microstructure"
fresh, flipw = sys.argv[1], Path(sys.argv[2])
sys.path.insert(0, str(MICRO))
import common                                           # noqa: E402
common.DATA = Path(fresh) / "data"
_c = os.getcwd(); os.chdir(fresh)
from forecast import build                              # noqa: E402
f = build(); os.chdir(_c)
from common import load_bars                            # noqa: E402


def touch_test(close, low, sig_d, xs, Ns, start, end):
    c, lo, s = close.to_numpy(), low.to_numpy(), sig_d.to_numpy(); d = close.index
    ok = (d >= start) & (d <= end)
    out = {}
    for x in xs:
        a = -np.log(1 - x)
        for N in Ns:
            pr, rl = [], []
            for i in np.where(ok)[0]:
                if i + N >= len(c) or not np.isfinite(s[i]): continue
                pr.append(2 * norm.cdf(-a / (s[i] * np.sqrt(N))))
                rl.append(float(lo[i + 1:i + N + 1].min() <= c[i] * (1 - x)))
            pr, rl = np.array(pr), np.array(rl)
            bins = np.quantile(pr, np.linspace(0, 1, 11)); b = np.clip(np.digitize(pr, bins[1:-1]), 0, 9)
            mp = np.array([pr[b == k].mean() for k in range(10)]); mr = np.array([rl[b == k].mean() for k in range(10)])
            slope = float(np.polyfit(mp, mr, 1)[0])
            brier = np.mean((pr - rl) ** 2); base = np.mean((rl.mean() - rl) ** 2)
            out[f"-{x:.1%} within {N}d"] = {"n": int(len(pr)), "mean predicted": round(float(pr.mean()), 3), "realized": round(float(rl.mean()), 3),
                                          "calibration slope": round(slope, 3), "Brier skill": round(float(1 - brier / base), 3),
                                          "usable (slope 0.8-1.2 and skill>0)": bool(0.8 <= slope <= 1.2 and brier < base)}
    return out


res = {}
g = load_bars("^GSPC"); g = g[g.index >= "2011-01-01"]
vix = f.VIX.reindex(g.index).ffill()
res["SPX, sigma = VIX (pre-registered)"] = touch_test(g.close, g.low, vix / 100 / np.sqrt(252), [0.01, 0.02, 0.03], [5, 10], "2012-01-01", "2026-10-12")
rv = np.log(g.close).diff().rolling(20).std()
res["SPX, sigma = 20d realized vol (post hoc comparison)"] = touch_test(g.close, g.low, rv, [0.01, 0.02, 0.03], [5, 10], "2012-01-01", "2026-10-12")
tl = load_bars("TSLA"); tl = tl[tl.index >= "2021-01-01"]
m = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
iv = m.atm_iv_30d.reindex(tl.index).ffill()
res["TSLA, sigma = own 30d ATM IV (registered levels)"] = touch_test(tl.close, tl.low, iv / np.sqrt(252), [0.01, 0.02, 0.03], [5, 10], "2021-03-01", "2026-10-14")
res["TSLA, sigma = own 30d ATM IV (TSLA-sized levels, added)"] = touch_test(tl.close, tl.low, iv / np.sqrt(252), [0.03, 0.05, 0.08], [5, 10], "2021-03-01", "2026-10-14")
(HERE / "out" / "b4.json").write_text(json.dumps(res, indent=1))
for k, v in res.items():
    print(k)
    for kk, vv in v.items():
        print(f"   {kk:16s} n {vv['n']} pred {vv['mean predicted']:.3f} real {vv['realized']:.3f} slope {vv['calibration slope']:+.2f} skill {vv['Brier skill']:+.3f} usable {vv['usable (slope 0.8-1.2 and skill>0)']}")

# ---------------- B5
r = json.loads((flipw / "SPY_1d.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
spy = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
spy = spy[~spy.index.duplicated(keep="last")]
lv = pd.read_csv(HERE.parent / "2026-10-27-flip-wicks" / "out" / "preopen_levels.csv", parse_dates=["date"]).set_index("date")
d = spy.join(lv[["flip_incl"]], how="left").join(f[["gex_pct"]], how="left")
d = d[(d.index >= "2020-01-03") & (d.index <= "2026-10-12")].copy()
c = d.close.to_numpy(); n = len(d)
fwd10 = np.r_[c[10:] / c[:-10] - 1, np.full(10, np.nan)]
hi20 = d.close.rolling(20).max().to_numpy()
fh = np.full(n, np.nan)
for i in range(n - 1):
    w = c[i + 1:i + 21]
    u = np.where(w > hi20[i])[0]; dn = np.where(w <= c[i] * 0.97)[0]
    fu = u[0] if len(u) else 10**9; fd = dn[0] if len(dn) else 10**9
    if fu < 10**9 or fd < 10**9: fh[i] = float(fu < fd)
    if i + 20 >= n: fh[i] = np.nan
near = (d.close / d.close.rolling(252, min_periods=120).max() >= 0.98).to_numpy()
conf = ((d.close > d.flip_incl) & (d.gex_pct < 0.90)).to_numpy()
valid = near & np.isfinite(d.flip_incl.to_numpy()) & np.isfinite(d.gex_pct.to_numpy())


def stat(cf):
    a = valid & cf; b = valid & ~cf
    return (np.nanmean(fwd10[a]) - np.nanmean(fwd10[b]), np.nanmean(fh[a]) - np.nanmean(fh[b]))


real = stat(conf)
rng = np.random.default_rng(0); shifts = rng.integers(20, n - 20, 1000)
null = np.array([stat(np.roll(conf, k)) for k in shifts])
a = valid & conf; b = valid & ~conf
res5 = {"universe": "SPY days within 2% of 252d high, 2020-01-03 to 2026-10-12", "days in universe": int(valid.sum()), "confirmed days": int(a.sum()),
        "fwd 10d %: confirmed / not": [round(100 * float(np.nanmean(fwd10[a])), 3), round(100 * float(np.nanmean(fwd10[b])), 3)],
        "diff pts": round(100 * real[0], 3), "p (shift null)": round(float(np.mean(null[:, 0] >= real[0])), 4),
        "P(new 20d high before -3%): confirmed / not": [round(float(np.nanmean(fh[a])), 3), round(float(np.nanmean(fh[b])), 3)],
        "diff": round(real[1], 3), "p (shift null) ": round(float(np.mean(null[:, 1] >= real[1])), 4)}
res5["passes (both p < 0.05)"] = bool(res5["p (shift null)"] < 0.05 and res5["p (shift null) "] < 0.05)
# components (descriptive)
for lab, cf in (("close above flip only", (d.close > d.flip_incl).to_numpy()), ("GEX < 90th only", (d.gex_pct < 0.90).to_numpy())):
    s = stat(cf); res5[f"component: {lab}"] = {"diff fwd10 pts": round(100 * s[0], 3), "diff P(high first)": round(s[1], 3), "confirmed days": int((valid & cf).sum())}
res5["today (Oct 27)"] = "SPY close 769.72 vs pre-open flip 770.34 -> NOT confirmed (0.08% under); GEX pct 0.255 (not pinned)"
(HERE / "out" / "b5.json").write_text(json.dumps(res5, indent=1))
print(json.dumps(res5, indent=1))
