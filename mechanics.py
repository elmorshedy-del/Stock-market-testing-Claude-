"""What pushes price: the mechanical flows, measured on each asset's own history (REPORT 4y).

Every mechanic here is a flow that can be computed before it happens:
  dealer put decay    $ dealers buy back over the next 20 sessions as customer puts lose delta and
                      expire, spot and IV unchanged (charm + expiry; SPY / MSFT chains 2020+, mech_book.py)
  dealer put release  $ dealers buy back if implied vol falls to the vol actually being realised (vanna)
  hedge build         VIX vs its own 6-month median: how much protection has been bought (S&P, 1990+)
  vol-control         exposure change already scheduled for funds that size by realised vol: the 63-day
                      window's old days drop out, new days come in at the VIX rate (S&P, 1990+)
  dark-pool buying    DIX (S&P, 2011+) and the asset's own FINRA off-exchange short share (2019+)
Test: forward 20-session return in the top third minus the bottom third of each gauge (own history).
The null slides the gauge against returns by >= 60 sessions (circular shift), which keeps both
series' persistence. Today: each gauge's percentile in its own history.
Q4: is the Oct-Nov strength any of these? Gauge levels in Q4 vs other windows, and Q4's
week-of-quarter profile vs Q1-Q3 (buyback windows reopen in the same weeks every quarter).
Usage: python mechanics.py      (needs out/mech_book_{SPY,MSFT}.csv from mech_book.py)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import OUT, load_bars
from finra_dpi import load as load_dpi
from forecast import build as spx_frame
from release import frame as spx_long

C1, C2, C3, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "legend.frameon": False})
H, NULL, MINSHIFT = 20, 2000, 60
RNG = np.random.default_rng(7)


def fwd(c, h=H):
    return np.log(c.shift(-h) / c)


def spread_test(x, y):
    """Top-third minus bottom-third mean forward return, its circular-shift p, and today's percentile."""
    m = x.notna() & y.notna()
    xv, yv = x[m].to_numpy(), y[m].to_numpy()
    lo, hi = np.quantile(xv, [1 / 3, 2 / 3])
    top, bot = xv >= hi, xv <= lo
    obs = yv[top].mean() - yv[bot].mean()
    null = []
    for _ in range(NULL):
        s = RNG.integers(MINSHIFT, len(xv) - MINSHIFT)
        null.append(yv[np.roll(top, s)].mean() - yv[np.roll(bot, s)].mean())
    null = np.array(null)
    now = x.dropna().iloc[-1]
    return {"spread": 100 * obs, "p": float(np.mean(np.abs(null - null.mean()) >= abs(obs - null.mean()))),
            "top": 100 * yv[top].mean(), "bot": 100 * yv[bot].mean(), "n": int(m.sum()),
            "pct_now": float((x.dropna() < now).mean()), "start": x[m].index[0].year}


def book(sym):
    b = pd.read_csv(OUT / f"mech_book_{sym}.csv", parse_dates=["date"]).set_index("date")
    for k in ("put_hedge", "decay_put", "release_put", "call_hedge"):
        b[k] = b[k] / b.adv                        # in days of the asset's own $ volume
    return b


def gauges():
    f = spx_long()
    c, vix = f.c, f.VIX
    r2 = np.log(c).diff() ** 2
    G = pd.DataFrame(index=c.index)
    G["hedge build"] = np.log(vix / vix.rolling(126).median())
    G["vol-control"] = 0.5 * np.log(r2.rolling(63).sum() / (r2.rolling(63 - H).sum() + H * (vix / 100) ** 2 / 252))
    G["dix"] = spx_frame().dix.reindex(c.index)
    spy = book("SPY")
    dpi, _ = load_dpi()
    d5 = dpi.rolling(5).mean()
    spy_c, ms_c = load_bars("SPY").close, load_bars("MSFT").close
    ms = book("MSFT")
    sp_rows = [("dealer put decay (charm + expiry)", spy.decay_put, fwd(spy_c)),
               ("dealer put release (IV to realised)", spy.release_put, fwd(spy_c)),
               ("hedge build (VIX vs 6-month norm)", G["hedge build"], fwd(c)),
               ("vol-control re-leveraging", G["vol-control"], fwd(c)),
               ("dark-pool buying: DIX", G.dix, fwd(c)),
               ("dark-pool buying: SPY's own", d5["SPY"], fwd(spy_c))]
    ms_rows = [("dealer put decay (charm + expiry)", ms.decay_put, fwd(ms_c)),
               ("dealer put release (IV to realised)", ms.release_put, fwd(ms_c)),
               ("put hedge on the book", ms.put_hedge, fwd(ms_c)),
               ("call open interest (delta, $)", ms.call_hedge, fwd(ms_c)),
               ("dark-pool buying: MSFT's own", d5["MSFT"], fwd(ms_c))]
    sp = [(n, spread_test(x, y)) for n, x, y in sp_rows]
    msr = [(n, spread_test(x, y)) for n, x, y in ms_rows]
    # the decay gauge rises after rallies (puts drift out of the money): check it net of the past 20 sessions
    x = spy.decay_put
    past = np.log(spy_c / spy_c.shift(20)).reindex(x.index)
    y = fwd(spy_c).reindex(x.index)
    m = x.notna() & past.notna() & y.notna()
    rk = lambda s: (s[m].rank() - s[m].rank().mean()).to_numpy()
    rx, rp, ry = rk(x), rk(past), rk(y)
    res = lambda a, b_: a - b_ * (a @ b_) / (b_ @ b_)
    partial = np.corrcoef(res(rx, rp), res(ry, rp))[0, 1]
    print(f"SPY put decay vs past 20d return: rank corr {np.corrcoef(rx, rp)[0, 1]:+.2f}; decay vs forward net of past {partial:+.3f} "
          f"(raw {np.corrcoef(rx, ry)[0, 1]:+.3f})")
    for lab, rows in (("S&P / SPY", sp), ("MSFT", msr)):
        print(f"\n{lab}: forward {H}-session return, top third minus bottom third of each gauge")
        for n, r in rows:
            print(f"   {n:38s} {r['start']}+ n={r['n']:5d}: top {r['top']:+.2f}% bottom {r['bot']:+.2f}% spread {r['spread']:+.2f} "
                  f"(p {r['p']:.2f}) | today {r['pct_now']:.0%}")
    return G, spy, ms, d5, sp, msr


def q4_check(G):
    c = spx_long().c
    f = fwd(c)
    q4 = ((c.index.month == 10) & (c.index.day >= 12)) | (c.index.month == 11)
    lv = {}
    for k in ("hedge build", "vol-control", "dix"):
        p = G[k].rolling(252, min_periods=120).rank(pct=True)
        lv[k] = (p[q4].mean(), p[~q4].mean())
    c2 = c["1995":"2026-09"]
    first = c2.index.to_series().groupby(c2.index.to_period("Q")).transform("min")
    pos = pd.Series(np.arange(len(c2)), index=c2.index)
    wk = ((pos - pos.reindex(first.values).to_numpy()) // 5).clip(upper=12)
    Z = pd.DataFrame({"wk": wk, "f": 100 * f.reindex(c2.index), "q4": c2.index.quarter == 4}).dropna()
    prof = Z.groupby(["wk", "q4"]).f.mean().unstack()
    nq = Z.groupby(["wk", "q4"]).f.size().unstack()
    print("\nQ4 vs other windows, mean trailing-year percentile:", {k: f"{a:.2f} vs {b:.2f}" for k, (a, b) in lv.items()})
    print("week-of-quarter forward 20-session return %, 1995+:")
    print(prof.round(2).T.to_string())
    return prof, lv, nq


def figure(G, spy, ms, d5, sp, msr, prof, lv):
    f = plt.figure(figsize=(15, 10.5))
    gs = f.add_gridspec(2, 2, height_ratios=[1, 1.05], hspace=0.42, wspace=0.62)

    def bars(a, rows, title):
        ys = np.arange(len(rows))
        third = lambda q: "top third" if q >= 2 / 3 else ("bottom third" if q <= 1 / 3 else "middle third")
        for y, (n, r) in zip(ys, rows):
            col = C1 if r["spread"] > 0 else C2
            a.barh(y, r["spread"], color=col, height=0.55, alpha=1.0 if r["p"] < 0.1 else 0.45)
            a.annotate(f"p {r['p']:.2f}", (r["spread"], y), xytext=(4 if r["spread"] >= 0 else -4, 0), textcoords="offset points",
                       ha="left" if r["spread"] >= 0 else "right", va="center", fontsize=7.5, color=MUTED)
        a.set_yticks(ys, [f"{n}\n{r['start']}+  ·  today {r['pct_now']:.0%} ({third(r['pct_now'])})" for n, r in rows])
        a.tick_params(axis="y", labelsize=8)
        a.invert_yaxis()
        a.axvline(0, color=INK, lw=0.8)
        lim = max(abs(r["spread"]) for _, r in rows) * 1.6
        a.set_xlim(-lim, lim)
        a.set_xlabel(f"forward {H}-session return: top third minus bottom third of the gauge (% points)")
        a.grid(axis="y", visible=False)
        a.set_title(title, loc="left", fontsize=9.5, color=INK)

    bars(f.add_subplot(gs[0, 0]), sp, "S&P / SPY: does each mechanic push price?\n"
         "pale = could be luck (p >= 0.1); under each name: where today sits in its own history")
    bars(f.add_subplot(gs[0, 1]), msr, "MSFT, its own data only: nothing clears luck;\n"
         "heavy call OI (a record today) has come before weaker months")

    c_ = f.add_subplot(gs[1, 0])
    x = prof.index.to_numpy()
    c_.plot(x, prof[False], color=MUTED, lw=2, marker="o", ms=4, label="Q1-Q3 (Jan-Sep)")
    c_.plot(x, prof[True], color=C1, lw=2.4, marker="o", ms=4, label="Q4 (Oct-Dec)")
    c_.axvspan(3.5, 10.5, color=C3, alpha=0.08, lw=0)
    c_.annotate("buyback window mostly open\n(after reports, until ~2 weeks\nbefore quarter end)", (7, c_.get_ylim()[1]), xytext=(0, -4),
                textcoords="offset points", ha="center", va="top", fontsize=8, color=C3)
    c_.axhline(0, color=MUTED, lw=0.7)
    c_.set_xticks(x, [f"{int(k) + 1}" for k in x])
    c_.set_xlabel("week of the quarter the 20-session window starts in (S&P, 1995-2026)")
    c_.set_ylabel(f"mean forward {H}-session return, %")
    c_.legend(loc="lower left", fontsize=8)
    c_.set_title("Q4's edge is not a mechanic we can see: it sits in weeks 1-6, where Q1-Q3 are weakest,\n"
                 f"and dark-pool buying is LOWER in Oct-Nov (pct {lv['dix'][0]:.2f} vs {lv['dix'][1]:.2f}); hedge build "
                 f"{lv['hedge build'][0]:.2f} vs {lv['hedge build'][1]:.2f}", loc="left", fontsize=9.5, color=INK)

    sub = gs[1, 1].subgridspec(2, 1, height_ratios=[1, 1], hspace=0.08)
    a1, a2 = f.add_subplot(sub[0]), f.add_subplot(sub[1])
    w = ms.loc["2026-05-01":]
    a1.plot(w.index, w.spot, color=INK, lw=1.8)
    rep = pd.Timestamp("2026-07-29")
    nxt = pd.Timestamp("2026-10-29")
    for a in (a1, a2):
        a.axvline(rep, color=C2, lw=1, ls=":")
        a.axvline(nxt, color=C1, lw=1, ls=":")
        a.set_xlim(w.index[0], pd.Timestamp("2026-11-06"))
    a1.annotate("Oct 28 report", (nxt, a1.get_ylim()[0]), xytext=(-4, 4), textcoords="offset points", ha="right", fontsize=8, color=C1)
    a1.annotate("Jul 29 report", (rep, a1.get_ylim()[1]), xytext=(-4, -4), textcoords="offset points", ha="right", va="top", fontsize=8,
                color=C2)
    a1.set_ylabel("MSFT")
    a1.tick_params(labelbottom=False)
    a1.set_title("MSFT 2026: what was loaded before the July move vs now\n"
                 "(percentile vs its own trailing year)", loc="left", fontsize=9.5, color=INK)
    pr = lambda s: s.rolling(252, min_periods=120).rank(pct=True).reindex(w.index)
    a2.plot(w.index, pr(ms.put_hedge).rolling(3, min_periods=1).mean(), color=C2, lw=1.8, label="put hedge on dealers' book (fuel)")
    a2.plot(w.index, pr(ms.call_hedge).rolling(3, min_periods=1).mean(), color=C3, lw=1.8, label="call open interest")
    a2.plot(w.index, pr(d5["MSFT"]).rolling(3, min_periods=1).mean(), color=C1, lw=2.2, label="own dark-pool buying")
    a2.set_ylim(0, 1.02)
    a2.set_ylabel("percentile")
    a2.legend(loc="lower left", fontsize=7.5, ncol=2, bbox_to_anchor=(0, -0.5))
    a2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b"))
    f.suptitle("The flows that move price are buyers, not dealer re-hedging. Charm, vanna and vol-control flows don't predict "
               "the S&P or MSFT on their own data.\nToday: S&P dark-pool buying is high, SPY's own has faded. MSFT: "
               "buyers have stayed since July and call OI is a record; no flow pushes it before the Oct 28 report.", x=0.01, ha="left", fontsize=10.5, color=INK, weight="bold")
    f.subplots_adjust(top=0.9, bottom=0.09, left=0.17, right=0.97)
    f.savefig(OUT / "mechanics.png", dpi=150)


if __name__ == "__main__":
    G, spy, ms, d5, sp, msr = gauges()
    prof, lv, _ = q4_check(G)
    figure(G, spy, ms, d5, sp, msr, prof, lv)
    print("saved", OUT / "mechanics.png")
