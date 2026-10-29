"""C1 (pin pull) and C11 (own-dealer hedge pressure) from the local engine chains (TSLA, NVDA, QQQ; 2020-01-15 to 2026-10-14).
Positions = OI dated D (prior close); IVs = prior session's close (flipmap.preopen). Usage: python options_ctx.py -> out/options_ctx.csv"""
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm, preopen, exposures, t       # noqa: E402

C = pd.read_csv(HERE / "out" / "context.csv", parse_dates=["date"])
EV = C[C.sym.isin(["TSLA", "NVDA", "QQQ"]) & (C.date >= "2020-01-15") & (C.date <= "2026-10-14")]
_cache = {}


def month(sym, ym, kind):
    k = (sym, ym, kind)
    if k not in _cache:
        f = t.DIR / f"{sym}_{ym}_{kind}.csv.gz"
        _cache[k] = norm(pd.read_csv(f)) if f.exists() else pd.DataFrame()
    return _cache[k]


def one(r):
    D, sym = pd.Timestamp(r["date"]), r["sym"]
    try:
        oi = month(sym, f"{D:%Y-%m}", "oi"); oi = oi[oi.date == D] if len(oi) else oi
        if not len(oi): return None
        oc = next(c for c in oi.columns if "open_interest" in c)
        S = float(r["open1m"]); out = {"sym": sym, "date": D}
        # C1: largest call-OI strike among expiries in the next 3 trading days (D, D+1, D+2 sessions)
        lim = pd.bdate_range(D, periods=3)[-1]
        near = oi[(oi.cp == "C") & (oi.expiration >= D) & (oi.expiration <= lim)]
        if len(near):
            k = near.groupby("strike")[oc].sum(); K = float(k.idxmax())
            out["near_call_wall"] = K; out["near_call_oi"] = float(k.max())
            out["C1_pin"] = int(S > K and (S - K) / S / r["sig"] <= 1.5)
        else:
            out["C1_pin"] = 0
        prevm = (D.replace(day=1) - pd.Timedelta(days=1)).strftime("%Y-%m")
        eod = pd.concat([month(sym, prevm, "eod"), month(sym, f"{D:%Y-%m}", "eod")])
        P = eod.date[eod.date < D].max()
        g = preopen(eod[eod.date == P], oi, D)
        gex = float(exposures(g, S).gex.sum())
        out["gex_open_usd"] = gex
        out["C11_pressure"] = gex * (r["gap"] * 100) / r["adv_usd"]   # dealer $ to trade for the gap, as a share of 20-day $ volume (+ = dealers sell)
        return out
    except Exception as e:
        print("err", sym, D.date(), str(e)[:80], flush=True); return None


if __name__ == "__main__":
    res = []   # single process: the forked pool hung (no CPU, no output) on the first run
    for i, rec in enumerate(EV.sort_values(["sym", "date"]).to_dict(orient="records")):
        x = one(rec)
        if x: res.append(x)
        if i % 100 == 0: print("progress", i, "of", len(EV), flush=True)
    O = pd.DataFrame(res); O.to_csv(HERE / "out" / "options_ctx.csv", index=False)
    print(len(O), "of", len(EV), "events; C1 =1:", int(O.C1_pin.sum()), "; pressure quantiles", O.C11_pressure.quantile([.1, .5, .9]).round(4).to_dict())
