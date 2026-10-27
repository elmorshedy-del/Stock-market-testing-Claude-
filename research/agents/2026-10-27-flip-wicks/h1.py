"""H1: the pre-open flip as a ceiling from below / floor from above, vs a circular-shift null (pre-registered @ ffed9e4).
Usage: python h1.py <folder with SPY_1d.json>  -> out/h1.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BANDS = [0.0005, 0.0010, 0.0015, 0.0025, 0.0040]
NSHIFT, MINSHIFT = 500, 20


def daily(folder):
    r = json.loads((Path(folder) / "SPY_1d.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return d[~d.index.duplicated(keep="last")].dropna()


def shares(o, h, l, c, L, b):
    """Return [up stall, up reject, down stall, down hold] shares and their event counts."""
    up = o < L; dn = o > L
    ru = up & (h >= L * (1 - b)); rd = dn & (l <= L * (1 + b))
    out = [np.mean(h[ru] <= L[ru] * (1 + b)) if ru.any() else np.nan, np.mean(c[ru] < L[ru]) if ru.any() else np.nan,
           np.mean(l[rd] >= L[rd] * (1 - b)) if rd.any() else np.nan, np.mean(c[rd] > L[rd]) if rd.any() else np.nan]
    return np.array(out), (int(ru.sum()), int(rd.sum()))


def run(df, col, rng_shifts):
    o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    rel = (df[col] / df.open - 1).to_numpy()
    real = {b: shares(o, h, l, c, o * (1 + rel), b) for b in BANDS}
    null = {b: np.array([shares(o, h, l, c, o * (1 + np.roll(rel, k)), b)[0] for k in rng_shifts]) for b in BANDS}
    return real, null


if __name__ == "__main__":
    lv = pd.read_csv(HERE / "out" / "preopen_levels.csv", parse_dates=["date"]).set_index("date")
    df = lv.join(daily(sys.argv[1]), how="inner").dropna(subset=["flip_incl", "flip_excl", "open"])
    df = df[df.index <= "2026-10-12"]
    rng = np.random.default_rng(0)
    shifts = rng.integers(MINSHIFT, len(df) - MINSHIFT, NSHIFT)
    names = ["up stall", "up reject", "down stall", "down hold"]
    cells, zs, zn = {}, [], []
    for col in ("flip_incl", "flip_excl"):
        real, null = run(df, col, shifts)
        for b in BANDS:
            r, (nu, nd) = real[b]; nm = null[b]
            for j, nme in enumerate(names):
                mu, sd = np.nanmean(nm[:, j]), np.nanstd(nm[:, j])
                p = float(np.mean(nm[:, j] >= r[j]))
                cells[f"{col} b={b:.2%} {nme}"] = {"real": round(float(r[j]), 4), "null mean": round(float(mu), 4), "diff": round(float(r[j] - mu), 4),
                                                   "p": round(p, 4), "events": nu if j < 2 else nd}
                zs.append((r[j] - mu) / sd); zn.append((nm[:, j] - mu) / sd)
    zn = np.array(zn)
    joint = float(np.mean(np.nanmedian(zn, axis=0) >= np.nanmedian(zs)))
    prim = {k: cells[f"flip_incl b=0.15% {k}"] for k in ("up stall", "up reject")}
    # descriptive splits for the primary cells
    def split(mask, label):
        d = df[mask]; s = rng.integers(MINSHIFT, max(MINSHIFT + 1, len(d) - MINSHIFT), 300)
        real, null = run(d, "flip_incl", s); r, (nu, nd) = real[0.0015]
        return {label: {"days": int(len(d)), "up-reach events": nu, "up stall real / null": [round(float(r[0]), 3), round(float(np.nanmean(null[0.0015][:, 0])), 3)],
                        "p stall": round(float(np.mean(null[0.0015][:, 0] >= r[0])), 3),
                        "up reject real / null": [round(float(r[1]), 3), round(float(np.nanmean(null[0.0015][:, 1])), 3)],
                        "p reject": round(float(np.mean(null[0.0015][:, 1] >= r[1])), 3)}}
    rnd = (np.abs(df.flip_incl / 5 - np.round(df.flip_incl / 5)) * 5) <= 0.5
    splits = {}
    for m, lab in ((df.index < "2023-01-01", "2020-22"), (df.index >= "2023-01-01", "2023-26"), (rnd, "flip within $0.50 of a $5 multiple"),
                   (~rnd, "flip NOT near a $5 multiple"), (df.gex_open < 0, "dealers short gamma at the open (incl 0DTE)"), (df.gex_open > 0, "dealers long gamma at the open")):
        splits.update(split(m.to_numpy() if hasattr(m, "to_numpy") else m, lab))
    res = {"days": int(len(df)), "first": str(df.index[0].date()), "last": str(df.index[-1].date()),
           "PRIMARY (incl 0DTE, b 0.15%, up-approach)": prim, "primary passes (both p < 0.05)": bool(all(v["p"] < 0.05 for v in prim.values())),
           "multiverse joint p (median z, 40 cells)": joint, "median z": float(np.nanmedian(zs)), "cells": cells, "splits": splits}
    (HERE / "out" / "h1.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "cells"}, indent=1))
    for k, v in cells.items():
        print(f"{k:42s} real {v['real']:.3f} null {v['null mean']:.3f} diff {v['diff']:+.3f} p {v['p']:.3f} n {v['events']}")
