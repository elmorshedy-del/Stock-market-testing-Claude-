"""Descriptive addendum (owner's chart question, no test): draw the S&P, QQQ and SMH channels by ONE rule. Slope = OLS trend of log price
since 2023-01-03; one parallel line through the 2026 scare low (2026-03-30 close) and one through the 2025 crash low (2025-04-08 close).
Usage: python same_rule.py -> out/same_rule.json, out/same_rule_lines.png"""
import json, importlib.util, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
INK, INK2, MUTED, GRID, SURF, BLUE, ORANGE = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#fcfcfb", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})
names = {"^GSPC": "S&P 500", "QQQ": "Nasdaq-100 (QQQ)", "SMH": "Chips (SMH)"}; LOWS = {"2026 scare low": "2026-03-30", "2025 crash low": "2025-04-08"}
fig, axs = plt.subplots(1, 3, figsize=(15, 6.2), gridspec_kw={"wspace": 0.22}); out = {}
for ax, sym in zip(axs, names):
    s = lc.yahoo(sym, "2022-06-01").close; x = s[s.index >= "2023-01-03"]; t = np.arange(len(x)); b, a = np.polyfit(t, np.log(x.values), 1); n = len(x) - 1
    w = s[s.index >= "2022-10-01"].resample("W-FRI").last(); ax.plot(w.index, w.values, color=INK2, lw=1.5, zorder=2)
    res = {"trend %/yr": round(100 * (np.exp(252 * b) - 1), 1), "close": round(float(s.iloc[-1]), 2)}
    for (lab, d), col in zip(LOWS.items(), (BLUE, ORANGE)):
        i = x.index.get_loc(pd.Timestamp(d)); c = np.log(x.iloc[i]) - b * i; jj = np.arange(i - 260, n + 1); jj = jj[jj >= 0]
        ax.plot(x.index[jj], np.exp(c + b * jj), color=col, lw=2, zorder=3); ax.scatter([x.index[i]], [x.iloc[i]], s=55, color=col, edgecolor=SURF, linewidth=1.3, zorder=4)
        today = float(np.exp(c + b * n)); gap = 100 * (today / s.iloc[-1] - 1); res[lab] = {"anchor close": round(float(x.iloc[i]), 2), "line today": round(today, 1), "gap from today's close %": round(gap, 1)}
        txt = f"{today:,.0f} ({gap:+.1f}%)" if gap < 0 else f"{today:,.0f} (broken)"
        ax.annotate(txt, (x.index[n], today), xytext=(6, 0), textcoords="offset points", va="center", fontsize=9, color=col, fontweight="bold")
    ax.scatter([s.index[-1]], [s.iloc[-1]], marker="D", s=60, color=INK, zorder=5)
    ax.annotate(f"today {s.iloc[-1]:,.0f}", (s.index[-1], s.iloc[-1]), xytext=(-8, 10), textcoords="offset points", ha="right", fontsize=9, color=INK, fontweight="bold")
    ax.set_yscale("log"); ax.set_xlim(pd.Timestamp("2022-10-01"), pd.Timestamp("2028-03-01")); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    yt = {"^GSPC": [4000, 5000, 6000, 7000, 8000], "QQQ": [300, 400, 500, 600, 700], "SMH": [100, 150, 200, 300, 450, 650]}[sym]
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator()); ax.set_yticks(yt); ax.set_yticklabels([f"{v:,}" for v in yt])
    ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in range(2023, 2028)]); ax.set_xticklabels([str(y) for y in range(2023, 2028)])
    ax.set_title(f"{names[sym]}   trend {res['trend %/yr']:+.0f}%/yr", loc="left", fontsize=11.5, fontweight="bold", color=INK); out[sym] = res
fig.suptitle("Same rule for all three: lines parallel to the 2023 trend, through the 2026 scare low (blue) and the 2025 crash low (orange)", x=0.125, ha="left", fontsize=12.5, fontweight="bold", color=INK, y=1.02)
fig.text(0.125, 0.955, "Blue: the S&P has ~4% left to it, QQQ is on it, SMH already broke it. Orange: everything has room (S&P ~10%, QQQ ~8%, SMH ~23%); chips' room is ~2.3x the S&P's.",
         fontsize=9.5, color=INK2, ha="left")
fig.text(0.125, 0.0, "Weekly closes since Oct 2022 (Yahoo). Lines use daily closes and the OLS slope of log price since 2023-01-03. Diamond = Nov 5, 2026 close.", fontsize=8, color=MUTED)
fig.savefig(O / "same_rule_lines.png", dpi=150, bbox_inches="tight"); json.dump(out, open(O / "same_rule.json", "w"), indent=1); print(json.dumps(out, indent=1))
