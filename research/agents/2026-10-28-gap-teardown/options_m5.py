"""M5 options features at the open (engine chains, local ThetaData; positions = OI dated D, IVs = prior close; 0DTE kept).
For TSLA, NVDA, MSFT, MU, QQQ events between 2020-01 and 2026-10-14. Usage: python options_m5.py  -> out/options_m5.csv"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm, preopen, fine_flip, gex_at, exposures, t       # noqa: E402

smp = pd.read_csv(HERE / "out" / "sample.csv", parse_dates=["date"])
F = pd.read_csv(HERE / "out" / "features.csv", parse_dates=["date"])
cache = {}


def month(sym, ym, kind):
    k = (sym, ym, kind)
    if k not in cache:
        f = t.DIR / f"{sym}_{ym}_{kind}.csv.gz"
        cache[k] = norm(pd.read_csv(f)) if f.exists() else pd.DataFrame()
    return cache[k]


rows = []
ev = F[F.sym.isin(["TSLA", "NVDA", "MSFT", "MU", "QQQ"]) & (F.date >= "2020-01-15") & (F.date <= "2026-10-14")]
for r in ev.itertuples():
    D = r.date
    oi = pd.concat([month(r.sym, f"{D:%Y-%m}", "oi")]); oi = oi[oi.date == D] if len(oi) else oi
    if not len(oi): continue
    prevm = (D - pd.offsets.MonthBegin(1)).strftime("%Y-%m")
    eod = pd.concat([month(r.sym, prevm, "eod"), month(r.sym, f"{D:%Y-%m}", "eod")])
    if not len(eod): continue
    P = eod.date[eod.date < D].max()
    try:
        g = preopen(eod[eod.date == P], oi, D)
        S = float(r.open_px)
        k = exposures(g, S).groupby("K").gex.sum()
        near = k[(k.index >= S * 0.95) & (k.index <= S * 1.05)]
        pos = near[near > 0]
        kmax = float(pos.idxmax()) if len(pos) else np.nan
        below = pos[pos.index < S]; big = below[below >= 0.5 * pos.max()] if len(pos) else below
        tot = float(exposures(g, S).gex.sum())
        rows.append({"sym": r.sym, "date": D, "M5a open above biggest +gamma strike": float(S > kmax) if np.isfinite(kmax) else np.nan,
                     "M5b dealer gamma at open >0": float(tot > 0), "M5c distance to big +gamma support below (sig)": ((S - float(big.index.max())) / S / r.sig) if len(big) else np.nan,
                     "open vs flip (sig)": (S / fine_flip(g, S) - 1) / r.sig, "gamma 1 sig below open, $bn": gex_at(g, S * (1 - r.sig)) / 1e9, "gamma at open, $bn": tot / 1e9})
    except Exception as e:
        print("m5 err", r.sym, D.date(), str(e)[:80])
pd.DataFrame(rows).to_csv(HERE / "out" / "options_m5.csv", index=False)
print("options rows", len(rows))
