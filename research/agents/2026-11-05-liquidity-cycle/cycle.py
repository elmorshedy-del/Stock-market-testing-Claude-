"""Q2: S&P liquidity/gamma cycle: phase rules, order test (D1), forecast by phase (D2), dwell (D3), expiry alignment (D4),
cross-check with SPY intraday thinness. Pre-registered. Usage: python cycle.py <DIX.csv> <orb-gamma data dir> -> out/q2.json, out/phases.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from common import daily_from_bars, pct_trailing, yahoo, gex_pct

HERE = Path(__file__).resolve().parent; B = Path(sys.argv[2]); rng = np.random.default_rng(0)
g = gex_pct(sys.argv[1]); spx = yahoo("%5EGSPC"); vix = yahoo("%5EVIX").close
f = g[["gp"]].join(spx[["high", "low", "close"]], how="inner").join(vix.rename("vix"), how="inner").dropna()
f = f[f.index >= "2012-01-01"].copy()
gp, vx = f.gp, f.vix
rec = (gp.rolling(15).min() <= 0.20) & (vx <= 0.85 * vx.rolling(10).max())
thin = gp <= 0.20; thinning = (gp <= 0.50) & (gp - gp.shift(10) <= -0.25); calm = gp >= 0.50
f["phase"] = np.select([rec, thin, thinning, calm], ["RECOVERY", "THIN", "THINNING", "CALM"], "OTHER")
ORDER = ["CALM", "THINNING", "THIN", "RECOVERY"]; NXT = {a: ORDER[(i + 1) % 4] for i, a in enumerate(ORDER)}
# D1 order
runs = (f.phase != f.phase.shift()).cumsum(); ep = f.groupby(runs).agg(phase=("phase", "first"), start=("phase", lambda s: s.index[0]), n=("phase", "size"))
seq = ep[ep.phase != "OTHER"].phase.tolist(); seq = [s for i, s in enumerate(seq) if i == 0 or s != seq[i - 1]]
canon = lambda q: np.mean([NXT[a] == b for a, b in zip(q[:-1], q[1:])])
obs = canon(seq); null = []
for _ in range(10000):
    q = list(rng.permutation(seq)); q = [s for i, s in enumerate(q) if i == 0 or s != q[i - 1]]; null.append(canon(q))
tm = pd.crosstab(pd.Series(seq[:-1], name="from"), pd.Series(seq[1:], name="to"), normalize="index").reindex(index=ORDER, columns=ORDER).round(2)
res = {"days": int(len(f)), "span": [str(f.index[0].date()), str(f.index[-1].date())], "phase share of days": f.phase.value_counts(normalize=True).round(3).to_dict(),
       "D1 order": {"episodes (non-OTHER, merged)": len(seq), "share of transitions to the canonical next phase": round(float(obs), 3),
                    "null mean / 95th pct": [round(float(np.mean(null)), 3), round(float(np.quantile(null, 0.95)), 3)], "p": round(float(np.mean(np.array(null) >= obs)), 4),
                    "PASS (p < 0.05)": bool(np.mean(np.array(null) >= obs) < 0.05), "transition matrix (row = from)": tm.fillna(0).to_dict(orient="index")}}
# D2 forecast
c = f.close; lc = np.log(c.to_numpy()); n = len(c)
fwd20 = np.r_[lc[20:] - lc[:-20], np.full(20, np.nan)]
r10 = np.r_[lc[10:] - lc[:-10], np.full(10, np.nan)]
leg = np.array([np.nanmax(r10[i + 1:i + 21]) >= np.log(1.035) if i + 21 <= n - 10 else np.nan for i in range(n)], float)
rng_d = ((f.high - f.low) / f.close).to_numpy(); rng10 = np.array([rng_d[i + 1:i + 11].mean() if i + 11 <= n else np.nan for i in range(n)])
OUT = {"fwd 20d return %": 100 * fwd20, "up-leg within 20 sessions %": 100 * leg, "fwd 10d mean range %": 100 * rng10}
ph = f.phase.to_numpy(); d2 = {}; pv = []
for p_ in ORDER:
    d2[p_] = {}
    for nm, y in OUT.items():
        ok = ~np.isnan(y); diff = np.nanmean(y[ok & (ph == p_)]) - np.nanmean(y[ok])
        nd = []
        for _ in range(2000):
            s = rng.integers(60, n - 60); q = np.roll(ph, s); nd.append(np.nanmean(y[ok & (q == p_)]) - np.nanmean(y[ok]))
        p2 = float(np.mean(np.abs(nd) >= abs(diff))); pv.append((p_, nm, p2))
        d2[p_][nm] = {"phase mean": round(float(np.nanmean(y[ok & (ph == p_)])), 3), "all days": round(float(np.nanmean(y[ok])), 3), "diff": round(float(diff), 3), "p (2-sided, circular shift)": round(p2, 4),
                      "days / episodes": [int((ok & (ph == p_)).sum()), int((ep.phase == p_).sum())]}
order = sorted(range(len(pv)), key=lambda i: pv[i][2]); m = len(pv); holm = {}; run = 0
for r_, i in enumerate(order):
    run = max(run, min(1, (m - r_) * pv[i][2])); holm[(pv[i][0], pv[i][1])] = round(run, 4)
for (p_, nm), hp in holm.items(): d2[p_][nm]["Holm p"] = hp
pred = {"RECOVERY fwd return >": d2["RECOVERY"]["fwd 20d return %"]["diff"] > 0 and holm[("RECOVERY", "fwd 20d return %")] < 0.05,
        "RECOVERY up-leg odds >": d2["RECOVERY"]["up-leg within 20 sessions %"]["diff"] > 0 and holm[("RECOVERY", "up-leg within 20 sessions %")] < 0.05,
        "THIN range >": d2["THIN"]["fwd 10d mean range %"]["diff"] > 0 and holm[("THIN", "fwd 10d mean range %")] < 0.05,
        "CALM range <": d2["CALM"]["fwd 10d mean range %"]["diff"] < 0 and holm[("CALM", "fwd 10d mean range %")] < 0.05}
res["D2 forecast by phase"] = d2; res["D2 predictions passed (Holm < 0.05, right sign)"] = pred
# D3 dwell and cycle time
res["D3 median episode length, sessions (IQR)"] = {p_: [float(ep[ep.phase == p_].n.median()), [float(ep[ep.phase == p_].n.quantile(.25)), float(ep[ep.phase == p_].n.quantile(.75))]] for p_ in ORDER}
st = ep[ep.phase != "OTHER"].reset_index(drop=True); cyc = []
i = 0
while i < len(st):
    if st.phase[i] == "CALM":
        j, want = i + 1, 1; seen = []
        while j < len(st) and want < 4:
            if st.phase[j] == ORDER[want]: want += 1
            elif st.phase[j] == "CALM": break
            j += 1
        if want == 4:
            k = j
            while k < len(st) and st.phase[k] != "CALM": k += 1
            if k < len(st): cyc.append(f.index.get_loc(st.start[k]) - f.index.get_loc(st.start[i]))
        i = j if j > i else i + 1
    else: i += 1
res["D3 full cycles CALM -> THINNING -> THIN -> RECOVERY -> CALM"] = {"count": len(cyc), "median sessions": float(np.median(cyc)) if cyc else None, "IQR": [float(np.quantile(cyc, .25)), float(np.quantile(cyc, .75))] if cyc else None}
# D4 expiry alignment
def opex(d):
    x = pd.Timestamp(d.year, d.month, 15); x = x + pd.Timedelta(days=(4 - x.weekday()) % 7)
    if d > x:
        m2 = d + pd.offsets.MonthBegin(1); x = pd.Timestamp(m2.year, m2.month, 15); x = x + pd.Timedelta(days=(4 - x.weekday()) % 7)
    return x
idx = f.index; tox = np.array([np.searchsorted(idx, opex(d)) - i for i, d in enumerate(idx)])
f["to_opex"] = pd.cut(tox, [-1, 4, 9, 14, 40], labels=["0-4", "5-9", "10-14", "15+"])
res["D4 phase share by sessions to monthly expiry"] = pd.crosstab(f.to_opex, f.phase, normalize="index").round(3).to_dict(orient="index")
# cross-check: SPY intraday thinness by phase
d = daily_from_bars([B / "SPY2020_rth_d2.parquet", B / "SPYarcx_rth_d2.parquet"]); Lp = pct_trailing(d.L_raw.rolling(5).mean())
xc = f.join(Lp.rename("Lp"), how="inner").dropna(subset=["Lp"])
res["cross-check: SPY thinness pct by phase (2020-26)"] = xc.groupby("phase").Lp.mean().round(3).to_dict()
res["today"] = {"date": str(f.index[-1].date()), "phase": f.phase.iloc[-1], "GEX pct": round(float(gp.iloc[-1]), 3), "VIX": round(float(vx.iloc[-1]), 2),
                "VIX needed for RECOVERY (0.85 x 10d max)": round(float(0.85 * vx.rolling(10).max().iloc[-1]), 2), "last 10 phases": f.phase.iloc[-10:].tolist()}
f[["gp", "vix", "close", "phase"]].to_csv(HERE / "out" / "phases.csv")
json.dump(res, open(HERE / "out" / "q2.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
