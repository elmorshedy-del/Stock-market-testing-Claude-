"""Where TSLA stands now (REPORT 4w): what the Oct 16 monthly expiry removes, TSLA's own
dark-pool index around the named moves vs now, and the calendar ahead with the windows
the named moves used.
Usage: python tsla_now.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import td_gamma as t
from common import OUT, load_bars
from episodes import EPISODES, TODAY_START
from finra_dpi import load as load_dpi
from hd_gamma import flip
from options_flow import exposures

C1, C2, C3, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "legend.frameon": False})
EXPIRY = pd.Timestamp("2026-10-16")


def chain(day):
    eod, oi = t.read("TSLA", "eod"), t.read("TSLA", "oi")
    e, o = eod[eod.date == day].copy(), oi[oi.date == day]
    e["mid"] = (e.bid + e.ask) / 2
    oc = next(c for c in o.columns if "open_interest" in c)
    d = e.merge(o[["date", "expiration", "strike", "cp", oc]].rename(columns={oc: "oi"}),
                on=["date", "expiration", "strike", "cp"], how="left")
    d["oi"] = d.oi.fillna(0)
    g = t.chain_day(d[(d.expiration - d.date).dt.days <= 120])
    g = g[g.oi > 0].copy()
    S = float(g.underlying_close.iloc[0])
    g["gex"] = exposures(g, S, "classic").gex.values
    return g, S


def main():
    day = t.read("TSLA", "oi").date.max()
    g, S = chain(day)
    f = plt.figure(figsize=(15, 9))
    gs = f.add_gridspec(2, 2, height_ratios=[1.1, 1])
    a = f.add_subplot(gs[0, 0])
    lo, hi = 0.8 * S, 1.2 * S
    z = g[g.K.between(lo, hi)]
    roll = z.expiration <= EXPIRY
    for lab, m, col in (("expires by Fri Oct 16", roll, C2), ("stays after Oct 16", ~roll, C1)):
        cg = z[m & (z.cp == "C")].groupby("K").oi.sum()
        pg = z[m & (z.cp == "P")].groupby("K").oi.sum()
        a.bar(cg.index - (1.2 if col == C2 else -1.2), cg / 1e3, width=2.2, color=col, label=f"call OI, {lab}")
        a.bar(pg.index - (1.2 if col == C2 else -1.2), -pg / 1e3, width=2.2, color=col, alpha=0.55, label=f"put OI, {lab}")
    a.axvline(S, color=INK, lw=1.2)
    a.annotate(f"TSLA {S:.0f}", (S, a.get_ylim()[1] * 0.92), xytext=(4, 0), textcoords="offset points", fontsize=8.5, color=INK)
    fa, fb = flip(g, S), flip(g[g.expiration > EXPIRY], S)
    for v, lab, col, yy in ((fa, f"own flip now {fa:.0f}", C2, 0.97), (fb, f"own flip after Oct 16 {fb:.0f}", C1, 0.90)):
        a.axvline(v, color=col, lw=1.2, ls="--")
        a.annotate(lab, (v, yy), xycoords=("data", "axes fraction"), xytext=(-4, 0), textcoords="offset points", ha="right",
                   fontsize=8, color=col, va="top")
    a.axhline(0, color=MUTED, lw=0.8)
    net_all, net_after = g.gex.sum(), g[g.expiration > EXPIRY].gex.sum()
    share = g[g.expiration <= EXPIRY].gex.abs().sum() / g.gex.abs().sum()
    a.set_title(f"TSLA open interest by strike, {day.date()} (calls up, puts down, thousands)\n"
                f"{share:.0%} of near-term gamma expires by Oct 16; dealer gamma {net_all / 1e6:.0f}M -> {net_after / 1e6:.0f}M "
                "per 1% after", loc="left", fontsize=9.5, color=INK)
    a.set_xlabel("strike")
    a.legend(loc="lower right", fontsize=7.5, ncol=1)

    b = f.add_subplot(gs[0, 1])
    dpi, _ = load_dpi()
    tp = dpi["TSLA"].dropna().rolling(5).mean().rolling(252, min_periods=120).rank(pct=True)
    for name, s, e, _ in EPISODES:
        i0 = tp.index.searchsorted(pd.Timestamp(s))
        w = tp.iloc[i0 - 15:i0 + 21]
        b.plot(np.arange(-15, len(w) - 15), w.to_numpy(), color=MUTED, lw=1, alpha=0.55,
               label="the 7 named moves" if name == EPISODES[0][0] else None)
    i0 = tp.index.searchsorted(pd.Timestamp(TODAY_START))
    w = tp.iloc[i0 - 15:]
    b.plot(np.arange(-15, len(w) - 15), w.to_numpy(), color=C1, lw=2.6, label="TSLA now (start = Sep 29 base)")
    b.scatter(len(w) - 16, w.iloc[-1], color=C1, s=40, zorder=5, edgecolor=SURF, lw=1.5)
    b.axvline(0, color=INK, lw=0.9)
    b.set_ylim(0, 1)
    b.set_xlabel("sessions from the start")
    b.set_ylabel("percentile vs trailing year")
    b.legend(loc="lower left", fontsize=8)
    b.set_title("TSLA's own dark-pool index (FINRA off-exchange short share, 5-day mean)\n"
                "the named moves were high or rising in their first week; now it has faded", loc="left", fontsize=9.5, color=INK)

    c_ = f.add_subplot(gs[1, :])
    px = load_bars("TSLA").close
    start = pd.Timestamp(TODAY_START)
    days = pd.bdate_range(start, "2026-11-27")
    ii = {d: k for k, d in enumerate(days)}
    hist = px[px.index >= start - pd.Timedelta(days=21)]
    c_.plot([ii.get(d, np.nan) if d >= start else -(len(pd.bdate_range(d, start)) - 1) for d in hist.index], hist.to_numpy(),
            color=INK, lw=1.8)
    # windows the named moves used, in sessions from their start
    big, top = [], []
    for name, s, e, _ in EPISODES:
        cc = px
        i0, it = cc.index.searchsorted(pd.Timestamp(s)), cc.index.searchsorted(pd.Timestamp(e))
        r5 = np.log(cc.shift(-5) / cc).iloc[i0:it - 4]
        big.append(cc.index.get_loc(r5.idxmax()) - i0)
        top.append(it - i0)
    for vals, lab, col, y in ((big, "strongest 5 sessions began", C3, 0.18), (top, "top", C2, 0.08)):
        y0 = hist.min() * 0.97
        for v in vals:
            c_.scatter(v, y0 + y * (hist.max() - hist.min()), marker="|", s=300, color=col, lw=2)
        c_.annotate(f"{lab}: sessions {min(vals)}-{max(vals)} after start (median {int(np.median(vals))})",
                    (max(vals) + 1, y0 + y * (hist.max() - hist.min())), fontsize=8, color=col, va="center")
    events = [("2026-10-16", "Oct 16\nexpiry"), ("2026-10-22", "Oct 22\nreport"), ("2026-11-03", "Nov 3\nmidterm"),
              ("2026-11-20", "Nov 20\nexpiry")]
    for d, lab in events:
        k = ii[pd.Timestamp(d)]
        c_.axvline(k, color=C1, lw=1, ls=":")
        c_.annotate(lab, (k, 0.98), xycoords=("data", "axes fraction"), xytext=(3, 0), textcoords="offset points", fontsize=8,
                    color=C1, va="top")
    c_.axvline(0, color=INK, lw=0.9)
    ticks = [k for k, d in enumerate(days) if d.weekday() == 0]
    c_.set_xticks(ticks, [days[k].strftime("%b %d") for k in ticks])
    c_.set_xlim(-16, len(days))
    c_.set_ylabel("TSLA")
    c_.set_title("The calendar ahead, counted in sessions from the Sep 29 base: where the named moves had their strongest stretch "
                 "(green) and their top (orange)", loc="left", fontsize=9.5, color=INK)
    f.tight_layout()
    f.savefig(OUT / "tsla_now.png", dpi=150)
    print("saved", OUT / "tsla_now.png", "| strongest-5 starts", sorted(big), "| tops", sorted(top))


if __name__ == "__main__":
    main()
