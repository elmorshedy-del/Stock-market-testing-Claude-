"""Write the CSV datasets behind the 'S&P gamma cycle' dashboard (out/dashboard/)."""
import json

import numpy as np
import pandas as pd

from common import OUT, load_bars
from forecast import build
from reset import first_days, prep

D = OUT / "dashboard"
END = "2026-10-08"


def spx_cycle(f, x):
    s = f.loc["2026-06-15":END]
    xx = x.loc[s.index]
    return pd.DataFrame({"date": s.index.strftime("%Y-%m-%d"), "spx": s.c.round(2),
                         "gex_pct": (100 * s.gex_pct).round(1), "dix_pct": (100 * s.dix_pct).round(1),
                         "vix": s.VIX.round(2), "reset": xx.reset.astype(int).to_numpy(),
                         "gamma_ran": xx.ran.astype(int).to_numpy()})


def odds(x):
    rows = []
    for era, start in (("2012+", "2012-01-01"), ("Since late 2019", "2019-10-01")):
        xx = x[x.index >= start].dropna(subset=["fwd20"])
        base_leg, base_con = xx.leg_next20.mean(), xx.consol.mean()
        def add(order, state, mask):
            ev = xx[first_days(mask)] if mask is not None else xx
            rows.append({"era": era, "order": order, "state": state, "p_leg_20d": round(100 * ev.leg_next20.mean(), 1),
                         "p_consolidation": round(100 * ev.consol.mean(), 1), "n": len(ev),
                         "base_leg": round(100 * base_leg, 1), "base_consolidation": round(100 * base_con, 1)})
        add(1, "Any day", None)
        add(2, "Gamma reset in the prior 20 days", xx.reset_prev20)
        add(3, "No reset in the prior 20 days", ~xx.reset_prev20)
        add(4, "Gamma ran up without price", xx.ran)
        idx = np.where(xx.leg_start)[0] + 10
        idx = idx[idx < len(xx)]
        end_pin = pd.Series(False, index=xx.index)
        end_unp = pd.Series(False, index=xx.index)
        for i in idx:
            (end_pin if xx.gex_pct.iloc[i] >= 0.9 else end_unp).iloc[i] = True
        for order, state, m in ((5, "Leg ended with gamma pinned", end_pin), (6, "Leg ended unpinned", end_unp)):
            ev = xx[m.to_numpy()]
            rows.append({"era": era, "order": order, "state": state, "p_leg_20d": round(100 * ev.leg_next20.mean(), 1),
                         "p_consolidation": round(100 * ev.consol.mean(), 1), "n": len(ev),
                         "base_leg": round(100 * base_leg, 1), "base_consolidation": round(100 * base_con, 1)})
    return pd.DataFrame(rows)


def legs_need_reset(x):
    rows = []
    for era, start in (("2012+", "2012-01-01"), ("Since late 2019", "2019-10-01")):
        xx = x[x.index >= start].dropna(subset=["fwd20"])
        legs = xx[xx.leg_start]
        rows.append({"era": era, "legs": len(legs), "legs_with_reset_pct": round(100 * legs.reset_prev20.mean(), 1),
                     "random_days_pct": round(100 * xx.reset_prev20.mean(), 1)})
    return pd.DataFrame(rows)


def tracks():
    mu, ms = load_bars("MU").close.loc["2026-09-15":END], load_bars("MSFT").close.loc["2026-09-15":END]
    ch = json.loads((OUT / "report_numbers.json").read_text())["channel"]
    lo0, b = ch["today_lower_mid_upper"][0], ch["log_slope_per_day"]
    k = np.arange(len(mu)) - list(mu.index.strftime("%Y-%m-%d")).index("2026-10-01")
    mut = pd.DataFrame({"date": mu.index.strftime("%Y-%m-%d"), "close": mu.round(2).to_numpy(),
                        "channel_lower": (lo0 * np.exp(b * k)).round(1)})
    mst = pd.DataFrame({"date": ms.index.strftime("%Y-%m-%d"), "close": ms.round(2).to_numpy()})
    return mut, mst


LEVELS = [("MU", "Upside trigger (largest gamma strike)", 1100), ("MU", "Gamma flip", 1011),
          ("MSFT", "Pin zone low", 510), ("MSFT", "Pin zone high", 525), ("MSFT", "Call wall", 550)]

SCORECARD = [
    ("SPX", "Oct 2", "Today's state does not raise the odds of an up-leg", "No leg yet: S&P +1.3% Oct 1 to Oct 8 (a leg needs +3.5% in 10 days)", "Consistent"),
    ("SPX", "Oct 2", "Entry rung R2 likely by the Oct 16 expiry (28% by Oct 2, 44% by Oct 9, 56% by Oct 16)", "Not on yet: lowest gamma since Oct 1 was the 44th percentile", "Not yet"),
    ("SPX", "Oct 2", "Usual path: a ~1% dip pushes gamma down within about 5 days", "Opposite: S&P rose 2% to Oct 6 and gamma ran to the 91st percentile", "Missed"),
    ("SPX", "Oct 2", "Gamma builds into monthly expiry, then drops", "Rose to Oct 6, fading since; the Oct 16 expiry is still ahead", "Partly"),
    ("SPX", "Oct 2", "High dark-pool buying (DIX above 80th) is a mild tilt up", "DIX stayed 81st-97th; S&P drifted up 1.3%", "Consistent"),
    ("SPX", "Oct 9", "Gamma ran without price (Oct 2-6): consolidation first, the next leg after a reset", "Open: check by early November", "Open"),
    ("MU", "Oct 1", "Rising lower channel line (1,070, +0.8% a day) breaks within ~3 days if price stalls", "Closed below it on Oct 2 (1,075 vs 1,078) and stayed below", "Played out"),
    ("MU", "Oct 1", "A breakout needs acceptance above 1,100", "No close above 1,100 (highest 1,088)", "Consistent"),
    ("MU", "Oct 1", "Most likely chop between 1,045 and 1,150", "Range 1,036 to 1,088: chop, a little lower than called", "Partly"),
    ("MU", "Oct 1", "Breakdown path: lose 1,070, then the gamma flip near 1,011", "Lost 1,070 on Oct 5; low close 1,036; 1,011 not reached", "Partly"),
    ("MSFT", "Oct 2", "Pinned near 510-525 into the Oct 16 expiry", "Closes 517.5 to 529.8: in or just above the zone", "Mostly"),
    ("MSFT", "Oct 2", "Earnings Oct 28 is the candidate breakout week", "Pending", "Open"),
    ("TSLA", "Oct 9", "Pinned chop 370-385 into the Oct 16 expiry, then the Oct 21 report", "Pending (375 on Oct 8)", "Open"),
]

if __name__ == "__main__":
    D.mkdir(exist_ok=True)
    f = build()
    x = prep(f)
    spx_cycle(f, x).to_csv(D / "spx_cycle.csv", index=False)
    odds(x).to_csv(D / "reset_odds.csv", index=False)
    legs_need_reset(x).to_csv(D / "legs_need_reset.csv", index=False)
    mu, ms = tracks()
    mu.to_csv(D / "mu_track.csv", index=False)
    ms.to_csv(D / "msft_track.csv", index=False)
    pd.DataFrame(LEVELS, columns=["market", "level", "value"]).to_csv(D / "levels.csv", index=False)
    pd.DataFrame(SCORECARD, columns=["market", "made", "call", "outcome", "verdict"]).assign(
        id=lambda t: [f"c{i + 1}" for i in range(len(t))]).to_csv(D / "scorecard.csv", index=False)
    for p in sorted(D.glob("*.csv")):
        print(p.name, len(pd.read_csv(p)))
