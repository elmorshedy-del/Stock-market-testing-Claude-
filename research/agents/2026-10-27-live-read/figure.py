"""Live read for Wed Oct 28: gamma maps (positions at the Oct 26 close, Tuesday's spot) + Tuesday's 5-minute path vs the levels.
Usage: python figure.py <live27/y folder with SPY_5m.json, TSLA_5m.json>  -> out/live_read_1028.png"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
LV = json.loads((OUT / "levels.json").read_text())
GREEN, RED, INK, MUTED, SURF, BLUE, ORANGE = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})


def bars(folder, n):
    r = json.loads((Path(folder) / f"{n}_5m.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    df = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")},
                      index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna(subset=["close"])
    return df[df.index.date == df.index.date.max()].between_time("09:30", "15:59")


def gamma_panel(ax, sym, lo, hi, step):
    L = LV[sym]; S = L["spot"]
    k = pd.read_csv(OUT / f"strikes_{sym}.csv").set_index("K").gex / 1e9
    k = k[(k.index >= lo) & (k.index <= hi) & ((k.index % step) == 0)]
    ax.barh(k.index, k.values, height=step * 0.8, color=[GREEN if v > 0 else RED for v in k.values])
    p = pd.read_csv(OUT / f"profile_{sym}.csv"); p = p[(p.price >= lo) & (p.price <= hi)]
    ax2 = ax.twiny(); ax2.plot(p["total dealer GEX $bn"], p.price, color=INK, lw=1.4); ax2.axvline(0, color=MUTED, lw=0.6, ls=":")
    ax2.set_xlabel("total dealer gamma if price were here, $bn per 1% (line)", fontsize=7.5, color=MUTED); ax2.tick_params(labelsize=7.5)
    ax.axhline(S, color=BLUE, lw=1.6); ax.text(ax.get_xlim()[1], S, f" close {S:.2f}", color=BLUE, va="bottom", ha="right", fontsize=8)
    ax.axhline(L["flip"], color=ORANGE, lw=1.4, ls="--"); ax.text(ax.get_xlim()[0], L["flip"], f" flip {L['flip']:.1f}", color=ORANGE, va="bottom", fontsize=8)
    ax.set_ylim(lo, hi); ax.set_xlabel(f"dealer gamma by strike, $bn per 1% (bars; every {step})")
    ax.set_ylabel(f"{sym} price")


def path_panel(ax, df, sym, levels):
    ax.plot(range(len(df)), df.close, color=INK, lw=1.3)
    vw = (df.close * df.volume).cumsum() / df.volume.cumsum(); ax.plot(range(len(df)), vw, color=MUTED, lw=1, ls=":")
    for y, lab, c in levels:
        ax.axhline(y, color=c, lw=1, ls="--"); ax.text(len(df) - 1, y, f" {lab}", color=c, fontsize=7.5, va="bottom", ha="right")
    ticks = [i for i, t in enumerate(df.index) if t.minute == 30 and t.hour in (10, 12, 14)] + [len(df) - 1]
    ax.set_xticks(ticks, [df.index[i].strftime("%H:%M") for i in ticks])
    ax.set_ylabel(f"{sym}, 5-minute closes (dotted: VWAP)")


fig, ax = plt.subplots(2, 2, figsize=(16, 11), gridspec_kw={"width_ratios": [1, 1.25], "hspace": 0.5, "wspace": 0.25})
s, t = LV["SPY"], LV["TSLA"]
gamma_panel(ax[0, 0], "SPY", 735, 805, 5)
ax[0, 0].set_title(f"SPY map for Wednesday: closed {abs(s['spot vs flip %']):.2f}% UNDER the flip ({s['flip']:.1f})\n"
                   f"Dealers short {abs(s['total GEX $bn per 1%']):.1f}bn per 1% (was -8.8bn Mon). Pocket 740-765 (red),\n"
                   f"magnets 775-800 (green). Call wall 800, put wall 750 (+82k puts built Mon)", loc="left", fontsize=9, color=INK)
dS = bars(sys.argv[1], "SPY")
path_panel(ax[0, 1], dS, "SPY", [(s["flip"], f"flip {s['flip']:.1f}", ORANGE), (775, "775 first green strike", GREEN), (765, "765", RED)])
ax[0, 1].set_title("Tuesday: SPY chopped around 770 and never closed a 5-minute bar above the flip\n"
                   "(high 771.14). AI-led: S&P +0.6% but the median large cap was flat (40 of 83 up).\n"
                   "A close above ~772.5 is the line where rallies have tended to hold (+13% vs -53% kept)", loc="left", fontsize=9, color=INK)
gamma_panel(ax[1, 0], "TSLA", 360, 440, 5)
ax[1, 0].set_title(f"TSLA map: long gamma (own-gamma {t['own-gamma pct']:.0%} pctile), {t['spot vs flip %']:.0f}% above flip {t['flip']:.0f}.\n"
                   f"Freed: near-price OI at the {t['near-OI pct (freed <= 0.33)']:.0%} pctile ({t['after Oct 30 expiry']['near-OI pct']:.1%} after Fri).\n"
                   f"400 (50k calls) is now BELOW price; next magnet 420 (40k calls, +15k built Mon)", loc="left", fontsize=9, color=INK)
dT = bars(sys.argv[1], "TSLA")
path_panel(ax[1, 1], dT, "TSLA", [(400, "400 call wall / round number", GREEN), (397.27, "Mon high 397.27", MUTED), (420, "420 magnet", GREEN)])
ax[1, 1].set_ylim(393, 423)
ax[1, 1].set_title("Tuesday: TSLA broke 400 in the 2nd five minutes and held it all day\n"
                   "(99% of bars above), closing near the high at 407.46, above VWAP.\n"
                   "The lid became a floor. Daily history: breaks of highs don't carry on by themselves (P4a)", loc="left", fontsize=9, color=INK)
fig.savefig(OUT / "live_read_1028.png", dpi=140, bbox_inches="tight", facecolor=SURF)
