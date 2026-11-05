"""Descriptive (owner question, no test): does today's macro/valuation look like the 2022 eve or like the early-2025 / early-2026 scares?
Monthly FRED series (data/, gitignored), DFII10, Shiller CAPE (multpl, live). Excess CAPE yield = 1/CAPE - 10y real yield (TIPS from 2003;
proxy 10y minus core CPI y/y for the full span). Usage: python regime.py"""
import json, re, html, urllib.request, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"
M = pd.read_csv(H / "data" / "fred_monthly_1999_2026.csv", index_col=0, parse_dates=True)
M["DFII10"] = pd.read_csv(H / "data" / "fred_dfii10_monthly_2003_2026.csv", index_col=0, parse_dates=True)["DFII10"]
page = urllib.request.urlopen(urllib.request.Request("https://www.multpl.com/shiller-pe/table/by-month", headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "replace")
rows = re.findall(r"<td>\s*([A-Z][a-z]{2} \d{1,2}, \d{4})\s*</td>\s*<td>([^<]*)</td>", page)
cape = pd.Series({pd.Timestamp(d): float(re.search(r"-?\d+(?:\.\d+)?", html.unescape(v)).group()) for d, v in rows}).sort_index()
M["CAPE"] = cape[cape.index.day == 1].reindex(M.index); M = M[M.index <= "2026-10-01"]
M["2y - fed funds"] = M.DGS2 - M.DFF; M["fed funds change 12m"] = M.DFF - M.DFF.shift(12); M["real 10y change 6m"] = M.DFII10 - M.DFII10.shift(6)
M["core CPI change 6m"] = M.CORECPI_YY - M.CORECPI_YY.shift(6); M["oil y/y %"] = 100 * (M.WTI / M.WTI.shift(12) - 1); M["unemployment - 12m low"] = M.UNRATE - M.UNRATE.rolling(12, min_periods=6).min()
M["ECY (TIPS)"] = 100 / M.CAPE - M.DFII10; M["ECY (proxy)"] = 100 / M.CAPE - (M.DGS10 - M.CORECPI_YY)
D = {"Mar 2000": "2000-03-01", "Jan 2022": "2022-01-01", "Feb 2025": "2025-02-01", "Jan 2026": "2026-01-01", "Oct 2026": "2026-10-01"}
cols = ["DFF", "fed funds change 12m", "2y - fed funds", "DGS10", "DFII10", "real 10y change 6m", "CORECPI_YY", "core CPI change 6m", "oil y/y %", "BAA10Y", "unemployment - 12m low", "CAPE", "ECY (TIPS)", "ECY (proxy)"]
T = {k: {c: (None if pd.isna(M.loc[v, c]) else round(float(M.loc[v, c]), 2)) for c in cols} for k, v in D.items()}
T["Oct 2026"]["note"] = "core CPI and unemployment for Oct 2026 not yet released (Sep 2026: core 2.57, unemployment 4.2, 0.1 above its 12-month low)"
e = M["ECY (TIPS)"].dropna(); ep = M["ECY (proxy)"].dropna()
out = {"table": T, "ECY (TIPS) lowest months since 2003": {str(k.date())[:7]: round(float(v), 2) for k, v in e.nsmallest(5).items()},
       "ECY (proxy) months <= 0 since 1999": [str(k.date())[:7] for k in ep[ep <= 0].index], "ECY (proxy) lowest month since 2001": (lambda q: {str(q.idxmin().date())[:7]: round(float(q.min()), 2)})(ep[ep.index >= "2001-01-01"]), "latest (Nov 4-5)": {"CAPE": float(cape.iloc[-1]), "TIPS 10y": 2.64, "ECY (TIPS)": round(100 / float(cape.iloc[-1]) - 2.64, 2)}}
json.dump(out, open(O / "regime.json", "w"), indent=1); print(json.dumps(out, indent=1)[:2500])
# ---- figure: valuation vs real rates, and what the Fed is priced to do
INK, INK2, MUTED, GRID, SURF, BLUE, ORANGE = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#fcfcfb", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})
fig, axs = plt.subplots(2, 1, figsize=(11, 10.5), sharex=True, gridspec_kw={"hspace": 0.38})
mk = {"Mar 2000": ORANGE, "Jan 2022": ORANGE, "Feb 2025": BLUE, "Jan 2026": BLUE, "Oct 2026": INK}
for ax, ser, ttl, sub in ((axs[0], "ECY (TIPS)", "1 · What stocks pay over inflation-protected bonds: earnings yield (1/CAPE) minus the 10-year real yield",
                           "Below 0 = stocks earn less than TIPS. Oct 2026: -0.32 pp, the lowest since TIPS data began in 2003. The dashed proxy (Sep 2026 +0.05) is the lowest since 2000,\nwhen it sat below 0. Jan 2022 started at +3.4 pp, so it had room to compress; the 2025 and 2026 scares started near +0.6 pp."),
                          (axs[1], "2y - fed funds", "2 · What the Fed is priced to do: 2-year yield minus fed funds (above 0 = more hikes priced)",
                           "Feb 2025 and Jan 2026 priced cuts (-0.1), so a 'Fed put' was there. Oct 2026 prices hikes (+0.86; +0.70 on Nov 4) after September's hike, like Jan 2022 (+0.90) and Mar 2000 (+0.68).")):
    if ser == "ECY (TIPS)": ax.plot(M.index, M["ECY (proxy)"], color=MUTED, lw=1.3, ls=(0, (3, 2)), label="proxy: 1/CAPE - (10y - core CPI)")
    ax.plot(M.index, M[ser], color=INK2, lw=2, label="1/CAPE - TIPS 10y" if ser == "ECY (TIPS)" else None)
    ax.axhline(0, color=MUTED, lw=1)
    for k, v in D.items():
        val = M.loc[v, ser] if not pd.isna(M.loc[v, ser]) else (M.loc[v, "ECY (proxy)"] if ser == "ECY (TIPS)" else np.nan)
        ax.scatter([pd.Timestamp(v)], [val], s=80, color=mk[k], edgecolor=SURF, linewidth=1.5, zorder=4, marker="D" if k == "Oct 2026" else "o")
        dx, ha = {"Feb 2025": (-10, "right"), "Jan 2026": (10, "left")}.get(k, (0, "center"))
        ax.annotate(f"{k}\n{val:+.2f}", (pd.Timestamp(v), val), xytext=(dx, 12 if val >= 0 or ser != "ECY (TIPS)" else -26), textcoords="offset points", ha=ha, fontsize=8.6, color=INK, fontweight="bold" if k == "Oct 2026" else None)
    ax.set_title(ttl, loc="left", fontsize=12, fontweight="bold", color=INK, pad=12 + 14 * (sub.count("\n") + 1)); ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9, color=INK2, va="bottom", linespacing=1.35)
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True); ax.set_ylabel("percentage points")
axs[0].set_ylim(-3, 8.5); axs[0].legend(loc="upper left", fontsize=8.6, frameon=False)
axs[1].text(0, -0.13, "Orange = eve of a bear market (2000, 2022). Blue = scares that recovered (2025, 2026). Diamond = today's record month. FRED (DFII10, DGS10, DGS2, DFF, core CPI); multpl (CAPE).",
            transform=axs[1].transAxes, fontsize=8, color=MUTED)
fig.savefig(O / "regime_compare.png", dpi=150, bbox_inches="tight"); print("figure written")
