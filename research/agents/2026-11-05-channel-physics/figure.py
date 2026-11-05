"""Figure for channel-physics: T1 variance ratios, T2 channel force, A1 reliability. Usage: python figure.py -> out/physics_tests.png"""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"
INK, INK2, MUTED, GRID, SURF, BAND, BLUE, ORANGE, AQUA = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#fcfcfb", "#e4e3de", "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})
P, A, S2 = json.load(open(O / "physics.json")), json.load(open(O / "a1.json")), json.load(open(O / "s2.json")); Z = np.load(O / "surrogates.npz")
names = ["S&P 500", "Nasdaq-100", "SOX"]; Q = [21, 63, 126, 252, 504, 756]; HZ = [21, 63, 252]
fig = plt.figure(figsize=(15, 10.6)); gs = fig.add_gridspec(2, 3, hspace=0.62, wspace=0.28)
for j, nm in enumerate(names):
    ax = fig.add_subplot(gs[0, j]); VR = Z[nm + "_VR"]; lo, md, hi = (np.percentile(VR, q, axis=0) for q in (2.5, 50, 97.5)); obs = [P[nm]["VR observed"][str(q)] for q in Q]
    ax.fill_between(Q, lo, hi, color=BAND, lw=0, label="random walk, same daily moves (95%)"); ax.plot(Q, md, color=MUTED, lw=1.2, ls=(0, (3, 2)), label="random walk median")
    ax.plot(Q, obs, color=INK, lw=2, marker="o", ms=6, label="actual"); ax.axhline(1, color=MUTED, lw=0.8)
    ax.set_xscale("log"); ax.set_xticks(Q); ax.set_xticklabels(["1m", "3m", "6m", "1y", "2y", "3y"]); ax.minorticks_off(); ax.set_ylim(0.3, 2.1); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    p = P[nm]["VR one-sided p (below)"]["756"]
    ax.set_title(f"{nm} ({P[nm]['start'][:4]}-2026)", loc="left", fontsize=11, fontweight="bold", color=INK, pad=22); ax.text(0, 1.015, f"3-year ratio {obs[-1]:.2f}; random walks {lo[-1]:.2f}-{hi[-1]:.2f} (p = {p:.2f})", transform=ax.transAxes, fontsize=8.8, color=INK2, va="bottom")
    if j == 0: ax.set_ylabel("variance ratio (< 1 = pulls back to trend)"); ax.legend(loc="upper left", fontsize=8.2, frameon=False)
fig.text(0.125, 0.955, "1 · Is there a restoring force? Variance ratios vs random walks with the market's real daily moves: no (H-T1 fails, Holm p 0.73)", fontsize=12.5, fontweight="bold", color=INK)
ax = fig.add_subplot(gs[1, 0]); xs = []; k = 0
for j, nm in enumerate(names):
    for h_i, h in enumerate(HZ):
        B = Z[nm + "_B"][:, h_i]; lo, hi = np.percentile(B, [2.5, 97.5]); ob = P[nm]["beta observed (fwd log return per 1 sigma of z)"][str(h)]; x = k
        ax.plot([x, x], [100 * lo, 100 * hi], color=MUTED, lw=6, alpha=0.45, solid_capstyle="round"); ax.scatter([x], [100 * ob], s=46, color=INK, zorder=3); xs.append((x, f"{['SPX', 'NDX', 'SOX'][j]}\n{h}d")); k += 1
    k += 0.8
ax.axhline(0, color=MUTED, lw=0.8); ax.set_xticks([x for x, _ in xs]); ax.set_xticklabels([l for _, l in xs], fontsize=7.8); ax.set_ylabel("forward return per 1σ of channel position (%)")
ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.set_title("2 · Does channel position predict returns?", loc="left", fontsize=11, fontweight="bold", color=INK, pad=44)
ax.text(0, 1.02, "Dots = actual; grey bars = random walks (95%).\nAll inside, slightly positive (momentum), the\nopposite of a pull back to the line. H-T2 fails.", transform=ax.transAxes, fontsize=8.8, color=INK2, va="bottom")
ax = fig.add_subplot(gs[1, 1]); cells = A["S&P 500 (primary)"]["cells"]; cols = {"-5% within 21": BLUE, "-5% within 63": AQUA, "-10% within 21": ORANGE, "-10% within 63": INK2}
for c, v in cells.items():
    rel = np.array(v["reliability (pred, obs, n) by decile"]); ax.plot(100 * rel[:, 0], 100 * rel[:, 1], marker="o", ms=5, lw=1.6, color=cols[c], label=f"{c} days (skill {v['BSS']:+.2f})")
ax.plot([0, 100], [0, 100], color=MUTED, lw=1, ls=(0, (3, 2))); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_xlabel("model probability of a fall (%)"); ax.set_ylabel("how often it happened, 2008-2026 (%)")
ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True); ax.legend(loc="upper left", fontsize=7.8, frameon=False)
ax.set_title("3 · The physics model: random walk + VIX", loc="left", fontsize=11, fontweight="bold", color=INK, pad=44)
ax.text(0, 1.02, f"Fit 1990-2007 (k = {A['S&P 500 (primary)']['k']}), tested 2008-2026. Right on\naverage, too high when VIX is high (fear fades), too\nlow when VIX is low (falls from calm). H-A1 fails.", transform=ax.transAxes, fontsize=8.8, color=INK2, va="bottom")
ax = fig.add_subplot(gs[1, 2]); ax.axis("off"); t = A["today (same-rule lines)"]; s2 = S2["surrogates (M0)"]
lines = ["4 · What survives, and today's odds", "",
         f"Channel-break rule on random walks: {100*s2['share 20%+: median / 5-95%'][0]:.0f}% became bears", f"(actual {100*S2['observed']['share became 20%+ bears']:.0f}%) and {100*s2['share 10%+: median / 5-95%'][0]:.0f}% fell 10%+ (actual 100%).",
         "Adding channel position to the volatility model:", "no gain out of sample (H-A2 holds).", "",
         "Model odds of touching the same-rule lines:"]
sp, qq = t["S&P 500"], t["QQQ (Nasdaq-100 model, VXN)"]
for nm, d, keys in (("S&P", sp, ("line through the 2026 low (7,076.2)", "line through the 2025 low (6,616.1)")), ("QQQ", qq, ("line through the 2026 low (641.6)", "line through the 2025 low (596.8)"))):
    for kk in keys:
        v = d[kk]; lines.append(f"  {nm} {kk.split('(')[1][:-1]}: {100*v['touch within 21']:.0f}% in a month, {100*v['touch within 63']:.0f}% in 3 months")
lines += ["", "Fat tails: real 10% falls came ~1.4x the model's rate,", "so read the deeper odds as floors."]
for i, l in enumerate(lines): ax.text(0, 1.0 - i * 0.062, l, transform=ax.transAxes, fontsize=12 if i == 0 else 9.3, fontweight="bold" if i == 0 else None, color=INK if i == 0 else INK2, va="top")
fig.text(0.125, 0.02, "Pre-registered study 2026-11-05-channel-physics (T1-T3 @ 1922c56, A1 @ 77b4866). Random walks = sign-randomized surrogates: every daily move kept, its direction shuffled (2,000 per index). Yahoo daily closes, ^VIX, ^VXN.", fontsize=8, color=MUTED)
fig.savefig(O / "physics_tests.png", dpi=150, bbox_inches="tight"); print("ok")
