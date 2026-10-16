"""The owner's named TSLA moves, bottom to top (design in README.md, committed at 7bbb370 before the run).
Per move: price, gamma flip (below-flip zone shaded), call/put walls, dealer-gamma percentile strip, freed strip.
Usage: OMP_NUM_THREADS=1 python named_moves.py -> out/named_moves.png, out/named_moves_table.csv
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
sys.path.insert(0, str(MICRO))
from burst_gamma import state                      # noqa: E402  (originals, imported unchanged)
from common import load_bars                       # noqa: E402
from named_weeks import MOVES                      # noqa: E402

PAD = 10
BLUE, ORANGE, GREEN, PURPLE, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#8a5cc2", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
GCMAP = LinearSegmentedColormap.from_list("g", [BLUE, "#bcd3f0", "#efeeea", "#f6c7b0", ORANGE])


def data():
    g = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
    g = g.join(state("TSLA")[["near_pct"]])
    c = load_bars("TSLA").close
    g["close"] = c.reindex(g.index)
    f = (g.spot / g.close).apply(lambda r: min((1.0, 3.0, 15.0), key=lambda x: abs(x - r)))   # split factor raw -> adjusted
    for col in ("spot", "flip_classic", "call_wall", "put_wall"):
        g[col] = g[col] / f
    g["gn"] = g.gex_classic / (g.spot * f * (g.call_oi + g.put_oi) * 100)
    g["gpct"] = g.gn.rolling(252, min_periods=120).rank(pct=True)
    g["below"] = g.spot < g.flip_classic
    g["freed"] = g.near_pct <= 1 / 3
    return g, c


def locate(c, a, b):
    i_a, i_b = c.index.searchsorted(pd.Timestamp(a)), c.index.searchsorted(pd.Timestamp(b) + pd.Timedelta(days=4), side="right") - 1
    seg = c.iloc[i_a:i_b + 16]
    top = seg.idxmax()
    seg0 = c.iloc[max(i_a - 15, 0):c.index.get_loc(top) + 1]
    return seg0.idxmin(), top


def table(g, c):
    rows = []
    for name, _, a, b in MOVES:
        bot, top = locate(c, a, b)
        z = g.loc[bot:top]
        after = g.loc[top:].iloc[:11]
        rb, rt = g.loc[bot], g.loc[top]
        rows.append({"move": name, "bottom": bot.date(), "top": top.date(), "sessions": len(z) - 1, "gain %": 100 * (rt.close / rb.close - 1),
                     "bottom: % vs flip": 100 * (rb.spot / rb.flip_classic - 1), "bottom: gamma pct": rb.gpct, "bottom: freed": bool(rb.freed),
                     "rally: share of days below flip": float(z.below.iloc[1:].mean()), "flip change bottom->top %": 100 * (rt.flip_classic / rb.flip_classic - 1),
                     "top: % vs flip": 100 * (rt.spot / rt.flip_classic - 1), "top: gamma pct": rt.gpct, "top: freed": bool(rt.freed),
                     "max gamma pct in rally": float(z.gpct.max()), "10 sessions after top %": 100 * (after.close.iloc[-1] / rt.close - 1)})
    return pd.DataFrame(rows)


def figure(g, c, T, pad=30):
    import matplotlib.dates as mdates
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f = plt.figure(figsize=(17, 27))
    outer = f.add_gridspec(4, 2, hspace=0.30, wspace=0.13)
    for k, ((name, _, a, b), row) in enumerate(zip(MOVES, T.itertuples())):
        inner = outer[k // 2, k % 2].subgridspec(3, 1, height_ratios=[3.4, 1, 1], hspace=0.12)
        ax, ag, an = f.add_subplot(inner[0]), f.add_subplot(inner[1]), f.add_subplot(inner[2])
        bot, top = pd.Timestamp(row.bottom), pd.Timestamp(row.top)
        i0, i1 = max(g.index.get_loc(bot) - pad, 0), min(g.index.get_loc(top) + pad, len(g) - 1)
        z = g.iloc[i0:i1 + 1]
        d = z.index
        px = z.spot
        fl = z.flip_classic.rolling(3, center=True, min_periods=1).median()       # display smoothing only
        ok = fl.notna().to_numpy()
        ax.fill_between(d, px, fl, where=ok & (px < fl).to_numpy(), interpolate=True, color=BLUE, alpha=0.28, lw=0)
        ax.fill_between(d, px, fl, where=ok & (px >= fl).to_numpy(), interpolate=True, color=ORANGE, alpha=0.14, lw=0)
        ax.plot(d, fl, color=ORANGE, lw=2.2)
        ax.plot(d, px, color=INK, lw=2.2)
        for t, lab in ((bot, "bottom"), (top, "top")):
            ax.axvline(t, color=MUTED, ls=":", lw=1)
        lo, hi = np.nanmin([px.min(), fl.min()]), np.nanmax([px.max(), fl.max()])
        ax.set_ylim(lo * 0.93, hi * 1.12)
        ytop = hi * 1.11
        ax.text(bot, ytop, f" bottom {bot:%b %d} \\${g.loc[bot, 'spot']:.0f}", ha="left", va="top", fontsize=8, color=INK)
        ax.text(top, ytop, f" top {top:%b %d} \\${g.loc[top, 'spot']:.0f} (+{row._5:.0f}%)", ha="left", va="top", fontsize=8, color=INK)
        ax.scatter([bot, top], [g.loc[bot, "spot"], g.loc[top, "spot"]], s=28, color=INK, zorder=5)
        fm = f"flip {row._10:+.0f}%" if row._10 == row._10 else "no flip near the top"
        ax.set_title(f"{name.split(' (')[0]}: {row.sessions} sessions bottom to top; {100 * (1 - row._9):.0f}% of rally days above the flip; {fm}",
                     loc="left", fontsize=9.5, color=INK)
        if k == 0:
            from matplotlib.patches import Patch
            from matplotlib.lines import Line2D
            ax.legend(handles=[Line2D([], [], color=INK, lw=2.2, label="TSLA"), Line2D([], [], color=ORANGE, lw=2.2, label="gamma flip"),
                               Patch(color=BLUE, alpha=0.28, label="below the flip (dealers short gamma)"),
                               Patch(color=ORANGE, alpha=0.14, label="above the flip (dealers long gamma)")], loc="center left", frameon=False, fontsize=8)
        gp = (100 * z.gpct).rolling(3, center=True, min_periods=1).mean()
        ag.axhspan(0, 100 / 3, color=BLUE, alpha=0.08, lw=0)
        ag.axhspan(200 / 3, 100, color=ORANGE, alpha=0.08, lw=0)
        ag.plot(d, gp, color=INK, lw=1.6)
        ag.set_ylim(0, 100)
        ag.set_yticks([0, 50, 100])
        ag.set_ylabel("dealer\ngamma pct", fontsize=8)
        npct = (100 * z.near_pct).rolling(3, center=True, min_periods=1).mean()
        an.axhspan(0, 100 / 3, color=GREEN, alpha=0.12, lw=0)
        an.plot(d, npct, color=GREEN, lw=1.6)
        an.set_ylim(0, 100)
        an.set_yticks([0, 50, 100])
        an.set_ylabel("near-price\nOI pct", fontsize=8)
        for axx in (ax, ag, an):
            axx.axvline(bot, color=MUTED, ls=":", lw=1)
            axx.axvline(top, color=MUTED, ls=":", lw=1)
            axx.set_xlim(d[0], d[-1])
            axx.xaxis.set_major_locator(mdates.MonthLocator())
            axx.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.tick_params(labelbottom=False)
        ag.tick_params(labelbottom=False)
        if k == 0:
            ag.text(d[1], 88, "top third: dealers most long gamma", fontsize=7.5, color=MUTED, va="center")
            ag.text(d[1], 12, "bottom third: most short gamma", fontsize=7.5, color=MUTED, va="center")
            an.text(d[1], 16, "green band = freed (little OI near the price)", fontsize=7.5, color=MUTED, va="center")
    f.suptitle("The named TSLA moves, 30 trading days either side of each bottom and top.\n"
               "Blue = price below the gamma flip (dealers short gamma); orange = above it. Lines are lightly smoothed (3-day) for display.",
               x=0.01, ha="left", fontsize=12, color=INK, weight="bold", y=0.905)
    f.savefig(OUT / "named_moves.png", dpi=140, bbox_inches="tight", facecolor=SURF)


def main():
    OUT.mkdir(exist_ok=True)
    g, c = data()
    T = table(g, c)
    T.to_csv(OUT / "named_moves_table.csv", index=False)
    figure(g, c, T)
    return T


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print(main().round(2).to_string(index=False))
