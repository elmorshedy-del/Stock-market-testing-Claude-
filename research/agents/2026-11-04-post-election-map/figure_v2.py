"""v2 figure: what changed overnight. (a) ES-implied SPY path over the gamma pocket (Tue positions); (b) TSLA vs its flip;
(c) AI names fading in the last premarket hour. Prices: Yahoo chart API 5-min (ES=F for the overnight). -> out/what_changed.png
Usage: python figure_v2.py"""
import datetime as dt
import json
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = Path(__file__).resolve().parent; O = HERE / "out"; M = json.load(open(O / "map_v2.json"))
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE, RED, GREEN = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834", "#c8372d", "#2f8f5b"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRAY, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.titleweight": "bold", "axes.titlesize": 11})
T0 = dt.datetime(2026, 11, 3, 16, 0)


def bars(sym, rng="2d"):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym.replace('^', '%5E')}?range={rng}&interval=5m&includePrePost=true"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    return [(dt.datetime.utcfromtimestamp(t) - dt.timedelta(hours=5), c) for t, c in zip(r["timestamp"], q["close"]) if c and dt.datetime.utcfromtimestamp(t) - dt.timedelta(hours=5) >= T0]


es = bars("ES=F"); ES16 = 7597.0; SPY16 = 754.35
spy_imp = [(t, SPY16 * c / ES16) for t, c in es]
tsla = bars("TSLA"); amd, nvda, smh = bars("AMD"), bars("NVDA"), bars("SMH")
fig, ax = plt.subplots(1, 3, figsize=(16, 5.6), facecolor=BG, gridspec_kw={"width_ratios": [1.25, 1.1, 0.95]})
for a in ax: a.set_facecolor(BG); a.grid(True, color=GRID, lw=0.8); a.spines[["top", "right"]].set_visible(False); a.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

a = ax[0]; s = M["SPY"]
a.axhspan(723, 745, color=RED, alpha=0.08); a.text(T0, 744.2, "  core pocket 723-745 (trough 735)", color=RED, fontsize=8.5, va="top")
for y, lab, col in [(s["flip incl. Wed 0DTE"], f"flip {s['flip incl. Wed 0DTE']:.1f}: above = calm (long gamma)", GREEN), (750, "750: biggest short-gamma strike", ORANGE), (740, "740 put wall", RED)]:
    a.axhline(y, color=col, lw=1.2, ls="--"); a.text(T0 if y > 760 else spy_imp[-1][0], y + 0.4, ("" if y > 760 else "") + lab + ("" if y > 760 else "  "), color=col, fontsize=8.5, ha="left" if y > 760 else "right")
a.plot([t for t, _ in spy_imp], [v for _, v in spy_imp], color=INK, lw=1.8)
lo = min(spy_imp, key=lambda x: x[1]); hi = max(spy_imp, key=lambda x: x[1])
a.annotate(f"scare low ≈ {lo[1]:.1f}\n(touched the pocket top)", lo, xytext=(lo[0] - dt.timedelta(hours=3.5), 737), fontsize=8.5, color=RED, arrowprops=dict(arrowstyle="->", color=RED))
a.annotate(f"snap-back high ≈ {hi[1]:.1f}", hi, xytext=(hi[0] - dt.timedelta(hours=4.5), 768.3), fontsize=8.5, color=GREEN, arrowprops=dict(arrowstyle="->", color=GREEN))
a.set_ylim(730, 770); a.set_ylabel("SPY (ES-implied overnight)")
a.set_title("(a) SPY: the scare happened overnight and failed.\nIt touched the pocket top, then snapped back +2.6%", loc="left")

a = ax[1]
tf = 377.5
a.axhline(tf, color=ORANGE, lw=1.6, ls="--"); a.text(dt.datetime(2026, 11, 3, 20, 15), tf + 0.6, "flip 377.5: close below = FULL SETUP", color=ORANGE, fontsize=8.5, fontweight="bold")
for y, lab, col in [(398.5, "Tue close 398.5", GRAY), (380, "380: biggest short-gamma strike", INK2), (372.2, "372.2: fills the late-Oct gap", BLUE), (365, "365: break level", RED)]:
    a.axhline(y, color=col, lw=1, ls=":"); a.text(tsla[-1][0] if y > 390 else dt.datetime(2026, 11, 3, 20, 15), y + 0.6, lab + ("  " if y > 390 else ""), color=col, fontsize=8.5, ha="right" if y > 390 else "left")
gap = [i for i in range(1, len(tsla)) if (tsla[i][0] - tsla[i - 1][0]).seconds > 3600]
segs = [tsla[:gap[0]], tsla[gap[0]:]] if gap else [tsla]
for sg in segs: a.plot([t for t, _ in sg], [v for _, v in sg], color=INK, lw=1.8)
a.set_ylim(360, 402); a.set_ylabel("TSLA (post-market and pre-market; no overnight prints)")
a.set_title(f"(b) TSLA did NOT bounce: SPY +{(spy_imp[-1][1] / SPY16 - 1) * 100:.1f}%, TSLA {(tsla[-1][1] / 398.5 - 1) * 100:.1f}%.\nIts own story now, sitting on its flip", loc="left")

a = ax[2]; ref = {"AMD": 483.90, "NVDA": 206.69}
for nm, b, col in [("AMD (beat Tue night)", amd, RED), ("NVDA", nvda, BLUE)]:
    k = nm.split()[0]; pts = [(t, (v / ref[k] - 1) * 100) for t, v in b if t >= dt.datetime(2026, 11, 4, 4, 0)]
    a.plot([t for t, _ in pts], [v for _, v in pts], color=col, lw=1.8, label=f"{nm}: now {pts[-1][1]:+.1f}%")
a.axhline(0, color=GRAY, lw=1); a.axvline(dt.datetime(2026, 11, 4, 7, 0), color=INK2, lw=1, ls=":"); a.text(dt.datetime(2026, 11, 4, 7, 2), a.get_ylim()[1] * 0.92, "07:00 fade starts", fontsize=8.5, color=INK2)
a.legend(frameon=False, fontsize=8.5, loc="lower left"); a.set_ylabel("% vs Tue 16:00 close")
a.set_title("(c) The new risk: AI is selling good news.\nAMD gave back its whole earnings pop", loc="left")
fig.suptitle(f"What changed overnight (Wed Nov 4, {tsla[-1][0]:%H:%M} ET): SPY's floor held; TSLA broke from SPY onto its own flip; AI fading into the open",
             x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK)
fig.text(0.01, 0.01, "Gamma map: Tuesday's closing positions (OI dated Nov 4) and Tuesday's closing IVs, classic dealer convention. Prices: Yahoo 5-min; ES=F scaled to SPY at the 16:00 close (754.35 / 7,597).",
         fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.03, 1, 0.92)); plt.savefig(O / "what_changed.png", dpi=150, facecolor=BG); print("ok", tsla[-1], spy_imp[-1], lo, hi)
