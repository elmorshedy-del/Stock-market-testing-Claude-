"""Follow-up for the owner (post hoc, descriptive): (1) how far the flip moves intraday from time decay alone
(same positions, IVs fixed; 0DTE time to expiry running down), Oct 13-28; (2) whether H1's stall effect holds on heavy-0DTE
days and Fridays (splits of the pre-registered H1 cell, labelled post hoc). Usage: python drift.py <spyg> <live27/td> <live28/td> <flipw>"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from flipmap import norm, preopen, fine_flip, t
from h1 import daily, run

HERE = Path(__file__).resolve().parent
spyg, td27, td28, flipw = map(Path, sys.argv[1:5])
eod = pd.concat([t.read("SPY", "eod")[lambda d: d.date >= "2026-10-08"], norm(pd.read_csv(spyg / "SPY_eod_1015_1023.csv.gz")),
                 norm(pd.read_csv(td27 / "SPY_eod_20261026.csv.gz")), norm(pd.read_csv(td27 / "SPY_eod_20261027.csv.gz"))]).drop_duplicates(subset=["date", "expiration", "strike", "cp"], keep="last")
oi = pd.concat([t.read("SPY", "oi")[lambda d: d.date >= "2026-10-08"], norm(pd.read_csv(spyg / "SPY_oi_1015_1023.csv.gz")), norm(pd.read_csv(spyg / "SPY_oi_20261026.csv.gz")),
                norm(pd.read_csv(td27 / "SPY_oi_20261027.csv.gz")), norm(pd.read_csv(td28 / "SPY_oi_20261028.csv.gz"))]).drop_duplicates(subset=["date", "expiration", "strike", "cp"], keep="last")
rows = []
for D in sorted(d for d in oi.date.unique() if d >= pd.Timestamp("2026-10-13")):
    P = max(x for x in eod.date.unique() if x < D)
    e = eod[eod.date == P]; ex_far = eod[(eod.date == eod[eod.date < P].date.max()) & ~eod.expiration.isin(e.expiration.unique())].assign(date=P)
    e = pd.concat([e, ex_far]); o = oi[oi.date == D]
    fl = {}
    for hm, hl in (("09:30", 6.5), ("12:00", 4.0), ("14:00", 2.0), ("15:00", 1.0), ("15:30", 0.5), ("15:45", 0.25), ("15:55", 1 / 12)):
        g = preopen(e, o, D, hours_left=hl); fl[hm] = round(fine_flip(g, float(g.underlying_close.median())), 2)
    has0 = bool((o.expiration == D).any())
    rows.append({"day": str(D.date()), "weekday": D.day_name()[:3], "0DTE expiry": has0, **fl, "drift 9:30->15:45": round(fl["15:45"] - fl["09:30"], 2), "drift 9:30->15:55": round(fl["15:55"] - fl["09:30"], 2)})
    print(rows[-1], flush=True)
dr = pd.DataFrame(rows)
# H1 splits (post hoc): heavy vs light 0DTE share at the open, and Fridays
lv = pd.read_csv(HERE / "out" / "preopen_levels.csv", parse_dates=["date"]).set_index("date")
df = lv.join(daily(flipw), how="inner").dropna(subset=["flip_incl", "open"]); df = df[df.index <= "2026-10-12"]
rng = np.random.default_rng(0)
q = df.share_0dte[df.has_0dte].quantile([1 / 3, 2 / 3]).to_numpy()
sp = {}
for lab, m in (("no 0DTE that day", ~df.has_0dte), ("0DTE share low third", df.has_0dte & (df.share_0dte <= q[0])), ("0DTE share high third", df.has_0dte & (df.share_0dte > q[1])),
               ("Fridays", df.index.dayofweek == 4), ("Mon-Thu", df.index.dayofweek < 4)):
    d = df[m]; s = rng.integers(20, max(21, len(d) - 20), 300)
    real, null = run(d, "flip_incl", s); out = {}
    for j, nm in enumerate(["up stall", "up reject", "down stall", "down hold"]):
        r0 = real[0.0015][0][j]; nl = null[0.0015][:, j]
        out[nm] = [round(float(r0), 3), round(float(np.nanmean(nl)), 3), round(float(np.mean(nl >= r0)), 3)]
    sp[lab] = {"days": int(len(d)), "events up/down": list(real[0.0015][1]), "real / null / p": out}
res = {"intraday flip drift (time decay only)": rows, "median drift 9:30->15:45 / ->15:55 ($)": [float(dr["drift 9:30->15:45"].median()), float(dr["drift 9:30->15:55"].median())],
       "max |drift| 9:30->15:45 / ->15:55 ($)": [float(dr["drift 9:30->15:45"].abs().max()), float(dr["drift 9:30->15:55"].abs().max())],
       "0DTE share tercile cut points": [round(float(x), 3) for x in q], "H1 band 0.15% splits (post hoc)": sp}
(HERE / "out" / "drift.json").write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != "intraday flip drift (time decay only)"}, indent=1))
