"""out/live_read_1030.png: Friday Oct 30 (month-end, heavy expiry) and Monday Nov 2 gamma profiles for SPY and TSLA,
Oct 29 intraday paths, breadth, TSLA skew/IV, and the S&P calendar base rates for the window ahead.
Usage: python figure.py <live29/y>"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
M, C, X = (json.loads((OUT / f).read_text()) for f in ("maps.json", "curves.json", "context.json"))
SK = pd.read_csv(OUT / "tsla_skew_recent.csv", parse_dates=["date"])
y = Path(sys.argv[1])
GREEN, RED, INK, MUTED, SURF, BLUE, ORANGE, GREY = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#eb6834", "#c9c8c3"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})


def bars(sym):
    r = json.loads((y / f"{sym}_1m.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    b = pd.DataFrame({k: q[k] for k in ("high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna()
    b = b[b.index.date == pd.Timestamp("2026-10-29").date()]
    return b[(b.index.strftime("%H:%M") >= "09:30") & (b.index.strftime("%H:%M") <= "20:00")]


fig = plt.figure(figsize=(18, 15)); gs = fig.add_gridspec(3, 3, hspace=0.55, wspace=0.25)
LV = {"SPY": dict(close=769.36, ah=764.73, implied=762.0, flipF=M["SPY"]["Friday Oct 30 (incl. the expiry) @ close Oct 29 769.36"]["flip"],
                  flipM=M["SPY"]["Monday Nov 2 (after the expiry) @ close Oct 29 769.36"]["flip"], cw=800, pw=750),
      "TSLA": dict(close=403.30, ah=397.45, implied=None, flipF=M["TSLA"]["Friday Oct 30 (incl. the expiry) @ close Oct 29 403.3"]["flip"],
                   flipM=M["TSLA"]["Monday Nov 2 (after the expiry) @ close Oct 29 403.3"]["flip"], cw=400, pw=350)}
for row, sym in enumerate(("SPY", "TSLA")):
    L = LV[sym]
    # left: Oct 29 path with levels
    a = fig.add_subplot(gs[row, 0]); b = bars(sym); x = (b.index.hour - 9.5) + b.index.minute / 60
    a.fill_between(x, b.low, b.high, color=GREY, lw=0); a.plot(x, b.close, color=INK, lw=1)
    a.axvspan(6.5, 10.5, color=BLUE, alpha=0.06); a.text(6.6, b.high.max(), "after hours", fontsize=7.5, color=BLUE, va="top")
    lv = [(L["flipF"], f"Friday flip {L['flipF']:.1f}", ORANGE)] + ([(765, "765 biggest − strike", RED), (760, "760", RED)] if sym == "SPY" else [(400, "400 call wall / biggest + strike", GREEN), (395, "395", MUTED), (389, "389 old triple top", MUTED)])
    for yv, lab, c in lv:
        if b.low.min() - 3 < yv < b.high.max() + 3:
            a.axhline(yv, color=c, lw=1, ls="--"); a.text(0.01, yv, lab, fontsize=7.5, color=c, va="bottom", transform=a.get_yaxis_transform())
    if L["implied"]:
        a.scatter([10.5], [L["implied"]], color=RED, zorder=5, s=25); a.annotate(f"ES-implied ~{L['implied']:.0f}\n(00:11 ET, ES −0.96%)", (10.5, L["implied"]), fontsize=7.5, color=RED, ha="right", xytext=(-6, -2), textcoords="offset points")
    a.set_xticks([0, 2, 4, 6.5, 8.5, 10.5]); a.set_xticklabels(["9:30", "11:30", "13:30", "16:00", "18:00", "20:00"])
    a.set_title(f"{sym} Thursday Oct 29: close {L['close']}, after hours {L['ah']}", loc="left", fontsize=10, color=INK)
    # middle: total-gamma profile, Friday vs Monday
    a = fig.add_subplot(gs[row, 1])
    for key, lab, c, ls in ((f"{sym} | Friday Oct 30 (incl. the expiry) | close Oct 29", "Friday (incl. Oct 30 expiry)", INK, "-"),
                            (f"{sym} | Monday Nov 2 (after the expiry) | close Oct 29", "Monday Nov 2 (expiry gone)", BLUE, "--")):
        cv = C[key]; a.plot(cv["price"], cv["total gamma $bn"], color=c, ls=ls, lw=1.6, label=lab)
    a.axhline(0, color=MUTED, lw=0.6)
    a.axvline(L["flipF"], color=ORANGE, lw=1, ls=":"); a.text(L["flipF"], a.get_ylim()[1] * (0.6 if sym == "TSLA" else 1), f" flip {L['flipF']:.1f}", color=ORANGE, fontsize=7.5, va="top")
    for v, lab, c in ((L["close"], "close", INK), (L["ah"], "after hrs", RED)):
        a.axvline(v, color=c, lw=0.8, alpha=0.6); a.text(v, a.get_ylim()[0], f" {lab}", rotation=90, fontsize=7, color=c, va="bottom")
    if sym == "SPY":
        z = M["SPY"]["Friday Oct 30 (incl. the expiry) @ close Oct 29 769.36"]["most negative total-gamma price (pocket centre)"]
        a.axvspan(742, 765, color=RED, alpha=0.07); a.text(753.5, a.get_ylim()[0] * 0.92, "pocket\n742–765", ha="center", fontsize=7.5, color=RED)
    a.set_xlabel(f"{sym} price"); a.set_ylabel("dealer gamma, $bn per 1% move"); a.legend(fontsize=7.5, frameon=False, loc="upper left")
    share = M[sym]["Oct 30 expiry share of |gamma|"]
    a.set_title(f"{sym} dealer gamma by price (Oct 28 OI): Oct 30 holds {share:.0%}", loc="left", fontsize=10, color=INK)

# right column top: breadth
a = fig.add_subplot(gs[0, 2]); B = X["breadth"]; v = B["% above 50-day, last 15 sessions"]
a.plot(range(len(v)), v, color=GREEN, marker="o", ms=3); a.axhline(63, color=MUTED, lw=0.8, ls=":"); a.text(0, 63.5, "normal near a high: 63%", fontsize=7.5, color=MUTED)
a.set_xticks([0, len(v) - 1]); a.set_xticklabels(["Oct 9", "Oct 29"]); a.set_ylabel("% of 81 large caps above 50-day")
a.set_title(f"Breadth broadening: {B['share up today']:.0%} up Thursday while S&P −0.3%\nequal-weight beat S&P by {B['equal-weight 83 vs S&P, last 20 sessions, pts']:+.1f} pts in 20 sessions", loc="left", fontsize=10, color=INK)
# right column middle: TSLA skew and IV
a = fig.add_subplot(gs[1, 2]); a2 = a.twinx()
a.plot(SK.date, SK.rr25 * 100, color=ORANGE, lw=1.5, label="25-delta risk reversal (call − put IV), pts")
a2.plot(SK.date, SK.atm_iv * 100, color=BLUE, lw=1.5, label="30-day ATM IV, %"); a2.spines["right"].set_visible(True)
a.set_ylabel("risk reversal, pts", color=ORANGE); a2.set_ylabel("ATM IV %", color=BLUE)
a.xaxis.set_major_locator(matplotlib.dates.DayLocator(bymonthday=[1, 8, 15, 22, 29])); a.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d")); a.tick_params(axis="x", rotation=0); h1, l1 = a.get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels(); a.legend(h1 + h2, l1 + l2, fontsize=7, frameon=False, loc="lower left")
a.set_title("TSLA options: ATM IV at a 1-year low (37%);\ncall skew richening since Oct 23 but still below its Oct 14 level", loc="left", fontsize=10, color=INK)
# bottom: calendar base rates
a = fig.add_subplot(gs[2, :]); cal = X["calendar"]; mt = X["midterm conditioning"]["years with Oct close within 5% of 52w high"]
rows = [("Last trading day of Oct\n1950–2025", cal["1950-2025"]["last trading day of October"]),
        ("Last day of Oct\n2020–25 (n 6)", cal["2020-2025"]["last trading day of October"]),
        ("First 3 days of Nov\n1950–2025", cal["1950-2025"]["first 3 trading days of November (sum)"]),
        ("Midterm election week\n(n 19)", cal["election week"]["midterm (close before election day -> Friday after)"]),
        ("Presidential election week\n(n 19)", cal["election week"]["presidential (close before election day -> Friday after)"]),
        ("November, all years\n1950–2025", cal["1950-2025"]["November month (sum of daily %)"]),
        ("November,\nmidterm years (n 19)", cal["midterm years"]["November month %"]),
        ("Nov, midterm years\nnear a high (n 9)", {"mean %": mt["Nov mean %"], "% up": 66.7}),
        ("Any 4-day turn of month\n1950–2025", cal["1950-2025"]["turn of month (last day + first 3), all months, sum"])]
xs = range(len(rows)); vals = [r[1]["mean %"] for r in rows]
a.bar(xs, vals, color=[GREEN if v > 0 else RED for v in vals], width=0.6)
for i, (lab, r) in enumerate(rows):
    a.text(i, vals[i] + (0.08 if vals[i] >= 0 else -0.08), f"{vals[i]:+.2f}%\n{r['% up']:.0f}% up", ha="center", va="bottom" if vals[i] >= 0 else "top", fontsize=8, color=INK)
a.set_xticks(list(xs)); a.set_xticklabels([r[0] for r in rows], fontsize=8); a.axhline(0, color=MUTED, lw=0.6); a.set_ylabel("S&P 500 mean return, %")
a.set_ylim(min(vals) - 0.8, max(vals) + 0.9)
a.set_title("S&P 500 base rates for the window ahead (descriptive, price index; not tests)", loc="left", fontsize=10, color=INK)
fig.suptitle("SPY and TSLA into month-end, the Oct 30 expiry, November and the Nov 3 midterms (data to 00:11 ET Fri Oct 30)", x=0.01, ha="left", fontsize=13, color=INK)
fig.savefig(OUT / "live_read_1030.png", dpi=130, bbox_inches="tight")
print("ok")
