"""TSLA checklist at the Nov 4 close + what today's trading could do to the flip. -> out/tsla_checklist.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent; O = HERE / "out"
S = json.load(open(O / "tsla_close_state.json")); G = json.load(open(O / "tsla_flip_grid.json"))
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE, RED, GREEN = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834", "#c8372d", "#2f8f5b"
plt.rcParams.update({"font.size": 10.5, "axes.titleweight": "bold", "axes.titlesize": 12})
fig = plt.figure(figsize=(16, 7.4), facecolor=BG); a = fig.add_axes([0.01, 0.08, 0.47, 0.80]); b = fig.add_axes([0.665, 0.16, 0.325, 0.66])
a.axis("off"); a.set_facecolor(BG)
rows = [  # (hit, name, now, needed, how far)
    (True, "Freed (options near price thin)", "24th pct", "≤ 33rd", "✓ 9 pts room"),
    (False, "FULL SETUP: close below own flip", "385.19 vs flip 377.6", "close ≤ 377.6", "−2.0%  (−$7.6)"),
    (False, "Practical lean: within 1% of flip", "+2.0% above", "≤ 381.4", "−1.0%  (−$3.8)"),
    (False, "Deep freed", "24th pct", "≤ 5th", "19 pts"),
    (False, "Washed-out RSI", "RSI 51", "≤ 38", "13 pts"),
    (True, "ATR not low (bursts need range)", "63rd pct", "> 33rd", "✓"),
    (True, "T5 warning off (S&P not in R4)", "SPY −0.7% off high", "R4: ≥ 2% off", "✓ (check tonight)"),
    (True, "S&P gamma reset", "17th pct", "≤ 30th", "✓"),
    (False, "R7 vol crush (VIX)", "VIX 16.61 (−21.5%)", "≤ 15.86 (−25%)", "0.75 VIX pts"),
    (True, "TSLA's own dark-pool buying high", "76th pct", "top third", "✓ lean"),
]
y = 0.95; a.text(0.0, 1.0, "TSLA at the Nov 4 close: what's hit, what's not, how far", fontsize=13, fontweight="bold", color=INK, transform=a.transAxes)
for i, (lab, ttl) in enumerate([("", 0.0), ("condition", 0.05), ("now", 0.45), ("needs", 0.66), ("how far", 0.84)]):
    a.text(ttl, y - 0.02, lab, fontsize=9.5, color=INK2, transform=a.transAxes, fontweight="bold")
for k, (hit, nm, now, need, far) in enumerate(rows):
    yy = y - 0.08 - k * 0.083; col = GREEN if hit else RED
    if k == 1: a.add_patch(plt.Rectangle((-0.005, yy - 0.03), 1.0, 0.07, transform=a.transAxes, color="#fbe9e7", zorder=0))
    a.text(0.0, yy, "●", color=col, fontsize=16, transform=a.transAxes, va="center")
    a.text(0.05, yy, nm, fontsize=10.5, color=INK, transform=a.transAxes, va="center", fontweight="bold" if k == 1 else "normal")
    a.text(0.45, yy, now, fontsize=9.8, color=INK2, transform=a.transAxes, va="center"); a.text(0.66, yy, need, fontsize=9.8, color=INK2, transform=a.transAxes, va="center")
    a.text(0.84, yy, far, fontsize=9.3, color=col, transform=a.transAxes, va="center", fontweight="bold")
a.text(0.0, -0.04, "State = the engine's own definition: OI dated Nov 4 (Tuesday's positions) + Nov 4 closing chain. \nThat state is fixed: not a full setup.",
       fontsize=8.8, color=INK2, transform=a.transAxes)
# right: flip scenarios
sc = [("official (today's IVs)", S["official state at Nov 4 close (OI dated Nov 4 + Nov 4 chain)"]), ("Tuesday's IVs (no IV move)", S["same positions with Tue Nov 3 IVs (isolates today's IV move)"]),
      ("+25% of all volume opens", S["+25% of today's volume as new OI (all)"]), ("+100% of all volume opens", S["+100% of today's volume as new OI (all)"]),
      ("+10% of PUT volume opens", G["P 0.1"]), ("+15% of PUT volume opens", G["P 0.15"]), ("+20% of PUT volume opens", G["P 0.2"]),
      ("+50% of PUT volume opens", S["+50% of today's PUT volume as new OI"]), ("+10% of CALL volume opens", G["C 0.1"])]
for i, (nm, s) in enumerate(sc[::-1]):
    col = GREEN if s["freed"] else GRAY; mk = "o"
    b.scatter(s["flip"], i, s=110, color=col, edgecolor=INK, zorder=5, marker=mk)
    b.text(s["flip"] + 0.4, i, f"{s['flip']:.1f}" + ("" if s["freed"] else "  (freed OFF)"), va="center", fontsize=9, color=INK2)
b.set_yticks(range(len(sc)), [n for n, _ in sc[::-1]], fontsize=9.5)
b.axvline(385.19, color=INK, lw=2); b.text(385.4, -0.85, "close 385.19", fontsize=9.5, fontweight="bold")
b.axvspan(385.19, 402, color=RED, alpha=0.06); b.text(394, 1.2, "flip above the close\n= 'below the flip'", fontsize=9, color=RED, ha="center")
b.set_xlim(368, 402); b.set_ylim(-1.2, len(sc) - 0.5); b.grid(True, axis="x", color=GRID); b.set_facecolor(BG); b.spines[["top", "right"]].set_visible(False)
b.set_xlabel("TSLA flip ($) in each case\ngreen = still freed · gray = freed turns off", fontsize=9.5)
b.set_title("Could today's trading put TSLA below its flip?\nOnly if mostly puts opened, and that un-frees it", loc="left")
fig.text(0.53, 0.012, "IV crush barely touched TSLA: 30-day ATM IV 45.2% → 43.3%, flip 377.5 → 377.6.\nToday's volume at 360–410: 296k calls, 269k puts (top: 400C 58k, 380P 53k). Real new positions (OI dated Nov 5) publish ~6–7am ET.", fontsize=8.8, color=INK2)
plt.savefig(O / "tsla_checklist.png", dpi=150, facecolor=BG); print("ok")
