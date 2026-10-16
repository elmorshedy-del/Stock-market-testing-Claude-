"""Figures for REPORT: out/fig_nvda.png, out/fig_tests.png. Reads out/results.json, out/posthoc.json, data/."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import tests as T

HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE / "out"
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
S1, S2, S3, NULL = "#2a78d6", "#eb6834", "#1baf7a", "#a9a8a2"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})

LABEL = {"FF_HIKE": "Fed hiking (12m)", "Y10_UP": "10y yield rising (6m)", "CURVE_FLAT": "Curve flat/inverted",
         "USD_UP": "Dollar rising (6m)", "M2_SLOW": "M2 growth slow", "MKT_EXT": "Nasdaq-100 at top of its channel",
         "MARGIN_FROTH": "Margin debt surging", "COMPOSITE": "Half or more of the above",
         "LIQ_DRAIN": "Fed liquidity draining", "TIPS_UP": "Real (TIPS) yield rising", "CREDIT_WIDEN": "Credit spreads widening",
         "GEX_LOW": "S&P dealer gamma low", "INV_GLUT": "Inventory outgrowing sales"}


def nvda_figure():
    ch, macro, inv = T.load()
    prices = pd.read_pickle(DATA / "monthly_prices.pkl")
    mo = prices[prices.symbol == "NVDA"].sort_index()
    nv = ch[(ch.symbol == "NVDA") & (ch.W == 84)].set_index("month")
    raw = T.raw_variables(macro, ch, 84)
    invm = T.inv_monthly(inv, macro.index)
    sig, inv_sig = T.signals(raw, invm, 2 / 3)
    sig["INV_GLUT"] = inv_sig["NVDA"]

    fig = plt.figure(figsize=(11, 8.6))
    ax = fig.add_axes([0.22, 0.40, 0.76, 0.53])
    x0 = pd.Timestamp("2012-01-01")
    m = mo[mo.index >= x0]
    ax.semilogy(m.index, m.close, color=INK, lw=1.6, label="NVDA monthly close", zorder=5)
    idx = {d: k for k, d in enumerate(mo.index)}
    for d, col, lab in ((pd.Timestamp("2018-09-30"), S1, "channel known at Sep 2018 top"),
                        (pd.Timestamp("2021-11-30"), S2, "channel known at Nov 2021 top"),
                        (mo.index[-1], S3, "channel known today")):
        r = nv.loc[d]
        i = idx[d]
        ks = np.arange(i - 83, min(i + 25, len(mo)))
        ks = ks[mo.index[ks] >= x0]
        c = r.a + r.b * ks
        dates = mo.index[ks]
        past = dates <= d
        for off, ls, w in ((r.lo, "-", 1.4), (r.hi, "-", 1.4), (0.0, ":", 1.0)):
            ax.plot(dates[past], np.exp(c[past] + off), color=col, lw=w, ls=ls, alpha=0.9)
            ax.plot(dates[~past], np.exp(c[~past] + off), color=col, lw=w, ls="--", alpha=0.9)
        ax.plot([], [], color=col, lw=1.4, label=lab)
        ax.scatter([d], [mo.close.loc[d]], s=46, color=col, edgecolor=SURF, linewidth=2, zorder=6)
    ax.plot([], [], color=INK2, ls="--", lw=1.2, label="dashed = the same lines carried forward (frozen)")
    ax.set_xlim(x0, mo.index[-1] + pd.offsets.MonthEnd(3))
    ax.set_ylim(0.15, 1500)
    ax.set_ylabel("price (split-adjusted, log scale)")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.set_title("NVDA: the 7-year channel as it could be drawn at each top (no hindsight)", loc="left",
                 color=INK, fontsize=12, fontweight="bold")
    last = nv.iloc[-1]
    ax.annotate(f"today ${mo.close.iloc[-1]:.0f}: middle of the channel", (mo.index[-1], mo.close.iloc[-1]),
                xytext=(-210, 40), textcoords="offset points", color=INK2, fontsize=9,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))

    names = ["FF_HIKE", "Y10_UP", "CURVE_FLAT", "USD_UP", "M2_SLOW", "MKT_EXT", "MARGIN_FROTH",
             "LIQ_DRAIN", "TIPS_UP", "CREDIT_WIDEN", "GEX_LOW", "INV_GLUT"]
    bx = fig.add_axes([0.22, 0.06, 0.76, 0.29], sharex=ax)
    s = sig.loc[sig.index >= x0, names]
    for k, n in enumerate(names):
        on = s[n] == 1
        bx.bar(s.index[on], 0.72, bottom=len(names) - 1 - k - 0.36, width=31, color=S1, linewidth=0)
        na = s[n].isna()
        bx.bar(s.index[na], 0.72, bottom=len(names) - 1 - k - 0.36, width=31, color=GRID, linewidth=0)
    bx.set_yticks(range(len(names)))
    bx.set_yticklabels([LABEL[n] for n in names[::-1]], fontsize=8.5)
    bx.set_ylim(-0.6, len(names) - 0.4)
    bx.grid(axis="y", visible=False)
    for d, col in ((pd.Timestamp("2018-09-30"), S1), (pd.Timestamp("2021-11-30"), S2)):
        bx.axvline(d, color=col, lw=1.2)
        ax.axvline(d, color=col, lw=0.6, alpha=0.4)
    bx.set_title("Signals ON (blue) = reading in the top third of its own last 10 years, as known that month; "
                 "gray = no data", loc="left", fontsize=9, color=INK2)
    fig.savefig(OUT / "fig_nvda.png", dpi=150)
    plt.close(fig)


def tests_figure():
    R = json.loads((OUT / "results.json").read_text())
    P = json.loads((OUT / "posthoc.json").read_text()) if (OUT / "posthoc.json").exists() else {}
    fig = plt.figure(figsize=(9, 14))
    # A
    ax = fig.add_axes([0.33, 0.845, 0.62, 0.10])
    paths = []
    for f in ("channels_boot.pkl", "channels_boot_extra.pkl"):
        if (DATA / f).exists():
            b = pd.read_pickle(DATA / f)
            b = b[b.valid & (b.z >= 0.5)]
            b = b[(b.t_rev <= 24) | (b.n_fwd >= 24)]
            paths += (b.t_rev <= 24).groupby(b.path).mean().tolist()
    paths = 100 * np.array(paths)
    ax.hist(paths, bins=np.arange(25, 52, 1), color=NULL, edgecolor=SURF, linewidth=1)
    real = 100 * R["A"]["real_rate_top"]
    ax.axvline(real, color=S1, lw=2.4)
    ax.text(real + 0.4, ax.get_ylim()[1] * 0.85, f"real stocks {real:.0f}%\n({int((paths >= real).sum())} of {len(paths)} random\nwalks do as well)", color=INK, fontsize=8.5, va="top")
    ax.set_xlabel("% of channel-top months that reach the lower line within 24 months")
    ax.set_yticks([])
    ax.set_title(f"A. Real stocks vs {len(paths)} random walks with each stock's own drift and vol (gray)",
                 loc="left", fontsize=10.5, color=INK, fontweight="bold")
    # B and C
    for pos, key, title, R2 in (([0.33, 0.455, 0.62, 0.29], "B", "B. Top of channel -> lower line within 24 months:\n    hit rate with signal ON minus OFF", R["B"]),
                                ([0.33, 0.075, 0.62, 0.29], "C", "C. Top of channel -> breakout above it within 24 months:\n    hit rate with easing signal ON minus OFF", R["C"]["vars"])):
        ax = fig.add_axes(pos)
        names = T.PRIMARY + T.SECONDARY
        names = [n for n in names if R2[n]["delta"] is not None]
        y = np.arange(len(names))[::-1]
        for yy, n in zip(y, names):
            r = R2[n]
            lo, hi = 100 * (r["null_mean"] - 1.645 * r["null_sd"]), 100 * (r["null_mean"] + 1.645 * r["null_sd"])
            ax.plot([lo, hi], [yy, yy], color=GRID, lw=7, solid_capstyle="round")
            col = S1 if r["p_shift"] < 0.05 else NULL
            ax.scatter([100 * r["delta"]], [yy], s=52, color=col, edgecolor=SURF, linewidth=2, zorder=3)
            pv = r["p_shift"]
            ax.text(100 * max(r["delta"], r["null_mean"] + 1.645 * r["null_sd"]) + 3, yy,
                    f"p {pv:.3f}" if pv < 0.01 else f"p {pv:.2f}",
                    va="center", fontsize=8, color=INK2)
        ax.axvline(0, color=INK2, lw=0.8)
        lab = LABEL if key == "B" else {**LABEL, "FF_HIKE": "Fed cutting (12m)", "Y10_UP": "10y yield falling",
                                         "CURVE_FLAT": "Curve steep", "USD_UP": "Dollar falling", "M2_SLOW": "M2 growth fast",
                                         "MKT_EXT": "Nasdaq-100 low in its channel", "MARGIN_FROTH": "Margin debt shrinking",
                                         "COMPOSITE": "Half or more easing", "LIQ_DRAIN": "Fed liquidity rising",
                                         "TIPS_UP": "Real yield falling", "CREDIT_WIDEN": "Credit tightening",
                                         "GEX_LOW": "S&P dealer gamma high", "INV_GLUT": "Inventory lean"}
        ax.set_yticks(y)
        ax.set_yticklabels([lab[n] for n in names], fontsize=8.5)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("difference in hit rate, points", fontsize=9)
        fam = R2[names[0]]["family_joint_p"], R2[names[-1]]["family_joint_p"]
        ax.set_title(f"{title}\n    family test p: top group {fam[0]:.2f}, bottom group {fam[1]:.2f} (pass needs < 0.05)",
                     loc="left", fontsize=10.5, color=INK, fontweight="bold")
        ax.axhline(len(T.SECONDARY) - 0.5, color=GRID, lw=1)
    fig.text(0.04, 0.012, "Gray bar: 90% of results when the signal is shifted in time (no real link). "
             "Blue dot: single-test p < 0.05,\nwhich is still not a pass on its own (the family test and both halves "
             "of history must agree).", fontsize=8.5, color=INK2)
    fig.savefig(OUT / "fig_tests.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    nvda_figure()
    tests_figure()
    print("figures written")
