"""out/rsi_gamma_precedents.png: SPY RSI by frame, Friday's dealer hedge flow decomposition, and post-2020 precedents.
Usage: python figure.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
R = json.loads((OUT / "rsi.json").read_text()); F = pd.read_csv(OUT / "flow_path.csv", index_col=0); P = json.loads((OUT / "precedents.json").read_text())
GREEN, RED, INK, MUTED, SURF, BLUE, AMBER, GREY = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#e8a33d", "#c9c8c3"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.parse_math": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(19, 13)); gs = fig.add_gridspec(2, 3, hspace=0.42, wspace=0.28)
# 1 RSI ladder
a = fig.add_subplot(gs[0, 0]); fr = ["1-hour", "4-hour", "daily", "weekly", "monthly"]
v = [R[k]["RSI"] for k in fr]; pc = [R[k]["trailing pct"] for k in fr]
cols = [RED if p < 1 / 3 else GREEN if p > 2 / 3 else AMBER for p in pc]
a.bar(fr, v, color=cols, width=0.6); a.axhline(70, color=MUTED, ls=":", lw=0.8); a.axhline(30, color=MUTED, ls=":", lw=0.8); a.axhline(50, color=MUTED, lw=0.5)
for i, (x, p) in enumerate(zip(v, pc)): a.text(i, x + 1.5, f"{x:.0f}\n({p:.0%} pct)", ha="center", fontsize=9.5)
a.set_ylim(0, 90); a.set_ylabel("RSI(14)")
a.text(-0.4, 84, "red = weakest third of its own history\ngreen = strongest third", fontsize=8.5, color=MUTED)
a.set_title("1. SPY RSI: short frames washed out, weekly\n    in its weak third, monthly trend strong", loc="left", fontsize=11.5, weight="bold", color=INK)
# 2 flow path
a = fig.add_subplot(gs[0, 1:]); x = np.arange(len(F))
cum = lambda c: F[c].cumsum() / 1e9
a.fill_between(x, 0, cum("0DTE gamma") + cum("0DTE charm") + cum("0DTE vanna"), color=AMBER, alpha=0.55, label="expiring Oct 30 options (all greeks)")
a.plot(x, cum("later gamma"), color=RED, lw=1.8, label="later expiries: gamma (price moves)")
a.plot(x, cum("later vanna"), color=BLUE, lw=1.8, label="later expiries: vanna (VIX moves)")
a.plot(x, cum("all charm"), color=GREEN, lw=1.8, label="all: charm (time passing)")
tot = cum("all gamma") + cum("all charm") + cum("all vanna"); a.plot(x, tot, color=INK, lw=2.6, label="TOTAL dealer hedging")
a.axhline(0, color=MUTED, lw=0.6); a.set_ylabel("cumulative dealer hedge trades, $bn (− = selling)")
a2 = a.twinx(); a2.plot(x, F.spy, color=GREY, lw=1.2); a2.set_ylabel("SPY", color=MUTED); a2.spines["right"].set_visible(True)
lo = int(np.argmin(F.spy.values)); a.axvline(lo, color=MUTED, ls=":", lw=0.8); a.text(lo, tot.min() * 1.02, f" SPY low {F.spy.min():.2f} ({F.index[lo]})", fontsize=9, color=MUTED, va="top")
tk = [i for i, t in enumerate(F.index) if t.endswith(":00") or t == F.index[-1]]; a.set_xticks(tk); a.set_xticklabels([F.index[i] for i in tk])
a.legend(loc="lower left", frameon=False, fontsize=9)
a.set_title("2. Friday: hedging added ~$28-33bn of selling into the afternoon low; only ~29% came from the EXPIRING options.\n    Most was later-dated puts (gamma) plus rising vol (vanna). Time decay (charm) bought slightly. All of it reversed into the close",
            loc="left", fontsize=11.5, weight="bold", color=INK)
# 3 precedents S1/S2 SPY +4w
a = fig.add_subplot(gs[1, 0])
for i, (k, lab, col) in enumerate((("S1 rotation weeks", "rotation weeks\n(n 24)", BLUE), ("S2 TSLA holds in a tech-selloff week", "TSLA held while\ntech sold (n 8)", RED))):
    vals = [r["SPY +4w %"] for r in P[k]["per match"].values() if r["in averages"] and r["SPY +4w %"] == r["SPY +4w %"]]
    a.scatter(np.full(len(vals), i) + np.random.default_rng(0).uniform(-0.12, 0.12, len(vals)), vals, color=col, s=30, alpha=0.8)
    a.hlines(np.median(vals), i - 0.25, i + 0.25, color=INK, lw=2); a.text(i + 0.28, np.median(vals), f"median {np.median(vals):+.1f}%\n{np.mean(np.array(vals) > 0):.0%} up", fontsize=9, va="center")
base = P["S1 rotation weeks"]["summary"]["SPY +4w"]; a.axhline(base["base mean %"], color=MUTED, ls="--", lw=0.8); a.text(1.45, base["base mean %"] + 0.4, f"any week +{base['base mean %']:.1f}% ({base['base % up']}% up)", fontsize=8.5, color=MUTED, ha="right")
a.set_xticks([0, 1]); a.set_xticklabels(["rotation weeks\n(n 24)", "TSLA held while\ntech sold (n 8)"]); a.set_xlim(-0.5, 1.9); a.set_ylabel("SPY 4 weeks later, %"); a.axhline(0, color=MUTED, lw=0.5)
a.set_title("3. Since 2020: all three together = 0 precedents.\n    The two halves point opposite ways", loc="left", fontsize=11.5, weight="bold", color=INK)
# 4 S2 table
a = fig.add_subplot(gs[1, 1:]); a.axis("off")
a.text(0, 0.97, "TSLA held while tech sold (QQQ week ≤ −1.5%, TSLA beat QQQ by ≥ 5 pts), since 2020: what came next", fontsize=11.5, weight="bold", color=INK, transform=a.transAxes, va="top")
hdr = ["week ending", "QQQ wk", "TSLA−QQQ", "SPY +1w", "SPY +4w", "SPY worst 4w", "TSLA +1w", "TSLA +4w", "context"]
ctx = {"2020-01-31": "pre-COVID", "2020-02-21": "COVID crash began", "2020-06-12": "2020 melt-up", "2022-03-04": "2022 bear", "2022-04-22": "2022 bear", "2022-09-16": "2022 bear",
       "2023-02-10": "post-rally chop", "2025-03-28": "tariff crash next", "2026-08-21": "this year"}
xs = [0, 0.11, 0.19, 0.28, 0.36, 0.44, 0.54, 0.62, 0.71]
for j, h in enumerate(hdr): a.text(xs[j], 0.88, h, fontsize=9.5, color=MUTED, weight="bold", transform=a.transAxes)
for i, (d, r) in enumerate(P["S2 TSLA holds in a tech-selloff week"]["per match"].items()):
    yy = 0.81 - i * 0.075; row = [d, f"{r['QQQ wk %']:+.1f}%", f"{r['TSLA-QQQ']:+.1f}", f"{r['SPY +1w %']:+.1f}%", f"{r['SPY +4w %']:+.1f}%", f"{r['SPY worst within 4w %']:+.1f}%", f"{r['TSLA +1w %']:+.1f}%", f"{r['TSLA +4w %']:+.1f}%", ctx.get(d, "")]
    for j, c in enumerate(row):
        col = INK if j in (0, 1, 2, 8) else (GREEN if c.startswith("+") and c != "+0.0%" else RED)
        a.text(xs[j], yy, c, fontsize=9.5, color=col, transform=a.transAxes)
s2 = P["S2 TSLA holds in a tech-selloff week"]["summary"]
a.text(0, 0.08, f"Non-overlapping 8: SPY +4w median {s2['SPY +4w']['median %']:+.1f}% ({s2['SPY +4w']['% up']}% up) vs any week +{s2['SPY +4w']['base mean %']:.1f}% ({s2['SPY +4w']['base % up']}% up); SPY worst within 4w median {s2['SPY worst within 4w']['median %']:.1f}% vs {s2['SPY worst within 4w']['base median %']:.1f}%.\n"
       f"TSLA's strength did not carry: TSLA +1w median {s2['TSLA +1w']['median %']:+.1f}% ({s2['TSLA +1w']['% up']}% up). Most cases sat inside bear phases (2020 crash, 2022, 2025 tariffs), unlike this week's narrow-breadth dip.",
       fontsize=9.5, color=INK, transform=a.transAxes, va="bottom")
fig.suptitle("SPY RSI by frame · was Friday expiring gamma? · post-2020 precedents for this week", x=0.01, ha="left", fontsize=15, weight="bold", color=INK)
fig.savefig(OUT / "rsi_gamma_precedents.png", dpi=115, bbox_inches="tight"); print("ok")
