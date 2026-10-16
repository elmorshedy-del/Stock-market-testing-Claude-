"""Follow-up: compare the legs off the owner's lower channel lines (Jan 2023, Apr 2024, Apr 2025, Jul 2026).
Descriptive. Usage: OMP_NUM_THREADS=1 python legs.py -> out/legs.csv, out/legs.png"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import channel_gamma as C

sys.path.insert(0, str(C.MICRO))
os.chdir(C.MICRO)
from forecast import build                         # noqa: E402

LOWS = {"Jan 2023": "2023-01-03", "Apr 2024": "2024-04-22", "Apr 2025": "2025-04-08", "Jul 2026 (now)": "2026-07-29"}
COL = {"Jan 2023": "#eb6834", "Apr 2024": "#2a78d6", "Apr 2025": "#1baf7a", "Jul 2026 (now)": "#0b0b0b"}
r = lambda v, k=0: (round(float(v), k) if v == v else None)


def frame():
    D = C.data()
    g = pd.read_csv(C.MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
    g["iv_pct"] = g.atm_iv_30d.ffill().rolling(252, min_periods=120).rank(pct=True)      # on the full history, not the plotted window
    D = D.join(g[["atm_iv_30d", "iv_pct"]])
    D["cp_ratio"] = D.call_oi / D.put_oi
    c = C.load_bars("TSLA").close
    D["dd_52w"] = 100 * (c / c.rolling(252, min_periods=60).max() - 1).reindex(D.index)
    return D


def table(D):
    spx, F = C.load_bars("^GSPC").close, build()
    bpos = float(((np.log(D["B mid"]) - np.log(D["D lowest"])) / (np.log(D["A upper"]) - np.log(D["D lowest"]))).mean())
    rows, paths = [], {}
    for name, d in LOWS.items():
        i = D.index.searchsorted(pd.Timestamp(d))
        w = D.iloc[i:i + 80]
        lo = w.iloc[0]
        paths[name] = w
        s0, s60 = spx.loc[:w.index[0]].iloc[-1], spx.loc[:w.index[-1]].iloc[-1]
        gx = F.gex_pct.loc[:w.index[0]].dropna()
        rows.append({"leg": name, "low date": str(w.index[0].date()), "low $": r(lo.close, 1),
                     "low vs its 52-week high %": r(lo.dd_52w, 1), "low vs line D %": r(100 * (lo.close / lo["D lowest"] - 1), 1), "low vs flip %": r(lo.dist, 1),
                     "dealer gamma pct at low": r(100 * lo.gpct), "near-OI pct at low": r(100 * lo.near_pct),
                     "ATM IV at low %": r(100 * lo.atm_iv_30d), "IV pct at low": r(100 * lo.iv_pct),
                     "calls/puts OI at low": r(lo.cp_ratio, 2), "calls/puts OI 40 sessions later": r(w.cp_ratio.iloc[min(39, len(w) - 1)], 2),
                     "highest channel position in 80 sessions": r(w.pos.max(), 2), "sessions within 0.08 of the mid line": int(((w.pos - bpos).abs() <= 0.08).sum()),
                     "S&P gamma pct at low": r(100 * gx.iloc[-1]) if len(gx) else None, "S&P over the window %": r(100 * (s60 / s0 - 1), 1),
                     "TSLA 40 sessions after %": r(100 * (w.close.iloc[min(39, len(w) - 1)] / lo.close - 1), 1), "sessions available": len(w)})
    return pd.DataFrame(rows).set_index("leg"), paths, bpos


def figure(paths, bpos):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": C.MUTED, "axes.labelcolor": C.MUTED, "xtick.color": C.MUTED, "ytick.color": C.MUTED,
                         "figure.facecolor": C.SURF, "axes.facecolor": C.SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, axs = plt.subplots(2, 2, figsize=(15, 9), gridspec_kw={"hspace": 0.32, "wspace": 0.22})
    a, b, c, d = axs.ravel()
    for name, w in paths.items():
        x = np.arange(len(w))
        kw = dict(color=COL[name], lw=2.6 if name.startswith("Jan") else 1.8, label=name)
        a.plot(x, w.pos, **kw)
        b.plot(x, w.dist.rolling(3, center=True, min_periods=1).median(), **kw)
        c.plot(x, 100 * w.gpct.rolling(3, center=True, min_periods=1).mean(), **kw)
        d.plot(x, 100 * w.iv_pct.rolling(3, center=True, min_periods=1).mean(), **kw)
    for y, lab in ((0, "D lowest"), (bpos, "B mid"), (1, "A upper")):
        a.axhline(y, color=C.CHAN, lw=1, alpha=0.6)
        a.text(79.5, y, f" {lab}", va="center", fontsize=8, color=C.CHAN)
    a.set_ylabel("position in your channel (D = 0, A = 1)")
    a.set_title("1. Path through the channel after each low", loc="left", fontsize=10, color=C.INK)
    a.legend(loc="upper left", frameon=False, fontsize=8.5)
    b.axhline(0, color=C.INK, lw=0.8)
    b.set_ylabel("price vs flip %")
    b.set_title("2. Distance from the gamma flip (below 0 = dealers short gamma)", loc="left", fontsize=10, color=C.INK)
    c.axhspan(200 / 3, 100, color=C.ORANGE, alpha=0.08, lw=0)
    c.axhspan(0, 100 / 3, color=C.BLUE, alpha=0.08, lw=0)
    c.set_ylim(0, 100)
    c.set_ylabel("dealer gamma pct")
    c.set_title("3. Dealer gamma vs its own year", loc="left", fontsize=10, color=C.INK)
    d.set_ylim(0, 100)
    d.set_ylabel("ATM implied vol, pct of its year")
    d.set_title("4. Implied volatility vs its own year", loc="left", fontsize=10, color=C.INK)
    for ax in axs.ravel():
        ax.set_xlabel("sessions after the low")
        ax.set_xlim(0, 79)
    f.suptitle("Legs off your lower lines: Jan 2023 (thick orange) against Apr 2024, Apr 2025 and the current leg from Jul 2026",
               x=0.01, ha="left", fontsize=11.5, color=C.INK, weight="bold")
    f.savefig(C.OUT / "legs.png", dpi=145, bbox_inches="tight", facecolor=C.SURF)


if __name__ == "__main__":
    D = frame()
    T, paths, bpos = table(D)
    T.T.to_csv(C.OUT / "legs.csv")
    figure(paths, bpos)
    pd.set_option("display.width", 220)
    print(f"mid line B = channel position {bpos:.2f}")
    print(T.T.to_string())
