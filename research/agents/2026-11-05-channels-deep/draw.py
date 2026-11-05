"""Observation: log-linear channels (2009 and 2023 starts, OLS on log price, +-1/2 sigma) for SPX, QQQ, SMH, RSP. In-sample fits, as drawn on a chart."""
import sys, importlib.util, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
def fit(s, start):
    x = s[s.index >= start]; t = (x.index - x.index[0]).days.values / 365.25; y = np.log(x.values)
    b, a = np.polyfit(t, y, 1); sd = (y - (a + b * t)).std(); return x.index, np.exp(a + b * t), sd, b, (y[-1] - (a + b * t[-1])) / sd
fig, axes = plt.subplots(2, 2, figsize=(16, 10.5), dpi=150); out = {}
for ax, (sym, nm) in zip(axes.flat, (("^GSPC", "S&P 500"), ("QQQ", "Nasdaq-100 (QQQ)"), ("SMH", "Chips (SMH)"), ("RSP", "Equal-weight S&P (RSP)"))):
    s = lc.yahoo(sym, "2008-06-01").close; s = s[s.index >= "2009-01-01"]
    ax.semilogy(s.index, s.values, color="#212121", lw=0.9)
    for start, col, lab in (("2009-03-09", "#1565c0", "2009 channel"), ("2023-01-03", "#c62828", "2023 channel")):
        idx, mid, sd, b, z = fit(s, start)
        ax.plot(idx, mid, color=col, lw=1.2, ls="-", label=f"{lab} (trend {100*(np.exp(b)-1):.0f}%/yr, now z {z:+.1f})")
        for k, ls in ((1, ":"), (2, "--")):
            ax.plot(idx, mid * np.exp(k * sd), color=col, lw=0.8, ls=ls); ax.plot(idx, mid * np.exp(-k * sd), color=col, lw=0.8, ls=ls)
        out[f"{nm} {lab}"] = {"z": round(float(z), 2), "-2σ now": round(float(mid[-1] * np.exp(-2 * sd)), 2), "mid now": round(float(mid[-1]), 2), "+2σ now": round(float(mid[-1] * np.exp(2 * sd)), 2), "trend %/yr": round(100 * (np.exp(b) - 1), 1)}
    ax.scatter(s.index[-1], s.iloc[-1], color="#c62828", s=40, zorder=5); ax.annotate(f"{s.iloc[-1]:,.0f}", (s.index[-1], s.iloc[-1]), xytext=(-60, -16), textcoords="offset points", fontsize=9, fontweight="bold", color="#c62828")
    ax.set_title(nm, loc="left", fontweight="bold"); ax.legend(frameon=False, fontsize=8.5, loc="upper left"); ax.spines[["top", "right"]].set_visible(False)
    # inset: zoom on 2023+
    ins = ax.inset_axes([0.58, 0.06, 0.4, 0.38]); z0 = s[s.index >= "2023-01-01"]; ins.semilogy(z0.index, z0.values, color="#212121", lw=0.8)
    idx, mid, sd, b, z = fit(s, "2023-01-03"); ins.plot(idx, mid, color="#c62828", lw=1)
    for k, ls in ((1, ":"), (2, "--")): ins.plot(idx, mid * np.exp(k * sd), color="#c62828", lw=0.7, ls=ls); ins.plot(idx, mid * np.exp(-k * sd), color="#c62828", lw=0.7, ls=ls)
    ins.scatter(z0.index[-1], z0.iloc[-1], color="#c62828", s=20, zorder=5); ins.set_xticks([]); ins.set_yticks([]); ins.set_title("2023 → now", fontsize=8, loc="left")
fig.suptitle("Channels redrawn: the equal-weight S&P sits mid-channel; the S&P sits on its 2023 floor; QQQ is below it; chips are inside both", x=0.01, ha="left", fontsize=13, fontweight="bold")
fig.text(0.01, 0.005, "Log-price OLS channels; solid = midline, dotted = ±1σ, dashed = ±2σ. In-sample fits (the line uses the whole window, so past touches look cleaner than they were live). Yahoo daily closes to Nov 5, 2026.", fontsize=7.5, color="#555")
plt.tight_layout(rect=(0, 0.02, 1, 0.95)); plt.savefig(O / "channels_redrawn.png"); import json; json.dump(out, open(O / "channels_insample.json", "w"), indent=1); print(json.dumps(out, indent=1))
