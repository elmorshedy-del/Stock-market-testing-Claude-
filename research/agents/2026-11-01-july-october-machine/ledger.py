"""Mechanism ledger (pre-registered @ 88bca6a): gauges G1-G7 for July and October 2026 phases, with turn-force z-scores.
Usage: python ledger.py <yahoo dir> <DIX.csv> -> out/ledger.json, out/gauges.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; YF = Path(sys.argv[1])


def yf(t):
    r = json.load(open(YF / f"{t}.json"))["chart"]["result"][0]
    s = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").normalize().tz_localize(None))
    return s[~s.index.duplicated(keep="last")].dropna()


d = pd.read_csv(sys.argv[2], parse_dates=["date"]).set_index("date")
spy = yf("SPY"); idx = spy.loc["2020-01-01":].index
G = pd.DataFrame(index=idx)
G["G1 GEX $bn (SqueezeMetrics)"] = d.gex.reindex(idx) / 1e9
G["G2 DIX %"] = 100 * d.dix.reindex(idx)
G["G3 VIX"] = yf("%5EVIX").reindex(idx)
G["G3 VIX9D/VIX (event kink >1)"] = (yf("%5EVIX9D") / yf("%5EVIX")).reindex(idx)
G["G3 VIX/VIX3M (inverted >1)"] = (yf("%5EVIX") / yf("%5EVIX3M")).reindex(idx)
G["G4 QQQ/IWM (log x100)"] = 100 * np.log(yf("QQQ") / yf("IWM")).reindex(idx)
G["G4 SMH/SPY (log x100)"] = 100 * np.log(yf("SMH") / spy).reindex(idx)
G["G4 RSP/SPY (log x100)"] = 100 * np.log(yf("RSP") / spy).reindex(idx)
G["G5 HYG/IEF (log x100)"] = 100 * np.log(yf("HYG") / yf("IEF")).reindex(idx)
G["G6 10y yield %"] = yf("%5ETNX").reindex(idx)   # Yahoo ^TNX is quoted in percent
G["G6 dollar index"] = yf("DX-Y.NYB").reindex(idx)
lr = np.log(spy).diff()
G["G7 SPY 20d realized vol %"] = (100 * lr.rolling(20).std() * np.sqrt(252)).reindex(idx)
G["G7 SPY vs 50-day MA %"] = (100 * (spy / spy.rolling(50).mean() - 1)).reindex(idx)
G["SPY"] = spy.reindex(idx)
G = G.ffill(limit=2); G.loc["2026-06-01":].to_csv(HERE / "out" / "gauges.csv")
down_sign = {"G1 GEX $bn (SqueezeMetrics)": -1, "G2 DIX %": -1, "G3 VIX": 1, "G3 VIX9D/VIX (event kink >1)": 1, "G3 VIX/VIX3M (inverted >1)": 1,
             "G4 QQQ/IWM (log x100)": -1, "G4 SMH/SPY (log x100)": -1, "G4 RSP/SPY (log x100)": 1, "G5 HYG/IEF (log x100)": -1, "G6 10y yield %": 1,
             "G6 dollar index": 1, "G7 SPY 20d realized vol %": 1, "G7 SPY vs 50-day MA %": -1}
pts = {"Jul 10": "2026-07-10", "Jul 29": "2026-07-29", "Aug 4": "2026-08-04", "Aug 14": "2026-08-14", "Oct 9": "2026-10-09", "Oct 30": "2026-10-30"}
L = {}
for g, sgn in down_sign.items():
    s = G[g]; v = {k: round(float(s.loc[t]), 3) for k, t in pts.items()}
    sd4 = s.diff(4).loc["2020-03-01":].std(); sdl = s.diff(14).loc["2020-03-01":].std()
    jd, od, jt = v["Jul 29"] - v["Jul 10"], v["Oct 30"] - v["Oct 9"], v["Aug 4"] - v["Jul 29"]
    L[g] = {"values": v, "July down leg change": round(jd, 3), "Oct down leg change": round(od, 3),
            "July down-leg z (vs 14-session moves)": round(jd / sdl, 2), "Oct down-leg z": round(od / sdl, 2),
            "similar down force (both in down direction)": bool(np.sign(jd) == sgn and np.sign(od) == sgn),
            "July turn change": round(jt, 3), "July turn z (vs 4-session moves)": round(jt / sd4, 2),
            "July turn force (|z|>1 in rebound direction)": bool(np.sign(jt) == -sgn and abs(jt / sd4) > 1),
            "Oct 30 level vs Jul 29 level": "beyond July low-point stress" if (v["Oct 30"] - v["Jul 29"]) * sgn > 0 else "less stressed than July's low"}
json.dump(L, open(HERE / "out" / "ledger.json", "w"), indent=1)
for g, x in L.items():
    print(f"{g:34s} Jul10 {x['values']['Jul 10']:9.3f} Jul29 {x['values']['Jul 29']:9.3f} Aug4 {x['values']['Aug 4']:9.3f} | Oct9 {x['values']['Oct 9']:9.3f} Oct30 {x['values']['Oct 30']:9.3f} | "
          f"downz J {x['July down-leg z (vs 14-session moves)']:+.2f} O {x['Oct down-leg z']:+.2f} sim {str(x['similar down force (both in down direction)'])[0]} | turn z {x['July turn z (vs 4-session moves)']:+.2f} {'TURN' if x['July turn force (|z|>1 in rebound direction)'] else '    '} | {x['Oct 30 level vs Jul 29 level']}")
