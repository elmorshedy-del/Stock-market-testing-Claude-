"""Exploratory (labelled as such): diagnosis of why S0 fails, H3 grid with a joint max-t null, and conditioning variables.
Usage: python explore.py [SYMBOL] -> out/explore_<SYM>.json, out/features_<SYM>.parquet"""
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"; O = HERE / "out"
sym = sys.argv[1] if len(sys.argv) > 1 else "SPY"
days = pd.read_parquet(O / f"days_{sym}.parquet"); C = 0.01
ORS, EXITS = [1, 5, 15, 30], ["close", "10R", "2R"]
VAR = [f"{s}_{m}_{e}" for s in ("S0", "S1") for m in ORS for e in EXITS]


def pnl(df, k, dirs=None):
    d = df[k + "_dir"].to_numpy() if dirs is None else dirs
    return np.where(d > 0, df[k + "_L"].fillna(0).to_numpy(), np.where(d < 0, df[k + "_S"].fillna(0).to_numpy(), 0.0))


tstat = lambda p: p.mean() / (p.std(ddof=1) / np.sqrt(len(p))) if p.std() > 0 else 0.0
out = {"note": "EXPLORATORY. Nothing here is a confirmatory test except where a pre-registered null is named."}

# 1. Why S0 fails: exit mix, R-multiples, gross vs net, the signal itself
k = "S0_5_10R"; d = days[k + "_dir"].to_numpy(); p = pnl(days, k)
e = days.px935.to_numpy(); Rbp = np.where(d > 0, (e + C - days.or5_lo) / (e + C), (days.or5_hi - (e - C)) / (e - C)) * 1e4
rm = np.where(d != 0, p / Rbp, np.nan)
first5 = (days.close * 0 + 0)  # placeholder for alignment
r5 = np.log(days.px935 / days.open) * 1e4; rest = np.log(days.close / days.px935) * 1e4
yr = days.index.year
out["1 diagnosis S0 5-min 10R"] = {
    "median opening-range risk R (bp)": round(float(np.nanmedian(Rbp)), 1),
    "exit mix: stopped (R <= -0.9) / target (R >= 9.5) / held to close": [round(float(np.nanmean(rm <= -0.9)), 3), round(float(np.nanmean(rm >= 9.5)), 3), round(float(np.nanmean((rm > -0.9) & (rm < 9.5))), 3)],
    "mean R per trade": round(float(np.nanmean(rm)), 3), "costs per trade (bp, ~2-3 cents on SPY)": round(float(np.nanmean(np.where(d != 0, 2.2 * C / e * 1e4, np.nan))), 2),
    "signal: corr(first-5-min return, 09:35->close return)": round(float(np.corrcoef(r5, rest)[0, 1]), 3),
    "signal by year": {int(y): round(float(np.corrcoef(r5[yr == y], rest[yr == y])[0, 1]), 3) for y in sorted(set(yr))},
    "S0 mean bp/day by year": {int(y): round(float(p[yr == y].mean()), 2) for y in sorted(set(yr))},
    "SPY 09:35->close mean bp by year": {int(y): round(float(days.hold935[yr == y].mean()), 2) for y in sorted(set(yr))},
}

# 2. H3 grid with a joint (max-t over all 24 variants) circular-shift null
N = len(days); shifts = range(20, N - 20)
act = {v: pnl(days, v) for v in VAR}
grid = {v: {"mean bp/day": round(float(act[v].mean()), 2), "t": round(float(tstat(act[v])), 2), "trades": int((days[v + "_dir"] != 0).sum()),
            "hit": round(float((act[v][act[v] != 0] > 0).mean()), 3)} for v in VAR}
mt_act = max(tstat(act[v]) for v in VAR); mt_min = min(tstat(act[v]) for v in VAR)
null_max = np.array([max(tstat(pnl(days, v, np.roll(days[v + "_dir"].to_numpy(), s))) for v in VAR) for s in shifts])
null_min = np.array([min(tstat(pnl(days, v, np.roll(days[v + "_dir"].to_numpy(), s))) for v in VAR) for s in shifts])
out["2 H3 grid (24 variants)"] = {"variants": grid, "best": max(grid, key=lambda v: grid[v]["t"]), "best t": round(float(mt_act), 2),
                                  "joint p (max-t, follow)": round(float((null_max >= mt_act).mean()), 4), "worst": min(grid, key=lambda v: grid[v]["t"]),
                                  "joint p (min-t, i.e. FADE the breakout)": round(float((null_min <= mt_min).mean()), 4)}

# 3. Conditioning variables (all known by 09:35)
y = pd.read_csv(D / f"{sym}_yahoo_daily.csv", index_col=0, parse_dates=True)
f = pd.DataFrame(index=days.index)
pc = y.close.shift(1).reindex(days.index)
f["gap_bp"] = (days.open / pc - 1) * 1e4
f["dir5"] = days["S0_5_10R_dir"]
f["gap_agree"] = np.sign(f.gap_bp) == f.dir5
tr = pd.concat([y.high - y.low, (y.high - y.close.shift()).abs(), (y.low - y.close.shift()).abs()], axis=1).max(axis=1)
atr = (tr.rolling(14).mean().shift(1) / y.close.shift(1) * 1e4).reindex(days.index)
f["or_width_atr"] = ((days.or5_hi - days.or5_lo) / days.open * 1e4) / atr
v5 = days.vol5; f["rvol5"] = v5 / v5.rolling(14).mean().shift(1)
f["prior_ret_bp"] = (y.close / y.close.shift(1) - 1).shift(1).reindex(days.index) * 1e4
f["dow"] = days.index.dayofweek
third_fri = lambda t: (t.weekday() == 4) and (15 <= t.day <= 21)
f["opex_day"] = [third_fri(t) for t in days.index]
f["opex_week"] = [any(third_fri(t + pd.Timedelta(days=i)) for i in range(0, 5 - t.weekday())) for t in days.index]
FOMC = ["2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18", "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
        "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10", "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16", "2026-10-28"]
f["fomc"] = days.index.isin(pd.to_datetime(FOMC))
try:
    u = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?period1=1700000000&period2=1793750400&interval=1d"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]; vix = pd.DataFrame({"o": q["open"], "c": q["close"]}, index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").tz_localize(None).normalize())
    vix = vix[~vix.index.duplicated(keep="last")].dropna(); vix.to_csv(D / "vix_daily.csv")
    f["vix_prev"] = vix.c.shift(1).reindex(days.index); f["vix_overnight"] = (vix.o - vix.c.shift(1)).reindex(days.index)
except Exception as ex:
    out["vix error"] = str(ex)[:80]
pl = pd.read_csv(HERE.parent / "2026-10-27-flip-wicks" / "out" / "preopen_levels.csv", parse_dates=["date"]).set_index("date")
f = f.join(pl[["flip_incl", "share_0dte", "gex_open"]])
f["dist_flip_bp"] = (days.px935 / f.flip_incl - 1) * 1e4; f["below_flip"] = (f.dist_flip_bp < 0).where(f.flip_incl.notna())
sm = pd.read_csv(D / "squeeze_dix.csv", parse_dates=["date"]).set_index("date")
pr = lambda s: s.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
f["gex_pct_prev"] = pr(sm.gex.astype(float)).shift(1).reindex(days.index); f["dix_pct_prev"] = pr(sm.dix.astype(float)).shift(1).reindex(days.index)
f["abs_r5_atr"] = (np.log(days.px935 / days.open).abs() * 1e4) / atr
f.to_parquet(O / f"features_{sym}.parquet")

cond = {}
for v in ["S0_5_10R", "S0_5_close", "S1_5_close", "S0_15_close", "S0_30_close"]:
    pv = pd.Series(pnl(days, v), index=days.index); dv = days[v + "_dir"]
    tab = {}
    for c in ["gap_bp", "or_width_atr", "rvol5", "vix_prev", "vix_overnight", "dist_flip_bp", "share_0dte", "gex_pct_prev", "dix_pct_prev", "prior_ret_bp", "abs_r5_atr"]:
        x = f[c]; ok = x.notna() & (dv != 0)
        if ok.sum() < 60: continue
        qs = pd.qcut(x[ok], 3, labels=["low", "mid", "high"])
        tab[c] = {str(b): [round(float(pv[ok][qs == b].mean()), 2), int((qs == b).sum())] for b in ["low", "mid", "high"]}
    for c in ["gap_agree", "opex_week", "opex_day", "fomc", "below_flip"]:
        x = f[c]; ok = x.notna() & (dv != 0)
        tab[c] = {str(b): [round(float(pv[ok][x[ok] == b].mean()), 2), int((x[ok] == b).sum())] for b in [True, False]}
    tab["dow"] = {int(b): round(float(pv[(f.dow == b) & (dv != 0)].mean()), 2) for b in range(5)}
    tab["below_flip x direction (mean bp/trade)"] = {f"{'below' if bf else 'above'} {'long' if s > 0 else 'short'}": [round(float(pv[(f.below_flip == bf) & (dv == s)].mean()), 2), int(((f.below_flip == bf) & (dv == s)).sum())] for bf in (True, False) for s in (1, -1)}
    cond[v] = tab
out["3 conditioning (mean bp/trade, n) by terciles or flags"] = cond
json.dump(out, open(O / f"explore_{sym}.json", "w"), indent=1, default=str)
print(json.dumps(out["1 diagnosis S0 5-min 10R"], indent=1)); print({k2: v2 for k2, v2 in out["2 H3 grid (24 variants)"].items() if k2 != "variants"})
for v, g in sorted(grid.items(), key=lambda kv: -kv[1]["t"]): print(f"{v:14s} {g}")
