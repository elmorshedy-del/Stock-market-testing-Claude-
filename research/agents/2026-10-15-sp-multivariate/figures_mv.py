"""Figure for the S&P multivariate study: out/fig_mv.png."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE / "out"
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
S1, S2, S3, NULL = "#2a78d6", "#eb6834", "#1baf7a", "#a9a8a2"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})
LAB = {"VOL": "Volatility only", "FULL": "Everything stacked", "FULL_NO_NFCI": "Everything, no NFCI",
       "V+M": "Vol + slow macro", "V+O": "Vol + options/flow/gamma", "V+R": "Vol + momentum/RSI",
       "V+S": "Vol + stretch"}


def main():
    R = json.loads((OUT / "results_mv.json").read_text())
    PH = json.loads((OUT / "posthoc_mv.json").read_text())
    P = pd.read_pickle(DATA / "preds.pkl")
    raw = pd.read_pickle(DATA / "features_raw.pkl")
    fig = plt.figure(figsize=(9, 13))

    # 1 out-of-sample AUC by layer
    ax = fig.add_axes([0.33, 0.69, 0.62, 0.25])
    r = R["Y_CORR|GBM"]
    order = ["VOL", "FULL", "FULL_NO_NFCI", "V+M", "V+O", "V+S", "V+R"]
    y = np.arange(len(order))[::-1]
    for yy, s in zip(y, order):
        a = r[s]["auc"]
        col = INK2 if s == "VOL" else (S1 if s == "V+R" else NULL)
        if s != "VOL":
            lo, hi = r[s]["d_auc_ci95"]
            ax.plot([r["VOL"]["auc"] + lo, r["VOL"]["auc"] + hi], [yy, yy], color=GRID, lw=6, solid_capstyle="round", zorder=1)
        ax.scatter([a], [yy], s=70, color=col, zorder=3, edgecolor=SURF, linewidth=2)
        ax.text(a, yy + 0.3, f"{a:.2f}", fontsize=8.5, color=INK, ha="center")
    ax.axvline(r["VOL"]["auc"], color=INK2, lw=0.8, ls="--")
    ax.axvline(0.5, color=GRID, lw=1)
    ax.set_yticks(y)
    ax.set_yticklabels([LAB[s] for s in order], fontsize=9)
    ax.set_ylim(-0.6, len(order) - 0.3)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0.38, 0.78)
    ax.set_xlabel("AUC on years the model never saw, 2000-2026 (0.5 = coin flip)\ngray bar: 95% range from resampling years",
                  fontsize=9)
    ax.set_title(f"1. Warning of a 10%+ S&P fall within 13 weeks ({r['events']} falls):\n"
                 f"    only momentum/RSI beats volatility (shift-test p {PH['P1']['familywise_p_max']:.2f})",
                 loc="left", fontsize=10.5, color=INK, fontweight="bold")

    # 2 direction
    ax = fig.add_axes([0.33, 0.37, 0.62, 0.22])
    t = PH["P4_rate_by_tercile"]
    feats = [("R_DIST_SMA40", "S&P vs its 40-week average"), ("R_BREADTH", "Share of stocks above 200-day avg"),
             ("R_MOM26", "26-week momentum"), ("R_RSI_W", "Weekly RSI")]
    w = 0.26
    for k, (f, lab) in enumerate(feats):
        yy = len(feats) - 1 - k
        for j, (q, col) in enumerate((("low", S2), ("mid", NULL), ("high", S1))):
            v = 100 * t[f][q]
            ax.barh(yy + (1 - j) * w, v, height=w * 0.9, color=col)
            ax.text(v + 0.6, yy + (1 - j) * w, f"{v:.0f}%", va="center", fontsize=8)
    ax.set_yticks(range(len(feats)))
    ax.set_yticklabels([lab for _, lab in feats][::-1], fontsize=9)
    ax.grid(axis="y", visible=False)
    ax.axvline(100 * R["Y_CORR|GBM"]["base_rate"], color=INK2, lw=0.8, ls="--")
    ax.set_xlabel("share of weeks followed by a 10%+ fall within 13 weeks, 2000-2026 (dashed = all weeks)", fontsize=9)
    for j, (q, col) in enumerate((("weakest third", S2), ("middle third", NULL), ("strongest third", S1))):
        ax.scatter([], [], color=col, marker="s", s=60, label=q)
    ax.set_ylim(-0.55, len(feats) + 0.15)
    ax.legend(frameon=False, fontsize=8.5, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.02))
    ax.set_title("2. The warning is a broken trend, not an overbought one:\n"
                 "    weak momentum and breadth come before falls; high RSI does not", loc="left", fontsize=10.5,
                 color=INK, fontweight="bold")

    # 3 by regime
    ax = fig.add_axes([0.33, 0.05, 0.62, 0.22])
    g = P[(P.outcome == "Y_CORR") & (P.model == "GBM") & (P.year != "now")]
    piv = g.pivot_table(index="week", columns="spec", values="p")
    yv = raw.Y_CORR.reindex(piv.index)
    ok = yv.notna()
    piv, yv = piv[ok], yv[ok]
    eras = [("2000-2009", piv.index < "2010-01-01"), ("2010 - Sep 2019", (piv.index >= "2010-01-01") & (piv.index < "2019-10-04")),
            ("Oct 2019 - 2026 (new options era)", piv.index >= "2019-10-04")]
    specs = [("VOL", INK2), ("V+O", NULL), ("V+R", S1)]
    w = 0.26
    for k, (lab, m) in enumerate(eras):
        yy = len(eras) - 1 - k
        for j, (s, col) in enumerate(specs):
            a = roc_auc_score(yv[m], piv.loc[m, s])
            ax.barh(yy + (1 - j) * w, a, height=w * 0.9, color=col)
            ax.text(a + 0.004, yy + (1 - j) * w, f"{a:.2f}", va="center", fontsize=8)
    ev = [PH["P3"][e]["events"] for e in ("2000-2009", "2010-2019Q3", "2019Q4-2026")]
    ax.set_yticks(range(len(eras)))
    ax.set_yticklabels([f"{lab}\n{n} falls" for (lab, _), n in zip(eras, ev)][::-1], fontsize=9)
    ax.set_xlim(0.4, 0.8)
    ax.axvline(0.5, color=INK2, lw=0.8)
    ax.grid(axis="y", visible=False)
    for s, col in specs:
        ax.scatter([], [], color=col, marker="s", s=60, label=LAB[s])
    ax.set_ylim(-0.55, len(eras) + 0.15)
    ax.legend(frameon=False, fontsize=8, loc="upper center", ncol=3, bbox_to_anchor=(0.45, 1.02))
    ax.set_xlabel("AUC by era (0.5 = coin flip)", fontsize=9)
    ax.set_title("3. Momentum/RSI holds in every era; options/flow turns useless after 2019",
                 loc="left", fontsize=10.5, color=INK, fontweight="bold")
    fig.savefig(OUT / "fig_mv.png", dpi=150)
    plt.close(fig)
    print("figure written")


if __name__ == "__main__":
    main()
