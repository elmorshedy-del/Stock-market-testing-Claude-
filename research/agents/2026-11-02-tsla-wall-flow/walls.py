"""TSLA gamma walls above 400 for the week of Nov 2 (positions = OI dated Oct 30 i.e. the Oct 29 close; IVs = Oct 30
closing chain; spot = Oct 30 close 399.81), plus where call OI was built during the Oct 26-27 burst.
Usage: python walls.py <td dir> -> out/walls.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "2026-10-27-flip-wicks"), str(HERE.parents[1] / "microstructure")]
from flipmap import norm, preopen, exposures, gex_at   # noqa: E402

td = Path(sys.argv[1]); S = 399.81; MON = pd.Timestamp("2026-11-02")
e = norm(pd.read_csv(td / "TSLA_eod_20261030.csv.gz")); e = e[e.date == pd.Timestamp("2026-10-30")]
oall = norm(pd.read_csv(td / "TSLA_oi_20261020_30.csv.gz"))
o30 = oall[oall.date == pd.Timestamp("2026-10-30")]   # preopen takes one OI date
g = preopen(e, o30, MON); g = g[g.expiration >= MON].copy(); g["underlying_close"] = S
ex = exposures(g, S)
byk = (ex.groupby("K").gex.sum() / 1e9)
up = byk[(byk.index > S) & (byk.index <= 470)].sort_values(ascending=False)
grid = np.linspace(380, 470, 181); tot = np.array([gex_at(g, s) for s in grid]) / 1e9
k45 = g[((g.expiration - MON).dt.days <= 45) & (g.K > S) & (g.K <= 470)]
coi = k45[k45.cp == "C"].groupby("K").oi.sum().sort_values(ascending=False)
# OI build during the burst: OI dated Oct 30 (Oct 29 close) minus OI dated Oct 26 (Oct 23 close), calls, strikes 400-470
def calls_on(d):
    x = oall[(oall.date == d) & (oall.cp == "C") & (oall.strike > 395) & (oall.strike <= 470)]
    return x.groupby("strike").open_interest.sum()
d_new, d_old = pd.Timestamp("2026-10-30"), pd.Timestamp("2026-10-26")
build = (calls_on(d_new) - calls_on(d_old).reindex(calls_on(d_new).index, fill_value=0)).sort_values(ascending=False)
byexp = k45[k45.cp == "C"].groupby([k45.expiration.dt.date, "K"]).oi.sum()
res = {"spot": S, "OI as of": "dated 2026-10-30 (positions at the Oct 29 close); Friday Oct 30 trading arrives in Monday's OI",
       "dealer gamma by strike above spot, $bn per 1% (top 8)": up.head(8).round(3).to_dict(),
       "largest call OI above spot, <=45 days (top 8, contracts)": coi.head(8).astype(int).to_dict(),
       "total dealer gamma curve: peak price": round(float(grid[np.argmax(tot)]), 1), "peak value $bn": round(float(tot.max()), 3),
       "total gamma at 400 / 410 / 420 / 430 / 440 / 450": [round(float(gex_at(g, s) / 1e9), 3) for s in (400, 410, 420, 430, 440, 450)],
       "call OI built Oct 23 close -> Oct 29 close (top 8)": build.head(8).astype(int).to_dict(),
       "call OI by expiry at 420/425/430/450": {str(k): {str(x): int(v) for x, v in byexp.xs(k, level=0).reindex([420, 425, 430, 450]).fillna(0).items()} for k in sorted({i[0] for i in byexp.index})[:5]}}
json.dump(res, open(HERE / "out" / "walls.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
pd.DataFrame({"price": grid, "total_gamma_bn": tot}).to_csv(HERE / "out" / "gamma_curve.csv", index=False)
byk[(byk.index >= 360) & (byk.index <= 470)].to_csv(HERE / "out" / "gamma_by_strike.csv")
