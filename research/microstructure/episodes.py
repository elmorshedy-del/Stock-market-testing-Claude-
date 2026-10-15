"""The TSLA moves named in the conversation, taken as given (start and top picked by hand
from the daily closes, no detection rule), and what TSLA's own options did through each.

Every episode is aligned on its start (the base close it launched from) and cut into
5-session blocks after it (block -k = the k-th 5 sessions before). Each block reports,
at its last session: the block's return, % above TSLA's own gamma flip, own-gamma
percentile (low = put-heavy, high = call-heavy), open interest near the price
(percentile), largest near-term call strike vs price (%), 30-day IV percentile,
call OI change since the start, S&P gamma percentile and DIX percentile.
No cutoffs: values are shown as they are.
Usage: python episodes.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from burst_gamma import state
from common import OUT, load_bars
from forecast import build as spx_frame

plt.rcParams.update({"font.size": 9, "axes.edgecolor": "#52514e", "axes.labelcolor": "#52514e",
                     "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.grid": True, "grid.color": "#e6e5e0",
                     "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "legend.frameon": False})

EPISODES = [  # label, start (base close), top (last high before the roll-over), note
    ("Oct 2021", "2021-10-08", "2021-11-04", "flat base the week before; Hertz day Oct 25"),
    ("Jan 2023", "2023-01-06", "2023-02-15", "off the bottom; burst Jan 9-27, report Jan 25 after close"),
    ("May 2023", "2023-05-15", "2023-06-20", "stair-step, ran 5 weeks"),
    ("Jun-Jul 2024", "2024-06-24", "2024-07-10", "smaller week, then the big week"),
    ("Oct-Nov 2024", "2024-10-23", "2024-11-11", "report, red week, election"),
    ("Apr-May 2025", "2025-04-21", "2025-05-27", "bounce after the crash: big, small, small, big"),
    ("Sep 2025", "2025-09-02", "2025-10-01", "smaller week, then the big week"),
]
TODAY_START = "2026-09-29"          # lowest close of the late-September base
BLOCKS = range(-3, 7)


def panel():
    c = load_bars("TSLA").close
    st = state("TSLA")
    m = pd.read_csv(OUT / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
    spx = spx_frame()
    x = st.join(c.rename("c"), how="inner")
    x["call_oi"] = m.call_oi
    x["spx_gex"] = spx.gex_pct.reindex(x.index).ffill(limit=3)
    x["dix"] = spx.dix_pct.reindex(x.index).ffill(limit=3)
    return x


def blocks(x, start, top=None):
    i0 = x.index.get_loc(x.index[x.index.searchsorted(pd.Timestamp(start))])
    it = x.index.get_loc(x.index[x.index.searchsorted(pd.Timestamp(top))]) if top else None
    rows = []
    for k in BLOCKS:
        a, b = (i0 + 5 * (k - 1), i0 + 5 * k) if k > 0 else (i0 + 5 * k - 5, i0 + 5 * k)
        partial = False
        if b >= len(x) and a < len(x) - 1:          # the running block: use what exists so far
            b, partial = len(x) - 1, True
        if b >= len(x) or a < 0:
            rows.append({"block": k})
            continue
        r = x.iloc[b]
        rows.append({"block": k, "ret_%": 100 * np.log(x.c.iloc[b] / x.c.iloc[a]), "flip_%": r.to_flip_pct, "own_g": r.g_pct,
                     "near_oi": r.near_pct, "wall_gap_%": r.to_call_wall_pct, "iv": r.iv_pct,
                     "call_oi_since_start_%": 100 * np.log(r.call_oi / x.call_oi.iloc[i0]), "spx_gex": r.spx_gex, "dix": r.dix,
                     "past_top": it is not None and b > it, "partial": partial, "date": x.index[b].date()})
    return pd.DataFrame(rows).set_index("block")


def heatmaps(tabs, today):
    specs = [("ret_%", "5-session return, %", "RdYlGn", (-15, 15), "{:+.0f}"),
             ("flip_%", "% above TSLA's own gamma flip", "PuOr_r", (-15, 15), "{:+.0f}"),
             ("own_g", "own gamma percentile (low = put-heavy, high = call-heavy)", "PuOr_r", (0, 1), "{:.2f}"),
             ("near_oi", "open interest near the price, percentile (low = 'freed')", "Greens_r", (0, 1), "{:.2f}"),
             ("wall_gap_%", "largest call strike vs price, % (negative = price above it)", "PuOr", (-15, 15), "{:+.0f}"),
             ("iv", "30-day implied vol percentile", "Purples", (0, 1), "{:.2f}"),
             ("dix", "S&P DIX percentile (dark-pool buying)", "Blues", (0, 1), "{:.2f}")]
    names = [e[0] for e in EPISODES] + ["TODAY"]
    allt = tabs + [today]
    f, axs = plt.subplots(len(specs), 1, figsize=(12.5, 2.05 * len(specs) + 0.8))
    cols = list(BLOCKS)
    for a, (col, title, cmap, (lo, hi), fmt) in zip(axs, specs):
        M = np.array([[t.loc[k, col] if col in t and k in t.index else np.nan for k in cols] for t in allt], dtype=float)
        a.imshow(M, aspect="auto", cmap=cmap, vmin=lo, vmax=hi, alpha=0.75)
        cm = plt.get_cmap(cmap)
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                v = M[i, j]
                if np.isfinite(v):
                    past = bool(allt[i].loc[cols[j], "past_top"]) if "past_top" in allt[i] and cols[j] in allt[i].index else False
                    r, g, b_, _ = cm(np.clip((v - lo) / (hi - lo), 0, 1))
                    r, g, b_ = [1 - 0.75 * (1 - u) for u in (r, g, b_)]          # the 0.75 alpha over a white surface
                    dark = 0.2126 * r + 0.7152 * g + 0.0722 * b_ < 0.52
                    ink = "#fcfcfb" if dark else ("#52514e" if past else "#0b0b0b")
                    a.text(j, i, fmt.format(v), ha="center", va="center", fontsize=7.5, color=ink,
                           style="italic" if past else "normal", weight="bold" if names[i] == "TODAY" else "normal")
        a.set_yticks(range(len(names)), names, fontsize=8)
        for lab in a.get_yticklabels():
            if lab.get_text() == "TODAY":
                lab.set_color("#2a78d6")
                lab.set_weight("bold")
        a.set_xticks(range(len(cols)), [f"{k:+d}" for k in cols], fontsize=8)
        a.axvline(cols.index(1) - 0.5, color="#0b0b0b", lw=1.2)
        a.axhline(len(names) - 1.5, color="#2a78d6", lw=1)
        a.set_title(title, loc="left", fontsize=9, color="#0b0b0b")
        a.grid(False)
        for s in a.spines.values():
            s.set_visible(False)
    axs[-1].set_xlabel("5-session blocks from the start (the black line); italic grey = after that move's top; "
                       "today's block +2 has 3 of 5 sessions so far")
    f.suptitle("TSLA moves you named, aligned on their start, and TSLA's own options underneath (blocks of 5 sessions); "
               "bottom row = the last 9 sessions from the Sep 29 base", x=0.01, ha="left", fontsize=10, color="#0b0b0b")
    f.tight_layout(rect=(0, 0, 1, 0.98))
    f.savefig(OUT / "episodes_TSLA.png", dpi=150)


def daily_overlay(x):
    """Daily paths aligned on each start: own gamma percentile, % above the own flip, IV percentile."""
    specs = [("g_pct", "own gamma percentile (low = put-heavy)"), ("to_flip_pct", "% above TSLA's own gamma flip"),
             ("iv_pct", "30-day implied vol percentile")]
    f, axs = plt.subplots(1, 3, figsize=(15, 4.2))
    for a, (col, title) in zip(axs, specs):
        for name, s, t, _ in EPISODES:
            i0 = x.index.searchsorted(pd.Timestamp(s))
            it = x.index.searchsorted(pd.Timestamp(t))
            w = x[col].iloc[i0 - 15:it + 1]
            k = np.arange(-15, len(w) - 15)
            a.plot(k, w.to_numpy(), color="#52514e", lw=1, alpha=0.5, label="the 7 named moves" if name == EPISODES[0][0] else None)
        i0 = x.index.searchsorted(pd.Timestamp(TODAY_START))
        w = x[col].iloc[i0 - 15:]
        k = np.arange(-15, len(w) - 15)
        a.plot(k, w.to_numpy(), color="#2a78d6", lw=2.6, label="TSLA now (start = Sep 29 base)")
        a.scatter(k[-1], w.iloc[-1], color="#2a78d6", s=40, zorder=5, edgecolor="#fcfcfb", lw=1.5)
        a.axvline(0, color="#0b0b0b", lw=0.9)
        a.set_xlabel("sessions from the start (grey lines run to each move's top)")
        a.set_title(title, loc="left", fontsize=9.5, color="#0b0b0b")
    axs[0].legend(loc="lower right", fontsize=8)
    f.suptitle("Day by day: the named moves (grey) and TSLA now (blue), aligned on the start", x=0.01, ha="left", fontsize=10.5)
    f.tight_layout()
    f.savefig(OUT / "episodes_daily_TSLA.png", dpi=150)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    x = panel()
    tabs = []
    for name, s, t, note in EPISODES:
        b = blocks(x, s, t)
        tabs.append(b)
        b.assign(episode=name).to_csv(OUT / f"episode_{name.replace(' ', '_')}.csv")
        print(f"\n=== {name}: {s} -> {t}  ({note})")
        print(b.drop(columns=["past_top", "partial"]).round(2).to_string())
    today = blocks(x, TODAY_START)
    print(f"\n=== TODAY from {TODAY_START}")
    print(today.drop(columns=["past_top"]).round(2).dropna(subset=["ret_%"]).to_string())
    heatmaps(tabs, today)
    print("saved", OUT / "episodes_TSLA.png")
    daily_overlay(x)
    print("saved", OUT / "episodes_daily_TSLA.png")

