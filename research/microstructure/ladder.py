"""Entry ladder: what is the EARLIEST condition at which the odds already tilt?

Each rung is an entry condition, from today's state through to the full
gamma-release signal. For every rung (first day the condition turns on, events
>= 10 days apart) we measure over the next 20 trading days:
  p_leg      an up-leg (top-decile 10d S&P return) starts within 20d
  lead       trading days from entry to that leg's start (how early you are)
  spx20      S&P return, and mae (worst drawdown) while holding
  call60     a 60-DTE ATM call bought at entry (IV = VIX), sold after 20 days
             with VIX then, 4% round-trip cost
and compare with every day ("any day"). CI = bootstrap on events.
"""
import numpy as np
import pandas as pd

from forecast import build
from strategy import call

HOLD, DTE, COST, GAP = 20, 60, 0.04, 10


def first_on(cond, gap=GAP):
    c = cond.fillna(False).to_numpy()
    out, last = np.zeros(len(c), bool), -10**9
    for i in np.where(c & ~np.r_[False, c[:-1]])[0]:
        if i - last >= gap:
            out[i], last = True, i
    return out


def rungs(f):
    hi10 = f.c.rolling(10).max()
    vmax10 = f.VIX.rolling(10).max()
    low_recent = (f.gex_pct.rolling(15).min() <= 0.20)
    return {
        "R0 today-like: mid GEX (0.35-0.55) + DIX>0.8": (f.gex_pct.between(0.35, 0.55)) & (f.dix_pct > 0.8),
        "R1 GEX pct <= 0.30": f.gex_pct <= 0.30,
        "R2 GEX pct <= 0.30 + DIX>0.5": (f.gex_pct <= 0.30) & (f.dix_pct > 0.5),
        "R3 GEX pct <= 0.20": f.gex_pct <= 0.20,
        "R4 GEX <= 0.20 + SPX >= 2% off 10d high": (f.gex_pct <= 0.20) & (f.c / hi10 - 1 <= -0.02),
        "R5 GEX <= 0.20 + 2% dip + DIX>0.5": (f.gex_pct <= 0.20) & (f.c / hi10 - 1 <= -0.02) & (f.dix_pct > 0.5),
        "R6 low GEX recently + VIX 15% off 10d max": low_recent & (f.VIX <= 0.85 * vmax10),
        "R7 low GEX recently + VIX 25% off 10d max": low_recent & (f.VIX <= 0.75 * vmax10),
    }


def outcomes(f):
    c, v = f.c.to_numpy(), f.VIX.to_numpy()
    n = len(c)
    fwd10 = np.r_[np.log(c[10:] / c[:-10]), np.full(10, np.nan)]
    top = np.nanquantile(fwd10, 0.9)
    rows = []
    for i in range(n - HOLD - 1):
        w = fwd10[i + 1:i + 1 + HOLD]
        leg = np.where(w > top)[0]
        p0 = call(c[i], c[i], DTE / 365, v[i] / 100)
        p1 = call(c[i + HOLD], c[i], (DTE - HOLD * 365 / 252) / 365, v[i + HOLD] / 100)
        rows.append((leg.size > 0, leg[0] + 1 if leg.size else np.nan, c[i + HOLD] / c[i] - 1,
                     c[i:i + HOLD + 1].min() / c[i] - 1, p1 / p0 - 1 - COST))
    o = pd.DataFrame(rows, columns=["leg", "lead", "spx20", "mae", "call60"], index=f.index[:n - HOLD - 1])
    return o.reindex(f.index)


def call_spread(f, w=0.05, cost=0.06):
    """60-DTE ATM / +5% call spread held HOLD days (flat vol at VIX: no skew, so
    absolute returns are flattered; compare rungs with 'any day', not with zero)."""
    c, v = f.c.to_numpy(), f.VIX.to_numpy()
    T0, T1 = DTE / 365, (DTE - HOLD * 365 / 252) / 365
    r = np.full(len(c), np.nan)
    for i in range(len(c) - HOLD - 1):
        k1, k2 = c[i], c[i] * (1 + w)
        p0 = call(c[i], k1, T0, v[i] / 100) - call(c[i], k2, T0, v[i] / 100)
        p1 = call(c[i + HOLD], k1, T1, v[i + HOLD] / 100) - call(c[i + HOLD], k2, T1, v[i + HOLD] / 100)
        r[i] = p1 / p0 - 1 - cost
    return pd.Series(r, index=f.index)


def summarize(o, mask, rng):
    x = o[mask].dropna(subset=["spx20"])
    if len(x) < 5:
        return None
    b = [x.call60.to_numpy()[rng.integers(0, len(x), len(x))].mean() for _ in range(2000)]
    bs = [x.spread60.to_numpy()[rng.integers(0, len(x), len(x))].mean() for _ in range(2000)]
    return {"n": len(x), "p_leg": x.leg.mean(), "lead_med": x.lead.median(), "spx20": x.spx20.mean(),
            "spx20_up": (x.spx20 > 0).mean(), "mae_med": x.mae.median(), "call60_mean": x.call60.mean(),
            "call60_ci": f"[{np.quantile(b, .05):+.2f}, {np.quantile(b, .95):+.2f}]",
            "call60_win": (x.call60 > 0).mean(), "spread60_mean": x.spread60.mean(),
            "spread60_ci": f"[{np.quantile(bs, .05):+.2f}, {np.quantile(bs, .95):+.2f}]"}


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    f = build()
    o = outcomes(f)
    o["spread60"] = call_spread(f)
    rng = np.random.default_rng(0)
    for start, lab in ((None, "2012-2026"), ("2019-10-01", "2019Q4-2026 (retail/0DTE)")):
        ff, oo = (f, o) if start is None else (f[f.index >= start], o[o.index >= start])
        rows = {"any day": summarize(oo, np.ones(len(oo), bool), rng)}
        for name, cond in rungs(ff).items():
            r = summarize(oo, first_on(cond), rng)
            if r:
                rows[name] = r
        t = pd.DataFrame(rows).T
        print(f"\n=== {lab}  (call60 CI = 90% bootstrap)")
        print(t.to_string(float_format=lambda v: f"{v:.3f}"))
    now = f.iloc[-1]
    print("\nNOW", f.index[-1].date(), {k: round(float(now[k]), 3) for k in ("gex_pct", "dix_pct", "VIX")},
          "| SPX vs 10d high %.1f%%" % (100 * (now.c / f.c.iloc[-10:].max() - 1)))
    for name, cond in rungs(f).items():
        print(f"  {'ON ' if bool(cond.iloc[-1]) else 'off'}  {name}")
