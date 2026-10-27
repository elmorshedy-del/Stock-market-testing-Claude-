"""Two figures: out/flow_mechanics.png (Part A) and out/trajectory.png (Part B).
Usage: python figure.py <ladder27 folder (data/DIX.csv)>"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
J = lambda f: json.loads((OUT / f).read_text())
A3, A4, A5, AS, B1, B2, B4, B5 = (J(f) for f in ("a3_mid.json", "a4.json", "a5.json", "a_summary.json", "b1.json", "b2.json", "b4.json", "b5.json"))
d = pd.read_csv(OUT / "a_daily.csv", parse_dates=["day"])
GREEN, RED, INK, MUTED, SURF, BLUE, ORANGE, GREY, PURPLE = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#eb6834", "#c9c8c3", "#7b5cd6"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
T = lambda ax, s: ax.set_title(s, loc="left", fontsize=9, color=INK)

# ---------------- Figure 1: mechanics
fig, ax = plt.subplots(2, 3, figsize=(19, 11), gridspec_kw={"hspace": 0.55, "wspace": 0.3})
es = d[d.sym == "ES"].sort_values("day"); ts = d[d.sym == "TSLA"].sort_values("day")
sm = pd.read_csv(Path(sys.argv[1]) / "data" / "DIX.csv", parse_dates=["date"]).set_index("date")
pct = sm.gex.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
a = ax[0, 0]; x = np.arange(len(es))
a.bar(x, es["ret %"], color=[GREEN if v > 0 else RED for v in es["ret %"]], width=0.6, label="ES open-to-close %")
a2 = a.twinx(); a2.plot(x, es["lambda (pts per 1k net)"], color=INK, lw=1.6, marker="o", ms=3, label="Kyle lambda (pts per 1k net contracts)")
g = pct.shift(1).reindex(es.day.values).to_numpy()
a2.plot(x, 4 * g, color=ORANGE, lw=1.2, ls="--", label="prior-day S&P dealer gamma pctile (x4)")
a2.set_ylabel("lambda / gamma pctile x4"); a2.spines["top"].set_visible(False)
a.set_xticks(x[::2], [t.strftime("%m-%d") for t in es.day][::2], fontsize=7.5); a.set_ylabel("ES open-to-close %")
h1, l1 = a.get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels(); a.legend(h1 + h2, l1 + l2, frameon=False, fontsize=7, loc="lower left")
s = AS["ES"]
T(a, f"A1 SPY (ES): moves are LIQUIDITY-led, not flow-led.\nDaily return vs net aggression: rho {s['Spearman(open-close return, delta % of volume)'][0]:+.2f} (p {s['Spearman(open-close return, delta % of volume)'][1]:.2f}).\n"
     f"Book got thinner: lambda {s['Kyle lambda first half / second half of window'][0]:.1f} -> {s['Kyle lambda first half / second half of window'][1]:.1f} as dealer gamma fell (rho {s['Spearman(prior-day S&P GEX pctile, Kyle lambda)'][0]:+.2f}, p {s['Spearman(prior-day S&P GEX pctile, Kyle lambda)'][1]:.2f})")
a = ax[0, 1]
a.scatter(ts["delta % of vol"], ts["ret %"], color=PURPLE, s=28)
for _, r in ts.iterrows():
    if abs(r["ret %"]) > 2.5 or abs(r["delta % of vol"]) > 11:
        a.text(r["delta % of vol"], r["ret %"] + 0.2, r.day.strftime("%m-%d"), fontsize=7, ha="center", color=MUTED)
a.axhline(0, color=INK, lw=0.6); a.axvline(0, color=INK, lw=0.6)
a.set_xlabel("TSLA net aggressive buying, % of Nasdaq volume"); a.set_ylabel("TSLA open-to-close %")
s = AS["TSLA"]
T(a, f"A1 TSLA: moves ARE flow-led. rho {s['Spearman(open-close return, delta % of volume)'][0]:+.2f} (p {s['Spearman(open-close return, delta % of volume)'][1]:.3f}, 26 days).\n"
     "Oct 16: -3.9% on -20% net selling. Oct 26: +2.0% on +12% net buying.\nWeekly net buying +3.5% since Oct 19: a driven rally")
a = ax[0, 2]
a.scatter(es["ret %"].abs(), es["hawkes n median"], color=BLUE, s=28, label="ES (16 days)")
a.scatter(ts["ret %"].abs(), ts["hawkes n median"], color=PURPLE, s=28, label="TSLA (26 days)")
a.axhline(1, color=RED, lw=0.8, ls=":"); a.text(0.02, 0.985, "n = 1: critical (runaway cascades)", fontsize=7.5, color=RED, transform=a.get_yaxis_transform())
a.set_ylim(0.45, 1.02); a.set_xlabel("|open-to-close return| %"); a.set_ylabel("Hawkes branching ratio n (median of 30-min fits)")
a.legend(frameon=False, fontsize=7.5, loc="center right")
T(a, "A2 Reflexivity: ~55-63% of market orders are triggered by earlier orders,\nbut the market is SUBCRITICAL (n well below 1) and big days are NOT\nmore self-exciting (ES rho -0.32): big moves need an outside push")
a = ax[1, 0]
for sym, col in (("ES", BLUE), ("TSLA", PURPLE)):
    z = A3[sym]; L = np.array(z["lags"]); C = np.array(z["C"])
    m = C > 0; a.loglog(L[m], C[m], "o-", color=col, ms=3, lw=1, label=f"{sym} sign memory C(lag), gamma {z['gamma (sign memory, C ~ lag^-gamma)']:.2f}")
    Ge = np.array(z["G_ell"]); G = np.array(z["G"]); mg = G > 0
    a.loglog(Ge[mg], G[mg], "s--", color=col, ms=3, lw=1, alpha=0.7, label=f"{sym} impact kernel G(lag), beta {z['beta (impact decay, G ~ lag^-beta)']:.2f} vs (1-gamma)/2 = {z['(1-gamma)/2 (diffusive-price prediction)']:.2f}")
a.set_xlabel("lag (market orders)"); a.legend(frameon=False, fontsize=7, loc="lower left")
T(a, "A3 Propagator physics: big orders are split (signs remember for 1,000 orders);\nimpact must decay as lag^-(1-gamma)/2 for prices to stay random.\nTSLA obeys it (0.06 vs 0.13); ES, a large-tick market, decays slower (0.17 vs 0.32)")
a = ax[1, 1]
r5 = pd.read_csv(OUT / "a5_rows.csv")
for sym, x5 in r5.groupby("sym"):
    a.scatter(x5["imb % of day $vol"].clip(-3, 3), x5["ret 15:50-close %"].clip(-1, 1), s=14, alpha=0.75, label=sym, color=(RED if sym == "SPY" else None))
a.axhline(0, color=INK, lw=0.6); a.axvline(0, color=INK, lw=0.6)
a.set_xlabel("closing-auction imbalance at 15:50, % of day's $ volume (buy +)"); a.set_ylabel("15:50 -> close %")
a.legend(frameon=False, fontsize=6.5, ncol=2, loc="upper left")
T(a, f"A5 The close: the 15:50 imbalance pushes the last 10 minutes.\nrho {A5['Spearman rho (pooled)']:+.2f} (p < 0.001, {A5['symbol-days']} symbol-days, PASSES); biggest fifth of imbalances:\n"
     f"close moved WITH the imbalance {100*A5['largest-fifth imbalances: share where close moved WITH the imbalance']:.0f}% of the time")
a = ax[1, 2]
rows = [r for r in A4["per day"] if r.get("buy/min ratio (final 0.1% vs earlier run)") not in (None,) and str(r.get("note")) in ("None", "nan")]
for i, r in enumerate(rows):
    e0, f0 = r["delta/min earlier, final"]
    a.plot([0, 1], [e0, f0], "-o", color=ORANGE if r["flip day"] else GREY, lw=1.5 if r["flip day"] else 1, ms=3)
    a.text(1.03, f0, r["day"][4:6] + "-" + r["day"][6:], fontsize=6.5, va="center", color=ORANGE if r["flip day"] else MUTED)
a.set_xticks([0, 1], ["prior 30 min of the run", "final 0.1% into the high"]); a.set_xlim(-0.2, 1.3)
a.set_ylabel("net aggressive buying, contracts per minute")
mb = A4["MBO Oct 20"]
T(a, "A4 Highs are made on a BUYING BURST (net buying jumps into the high),\non flip days (orange) and others alike: not quiet exhaustion. Oct 20 book:\n"
     f"{mb['at the high (price and 1 tick above)']['net new offers/min']:.1f} net new offers/min at the high vs {mb['placebo: 10 other 5-min swing highs that day, median net new offers/min']:.1f} at other highs (sellers layered)")
fig.savefig(OUT / "flow_mechanics.png", dpi=140, bbox_inches="tight", facecolor=SURF)

# ---------------- Figure 2: trajectory and entry
fig, ax = plt.subplots(2, 2, figsize=(16, 11), gridspec_kw={"hspace": 0.5, "wspace": 0.25})
fans = pd.read_csv(OUT / "b2_fans.csv")
for k, (sym, S0, lv, H) in enumerate((("SPY", 769.72, [(750, "put wall 750", RED), (770.3, "pre-open flip ~770", ORANGE), (780, "780 magnet / ~S&P high", GREEN), (800, "800 call wall", GREEN)], 20),
                                      ("TSLA", 407.46, [(389, "389 old triple top", RED), (400, "400 floor (call wall)", ORANGE), (420, "420 magnet", GREEN), (450, "450 (Barclays target)", GREEN)], 10))):
    a = ax[0, k]; f = fans[fans.asset == ("SPX" if sym == "SPY" else "TSLA")]
    h = f.h.to_numpy()
    a.fill_between(h, S0 * (1 + f.q5), S0 * (1 + f.q95), color=BLUE, alpha=0.12, label="real-world analogs: 5-95%")
    a.fill_between(h, S0 * (1 + f.q25), S0 * (1 + f.q75), color=BLUE, alpha=0.25, label="analogs: 25-75%")
    a.plot(h, S0 * (1 + f.q50), color=BLUE, lw=1.8, label="analogs: median")
    a.plot(h, S0 * (1 + f.all_q50), color=MUTED, lw=1, ls=":", label="all days: median")
    for exp, tdays in (("2026-10-30", 3), ("2026-11-06", 8), ("2026-11-20", 18)):
        if tdays > H: continue
        qd = B1[sym][exp]["quantiles"]
        a.errorbar([tdays], [qd["q50"]], yerr=[[qd["q50"] - qd["q05"]], [qd["q95"] - qd["q50"]]], fmt="D", color=PURPLE, capsize=4, ms=5, lw=1.2)
        a.errorbar([tdays], [qd["q50"]], yerr=[[qd["q50"] - qd["q25"]], [qd["q75"] - qd["q50"]]], fmt="none", color=PURPLE, capsize=0, lw=4, alpha=0.5)
    a.plot([], [], "D", color=PURPLE, label="options-implied (Oct 30, Nov 6, Nov 20): 5-25-50-75-95%")
    for y, lab, c in lv:
        a.axhline(y, color=c, lw=0.8, ls="--"); a.text(H + 0.2, y, " " + lab, fontsize=7.5, color=c, va="center")
    a.set_xlim(0, H + 5.5); a.set_xlabel("sessions ahead (from the Oct 27 close)"); a.set_ylabel(f"{sym}")
    a.legend(frameon=False, fontsize=7, loc="lower left")
b2s = B2["SPX analog (R2 within 10 sessions, within 2% of 52w high, VIX 15-20)"]; b2t = B2["TSLA analog (freed, >5% above own flip), 2021-Oct 14 2026"]
T(ax[0, 0], f"SPY trajectory. Today's state (low gamma near highs, VIX 15-20; {b2s['episodes (gap>10)']} past episodes):\nmedian +{b2s['fwd median % at 1/3/5/10/20d'][3]:.1f}% in 10d, +{b2s['fwd median % at 1/3/5/10/20d'][4]:.1f}% in 20d, WEAKER than all days (+0.7/+1.5) with a fatter\n"
     f"left tail; P(+3% before -3%) {100*b2s['P(+3% before -3%, closes, within 60d)'][0]:.0f}% vs {100*b2s['P(+3% before -3%), all days'][0]:.0f}% all days. Options: 50% band 762-784 by Nov 6")
T(ax[0, 1], f"TSLA trajectory. Freed and >5% above its flip ({b2t['episodes (gap>10)']} episodes): median {b2t['fwd median % at 1/3/5/10d'][3]:+.1f}% in 10d\n"
     f"(all days +0.2%); touches +10% {100*b2t['P(close >= +10% at any point within 10d)']:.0f}% vs {100*b2t['same, all days ']:.0f}%, -5% {100*b2t['P(close <= -5% at any point within 10d)']:.0f}% vs {100*b2t['same, all days']:.0f}%.\n"
     f"Options: P(below 400 on Nov 6) {100*B1['TSLA']['2026-11-06']['P(below level)']['400']:.0f}%, below 389 {100*B1['TSLA']['2026-11-06']['P(below level)']['389']:.0f}%")
a = ax[1, 0]
for key, col, lab in (("SPX, sigma = VIX (pre-registered)", RED, "SPX, sigma = VIX"), ("SPX, sigma = 20d realized vol (post hoc comparison)", ORANGE, "SPX, sigma = realized vol"),
                      ("TSLA, sigma = own 30d ATM IV (TSLA-sized levels, added)", PURPLE, "TSLA, sigma = own IV")):
    v = B4[key]; pr = [x["mean predicted"] for x in v.values()]; rl = [x["realized"] for x in v.values()]
    a.scatter(pr, rl, color=col, s=36, label=lab)
a.plot([0, 1], [0, 1], color=INK, lw=0.8, ls=":"); a.set_xlim(0, 1); a.set_ylim(0, 1)
a.set_xlabel("predicted P(touch a pullback level) - reflection principle"); a.set_ylabel("what happened")
a.legend(frameon=False, fontsize=8, loc="upper left")
T(a, "B4 The elegant first-passage formula FAILS its pre-registered test for SPX:\nwith VIX it overstates pullback odds by ~1.5x (options carry a risk premium);\nTSLA's own IV is about right on average. Use the analog odds, not the formula")
a = ax[1, 1]; a.axis("off")
nb = B2["B3 November S&P (Yahoo monthly; years available)"]
txt = (f"B3  November, S&P {nb['first year']}-2025 ({nb['years']} years): mean +{nb['mean %']:.1f}%, up {100*nb['share up']:.0f}% of years, the best month;\n"
       f"      Octobers ending within 3% of the high: +{nb['Oct close within 3% of 12m high: years / mean % / share up'][1]:.1f}%, up {100*nb['Oct close within 3% of 12m high: years / mean % / share up'][2]:.0f}%.\n\n"
       f"B5  'Lasting burst' confirmation (close above the pre-open flip + gamma not pinned): FAILS.\n"
       f"      Confirmed vs other near-high days: next 10d {B5['fwd 10d %: confirmed / not'][0]:+.2f}% vs {B5['fwd 10d %: confirmed / not'][1]:+.2f}% (p {B5['p (shift null)']:.2f}); new high before -3%:\n"
       f"      {100*B5['P(new 20d high before -3%): confirmed / not'][0]:.0f}% vs {100*B5['P(new 20d high before -3%): confirmed / not'][1]:.0f}% (p {B5['p (shift null) ']:.2f}). There is NO tested trigger that 'confirms' a burst.\n\n"
       "WHAT IS TESTED AND USABLE FOR AN ENTRY\n"
       "  - Ladder R2 (fired Oct 20): up-leg odds 64-78% within 20 sessions, but in today's near-high subset the\n"
       "    distribution is two-sided: favour defined-risk (call spreads beat naked calls in the ladder test).\n"
       "  - The flip as a FLOOR from above (flip-wicks H1): lows stop there 45% vs 36%, closes hold 67% vs 62%.\n"
       "    A dip to a flip SPY has closed above is the tested place to buy; it is support, not a trend signal.\n"
       "  - Pullback odds come from the analogs: SPY -2% touch within 10 sessions ~28%; TSLA -5% ~47%.\n"
       "  - Execution: read the 15:50 closing imbalance before any late-day order (A5).")
a.text(0, 1, txt, va="top", fontsize=8.6, color=INK, family="DejaVu Sans")
fig.savefig(OUT / "trajectory.png", dpi=140, bbox_inches="tight", facecolor=SURF)
