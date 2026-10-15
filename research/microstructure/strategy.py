"""Gamma-release strategy for catching index up-legs, tested walk-forward.

Thesis (from release.py): up-legs start when S&P dealer gamma is low or negative
(price is free) and end when the rally rebuilds gamma to an extreme (pinned).
Low gamma alone also marks selloffs, so the entry needs an ignition:

  ARMED     GEX percentile (vs trailing year) <= ARM within the last 15 days
  IGNITION  VIX closes >= K below its 10-day max (vol starts to be crushed:
            vanna/charm buying begins); first such day while armed
  ENTRY     close of the NEXT day (GEX is published after the close)
  EXIT      GEX percentile >= PIN (gamma rebuilt, price pinned) or MAXHOLD days

Measured as SPX return and as a bought 30-day ATM call (IV = VIX at entry and
exit, Black-Scholes, 4% round-trip cost on premium). Parameters are chosen on
2012-2018 only; 2019-2026 is the untouched out-of-sample test. The grid table
shows whether the result is a plateau (robust) or a spike (overfit).
"""
import itertools

import numpy as np
import pandas as pd
from scipy.stats import norm

from common import DATA, load_bars

SPLIT = pd.Timestamp("2019-01-01")
COST = 0.04
DTE = 30


def frame():
    s, v = load_bars("^GSPC").close, load_bars("^VIX").close
    g = pd.read_csv(DATA / "DIX.csv", parse_dates=["date"]).set_index("date").gex
    d = pd.DataFrame({"c": s, "vix": v}).join(g, how="inner").dropna()
    d["gpct"] = d.gex.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
    return d.dropna()


def call(S, K, T, iv, r=0.04):
    if T <= 0:
        return max(S - K, 0.0)
    d1 = (np.log(S / K) + (r + 0.5 * iv * iv) * T) / (iv * np.sqrt(T))
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d1 - iv * np.sqrt(T))


def trades(d, arm=0.10, k=0.15, pin=0.90, maxhold=20):
    c, vix, gp = d.c.to_numpy(), d.vix.to_numpy(), d.gpct.to_numpy()
    armed = pd.Series(gp <= arm).rolling(15, min_periods=1).max().to_numpy() > 0
    vmax = pd.Series(vix).rolling(10).max().to_numpy()
    ign = armed & (vix <= (1 - k) * vmax)
    out, i, n = [], 0, len(c)
    while i < n - 2:
        if ign[i]:
            e = i + 1
            x = next((j for j in range(e + 1, min(e + maxhold, n - 1) + 1) if gp[j] >= pin), min(e + maxhold, n - 1))
            S0, K = c[e], c[e]
            p0 = call(S0, K, DTE / 365, vix[e] / 100)
            p1 = call(c[x], K, (DTE - (x - e) * 365 / 252) / 365, vix[x] / 100)
            path = c[e:x + 1] / S0 - 1
            out.append({"signal": d.index[i], "entry": d.index[e], "exit": d.index[x], "days": x - e,
                        "spx_ret": c[x] / S0 - 1, "mae": path.min(), "call_ret": p1 / p0 - 1 - COST,
                        "exit_by_pin": gp[x] >= pin, "gpct_entry": gp[e], "vix_entry": vix[e]})
            i = x + 1
        else:
            i += 1
    return pd.DataFrame(out)


def stats(t, d):
    if t.empty:
        return {"n": 0}
    # benchmark: every day, same holding period distribution -> mean SPX return per trade
    c = d.c.to_numpy()
    h = int(round(t.days.mean()))
    base = np.mean(c[h:] / c[:-h] - 1)
    return {"n": len(t), "hit": (t.spx_ret > 0).mean(), "spx_mean": t.spx_ret.mean(), "bench_same_hold": base,
            "excess": t.spx_ret.mean() - base, "worst_mae": t.mae.min(), "avg_days": t.days.mean(),
            "call_mean": t.call_ret.mean(), "call_median": t.call_ret.median(), "call_hit": (t.call_ret > 0).mean(),
            "pin_exits": t.exit_by_pin.mean()}


def random_entry_calls(d, n_trades, hold, reps=2000, seed=0):
    """Call returns from random entry days with the same count and holding period."""
    rng = np.random.default_rng(seed)
    c, vix = d.c.to_numpy(), d.vix.to_numpy()
    idx = np.arange(len(c) - hold - 1)
    res = []
    for _ in range(reps):
        e = rng.choice(idx, n_trades)
        r = [call(c[x], c[x0], (DTE - hold * 365 / 252) / 365, vix[x] / 100) / call(c[x0], c[x0], DTE / 365, vix[x0] / 100) - 1 - COST
             for x0, x in zip(e, e + hold)]
        res.append(np.mean(r))
    return np.array(res)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    d = frame()
    ins, oos = d[d.index < SPLIT], d[d.index >= SPLIT]
    grid = []
    for arm, k, pin, mh in itertools.product((0.05, 0.10, 0.20), (0.10, 0.15, 0.20, 0.25), (0.80, 0.90, 0.95), (10, 20)):
        s_in = stats(trades(ins, arm, k, pin, mh), ins)
        s_out = stats(trades(oos, arm, k, pin, mh), oos)
        grid.append({"arm": arm, "k": k, "pin": pin, "maxhold": mh, "n_in": s_in["n"], "ex_in": s_in.get("excess"),
                     "call_in": s_in.get("call_mean"), "n_out": s_out["n"], "ex_out": s_out.get("excess"),
                     "hit_out": s_out.get("hit"), "call_out": s_out.get("call_mean")})
    g = pd.DataFrame(grid)
    print("parameter grid (excess = SPX return over same-length random hold)")
    print(g.round(4).to_string(index=False))
    # pick on in-sample only: best in-sample call return with >= 8 trades
    best = g[g.n_in >= 8].sort_values("call_in", ascending=False).iloc[0]
    p = dict(arm=best.arm, k=best.k, pin=best.pin, maxhold=int(best.maxhold))
    print("\nchosen on 2012-2018:", p)
    print("in-sample share of grid with positive excess:", (g.ex_in > 0).mean().round(2),
          " out-of-sample:", (g.ex_out > 0).mean().round(2))
    for lab, part in (("IN 2012-2018", ins), ("OUT 2019-2026", oos)):
        t = trades(part, **p)
        s = stats(t, part)
        rnd = random_entry_calls(part, s["n"], int(round(s["avg_days"])))
        s["call_vs_random_pctile"] = (rnd < s["call_mean"]).mean()
        print(f"\n{lab}: " + ", ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}" for k, v in s.items()))
        if lab.startswith("OUT"):
            print(t.assign(spx_ret=lambda x: (100 * x.spx_ret).round(1), mae=lambda x: (100 * x.mae).round(1),
                           call_ret=lambda x: (100 * x.call_ret).round(0)).drop(columns=["signal"]).round({"gpct_entry": 2, "vix_entry": 2}).to_string(index=False))
            t.to_csv(DATA.parent / "out" / "strategy_trades_oos.csv", index=False)
    last = d.iloc[-15:]
    print("\nNOW:", d.index[-1].date(), f"GEX pct {d.gpct.iloc[-1]:.2f}, min last 15d {last.gpct.min():.2f}, "
          f"VIX {d.vix.iloc[-1]:.1f} vs 10d max {d.vix.iloc[-10:].max():.1f}",
          "-> ARMED" if last.gpct.min() <= p["arm"] else "-> not armed")
