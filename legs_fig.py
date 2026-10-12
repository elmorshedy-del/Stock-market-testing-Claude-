"""Figures for REPORT 4v: anatomy of the named TSLA legs next to today, the path every leg
takes through (distance above own flip, own gamma percentile), and elections.
Usage: python legs_fig.py      (after legs.py, leg_stages.py, elections.py)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import OUT
from elections import MID, PRES, table as election_table

C1, C2, C3, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0"
SURF = "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "legend.frameon": False})
CASES = [("Oct 2021 (Hertz)", "2021-10-11", "2021-11-04"), ("Jan 2023 (off the bottom)", "2023-01-05", "2023-02-15"),
         ("May 2023", "2023-05-04", "2023-06-20"), ("Jun-Jul 2024", "2024-06-11", "2024-07-10"),
         ("Oct-Nov 2024 (report, red week, election)", "2024-10-23", "2024-11-11"), ("Apr-May 2025 (bounce)", "2025-04-21", "2025-05-27"),
         ("Sep 2025", "2025-08-21", "2025-10-01")]


def anatomy(x):
    f, axs = plt.subplots(2, 4, figsize=(16, 7.4))
    panels = CASES + [("TODAY (to Oct 9 close)", None, None)]
    for a, (name, s, e) in zip(axs.ravel(), panels):
        if s:
            s, e = pd.Timestamp(s), pd.Timestamp(e)
            w = x.loc[s - pd.Timedelta(days=35):e + pd.Timedelta(days=21)]
        else:
            w = x.iloc[-45:]
        spot = w.spot
        flip = spot / (1 + w.flip / 100)
        a.plot(w.index, spot, color=INK, lw=1.6, label="TSLA (option-implied spot)")
        a.plot(w.index, flip, color=C2, lw=1.6, label="own gamma flip")
        a.step(w.index, w.call_wall.rolling(3, min_periods=1).median(), where="post", color=C3, lw=1.3,
               label="call wall (3-day median)")
        if s:
            a.axvspan(s, e, color=C3, alpha=0.08, lw=0)
        for col, mk, colr, lab in (("s2", "o", C1, "lead-in (stage 2)"), ("s3", "^", C3, "wall test (stage 3)"),
                                   ("top", "v", C2, "top signal")):
            d = w.index[w[col].astype(bool)]
            a.scatter(d, spot[d] * (1.025 if col != "top" else 1.045), marker=mk, s=26, color=colr, edgecolor=SURF, lw=0.8,
                      zorder=4, label=lab)
        a.tick_params(axis="x", labelsize=7.5, rotation=0)
        a.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(maxticks=4))
        a.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d\n%Y"))
        a.set_title(name, loc="left", fontsize=9.5, color=C1 if not s else INK, weight="bold" if not s else "normal")
        if not s:
            for sp in a.spines.values():
                sp.set_edgecolor(C1)
            n = w.iloc[-1]
            a.annotate(f"flip {flip.iloc[-1]:.0f}  ·  wall {n.call_wall:.0f}\nown gamma {n.g_pct:.2f}  ·  IV pct {n.iv_pct:.2f}",
                       (0.02, 0.04), xycoords="axes fraction", fontsize=8, color=C1)
    h, l = axs[0, 0].get_legend_handles_labels()
    f.legend(h, l, loc="lower center", ncol=6, fontsize=8, bbox_to_anchor=(0.5, -0.005))
    f.suptitle("TSLA up-legs, underneath: price vs its own gamma flip and largest call strike; green band = the leg. "
               "Same layout for today (blue).", x=0.01, ha="left", fontsize=10.5, color=INK)
    f.tight_layout(rect=(0, 0.04, 1, 1))
    f.savefig(OUT / "legs_anatomy_TSLA.png", dpi=150)


def path_map(x, stages):
    f, (a, b) = plt.subplots(1, 2, figsize=(14, 5.6), gridspec_kw={"width_ratios": [1.6, 1]})
    zones = [((-3, 3), (0, 0.45), "1 base", C2, (-2.8, 0.02, "bottom")), ((3, 10), (0.6, 1.0), "2 lead-in", C1, (3.2, 0.61, "bottom")),
             ((5, 25), (0.75, 1.0), "3 wall test (+ call wall <=2% above)", C3, (10.2, 0.755, "bottom")),
             ((15, 25), (0, 1.0), "top zone\n(+ IV pct >= 0.9)", MUTED, (15.3, 0.30, "bottom"))]
    for (x0, x1), (y0, y1), lab, col, (tx, ty, va) in zones:
        a.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, color=col, alpha=0.07, lw=0))
        a.text(tx, ty, lab, fontsize=8, color=col, va=va)
    for name, s, e in CASES:
        w = x.loc[pd.Timestamp(s) - pd.Timedelta(days=14):pd.Timestamp(e)]
        px, py = w.flip.clip(-15, 25).rolling(3, min_periods=1).mean(), w.g_pct.rolling(3, min_periods=1).mean()
        a.plot(px, py, color=MUTED, lw=1, alpha=0.7)
        a.scatter(px.iloc[0], py.iloc[0], s=18, color=MUTED, zorder=3)
        a.scatter(px.iloc[-1], py.iloc[-1], s=26, marker="s", color=MUTED, zorder=3)
        short = {"Oct 2021": (4, -10), "Jan 2023": (-30, 6), "May 2023": (-12, 6), "Jun-Jul 2024": (-30, 6),
                 "Oct-Nov 2024": (4, -10), "Apr-May 2025": (4, -10), "Sep 2025": (-14, -12)}
        nm = name.split(" (")[0]
        a.annotate(nm, (px.iloc[-1], py.iloc[-1]), xytext=short.get(nm, (3, 3)), textcoords="offset points", fontsize=7, color=MUTED)
    t = x.iloc[-15:]
    px, py = t.flip.clip(-15, 25).rolling(3, min_periods=1).mean(), t.g_pct.rolling(3, min_periods=1).mean()
    a.plot(px, py, color=C1, lw=2.4, label="TSLA last 15 sessions (3-day smoothed)")
    a.scatter(px.iloc[-1], py.iloc[-1], s=60, color=C1, edgecolor=SURF, lw=1.5, zorder=5)
    a.annotate("today", (px.iloc[-1], py.iloc[-1]), xytext=(-34, -4), textcoords="offset points", color=C1, fontsize=9, weight="bold")
    a.set_xlim(-15, 25)
    a.set_ylim(0, 1)
    a.set_xlabel("% above TSLA's own gamma flip")
    a.set_ylabel("own gamma percentile (low = put-heavy, high = call-heavy)")
    a.legend(loc="upper left", fontsize=8)
    a.set_title("Every named leg (gray: dot = 2 weeks before start, square = top) walks from the base\n"
                "at the flip to call-heavy and stretched; today (blue) is in the lead-in zone", loc="left", fontsize=9.5, color=INK)
    ys = np.arange(len(stages))
    b.barh(ys - 0.18, 100 * stages["P(+15% in 15d)"], height=0.34, color=C3, label="+15% within 15 sessions")
    b.barh(ys + 0.18, 100 * stages["P(-10% in 10d)"], height=0.34, color=C2, label="-10% within 10 sessions")
    b.axvline(100 * stages["all days +15%"].iloc[0], color=C3, ls=":", lw=1)
    b.axvline(100 * stages["all days -10%"].iloc[0], color=C2, ls=":", lw=1)
    for y, (u, d) in enumerate(zip(stages["P(+15% in 15d)"], stages["P(-10% in 10d)"])):
        b.annotate(f"{100 * u:.0f}%", (100 * u, y - 0.18), xytext=(3, 0), textcoords="offset points", va="center", fontsize=8)
        b.annotate(f"{100 * d:.0f}%", (100 * d, y + 0.18), xytext=(3, 0), textcoords="offset points", va="center", fontsize=8)
    b.set_yticks(ys, [f"{l}\n({n} episodes)" for l, n in zip(["1 base", "2 lead-in (today)", "3 wall test", "top signal"], stages.episodes)])
    b.invert_yaxis()
    b.set_xlabel("% of episodes (dotted = all days)")
    b.legend(loc="upper right", fontsize=8)
    b.grid(axis="y", visible=False)
    b.set_title("What followed each stage, all days 2021-2026", loc="left", fontsize=9.5, color=INK)
    f.tight_layout()
    f.savefig(OUT / "legs_path_TSLA.png", dpi=150)


def elections_fig():
    E, B, fr = election_table()
    c, v = fr.c, fr.VIX
    f, axs = plt.subplots(1, 2, figsize=(13, 4.6))
    groups = {"presidential, VIX rose >=2 pts into the vote (2016, 2020, 2024)": ([d for d in PRES if E.loc[d, "vix_runup_10d_pts"] >= 2], C2),
              "presidential, no VIX run-up (1992-2012)": ([d for d in PRES if E.loc[d, "vix_runup_10d_pts"] < 2 and d != "2008-11-04"], MUTED),
              "midterms (1994-2022)": (MID, C1)}
    for a, (series, lab) in zip(axs, ((v, "VIX, points vs election-day close"), (np.log(c), "S&P 500, % vs election-day close"))):
        for g, (dates, col) in groups.items():
            paths = []
            for d in dates:
                i = c.index.searchsorted(pd.Timestamp(d))
                seg = series.iloc[i - 10:i + 11].to_numpy()
                paths.append(seg - seg[10] if lab.startswith("VIX") else 100 * (np.exp(seg - seg[10]) - 1))
            p = np.array(paths)
            k = np.arange(-10, 11)
            a.plot(k, p.mean(0), color=col, lw=2.2, label=f"{g} (n={len(dates)})")
            a.fill_between(k, p.min(0), p.max(0), color=col, alpha=0.10, lw=0)
        a.axvline(0, color=INK, lw=0.8)
        a.axhline(0, color=MUTED, lw=0.6)
        a.set_xlabel("sessions from election day")
        a.set_title(lab, loc="left", fontsize=9.5, color=INK)
    axs[0].legend(loc="lower left", fontsize=7.5)
    f.suptitle("Elections release the market when hedges were bought into them: line = average, band = range. "
               "2008 crash excluded from the presidential no-run-up group.", x=0.01, ha="left", fontsize=10, color=INK)
    f.tight_layout()
    f.savefig(OUT / "elections.png", dpi=150)


if __name__ == "__main__":
    x = pd.read_csv(OUT / "legs_daily_TSLA.csv", index_col=0, parse_dates=True)
    from leg_stages import summary
    z = x[x.index >= "2021-01-01"].dropna(subset=["f10", "max15", "min10", "g_pct", "iv_pct"])
    stages = pd.DataFrame([summary(z, z[k], k) for k in ("s1", "s2", "s3", "top")])
    anatomy(x)
    path_map(x, stages)
    elections_fig()
    print("saved legs_anatomy_TSLA.png, legs_path_TSLA.png, elections.png")
