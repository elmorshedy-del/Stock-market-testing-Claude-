"""Follow-up (owner: the flip and heavy expiry clusters - end of month, big weeklies). Post hoc, descriptive.
(1) This week, positions fixed (OI dated Oct 28 = Oct 27 close), IVs fixed: the flip and gamma mix from Thu to after the Oct 30 expiry.
(2) History 2020-Oct 2026: how much the pre-open flip jumps across expiries, by how much gamma expired.
(3) Does the flip's stall effect (H1, band 0.15%) hold in weeks with a big expiry cluster? (engine gamma_share_5d)
Usage: python expiry_cycle.py <live28/td> <live27/td> <flipw>  -> out/expiry_cycle.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from flipmap import norm, preopen, fine_flip, gex_at, exposures, t
from h1 import daily, run

HERE = Path(__file__).resolve().parent
td28, td27, flipw = map(Path, sys.argv[1:4])
res = {}
# (1) this week
for sym, S in (("SPY", 772.35), ("TSLA", 404.46)):
    e = norm(pd.read_csv(td27 / f"{sym}_eod_20261027.csv.gz")); e = e[e.date == pd.Timestamp("2026-10-27")]
    far = norm(pd.read_csv(td27 / f"{sym}_eod_20261026.csv.gz")); far = far[~far.expiration.isin(e.expiration.unique())].assign(date=pd.Timestamp("2026-10-27"))
    e = pd.concat([e, far]); o = norm(pd.read_csv(td28 / f"{sym}_oi_20261028.csv.gz"))
    path = {}
    for lab, D, hl in (("Thu 09:30", "2026-10-29", 6.5), ("Thu 15:45", "2026-10-29", 0.25), ("Fri 09:30", "2026-10-30", 6.5), ("Fri 12:00", "2026-10-30", 4.0),
                       ("Fri 15:00", "2026-10-30", 1.0), ("Fri 15:45", "2026-10-30", 0.25), ("Mon 09:30 (Oct 30 gone)", "2026-11-02", 6.5)):
        g = preopen(e, o, pd.Timestamp(D), hours_left=hl); g["underlying_close"] = S
        ex = exposures(g, S); a = ex.gex.abs()
        k = ex.groupby("K").gex.sum() / 1e9
        path[lab] = {"flip": round(fine_flip(g, S), 2), "total gamma at today's close $bn/1%": round(float(ex.gex.sum() / 1e9), 2),
                     "Oct 30 share of |gamma|": round(float(a[ex.exp == pd.Timestamp("2026-10-30").date()].sum() / a.sum()), 3),
                     "biggest +strike": [float(k.idxmax()), round(float(k.max()), 3)], "biggest -strike": [float(k.idxmin()), round(float(k.min()), 3)]}
    res[f"(1) {sym} this week, positions fixed"] = path
    print(sym, json.dumps(path, indent=1), flush=True)
# (2) flip jumps across expiries
lv = pd.read_csv(HERE / "out" / "preopen_levels.csv", parse_dates=["date"]).set_index("date")
lv = lv[lv.index <= "2026-10-12"].copy()
lv["jump %"] = 100 * (lv.flip_incl.shift(-1) / lv.flip_incl - 1)                     # tomorrow's pre-open flip vs today's
lv["expiring share"] = lv.share_0dte                                                 # share of |gamma| expiring today (at the open)
third = lambda d: (d.weekday() == 4) and (15 <= d.day <= 21)
lv["monthly opex"] = [third(d) for d in lv.index]
lv["month end"] = [(d + pd.offsets.BDay(1)).month != d.month for d in lv.index]
z = lv.dropna(subset=["jump %"])
bins = pd.cut(z["expiring share"], [-0.01, 0.0001, 0.15, 0.25, 0.35, 1.0], labels=["none", "<15%", "15-25%", "25-35%", ">35%"])
res["(2) |flip jump to next day| % by share of gamma expiring that day"] = {str(b): {"days": int(len(x)), "median |jump| %": round(float(x["jump %"].abs().median()), 3), "90th pct |jump| %": round(float(x["jump %"].abs().quantile(0.9)), 3)}
                                                                          for b, x in z.groupby(bins, observed=True)}
res["(2) median |jump| %: monthly opex / month-end / other days"] = [round(float(z[z["monthly opex"]]["jump %"].abs().median()), 3), round(float(z[z["month end"]]["jump %"].abs().median()), 3),
                                                                    round(float(z[~z["monthly opex"] & ~z["month end"]]["jump %"].abs().median()), 3)]
# (3) H1 in big-expiry-cluster weeks (engine gamma_share_5d = share of |gamma| expiring within 5 trading days, prior close)
eng = pd.read_csv(t.OUT / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")
df = lv.join(daily(flipw), how="inner").dropna(subset=["flip_incl", "open"])
df["g5"] = eng.gamma_share_5d.shift(1).reindex(df.index)
df = df.dropna(subset=["g5"])
q = df.g5.quantile([1 / 3, 2 / 3]).to_numpy()
rng = np.random.default_rng(0); sp = {}
for lab, m in (("light cluster (5-day share low third)", df.g5 <= q[0]), ("heavy cluster (5-day share high third)", df.g5 > q[1]),
               ("3 sessions before a monthly opex", pd.Series([any(third(d + pd.offsets.BDay(k)) for k in (1, 2, 3)) for d in df.index], index=df.index)),
               ("day after monthly opex", pd.Series([third(d - pd.offsets.BDay(1)) for d in df.index], index=df.index))):
    d = df[m.to_numpy()]; s = rng.integers(20, max(21, len(d) - 20), 300)
    real, null = run(d, "flip_incl", s); out = {}
    for j, nm in enumerate(["up stall", "up reject", "down stall", "down hold"]):
        r0 = real[0.0015][0][j]; nl = null[0.0015][:, j]
        out[nm] = [round(float(r0), 3), round(float(np.nanmean(nl)), 3), round(float(np.mean(nl >= r0)), 3)]
    sp[lab] = {"days": int(len(d)), "reach events up/down": list(real[0.0015][1]), "real / null / p": out}
res["(3) H1 (band 0.15%) by expiry-cluster state, post hoc"] = sp
res["(3) 5-day share cut points"] = [round(float(x), 3) for x in q]
(HERE / "out" / "expiry_cycle.json").write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if not k.startswith("(1)")}, indent=1))
