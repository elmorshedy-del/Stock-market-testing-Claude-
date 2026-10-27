"""A1 (signed flow, Kyle lambda), A2 (Hawkes branching ratio), A3 (propagator, gamma vs beta), A6 (TSLA composition) per session.
Pre-registered @ bdc698c. Usage: python a_flow.py  -> out/a_daily.csv, out/a_hawkes.csv, out/a3.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from flowlib import load_trades, merge_orders, kyle_lambda, hawkes_day, sign_acf, response, propagator

HERE = Path(__file__).resolve().parent; DATA = HERE / "data"
LAGS = np.unique(np.round(np.logspace(0, 3, 25)).astype(int))
EDGES = [0, 1, 2, 3, 5, 8, 12, 18, 27, 40, 60, 90, 135, 200, 300, 450, 700, 1000]
rows, hk, a3 = [], [], {}
for sym, tick in (("ES", 0.25), ("TSLA", 0.01)):
    eps_all, p_all, day_sign = [], [], []
    for f in sorted(DATA.glob(f"{sym}_trades_*.parquet")):
        day = pd.Timestamp(f.stem.split("_")[-1])
        d = load_trades(f)
        if len(d) < 1000:
            continue
        m = merge_orders(d)
        start = pd.Timestamp(f"{day.date()} 13:30", tz="UTC")
        o, c, h, l = d.price.iloc[0], d.price.iloc[-1], d.price.max(), d.price.min()
        bv, sv = d["size"][d.sign > 0].sum(), d["size"][d.sign < 0].sum()
        lam, r2 = kyle_lambda(d)
        odd = (d["size"] < 100).mean() if sym == "TSLA" else np.nan
        hw = hawkes_day(m, start).assign(sym=sym, day=day.date())
        hk.append(hw)
        rows.append({"sym": sym, "day": day.date(), "open": o, "close": c, "high": h, "low": l, "ret %": 100 * (c / o - 1),
                     "volume": int(d["size"].sum()), "buy vol": int(bv), "sell vol": int(sv), "delta": int(bv - sv), "delta % of vol": 100 * (bv - sv) / (bv + sv),
                     "orders": len(m), "lambda (pts per 1k net)": lam * 1000, "lambda R2": r2,
                     "hawkes n median": float(hw.n.median()), "hawkes n max": float(hw.n.max()),
                     "retail-size share (<100 sh)": odd, "unsigned share": float((d.side == "N").mean())})
        eps_all.append(m.sign.to_numpy()); p_all.append(m.price.to_numpy() / tick); day_sign.append(np.sign(c - o))
        print(sym, day.date(), round(rows[-1]["ret %"], 2), "delta%", round(rows[-1]["delta % of vol"], 2), "n", round(rows[-1]["hawkes n median"], 3), flush=True)
    # A3: pooled over days (statistics computed within each day, then averaged)
    C = np.mean([sign_acf(e, LAGS) for e in eps_all], axis=0)
    Rr = np.mean([response(e, p, LAGS) for e, p in zip(eps_all, p_all)], axis=0)
    fitC = (LAGS >= 10) & (LAGS <= 1000) & (C > 0)
    gamma = -np.polyfit(np.log(LAGS[fitC]), np.log(C[fitC]), 1)[0]
    Gs = [propagator(e, p, EDGES) for e, p in zip(eps_all, p_all)]
    ell = Gs[0][0]; G = np.mean([g[1] for g in Gs], axis=0)
    fitG = (ell >= 5) & (ell <= 450) & (G > 0)
    beta = -np.polyfit(np.log(ell[fitG]), np.log(G[fitG]), 1)[0] if fitG.sum() >= 3 else np.nan
    up = [i for i, s in enumerate(day_sign) if s > 0]; dn = [i for i, s in enumerate(day_sign) if s < 0]
    pers = lambda ids: float(np.mean([response(eps_all[i], p_all[i], [1000])[0] / response(eps_all[i], p_all[i], [10])[0] for i in ids])) if ids else np.nan
    a3[sym] = {"days": len(eps_all), "sign ACF C(lag) at 1/10/100/1000": [round(float(np.interp(L, LAGS, C)), 4) for L in (1, 10, 100, 1000)],
               "gamma (C ~ lag^-gamma, lags 10-1000)": round(float(gamma), 3),
               "propagator G(lag) in ticks at 1/10/100/1000": [round(float(np.interp(L, ell, G)), 4) for L in (1, 10, 100, 1000)],
               "beta (G ~ lag^-beta, lags 5-450)": round(float(beta), 3), "diffusivity prediction (1-gamma)/2": round(float((1 - gamma) / 2), 3),
               "beta within +-0.1 of (1-gamma)/2": bool(abs(beta - (1 - gamma) / 2) <= 0.1),
               "response R(lag) ticks at 1/10/100/1000": [round(float(np.interp(L, LAGS, Rr)), 3) for L in (1, 10, 100, 1000)],
               "persistence R(1000)/R(10): up days / down days": [round(pers(up), 3), round(pers(dn), 3)],
               "lags": LAGS.tolist(), "C": C.round(5).tolist(), "R": Rr.round(4).tolist(), "G_ell": ell.tolist(), "G": G.round(5).tolist()}
pd.DataFrame(rows).to_csv(HERE / "out" / "a_daily.csv", index=False)
pd.concat(hk).to_csv(HERE / "out" / "a_hawkes.csv", index=False)
(HERE / "out" / "a3.json").write_text(json.dumps(a3, indent=1))
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("lags", "C", "R", "G_ell", "G")} for k, v in a3.items()}, indent=1))
