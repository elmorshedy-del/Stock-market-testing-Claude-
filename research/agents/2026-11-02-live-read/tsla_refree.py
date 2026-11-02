"""Can TSLA get 'freed' again soon? (map + descriptive history, not a test)
(a) Roll-off schedule: near-price OI share (OI within +-5% of spot in expiries <= 45 days / all OI <= 120 days, engine definition)
    now and after each expiry rolls off, assuming no new contracts (an upper bound on freeing), ranked vs the engine's trailing year.
(b) History 2021-26: after a freed spell ends, how soon does the next one start; freed odds by days to monthly opex.
Usage: python tsla_refree.py <td dir> -> out/tsla_refree.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; MICRO = HERE.parents[1] / "microstructure"
sys.path[:0] = [str(HERE.parent / "2026-10-27-flip-wicks")]
from flipmap import norm   # noqa: E402
td = Path(sys.argv[1]); MON = pd.Timestamp("2026-11-02"); S = 402.22
o = norm(pd.read_csv(td / "TSLA_oi_20261102.csv.gz")); c = [x for x in o.columns if "open_interest" in x or x == "oi"][0]
o["exp"] = pd.to_datetime(o.expiration); o = o[(o.exp >= MON) & (o.exp <= MON + pd.Timedelta(days=120))]
h = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
hist = h.near_oi_share.iloc[-251:]
def share(df, d, spot):
    near = df[(df.exp - d).dt.days.le(45) & df.strike.between(0.95 * spot, 1.05 * spot)][c].sum(); return float(near / df[c].sum())
exps = sorted(o.exp.unique()); res = {"expiries in file": [str(pd.Timestamp(e).date()) for e in exps]}
near_by = o[(o.exp - MON).dt.days.le(45) & o.strike.between(0.95 * S, 1.05 * S)].groupby("exp")[c].sum()
res["near-price OI by expiry (thousands, share of near total)"] = {str(pd.Timestamp(e).date()): [round(float(v / 1e3), 1), round(float(v / near_by.sum()), 3)] for e, v in near_by.items()}
steps = {}
for d, lab in [(MON, "now (Nov 2 OI)"), (pd.Timestamp("2026-11-03"), "after Mon Nov 2 expiry"), (pd.Timestamp("2026-11-05"), "after Wed Nov 4"), (pd.Timestamp("2026-11-09"), "after Fri Nov 6"),
               (pd.Timestamp("2026-11-16"), "after Fri Nov 13"), (pd.Timestamp("2026-11-23"), "after Fri Nov 20 (monthly)")]:
    x = o[o.exp >= d]
    for sp in (S, 420.0, 385.0):
        s = share(x, d, sp); steps.setdefault(lab, {})[f"at {sp:g}"] = [round(s, 4), round(float((hist < s).mean()), 3)]
res["near share and pct if nobody adds contracts [share, pct]"] = steps
# (b) history
p = h.near_oi_share.rolling(252, min_periods=120).rank(pct=True).dropna(); fr = p <= 1 / 3
ends = fr.index[(~fr) & fr.shift(1, fill_value=False)]; gaps = []
for e in ends:
    nxt = fr[(fr.index > e) & fr]
    if len(nxt): gaps.append(int(fr.index.get_loc(nxt.index[0]) - fr.index.get_loc(e)))
g = np.array(gaps)
res["after a freed spell ends: sessions until the next one (n, median, IQR, share <= 5 / <= 10 / <= 15)"] = [len(g), float(np.median(g)), [float(np.percentile(g, 25)), float(np.percentile(g, 75))],
    round(float((g <= 5).mean()), 2), round(float((g <= 10).mean()), 2), round(float((g <= 15).mean()), 2)]
def third_fri(y, m):
    d = pd.Timestamp(y, m, 1); return d + pd.Timedelta(days=(4 - d.weekday()) % 7 + 14)
opex = sorted({third_fri(d.year, d.month) for d in p.index} | {third_fri((d + pd.offsets.MonthBegin(1)).year, (d + pd.offsets.MonthBegin(1)).month) for d in p.index})
nxt = [min(x for x in opex if x >= d) for d in p.index]; dto = np.array([np.busday_count(d.date(), n.date()) for d, n in zip(p.index, nxt)])
tab = {}
for lo, hi, lab in [(0, 0, "opex day"), (1, 3, "1-3 sessions before"), (4, 8, "4-8 before"), (9, 13, "9-13 before"), (14, 25, "14+ before")]:
    m = (dto >= lo) & (dto <= hi); tab[lab] = [int(m.sum()), round(float(fr[m].mean()), 2)]
after = np.array([np.busday_count(max(x for x in opex if x <= d).date(), d.date()) if any(x <= d for x in opex) else 99 for d in p.index])
for lo, hi, lab in [(1, 3, "1-3 sessions after opex"), (4, 6, "4-6 after")]:
    m = (after >= lo) & (after <= hi); tab[lab] = [int(m.sum()), round(float(fr[m].mean()), 2)]
res["freed odds by position in the monthly cycle [days, P(freed)] (all days ~33%)"] = tab
json.dump(res, open(HERE / "out" / "tsla_refree.json", "w"), indent=1); print(json.dumps(res, indent=1))
