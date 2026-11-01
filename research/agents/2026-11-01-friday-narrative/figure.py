"""out/friday_narrative.png: Fri Oct 30 timeline with the pre-registered chapter verdicts. Usage: python figure.py <db dir> <1m dir>"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"; DB, Y = Path(sys.argv[1]), Path(sys.argv[2]); ET = "America/New_York"
N = json.loads((OUT / "narrative.json").read_text())
GREEN, RED, INK, MUTED, SURF, BLUE, AMBER, GREY = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#e8a33d", "#c9c8c3"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.parse_math": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})


def es(day):
    d = pd.read_parquet(DB / f"ES_trades_{day}.parquet"); d = d[d.action == "T"]; d.index = d.index.tz_convert(ET)
    sz = d["size"].astype("int64"); d["signed"] = np.where(d.side == "B", sz, np.where(d.side == "A", -sz, 0))
    return d.signed.resample("1min").sum().between_time("09:30", "15:59")


fri = es("2026-10-30"); base = pd.concat([es(d).reset_index(drop=True) for d in ("2026-10-23", "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29")], axis=1)
spy = pd.read_parquet(DB / "SPY_1m_2026-10-30.parquet"); spy.index = spy.index.tz_convert(ET)
r = json.load(open(Y / "VIX_1m.json"))["chart"]["result"][0]
vix = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert(ET)).dropna()
vix = vix[vix.index.date == pd.Timestamp("2026-10-30").date()].between_time("09:30", "15:59")
p = pd.read_parquet(DB / "SPY_puts_tcbbo_2026-10-30.parquet"); p.index = p.index.tz_convert(ET); p["size"] = p["size"].astype("int64")
p["mid"] = (p.bid_px_00 + p.ask_px_00) / 2; p["sell"] = p.price < p.mid; p["exp"] = p.symbol.str[6:12]
hx = lambda idx: (idx.hour - 9.5) + idx.minute / 60
fig, ax = plt.subplots(4, 1, figsize=(17, 16), sharex=True, gridspec_kw={"height_ratios": [1.4, 1, 0.7, 0.9], "hspace": 0.12})
CH = [(0, 1, "C1 the open: aggressive selling, z −2.9\n(flow FOLLOWED price, did not lead)", RED), (1, 5, "C2 the grind: persistent flow + higher impact (pass);\nnet market orders roughly balanced: price slid on passive selling", AMBER),
      (5, 5.4, "C3 the low", BLUE), (5.4, 6.5, "C4 rebound: buyers arrived\n(ES +13.5k vs +2.8k normal); MOC was SELL-side", GREEN)]
for a in ax:
    for x0, x1, _, col in CH: a.axvspan(x0, x1, color=col, alpha=0.06, lw=0)
a = ax[0]; x = hx(spy.index); a.plot(x, spy.close, color=INK, lw=1.2)
for x0, x1, lab, col in CH: a.text((x0 + x1) / 2, 762.6, lab, ha="center", va="top", fontsize=9, color=col, weight="bold")
lo = spy.low.idxmin(); a.scatter([hx(pd.DatetimeIndex([lo]))[0]], [spy.low.min()], color=RED, zorder=5)
a.annotate(f"low {spy.low.min():.2f} ({lo.strftime('%H:%M')}): 750 = put wall + round number;\nvisible Arca book NOT thicker there (50 s of data)", (hx(pd.DatetimeIndex([lo]))[0], spy.low.min()), xytext=(-330, 8), textcoords="offset points", fontsize=9, color=RED, arrowprops=dict(arrowstyle="->", color=RED))
a.axhline(750, color=RED, ls="--", lw=0.8); a.set_ylabel("SPY"); a.set_ylim(748.5, 763)
a.set_title("Friday Oct 30, told only from pre-registered evidence (claims written before the data were pulled)", loc="left", fontsize=13, weight="bold", color=INK)
a = ax[1]; xb = np.arange(len(base)) / 60
a.plot(hx(fri.index), fri.cumsum() / 1000, color=INK, lw=1.8, label="Friday")
a.plot(xb, base.cumsum().mean(axis=1) / 1000, color=MUTED, lw=1.2, ls="--", label="mean of Oct 23-29")
a.axhline(0, color=MUTED, lw=0.5); a.set_ylabel("ES aggressive buy − sell,\ncumulative, k contracts"); a.legend(frameon=False, loc="upper left")
a.text(3, -9.5, "after the opening hour, market orders were net BUYING (+22.6k) while price kept falling:\nthe slide came from passive sellers and retreating bids, not from panic market orders", fontsize=9, color=INK)
a = ax[2]; a.plot(hx(vix.index), vix, color=BLUE, lw=1.4); a.set_ylabel("VIX")
vm = vix.idxmax(); a.annotate(f"VIX high {vix.max():.1f} at {vm.strftime('%H:%M')}\n(before the price low; seen before pre-registration)", (hx(pd.DatetimeIndex([vm]))[0], vix.max()), xytext=(15, -25), textcoords="offset points", fontsize=9, color=BLUE)
a = ax[3]
for ex, col, lab in (("261120", RED, "Nov 20 puts 740-760"), ("261030", AMBER, "Oct 30 (0DTE) puts 745-765")):
    y = p[p.exp == ex]; v5 = y["size"].resample("5min").sum(); s5 = y.loc[y.sell, "size"].resample("5min").sum().reindex(v5.index).fillna(0)
    scale = 1 if ex == "261120" else 0.1
    a.bar(hx(v5.index) + (0.02 if ex == "261120" else -0.02), v5 * scale, width=0.035, color=col, alpha=0.75, label=lab + (" (×0.1)" if scale != 1 else ""))
a.set_ylabel("put contracts per 5 min"); a.legend(frameon=False, loc="upper left")
c6 = N["C6 put monetization"]
a.text(5.45, a.get_ylim()[1] * 0.75, f"Nov 20 puts: {c6['Nov 20 740-760 13:30-14:30']['contracts/min']:.0f} → {c6['Nov 20 740-760 14:30-15:00']['contracts/min']:.0f}/min at the low;\n"
       f"seller-initiated {c6['Nov 20 740-760 14:30-15:00']['seller-initiated share']:.0%} at the low, {c6['Nov 20 740-760 15:00-15:30']['seller-initiated share']:.0%} in 15:00-15:30\n(put holders cashing in → dealers buy back hedges)", fontsize=9, color=RED)
a.set_xticks([0, 1, 2, 3, 4, 5, 6, 6.5]); a.set_xticklabels(["9:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:00"])
fig.text(0.01, 0.005, "Verdicts: C1 FAIL (aggressive selling yes, z −2.9; futures lead no). C2 PASS. C3a untestable as designed (top-10 book only ~10 cents deep; post-hoc alt: no thicker book). C3b PASS (buyers stepping up into the low).\n"
         "C4a PASS. C4b FAIL (month-end close was sell-side on Arca, ~1.0M shares at 15:50 → 82k by 15:59). C5 FAIL: election-night variance only 1.23× a normal day, so the VIX rise was not mainly election hedging. C6 PASS (weak at the low, strong after).",
         fontsize=9.5, color=INK)
fig.savefig(OUT / "friday_narrative.png", dpi=115, bbox_inches="tight"); print("ok")
