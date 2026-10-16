"""Round-2 figures: out/fig_r2_why.png (why prediction fails), out/fig_r2_tests.png (the confirmatory tests)."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import r2_lib as L

OUT, PREV = L.OUT, L.PREV
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
S1, S2, S3, NULL = "#2a78d6", "#eb6834", "#1baf7a", "#a9a8a2"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})
NAMES = {"FF_HIKE": "Fed hiking", "Y10_UP": "10y yield rising", "CURVE_FLAT": "Curve flat/inverted",
         "USD_UP": "Dollar rising", "M2_SLOW": "M2 growth slow", "MARGIN_FROTH": "Margin debt surging",
         "LIQ_DRAIN": "Fed liquidity draining", "TIPS_UP": "Real yield rising", "CREDIT_WIDEN": "Credit widening",
         "GEX_LOW": "S&P dealer gamma low", "DIX_LOW": "Dark-pool buying low", "VIX_HIGH": "VIX high",
         "VIX_INVERT": "VIX curve inverted", "AVG_CORR": "Stocks moving together", "MKT_EXT": "Nasdaq stretched"}


def why():
    R = json.loads((OUT / "results_r2.json").read_text())
    E = json.loads((OUT / "explore_r2.json").read_text())
    fig = plt.figure(figsize=(9, 13))
    # 1 calibration
    ax = fig.add_axes([0.11, 0.70, 0.84, 0.24])
    d = pd.DataFrame(R["C2"]["calibration_deciles"])
    ax.plot([0, 70], [0, 70], color=INK2, lw=1.0, ls="--")
    ax.plot(d.pred * 100, d.real * 100, color=S1, lw=2, marker="o", ms=7, mec=SURF, mew=2)
    ax.set_xlim(0, 70)
    ax.set_ylim(0, 70)
    ax.set_xlabel("random-walk odds of touching the lower line in 24 months (distance vs volatility), %")
    ax.set_ylabel("what actually happened, %")
    ax.text(52, 47, "dashed = perfect forecast", color=INK2, fontsize=8.5)
    ax.annotate("even calm stocks far from the line\ntouch it 20% of the time: market-wide crashes",
                (d.pred.iloc[0] * 100, d.real.iloc[0] * 100), xytext=(21, 29), textcoords="data", fontsize=8.5,
                color=INK2, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    c2 = R["C2"]
    ax.set_title(f"1. Distance and volatility rank the risk better than channel position (AUC {c2['auc_barrier']:.2f} vs "
                 f"{c2['auc_z']:.2f}),\n    but real touches run about double the random-walk odds", loc="left",
                 fontsize=10.5, color=INK, fontweight="bold")
    # 2 drift
    ax = fig.add_axes([0.11, 0.42, 0.84, 0.18])
    e7 = E["E7"]
    vals = [100 * (np.exp(12 * e7["median_channel_slope_per_month"]) - 1),
            100 * (np.exp(12 * e7["median_realised_drift_per_month"]) - 1)]
    ax.barh([1, 0], vals, color=[S2, S1], height=0.55)
    for yv, v, lab in ((1, vals[0], "how fast the channel's lines rise"), (0, vals[1], "how fast the stock actually rose next")):
        ax.text(v + 0.5, yv, f"{v:.0f}% a year", va="center", fontsize=9.5, color=INK)
        ax.text(0.5, yv + 0.38, lab, fontsize=9, color=INK2)
    ax.set_yticks([])
    ax.set_xlim(0, max(vals) * 1.35)
    ax.set_ylim(-0.5, 1.75)
    ax.set_xlabel("median over 5,241 top-of-channel stock-months with 24 months of history after them")
    ax.set_title("2. After a stock reaches the top, it grows slower than its channel:\n    the lower line partly "
                 "catches up with price instead of price falling to it", loc="left", fontsize=10.5, color=INK,
                 fontweight="bold")
    # 3 lead-lag
    ax = fig.add_axes([0.11, 0.05, 0.84, 0.27])
    ll = pd.read_csv(OUT / "e1_leadlag.csv")
    piv = ll.pivot_table(index=["var", "k"], columns="group", values="on_share").reset_index()
    piv["gap"] = 100 * (piv.reverting - piv["not"])
    for v, col in (("VIX_HIGH", S1), ("MARGIN_FROTH", S2), ("AVG_CORR", S3), ("CREDIT_WIDEN", NULL)):
        g = piv[piv["var"] == v]
        ax.plot(g.k, g.gap, color=col, lw=2, label=NAMES[v])
    ax.axvline(0, color=INK2, lw=0.8)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.text(0.3, ax.get_ylim()[1] * 0.9, "last month at the top", color=INK2, fontsize=8.5)
    ax.set_xlabel("months from the last month at the top of the channel")
    ax.set_ylabel("signal ON: tops that fell minus\ntops that didn't, % points")
    ax.legend(frameon=False, fontsize=8.5, loc="lower left", ncol=2)
    ax.set_title("3. Tops that fell vs tops that didn't: volatility was high all along, margin debt peaks at the top,\n"
                 "    stocks start moving together only after (1,216 episodes, 124 stocks; exploratory)", loc="left",
                 fontsize=10.5, color=INK, fontweight="bold")
    fig.savefig(OUT / "fig_r2_why.png", dpi=150)
    plt.close(fig)


def tests():
    R = json.loads((OUT / "results_r2.json").read_text())
    R1 = json.loads((PREV / "out" / "results.json").read_text())
    fig = plt.figure(figsize=(9, 11))
    ax = fig.add_axes([0.33, 0.80, 0.62, 0.13])
    m1 = R1["B"]["MARGIN_FROTH"]
    c1 = R["C1"]
    bars = [("Tech stocks (round 1,\nwhere the lead came from)", 100 * m1["delta"], m1["p_shift"], S2),
            ("93 fresh non-tech stocks\n(round 2, the real test)", 100 * c1["delta"], c1["p_shift"], S1)]
    for k, (lab, v, p, col) in enumerate(bars):
        ax.barh(1 - k, v, color=col, height=0.55)
        ax.text(v + 1, 1 - k, f"+{v:.0f} points, p {p:.2f}", va="center", fontsize=9.5, color=INK)
    ax.set_yticks([1, 0])
    ax.set_yticklabels([b[0] for b in bars], fontsize=9)
    ax.set_xlim(0, 50)
    ax.set_xlabel("extra chance a channel top falls to the lower line when margin debt is surging, points")
    ax.set_title("C1. The margin-debt lead does not hold up on fresh stocks", loc="left", fontsize=10.5,
                 color=INK, fontweight="bold")
    ax = fig.add_axes([0.33, 0.07, 0.62, 0.62])
    C3 = R["C3"]
    names = list(C3["vars"])
    y = np.arange(len(names))[::-1]
    for yy, n in zip(y, names):
        r = C3["vars"][n]
        if r["delta"] is None:
            continue
        col = S1 if r["p_shift"] < 0.05 else NULL
        ax.scatter([100 * r["delta"]], [yy], s=60, color=col, edgecolor=SURF, linewidth=2, zorder=3)
        ax.text(100 * r["delta"] + (3 if r["delta"] >= 0 else -3), yy,
                f"p {r['p_shift']:.2f}" + ("  (few swings)" if r["underpowered"] else ""),
                va="center", ha="left" if r["delta"] >= 0 else "right", fontsize=8, color=INK2)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([NAMES[n] for n in names], fontsize=9)
    ax.set_xlim(-60, 75)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("difference in how often a top fell to the lower line within 26 weeks, ON minus OFF, points")
    ax.set_title(f"C3. S&P 500 zoomed in (weekly, 3-year channels since 1928): {C3['episode_totals']['episodes']} tops, "
                 f"\n     {C3['episode_totals']['reverting']} fell to the lower line in {C3['episode_totals']['waves']} "
                 f"waves. Family test p {C3['family_minp']:.2f}: nothing passes", loc="left", fontsize=10.5,
                 color=INK, fontweight="bold")
    fig.text(0.04, 0.012, "Blue dot: single-test p < 0.05, not a pass on its own. \"Few swings\": fewer than 6 "
             "independent drops inside that signal's history.", fontsize=8.5, color=INK2)
    fig.savefig(OUT / "fig_r2_tests.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    why()
    tests()
    print("figures written")
