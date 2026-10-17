"""Exploratory (descriptive, before any test): which objectively computable lines track the owner's hand-drawn TSLA channel?
Usage: OMP_NUM_THREADS=1 python explore.py -> out/explore_tsla.png, out/explore_gaps.csv"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-10-16-owner-channel-gamma"))
import channel_gamma as C                          # noqa: E402  (owner's lines, as reconstructed there)
from common import load_bars                       # noqa: E402

BOT = {"Jan 2023": "2023-01-03", "Apr 2024": "2024-04-22", "Apr 2025": "2025-04-08", "Jul 2026": "2026-07-29"}
GREENS = ["#0e6b4a", "#1baf7a", "#5fd0a5", "#a6e8cd"]


def series():
    raw = load_bars("TSLA")
    b = raw[(raw.index >= "2022-06-01") & (raw.index <= "2026-10-14")]
    tp = (b.high + b.low + b.close) / 3
    g = pd.read_csv(C.MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
    f = (g.spot / raw.close.reindex(g.index)).round().clip(lower=1)
    S = {}
    for n, d in BOT.items():
        m = b.index >= d
        S[f"cost basis since the {n} low (anchored VWAP)"] = (tp[m] * b.volume[m]).cumsum() / b.volume[m].cumsum()
    S["200-day average"] = b.close.rolling(200).mean()
    S["50-day average"] = b.close.rolling(50).mean()
    S["gamma flip (20-day median)"] = (g.flip_classic / f).reindex(b.index).rolling(20, min_periods=5).median()
    S["put wall (20-day median)"] = (g.put_wall / f).reindex(b.index).rolling(20, min_periods=5).median()
    S["call wall (20-day median)"] = (g.call_wall / f).reindex(b.index).rolling(20, min_periods=5).median()
    L = pd.DataFrame({k: C.line(b.index, k) for k in C.LINES}, index=b.index)
    return b, S, L


def main():
    b, S, L = series()
    rows = []
    for k, s in S.items():
        s = s.dropna()
        j = s.index.intersection(L.index)
        rows.append({"candidate": k, **{ln.split()[0]: round(100 * float(np.nanmedian(np.abs(np.log(s[j] / L.loc[j, ln])))), 1) for ln in C.LINES}})
    T = pd.DataFrame(rows).set_index("candidate")
    T.to_csv(HERE / "out" / "explore_gaps.csv")
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": C.MUTED, "axes.labelcolor": C.MUTED, "xtick.color": C.MUTED, "ytick.color": C.MUTED,
                         "figure.facecolor": C.SURF, "axes.facecolor": C.SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, (ax, az) = plt.subplots(1, 2, figsize=(17, 7), gridspec_kw={"width_ratios": [2.2, 1], "wspace": 0.12})
    for a, start in ((ax, "2022-06-01"), (az, "2026-06-15")):
        m = b.index >= start
        for k, lw in zip(C.LINES, (2.0, 1.4, 1.4, 2.0)):
            a.plot(b.index[m], L[k][m], color=C.CHAN, lw=lw, alpha=0.55)
        a.semilogy(b.index[m], b.close[m], color=C.INK, lw=1.4)
        for (k, s), col in zip(list(S.items())[:4], GREENS):
            s = s[s.index >= start]
            a.plot(s.index, s, color=col, lw=1.6)
        a.plot(b.index[m], S["200-day average"][m], color=C.MUTED, lw=1.3, ls="--")
        if a is az:
            a.plot(b.index[m], S["gamma flip (20-day median)"][m], color=C.ORANGE, lw=1.6)
            a.plot(b.index[m], S["put wall (20-day median)"][m], color=C.BLUE, lw=1.2, ls=":")
            a.plot(b.index[m], S["50-day average"][m], color=C.MUTED, lw=1.0, ls="-.")
        a.minorticks_off()
    az.xaxis.set_major_locator(mdates.MonthLocator())
    az.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_yticks([100, 150, 200, 300, 400, 500], ["100", "150", "200", "300", "400", "500"])
    az.set_yticks([280, 300, 320, 340, 360, 380, 400, 440], ["280", "300", "320", "340", "360", "380", "400", "440"])
    ax.set_title("TSLA with your lines (blue) and the cost basis since each low (greens; darkest = Jan 2023). Dashed grey = 200-day average",
                 loc="left", fontsize=9.5, color=C.INK)
    az.set_title("Since Jun 2026: cost basis since the July low, gamma flip (orange),\nput wall (blue dots), 50-day average (grey dash-dot) all converge near $350-358",
                 loc="left", fontsize=9.5, color=C.INK)
    f.suptitle("Exploratory: which computable lines track your hand-drawn TSLA channel? (descriptive, before any test)", x=0.01, ha="left",
               fontsize=11.5, color=C.INK, weight="bold")
    f.savefig(HERE / "out" / "explore_tsla.png", dpi=140, bbox_inches="tight", facecolor=C.SURF)
    return T


if __name__ == "__main__":
    print(main().to_string())
