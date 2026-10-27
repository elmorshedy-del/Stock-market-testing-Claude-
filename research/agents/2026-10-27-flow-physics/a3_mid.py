"""A3 redo with mid-price proxies (bid-ask bounce removed): m_n = p_n/tick - eps_n/2 (ES: one-tick spread almost always;
TSLA: half-spread approximated as half a tick, a stated limit). Writes out/a3_mid.json (the A3 result of record)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from flowlib import load_trades, merge_orders, sign_acf, response, propagator

HERE = Path(__file__).resolve().parent; DATA = HERE / "data"
LAGS = np.unique(np.round(np.logspace(0, 3, 25)).astype(int))
EDGES = [0, 1, 2, 3, 5, 8, 12, 18, 27, 40, 60, 90, 135, 200, 300, 450, 700, 1000]
out = {}
for sym, tick in (("ES", 0.25), ("TSLA", 0.01)):
    E, M, ds = [], [], []
    for f in sorted(DATA.glob(f"{sym}_trades_*.parquet")):
        m = merge_orders(load_trades(f))
        e = m.sign.to_numpy().astype(float); mid = m.price.to_numpy() / tick - e / 2
        E.append(e); M.append(mid); ds.append(np.sign(mid[-1] - mid[0]))
    C = np.mean([sign_acf(e, LAGS) for e in E], axis=0)
    R = np.mean([response(e, m_, LAGS) for e, m_ in zip(E, M)], axis=0)
    fc = (LAGS >= 10) & (LAGS <= 1000) & (C > 0)
    gamma = -np.polyfit(np.log(LAGS[fc]), np.log(C[fc]), 1)[0]
    Gs = [propagator(e, m_, EDGES) for e, m_ in zip(E, M)]; ell = Gs[0][0]; G = np.mean([g[1] for g in Gs], axis=0)
    fg = (ell >= 5) & (ell <= 450) & (G > 0)
    beta = -np.polyfit(np.log(ell[fg]), np.log(G[fg]), 1)[0] if fg.sum() >= 3 else np.nan
    up = [i for i, s in enumerate(ds) if s > 0]; dn = [i for i, s in enumerate(ds) if s < 0]
    pers = lambda ids: float(np.median([response(E[i], M[i], [1000])[0] / response(E[i], M[i], [10])[0] for i in ids]))
    out[sym] = {"days": len(E), "gamma (sign memory, C ~ lag^-gamma)": round(float(gamma), 3),
                "C at 1/10/100/1000": [round(float(np.interp(L, LAGS, C)), 4) for L in (1, 10, 100, 1000)],
                "beta (impact decay, G ~ lag^-beta)": round(float(beta), 3), "(1-gamma)/2 (diffusive-price prediction)": round(float((1 - gamma) / 2), 3),
                "beta within +-0.1": bool(abs(beta - (1 - gamma) / 2) <= 0.1),
                "G in ticks at 1/10/100/450": [round(float(np.interp(L, ell, G)), 4) for L in (1, 10, 100, 450)],
                "R in ticks at 1/10/100/1000": [round(float(np.interp(L, LAGS, R)), 4) for L in (1, 10, 100, 1000)],
                "persistence R(1000)/R(10), median: up days / down days": [round(pers(up), 3), round(pers(dn), 3)], "up / down days": [len(up), len(dn)],
                "lags": LAGS.tolist(), "C": C.round(5).tolist(), "R": R.round(5).tolist(), "G_ell": ell.tolist(), "G": G.round(5).tolist()}
    print(sym, {k: v for k, v in out[sym].items() if k not in ("lags", "C", "R", "G_ell", "G")}, flush=True)
(HERE / "out" / "a3_mid.json").write_text(json.dumps(out, indent=1))
