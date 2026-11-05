"""Descriptive 2000 vs 2026 comparison (owner asked for reasoning, not a test). Usage: python figure.py <prices.csv> <fred_macro.csv>"""
import sys, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, pandas as pd, numpy as np
from pathlib import Path
O = Path(__file__).resolve().parent / "out"
P = pd.read_csv(sys.argv[1], index_col=0, parse_dates=True); M = pd.read_csv(sys.argv[2], index_col=0, parse_dates=True)
B, R = "#6d4c41", "#c62828"
fig = plt.figure(figsize=(15, 10), dpi=150); gs = fig.add_gridspec(2, 2, hspace=0.38, wspace=0.22)
# A year shape
a = fig.add_subplot(gs[0, 0])
for y, c, lab in ((2000, B, "Nasdaq-100 in 2000"), (2026, R, "Nasdaq-100 in 2026")):
    base = P["^NDX"][P.index < f"{y}-01-01"].iloc[-1]; x = P["^NDX"][f"{y}-01-01":f"{y}-12-31"]; x = 100 * (x / base - 1)
    a.plot(x.index.dayofyear, x.values, color=c, lw=2, label=lab)
    nv = x[:f"{y}-11-05"]; a.scatter(nv.index[-1].dayofyear, nv.iloc[-1], color=c, s=40, zorder=4)
    pk = x.idxmax(); a.annotate(f"peak {pk:%b %d}", (pk.dayofyear, x.max()), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8.5, color=c)
a.axvline(pd.Timestamp("2026-11-05").dayofyear, color="#999", lw=0.8, ls=":"); a.text(pd.Timestamp("2026-11-05").dayofyear - 2, -38, "Nov 5", ha="right", fontsize=8, color="#666")
a.axhline(0, color="#bbb", lw=0.8)
mt = pd.date_range("2026-01-01", periods=12, freq="MS"); a.set_xticks(mt.dayofyear); a.set_xticklabels(mt.strftime("%b"), fontsize=8)
a.set_ylabel("% from Jan 1"); a.set_ylim(-44, 34); a.legend(frameon=False, fontsize=9, loc="lower left")
a.set_title("A. Different year: 2000's top was in March, 2026's in October", loc="left", fontweight="bold", fontsize=11)
# B semis
b = fig.add_subplot(gs[0, 1])
for pk, c, lab, end in (("2000-03-10", B, "chips (SOX) from Mar 10, 2000 peak", "2001-03-30"), ("2026-06-22", R, "chips (SOX) from Jun 22, 2026 peak", "2026-12-31")):
    x = P["^SOX"][pk:end]; x = 100 * (x / x.iloc[0] - 1); b.plot(range(len(x)), x.values, color=c, lw=2, label=lab)
b.scatter(len(P["^SOX"]["2026-06-22":]) - 1, 100 * (P["^SOX"].iloc[-1] / P["^SOX"]["2026-06-22"] - 1), color=R, s=40, zorder=4)
i00 = len(P["^SOX"]["2000-03-10":"2000-11-30"]) - 1; v00 = 100 * (P["^SOX"][:"2000-11-30"].iloc[-1] / P["^SOX"]["2000-03-10"] - 1)
b.annotate("Nov 30, 2000", (i00, v00), xytext=(8, -2), textcoords="offset points", fontsize=8.5, color=B)
b.annotate("today", (len(P["^SOX"]["2026-06-22":]) - 1, 100 * (P["^SOX"].iloc[-1] / P["^SOX"]["2026-06-22"] - 1)), xytext=(8, -10), textcoords="offset points", fontsize=9, color=R, fontweight="bold")
b.axhline(0, color="#bbb", lw=0.8); b.set_xlabel("sessions since the chip peak"); b.set_ylabel("% from peak")
b.set_title("B. Same chip pattern: peak, lower high, collapse (2026 faster)", loc="left", fontweight="bold", fontsize=11)
b.legend(frameon=False, fontsize=9, loc="lower left")
# C rotation
c = fig.add_subplot(gs[1, 0])
names = {"XLK": "Tech", "XLY": "Discretionary", "XLI": "Industrials", "XLE": "Energy", "XLF": "Financials", "XLU": "Utilities", "XLV": "Health care", "XLP": "Staples", "^NYA": "Average stock (NYSE)"}
def r(a_, b_): x = P[(P.index >= a_) & (P.index <= b_)]; return 100 * (x.iloc[-1] / x.iloc[0] - 1)
r00 = r("2000-03-27", "2000-11-03"); r26 = r("2026-10-06", "2026-11-05"); y = np.arange(len(names))
c.barh(y + 0.2, [r00[k] for k in names], 0.38, color=B, label="2000: Nasdaq peak (Mar 27) → Nov 3 (7 months)")
c.barh(y - 0.2, [r26[k] for k in names], 0.38, color=R, label="2026: Nasdaq peak (Oct 6) → today (1 month)")
c.set_yticks(y); c.set_yticklabels(list(names.values()), fontsize=9); c.axvline(0, color="k", lw=0.8)
c.set_xlabel("% return"); c.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=1)
c.set_title("C. Same rotation: out of tech, into defensives; average stock holds", loc="left", fontweight="bold", fontsize=11)
# D macro table
d = fig.add_subplot(gs[1, 1]); d.axis("off")
g = lambda s, dt: M.loc[dt, s]
rows = [("Fed", f"done hiking, 6.5%", f"hiked Sep 17 to {g('DFF','2026-10-01'):.2f}%", "differs"),
        ("2y vs Fed funds", f"{g('DGS2','2000-11-01'):.2f} < {g('DFF','2000-11-01'):.2f}: pricing cuts", f"{g('DGS2','2026-10-01'):.2f} > {g('DFF','2026-10-01'):.2f}: pricing hikes", "differs"),
        ("10y yield (year)", f"falling {g('DGS10','2000-01-01'):.1f} → {g('DGS10','2000-11-01'):.1f}", f"rising {g('DGS10','2026-01-01'):.1f} → {g('DGS10','2026-10-01'):.1f}", "differs"),
        ("Curve 10y−2y", f"inverted ({g('T10Y2Y','2000-11-01'):+.2f})", f"positive ({g('T10Y2Y','2026-10-01'):+.2f})", "differs"),
        ("Credit (Baa−10y)", f"widening {g('BAA10Y','2000-01-01'):.2f} → {g('BAA10Y','2000-11-01'):.2f}", f"tight {g('BAA10Y','2026-01-01'):.2f} → {g('BAA10Y','2026-10-01'):.2f}", "differs"),
        ("Oil (WTI)", f"${g('WTI','2000-11-01'):.0f}, up ~{100*(g('WTI','2000-11-01')/g('WTI','1999-11-01')-1):.0f}% y/y", f"${g('WTI','2026-10-01'):.0f}, up ~{100*(g('WTI','2026-10-01')/g('WTI','2026-01-01')-1):.0f}% this year", "rhymes"),
        ("Core inflation", f"{g('CORECPI_YY','2000-11-01'):.1f}%", f"{g('CORECPI_YY','2026-09-01'):.1f}%", "rhymes"),
        ("Unemployment", f"{g('UNRATE','2000-11-01'):.1f}% (very tight)", f"{g('UNRATE','2026-09-01'):.1f}% (softer)", "differs"),
        ("VIX", "~26 all month", f"{P['^VIX'].iloc[-1]:.0f} today (was ~17)", "rhymes now")]
t = d.table(cellText=[[a_, b_, c_, e_] for a_, b_, c_, e_ in rows], colLabels=["", "Nov 2000", "Oct–Nov 2026", ""], loc="upper center", cellLoc="left", colWidths=[0.2, 0.33, 0.33, 0.14])
t.auto_set_font_size(False); t.set_fontsize(8.6); t.scale(1, 1.55)
for (i, j), cell in t.get_celld().items():
    cell.set_edgecolor("#ddd")
    if i == 0: cell.set_text_props(fontweight="bold")
    if j == 3 and i > 0: cell.set_text_props(color="#2e7d32" if "rhymes" in rows[i - 1][3] else R, fontweight="bold")
d.set_title("D. Macro: 2026 looks like SPRING 2000 (tightening),\n     not November 2000 (credit cracking)", loc="left", fontweight="bold", fontsize=11)
fig.suptitle("2000 vs now: same rotation and chip pattern, but a different phase. Today rhymes with spring 2000, not November 2000.", x=0.01, ha="left", fontsize=13.5, fontweight="bold")
fig.text(0.01, 0.01, "Sources: Yahoo (^NDX, ^SOX, ^NYA, sector SPDRs, ^VIX); FRED (DFF, DGS2, DGS10, T10Y2Y, BAA10Y, WTI, UNRATE, core CPI). 2026 rows use the latest monthly data (Oct, or Sep for CPI/jobs). Descriptive, n = 1.", fontsize=7.5, color="#555")
plt.savefig(O / "2000_vs_now.png", bbox_inches="tight"); print("ok")
