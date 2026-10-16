"""Pierce and reclaim (design in README.md, pre-registered at 41c1b14): freed days that trade below the flip but close
above it, against the full setup (close below) and days that never touch the flip.
Usage: OMP_NUM_THREADS=1 python pierce_reclaim.py -> out/results.json, out/report_days.csv, out/pierce_reclaim.png"""
import json
import os
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
os.chdir(MICRO)                                     # forecast.py reads data/DIX.csv by relative path
from common import load_bars                       # noqa: E402  (originals, imported unchanged)
from edge_lab import edge_test, load, marks, outcome   # noqa: E402
from tsla_eras import REACTIONS_2020               # noqa: E402

REACTIONS_2026 = ["2026-01-29", "2026-04-23", "2026-07-23"]     # Tesla's 2026 report dates (see owner-channel-gamma follow-up 2)
RNG = np.random.default_rng(20261016)
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def groups():
    x, c, sig, freed, pos = load()
    b = load_bars("TSLA").reindex(x.index)
    f = (x.spot / b.close).apply(lambda r: min((1.0, 3.0, 15.0), key=lambda k: abs(k - r)))
    fl = x.flip / f
    below = x.below.astype(bool).to_numpy()
    pierce = (b.low < fl).to_numpy() & ~below
    G = {"A  closed below the flip (full setup)": freed & below, "B  traded below, closed above": freed & pierce,
         "C  never traded below": freed & ~below & ~pierce}
    return x, c, b, fl, G, pierce


def rates(m, y):
    ok = m & ~np.isnan(y)
    return float(y[ok].mean()) if ok.any() else None


def main():
    OUT.mkdir(exist_ok=True)
    x, c, b, fl, G, pierce = groups()
    idx = x.index
    up3, dn3 = outcome(marks(c), idx, 3), outcome(marks(c, -1), idx, 3)
    res = {"analysis days": len(idx), "base up-burst within 3": float(np.nanmean(up3)), "base down-burst within 3": float(np.nanmean(dn3)), "groups": {}}
    for k, m in G.items():
        res["groups"][k] = {"days": int(m.sum()), "episodes": int((m & ~np.r_[False, m[:-1]]).sum()),
                            "up-burst within 3": rates(m, up3), "down-burst within 3": rates(m, dn3)}
    res["H1 (B, freed)"] = edge_test(list(G.values())[1], up3, RNG)
    res["H1 pass"] = bool(res["H1 (B, freed)"]["p"] < 0.05 and res["H1 (B, freed)"]["lift"] > 0)
    res["secondary: B on all days"] = {**edge_test(pierce, up3, RNG), "up-burst within 3": rates(pierce, up3), "down-burst within 3": rates(pierce, dn3)}
    res["check: A reproduces the full setup"] = edge_test(list(G.values())[0], up3, RNG)
    (OUT / "results.json").write_text(json.dumps(res, indent=1))

    allc = load_bars("TSLA")
    upm, rows = marks(allc.close), []
    for t in map(pd.Timestamp, REACTIONS_2020 + REACTIONS_2026):
        if t not in idx:
            continue
        j = allc.index.get_loc(t)
        pc = allc.close.iloc[j - 1]
        lo, cl, op = allc.low.iloc[j], allc.close.iloc[j], allc.open.iloc[j]
        rows.append({"reaction day": t.date(), "open vs prior close %": round(100 * (op / pc - 1), 1), "low vs prior close %": round(100 * (lo / pc - 1), 1),
                     "close vs prior close %": round(100 * (cl / pc - 1), 1), "low below the flip": bool(lo < fl.loc[t]),
                     "close vs flip %": round(100 * (cl / fl.loc[t] - 1), 1) if fl.loc[t] == fl.loc[t] else None,
                     "freed at close": bool(x.near_pct.loc[t] <= 1 / 3),
                     "up-burst in next 3": bool(upm.iloc[j + 1:j + 4].any()) if j + 3 < len(allc) else None,
                     "next 20 sessions %": round(100 * (allc.close.iloc[min(j + 20, len(allc) - 1)] / cl - 1), 1)})
    R = pd.DataFrame(rows)
    R.to_csv(OUT / "report_days.csv", index=False)
    figure(res, R)
    return res, R


def figure(res, R):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, (a, r) = plt.subplots(1, 2, figsize=(15, 5.6), gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.25})
    ks = list(res["groups"])
    y = np.arange(len(ks))[::-1]
    for yy, k in zip(y, ks):
        g = res["groups"][k]
        a.barh(yy + 0.19, 100 * g["up-burst within 3"], height=0.36, color=GREEN)
        a.barh(yy - 0.19, 100 * g["down-burst within 3"], height=0.36, color=ORANGE)
        a.text(100 * g["up-burst within 3"] + 1, yy + 0.19, f"{100 * g['up-burst within 3']:.0f}% up", va="center", fontsize=8.5, color=INK)
        a.text(100 * g["down-burst within 3"] + 1, yy - 0.19, f"{100 * g['down-burst within 3']:.0f}% down", va="center", fontsize=8.5, color=INK)
    a.axvline(100 * res["base up-burst within 3"], color=GREEN, ls=":", lw=1.2)
    a.axvline(100 * res["base down-burst within 3"], color=ORANGE, ls=":", lw=1.2)
    a.set_yticks(y, [f"{k}\n{res['groups'][k]['days']} days, {res['groups'][k]['episodes']} episodes" for k in ks])
    a.set_xlim(0, 60)
    a.set_xlabel("% of days with a burst in the next 3 sessions (dotted = all days)")
    h = res["H1 (B, freed)"]
    a.set_title(f"Freed days by where the day traded vs the flip (B vs all days: {100 * h['lift']:+.0f} pts, p {h['p']:.2f})", loc="left", fontsize=10, color=INK)
    z = R[R["low vs prior close %"] < 0].sort_values("close vs prior close %")
    for i, (_, row) in enumerate(z.iterrows()):
        lo, cl, up = row["low vs prior close %"], row["close vs prior close %"], row["up-burst in next 3"]
        under = bool(row["freed at close"]) and row["close vs flip %"] == row["close vs flip %"] and row["close vs flip %"] < 0   # full setup at that close
        col = GREEN if up else MUTED
        r.plot([lo, cl], [i, i], color=col, lw=2)
        r.scatter([lo], [i], s=14, color=col)
        r.scatter([cl], [i], s=40, color=col, marker="D" if under else "o", edgecolor=INK if under else "none")
        r.text(6, i, f"{pd.Timestamp(row['reaction day']):%b %Y}   next 20: {row['next 20 sessions %']:+.0f}%", va="center", fontsize=8, color=INK)
    r.axvline(0, color=INK, lw=0.8)
    r.set_yticks([])
    r.set_xlim(-17, 19)
    r.set_xlabel("% vs the prior close: line from the day's low to its close")
    r.set_title("Report days that traded below the prior close\n(green = up-burst within 3 sessions; diamond = full setup on at that close)",
                loc="left", fontsize=10, color=INK)
    f.suptitle("A dip below the flip that recovers by the close vs a close below it (TSLA 2021-2026, freed days)",
               x=0.01, ha="left", fontsize=11.5, color=INK, weight="bold", y=1.0)
    f.savefig(OUT / "pierce_reclaim.png", dpi=145, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    res, R = main()
    print(json.dumps(res, indent=1))
    pd.set_option("display.width", 220)
    print(R.to_string(index=False))
