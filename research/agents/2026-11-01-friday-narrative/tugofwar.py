"""out/tug_of_war.png: why price fell while buyers traded more often. Friday 10:30-14:52 ES minutes split into
sell-dominated vs buy-dominated, vs the 5 prior days; plus a thin-bid / thick-ask cartoon. Usage: python tugofwar.py <db dir>"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"; DB = Path(sys.argv[1]); ET = "America/New_York"
GREEN, RED, INK, MUTED, SURF, BLUE, GREY = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#c9c8c3"
plt.rcParams.update({"font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.parse_math": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})


def mins(day):
    d = pd.read_parquet(DB / f"ES_trades_{day}.parquet"); d = d[d.action == "T"]; d.index = d.index.tz_convert(ET); sz = d["size"].astype("int64")
    m = pd.DataFrame({"buy": sz.where(d.side == "B", 0).resample("1min").sum(), "sell": sz.where(d.side == "A", 0).resample("1min").sum(), "px": d.price.resample("1min").last()}).between_time("09:30", "15:59")
    m["px"] = m.px.ffill(); m["chg"] = m.px.diff(); m["net"] = m.buy - m.sell
    return m.dropna().between_time("10:30", "14:52")


days = ["2026-10-23", "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"]
F = mins("2026-10-30"); B = [mins(d) for d in days]
stats = {}
for lab, g in [("Fri", F)] + list(zip(days, B)):
    ns, nb = g[g.net < 0], g[g.net > 0]
    X = np.c_[np.ones(len(g)), g.buy / 1000, g.sell / 1000]; b = np.linalg.lstsq(X, g.chg, rcond=None)[0]
    stats[lab] = {"sell-min n": len(ns), "sell-min pts": round(float(ns.chg.sum()), 1), "sell-min avg": round(float(ns.chg.mean()), 2),
                  "buy-min n": len(nb), "buy-min pts": round(float(nb.chg.sum()), 1), "buy-min avg": round(float(nb.chg.mean()), 2), "total": round(float(g.chg.sum()), 1),
                  "impact/1k buys": round(float(b[1]), 2), "impact/1k sells": round(float(b[2]), 2), "drift pts/min": round(float(b[0]), 3)}
json.dump(stats, open(OUT / "tug_of_war.json", "w"), indent=1)

fig = plt.figure(figsize=(18, 11)); gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1], hspace=0.38, wspace=0.2)
# 1: tug of war cumulative
a = fig.add_subplot(gs[0, :]); x = (F.index.hour - 9.5) + F.index.minute / 60
sell_path = F.chg.where(F.net < 0, 0).cumsum(); buy_path = F.chg.where(F.net > 0, 0).cumsum(); tot = F.chg.cumsum()
a.plot(x, sell_path, color=RED, lw=2.4, label=f"points moved in SELL-dominated minutes ({stats['Fri']['sell-min n']} minutes)")
a.plot(x, buy_path, color=GREEN, lw=2.4, label=f"points moved in BUY-dominated minutes ({stats['Fri']['buy-min n']} minutes)")
a.plot(x, tot, color=INK, lw=2.8, label="actual price change (the sum)")
a.axhline(0, color=MUTED, lw=0.6); a.set_ylabel("ES points, cumulative from 10:30")
for y, t, c in ((sell_path.iloc[-1], f"{sell_path.iloc[-1]:+.0f}", RED), (buy_path.iloc[-1], f"{buy_path.iloc[-1]:+.0f}", GREEN), (tot.iloc[-1], f"{tot.iloc[-1]:+.0f}", INK)):
    a.text(x[-1] + 0.03, y, t, color=c, fontsize=13, weight="bold", va="center")
a.legend(frameon=False, loc="lower left", fontsize=11)
a.set_xticks([1, 2, 3, 4, 5]); a.set_xticklabels(["10:30", "11:30", "12:30", "13:30", "14:30"]); a.set_xlim(0.95, 5.55)
a.set_title("A tug of war: buyers won MORE minutes, sellers won BIGGER minutes (Friday 10:30-14:52, ES futures)", loc="left", fontsize=14, weight="bold", color=INK)
# 2: per-minute size Fri vs normal
b = fig.add_subplot(gs[1, 0])
nb_avg = np.mean([stats[d]["buy-min avg"] for d in days]); ns_avg = np.mean([stats[d]["sell-min avg"] for d in days])
nbn = np.mean([stats[d]["buy-min n"] for d in days]); nsn = np.mean([stats[d]["sell-min n"] for d in days])
xs = np.arange(2); w = 0.35
b.bar(xs - w / 2, [ns_avg, nb_avg], w, color=[RED, GREEN], alpha=0.35, label="normal day (avg of Oct 23-29)")
b.bar(xs + w / 2, [stats["Fri"]["sell-min avg"], stats["Fri"]["buy-min avg"]], w, color=[RED, GREEN], label="Friday")
for i, (v0, v1, n0, n1) in enumerate(((ns_avg, stats["Fri"]["sell-min avg"], nsn, stats["Fri"]["sell-min n"]), (nb_avg, stats["Fri"]["buy-min avg"], nbn, stats["Fri"]["buy-min n"]))):
    b.text(i - w / 2, v0 + (0.08 if v0 > 0 else -0.08), f"{v0:+.2f}\n({n0:.0f} min)", ha="center", va="bottom" if v0 > 0 else "top", fontsize=10, color=MUTED)
    b.text(i + w / 2, v1 + (0.08 if v1 > 0 else -0.08), f"{v1:+.2f}\n({n1} min)", ha="center", va="bottom" if v1 > 0 else "top", fontsize=10.5, color=INK, weight="bold")
b.axhline(0, color=MUTED, lw=0.6); b.set_xticks(xs); b.set_xticklabels(["a SELL-dominated minute", "a BUY-dominated minute"]); b.set_ylim(-2.8, 1.6)
b.set_ylabel("average ES points moved per minute"); b.legend(frameon=False, loc="lower right", fontsize=9.5)
b.set_title("Friday: sell minutes hit twice as hard, buy minutes half as hard", loc="left", fontsize=12.5, weight="bold", color=INK)
# 3: cartoon thin bids / thick asks
c = fig.add_subplot(gs[1, 1]); c.axis("off"); c.set_xlim(0, 20); c.set_ylim(-1, 11)
lv = np.arange(9, 0, -1)
asks = {9: 6, 8: 6, 7: 7, 6: 7}; bids = {5: 1.5, 4: 1.5, 3: 1.5, 2: 1.5, 1: 1.5}
for L in lv:
    y = L; c.text(0.3, y, f"level {L}", fontsize=9, color=MUTED, va="center")
    if L in asks: c.add_patch(plt.Rectangle((2.5, y - 0.35), asks[L] * 0.7, 0.7, color=RED, alpha=0.75))
    if L in bids: c.add_patch(plt.Rectangle((2.5, y - 0.35), bids[L] * 0.7, 0.7, color=GREEN, alpha=0.75))
c.annotate("", xy=(2.5, 6), xytext=(10, 6), arrowprops=dict(arrowstyle="->", color=GREEN, lw=2.5))
c.text(10.2, 6.5, "BUY 10: eats part of ONE thick\nsell wall → price up 0 to 1 level", fontsize=10, color=INK, va="center")
c.annotate("", xy=(2.5, 5), xytext=(10, 5), arrowprops=dict(arrowstyle="->", color=RED, lw=2.5))
c.text(10.2, 4.6, "SELL 10: wipes out several THIN\nbid levels → price down 3-4 levels", fontsize=10, color=INK, va="center")
c.text(0.3, -0.5, "red = resting sell orders (asks), thick: sellers waiting above\ngreen = resting buy orders (bids), thin: buyers pulled back below\nSame size order, very different push. More buy orders can still lose.", fontsize=10, color=INK, va="top")
c.set_title("Why: thick sellers waiting above, thin buyers below", loc="left", fontsize=12.5, weight="bold", color=INK)
fig.suptitle("You were right: market SELLS into thin bids did the damage. They just came in fewer, sharper bursts", x=0.01, ha="left", fontsize=16, weight="bold", color=INK)
fig.savefig(OUT / "tug_of_war.png", dpi=115, bbox_inches="tight"); print(json.dumps(stats["Fri"]))
