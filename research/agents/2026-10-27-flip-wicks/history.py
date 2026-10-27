"""Pre-open flips (incl / excl 0DTE) for every SPY day 2020-01 .. 2026-10-12, and each day's 0DTE OI by strike (+-4%).
Per month in parallel. Output: out/preopen_levels.csv (derived), data/odte_oi.csv.gz (licensed-derived, gitignored)."""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from flipmap import norm, preopen, fine_flip, exposures, t

HERE = Path(__file__).resolve().parent
END = pd.Timestamp("2026-10-12")


def month_files():
    return sorted(p.name[4:11] for p in t.DIR.glob("SPY_20??-??_oi.csv.gz"))


def work(ym):
    months = month_files(); i = months.index(ym)
    oi = norm(pd.read_csv(t.DIR / f"SPY_{ym}_oi.csv.gz"))
    eods = [norm(pd.read_csv(t.DIR / f"SPY_{m}_eod.csv.gz")) for m in ([months[i - 1]] if i else []) + [ym]]
    eod = pd.concat(eods, ignore_index=True)
    edays = sorted(eod.date.unique())
    rows, odte = [], []
    for D in sorted(oi.date.unique()):
        if D > END:
            continue
        prev = [x for x in edays if x < D]
        if not prev:
            continue
        P = prev[-1]
        try:
            g = preopen(eod[eod.date == P], oi[oi.date == D], D)
            if len(g) < 50:
                continue
            S = float(g.underlying_close.median())
            has0 = bool((g.expiration == D).any())
            fi = fine_flip(g, S)
            fe = fine_flip(g[g.expiration > D], S) if has0 else fi
            share0 = float(exposures(g[g.expiration == D], S).gex.abs().sum() / exposures(g, S).gex.abs().sum()) if has0 else 0.0
            rows.append({"date": D, "prior": P, "S_prior": S, "flip_incl": fi, "flip_excl": fe, "has_0dte": has0, "share_0dte": share0,
                         "gex_open": float(exposures(g, S).gex.sum())})
            z = oi[(oi.date == D) & (oi.expiration == D)]
            if len(z):
                oc = next(c for c in z.columns if "open_interest" in c)
                z = z[z.strike.between(0.96 * S, 1.04 * S)]
                odte.append(z.groupby(["strike", "cp"])[oc].sum().unstack(fill_value=0).reset_index().assign(date=D))
        except Exception as e:                     # noqa: BLE001  (log and keep going; counted in the README)
            print(ym, D.date(), "error", str(e)[:80], flush=True)
    print(ym, len(rows), flush=True)
    return pd.DataFrame(rows), (pd.concat(odte, ignore_index=True) if odte else pd.DataFrame())


if __name__ == "__main__":
    ms = [m for m in month_files() if m <= "2026-10"]
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as p:
        res = p.map(work, ms)
    lv = pd.concat([r[0] for r in res], ignore_index=True).sort_values("date")
    od = pd.concat([r[1] for r in res if len(r[1])], ignore_index=True)
    (HERE / "out").mkdir(exist_ok=True); (HERE / "data").mkdir(exist_ok=True)
    lv.to_csv(HERE / "out" / "preopen_levels.csv", index=False)
    od.to_csv(HERE / "data" / "odte_oi.csv.gz", index=False)
    print("days", len(lv), "with 0DTE", int(lv.has_0dte.sum()), "flip missing", int(lv.flip_incl.isna().sum()))
