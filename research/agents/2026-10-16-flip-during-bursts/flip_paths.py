"""Descriptive event study (README.md, committed at 0b12c4d before the run): price, flip and positions from day -10
to +10 around TSLA up-bursts, split by the state at the close before the burst, with a random-day baseline.
Usage: OMP_NUM_THREADS=1 python flip_paths.py -> out/paths.csv, out/summary.json, out/flip_paths.png
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
sys.path.insert(0, str(MICRO))
from burst_gamma import state                      # noqa: E402  (originals, imported unchanged)
from common import load_bars                       # noqa: E402
from stock_now import burst_days                   # noqa: E402

W = 10
RNG = np.random.default_rng(20261016)
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def frame():
    g = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
    s = state("TSLA")[["near_pct"]]
    g = g.join(s)
    g["dist"] = 100 * (g.spot / g.flip_classic - 1)
    g["gn"] = g.gex_classic / (g.spot * (g.call_oi + g.put_oi) * 100)
    g["gn_pct"] = g.gn.rolling(252, min_periods=120).rank(pct=True)
    c = load_bars("TSLA").close
    bd = pd.Series(burst_days(c, 1), index=c.index).reindex(g.index).fillna(False).astype(bool)
    g["burst"] = bd
    return g


def paths(g, days):
    idx = {d: i for i, d in enumerate(g.index)}
    rows = []
    for d in days:
        i = idx[d]
        if i - W < 0 or i + W >= len(g):
            continue
        base = g.iloc[i - 1]
        for k in range(-W, W + 1):
            r = g.iloc[i + k]
            rows.append({"event": d, "k": k, "price": 100 * r.spot / base.spot, "flip": 100 * r.flip_classic / base.spot,
                         "dist": r.dist, "call_oi": 100 * (r.call_oi / base.call_oi - 1), "put_oi": 100 * (r.put_oi / base.put_oi - 1),
                         "near_pct": r.near_pct, "gn_pct": r.gn_pct, "call_wall": 100 * r.call_wall / base.spot, "put_wall": 100 * r.put_wall / base.spot})
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(exist_ok=True)
    g = frame()
    g = g[g.index >= "2020-03-01"]
    pre = g.shift(1)
    full = (pre.near_pct <= 1 / 3) & (pre.dist < 0)
    below_only = (pre.near_pct > 1 / 3) & (pre.dist < 0)
    above = pre.dist >= 0
    groups = {"from the full setup": g.index[g.burst & full], "from below the flip only": g.index[g.burst & below_only],
              "from above the flip": g.index[g.burst & above]}
    rand = g.index[W + 1:-W - 1]                                   # every eligible day (fewer than the 2,000 planned exist)
    P = {k: paths(g, v) for k, v in groups.items()}
    P["all days (baseline)"] = paths(g, rand)
    allp = pd.concat({k: v for k, v in P.items()}, names=["group"]).reset_index(level=0)
    allp.to_csv(OUT / "paths.csv", index=False)
    med = allp.groupby(["group", "k"]).median(numeric_only=True)
    summ = {}
    for grp in P:
        m = med.loc[grp]
        n = P[grp].event.nunique()
        summ[grp] = {"events": int(n), **{f"{col} at day {k}": float(m.loc[k, col]) for col in ("price", "flip", "dist", "call_oi", "put_oi", "near_pct", "gn_pct")
                                          for k in (-5, -1, 0, 1, 3, 5, 10)}}
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    figure(allp, med, P)
    return summ


def band(ax, allp, grp, col, color, label):
    z = allp[allp.group == grp].groupby("k")[col]
    m, lo, hi = z.median(), z.quantile(0.25), z.quantile(0.75)
    ax.plot(m.index, m, color=color, lw=2.2, label=label)
    ax.fill_between(m.index, lo, hi, color=color, alpha=0.12, lw=0)


def figure(allp, med, P):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, axs = plt.subplots(2, 3, figsize=(16, 9.2), gridspec_kw={"hspace": 0.45, "wspace": 0.28})
    grps = ["from the full setup", "from below the flip only", "from above the flip"]
    for ax, grp in zip(axs[0], grps):
        band(ax, allp, grp, "price", INK, "TSLA price")
        band(ax, allp, grp, "flip", ORANGE, "gamma flip")
        band(ax, allp, grp, "call_wall", GREEN, "call wall")
        ax.axvline(0, color=MUTED, ls=":", lw=1)
        ax.axhline(100, color=GRID, lw=1)
        ax.set_xlabel("sessions from the burst day")
        ax.set_ylabel("level, day -1 price = 100")
        ax.set_title(f"Up-bursts {grp} ({P[grp].event.nunique()} bursts)", loc="left", fontsize=10, color=INK)
        ax.legend(loc="upper left", frameon=False, fontsize=8)
    a, b, c = axs[1]
    for grp, col in zip(grps + ["all days (baseline)"], [ORANGE, BLUE, GREEN, MUTED]):
        m = med.loc[grp]
        a.plot(m.index, m.dist, color=col, lw=2, label=grp)
        b.plot(m.index, m.call_oi, color=col, lw=2, label=grp)
        b.plot(m.index, m.put_oi, color=col, lw=1.4, ls="--")
        c.plot(m.index, 100 * m.near_pct, color=col, lw=2, label=grp)
    a.axhline(0, color=INK, lw=1)
    a.set_ylabel("price vs flip, % (below 0 = below the flip)")
    a.set_title("Distance from the flip: median path", loc="left", fontsize=10, color=INK)
    b.set_ylabel("% change vs day -1 (solid calls, dashed puts)")
    b.set_title("Open interest added around the burst", loc="left", fontsize=10, color=INK)
    c.axhline(100 / 3, color=MUTED, ls=":", lw=1)
    c.set_ylabel("near-price OI, percentile (below dotted = freed)")
    c.set_title("Freed state: near-price OI percentile", loc="left", fontsize=10, color=INK)
    for ax in (a, b, c):
        ax.axvline(0, color=MUTED, ls=":", lw=1)
        ax.set_xlabel("sessions from the burst day")
        ax.legend(loc="best", frameon=False, fontsize=7.5)
    f.suptitle("TSLA up-bursts 2020-2026: how price, the flip and positions move around the burst day (medians; shaded = middle half)",
               x=0.01, ha="left", fontsize=11, color=INK, weight="bold")
    f.savefig(OUT / "flip_paths.png", dpi=150, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    s = main()
    for grp, v in s.items():
        print(f"\n{grp}: {v['events']} events")
        for col in ("price", "flip", "dist", "call_oi", "put_oi", "near_pct", "gn_pct"):
            print(f"  {col:9s} " + "  ".join(f"d{k:+d} {v[f'{col} at day {k}']:7.2f}" for k in (-5, -1, 0, 1, 3, 5, 10)))
