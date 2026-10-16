"""Figure for the technical-indicator study: where the indicators carry signal (Part A z-scores), and the two
setup refinements that matter now (Part B cells). Reads out/part_a.csv and out/today.csv; recomputes the Part B
cells with indicators.py. Usage: OMP_NUM_THREADS=1 python figures.py -> out/indicators.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import indicators as I

BLUE, ORANGE, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
CMAP = LinearSegmentedColormap.from_list("div", [BLUE, "#bcd3f0", "#efeeea", "#f6c7b0", ORANGE])
COLS = [(a, tf) for a in I.ASSETS for tf in I.TFS]


def heat(ax, A, stat, title):
    M = np.full((len(I.IND), len(COLS)), np.nan)
    for j, (a, tf) in enumerate(COLS):
        for i, ind in enumerate(I.IND):
            r = A[(A.asset == a) & (A.timeframe == tf) & (A.indicator == ind) & (A.statistic == stat)].iloc[0]
            M[i, j] = r.z
            ax.text(j, i, f"{r.z:+.1f}", ha="center", va="center", fontsize=7.5, color=SURF if abs(r.z) >= 3 else INK)
            if r.robust:
                ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, ec=INK, lw=2.4))
    im = ax.imshow(np.clip(M, -4, 4), cmap=CMAP, vmin=-4, vmax=4, aspect="auto")
    ax.set_xticks(range(len(COLS)), [f"{a}\n{tf}" for a, tf in COLS], fontsize=8)
    ax.set_yticks(range(len(I.IND)), I.IND, fontsize=8)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(title, loc="left", fontsize=9.5, color=INK)
    return im


def cells(sym, key, out):
    F = I.setups()[sym]
    v = I.daily_aligned(sym, F.index)[key]
    y = F[out]
    rows = []
    for lab, m in (("low", v <= 1 / 3), ("middle", (v > 1 / 3) & (v < 2 / 3)), ("high", v >= 2 / 3)):
        mm = F.setup & m & y.notna()
        rows.append((lab, 100 * y[mm].mean() if mm.any() else np.nan, int(mm.sum()), I.episodes(mm.to_numpy())))
    return rows, 100 * y[F.setup & y.notna()].mean()


def bars(ax, rows, base, now, title, ylabel):
    xs = range(len(rows))
    cols = [MUTED if lab == now else "#9db9e6" for lab, *_ in rows]
    ax.bar(xs, [r[1] for r in rows], color=cols, width=0.62)
    ax.axhline(base, color=MUTED, ls=":", lw=1.2)
    for x, (lab, v, d, e) in zip(xs, rows):
        ax.text(x, (v if v == v else 0) + 1.5, f"{v:.0f}%\n{d} days / {e} ep.", ha="center", va="bottom", fontsize=8, color=INK)
    ax.set_xticks(list(xs), [f"{lab}{'  (now)' if lab == now else ''}" for lab, *_ in rows], fontsize=8.5)
    ax.set_ylim(0, 85)
    ax.set_ylabel(f"{ylabel}  (dotted: setup, any reading, {base:.0f}%)", fontsize=8.5)
    ax.set_title(title, loc="left", fontsize=9.5, color=INK)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def main():
    A = pd.read_csv(I.OUT / "part_a.csv")
    T = pd.read_csv(I.OUT / "today.csv")
    state = lambda a, tf, ind: T[(T.asset == a) & (T.timeframe == tf) & (T.indicator == ind)].state.iloc[0]
    f = plt.figure(figsize=(15, 10.5))
    f.patch.set_facecolor(SURF)
    gs = f.add_gridspec(2, 3, height_ratios=[1.15, 1], hspace=0.42, wspace=0.28)
    for k, (stat, t) in enumerate(zip(I.STATS, ("Direction: mean 10-bar return,\nindicator high minus low",
                                                   "Entry: chance of a big up move,\nhigh minus low",
                                                   "Exit: chance of a big down move,\nhigh minus low"))):
        hx = f.add_subplot(gs[0, k])
        im = heat(hx, A, stat, t)
    cb = f.colorbar(im, cax=hx.inset_axes([1.05, 0.0, 0.045, 1.0]))
    cb.set_label("z vs the time-shift null; box = survives the\nfamily-wise test, same sign in both eras", fontsize=8)
    cb.ax.tick_params(labelsize=8)
    a1, a2 = f.add_subplot(gs[1, 0:1]), f.add_subplot(gs[1, 1:2])
    rows, base = cells("TSLA", ("daily", "ATR%"), "up-burst within 3")
    bars(a1, rows, base, state("TSLA", "daily", "ATR%"), "TSLA full setup, by daily ATR%:\nup-burst within 3 sessions\npasses (p 0.001); low cell only 8 episodes", "% of setup days")
    rows, base = cells("MSFT", ("daily", "Trend distance"), "up-leg within 10")
    bars(a2, rows, base, state("MSFT", "daily", "Trend distance"), "MSFT release setup, by distance above\nits 200-day: up-leg within 10 sessions\nlead only (p 0.053; bar was 0.0042)", "% of setup days")
    ax = f.add_subplot(gs[1, 2])
    ax.axis("off")
    ax.text(0, 1, "What it means now (data to Oct 15)", fontsize=10, color=INK, weight="bold", va="top")
    lines = ["MSFT: 24% above its 200-day (99th pct).",
             "  Alone: big 10-day up moves 16% vs 24%",
             "  when it sits low (the one robust result);",
             "  average return still positive, no extra",
             "  downside. Expect a grind, not a jump.",
             "",
             "TSLA: daily ATR at its 2nd percentile.",
             "  If the setup turns on with ATR this low,",
             "  past setups produced no 3-day burst",
             "  (0 of 11 days). Bursts are fixed-size",
             "  moves, so low volatility mechanically",
             "  makes them rarer.",
             "",
             "Nothing else survives: TSLA's indicators",
             "carry no robust signal on any timeframe."]
    for i, s in enumerate(lines):
        ax.text(0, 0.9 - i * 0.062, s, fontsize=8.8, color=INK, va="top", family="DejaVu Sans")
    f.suptitle("Technical indicators on TSLA and MSFT: one robust signal alone (MSFT stretched above its 200-day = fewer big up moves); "
               "inside our setups, volatility and stretch matter", x=0.01, ha="left", fontsize=11, color=INK, weight="bold")
    f.savefig(I.OUT / "indicators.png", dpi=150, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    main()
