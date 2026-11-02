"""ORB engine + pre-registered H1 (replication) and H2 (gamma regime). Usage: python orb.py [SYMBOL] [--incl-d2]
Per day and variant it computes the long and the short outcome, so a circular-shift null can swap the direction signal.
Outputs: out/days_<SYM>.parquet (per-day pnl for every grid variant, both directions) and out/h1h2_<SYM>.json."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"; O = HERE / "out"
sym = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "SPY"
INCL_D2 = "--incl-d2" in sys.argv
C = 0.01   # $ per share per side; stops pay one more cent
ORS, EXITS = [1, 5, 15, 30], ["close", "10R", "2R"]

if INCL_D2:   # robustness: D2-flagged days (complete bars; Yahoo's extremes differ by a few bp) added back
    rth = pd.read_parquet(D / f"{sym}_rth_d2.parquet")
else:
    rth = pd.read_parquet(D / f"{sym}_rth.parquet")
grid = {}
for d, g in rth.groupby("date"):
    g = g.set_index("hm").reindex(pd.date_range("09:30", "15:59", freq="1min").strftime("%H:%M"))
    if g.open.isna().iloc[:30].any(): continue
    grid[d] = g[["open", "high", "low", "close", "volume"]].ffill().to_numpy()   # fill rare gaps with the last close-ish values


def run_long(x, m, stop, target, entry_i, entry_px):
    """Long from bar entry_i at entry_px (cost added), stop/target checked from entry_i (S0) ; returns exit price net."""
    o, h, l, c = x[:, 0], x[:, 1], x[:, 2], x[:, 3]
    seg = slice(entry_i, 390)
    js = np.flatnonzero(l[seg] <= stop); jt = np.flatnonzero(h[seg] >= target) if target is not None else np.array([], int)
    j = js[0] if len(js) else 10**6; k = jt[0] if len(jt) else 10**6
    if j == 10**6 and k == 10**6: return c[-1] - C
    if j <= k: return min(stop, o[entry_i + j]) - 2 * C
    return max(target, o[entry_i + k]) - C


def s0(x, m, exit_rule):
    """Zarattini-Aziz: first m-minute candle direction, entry at bar m open, stop at the candle's opposite extreme."""
    o0, cm = x[0, 0], x[m - 1, 3]; hi, lo = x[:m, 1].max(), x[:m, 2].min(); e = x[m, 0]
    d = np.sign(cm - o0)
    outL = outS = np.nan
    if e > lo:   # long version
        R = e + C - lo; tgt = None if exit_rule == "close" else e + C + R * (10 if exit_rule == "10R" else 2)
        outL = (run_long(x, m, lo, tgt, m, e) - (e + C)) / (e + C) * 1e4
    if e < hi:   # short version, mirror the bars
        y = -x[:, [0, 2, 1, 3]]; R = hi - (e - C); tgt = None if exit_rule == "close" else -(e - C - R * (10 if exit_rule == "10R" else 2))
        ex = -run_long(y, m, -hi, tgt, m, -e)   # net exit price (cost already applied in mirrored space)
        outS = ((e - C) - ex) / (e - C) * 1e4
    return d, outL, outS


def s1(x, m, exit_rule):
    """Classic breakout of the m-minute range, first break only, entries before 15:00 (bar 330), stop at the other side."""
    hi, lo = x[:m, 1].max(), x[:m, 2].min()
    up = np.flatnonzero(x[m:330, 1] > hi + 0.01); dn = np.flatnonzero(x[m:330, 2] < lo - 0.01)
    iu = up[0] + m if len(up) else None; idn = dn[0] + m if len(dn) else None
    outL = outS = np.nan
    if iu is not None:
        e = max(hi + 0.01, x[iu, 0]); R = e + C - lo; tgt = None if exit_rule == "close" else e + C + R * (10 if exit_rule == "10R" else 2)
        ex = (min(lo, x[iu, 3]) - 2 * C) if x[iu, 3] <= lo else (run_long(x, m, lo, tgt, iu + 1, e) if iu + 1 < 390 else x[iu, 3] - C)
        outL = (ex - (e + C)) / (e + C) * 1e4
    if idn is not None:
        e = min(lo - 0.01, x[idn, 0]); y = -x[:, [0, 2, 1, 3]]; R = hi - (e - C); tgt = None if exit_rule == "close" else -(e - C - R * (10 if exit_rule == "10R" else 2))
        ex = -((min(-hi, y[idn, 3]) - 2 * C) if y[idn, 3] <= -hi else (run_long(y, m, -hi, tgt, idn + 1, -e) if idn + 1 < 390 else y[idn, 3] - C))
        outS = ((e - C) - ex) / (e - C) * 1e4
    if iu is None and idn is None: d = 0
    elif idn is None or (iu is not None and iu < idn): d = 1
    elif iu is None or idn < iu: d = -1
    else: d = 0   # both in the same bar: ambiguous, no trade
    return d, outL, outS


rows = []
for d, x in grid.items():
    r = {"date": d, "open": x[0, 0], "close": x[-1, 3], "px935": x[5, 0], "or5_hi": x[:5, 1].max(), "or5_lo": x[:5, 2].min(),
         "vol5": x[:5, 4].sum(), "vol_day": x[:, 4].sum(), "hold935": (x[-1, 3] - C - (x[5, 0] + C)) / (x[5, 0] + C) * 1e4}
    for m in ORS:
        for ex in EXITS:
            for nm, f in (("S0", s0), ("S1", s1)):
                dd, L, S = f(x, m, ex); k = f"{nm}_{m}_{ex}"
                r[k + "_dir"], r[k + "_L"], r[k + "_S"] = dd, L, S
    rows.append(r)
days = pd.DataFrame(rows).set_index("date").sort_index()
days.to_parquet(O / f"days_{sym}{'_d2' if INCL_D2 else ''}.parquet")


def pnl(df, k, dirs=None):
    d = df[k + "_dir"].to_numpy() if dirs is None else dirs
    return np.where(d > 0, df[k + "_L"].fillna(0).to_numpy(), np.where(d < 0, df[k + "_S"].fillna(0).to_numpy(), 0.0))


def shift_null(df, k, stat=np.mean):
    d = df[k + "_dir"].to_numpy(); N = len(d); act = stat(pnl(df, k))
    null = np.array([stat(pnl(df, k, np.roll(d, s))) for s in range(20, N - 20)])
    return act, float((null >= act).mean()), null


def summ(p, n_trades):
    p = np.asarray(p); t = p[p != 0]
    return {"days": int(len(p)), "trades": int(n_trades), "mean bp/day": round(float(p.mean()), 3), "mean bp/trade": round(float(t.mean()), 3) if len(t) else None,
            "hit rate": round(float((t > 0).mean()), 3) if len(t) else None, "ann. Sharpe (daily)": round(float(p.mean() / p.std() * np.sqrt(252)), 2) if p.std() > 0 else None,
            "total bp": round(float(p.sum()), 1)}


res = {"symbol": sym, "sample": f"{days.index.min().date()} to {days.index.max().date()}", "sessions": len(days), "incl D2-flagged days": INCL_D2}
k0 = "S0_5_10R"; act, p, _ = shift_null(days, k0)
p0 = pnl(days, k0); d0 = days[k0 + "_dir"]
res["H1 S0 (5-min, 10R, primary)"] = {**summ(p0, (d0 != 0).sum()), "shift-null p": round(p, 4), "PASS": bool(act > 0 and p < 0.05),
                                      "longs": summ(np.where(d0 > 0, p0, 0), (d0 > 0).sum()), "shorts": summ(np.where(d0 < 0, p0, 0), (d0 < 0).sum())}
k1 = "S1_5_close"; a1, pp1, _ = shift_null(days, k1); p1 = pnl(days, k1)
res["S1 classic 5-min breakout, exit close (secondary)"] = {**summ(p1, (days[k1 + "_dir"] != 0).sum()), "shift-null p": round(pp1, 4)}
res["benchmark: long 09:35 -> close every day"] = summ(days.hold935.to_numpy(), len(days))

# H2: gamma regime from flip-wicks pre-open levels (prior-close OI), through 2026-10-12
if not sym.startswith("SPY"):
    json.dump(res, open(O / f"h1h2_{sym}{'_d2' if INCL_D2 else ''}.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str)); sys.exit(0)
pl = pd.read_csv(HERE.parent / "2026-10-27-flip-wicks" / "out" / "preopen_levels.csv", parse_dates=["date"]).set_index("date")
g = days.join(pl[["flip_incl", "flip_excl", "share_0dte", "gex_open"]], how="inner")
sm = pd.read_csv(HERE.parent.parent.parent / "research" / "agents" / "2026-11-02-orb-gamma" / "data" / "squeeze_dix.csv", parse_dates=["date"]).set_index("date") if (D / "squeeze_dix.csv").exists() else None


def regime_test(df, lab, k=k0):
    """mean pnl on lab==1 minus lab==0, null = circular shift of the label series."""
    p = pnl(df, k); lab = lab.astype(int).to_numpy(); N = len(p)
    diff = lambda L: p[L == 1].mean() - p[L == 0].mean()
    act = diff(lab); null = np.array([diff(np.roll(lab, s)) for s in range(20, N - 20)])
    out = {"n below/low": int(lab.sum()), "n above/high": int((1 - lab).sum()), "mean bp/day below": round(float(p[lab == 1].mean()), 3),
           "mean bp/day above": round(float(p[lab == 0].mean()), 3), "diff": round(float(act), 3), "shift-null p (one-sided, below > above)": round(float((null >= act).mean()), 4)}
    d = df[k + "_dir"].to_numpy()
    for nm, sel in (("longs", d > 0), ("shorts", d < 0)):
        out[nm + " mean bp/trade below vs above"] = [round(float(p[sel & (lab == 1)].mean()), 2), round(float(p[sel & (lab == 0)].mean()), 2)]
    return out


h2 = {"primary: 09:35 price < flip_incl": regime_test(g, g.px935 < g.flip_incl), "secondary: 09:35 price < flip_excl": regime_test(g, g.px935 < g.flip_excl)}
if sm is not None:
    s = sm["gex"].astype(float); pct = s.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True).shift(1)   # prior close, vs trailing year
    gg = g.join(pct.rename("gex_pct"), how="inner"); gg = gg[(gg.gex_pct <= 1 / 3) | (gg.gex_pct >= 2 / 3)]
    h2["secondary: S&P GEX bottom vs top tercile (prior close)"] = regime_test(gg, gg.gex_pct <= 1 / 3)
ps = [v["shift-null p (one-sided, below > above)"] for v in h2.values()]
order = np.argsort(ps); holm = {}
for rank, i in enumerate(order): holm[list(h2)[i]] = min(1.0, max([ps[j] * (len(ps) - r) for r, j in enumerate(order[:rank + 1])]))
for kk in h2: h2[kk]["Holm p"] = round(holm[kk], 4)
h2["PASS (primary p < 0.05, diff > 0)"] = bool(h2["primary: 09:35 price < flip_incl"]["diff"] > 0 and h2["primary: 09:35 price < flip_incl"]["shift-null p (one-sided, below > above)"] < 0.05)
h2["sessions with gamma state"] = f"{g.index.min().date()} to {g.index.max().date()} ({len(g)})"
res["H2 gamma regime (S0 5-min 10R)"] = h2
json.dump(res, open(O / f"h1h2_{sym}{'_d2' if INCL_D2 else ''}.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
