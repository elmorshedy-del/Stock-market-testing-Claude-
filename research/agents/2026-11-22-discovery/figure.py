"""Discovery pass 1-2 in one figure: the funnel, out-of-sample skill against chance, the incremental test, and what current stress predicts."""
import json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

H = Path(__file__).resolve().parent
SURF, INK, INK2, MUTED, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.3, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF})
M = {(r["target"], r["features"]): r for r in json.load(open(H / "out" / "models.json"))}
P2 = {r["target"]: r for r in json.load(open(H / "out" / "pass2.json"))}
S = pd.read_csv(H / "out" / "screen.csv")
LAB = {"vol4": "Volatility, next 4 weeks", "mdd13": "Worst drawdown, next 13 weeks", "crash13": "A fall of 10%+ within 13 weeks",
       "ret4": "Return, next 4 weeks", "ret13": "Return, next 13 weeks"}

fig = plt.figure(figsize=(17.5, 10.4))
ax0 = fig.add_axes([0.02, 0.47, 0.34, 0.39]); ax0.axis("off")
axB = fig.add_axes([0.53, 0.56, 0.20, 0.29]); axC = fig.add_axes([0.83, 0.56, 0.15, 0.29]); axD = fig.add_axes([0.06, 0.09, 0.40, 0.29])
axE = fig.add_axes([0.55, 0.06, 0.43, 0.33]); axE.axis("off")
def style(ax, grid="x"):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.grid(True, axis=grid, color=GRID, lw=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)

# A: the funnel
ax0.text(0, 1.0, "A. The system, run once", fontsize=12.3, color=INK, va="top")
steps = [("226 candidate variables", "levels, changes, speeds, accelerations,\nco-movements, system measures"),
         ("1,130 variable × target pairs", "screened against 500\ntime-shifted copies of each target"),
         (f"{int(S.survivor.sum())} pass the screen", "false-discovery control + same sign\nin each decade; most = current stress"),
         ("0 beat a 3-variable\nstress model", "out of sample 2000–2019, walk-forward;\nchance from 40 shifted reruns"),
         ("Lockbox 2020–2026:\nstill sealed", "opened once, only for a candidate that survives")]
w0 = [1.0, 0.86, 0.68, 0.44, 0.44]
for i, ((h1, h2), w) in enumerate(zip(steps, w0)):
    y = 0.83 - i * 0.18
    fc = "#eef3fb" if i < 3 else ("#f4f3ef" if i == 4 else "#fdeee7")
    ax0.add_patch(FancyBboxPatch((0.25 - w / 2 * 0.48, y - 0.065), w * 0.48, 0.13, boxstyle="round,pad=0.004,rounding_size=0.015", fc=fc, ec=BASE, lw=0.9, transform=ax0.transAxes))
    ax0.text(0.25, y, h1, ha="center", va="center", fontsize=10.2, weight="bold", color=INK, transform=ax0.transAxes)
    ax0.text(0.52, y, h2, ha="left", va="center", fontsize=8.7, color=INK2, transform=ax0.transAxes, linespacing=1.25)

# B: pass 1 skill against the pre-registered benchmark
tgs = ["vol4", "mdd13", "crash13", "ret4", "ret13"]; yy = np.arange(len(tgs))[::-1]
for j, tg in enumerate(tgs):
    r = M[(tg, "CLEAN")]
    axB.barh(yy[j] + 0.18, r["skill"], height=0.32, color=ORANGE); axB.barh(yy[j] - 0.18, r["added_bench_skill_vs_prereg_bench"], height=0.32, color=BLUE)
    axB.plot([r["null_p95"]] * 2, [yy[j] + 0.02, yy[j] + 0.34], color=INK, lw=1.6)
axB.axvline(0, color=BASE, lw=1); axB.set_yticks(yy); axB.set_yticklabels([LAB[t] for t in tgs], fontsize=9.6)
axB.set_xlim(-0.75, 0.35); style(axB); axB.set_xlabel("skill against the simple benchmark (0 = no better; 1 = perfect)")
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
axB.legend(handles=[Patch(color=ORANGE, label="machine learning, 182 variables"), Patch(color=BLUE, label="3 variables: VIX + recent volatility"),
                    Line2D([0], [0], color=INK, lw=1.6, label="what chance alone reaches (95th pct)")],
           loc="upper left", bbox_to_anchor=(-0.85, -0.17), ncol=3, frameon=False, fontsize=8.8, handlelength=1.3, columnspacing=1.2)
axB.set_title("B. Out of sample, 2000–2019: nothing beats current stress", loc="left", color=INK, fontsize=12.3, pad=8)

# C: pass 2 incremental
t2 = ["vol4", "mdd13", "crash13"]; y2 = np.arange(3)[::-1]
for j, tg in enumerate(t2):
    r = P2[tg]
    for k, (m, off) in enumerate((("ridge", 0.17), ("boost", -0.17))):
        axC.barh(y2[j] + off, r[m]["skill_vs_S"], height=0.3, color=[BLUE, ORANGE][k])
        axC.plot([r[m]["null_p95"]] * 2, [y2[j] + off - 0.15, y2[j] + off + 0.15], color=INK, lw=1.6)
axC.axvline(0, color=BASE, lw=1); axC.set_yticks(y2); axC.set_yticklabels(["Volatility", "Drawdown", "10% fall"], fontsize=9.6)
style(axC); axC.set_xlabel("skill added on top of current stress")
lo = min(min(P2[t][m]["skill_vs_S"], P2[t][m]["null_p95"]) for t in t2 for m in ("ridge", "boost"))
hi = max(max(P2[t][m]["skill_vs_S"], P2[t][m]["null_p95"]) for t in t2 for m in ("ridge", "boost"))
axC.set_xlim(min(lo, -0.05) - 0.05, max(hi, 0.05) + 0.05)
axC.set_title("C. Anything on top of stress?", loc="left", color=INK, fontsize=12.3, pad=8)
axC.text(0.0, -0.17, "blue: linear   orange: small trees\nvariables chosen each year from\nthe past only", fontsize=8.6, color=INK2, transform=axC.transAxes, va="top", linespacing=1.3)

# D: what current stress predicts, in the owner's units (1990-2019)
X = pd.read_parquet(H / "data" / "features.parquet"); T = pd.read_parquet(H / "data" / "targets.parquet")
d = pd.concat([X["VIX|level"], T[["crash13", "vol4", "end13"]]], axis=1).loc["1990":"2019"].dropna()
d = d[pd.to_datetime(d.end13) < pd.Timestamp("2020-01-01")]
bins = [0, 13, 16, 20, 25, 30, 100]; lab = ["<13", "13-16", "16-20", "20-25", "25-30", "30+"]
d["b"] = pd.cut(d["VIX|level"], bins, labels=lab)
g = d.groupby("b", observed=True).agg(p=("crash13", "mean"), n=("crash13", "size"), vol=("vol4", lambda s: np.exp(s).median() * 100))
xs = np.arange(len(g))
axD.bar(xs, 100 * g.p, width=0.62, color=BLUE)
for i, (p, n, v) in enumerate(zip(g.p, g.n, g.vol)):
    axD.text(i, 100 * p + 1.2, f"{100 * p:.0f}%", ha="center", fontsize=9.6, color=INK)
    axD.text(i, -6.5, f"n={n}\nvol {v:.0f}", ha="center", fontsize=8.4, color=INK2, va="top", linespacing=1.2)
axD.axhline(100 * d.crash13.mean(), color=INK2, lw=1.2, ls=(0, (4, 3)))
axD.text(-0.45, 100 * d.crash13.mean() + 1.0, f"all weeks {100 * d.crash13.mean():.0f}%", fontsize=9, color=INK2, ha="left")
axD.set_xticks(xs); axD.set_xticklabels([f"VIX {l}" for l in lab]); axD.tick_params(axis="x", pad=26)
axD.set_ylim(0, max(100 * g.p) + 10); style(axD, "y"); axD.set_ylabel("weeks followed by a 10%+ fall within 13 weeks (%)")
axD.set_title("D. The one real predictor, in your units (1990–2019, weekly)", loc="left", color=INK, fontsize=12.3, pad=8)
axD.text(0, -0.36, "vol = median realized volatility over the next 4 weeks, in %. Weeks overlap, so the effective sample is smaller than n.",
         fontsize=8.6, color=MUTED, transform=axD.transAxes)

# E: what this means
axE.text(0, 1.0, "E. What it means", fontsize=12.3, color=INK, va="top")
lines = ["How big and how dangerous the next weeks are: predictable, and almost entirely from how stressed the market is now.",
         "Which way it goes: not predictable from any of the 182 variables, at 4 or 13 weeks.",
         "Speeds, accelerations, correlations and macro levels add nothing that survives once current stress is known.",
         "Lead and lag between assets week to week: no link repeats in both halves of 1990–2019.",
         "One input failed the audit: a financial-conditions index (NFCI) whose history is rewritten every week.",
         "Next: search where the edge may actually live: faster data (intraday), positioning, and single stocks like TSLA."]
for i, s in enumerate(lines):
    axE.text(0.0, 0.85 - i * 0.145, "•", fontsize=11, color=INK, va="top", transform=axE.transAxes)
    axE.text(0.025, 0.85 - i * 0.145, s, fontsize=10.2, color=INK, va="top", transform=axE.transAxes, wrap=True)

fig.text(0.02, 0.962, "A rigorous search of 226 variables found one dependable predictor: how stressed the market is right now",
         fontsize=16.2, weight="bold", color=INK)
fig.text(0.02, 0.925, "Point-in-time weekly data 1990–2019, walk-forward out of sample, chance measured by time-shifted reruns, false-discovery control, "
         "decade stability. 2020–2026 is sealed for confirmation.", fontsize=10.6, color=INK2, va="top")
out = H / "out" / "discovery.png"; fig.savefig(out, dpi=200); print(out)
