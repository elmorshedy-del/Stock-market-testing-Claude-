"""What follows a weak Monday-Thursday into monthly expiry? (REPORT 4ae addendum)
For every monthly expiry week: the Monday-Thursday return (prior Friday close -> Thursday close), the
expiry-Friday return, and the next one and two weeks. Weeks are grouped by how weak Mon-Thu was, against
all expiry weeks, with a luck check (random sets of the same size). The S&P uses the index (^GSPC):
SPY's closes carry its quarterly dividend drop, which lands on expiry Friday in Mar/Jun/Sep/Dec.
Big day = more than one standard deviation of the prior 20 sessions. History starts in 1983, when index
options began (from 1970 the effects fade, which fits an options mechanism); see REPORT 4ae for by-era rows.
Usage: python expiry_week.py 2026-10-15 "^GSPC=7811.54,7727.5" "QQQ=751.27,724.5" "TSLA=382.70,362.5" "MSFT=535.07,537.9"
       (as-of date, then SYMBOL=prior Friday close,current price)
"""
import sys

import numpy as np
import pandas as pd

from common import load_bars
from forecast import build, third_fridays


def table(sym, asof, prev_fri, now_px, rng):
    g = build().gex_pct
    c = load_bars(sym).close
    c = c[(c.index < asof) & (c.index >= "1983-01-01")]
    idx, rows = c.index, []
    for o in sorted(third_fridays(idx)):
        if o not in idx:
            continue
        i = idx.get_loc(o)
        if i < 25 or i + 10 >= len(idx):
            continue
        thu, prevfri = idx[i - 1], idx[idx < o - pd.Timedelta(days=4)][-1]
        sd = np.log(c).diff().iloc[i - 21:i - 1].std()
        rows.append({"opex": o, "monthu": c[thu] / c[prevfri] - 1, "fri": c[o] / c[thu] - 1, "z": np.log(c[o] / c[thu]) / sd,
                     "wk1": c.iloc[i + 5] / c[o] - 1, "wk2": c.iloc[i + 10] / c[o] - 1, "g": g.asof(thu) if thu >= g.index[0] else np.nan})
    d = pd.DataFrame(rows).set_index("opex")
    now = now_px / prev_fri - 1
    sets = {"all expiry weeks": d.monthu == d.monthu, "Mon-Thu bottom third": d.monthu <= d.monthu.quantile(1 / 3),
            f"Mon-Thu as weak as now (<= {100 * now:+.1f}%)": d.monthu <= now,
            "bottom third + S&P gamma low Thu": (d.monthu <= d.monthu.quantile(1 / 3)) & (d.g <= 1 / 3)}
    out = []
    for lab, m in sets.items():
        x = d[m]
        def luck(col, fn):
            obs = fn(x[col])
            null = np.array([fn(d[col].sample(len(x), random_state=int(s))) for s in rng.integers(1e9, size=2000)])
            return obs, float(np.mean(null >= obs))
        bu, pbu = luck("z", lambda v: (v > 1).mean())
        w1, pw1 = luck("wk1", lambda v: v.mean())
        out.append({"set": lab, "n": len(x), "Fri up %": 100 * (x.fri > 0).mean(), "Fri mean %": 100 * x.fri.mean(),
                    "Fri big up %": 100 * bu, "p big up": pbu, "Fri big down %": 100 * (x.z < -1).mean(),
                    "next wk mean %": 100 * w1, "p next wk": pw1, "next wk up %": 100 * (x.wk1 > 0).mean(), "2 wks mean %": 100 * x.wk2.mean()})
    return pd.DataFrame(out).set_index("set"), now, (d.monthu < now).mean(), d.index[0]


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    asof = pd.Timestamp(sys.argv[1])
    rng = np.random.default_rng(2)
    for arg in sys.argv[2:]:
        sym, vals = arg.split("=")
        pf, nw = map(float, vals.split(","))
        t, now, pc, first = table(sym, asof, pf, nw, rng)
        print(f"\n=== {sym} from {first.date()} | this week Mon-Thu {100 * now:+.1f}% (percentile {pc:.2f})")
        print(t.round(2).to_string())
