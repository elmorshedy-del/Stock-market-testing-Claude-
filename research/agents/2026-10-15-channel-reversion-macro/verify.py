"""Checks with known answers. Exit code 1 if any fail.

V1  channel position at t does not change when every bar after t is scrambled (no look-ahead in the fit)
V2  every signal at t is unchanged when all macro data after t are deleted (no look-ahead in percentiles)
V3  publication lags: CPI YoY used at t is BLS month t-1; margin debt used at t is FINRA month t-1;
    net liquidity at t is from a Wednesday at least 2 days before t
V4  inventory signal at t comes only from filings dated on or before t, and filings lag period ends by >= 15 days
V5  outcome definition by hand on one case (NVDA, channel frozen at 2018-09): recompute the lower line and first touch
V6  null calibration: persistent random signals with no true effect give p < 0.05 about 5% of the time
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import tests as T
from channel_fit import fit_channel
from channels_panel import channel_rows

HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE / "out"
fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  {detail}" if detail else ""))
    if not ok:
        fails.append(name)


prices = pd.read_pickle(DATA / "monthly_prices.pkl")
ch, macro, inv = T.load()

# V1
rng = np.random.default_rng(1)
worst = 0.0
for sym in ("NVDA", "AMD", "CSCO", "^NDX"):
    mo = prices[prices.symbol == sym].sort_index()
    mo = mo[~mo.partial]
    lh, ll, lc = (np.log(mo[c].to_numpy(float)) for c in ("high", "low", "close"))
    full = {r[0]: r[6] for r in channel_rows(lh, ll, lc, len(lc), 84)}
    for i in rng.choice(np.arange(84, len(lc) - 5), 6, replace=False):
        perm = rng.permutation(np.arange(i + 1, len(lc)))
        lh2, ll2, lc2 = lh.copy(), ll.copy(), lc.copy()
        lh2[i + 1:], ll2[i + 1:], lc2[i + 1:] = lh[perm], ll[perm], lc[perm]
        z2 = {r[0]: r[6] for r in channel_rows(lh2[:i + 1], ll2[:i + 1], lc2[:i + 1], i + 1, 84)}[i]
        worst = max(worst, abs(z2 - full[i]))
check("V1 channel z ignores the future", worst < 1e-12, f"max |dz| = {worst:.2e}")

# V2
raw_full = T.raw_variables(macro, ch, 84)
invm = T.inv_monthly(inv, macro.index)
sig_full, _ = T.signals(raw_full, invm, 2 / 3)
worst = 0
for t in ("1999-12-31", "2008-06-30", "2018-09-30", "2021-11-30", "2025-01-31"):
    t = pd.Timestamp(t)
    m_cut = macro[macro.index <= t]
    ch_cut = ch[ch.month <= t]
    raw_cut = T.raw_variables(m_cut, ch_cut, 84)
    sig_cut, _ = T.signals(raw_cut, invm[invm.index <= t], 2 / 3)
    a, b = sig_full.loc[t].to_numpy(float), sig_cut.loc[t].to_numpy(float)
    worst += int(np.sum(~((a == b) | (np.isnan(a) & np.isnan(b)))))
check("V2 signals at t ignore data after t", worst == 0, f"{worst} mismatches over 5 dates x {sig_full.shape[1]} signals")

# V3
cpi = {}
for f in sorted((DATA / "bls").glob("cpi_*.json")):
    for r in json.loads(f.read_text())["Results"]["series"][0]["data"]:
        if r["value"] not in ("-", "") and r["period"] != "M13":
            cpi[(int(r["year"]), int(r["period"][1:]))] = float(r["value"])
t = pd.Timestamp("2022-07-31")                       # June 2022 CPI (released Jul 13) is what is known at end-July
exp = 100 * np.log(cpi[(2022, 6)] / cpi[(2021, 6)])
check("V3a CPI YoY at end-Jul-2022 is the June print", abs(macro.loc[t, "cpi_yoy"] - exp) < 1e-3,
      f"{macro.loc[t, 'cpi_yoy']:.3f} vs {exp:.3f}")
fin = pd.read_excel(DATA / "finra_margin.xlsx")
fin = fin.set_index(fin.columns[0])[fin.columns[1]].astype(float)
exp = 100 * np.log(fin["2021-10"] / fin["2020-10"])
check("V3b margin YoY at end-Nov-2021 is the October figure", abs(macro.loc["2021-11-30", "margin_yoy"] - exp) < 1e-3,
      f"{macro.loc['2021-11-30', 'margin_yoy']:.3f} vs {exp:.3f}")
import build_panel as BP
h41 = BP.fed_series("H41", ["RESPPMA_N.WW", "RESPPLLDT_N.WW", "RESPPLLRD_N.WW"])
w = pd.DataFrame(h41).dropna()
nl = (w.iloc[:, 0] - w.iloc[:, 1] - w.iloc[:, 2]) / 1000
t = pd.Timestamp("2022-09-30")                        # Friday; last Wednesday <= Sep 28 is Sep 28
check("V3c net liquidity at end-Sep-2022 is the Sep 28 Wednesday", abs(macro.loc[t, "netliq"] - nl[pd.Timestamp("2022-09-28")]) < 1e-6)

# V4
lag = (inv.known - inv.end).dt.days
check("V4a every inventory filing is at least 15 days after its period end", bool((lag >= 15).all()), f"min lag {lag.min()} days")
nv = inv[inv.symbol == "NVDA"].sort_values("known")
t = pd.Timestamp("2018-10-31")
used = invm.loc[t, "NVDA"]
expect = nv[nv.known <= t].inv_gap.iloc[-1]
check("V4b NVDA inventory gap at end-Oct-2018 is the Aug-2018 filing, not the Nov one", abs(used - expect) < 1e-9,
      f"{used:.2f} (filing {nv[nv.known <= t].known.iloc[-1].date()})")

# V5
mo = prices[prices.symbol == "NVDA"].sort_index()
mo = mo[~mo.partial]
i = mo.index.get_loc(pd.Timestamp("2018-09-30"))
lh, ll, lc = (np.log(mo[c].to_numpy(float)) for c in ("high", "low", "close"))
t_idx = np.arange(i - 83, i + 1, dtype=float)
a, b, lo, hi, r2 = fit_channel(lh[i - 83:i + 1], ll[i - 83:i + 1], lc[i - 83:i + 1], t_idx, 0.05)
first = None
for k in range(1, 37):
    if ll[i + k] <= a + b * (i + k) + lo:
        first = k
        break
row = ch[(ch.symbol == "NVDA") & (ch.W == 84) & (ch.month == "2018-09-30")].iloc[0]
same = (first is None and np.isnan(row.t_rev)) or (first == row.t_rev)
check("V5 hand-recomputed NVDA 2018 lower-line touch matches the panel", same,
      f"first touch {first} months later ({mo.index[i + first].date() if first else 'none'}); "
      f"lower line then {np.exp(a + b * (i + first) + lo) if first else float('nan'):.2f}, low {mo.low.iloc[i + first] if first else float('nan'):.2f}")

# V6: null calibration on the real base-spec rows with fake persistent signals
rows = T.rows_for(ch, T.BASE)
y = rows.y.to_numpy()
months = pd.date_range("1981-01-31", macro.index[-1], freq="ME")
draws = np.random.default_rng(7).uniform(0.1, 0.9, 200)
pv = []
for rep in range(200):
    g = np.random.default_rng(1000 + rep)
    x = np.zeros(len(months))
    for k in range(1, len(x)):                         # AR(1) monthly, phi 0.95 (like a macro series)
        x[k] = 0.95 * x[k - 1] + g.normal()
    s = pd.Series(x, index=months)
    sig = pd.Series(np.where(T.trailing_pct(s).isna(), np.nan, (T.trailing_pct(s) >= 2 / 3).astype(float)), index=months)
    si = T.ShiftIndex(sig)
    pos = si.positions(rows.month.to_numpy())
    obs = T.delta(y, si.values(pos, 0))
    null = np.array([T.delta(y, si.values(pos, f)) for f in draws])
    null = null[~np.isnan(null)]
    pv.append((1 + (null >= obs).sum()) / (1 + len(null)))
fp = float(np.mean(np.array(pv) < 0.05))
check("V6 circular-shift null: false-positive rate near 5%", 0.01 <= fp <= 0.10, f"{fp:.1%} of 200 no-effect signals at p < 0.05")

print("\n" + ("ALL PASS" if not fails else f"{len(fails)} FAILED: {fails}"))
sys.exit(1 if fails else 0)
