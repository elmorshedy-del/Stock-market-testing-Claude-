"""Diagnostic (after A1 failed with corr -0.82, a signing artefact suspect): which minute's quote is contemporaneous with a minute's trades?
Uses only option prices (no SPY returns): for every contract-minute with volume, is the VWAP inside the bid-ask of minute t-1, t or t+1,
and which mid is closest? Usage: python quote_alignment.py  -> out/quote_alignment.json"""
import json

import numpy as np
import pandas as pd

import flows as Fl


def main():
    files = sorted(Fl.SRC.glob("*.csv.gz"))
    pick = files[::24]
    agg = {k: [] for k in ("inside t-1", "inside t", "inside t+1", "closest t-1", "closest t", "closest t+1", "closest avg(t,t+1)", "closest avg(t-1,t)")}
    for f in pick:
        piv, strikes, call, cols = Fl.M.load_day(pd.Timestamp(f.name[:8]))
        bid, ask, vol, vwap = (piv[k].to_numpy() for k in ("bid", "ask", "volume", "vwap"))
        ok = (bid > 0) & (ask > 0)
        mid = np.where(ok, (bid + ask) / 2, np.nan)
        sh = lambda a, k: np.vstack([np.full((1, a.shape[1]), np.nan), a[:-1]]) if k == -1 else (np.vstack([a[1:], np.full((1, a.shape[1]), np.nan)]) if k == 1 else a)
        m = (vol > 0) & (vwap > 0)
        for k, lab in ((-1, "t-1"), (0, "t"), (1, "t+1")):
            b, a = sh(np.where(ok, bid, np.nan), k), sh(np.where(ok, ask, np.nan), k)
            v = m & np.isfinite(b) & np.isfinite(a)
            agg[f"inside {lab}"].append(float(((vwap >= b - 1e-9) & (vwap <= a + 1e-9))[v].mean()))
        cands = {"t-1": sh(mid, -1), "t": mid, "t+1": sh(mid, 1), "avg(t,t+1)": np.nanmean(np.stack([mid, sh(mid, 1)]), 0), "avg(t-1,t)": np.nanmean(np.stack([sh(mid, -1), mid]), 0)}
        err = np.stack([np.abs(vwap - c) for c in cands.values()])
        v = m & np.all(np.isfinite(err), axis=0)
        best = np.argmin(err[:, v], axis=0)
        for i, lab in enumerate(cands):
            agg[f"closest {lab}"].append(float((best == i).mean()))
    res = {"days sampled": len(pick), **{k: float(np.mean(v)) for k, v in agg.items()}}
    (Fl.OUT / "quote_alignment.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
