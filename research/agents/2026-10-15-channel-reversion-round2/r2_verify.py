"""Round-2 checks with known answers. Exit code 1 if any fail.

W1  non-tech and S&P weekly channel positions ignore every bar after t
W2  weekly known-at rules: margin debt on a mid-July Friday is May's figure; net liquidity uses the Wednesday >= 2 days
    earlier; VIX_INVERT equals VIX / VIX3M on that Friday
W3  adjusted bars: MO's Mar-2008 spin-off and KR's Oct-1988 recapitalisation no longer show as crashes
W4  null calibration on the S&P weekly panel: persistent no-effect signals give p < 0.05 about 5% of the time
W5  the barrier formula matches a Monte Carlo of a driftless random walk (and with drift for the E7 formula)
"""
import sys

import numpy as np
import pandas as pd

import r2_lib as L
from channels_panel import channel_rows

DATA, OUT, PREV = L.DATA, L.OUT, L.PREV
fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  {detail}" if detail else ""))
    if not ok:
        fails.append(name)


# W1
rng = np.random.default_rng(3)
worst = 0.0
prices = pd.read_pickle(DATA / "monthly_prices.pkl")
wk = pd.read_pickle(DATA / "sp_weekly.pkl")
cases = [(prices[prices.symbol == s].sort_index(), 84) for s in ("XOM", "JPM", "WMT")] + [(wk, 156)]
for mo, W in cases:
    mo = mo[~mo.partial]
    lh, ll, lc = (np.log(mo[c].to_numpy(float)) for c in ("high", "low", "close"))
    full = {r[0]: r[6] for r in channel_rows(lh, ll, lc, len(lc), W)}
    for i in rng.choice(np.arange(W, len(lc) - 5), 5, replace=False):
        z2 = {r[0]: r[6] for r in channel_rows(lh[:i + 1], ll[:i + 1], lc[:i + 1], i + 1, W)}[i]
        worst = max(worst, abs(z2 - full[i]))
check("W1 channel z ignores the future (non-tech monthly, S&P weekly)", worst < 1e-12, f"max |dz| = {worst:.1e}")

# W2
m = pd.read_csv(OUT / "sp_macro_weekly.csv", parse_dates=["week"], index_col="week")
fin = pd.read_excel(PREV / "data" / "finra_margin.xlsx")
fin = fin.set_index(fin.columns[0])[fin.columns[1]].astype(float)
exp = 100 * np.log(fin["2022-05"] / fin["2021-05"])
got = m.loc["2022-07-15", "MARGIN_FROTH"]
check("W2a margin YoY on Fri 2022-07-15 is May's figure", abs(got - exp) < 1e-3, f"{got:.3f} vs {exp:.3f}")
import build_panel as BP
BP.DATA = PREV / "data"
h41 = BP.fed_series("H41", ["RESPPMA_N.WW", "RESPPLLDT_N.WW", "RESPPLLRD_N.WW"])
w = pd.DataFrame(h41).dropna()
nl = (w.iloc[:, 0] - w.iloc[:, 1] - w.iloc[:, 2]) / 1000
exp = -np.log(nl[pd.Timestamp("2022-09-28")] / nl[nl.index <= pd.Timestamp("2022-09-30") - pd.Timedelta(days=184)].iloc[-1])
got = m.loc["2022-09-30", "LIQ_DRAIN"]
check("W2b net liquidity change on Fri 2022-09-30 uses Wed Sep 28", abs(got - exp) < 1e-5,  # CSV keeps 5 decimals
      f"{got:.5f} vs {exp:.5f}")
BP.DATA = DATA
v3 = BP.load_yahoo("VIX3M").adjclose
BP.DATA = PREV / "data"
v = BP.load_yahoo("^VIX").adjclose
d = pd.Timestamp("2020-03-20")
check("W2c VIX_INVERT on Fri 2020-03-20 = VIX / VIX3M", abs(m.loc[d, "VIX_INVERT"] - v[d] / v3[d]) < 1e-4,
      f"{m.loc[d, 'VIX_INVERT']:.4f}")

# W3
p = prices
ok = True
for s, mth in (("MO", "2008-03-31"), ("KR", "1988-10-31")):
    g = p[p.symbol == s].sort_index()
    r = np.log(g.close).diff().loc[mth]
    ok &= abs(r) < 0.3
check("W3 spin-off / special-dividend months are no longer fake crashes", ok)

# W4
spch = pd.read_pickle(DATA / "sp_channels.pkl")
rs = L.rows(spch, ["^GSPC"], 156, 0.5, 26, key="week")
weeks = m.index[m.index >= "1955-01-01"]
draws = np.random.default_rng(5).uniform(0.1, 0.9, 200)
pv = []
for rep in range(200):
    g = np.random.default_rng(2000 + rep)
    x = np.zeros(len(weeks))
    for k in range(1, len(x)):
        x[k] = 0.99 * x[k - 1] + g.normal()
    s = L.signal(pd.Series(x, index=weeks), win=260, minp=104)
    pv.append(L.p_one_sided(L.shift_deltas(rs, s, draws)))
fp = float(np.nanmean(np.array(pv) < 0.05))
check("W4 S&P weekly shift null: false positives near 5%", 0.01 <= fp <= 0.10, f"{fp:.1%} of 200 no-effect signals at p < 0.05")

# W5
g = np.random.default_rng(9)
n, steps, H = 20000, 24 * 40, 24
dt = H / steps
for x0, mdrift, sig in ((0.4, 0.0, 0.08), (0.4, -0.006, 0.08)):
    paths = x0 + np.cumsum(mdrift * dt + sig * np.sqrt(dt) * g.standard_normal((n, steps)), axis=1)
    mc = (paths.min(axis=1) <= 0).mean()
    import r2_explore as E
    f = float(E.p_drift(x0, mdrift, sig, H)) if mdrift else float(L.p_barrier(x0, sig, H))
    check(f"W5 barrier formula vs Monte Carlo (drift {mdrift})", abs(mc - f) < 0.02, f"MC {mc:.3f} vs formula {f:.3f}")

print("\n" + ("ALL PASS" if not fails else f"{len(fails)} FAILED: {fails}"))
sys.exit(1 if fails else 0)
