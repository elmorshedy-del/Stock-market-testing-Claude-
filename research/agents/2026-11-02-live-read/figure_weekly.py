"""ADHD figure: TSLA's weekly rhythm since Oct 19 (price halves + freed-by-day), the 2023-26 base rates, and this week's calls."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent; W = json.load(open(HERE / "out" / "weekly_rhythm.json"))
BLUE, ORG, BG, INK, INK2, GRID, GRAY, LG = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#efeeea"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(17, 10.5), facecolor=BG)
gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.85], width_ratios=[1, 1.25], hspace=0.38, wspace=0.18, left=0.06, right=0.97, top=0.85, bottom=0.05)
fig.text(0.02, 0.945, "TSLA's weekly rhythm is real in the positioning: freed on Monday, piled up by midweek", fontsize=20, weight="bold", color=INK)
fig.text(0.02, 0.9, "Up early, down late in both weeks since Oct 19. The Friday weekly expiry clears contracts near the price, so Mondays start freed. Descriptive, not a test.", fontsize=12, color=INK2)
ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor(BG)
wk = W["(c) by week, compounded % [Mon-Wed, Thu-Fri]"]; labs = ["Oct 12 wk\n(the reset)", "Oct 19 wk", "Oct 26 wk"]
for i, (k, (a, b)) in enumerate(wk.items()):
    ax.bar(i - 0.18, a, 0.34, color=BLUE if a > 0 else ORG); ax.bar(i + 0.18, b, 0.34, color=BLUE if b > 0 else ORG, alpha=0.55)
    ax.text(i - 0.18, a + (0.4 if a > 0 else -1.0), f"{a:+.1f}", ha="center", fontsize=12, weight="bold"); ax.text(i + 0.18, b + (0.4 if b > 0 else -1.0), f"{b:+.1f}", ha="center", fontsize=12)
ax.axhline(0, color=INK2, lw=1); ax.set_xticks(range(3)); ax.set_xticklabels(labs, fontsize=11); ax.set_ylabel("% move"); ax.yaxis.grid(True, color=GRID); ax.set_ylim(-6, 11)
ax.text(-0.45, 10, "solid = Mon–Wed   faded = Thu–Fri", fontsize=10.5, color=INK2)
ax.set_title("Price: up first half, down second half", loc="left", fontsize=14, weight="bold", color=INK)
ax = fig.add_subplot(gs[0, 1]); ax.set_facecolor(BG)
a = W["(a) going into each day (OI files only)"]; d = [k for k in a if k >= "2026-10-19"]; v = [100 * a[k]["near pct"] for k in d]
cols = [ORG if a[k]["weekday"] == "Mon" else BLUE for k in d]
ax.bar(range(len(d)), v, color=cols); ax.axhline(33, color=ORG, ls="--", lw=1.2); ax.text(len(d) - 0.5, 35, "freed below 33", fontsize=10, color=ORG, ha="right")
for i, (k, x) in enumerate(zip(d, v)): ax.text(i, x + 1.5, f"{x:.0f}", ha="center", fontsize=10.5, weight="bold" if a[k]["weekday"] == "Mon" else "normal")
ax.set_xticks(range(len(d))); ax.set_xticklabels([a[k]["weekday"] + "\n" + k[5:] for k in d], fontsize=9.5); ax.set_ylim(0, 80); ax.set_ylabel("near-price OI pct"); ax.yaxis.grid(True, color=GRID)
ax.set_title("Positioning: every Monday starts freed (orange)", loc="left", fontsize=14, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, 0]); ax.axis("off")
b = W["(b) engine 2023-Oct 2026, mean pct by weekday [near-OI pct, own-gamma pct, n]"]; dd = W["(d) 2023-26 weeks (n, mean Mon-Wed %, mean Thu-Fri %, share of weeks up-then-down)"]; up = W["(d) weeks with Mon-Wed > +5%: n, mean Thu-Fri %, share Thu-Fri down"]
ax.set_title("Is it a rule? 2023–26 (200 weeks)", loc="left", fontsize=14, weight="bold", color=INK)
L = [(f"✓ Near-price OI by weekday: Mon {int(100*b['Mon'][0])} · Tue {int(100*b['Tue'][0])} · Wed {int(100*b['Wed'][0])} · Thu {int(100*b['Thu'][0])} · Fri {int(100*b['Fri'][0])}", INK),
     (f"✓ Mon–Wed averages {dd[1]:+.1f}%, Thu–Fri {dd[2]:+.1f}%  (Monday up-bursts 1.95×, tested)", INK),
     (f"✗ After a big first half (> +5%, {up[0]} weeks): Thu–Fri fell only {int(100*up[2])}%", ORG),
     ("    → the rise-early part is real; the fade-late part is a coin flip", ORG)]
for i, (t, c) in enumerate(L): ax.text(0, 0.82 - i * 0.2, t, fontsize=12.3, color=c, transform=ax.transAxes, weight="bold" if i == 3 else "normal")
ax = fig.add_subplot(gs[1, 1]); ax.axis("off"); ax.set_title("This week", loc="left", fontsize=14, weight="bold", color=INK)
ax.add_patch(FancyBboxPatch((0, 0.05), 1, 0.85, boxstyle="round,pad=0.02,rounding_size=0.03", fc="#f4f3ef", ec=GRID, transform=ax.transAxes))
L = [("Setup matches: Monday freed (23rd pct), pre-market up +1.2%", INK, True), ("…but weaker than the last two Mondays (14th, 16th) and the election lands Tue–Wed", INK2, False),
     ("Fri Nov 6 holds 56% of the near-price contracts → late-week pin, then a Mon Nov 9 flush", INK2, False),
     ("W1  pop ≥ +3% (≥ 412) by Wed: 60%   •   W2  Fri close < Wed close: 60%", BLUE, True),
     ("W3  Fri close ≥ 420 (keeps your steep channel's pace): 20%", ORG, True),
     ("Hand-drawn channel lines held only 48–50% in our TSLA test: treat the line as a guide, not a floor", INK2, False)]
for i, (t, c, bold) in enumerate(L): ax.text(0.03, 0.8 - i * 0.13, t, fontsize=11.6, color=c, weight="bold" if bold else "normal", transform=ax.transAxes)
fig.savefig(HERE / "out" / "weekly_rhythm.png", dpi=110, facecolor=BG); print("ok")
