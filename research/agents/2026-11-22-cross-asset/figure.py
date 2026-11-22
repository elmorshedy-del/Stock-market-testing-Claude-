"""Two phases of the 2026 selloff: prices, the 10-year yield, gold against what yields predict, and the fingerprint scores."""
import json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analysis import load, COLS

H = Path(__file__).resolve().parent
SURF, INK, INK2, MUTED, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"          # slots 1-3, validated all-pairs (light)
SHADE1, SHADE2 = "#f1f0ec", "#e7e6e0"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.3, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF})
F = json.load(open(H / "out" / "fingerprints.json"))
x = load(); a0 = "2026-08-31"; w = x.loc[a0:"2026-11-20"]
P1, P2 = ("2026-09-03", "2026-10-05"), ("2026-10-06", "2026-11-20")

def style(ax):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.grid(True, axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
    for (a, b), c in ((P1, SHADE1), (P2, SHADE2)): ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=c, zorder=0, lw=0)
def dates(ax, labels=True):
    t = [pd.Timestamp(d) for d in ["2026-09-01", "2026-09-15", "2026-10-01", "2026-10-15", "2026-11-01", "2026-11-15"]]
    ax.set_xticks(t); ax.set_xticklabels([d.strftime("%b %-d") for d in t] if labels else [])
    ax.set_xlim(pd.Timestamp(a0), pd.Timestamp("2026-11-24"))

fig = plt.figure(figsize=(17.5, 10.6))
axA = fig.add_axes([0.045, 0.40, 0.43, 0.39]); axB = fig.add_axes([0.045, 0.085, 0.43, 0.22])
axC = fig.add_axes([0.555, 0.40, 0.355, 0.39]); axD = fig.add_axes([0.555, 0.075, 0.42, 0.25]); axD.axis("off")

# A: prices indexed to 100 on Aug 31
for k, col, lab in (("STOCKS", BLUE, "S&P 500"), ("GOLD", AQUA, "Gold"), ("BTC", ORANGE, "Bitcoin")):
    s = 100 * w[k] / w[k].iloc[0]; axA.plot(s.index, s, color=col, lw=2.1, solid_capstyle="round")
    axA.text(s.index[-1] + pd.Timedelta(days=0.8), s.iloc[-1], f"{lab} {s.iloc[-1] - 100:+.0f}%", va="center", fontsize=10, color=INK)
style(axA); dates(axA, labels=False); axA.set_ylim(62, 112); axA.set_ylabel("index, Aug 31 = 100")
axA.text(pd.Timestamp("2026-09-04"), 64.5, "Phase 1: yields rise", fontsize=10, color=INK2, weight="bold")
axA.text(pd.Timestamp("2026-10-07"), 64.5, "Phase 2: everything falls but Treasuries", fontsize=10, color=INK2, weight="bold")
for d, t, y in (("2026-11-05", "Nov 5", 77), ("2026-11-20", "Nov 20", 70)):
    axA.annotate(t, xy=(pd.Timestamp(d), w.STOCKS.loc[d] / w.STOCKS.iloc[0] * 100), xytext=(pd.Timestamp(d) - pd.Timedelta(days=6), y),
                 fontsize=9.5, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
axA.set_title("A. Stocks, gold and bitcoin since Aug 31", loc="left", color=INK, fontsize=12, pad=8)

# B: 10-year yield
axB.plot(w.index, w.US10Y, color=INK2, lw=2.0); style(axB); dates(axB); axB.set_ylim(4.6, 5.45)
axB.set_ylabel("percent")
axB.annotate(f"5.31% on Oct 5, highest since 2002", xy=(pd.Timestamp("2026-10-05"), 5.311), xytext=(pd.Timestamp("2026-10-09"), 5.36), fontsize=9.6, color=INK,
             arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8), va="center")
axB.text(w.index[-1] + pd.Timedelta(days=0.8), w.US10Y.iloc[-1], f"{w.US10Y.iloc[-1]:.2f}%", va="center", fontsize=10, color=INK)
axB.set_title("B. US 10-year yield: up 54bp in phase 1, down 40bp in phase 2", loc="left", color=INK, fontsize=12, pad=8)

# C: gold actual vs what real yields and the dollar predict
gm = F["gold_model"]; r = x.pct_change() * 100
real = pd.read_csv(H / "data" / "FRED_DFII10.csv"); real.columns = ["d", "v"]; real["d"] = pd.to_datetime(real.d)
real = real.set_index("d").v.replace(".", np.nan).astype(float).reindex(x.index).ffill()
pred = gm["const"] + gm["per_bp_real"] * real.diff() * 100 + gm["per_pct_usd"] * r.USD
act_c = 100 * (1 + r.GOLD.loc[w.index[1:]] / 100).cumprod(); pre_c = 100 * (1 + pred.loc[w.index[1:]] / 100).cumprod()
act_c = pd.concat([pd.Series([100.0], index=[w.index[0]]), act_c]); pre_c = pd.concat([pd.Series([100.0], index=[w.index[0]]), pre_c])
axC.plot(pre_c.index, pre_c, color=MUTED, lw=2.0, ls=(0, (5, 3)))
axC.plot(act_c.index, act_c, color=AQUA, lw=2.2, solid_capstyle="round")
axC.fill_between(act_c.loc[P2[0]:].index, act_c.loc[P2[0]:], pre_c.loc[P2[0]:], color=AQUA, alpha=0.10, lw=0)
style(axC); dates(axC); axC.set_ylim(74, 106); axC.set_ylabel("index, Aug 31 = 100")
axC.text(pre_c.index[-1] + pd.Timedelta(days=0.8), pre_c.iloc[-1], f"what yields and the\ndollar predict {pre_c.iloc[-1] - 100:+.0f}%", va="center", fontsize=9.6, color=INK2, linespacing=1.25)
axC.text(act_c.index[-1] + pd.Timedelta(days=0.8), act_c.iloc[-1], f"gold, actual\n{act_c.iloc[-1] - 100:+.0f}%", va="center", fontsize=9.6, color=INK, linespacing=1.25)
axC.text(pd.Timestamp("2026-10-07"), 79.5, "Shaded gap: gold sold for reasons\nyields and the dollar cannot explain", fontsize=10, color=INK, linespacing=1.3)
axC.set_title("C. Gold against what real yields and the dollar predict", loc="left", color=INK, fontsize=12, pad=8)

# D: fingerprints
E = F["episodes"]; short = {"Discount-rate shock": "rate shock", "Growth scare": "growth scare", "Yen-carry unwind": "yen-carry unwind",
                            "Dollar-funded deleveraging": "forced selling, dollar-funded", "Loss of trust in US assets": "loss of trust in US"}
rows = [("2020 dash for cash", "forced selling, Treasuries sold too"), ("2022 rate shock", "rate shock"), ("2024 yen-carry unwind", "yen-carry unwind"),
        ("2025 tariff shock", "loss of trust in US"), ("2026 phase 1 (Sep 3 - Oct 5)", None), ("2026 phase 2 (Oct 6 - Nov 20)", None)]
axD.text(0.0, 1.0, "D. Which mechanism fits? Signs predicted from who is forced,\n    written before any episode was computed",
         fontsize=12, color=INK, va="top", transform=axD.transAxes)
hx = [0.0, 0.24, 0.31, 0.38, 0.45, 0.525, 0.62]
for xx, t in zip(hx, ["Episode", "Bonds", "Gold", "Dollar", "Yen", "Best fit (share of signs matched)", ""]):
    axD.text(xx, 0.80, t, fontsize=9.4, color=MUTED, transform=axD.transAxes, va="center")
axD.plot([0, 1], [0.75, 0.75], color=BASE, lw=1, transform=axD.transAxes)
arrow = {1: "▲", -1: "▼", 0: "–"}
for i, (name, known) in enumerate(rows):
    y = 0.67 - i * 0.118; e = E[name]; sg = e["signs"]; best = e["best"]; sc = e["match"][best]
    lab = name.replace(" (Sep 3 - Oct 5)", "").replace(" (Oct 6 - Nov 20)", "")
    axD.text(hx[0], y, lab, fontsize=10, color=INK, transform=axD.transAxes, va="center", weight="bold" if known is None else "normal")
    for xx, k in zip(hx[1:5], ["BONDS", "GOLD", "USD", "YEN"]):
        axD.text(xx + 0.012, y, arrow[sg[k]], fontsize=10.5, color=INK, transform=axD.transAxes, va="center")
    verdict = f"{short[best]} ({sc:.0%})"
    if known is not None:
        ok = short[best] == known
        verdict += "   ✓" if ok else "   ✗ (see note)"
    axD.text(hx[5], y, verdict, fontsize=10, color=INK, transform=axD.transAxes, va="center", weight="bold" if known is None else "normal")
axD.text(0.0, -0.05, "Bonds up with gold down is the giveaway: only forced selling sells gold while Treasuries rally.\n"
         "Note: 2020 was missed because my table had no case where even Treasuries are sold.", fontsize=9.3, color=INK2, transform=axD.transAxes, va="top", linespacing=1.4)

fig.text(0.022, 0.962, "The selloff has two phases. Rising yields fit only the first. The second is forced selling of everything except Treasuries.",
         fontsize=16, weight="bold", color=INK)
fig.text(0.022, 0.925, "Phase 1 (Sep 3 - Oct 5): the 10-year rose 54bp, almost all of it real yield. Gold fell, stocks still made a record. "
         "Phase 2 (Oct 6 - Nov 20): yields fell 40bp and long bonds rose, yet gold fell 16%,\nbitcoin 31% and the S&P 12%. "
         "The yen did not jump, so this is not a yen-carry unwind. Gold's correlation with stocks rose from 0.11 to 0.46.",
         fontsize=10.6, color=INK2, va="top", linespacing=1.45)
fig.text(0.022, 0.012, "Data: Yahoo daily closes, FRED (real 10-year yield). Gold model fitted on Jan 2023 - Aug 2026; the Nov 20 real-yield change is not yet published "
         "and is set to zero, which understates the prediction.", fontsize=8.6, color=MUTED)
out = H / "out" / "cross_asset.png"; fig.savefig(out, dpi=200); print(out)
