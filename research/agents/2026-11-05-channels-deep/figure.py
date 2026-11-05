"""Figures for P2/S1, X1, P3 (out/history_calendar.png) and P4 (out/deep_change_checklist.png). Reads the out/*.json files. Usage: python figure.py"""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"
INK, INK2, MUTED, GRID, SURF, BAND = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#fcfcfb", "#e9e8e3"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#b9b8b2"   # reference palette slots 1-2 + neutral
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})
hist, s1, x1, p4 = (json.load(open(O / f)) for f in ("history.json", "s1_threshold.json", "x1_depth.json", "p4.json"))
cls = lambda d: ORANGE if d <= -20 else BLUE if d <= -10 else GRAY
def head(ax, title, sub):
    ax.set_title(title, loc="left", fontsize=12.5, fontweight="bold", color=INK, pad=10 + 14.5 * (sub.count("\n") + 1))
    ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=9.3, color=INK2, va="bottom", ha="left", linespacing=1.35)
legend_cls = [Patch(color=GRAY, label="stopped above -10%"), Patch(color=BLUE, label="-10% to -20%"), Patch(color=ORANGE, label="-20% or worse (bear)")]
# ======================= figure 1: history + calendar =======================
fig, axs = plt.subplots(3, 1, figsize=(11, 17.5), gridspec_kw={"height_ratios": [1.35, 1.0, 0.85], "hspace": 0.42})
ax = axs[0]; ev = hist["P2 events (short z<=-1.75, long z>-1)"]; t = x1["today"]; sm = hist["P2 summary"]; br = s1["base rates (every 5th session since 1965)"]
rows = [(d, r["dd at event %"], r["max dd next 252 (from running peak) %"], r["complete (252 sessions observed)"]) for d, r in ev.items()]
rows.append((f"TODAY  (z {s1['today']['short z']})", t["depth %"], t["depth %"], None))
y = np.arange(len(rows))[::-1]
for yi, (d, dd0, mdd, comp) in zip(y, rows):
    if comp: ax.barh(yi, mdd, color=cls(mdd), height=0.64, zorder=2)
    else: ax.barh(yi, mdd, color=SURF, edgecolor=INK2 if comp is None else GRAY, hatch="////", height=0.64, linewidth=0.9, zorder=2)
    ax.plot([dd0, dd0], [yi - 0.36, yi + 0.36], color=INK, lw=2, zorder=3)
    note = "" if comp else ("  so far (window still open)" if comp is False else "  so far: today's fall")
    ax.text(mdd - 0.7, yi, f"{mdd:.0f}%{note}" if comp else f"{mdd:.0f}%", va="center", ha="right", fontsize=8.6, color=INK2)
    if not comp: ax.text(0.4, yi, note.strip(), va="center", ha="left", fontsize=8.6, color=INK2)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=9); ax.get_yticklabels()[-1].set_fontweight("bold")
ax.set_xlim(-38, 21); ax.set_ylim(-0.8, len(rows) - 0.3)
for v in (-10, -20): ax.axvline(v, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
ax.axvline(0, color=MUTED, lw=0.8); ax.set_xlabel("deepest fall from the running peak in the next 12 months (%)   ·   black tick = how far down it already was on the signal day")
ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
head(ax, "1 · Every time the S&P's 3-year channel broke while its 15-year channel held (1965-2026)",
     f"Finished cases: {sm['became >=10% correction']} of {sm['completed']} fell 10%+ within a year; {sm['became >=20% bear']} of {sm['completed']} ({100*sm['became >=20% bear']/sm['completed']:.0f}%) became 20%+ bears.\n"
     f"Compare any day 2.5-10% off its high: {100*br['those >=10%']:.0f}% fell 10%+, {100*br['those >=20%']:.0f}% became bears.  Today reads {s1['today']['short z']}σ vs the -1.75 rule (misses by a hair;\n"
     f"at -1.65 it qualifies and the finished cases read {s1['threshold -1.65']['>=10%']} of {s1['threshold -1.65']['completed']} and {s1['threshold -1.65']['>=20%']} of {s1['threshold -1.65']['completed']}).")
ax.legend(handles=legend_cls + [Line2D([], [], color=INK, lw=2, label="already down on the signal day")], loc="upper right", fontsize=8.6, frameon=False, ncol=1)
# ---- panel 2: X1
ax = axs[1]; E = pd.DataFrame(x1["episodes"]); E["t"] = pd.to_datetime(E.record); n = len(E)
k_stop, k_mid, k_bear = int((E["final depth %"] > -10).sum()), int(((E["final depth %"] <= -10) & (E["final depth %"] > -20)).sum()), int((E["final depth %"] <= -20).sum())
on = E[E.month.isin([10, 11])]; on_b, on_10 = int((on["final depth %"] <= -20).sum()), int((on["final depth %"] <= -10).sum())
ax.scatter(E.t, E["final depth %"], s=58, c=[cls(v) for v in E["final depth %"]], edgecolor=SURF, linewidth=1.4, zorder=3)
for _, r in E[E["final depth %"] <= -20].iterrows():
    ax.annotate(str(r.t.year), (r.t, r["final depth %"]), xytext=(0, -12), textcoords="offset points", ha="center", va="top", fontsize=8.4, color=INK2)
ax.scatter([pd.Timestamp(t["record date"])], [t["depth %"]], marker="D", s=80, color=INK, zorder=4)
ax.annotate(f"today {t['depth %']:.1f}% (still open)", (pd.Timestamp(t["record date"]), t["depth %"]), xytext=(4, 9), textcoords="offset points", ha="right", va="bottom", fontsize=8.6, color=INK, fontweight="bold")
for v in (-10, -20): ax.axhline(v, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
ax.set_ylim(-62, 0); ax.set_ylabel("where the decline bottomed (%)"); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
head(ax, f"2 · Every S&P decline from a record that reached today's -6% ({n} since 1950): where it ended",
     f"{k_stop} stopped above -10% ({100*k_stop/n:.0f}%) · {k_mid} ended between -10% and -20% ({100*k_mid/n:.0f}%) · {k_bear} became bears ({100*k_bear/n:.0f}%).\n"
     f"Records set in Oct-Nov: {len(on)} such declines, {on_10} reached -10%, {on_b} became bears (small n; no sign that late-year starts stay shallow).")
ax.legend(handles=legend_cls + [Line2D([], [], marker="D", color=INK, lw=0, ms=7, label="today")], loc="upper left", bbox_to_anchor=(0, -0.07), fontsize=8.6, frameon=False, ncol=4)
# ---- panel 3: P3
ax = axs[2]; b = hist["P3 bear markets (>=20% from a record close, pre-registered, 1928-)"]; L = pd.DataFrame(b["list"]); L["m"] = pd.to_datetime(L.peak).dt.month
cnt = L.m.value_counts().reindex(range(1, 13), fill_value=0); c = hist["P3 corrections (>=10% from a record close, pre-registered) by peak month"]
ax.axvspan(10.5, 12.5, color=BAND, zorder=0); ax.text(11.5, 2.75, "Nov-Dec", ha="center", fontsize=9, color=INK2)
ax.bar(cnt.index, cnt.values, width=0.62, color=ORANGE, zorder=2)
for m in range(1, 13):
    yrs = sorted(pd.to_datetime(L[L.m == m].peak).dt.year.tolist())
    if yrs: ax.text(m, cnt[m] + 0.08, "\n".join(map(str, yrs)), ha="center", va="bottom", fontsize=8.4, color=INK2, linespacing=1.15)
ax.axhline(len(L) / 12, color=INK2, lw=1.2, ls=(0, (4, 3))); ax.text(5.5, len(L) / 12 + 0.05, "chance: 1 a month", fontsize=8.6, color=INK2, va="bottom", ha="center")
ax.set_xticks(range(1, 13)); ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]); ax.set_xlim(0.3, 12.7)
ax.set_ylim(0, 3.4); ax.set_yticks([0, 1, 2, 3]); ax.set_ylabel("bear markets that began"); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
son, oth = c["Sep-Nov peaks: n / became >=20%"], c["other months: n / became >=20%"]
head(ax, f"3 · The month each bear market began ({len(L)} falls of 20%+ from a record, 1928-2026)",
     f"Nov-Dec: {b['peaks in Nov-Dec']} of {len(L)} ({100*b['share']:.0f}%) vs 17% by chance, so they are not rarer (one-sided p = {b['H-P3 binomial p (fewer than chance)']:.2f}). Jan-Jun: {b['peaks in Jan-Jun']} of {len(L)}.\n"
     f"10%+ declines from a record that began in Sep-Nov became bears {son[1]} of {son[0]}; other months {oth[1]} of {oth[0]} (p = {c['Fisher p']:.2f}).")
axs[2].text(0, -0.16, "S&P 500 closes (Yahoo ^GSPC). Pre-registered study 2026-11-05-channels-deep; panel 2 and the -1.65 check are exploratory additions, labelled as such in the README.",
         transform=axs[2].transAxes, fontsize=8, color=MUTED)
fig.savefig(O / "history_calendar.png", dpi=150, bbox_inches="tight"); plt.close(fig)
# ======================= figure 2: deep-change checklist =======================
I = p4["indicators"]; order = ["WTI oil y/y (%)", "Core CPI y/y (%)", "VIX / VIX3M", "2y - fed funds (pp)", "10y real yield, TIPS (%)", "10y - core CPI y/y (pp)", "Baa - 10y (pp)",
                                "Unemployment - 12-month low (pp)", "Shiller CAPE"]
names = {"WTI oil y/y (%)": "Oil (WTI), % vs a year earlier", "Core CPI y/y (%)": "Core inflation, % y/y", "VIX / VIX3M": "VIX ÷ 3-month VIX (21 sessions to the record)",
         "2y - fed funds (pp)": "2-year yield minus fed funds (hikes priced if > 0)", "10y real yield, TIPS (%)": "10-year real yield, TIPS (%)", "10y - core CPI y/y (pp)": "10-year yield minus core inflation (real-rate proxy)",
         "Baa - 10y (pp)": "Credit: Baa corporate minus 10-year (pp)", "Unemployment - 12-month low (pp)": "Unemployment minus its 12-month low (pp)", "Shiller CAPE": "Shiller CAPE (valuation)"}
lab = {"2000": "'00", "2007": "'07", "2020": "'20", "2022": "'22", "1999": "'99", "2015": "'15", "2018a": "Jan'18", "2018b": "Sep'18", "2025": "'25"}
fig, axs = plt.subplots(len(order), 1, figsize=(11, 2.05 * len(order) + 1.6), gridspec_kw={"hspace": 0.95})
def place(ax, pts, yv, color, below):
    pts = sorted([(v, k) for k, v in pts.items() if v is not None]); lo, hi = ax.get_xlim(); tol = 0.045 * (hi - lo); last = None; lvl = 0
    for v, k in pts:
        ax.scatter([v], [yv], s=62, color=color, edgecolor=SURF, linewidth=1.3, zorder=3)
        lvl = (lvl + 1) % 2 if last is not None and v - last < tol else 0; last = v
        off = (-9 - 9 * lvl) if below else (7 + 9 * lvl)
        ax.annotate(lab[k], (v, yv), xytext=(0, off), textcoords="offset points", ha="center", va="top" if below else "bottom", fontsize=8.2, color=INK2)
for ax, ind in zip(axs, order):
    r = I[ind]; q = r["distribution"]["p10/p33/p50/p67/p90"]; now, lat = r["now (month of the 2026 record)"], r["latest"]
    vals = [v for v in list(r["bear eves"].values()) + list(r["control eves (10-20% declines)"].values()) + [now, lat] + [q[0], q[4]] if v is not None]
    lo, hi = min(vals), max(vals); pad = 0.08 * (hi - lo); ax.set_xlim(lo - pad, hi + pad); ax.set_ylim(-1.9, 1.75)
    ax.add_patch(plt.Rectangle((q[0], -0.22), q[4] - q[0], 0.44, color=BAND, zorder=1, lw=0)); ax.plot([q[2], q[2]], [-0.22, 0.22], color=MUTED, lw=1.2, zorder=2)
    place(ax, r["bear eves"], 0.62, ORANGE, False); place(ax, r["control eves (10-20% declines)"], -0.62, BLUE, True)
    ax.scatter([now], [0], marker="D", s=78, color=INK, zorder=4)
    fb = "" if not r["now fallback month"] else f"   ·   black diamond = {pd.Timestamp(r['now fallback month'] + '-01').strftime('%b %Y')} (Oct not out yet)"
    if lat is not None and abs(lat - now) > 1e-9: ax.scatter([lat], [0], marker="D", s=70, facecolor=SURF, edgecolor=INK, linewidth=1.5, zorder=4)
    ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.tick_params(axis="x", labelsize=8.5)
    auc = r["AUC bear eves above controls (0.5 = no separation)"]; nb, nc = r["n bear / control"]
    sep = "bear eves ran higher than correction eves" if auc >= 0.7 else "bear eves ran lower than correction eves" if auc <= 0.3 else "bear eves and correction eves overlap"
    rh = [k for k, v in r["read vs each bear eve (same tercile of the 1999-2026 months = rhymes)"].items() if v == "rhymes"]
    ax.set_title(names[ind], loc="left", fontsize=10.5, fontweight="bold", color=INK, pad=19)
    ax.text(0, 1.03, f"{sep} (AUC {auc:.2f}, {nb} v {nc})   ·   today rhymes with: {', '.join(rh) if rh else 'none'}{fb}", transform=ax.transAxes,
            ha="left", va="bottom", fontsize=8.6, color=INK2)
axs[0].text(0, 1.98, "4 · Deep-change checklist: the macro at today's record vs the eve of 4 bear markets and of 5 declines that stopped short of 20%", transform=axs[0].transAxes,
            fontsize=12.5, fontweight="bold", color=INK, va="bottom")
axs[0].text(0, 1.5, "Eve = the month of the record close. Grey bar = middle 80% of all months 1999-2026, tick = median. 'Rhymes' = same third of that range. AUC = chance a bear eve reads\n"
            "higher than a correction eve (0.5 = no help). With 4 v 5 cases, read AUC as a hint only. Black diamond = Oct 2026 (record month), hollow diamond = latest print.",
            transform=axs[0].transAxes, fontsize=8.8, color=INK2, va="bottom", linespacing=1.35)
fig.legend(handles=[Line2D([], [], marker="o", color=ORANGE, lw=0, ms=8, label="eve of a bear market (2000, 2007, 2020, 2022)"),
                    Line2D([], [], marker="o", color=BLUE, lw=0, ms=8, label="eve of a 10-20% decline from a record (1999, 2015, Jan & Sep 2018, 2025)"),
                    Line2D([], [], marker="D", color=INK, lw=0, ms=8, label="today: Oct 2026, the record month"),
                    Line2D([], [], marker="D", markerfacecolor=SURF, markeredgecolor=INK, lw=0, ms=8, label="today: latest print")], loc="lower left", bbox_to_anchor=(0.11, 0.0), fontsize=8.8, frameon=False, ncol=1)
fig.text(0.62, 0.012, "FRED (BAA10Y, DGS2, DFF, DFII10, DGS10, UNRATE, core CPI, WTI); multpl (CAPE);\nYahoo (^VIX, ^VIX3M, CL=F). Latest prints Nov 3-5, 2026.", fontsize=8, color=MUTED)
fig.subplots_adjust(top=0.91, bottom=0.07)
fig.savefig(O / "deep_change_checklist.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("figures written")
