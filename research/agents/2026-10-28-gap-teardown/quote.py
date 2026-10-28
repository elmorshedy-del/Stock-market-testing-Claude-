"""Cost estimate for the full VF + SC pull (Amendment 3 rule: all VF + SC if it fits $32). Quotes a random 60 events (seed 0)
for trades 04:00-10:35, mbp-10 09:25-10:35 and imbalance 09:20-09:31, then scales by symbol-year means. Usage: python quote.py <key>"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import databento as db
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
c = db.Historical(sys.argv[1])
ev = pd.read_csv(HERE / "out" / "events.csv", parse_dates=["date"])
vs = ev[ev.cls.isin(["VF", "SC"])]
q = vs.sample(60, random_state=0)
et = lambda d, hm: pd.Timestamp(f"{d.date()} {hm}", tz="America/New_York").tz_convert("UTC")


def cost(r):
    tot = 0
    for s, a, b in [("trades", "04:00", "10:35"), ("mbp-10", "09:25", "10:35"), ("imbalance", "09:20", "09:31")]:
        for k in range(5):
            try:
                tot += c.metadata.get_cost(dataset="XNAS.ITCH", symbols=[r.sym], schema=s, start=et(r.date, a), end=et(r.date, b)); break
            except Exception:
                time.sleep(4 * (k + 1))
        else:
            return np.nan
    return tot


with ThreadPoolExecutor(4) as ex:
    q = q.assign(cost=list(ex.map(cost, list(q.itertuples()))))
print("quoted", int(q.cost.notna().sum()), "of 60"); q = q.dropna(subset=["cost"]); q["yr"] = q.date.dt.year
print(q.groupby("sym").cost.agg(["mean", "count"]).round(3).to_dict())
by = q.groupby("sym").cost.mean()
est_vs = float(vs.sym.map(by).sum()); est_mid = float(ev[ev.cls == "mid"].sym.map(by).mean() * 120)
print("mean per event $", round(q.cost.mean(), 4), " est all VF+SC $", round(est_vs, 2), " est 120 mid $", round(est_mid, 2))
