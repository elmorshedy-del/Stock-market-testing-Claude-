"""Today vs the run-up to past up-bursts, using the stock's own option positioning.

Figure 1 (event study): the 30 sessions before every up-burst since 2021 (median and
interquartile band) for near-money OI percentile, own-gamma percentile, % above the own
gamma flip, 30-day IV percentile and the price path, with the last 30 sessions overlaid
as if a burst came next session.
Figure 2 (fingerprint): the day-before state of the bursts named in the conversation,
side by side with today. Cells are coloured only where the studies found an effect
(4s/4t: near-money OI, put-heaviness, flip side; 4p/4j: S&P gamma).
Usage: python burst_compare.py TSLA
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from burst_gamma import events, state
from common import OUT, load_bars
from forecast import build as spx_frame
from q4_forensics import calendar

C1, C2, C3, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0"
SURF = "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "legend.frameon": False})
NAMED = {"2024-06-17": "Jun '24", "2024-07-01": "Jul '24 (call-wall break)", "2024-10-24": "Oct '24 report (Q4)",
         "2024-11-06": "Nov '24 election (Q4)", "2025-04-23": "Apr '25 report", "2025-05-12": "May '25",
         "2025-05-27": "late May '25", "2025-09-11": "Sep '25", "2025-10-06": "Oct '25 a", "2025-10-13": "Oct '25 b",
         "2025-11-24": "Nov '25"}
W = 30


def panel_data(sym):
    s = state(sym)
    c = load_bars(sym).close
    s["path"] = 100 * (c.reindex(s.index) / c.reindex(s.index).shift(W) - 1)   # used only for today's baseline
    e, _ = events(sym)
    idx = s.index
    rows = []
    for b in pd.to_datetime(e.burst):
        i = idx.searchsorted(b)
        if i - W < 0:
            continue
        w = s.iloc[i - W:i]
        p = c.reindex(w.index)
        rows.append(pd.DataFrame({"k": np.arange(-W, 0), "near_pct": w.near_pct.to_numpy(), "g_pct": w.g_pct.to_numpy(),
                                  "to_flip_pct": w.to_flip_pct.to_numpy(), "iv_pct": w.iv_pct.to_numpy(),
                                  "path": 100 * (p.to_numpy() / p.iloc[0] - 1), "burst": b}))
    ev = pd.concat(rows)
    now = s.iloc[-W:]
    pn = c.reindex(now.index)
    today = pd.DataFrame({"k": np.arange(-W, 0), "near_pct": now.near_pct.to_numpy(), "g_pct": now.g_pct.to_numpy(),
                          "to_flip_pct": now.to_flip_pct.to_numpy(), "iv_pct": now.iv_pct.to_numpy(),
                          "path": 100 * (pn.to_numpy() / pn.iloc[0] - 1)})
    base = s[s.index >= "2021-01-01"]
    return ev, today, base, e, s


def fig_paths(sym, ev, today, base):
    specs = [("near_pct", "open interest near the price\n(percentile; low = 'freed')", (0, 1)),
             ("g_pct", "own gamma percentile\n(low = put-heavy)", (0, 1)),
             ("to_flip_pct", "% above own gamma flip", None),
             ("iv_pct", "30-day implied vol percentile", (0, 1)),
             ("path", f"{sym} price, % from 30 sessions before", None)]
    f, ax = plt.subplots(1, len(specs), figsize=(15, 3.9))
    q = ev.groupby("k")
    for a, (col, lab, lim) in zip(ax, specs):
        med, lo, hi = q[col].median(), q[col].quantile(0.25), q[col].quantile(0.75)
        a.fill_between(med.index, lo, hi, color=C3, alpha=0.18, lw=0, label="middle half of past bursts")
        a.plot(med.index, med, color=C3, lw=2, label=f"median of {ev.burst.nunique()} up-bursts")
        if col != "path":
            a.axhline(base[col].median(), color=MUTED, lw=1, ls=":", label="typical day")
        else:
            a.axhline(0, color=MUTED, lw=0.8)
        a.plot(today.k, today[col], color=C1, lw=2.4, label="last 30 sessions (to Oct 9)")
        a.scatter([today.k.iloc[-1]], [today[col].iloc[-1]], color=C1, s=36, zorder=4, edgecolor=SURF, lw=1.5)
        a.annotate(f"now\n{today[col].iloc[-1]:.2f}" if lim else f"now\n{today[col].iloc[-1]:+.1f}",
                   (today.k.iloc[-1], today[col].iloc[-1]), xytext=(6, 0), textcoords="offset points", ha="left",
                   va="center", fontsize=8, color=C1)
        a.set_xlim(-31, 5)
        if lim:
            a.set_ylim(*lim)
        a.set_xlabel("sessions before the burst")
        a.set_title(lab, loc="left", fontsize=9, color=INK)
    h, l = ax[0].get_legend_handles_labels()
    f.legend(h, l, loc="lower center", ncol=4, fontsize=8, bbox_to_anchor=(0.5, -0.01))
    f.suptitle(f"{sym}: the run-up to past up-bursts (green) vs the last 30 sessions (blue), "
               "drawn as if a burst came next session", x=0.01, ha="left", fontsize=10.5, color=INK)
    f.tight_layout(rect=(0, 0.06, 1, 1))
    f.savefig(OUT / f"burst_compare_paths_{sym}.png", dpi=150)


def fingerprint(sym, e, s):
    spx = spx_frame()
    c = load_bars(sym).close
    spy = load_bars("SPY").close.reindex(c.index).ffill()
    cal = calendar(c.index.append(pd.DatetimeIndex([c.index[-1] + pd.offsets.BDay(1)])))

    def ytd_gap(t):
        y0 = c[:f"{t.year - 1}-12-31"].iloc[-1]
        s0 = spy[:f"{t.year - 1}-12-31"].iloc[-1]
        return 100 * (np.log(c[t] / y0) - np.log(spy[t] / s0))

    rows, labels = [], []
    for d, lab in NAMED.items():
        b = pd.Timestamp(d)
        i = c.index.get_loc(b)
        prev = c.index[i - 1]
        r = e[e.burst.astype(str) == d]
        rows.append({"move": f"+{float(r.move_2d.iloc[0]):.0f}% 2d" if len(r) else "", "prev": prev, "burst_day": b})
        labels.append(f"{lab}  {b:%Y-%m-%d}")
    nxt = c.index[-1] + pd.offsets.BDay(1)
    rows.append({"move": "?", "prev": c.index[-1], "burst_day": nxt})
    labels.append(f"TODAY (Oct 9 close), next session {nxt:%a %b %d}")
    out = []
    for r in rows:
        p = r["prev"]
        st = s.loc[p]
        out.append({"near-money OI pct": st.near_pct, "own gamma pct": st.g_pct, "% vs own flip": st.to_flip_pct,
                    "% to call wall": st.to_call_wall_pct, "30d IV pct": st.iv_pct,
                    "20d return %": 100 * np.log(c[p] / c.iloc[c.index.get_loc(p) - 20]),
                    "YTD vs SPY (pts)": ytd_gap(p), "S&P gamma pct": spx.gex_pct.asof(p), "S&P DIX pct": spx.dix_pct.asof(p),
                    "sessions to opex": cal.tdays_to_opex.get(r["burst_day"], np.nan), "weekday": r["burst_day"].strftime("%a"),
                    "burst": r["move"]})
    t = pd.DataFrame(out, index=labels)
    # similarity to today on the positioning/price measures, each scaled by its spread across all days
    keys = ["near-money OI pct", "own gamma pct", "% vs own flip", "30d IV pct", "20d return %"]
    allv = pd.DataFrame({"near-money OI pct": s.near_pct, "own gamma pct": s.g_pct, "% vs own flip": s.to_flip_pct,
                         "30d IV pct": s.iv_pct, "20d return %": 100 * np.log(c / c.shift(20)).reindex(s.index)})
    sd = allv[allv.index >= "2021-01-01"].std()
    d = (((t[keys] - t[keys].iloc[-1]) / sd) ** 2).sum(axis=1) ** 0.5
    t["distance to today"] = d

    def tone(col, v):        # +1 favours an up-burst, -1 against, 0 no tested effect / neutral
        if not np.isfinite(v) if isinstance(v, float) else False:
            return 0
        if col == "near-money OI pct":
            return 1 if v <= 1 / 3 else (-1 if v >= 2 / 3 else 0)
        if col == "own gamma pct":
            return -1 if v <= 1 / 3 else 0
        if col == "% vs own flip":
            return -1 if v < 0 else 0
        if col == "S&P gamma pct":
            return 1 if v <= 0.30 else (-1 if v >= 0.90 else 0)
        if col == "weekday":
            return 1 if v == "Mon" else 0
        return 0

    cols = list(t.columns)
    f, a = plt.subplots(figsize=(16, 0.42 * len(t) + 1.6))
    a.set_xlim(0, len(cols))
    a.set_ylim(len(t), 0)
    a.axis("off")
    fills = {1: "#cdeee0", -1: "#fbd9c8", 0: SURF}
    for i, (lab, row) in enumerate(t.iterrows()):
        today_row = lab.startswith("TODAY")
        for j, col in enumerate(cols):
            v = row[col]
            tn = tone(col, v)
            a.add_patch(plt.Rectangle((j + 0.03, i + 0.06), 0.94, 0.88, color=fills[tn], lw=0))
            if today_row:
                a.add_patch(plt.Rectangle((j + 0.03, i + 0.06), 0.94, 0.88, fill=False, edgecolor=C1, lw=1.6))
            txt = v if isinstance(v, str) else (f"{v:.2f}" if "pct" in col or col == "distance to today" else
                                                 f"{v:+.1f}" if "%" in col or "pts" in col else f"{v:.0f}")
            if col == "distance to today" and today_row:
                txt = "-"
            a.text(j + 0.5, i + 0.5, txt, ha="center", va="center", fontsize=8.5, color=INK, weight="bold" if today_row else "normal")
        a.text(-0.08, i + 0.5, lab, ha="right", va="center", fontsize=8.5, color=C1 if today_row else INK,
               weight="bold" if today_row else "normal")
    heads = {"near-money OI pct": "OI near price\n(low = freed)", "own gamma pct": "own gamma\n(low = put-heavy)",
             "% vs own flip": "% vs own\ngamma flip", "% to call wall": "% to\ncall wall", "30d IV pct": "30d IV\npct",
             "20d return %": "20-day\nreturn %", "YTD vs SPY (pts)": "YTD vs SPY\n(pts)", "S&P gamma pct": "S&P gamma\npct",
             "S&P DIX pct": "S&P DIX\npct", "sessions to opex": "sessions to\nmonthly opex", "weekday": "burst\nweekday",
             "burst": "burst\n(2-day)", "distance to today": "distance\nto today"}
    for j, col in enumerate(cols):
        a.text(j + 0.5, -0.12, heads.get(col, col), ha="center", va="bottom", fontsize=8, color=MUTED)
    a.set_title(f"{sym}: the day before each up-burst you named vs today. Green = condition that favoured up-bursts in the tests, "
                "orange = against, blank = no tested effect", loc="left", fontsize=10, color=INK, pad=34)
    f.subplots_adjust(left=0.2, right=0.995, top=0.84, bottom=0.02)
    f.savefig(OUT / f"burst_compare_table_{sym}.png", dpi=150)
    return t


if __name__ == "__main__":
    sym = (sys.argv[1:] or ["TSLA"])[0]
    ev, today, base, e, s = panel_data(sym)
    fig_paths(sym, ev, today, base)
    t = fingerprint(sym, e, s)
    pd.set_option("display.width", 250)
    print(t.round(2).to_string())
    q = ev.groupby("k")
    print("\nmedian path of past bursts at -1 / -5 / -10 / -20:")
    print(q[["near_pct", "g_pct", "to_flip_pct", "iv_pct", "path"]].median().loc[[-20, -10, -5, -1]].round(2).to_string())
    print("today at the same offsets:")
    print(today.set_index("k").loc[[-20, -10, -5, -1], ["near_pct", "g_pct", "to_flip_pct", "iv_pct", "path"]].round(2).to_string())
