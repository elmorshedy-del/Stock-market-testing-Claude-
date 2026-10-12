"""Figure for REPORT 4aa: is MSFT held back by a pinned market and released when S&P dealer gamma is low?
Usage: python held_back_fig.py      (after held_back.py MSFT AAPL AMZN GOOGL META NVDA AVGO)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import OUT, load_bars
from held_back import cells, frame, pct

C1, C2, C3, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "legend.frameon": False})
PEERS = ["MSFT", "GOOGL", "AMZN", "AVGO", "NVDA", "META", "AAPL"]
GEX = "S&P dealer gamma (GEX)"


def main():
    X = frame("MSFT")
    t = cells(X, col="gex", start="2012-01-01")
    f = plt.figure(figsize=(15, 9.6))
    gs = f.add_gridspec(2, 2, height_ratios=[1, 0.95], hspace=0.45, wspace=0.25)

    a = f.add_subplot(gs[0, 0])
    labs = ["MSFT leading SPY\nS&P gamma low", "MSFT leading SPY\nS&P gamma not low", "MSFT not leading\nS&P gamma low",
            "MSFT not leading\nS&P gamma not low"]
    xs = np.arange(4)
    a.bar(xs - 0.2, t["up-leg %"], width=0.38, color=C3, label="up-leg starts within 10 sessions")
    a.bar(xs + 0.2, t["down-leg %"], width=0.38, color=C2, label="down-leg starts within 10 sessions")
    for x, (u, d) in zip(xs, t[["up-leg %", "down-leg %"]].itertuples(index=False)):
        a.annotate(f"{u:.0f}%", (x - 0.2, u), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5)
        a.annotate(f"{d:.0f}%", (x + 0.2, d), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5)
    labs = [f"{l}\nreturn {r:+.1f}%\n{n} days" for l, r, n in zip(labs, t["return %"], t["days"])]
    a.set_xticks(xs, labs, fontsize=8)
    a.set_ylim(0, 62)
    a.set_ylabel("% of days")
    a.legend(loc="upper right", fontsize=8)
    a.axvspan(-0.5, 0.5, color=C3, alpha=0.07, lw=0)
    a.set_title("MSFT 2017-2026: leading SPY (20-day, top third) and S&P dealer gamma (bottom third)\n"
                "a leader under a low-gamma market gets the up-legs without the extra down-legs", loc="left", fontsize=9.5, color=INK)
    a.grid(axis="x", visible=False)

    b = f.add_subplot(gs[0, 1])
    rows = []
    for s in PEERS:
        fm = pd.read_csv(OUT / f"held_back_families_{s}.csv")
        q = fm[(fm.gauge == GEX) & (fm.days == "in state") & (fm.statistic == "release")].set_index("outcome")
        rows.append((s, 100 * q.loc["up-leg", "median_effect"], q.loc["up-leg", "joint_p"], 100 * q.loc["down-leg", "median_effect"],
                     q.loc["down-leg", "joint_p"]))
    ys = np.arange(len(rows))
    for y, (s, u, pu, d, pd_) in zip(ys, rows):
        b.barh(y - 0.19, u, height=0.36, color=C3, alpha=1 if pu < 0.05 else 0.4)
        b.barh(y + 0.19, d, height=0.36, color=C2, alpha=1 if pd_ < 0.05 else 0.4)
        b.annotate(f"p {pu:.3f}" if pu >= 0.003 else "p < 0.003", (max(u, 0), y - 0.19), xytext=(4, 0), textcoords="offset points", va="center",
                   fontsize=7.5, color=MUTED)
        b.annotate(f"p {pd_:.3f}" if pd_ >= 0.003 else "p < 0.003", (max(d, 0), y + 0.19), xytext=(4, 0), textcoords="offset points",
                   va="center", fontsize=7.5, color=MUTED)
    b.set_yticks(ys, [r[0] for r in rows])
    b.invert_yaxis()
    b.axvline(0, color=INK, lw=0.8)
    b.set_xlim(-5, 38)
    b.set_xlabel("change in up-leg (green) / down-leg (orange) odds, pct points, when S&P gamma is low\n"
                 "and the stock leads SPY (median of 27 specifications; pale = could be luck)")
    b.grid(axis="y", visible=False)
    b.set_title("Same test on other mega-caps: MSFT is the cleanest case, GOOGL and AMZN agree;\n"
                "META and NVDA just move more both ways; AAPL gets more down-legs", loc="left", fontsize=9.5, color=INK)

    c = f.add_subplot(gs[1, :])
    m, s = load_bars("MSFT").close, load_bars("SPY").close
    idx = m.index.intersection(s.index)
    lm, ls = np.log(m.reindex(idx)), np.log(s.reindex(idx))
    rs = pct((lm - lm.shift(20)) - (ls - ls.shift(20)))
    w0 = pd.Timestamp("2026-05-01")
    rs, gx = rs[rs.index >= w0], X.gex[X.index >= w0].dropna()
    c.axhspan(0, 1 / 3, color=C1, alpha=0.08, lw=0)
    c.axhspan(2 / 3, 1, color=C3, alpha=0.08, lw=0)
    c.plot(gx.index, gx, color=C1, lw=2.2, label="S&P dealer gamma percentile (low = market unpinned)")
    c.plot(rs.index, rs, color=C3, lw=2.2, label="MSFT 20-day lead over SPY, percentile (high = leading)")
    both = (rs.reindex(gx.index) >= 2 / 3) & (gx <= 1 / 3)
    c.scatter(gx.index[both], gx[both], color=INK, s=22, zorder=5, label="both on: the release setup")
    c.annotate("bottom third: S&P gamma low", (pd.Timestamp("2026-08-04"), 0.03), fontsize=8, color=C1)
    c.annotate("top third: MSFT leading", (pd.Timestamp("2026-06-08"), 0.97), fontsize=8, color=C3, va="top")
    for d, lab in (("2026-07-29", "Jul 29\nreport"), ("2026-10-16", "Oct 16\nexpiry"), ("2026-10-28", "Oct 28\nreport")):
        c.axvline(pd.Timestamp(d), color=MUTED, lw=1, ls=":")
        c.annotate(lab, (pd.Timestamp(d), 1.0), xytext=(3, -2), textcoords="offset points", fontsize=8, color=MUTED, va="top")
    c.scatter([gx.index[-1]], [gx.iloc[-1]], color=C1, s=55, zorder=6, edgecolor=SURF, lw=1.5)
    c.annotate(f"{gx.iloc[-1]:.2f} on {gx.index[-1]:%b %d}", (gx.index[-1], gx.iloc[-1]), xytext=(6, -12), textcoords="offset points",
               fontsize=8.5, color=C1)
    c.scatter([rs.index[-1]], [rs.iloc[-1]], color=C3, s=55, zorder=6, edgecolor=SURF, lw=1.5)
    c.set_xlim(w0, pd.Timestamp("2026-11-06"))
    c.set_ylim(0, 1.02)
    c.set_ylabel("percentile vs trailing year")
    c.legend(loc="lower left", fontsize=8, ncol=3, bbox_to_anchor=(0, -0.2))
    c.set_title("Now: MSFT leads (top third) but S&P gamma is not low (0.62), so the release setup is OFF.\n"
                "From readings like this it hit the bottom third within 10 sessions 53% of the time; the Oct 16 expiry removes 78% of "
                "SPY's dealer gamma.", loc="left", fontsize=9.5, color=INK)
    f.suptitle("Your thesis, tested: MSFT held back by a pinned market and released when S&P dealer gamma is low. "
               "Supported for MSFT (up-legs 50% vs 24%, p < 0.003).\nThe trigger is S&P gamma, not SPY open interest near its "
               "price (that version shows nothing).", x=0.01, ha="left", fontsize=10.5, color=INK, weight="bold")
    f.subplots_adjust(top=0.89, bottom=0.11, left=0.05, right=0.98)
    f.savefig(OUT / "held_back.png", dpi=150)
    print("saved", OUT / "held_back.png")


if __name__ == "__main__":
    main()
