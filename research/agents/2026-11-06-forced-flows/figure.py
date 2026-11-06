"""Combined figure for 2026-11-06 aftershocks + forced-flows. Usage: python figure.py -> out/physics_next.png"""
import json, importlib.util, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"; AS = H.parent / "2026-11-06-aftershocks" / "out" / "hawkes.json"
INK, INK2, MUTED, GRID, SURF, BLUE, ORANGE = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#fcfcfb", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})
A, F = json.load(open(AS)), json.load(open(O / "ff.json"))
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
fig, axs = plt.subplots(2, 2, figsize=(14.5, 11.5), gridspec_kw={"hspace": 0.55, "wspace": 0.28})
def head(ax, t, s): ax.set_title(t, loc="left", fontsize=11.5, fontweight="bold", color=INK, pad=12 + 14 * (s.count("\n") + 1)); ax.text(0, 1.02, s, transform=ax.transAxes, fontsize=9, color=INK2, va="bottom", linespacing=1.35)
# 1 branching ratios
ax = axs[0, 0]; nm = ["S&P 500", "Nasdaq-100", "SOX"]; n = [A[k]["fits (in-sample <2008)"]["pow"]["n (branching ratio)"] for k in nm]; sh = [A[k]["share of oos event days attributed to triggering (pow)"] for k in nm]
ax.barh(nm[::-1], n[::-1], color=BLUE, height=0.5); ax.axvline(1, color=ORANGE, lw=1.5, ls=(0, (4, 3))); ax.text(1.0, 2.45, " critical (n = 1):\n cascades never stop", color=ORANGE, fontsize=8.6, va="top")
for i, (a, b) in enumerate(zip(n[::-1], sh[::-1])): ax.text(a - 0.02, i, f"n = {a:.2f}   ·   {100*b:.0f}% of big days are aftershocks", ha="right", va="center", color="white", fontsize=9, fontweight="bold")
ax.set_xlim(0, 1.25); ax.set_xlabel("branching ratio: big days triggered by each big day"); ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
head(ax, "1 · Fear feeds on itself (aftershocks study)", "Fitted on data before 2008; beats a constant rate by a wide margin out of sample, 2008-2026.\nBig day = move of at least 3x the 5-year median (about 1.7% for the S&P today).")
# 2 aftershock decay after S&P mainshocks
ax = axs[0, 1]; s = lc.yahoo("^GSPC", "1950-01-01").close; r = np.diff(np.log(s.values)); sc = pd.Series(np.abs(r)).rolling(1260, min_periods=1260).median().shift(1).values; ok = ~np.isnan(sc)
r, sc = r[ok], sc[ok]; x = (np.abs(r) >= 3 * sc).astype(float); big = np.abs(r) >= 8 * sc; main = [i for i in np.where(big)[0] if not big[max(0, i - 63):i].any()]
bins = [(1, 1), (2, 3), (4, 7), (8, 15), (16, 31), (32, 63), (64, 120)]; idx = s.index[1:][ok]; base = x.mean()
for lab, sel, col in (("before 2008", [i for i in main if idx[i] < pd.Timestamp("2008-01-01")], MUTED), ("2008 on", [i for i in main if idx[i] >= pd.Timestamp("2008-01-01")], INK)):
    mid, rate = [], []
    for a0, b0 in bins:
        v = [x[i + t] for i in sel for t in range(a0, b0 + 1) if i + t < len(x)]; mid.append(np.sqrt(a0 * b0)); rate.append(np.mean(v))
    ax.plot(mid, 100 * np.array(rate), marker="o", ms=7, color=col, lw=2, label=f"after {len(sel)} S&P mainshocks, {lab}")
t = np.arange(1, 121); ef = A["S&P 500"]["Omori mainshocks"]["in-sample exp fit"]; ax.plot(t, 100 * (ef["b"] + ef["K"] * np.exp(-t / ef["tau"])), color=BLUE, lw=1.8, label=f"fit on pre-2008 shocks (time constant {ef['tau']:.0f} sessions)")
ax.axhline(100 * base, color=MUTED, lw=1, ls=(0, (3, 2))); ax.text(1.05, 100 * base + 0.8, f"normal rate {100*base:.0f}%", fontsize=8.6, color=INK2)
ax.set_xscale("log"); ax.set_xlim(0.9, 130); ax.set_xlabel("sessions after the shock"); ax.set_ylabel("chance of a big day (%)"); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True); ax.legend(loc="upper right", fontsize=8.4, frameon=False)
ax.set_ylim(0, 75); head(ax, "2 · How long fear lingers", "After a big shock, big days run 2-6x normal for weeks and fade over about 4 months, more strongly\nsince 2008. The fit and the cascade math (16 / (1 - 0.82) = 89 sessions) give the timescale, not the early peak.")
# 3 forced flow on Nov 5
ax = axs[1, 0]; dec = sorted(F["Nov 5 decomposition"], key=lambda d: d["as % of daily $ volume"]); lab = {"SEMIS": "Semis", "NDX": "Nasdaq-100", "SPX": "S&P 500"}
ax.barh([lab.get(d["u"], d["u"]) for d in dec], [d["as % of daily $ volume"] for d in dec], color=ORANGE, height=0.6)
for i, d in enumerate(dec): ax.text(d["as % of daily $ volume"] + 0.3, i, f"${-d['forced close rebalancing $bn']:.1f}bn", va="center", fontsize=8.6, color=INK2)
ax.set_xlabel("leveraged-ETF selling forced at the Nov 5 close, % of a normal day's $ volume"); ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True); ax.set_xlim(0, 27)
head(ax, "3 · The forced selling is real and large (forced-flows study)", "Leveraged ETFs must trade L(L-1) x assets x the day's move at the close. Semis: roughly $21-28bn\n(the range depends on when Yahoo's asset figure was taken), about a fifth of a normal day's volume.")
# 4 predicted vs actual last 30 min on big days
ax = axs[1, 1]; exec(open(H / "ff_test.py").read().split("def tests(df):")[0]); df = build(); bd = df[df.R.abs() >= 0.025]
nov = bd.date == pd.Timestamp("2026-11-05"); ax.scatter(100 * bd.x[~nov], 100 * bd.r[~nov], s=22, color=MUTED, alpha=0.6, label="other big days (Aug 13 - Nov 4)")
ax.scatter(100 * bd.x[nov], 100 * bd.r[nov], s=46, color=ORANGE, edgecolor=SURF, linewidth=1, zorder=3, label="Nov 5")
lim = 3.3; ax.plot([-lim, lim], [-lim, lim], color=INK2, lw=1, ls=(0, (3, 2))); ax.axhline(0, color=MUTED, lw=0.8); ax.axvline(0, color=MUTED, lw=0.8)
ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_xlabel("textbook impact of the forced flow (%)"); ax.set_ylabel("actual move, 15:30 to close (%)"); ax.legend(loc="upper left", fontsize=8.4, frameon=False)
ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True); c = np.corrcoef(bd.x, bd.r)[0, 1]
head(ax, "4 · ...but the last 30 minutes don't follow it", f"{len(bd)} big-move days across 11 names: correlation {c:.2f}, same sign {100*(np.sign(bd.x) == np.sign(bd.r)).mean():.0f}%. Nov 5 fit (orange),\nOct 30 went the other way. Pre-registered tests H-FF1-3 all fail: the flow is predictable, so it's priced early.")
fig.text(0.125, 0.015, "Studies 2026-11-06-aftershocks (pre-registered @ 0273b35) and 2026-11-06-forced-flows (same commit). Yahoo daily and 5-minute data, Yahoo leveraged-ETF net assets.", fontsize=8, color=MUTED)
fig.savefig(O / "physics_next.png", dpi=150, bbox_inches="tight"); print("ok")
