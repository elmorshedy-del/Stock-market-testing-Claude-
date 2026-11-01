"""out/explainer_buying_falling.png: (A) how price falls while market orders are net buys, (B) Friday's real ES buy- vs
sell-initiated volume, (C) price-then-selling vs selling-then-price at the open, (D) the feedback loop. Usage: python explainer.py <db dir>"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"; DB = Path(sys.argv[1]); ET = "America/New_York"
GREEN, RED, INK, MUTED, SURF, BLUE, AMBER, GREY = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#e8a33d", "#c9c8c3"
plt.rcParams.update({"font.size": 10.5, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.parse_math": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
d = pd.read_parquet(DB / "ES_trades_2026-10-30.parquet"); d = d[d.action == "T"]; d.index = d.index.tz_convert(ET); sz = d["size"].astype("int64")
m = pd.DataFrame({"buy": sz.where(d.side == "B", 0).resample("1min").sum(), "sell": sz.where(d.side == "A", 0).resample("1min").sum(), "px": d.price.resample("1min").last()}).between_time("09:30", "15:59")
m["px"] = m.px.ffill(); m["flow"] = m.buy - m.sell; m["ret"] = np.log(m.px).diff() * 1e4
fig = plt.figure(figsize=(18, 14)); gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.18)

# A: order-book cartoon
a = fig.add_subplot(gs[0, 0]); a.axis("off"); a.set_xlim(0, 30); a.set_ylim(-1.5, 11)
levels = [100.03, 100.02, 100.01, 100.00, 99.99, 99.98, 99.97]
frames = [  # (asks {price: size}, bids {price: size}, buy_at)
    ({100.03: 3, 100.02: 3, 100.01: 4}, {100.00: 4, 99.99: 3, 99.98: 3}, 100.01),
    ({100.02: 2, 100.01: 3, 100.00: 5}, {99.99: 2, 99.98: 3, 99.97: 3}, 100.00),
    ({100.01: 2, 100.00: 3, 99.99: 5}, {99.98: 2, 99.97: 2}, 99.99)]
for f, (asks, bids, buy) in enumerate(frames):
    x0 = 1 + f * 10
    a.text(x0 + 3.5, 10.4, ["1. start", "2. a moment later", "3. a moment later"][f], ha="center", fontsize=11, weight="bold", color=INK)
    for i, lv in enumerate(levels):
        y = 9 - i * 1.3
        a.text(x0, y, f"{lv:.2f}", fontsize=9, color=MUTED, va="center")
        if lv in asks: a.add_patch(plt.Rectangle((x0 + 2.2, y - 0.4), asks[lv] * 0.9, 0.8, color=RED, alpha=0.75))
        if lv in bids: a.add_patch(plt.Rectangle((x0 + 2.2, y - 0.4), bids[lv] * 0.9, 0.8, color=GREEN, alpha=0.75))
        if lv == buy:
            a.annotate("", xy=(x0 + 2.2, y), xytext=(x0 + 7.6, y), arrowprops=dict(arrowstyle="->", color=INK, lw=2))
            a.text(x0 + 7.7, y + 0.35, "market BUY\nhits the ask", fontsize=8, color=INK, va="bottom")
    mid = (min(asks) + max(bids)) / 2
    a.text(x0 + 3.5, -0.6, f"price ≈ {mid:.3f}", ha="center", fontsize=10.5, color=RED if f else INK, weight="bold")
a.text(1, -1.4, "red = resting SELL orders (asks)   green = resting BUY orders (bids)\nEvery trade here is started by a buyer, yet the price falls: the seller keeps re-posting lower asks and bidders step back.",
       fontsize=9.5, color=INK, va="top")
a.set_title("A. How price can fall while BUYERS start the trades", loc="left", fontsize=13, weight="bold", color=INK)

# B: real Friday volumes 10:30-14:52
b = fig.add_subplot(gs[0, 1]); g = m.between_time("10:30", "14:52")
x = (g.index.hour - 9.5) + g.index.minute / 60
b.plot(x, g.buy.cumsum() / 1000, color=GREEN, lw=2, label=f"buyer-started volume ({g.buy.sum()/1000:.0f}k)")
b.plot(x, g.sell.cumsum() / 1000, color=RED, lw=2, label=f"seller-started volume ({g.sell.sum()/1000:.0f}k)")
b.fill_between(x, g.sell.cumsum() / 1000, g.buy.cumsum() / 1000, color=GREEN, alpha=0.15)
b.set_ylabel("ES contracts, cumulative (k)"); b.legend(frameon=False, loc="lower right")
b2 = b.twinx(); b2.plot(x, g.px, color=INK, lw=1.2, alpha=0.7); b2.set_ylabel("ES price", color=INK); b2.spines["right"].set_visible(True)
gap = g.buy.sum() - g.sell.sum(); b.text(x[len(x) // 2], g.sell.sum() / 1000 * 0.25, f"buyers started only {gap/1000:+.1f}k more\n= {gap / (g.buy.sum() + g.sell.sum()):.1%} of all volume:\nnearly a tie, not a buying spree.\nPrice fell {g.px.iloc[-1] - g.px.iloc[0]:+.0f} points anyway (black line)", fontsize=9.5, color=INK, ha="center")
b.set_xticks([1, 2, 3, 4, 5]); b.set_xticklabels(["10:30", "11:30", "12:30", "13:30", "14:30"])
b.set_title("B. Friday 10:30-14:52, real futures data: almost a tie, price down", loc="left", fontsize=13, weight="bold", color=INK)

# C: two scatters at the open
c = fig.add_subplot(gs[1, 0]); o = m.between_time("09:30", "10:29").copy()
o["next_flow"] = o.flow.shift(-1); o["next_ret"] = o.ret.shift(-1); o = o.dropna()
c.scatter(o.ret, o.next_flow / 1000, color=RED, s=26, alpha=0.8, label=f"price move this minute → net selling NEXT minute (corr {o.ret.corr(o.next_flow):+.2f})")
fit = np.polyfit(o.ret, o.next_flow / 1000, 1); xx = np.linspace(o.ret.min(), o.ret.max(), 10); c.plot(xx, np.polyval(fit, xx), color=RED, lw=1.5)
c.axhline(0, color=MUTED, lw=0.5); c.axvline(0, color=MUTED, lw=0.5); c.set_ylim(-2.6, 1.6)
c.set_xlabel("ES price change this minute, bp"); c.set_ylabel("net buying (+) / selling (−) the NEXT minute, k contracts")
c.text(0.02, 0.04, f"Opposite direction: net selling this minute → price change NEXT minute: corr {o.flow.corr(o.next_ret):+.2f} (nothing).\nSame minute: selling and falling happen together (corr {o.flow.corr(o.ret):+.2f}).\nSo selling DID push price in the moment, but each drop called in MORE selling a minute later.",
       transform=c.transAxes, fontsize=9.5, color=INK)
c.legend(frameon=False, loc="upper left", fontsize=9.5)
c.set_title("C. The open (9:30-10:30): drops came first, extra selling followed", loc="left", fontsize=13, weight="bold", color=INK)

# D: feedback loop
dd = fig.add_subplot(gs[1, 1]); dd.axis("off"); dd.set_xlim(0, 10); dd.set_ylim(0, 10)
box = lambda x, y, t, col: (dd.add_patch(FancyBboxPatch((x - 1.9, y - 0.75), 3.8, 1.5, boxstyle="round,pad=0.15", fc=col + "22", ec=col, lw=2)), dd.text(x, y, t, ha="center", va="center", fontsize=10.5, color=INK))
box(5, 8.5, "price ticks down", RED)
box(7.7, 5, "forced sellers react:\ndealer hedges (short gamma),\nstop-losses, trend algos", AMBER)
box(5, 1.5, "they sell into the bids", RED)
box(2.3, 5, "bids thin out / step back\n(liquidity providers retreat)", BLUE)
for (x1, y1), (x2, y2) in (((6.6, 8.0), (7.6, 6.0)), ((7.6, 4.0), (6.6, 2.0)), ((3.4, 2.0), (2.4, 4.0)), ((2.4, 6.0), (3.4, 8.0))):
    dd.add_patch(FancyArrowPatch((x1, y1), (x2, y2), connectionstyle="arc3,rad=-0.2", arrowstyle="-|>", mutation_scale=22, color=INK, lw=1.8))
dd.text(5, 5, "a loop that\nfeeds itself", ha="center", va="center", fontsize=12, color=MUTED, style="italic")
dd.text(0.1, 0.0, "Informed selling looks different: selling comes FIRST and price follows (someone knows something).\nFriday's open looked like the loop: the price moved, then reactive sellers piled in. The loop stopped when\nbuyers began stepping up (14:37-14:52) and VIX turned (14:35).", fontsize=9.5, color=INK, va="top")
dd.set_title("D. Why 'price first, selling after' still means selling pushed price", loc="left", fontsize=13, weight="bold", color=INK)
fig.suptitle("Two things that sound backwards, explained with Friday's own data", x=0.01, ha="left", fontsize=16, weight="bold", color=INK)
fig.savefig(OUT / "explainer_buying_falling.png", dpi=115, bbox_inches="tight"); print("ok")
