"""out/equations.png: the three derived layers (book identity, hedging, feedback) and Friday 14:00-15:30 showing the
vol divergence at the retest. Usage: python equations_fig.py <db dir> <Yahoo 1m dir> <flow_path.csv>"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"; DB, Y, FP = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]); ET = "America/New_York"
GREEN, RED, INK, MUTED, SURF, BLUE, AMBER = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#e8a33d"
plt.rcParams.update({"font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(19, 10.5)); gs = fig.add_gridspec(3, 2, width_ratios=[1.05, 1], hspace=0.25, wspace=0.12)
L = fig.add_subplot(gs[:, 0]); L.axis("off"); L.set_xlim(0, 10); L.set_ylim(0, 10)
cards = [(8.0, BLUE, "1. The book identity  (Cont, Kukanov & Stoikov 2014)",
          r"$\Delta p \;\approx\; \dfrac{\mathrm{OFI}}{D}$",
          "OFI = (bids added − bids cancelled − market SELLS) − (asks added − asks cancelled − market BUYS)\nD = depth.  Market orders are only one term: pulled bids and lower offers push price down too.\nThin bids (small D) make each sell hit harder. Friday: sell minutes −2.00 pts vs buy minutes +0.54."),
         (4.9, AMBER, "2. Forced hedging  (Black–Scholes delta hedge)",
          r"$H \;=\; -\,\Gamma\,\Delta S \;-\; \mathrm{Vanna}\,\Delta\sigma \;-\; \mathrm{Charm}\,\Delta t$",
          "Dealers short puts must SELL when price falls (Γ term) and when implied vol rises (Vanna term);\ntime passing lets them buy back a little (Charm). When vol FALLS, the Vanna term turns into BUYING\neven if price is flat."),
         (1.8, RED, "3. Feedback  (Kyle 1985 impact + the hedge above)",
          r"$\Delta p \;=\; \dfrac{\lambda\,u}{1-\lambda\,|\Gamma|}\;+\;\dfrac{\lambda\,\mathrm{Vanna}\,(-\Delta\sigma)}{1-\lambda\,|\Gamma|}$",
          "u = outside flow (news, real sellers), λ = price impact per $. Short gamma multiplies every push by 1/(1−λ|Γ|).\nThe loop stops only when (i) u fades, (ii) σ starts FALLING, or (iii) liquidity returns (λ down).\nThe equations give the CONDITIONS for a turn, never the exact minute.")]
for y, col, title, eq, txt in cards:
    L.add_patch(FancyBboxPatch((0.1, y - 1.25), 9.8, 2.75, boxstyle="round,pad=0.08", fc=col + "14", ec=col, lw=1.8))
    L.text(0.35, y + 1.2, title, fontsize=12.5, weight="bold", color=col, va="top")
    L.text(5.0, y + 0.25, eq, fontsize=19, color=INK, ha="center", va="center")
    L.text(0.35, y - 0.55, txt, fontsize=9.6, color=INK, va="center")
# right: Friday 14:00-15:30
spy = pd.read_parquet(DB / "SPY_1m_2026-10-30.parquet"); spy.index = spy.index.tz_convert(ET); spy = spy.between_time("14:00", "15:30")
r = json.load(open(Y / "VIX_1m.json"))["chart"]["result"][0]
vix = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert(ET)).dropna()
vix = vix[vix.index.date == pd.Timestamp("2026-10-30").date()].between_time("14:00", "15:30")
fp = pd.read_csv(FP); fp = fp[(fp.time >= "14:00") & (fp.time <= "15:30")]
tx = lambda idx: idx.hour + idx.minute / 60
a = fig.add_subplot(gs[0, 1]); a.plot(tx(spy.index), spy.low, color=INK, lw=1.3); a.set_ylabel("SPY (1-min low)")
l1 = spy.loc[:"2026-10-30 14:40"].low; l2 = spy.loc["2026-10-30 14:45":"2026-10-30 15:00"].low
for s_, col in ((l1, MUTED), (l2, RED)):
    t0 = s_.idxmin(); a.scatter([tx(pd.DatetimeIndex([t0]))[0]], [s_.min()], color=col, zorder=5); a.text(tx(pd.DatetimeIndex([t0]))[0] + 0.01, s_.min() - 0.35, f"{s_.min():.2f} @ {t0.strftime('%H:%M')}", fontsize=9.5, color=col)
a.set_title("Friday 14:00-15:30: price made a slightly LOWER low at 14:52 ...", loc="left", fontsize=12, weight="bold", color=INK)
b = fig.add_subplot(gs[1, 1], sharex=a); b.plot(tx(vix.index), vix, color=BLUE, lw=1.4); b.set_ylabel("VIX")
v1 = vix.loc[:"2026-10-30 14:40"]; v2 = vix.loc["2026-10-30 14:45":"2026-10-30 15:00"]
b.scatter([tx(pd.DatetimeIndex([v1.idxmax()]))[0]], [v1.max()], color=MUTED, zorder=5); b.text(tx(pd.DatetimeIndex([v1.idxmax()]))[0] + 0.01, v1.max() + 0.1, f"{v1.max():.1f} @ {v1.idxmax().strftime('%H:%M')}", fontsize=9.5, color=MUTED)
b.scatter([tx(pd.DatetimeIndex([v2.idxmax()]))[0]], [v2.max()], color=BLUE, zorder=5); b.text(tx(pd.DatetimeIndex([v2.idxmax()]))[0] + 0.01, v2.max() + 0.15, f"{v2.max():.1f}: a LOWER high", fontsize=9.5, color=BLUE)
b.set_title("... but implied vol did NOT make a new high (vol divergence)", loc="left", fontsize=12, weight="bold", color=INK)
c = fig.add_subplot(gs[2, 1], sharex=a); h = fp.time.str[:2].astype(int) + fp.time.str[3:].astype(int) / 60
c.bar(h - 2.5 / 60, fp["all vanna"] / 1e9, width=4 / 60, color=[GREEN if v > 0 else RED for v in fp["all vanna"]])
c.axhline(0, color=MUTED, lw=0.6); c.set_ylabel("Vanna-term hedge flow\n$bn per 5 min (model)")
c.set_title("Layer 2's vol term flipped to dealer BUYING at 14:40, 12 minutes before the final low", loc="left", fontsize=12, weight="bold", color=INK)
c.set_xticks([14, 14.25, 14.5, 14.75, 15, 15.25, 15.5]); c.set_xticklabels(["14:00", "14:15", "14:30", "14:45", "15:00", "15:15", "15:30"])
fig.suptitle("The mechanics as equations, and what they could (and could not) say at 14:52", x=0.01, ha="left", fontsize=16, weight="bold", color=INK)
fig.savefig(OUT / "equations.png", dpi=115, bbox_inches="tight"); print("ok")
