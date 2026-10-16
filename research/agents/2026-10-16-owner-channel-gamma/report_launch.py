"""Follow-up (descriptive, written after seeing the legs): every TSLA earnings reaction since Aug 2022, by where it sat in
the owner's channel and against the gamma flip, plus the 2026 map into the Oct 21 report.
Usage: OMP_NUM_THREADS=1 python report_launch.py -> out/reports.csv, out/report_launch.png"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import channel_gamma as C

sys.path.insert(0, str(C.MICRO))
os.chdir(C.MICRO)
from stock_now import burst_days                   # noqa: E402
from tsla_eras import REACTIONS_2020               # noqa: E402

# Next-session reactions to the 2026 reports (Q4 2025 on Jan 28, Q1 on Apr 22, Q2 on Jul 22, all after the close).
# The volume detector in q4_forensics picks Apr 15 for Q1 2026, which is not a report day, so the dates are listed here.
REACTIONS_2026 = ["2026-01-29", "2026-04-23", "2026-07-23"]
NEXT = pd.Timestamp("2026-10-22")                  # reaction session to the Q3 2026 report (Wed Oct 21, after the close)
LIVE = (pd.Timestamp("2026-10-16"), 364.7)         # Yahoo, Oct 16 session, before the after-close refresh
FLIP_BAND = (348, 356)                             # post-expiry flip estimate; recompute Monday with real OI (tsla_live.py)
r1 = lambda v: round(float(v), 1)


def frame():
    D = C.data()
    D["full"] = (D.near_pct <= 1 / 3) & (D.dist < 0)
    c = C.load_bars("TSLA").close
    D["up"] = pd.Series(burst_days(c, 1), index=c.index).reindex(D.index).fillna(False).astype(bool)
    return D, c


def reports(D, c):
    rows = []
    for t in map(pd.Timestamp, REACTIONS_2020 + REACTIONS_2026):
        if not D.index[0] < t <= D.index[-1]:
            continue
        i, j = D.index.get_loc(t), c.index.get_loc(t)
        p = D.iloc[i - 1]
        rows.append({"reaction day": t.date(), "close before $": r1(p.close), "channel position before": round(float(p.pos), 2),
                     "vs line D before %": r1(100 * (p.close / p["D lowest"] - 1)), "vs flip before %": r1(p.dist),
                     "full setup at the close before": bool(p.full), "full-setup days in the 10 before": int(D.full.iloc[i - 10:i].sum()),
                     "reaction day %": r1(100 * (c.iloc[j] / c.iloc[j - 1] - 1)), "up-burst": bool(D.up.iloc[i]),
                     "20 sessions later %": r1(100 * (c.iloc[min(j + 19, len(c) - 1)] / c.iloc[j - 1] - 1)),
                     "highest channel position in the next 60": round(float(D.pos.iloc[i:i + 60].max()), 2),
                     "sessions after": int(min(len(c) - 1 - j + 1, 60))})
    return pd.DataFrame(rows)


def figure(D, R):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": C.MUTED, "axes.labelcolor": C.MUTED, "xtick.color": C.MUTED, "ytick.color": C.MUTED,
                         "figure.facecolor": C.SURF, "axes.facecolor": C.SURF, "axes.spines.top": False, "axes.spines.right": False})
    f = plt.figure(figsize=(16, 13.5))
    gs = f.add_gridspec(2, 2, height_ratios=[1, 1.25], hspace=0.3, wspace=0.18)
    a, b, m = f.add_subplot(gs[0, 0]), f.add_subplot(gs[0, 1]), f.add_subplot(gs[1, :])
    now_pos = float((np.log(LIVE[1]) - np.log(C.line(pd.DatetimeIndex([LIVE[0]]), "D lowest")[0]))
                    / (np.log(C.line(pd.DatetimeIndex([LIVE[0]]), "A upper")[0]) - np.log(C.line(pd.DatetimeIndex([LIVE[0]]), "D lowest")[0])))
    bpos = float(((np.log(D["B mid"]) - np.log(D["D lowest"])) / (np.log(D["A upper"]) - np.log(D["D lowest"]))).mean())

    # 1. every report: position before vs the next 20 sessions
    a.axvspan(-0.45, bpos, color=C.BLUE, alpha=0.06, lw=0)
    a.axhline(0, color=C.INK, lw=0.8)
    for x, lab in ((0, "D"), (bpos, "B"), (1, "A")):
        a.axvline(x, color=C.CHAN, lw=1, alpha=0.5)
        a.text(x, 66, lab, ha="center", fontsize=8.5, color=C.CHAN)
    for _, row in R.iterrows():
        x, y, ring = row["channel position before"], row["20 sessions later %"], row["full setup at the close before"]
        a.scatter(x, y, s=80 if ring else 46, color=C.GREEN if y > 0 else C.ORANGE, edgecolor=C.INK if ring else "none", lw=1.4, zorder=4)
        a.text(x + 0.025, y, pd.Timestamp(row["reaction day"]).strftime("%b %y"), fontsize=7.5, color=C.INK, va="center")
    a.axvline(now_pos, color=C.INK, ls="--", lw=1.2)
    a.text(now_pos + 0.02, -38, f"now\n({now_pos:.2f})", fontsize=8, color=C.INK)
    lo, hi = R[R["channel position before"] < bpos], R[R["channel position before"] >= bpos]          # split at your mid line B
    a.text(0.17, -22, f"below the mid line B: {(lo['20 sessions later %'] > 0).sum()} of {len(lo)} up\nmedian {lo['20 sessions later %'].median():+.0f}%",
           fontsize=8.5, color=C.INK, va="top")
    a.text(1.62, 66, f"above it: {(hi['20 sessions later %'] > 0).sum()} of {len(hi)} up\nmedian {hi['20 sessions later %'].median():+.0f}%",
           fontsize=8.5, color=C.INK, va="top", ha="right")
    a.set_xlim(-0.45, 1.65)
    a.set_ylim(-42, 70)
    a.set_xlabel("channel position at the close before the report (D = 0, A = 1)")
    a.set_ylabel("TSLA over the 20 sessions from that close, %")
    a.set_title("1. Every report since Aug 2022: green = up 20 sessions on, ring = full setup", loc="left", fontsize=10, color=C.INK)

    # 2. the five reports closest to line D, aligned on the reaction day
    keep = {"2024-10-24": (C.BLUE, "Oct 2024 (Q3, catch-up year)"), "2025-04-23": (C.GREEN, "Apr 2025"),
            "2026-07-23": (C.ORANGE, "Jul 2026 (failed)"), "2023-01-26": ("#8a5cc2", "Jan 2023"), "2024-04-24": ("#c2a35c", "Apr 2024")}
    for d, (col, lab) in keep.items():
        i = D.index.get_loc(pd.Timestamp(d))
        w = D.iloc[max(i - 40, 0):i + 41]
        b.plot(np.arange(len(w)) - (i - max(i - 40, 0)), w.pos, color=col, lw=1.8, label=lab)
    k_now = -int(np.busday_count(LIVE[0].date(), NEXT.date()))
    i_now = len(D)
    w = D.iloc[i_now - 37:]
    xs = np.arange(len(w)) - len(w) + k_now
    b.plot(np.append(xs, k_now), np.append(w.pos.to_numpy(), now_pos), color=C.INK, lw=2.6, label="now (Oct 2026)")
    for y, lab in ((0, "D"), (bpos, "B mid"), (1, "A upper")):
        b.axhline(y, color=C.CHAN, lw=1, alpha=0.5)
        b.text(40.5, y, f" {lab}", va="center", fontsize=8, color=C.CHAN)
    b.axvline(0, color=C.MUTED, ls=":", lw=1)
    b.text(0.5, 1.5, "report reaction day", fontsize=8, color=C.MUTED)
    b.set_xlim(-40, 40)
    b.set_ylim(-0.45, 1.7)
    b.set_xlabel("sessions from the report reaction day")
    b.set_ylabel("channel position")
    b.legend(loc="upper left", frameon=False, fontsize=8)
    b.set_title("2. The five reports closest to line D, aligned on the report", loc="left", fontsize=10, color=C.INK)

    # 3. the 2026 map with the lines carried to year end
    z = D[D.index >= "2026-05-15"]
    ext = pd.bdate_range(z.index[-1] + pd.Timedelta(days=1), "2026-12-31")
    full_idx = z.index.append(ext)
    for k in C.LINES:
        m.plot(full_idx, C.line(full_idx, k), color=C.CHAN, lw=1.8 if k[0] in "AD" else 1.3, alpha=0.75)
        m.text(full_idx[-1] + pd.Timedelta(days=3), C.line(full_idx[-1:], k)[0], f"{k.split()[0]}  ${C.line(full_idx[-1:], k)[0]:.0f}",
               va="center", fontsize=8.5, color=C.CHAN)
    fl = z.flip.rolling(3, center=True, min_periods=1).median()
    ok = fl.notna().to_numpy()
    m.fill_between(z.index, z.close, fl, where=ok & (z.close < fl).to_numpy(), interpolate=True, color=C.BLUE, alpha=0.28, lw=0)
    m.fill_between(z.index, z.close, fl, where=ok & (z.close >= fl).to_numpy(), interpolate=True, color=C.ORANGE, alpha=0.14, lw=0)
    m.plot(z.index, fl, color=C.ORANGE, lw=2)
    m.plot(z.index, z.close, color=C.INK, lw=2.2)
    m.plot([z.index[-1], LIVE[0]], [z.close.iloc[-1], LIVE[1]], color=C.INK, lw=2.2)
    fs = z[z.full]
    m.scatter(fs.index, fs.close * 0.965, marker="s", s=14, color=C.BLUE, zorder=5)
    ups = z[z.up]
    m.scatter(ups.index, ups.close * 1.035, marker="^", s=34, color=C.GREEN, zorder=5)
    m.fill_between([LIVE[0], NEXT + pd.Timedelta(days=6)], *FLIP_BAND, color=C.ORANGE, alpha=0.35, lw=0)
    m.annotate(f"post-expiry flip ~${FLIP_BAND[0]}-{FLIP_BAND[1]}\n(estimate; recompute with real OI Monday)", xy=(LIVE[0], FLIP_BAND[0]),
               xytext=(pd.Timestamp("2026-09-25"), 296), fontsize=8, color=C.ORANGE, ha="center",
               arrowprops=dict(arrowstyle="-", color=C.ORANGE, lw=1))
    m.scatter([LIVE[0]], [LIVE[1]], s=36, color=C.INK, zorder=6)
    m.text(LIVE[0] - pd.Timedelta(days=2), LIVE[1] * 1.045, f"Oct 16 ${LIVE[1]:.0f}", ha="right", fontsize=8.5, color=C.INK)
    for t, lab in ((pd.Timestamp("2026-07-23"), "Q2 report\n-14.5%"), (NEXT, "Q3 report\nWed Oct 21")):
        m.axvline(t, color=C.MUTED, ls=":", lw=1.2)
        m.text(t + pd.Timedelta(days=1), 640, lab, fontsize=8.5, color=C.INK, va="top")
    land = NEXT + pd.offsets.BDay(19)
    pts = sorted((LIVE[1] * (1 + row["20 sessions later %"] / 100), row) for _, row in lo.iterrows() if row["sessions after"] >= 20)
    ly = []
    for y, _ in pts:                                # spread labels that would overlap (display only; dots stay exact)
        ly.append(max(y, ly[-1] * 1.03) if ly else y)
    for (y, row), yl in zip(pts, ly):
        v = row["20 sessions later %"]
        m.scatter([land], [y], s=30, color=C.GREEN if v > 0 else C.ORANGE, zorder=6)
        m.text(land + pd.Timedelta(days=3), yl, f"{pd.Timestamp(row['reaction day']):%b %y} {v:+.0f}%", fontsize=7.5, color=C.INK, va="center")
    m.text(land, 245, "where the 20-session moves after the\nreports below the mid line would land\n(from today's price; not a forecast)",
           ha="center", fontsize=8, color=C.MUTED)
    m.set_yscale("log")
    m.set_yticks([250, 300, 350, 400, 450, 500, 600], ["250", "300", "350", "400", "450", "500", "600"])
    m.minorticks_off()
    m.set_ylim(235, 660)
    m.set_xlim(z.index[0], full_idx[-1] + pd.Timedelta(days=28))
    m.xaxis.set_major_locator(mdates.MonthLocator())
    m.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    m.set_ylabel("TSLA (log)")
    m.set_title("3. 2026 in your channel: blue squares = full-setup closes, green triangles = up-bursts, blue fill = below the flip",
                loc="left", fontsize=10, color=C.INK)
    f.suptitle("The launches off your lower lines came on earnings reports. The Q3 report on Oct 21 is the first since the July low at D.",
               x=0.01, ha="left", fontsize=12, color=C.INK, weight="bold", y=0.935)
    f.savefig(C.OUT / "report_launch.png", dpi=140, bbox_inches="tight", facecolor=C.SURF)


if __name__ == "__main__":
    D, c = frame()
    R = reports(D, c)
    R.to_csv(C.OUT / "reports.csv", index=False)
    figure(D, R)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 20)
    print(R.to_string(index=False))
