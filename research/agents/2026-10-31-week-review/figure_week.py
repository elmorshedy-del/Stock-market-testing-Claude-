"""out/week_review_1031.png: Friday Oct 30 scorecard (SPY and TSLA paths vs pre-stated levels), the ladder, October's
AI-vs-rest split, D2, Monday's SPY gamma map, and the election VIX run-up. Usage: python figure_week.py <live31 dir>"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"; D = Path(sys.argv[1])
MICRO = HERE.parents[1] / "microstructure"; LR = HERE.parent / "2026-10-30-live-read" / "out"
GREEN, RED, INK, MUTED, SURF, BLUE, AMBER, GREY = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#e8a33d", "#c9c8c3"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.parse_math": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})


def bars(s):
    r = json.load(open(D / "y" / f"{s}_1m.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    b = pd.DataFrame({k: q[k] for k in ("high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna()
    b = b[b.index.date == pd.Timestamp("2026-10-30").date()]; return b.between_time("09:30", "15:59")


fig = plt.figure(figsize=(20, 17)); gs = fig.add_gridspec(3, 3, hspace=0.48, wspace=0.24)
# A: SPY Friday vs pre-stated levels
a = fig.add_subplot(gs[0, 0]); b = bars("SPY"); x = (b.index.hour - 9.5) + b.index.minute / 60
a.fill_between(x, b.low, b.high, color=GREY, lw=0); a.plot(x, b.close, color=INK, lw=1)
a.axhspan(750, 754, color=RED, alpha=0.10); a.text(0.05, 752, "called: realistic flush low 750–754", fontsize=8.5, color=RED, va="center")
for y, lab, col in ((750, "750 put wall", RED), (760, "760 accelerant", RED), (762, "~762 ES-implied open (called)", MUTED), (757.8, "757.8: close here or lower makes the GEX half of R2 likely", BLUE)):
    a.axhline(y, color=col, lw=1, ls="--"); a.text(6.45, y + 0.15, lab, fontsize=8, color=col, ha="right", va="bottom")
a.scatter([x[b.low.argmin()]], [b.low.min()], color=RED, zorder=5); a.annotate(f"low {b.low.min():.2f} at 14:52", (x[b.low.argmin()], b.low.min()), xytext=(-110, -14), textcoords="offset points", fontsize=8.5, color=RED)
a.set_xticks([0, 1, 2, 3, 4, 5, 6.5]); a.set_xticklabels(["9:30", "10:30", "11:30", "12:30", "13:30", "14:30", "16:00"]); a.set_ylim(748.5, 763)
a.set_title(f"A. SPY Fri: flush to the put wall, rebound, close {b.close.iloc[-1]:.2f}", loc="left", fontsize=11, weight="bold", color=INK)
# B: TSLA Friday
a = fig.add_subplot(gs[0, 1]); b = bars("TSLA"); x = (b.index.hour - 9.5) + b.index.minute / 60
ev = pd.read_csv(LR / "d1_events.csv", index_col=0); sd = ev.ex.std()
pred = 403.30 * (1 + 2.0 * (-0.0182)); lo, hi = 403.30 * (1 + 2.65 * (-0.0182)), pred
a.fill_between(x, b.low, b.high, color=GREY, lw=0); a.plot(x, b.close, color=INK, lw=1)
a.axhspan(lo, hi, color=RED, alpha=0.10); a.text(0.05, (lo + hi) / 2, f"our beta translator: {lo:.0f}–{hi:.0f} (wrong)", fontsize=8.5, color=RED, va="center")
a.axhspan(pred - sd * 403.3, pred + sd * 403.3, color=RED, alpha=0.04)
for y, lab, col in ((400, "400: your call, and the biggest + strike (right)", GREEN), (388.7, "389 old triple top", MUTED)):
    a.axhline(y, color=col, lw=1.2, ls="-" if y == 400 else "--"); a.text(6.45, y + 0.3, lab, fontsize=8, color=col, ha="right", va="bottom")
a.set_xticks([0, 1, 2, 3, 4, 5, 6.5]); a.set_xticklabels(["9:30", "10:30", "11:30", "12:30", "13:30", "14:30", "16:00"])
a.set_title(f"B. TSLA Fri: −0.9% on an S&P −1.8% day, close {b.close.iloc[-1]:.2f}", loc="left", fontsize=11, weight="bold", color=INK)
# C: ladder
a = fig.add_subplot(gs[0, 2]); a.axis("off")
rungs = [("R0", "mid GEX + DIX > 80th", False), ("R1", "GEX ≤ 30th", True), ("R2", "R1 + DIX > 50th", False), ("R3", "GEX ≤ 20th", True),
         ("R4", "R3 + S&P ≥ 2% off 10d high", True), ("R5", "R4 + DIX > 50th", False), ("R6", "VIX ≤ 16.53", False), ("R7", "VIX ≤ 14.59", False)]
for i, (k, lab, on) in enumerate(rungs):
    yy = 0.95 - i * 0.095; a.add_patch(plt.Rectangle((0.02, yy - 0.04), 0.13, 0.08, color=GREEN if on else GREY, transform=a.transAxes))
    a.text(0.085, yy, k, transform=a.transAxes, ha="center", va="center", fontsize=11, weight="bold", color="white" if on else INK)
    a.text(0.18, yy, lab + ("   ON" if on else ""), transform=a.transAxes, va="center", fontsize=10, color=GREEN if on else MUTED, weight="bold" if on else "normal")
a.text(0.02, -0.06, "GEX $1.06bn (6th pct, from $5.62bn); DIX 43.8% (22nd pct)\nR4: up-leg within 20 sessions 70% / 74% vs 50% / 58% any day.\nThe DIX half of R2/R5 came up tails.", transform=a.transAxes, fontsize=9, color=INK, va="bottom")
a.set_title("C. S&P ladder at Friday's close: R1, R3, R4 on", loc="left", fontsize=11, weight="bold", color=INK)
# D: October AI vs rest
a = fig.add_subplot(gs[1, 0])
sect = [("SMH", -14.21), ("XLC", -9.98), ("XLK", -8.30), ("NDX", -6.65), ("S&P", -0.93), ("IWM", 0.52), ("RSP", 4.95), ("XLF", 5.82), ("XLY", 6.01), ("XLB", 8.30), ("XLV", 9.77), ("XLU", 10.12), ("XLP", 10.94), ("XLE", 13.85)]
a.barh([s for s, _ in sect], [v for _, v in sect], color=[RED if v < 0 else GREEN for _, v in sect])
for i, (s, v) in enumerate(sect): a.text(v + (0.3 if v >= 0 else -0.3), i, f"{v:+.1f}%", va="center", ha="left" if v >= 0 else "right", fontsize=8.5)
a.axvline(0, color=MUTED, lw=0.6); a.set_xlim(-19, 18); a.set_xlabel("October return, %")
a.set_title("D. October: AI −12.6% vs the rest +7.3% (our 81 large caps)", loc="left", fontsize=11, weight="bold", color=INK)
# E: D2
a = fig.add_subplot(gs[1, 1]); d2 = json.loads((OUT / "d2.json").read_text())
L = pd.DataFrame({"rsp": None}, index=[])
r = json.load(open(D / "long" / "RSP.json"))["chart"]["result"][0]; q = json.load(open(D / "long" / "QQQ.json"))["chart"]["result"][0]
def ser(rr):
    c = rr["indicators"].get("adjclose", [{}])[0].get("adjclose", rr["indicators"]["quote"][0]["close"])
    s = pd.Series(c, index=pd.to_datetime(rr["timestamp"], unit="s").normalize()).dropna(); return s[~s.index.duplicated(keep="last")]
sp = (ser(r).pct_change(20) - ser(q).pct_change(20)).dropna().loc[:"2026-10-30"] * 100
a.plot(sp.index, sp, color=MUTED, lw=0.6); a.axhline(sp.iloc[-1], color=RED, lw=1, ls="--")
a.scatter([sp.index[-1]], [sp.iloc[-1]], color=RED, zorder=5); a.text(sp.index[-1], sp.iloc[-1] + 0.6, f"now {sp.iloc[-1]:.1f} pts: the record", color=RED, fontsize=9, ha="right")
for dte in d2["per event"]: a.axvline(pd.Timestamp(dte), color=BLUE, lw=0.5, alpha=0.6)
a.set_ylabel("equal-weight S&P minus Nasdaq-100, 20-session return, pts")
dd = d2["all days"]
a.text(0.02, 0.04, f"D2 (pre-registered): after the 15 past record divergences (blue)\nS&P 20 sessions later {dd['spx20']['events']*100:+.1f}% vs {dd['spx20']['base']*100:+.1f}% any day (p {dd['spx20']['p (events > base)']:.2f});\nup-leg {dd['leg']['events']:.0%} vs {dd['leg']['base']:.0%}.  No edge either way.", transform=a.transAxes, fontsize=8.8, color=INK)
a.set_title("E. Record divergence; past records predicted nothing", loc="left", fontsize=11, weight="bold", color=INK)
# F: Monday SPY gamma map
a = fig.add_subplot(gs[1, 2]); cv = json.loads((OUT / "curves_mon.json").read_text())["SPY"]; mm = json.loads((OUT / "maps_mon.json").read_text())["SPY"]
a.plot(cv["total gamma $bn"], cv["price"], color=INK, lw=2); a.axvline(0, color=MUTED, lw=0.6)
a.fill_betweenx(cv["price"], cv["total gamma $bn"], 0, where=np.array(cv["total gamma $bn"]) < 0, color=RED, alpha=0.10)
for y, lab, col, ls in ((mm["flip"], f"{mm['flip']:.1f} flip (reclaim = damping)", GREEN, "-"), (755.72, "755.72 Fri close", INK, ":"), (750, "750 put wall (held Fri)", RED, "--"),
                        (740.6, f"~740: deepest pocket ({mm['most negative total-gamma price']:.0f}) = channel kill line (SPX 7,428)", BLUE, "--")):
    a.axhline(y, color=col, lw=1.1, ls=ls); a.text(min(cv["total gamma $bn"]) * 0.98, y + 0.4, lab, fontsize=8.3, color=col, va="bottom")
a.set_xlabel("dealer gamma, $bn per 1% (Oct 29 positions, Fri IVs)"); a.set_ylabel("SPY")
a.set_title("F. Monday's SPY map: deep short gamma below 774", loc="left", fontsize=11, weight="bold", color=INK)
# G: election VIX
a = fig.add_subplot(gs[2, 0]); e = pd.read_csv(MICRO / "out" / "elections.csv")
for kind, col in (("presidential", MUTED), ("midterm", BLUE)):
    z = e[e.kind == kind]; a.scatter(z.vix_runup_10d_pts, z.vix_5d_pts, color=col, s=30, label=kind)
    for _, rr in z.iterrows(): a.text(rr.vix_runup_10d_pts + 0.15, rr.vix_5d_pts, rr.date[:4], fontsize=7, color=col)
bb = np.polyfit(e.vix_runup_10d_pts, e.vix_5d_pts, 1); xx = np.linspace(-6, 7, 10); a.plot(xx, np.polyval(bb, xx), color=INK, lw=0.8, ls="--")
a.axvline(2.11, color=RED, lw=1.2); a.text(2.3, 13.5, "2026 so far: +2.1\n(largest midterm run-up;\nfits a VIX drop of ~3.8\nin the 5 days after)", color=RED, fontsize=8.5, va="top")
a.set_xlabel("VIX change over the 10 sessions into the vote"); a.set_ylabel("VIX change, 5 sessions after"); a.legend(frameon=False, fontsize=8.5, loc="lower left")
a.set_title("G. Election: hedges have now built (ρ −0.77 build vs release)", loc="left", fontsize=11, weight="bold", color=INK)
# H: scorecard text
a = fig.add_subplot(gs[2, 1:]); a.axis("off")
lines = [("✓", "SPY open ~762 (ES-implied); actual 761.40", GREEN), ("✓", "Flush low in 750–754 at the 750 put wall; actual 750.36, then a +5 rebound into the month-end close", GREEN),
         ("✓", "GEX half of R2 likely at a close ≤ 757.8; GEX fell to the 6th pct (bigger than the model said)", GREEN),
         ("✗", "R2 / R5: the DIX half (~60%) failed, DIX 22nd pct.  R4 fired instead (green light C)", RED),
         ("✗", "Owner's close 760 ± 2: actual 755.72", RED),
         ("✓", "Owner: TSLA back to 400. TSLA low 387.52 (just under 389) at 9:36, high 404.20, close 399.81", GREEN),
         ("✗", "Our TSLA translator (384–389): the beta point estimate ignored TSLA's own spread; Friday's +2.8 pt excess is only the 80th pct of past days", RED),
         ("·", "AAPL earnings gap-up vanished before the open (no fade test); AMZN −7% gap-down closed −1.4% (gap-downs untested)", MUTED),
         ("✓", "Read 'selling is megacap-specific': confirmed (AI basket −12.6% vs rest +7.3% in October; defensives up Friday)", GREEN)]
for i, (m, t, c) in enumerate(lines):
    a.text(0.0, 0.95 - i * 0.105, m, fontsize=14, color=c, weight="bold", transform=a.transAxes, va="top"); a.text(0.035, 0.95 - i * 0.105, t, fontsize=10.5, color=INK, transform=a.transAxes, va="top")
a.set_title("H. Scorecard of Thursday night's calls", loc="left", fontsize=11, weight="bold", color=INK)
fig.suptitle("Week review, Oct 26–30: AI selloff inside a broad market; R4 fired; election hedges built", x=0.01, ha="left", fontsize=15, weight="bold", color=INK)
fig.savefig(OUT / "week_review_1031.png", dpi=115, bbox_inches="tight"); print("ok", round(sd, 4))
