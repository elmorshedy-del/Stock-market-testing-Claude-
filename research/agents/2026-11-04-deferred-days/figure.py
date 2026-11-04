"""Deferred-days figure: (a) ES Oct 27 last hour, price + cumulative net aggression; (b) 15:50 closing imbalances; (c) TSLA gap-ups first 5 min vs next 55 min with Oct 26-28.
Usage: python figure.py -> out/deferred_days.png"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"; GT = HERE.parent / "2026-10-28-gap-teardown"
sys.path.insert(0, str(HERE.parent / "2026-10-27-flow-physics")); from flowlib import load_trades   # noqa: E402
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE, RED, GREEN = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834", "#c8372d", "#2f8f5b"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRAY, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.titleweight": "bold", "axes.titlesize": 11})
d4, g1 = json.load(open(HERE / "out" / "d4.json")), json.load(open(HERE / "out" / "g1.json"))
fig, ax = plt.subplots(1, 3, figsize=(17, 5.6), facecolor=BG, gridspec_kw={"width_ratios": [1.2, 1, 1]})
for a in ax: a.set_facecolor(BG); a.grid(True, color=GRID, lw=0.8); a.spines[["top", "right"]].set_visible(False)
x = load_trades(D / "ES_trades_20261027.parquet").set_index("ts_event"); x.index = x.index.tz_convert("America/New_York")
x = x.between_time("15:00", "15:59:59"); px = x.price.resample("30s").last().ffill(); cd = (x["size"] * x.sign).resample("30s").sum().cumsum()
a = ax[0]; a.plot(px.index, px.values, color=INK, lw=1.8); a.set_ylabel("ES (Dec) price")
b = a.twinx(); b.plot(cd.index, cd.values / 1e3, color=BLUE, lw=1.6); b.set_ylabel("cumulative net aggressive buying since 15:00 (k contracts)", color=BLUE); b.spines[["top"]].set_visible(False)
for t, lab, col, y, ha in [("15:45:23", "day high 7772.75 \n(buyers still buying:\nnot exhaustion) ", GREEN, px.max() - 0.3, "right"), ("15:50:00", " 15:50 imbalances\n published:\n mega-cap SELLS", RED, px.min() + 0.5, "left")]:
    tt = pd.Timestamp(f"2026-10-27 {t}", tz="America/New_York"); a.axvline(tt, color=col, lw=1.2, ls="--"); a.text(tt, y, lab, color=col, fontsize=8.5, va="top" if ha == "right" else "bottom", ha=ha)
a.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%H:%M", tz="America/New_York"))
a.set_title("(a) Oct 27 'the 15:50 drop': ES buying ran into the high,\nthen sellers hit from 15:50 (−13 pts to the close)", loc="left")
a = ax[1]; rows = pd.DataFrame(d4["A5 Oct 27 rows"]).sort_values("imb % of day $vol")
cols = [RED if v < 0 else GREEN for v in rows["imb % of day $vol"]]
a.barh(rows.sym, rows["imb % of day $vol"], color=cols, alpha=0.85, label="15:50 imbalance, % of day's $ volume")
a2 = a.twiny(); a2.scatter(rows["ret 15:50-close %"], rows.sym, color=INK, zorder=5, s=28, label="15:50→close return %"); a2.set_xlabel("15:50 → close return % (black dots)")
a.axvline(0, color=INK2, lw=1); a.set_xlabel("closing imbalance at 15:50, % of the day's dollar volume (bars)")
net = sum(r["imb $m"] for r in d4["A5 Oct 27 rows"])
a.set_title(f"(b) Net ≈ ${net / 1e3:+.2f}bn of closing SELL imbalance across 10 names;\nall 10 fell into the close", loc="left", pad=30)
a = ax[2]; fe = pd.read_csv(GT / "out" / "features.csv", parse_dates=["date"]); ts = fe[(fe.sym == "TSLA") & (fe.date < "2026-10-26")]
for c, col, lab in (("mid", GRAY, "other TSLA gap-ups"), ("VF", RED, "fade days (VF)"), ("SC", GREEN, "continuation days (SC)")):
    z = ts[ts.cls == c]; a.scatter(z["ret 09:30->09:35 (sig)"], z["ret 09:35->10:30 (sig)"], s=16, color=col, alpha=0.6, label=lab)
for lab, col in (("Oct 26", GREEN), ("Oct 27", BLUE), ("Oct 28", RED)):
    vx, vy = g1[lab]["ret 09:30->09:35 (sig)"]["value"], g1[lab]["ret 09:35->10:30 (sig)"]["value"]
    a.scatter([vx], [vy], s=140, color=col, edgecolor=INK, zorder=6, marker="*"); a.annotate(lab, (vx, vy), xytext=(6, 6), textcoords="offset points", fontsize=9, fontweight="bold", color=col)
a.axhline(0, color=INK2, lw=0.8); a.axvline(0, color=INK2, lw=0.8); a.axvline(-0.25, color=ORANGE, lw=1, ls=":"); a.text(-0.26, a.get_ylim()[1] * 0.9, "≤ −0.25σ\nwarning row", ha="right", fontsize=8, color=ORANGE)
a.set_xlabel("first 5 minutes, 09:30→09:35 (σ)"); a.set_ylabel("next 55 minutes, 09:35→10:30 (σ)"); a.legend(frameon=False, fontsize=8, loc="lower right")
a.set_title("(c) TSLA Oct 28: the 09:35 read flagged the fade\n(first 5 min −0.31σ on −23% delta, then −0.81σ)", loc="left")
fig.suptitle("Deferred days, now measured: Oct 27's late drop was a closing-auction sell imbalance; Oct 28's fade showed at 09:35, not before",
             x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK)
fig.text(0.01, 0.01, "Databento: ES trades (GLBX), Nasdaq/Arca imbalance messages, TSLA Nasdaq trades and book. Return 15:50→close from Yahoo 5-min bars. Measurements unchanged from flow-physics and gap-teardown.", fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.03, 1, 0.92)); plt.savefig(HERE / "out" / "deferred_days.png", dpi=150, facecolor=BG); print("ok")
