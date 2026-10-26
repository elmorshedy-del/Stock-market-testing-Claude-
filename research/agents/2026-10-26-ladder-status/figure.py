"""Ladder status figure: out/ladder_status.png. Rung odds from ladder.py rerun on fresh data (Oct 26);
TSLA state odds from REPORT 4w (all days 2021-2026, bursts = +-5% in a day or +-9% in two)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "out"
st = json.loads((OUT / "status.json").read_text())
L, T = st["S&P ladder"], st["TSLA"]
GREEN, GREY, INK, MUTED, SURF, RED, BLUE = "#1baf7a", "#c9c8c3", "#0b0b0b", "#52514e", "#fcfcfb", "#d64545", "#2a78d6"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
# (label, P(leg) 2012-26, P(leg) 2019Q4-26, condition still needed)
rungs = [("R0 mid GEX + DIX>80th", .569, .657, "off: GEX is low, not mid"),
         ("R1 GEX <= 30th", .602, .710, ""),
         ("R2 GEX <= 30th + DIX > 50th", .642, .776, "ON since Oct 20 (Fri: GEX 23rd, DIX 69th)"),
         ("R3 GEX <= 20th", .645, .725, "was on Oct 16 and Oct 22; Fri 23rd"),
         ("R4 R3 + S&P >= 2% off 10d high", .698, .739, f"needs S&P <= {L['R4 needs SPX <=']:,.0f} (from Tue <= 7,602); missed by 0.1% twice"),
         ("R5 R4 + DIX > 50th", .735, .833, "DIX part already on"),
         ("R6 VIX 15% off its 10d max", .552, .643, f"needs VIX <= {L['R6 needs VIX <=']:.1f} (now {L['VIX']:.1f})"),
         ("R7 VIX 25% off its 10d max", .476, .519, f"needs VIX <= {L['R7 needs VIX <=']:.1f}: the rung where calls pay")]
on = {k.split()[0]: v for k, v in L["rungs on"].items()}
fig, (a, b) = plt.subplots(1, 2, figsize=(16, 6.6), gridspec_kw={"width_ratios": [1.45, 1], "wspace": 0.55})
for i, (lab, p12, p19, need) in enumerate(rungs):
    y = len(rungs) - 1 - i
    live = on[lab.split()[0]]
    a.barh(y, p19 * 100, color=GREEN if live else GREY, height=0.62)
    a.scatter(p12 * 100, y, color=INK, s=22, zorder=3)
    a.text(p19 * 100 + 1, y, f"{p19:.0%}" + ("   " + need if need else ""), va="center", fontsize=8.2, color=INK if live else MUTED,
           fontweight="bold" if live else None)
a.axvline(57.6, color=INK, lw=0.9, ls="--"); a.text(57.6, len(rungs) - 0.35, "any day 58%", fontsize=7.5, color=MUTED, ha="center")
a.set_yticks(range(len(rungs)), [r[0] for r in rungs][::-1], fontsize=8.5)
a.set_xlim(0, 150); a.set_xticks(range(0, 101, 20))
a.set_xlabel("P(an S&P up-leg starts within 20 sessions), %   bars: 2019Q4-2026, dots: 2012-2026")
a.set_title(f"SPY on the S&P entry ladder: R1 + R2 ON (SqueezeMetrics, Fri {L['squeeze day'][5:]})\n"
            f"R2 = the earliest rung with a real tilt: 78% vs 58% (64% vs 50% since 2012), lead ~5 days.\n"
            f"Pays with a call SPREAD (+16% vs +12% any day); naked calls only pay at R7 (vol crush).\n"
            f"S&P {L['SPX']:,.0f} Mon, {L['SPX vs 10d high %']:.1f}% off its 10-day high; VIX {L['VIX']:.1f}", loc="left", fontsize=9, color=INK)
states = [("neither", 12, 16, 37, 43), ("below own\nflip only", 13, 15, 55, 41), ("FREED only\n(TSLA NOW)", 20, 23, 60, 61),
          ("freed + below flip\n(full setup)", 39, 17, 76, 67)]
x = range(len(states)); w = 0.36
b.bar([i - w / 2 for i in x], [s[1] for s in states], w, color=GREEN, label="up-burst within 3 sessions")
b.bar([i + w / 2 for i in x], [s[2] for s in states], w, color=RED, label="down-burst within 3 sessions")
for i, s in enumerate(states):
    b.text(i - w / 2, s[1] + 0.8, f"{s[1]}%", ha="center", fontsize=8); b.text(i + w / 2, s[2] + 0.8, f"{s[2]}%", ha="center", fontsize=8)
b.axhline(17, color=INK, lw=0.9, ls="--"); b.text(-0.55, 17.6, "all days 17%", fontsize=7.5, color=MUTED, ha="left")
b.patches[2].set_edgecolor(INK); b.patches[2].set_linewidth(2); b.patches[6].set_edgecolor(INK); b.patches[6].set_linewidth(2)
b.set_xticks(list(x), [s[0] for s in states], fontsize=8)
b.set_ylim(0, 46); b.set_ylabel("share of days, %")
b.legend(frameon=False, fontsize=8, loc="upper left")
o, o2 = T["Oct 26 positions"], T["after Oct 30 expiry"]
b.set_title(f"TSLA on its own-options ladder: FREED, not below the flip\n"
            f"Near-price OI at the {o['near-OI pct']:.0%} pctile ({o2['near-OI pct']:.1%} after Fri expiry); "
            f"{o['% above flip']:.1f}% above flip {o['flip']:.0f}.\n"
            f"Freed = bigger moves both ways (vol-controlled, the extra is up, 1.8x).\n"
            f"Full setup needs a drop under ~{o2['flip']:.0f}-{o['flip']:.0f}. Lid: call wall {o['call wall']:.0f}", loc="left", fontsize=9, color=INK)
fig.savefig(OUT / "ladder_status.png", dpi=140, bbox_inches="tight", facecolor=SURF)
