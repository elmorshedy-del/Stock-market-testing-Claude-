"""The owner's weekly TSLA channel against the options state (design in README.md, committed at 0b4c614).
Usage: OMP_NUM_THREADS=1 python channel_gamma.py -> out/channel_gamma.png, out/zones.csv, out/legs.csv
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
sys.path.insert(0, str(MICRO))
from burst_gamma import state                      # noqa: E402  (originals, imported unchanged)
from common import load_bars                       # noqa: E402
from own_multiverse import within                  # noqa: E402
from stock_now import burst_days                   # noqa: E402

LINES = {"A upper": ((2022.655, 179), (2027.188, 656)), "B mid": ((2022.931, 156), (2027.456, 571)),
         "C second lowest": ((2022.983, 129), (2028.484, 578)), "D lowest": ((2022.421, 103), (2028.207, 497))}
START, END = "2022-08-01", "2026-10-15"
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
CHAN = "#3b5bdb"


def yearfrac(idx):
    return idx.year + (idx.dayofyear - 1) / 365.25


def line(idx, key):
    (x1, p1), (x2, p2) = LINES[key]
    return np.exp(np.log(p1) + (np.log(p2) - np.log(p1)) * (yearfrac(idx) - x1) / (x2 - x1))


def data():
    g = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
    g = g.join(state("TSLA")[["near_pct"]])
    c = load_bars("TSLA").close
    c = c[(c.index >= "2021-01-01") & (c.index <= END)]
    D = pd.DataFrame({"close": c})
    D = D.join(g[["spot", "flip_classic", "gex_classic", "call_oi", "put_oi", "near_pct"]])
    f = (D.spot / D.close).round().clip(lower=1)
    D["flip"] = D.flip_classic / f
    D["dist"] = 100 * (D.close / D.flip - 1)
    gn = D.gex_classic / (D.spot * (D.call_oi + D.put_oi) * 100)
    D["gpct"] = gn.rolling(252, min_periods=120).rank(pct=True)
    D["up10"] = within(burst_days(c, 1), 10)
    lc = np.log(D.close)
    D["fwd20"] = lc.shift(-20) - lc
    D = D[D.index >= START]
    for k in LINES:
        D[k] = line(D.index, k)
    a, d = np.log(D["A upper"]), np.log(D["D lowest"])
    D["pos"] = (np.log(D.close) - d) / (a - d)
    cuts = [-np.inf, 0, ((np.log(D["C second lowest"]) - d) / (a - d)).mean(), ((np.log(D["B mid"]) - d) / (a - d)).mean(), 1, np.inf]
    D["zone"] = pd.cut(D.pos, cuts, labels=["below D (lowest)", "D-C lower band", "C to B (lower half)", "B to A (upper half)", "above A (upper)"])
    return D


def zones(D):
    rows = []
    for z, x in D.groupby("zone", observed=True):
        rows.append({"zone": z, "days": len(x), "share below flip %": 100 * (x.dist < 0).mean(), "median % vs flip": x.dist.median(),
                     "median dealer-gamma pct": 100 * x.gpct.median(), "median near-OI pct": 100 * x.near_pct.median(),
                     "share freed %": 100 * (x.near_pct <= 1 / 3).mean(), "up-burst within 10 % (in-sample)": 100 * x.up10.mean(),
                     "next-20-session return % (in-sample)": 100 * x.fwd20.mean()})
    return pd.DataFrame(rows)


def figure(D, Z):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f = plt.figure(figsize=(16, 15))
    gs = f.add_gridspec(5, 1, height_ratios=[3.2, 1.1, 1, 1, 1.6], hspace=0.2)
    ax, ad, ag, an = (f.add_subplot(gs[i]) for i in range(4))
    zb = f.add_subplot(gs[4])
    d = D.index
    for k, lw in zip(LINES, (2.2, 1.6, 1.6, 2.2)):
        ax.plot(d, D[k], color=CHAN, lw=lw, alpha=0.75)
        ax.text(d[-1] + pd.Timedelta(days=6), D[k].iloc[-1], f"{k.split()[0]}  ${D[k].iloc[-1]:.0f}", va="center", fontsize=8.5, color=CHAN)
    ax.semilogy(d, D.close, color=INK, lw=1.6)
    ax.set_yticks([100, 150, 200, 300, 400, 500, 600], ["100", "150", "200", "300", "400", "500", "600"])
    ax.minorticks_off()
    ax.set_ylabel("TSLA (log)")
    ax.set_title("Your channel (reconstructed from the screenshot): A upper, B mid, C and D the lower pair", loc="left", fontsize=10, color=INK)
    dist = D.dist.rolling(3, center=True, min_periods=1).median()
    ad.fill_between(d, 0, dist, where=dist < 0, color=BLUE, alpha=0.35, lw=0, interpolate=True)
    ad.fill_between(d, 0, dist, where=dist >= 0, color=ORANGE, alpha=0.25, lw=0, interpolate=True)
    ad.axhline(0, color=INK, lw=0.8)
    ad.set_ylabel("price vs flip %")
    ad.set_ylim(-25, 35)
    ad.text(d[3], 28, "orange = above the flip (dealers long gamma)   blue = below it (short gamma)", fontsize=8, color=MUTED)
    gp = (100 * D.gpct).rolling(5, center=True, min_periods=1).mean()
    ag.axhspan(0, 100 / 3, color=BLUE, alpha=0.08, lw=0)
    ag.axhspan(200 / 3, 100, color=ORANGE, alpha=0.08, lw=0)
    ag.plot(d, gp, color=INK, lw=1.4)
    ag.set_ylim(0, 100)
    ag.set_ylabel("dealer gamma pct")
    npct = (100 * D.near_pct).rolling(5, center=True, min_periods=1).mean()
    an.axhspan(0, 100 / 3, color=GREEN, alpha=0.12, lw=0)
    an.plot(d, npct, color=GREEN, lw=1.4)
    an.set_ylim(0, 100)
    an.set_ylabel("near-price OI pct\n(green band = freed)")
    for axx in (ax, ad, ag, an):
        axx.set_xlim(d[0], d[-1] + pd.Timedelta(days=70))
        axx.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
        axx.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        axx.grid(axis="x", color=GRID, lw=0.6)
    for axx in (ax, ad, ag):
        axx.tick_params(labelbottom=False)
    Zs = Z.set_index("zone")
    order = list(Zs.index)[::-1]
    y = np.arange(len(order))
    zb.barh(y + 0.2, Zs.loc[order, "share below flip %"], height=0.38, color=BLUE, label="share of days below the flip")
    zb.barh(y - 0.2, Zs.loc[order, "median dealer-gamma pct"], height=0.38, color=ORANGE, alpha=0.8, label="median dealer-gamma percentile")
    for yy, z in zip(y, order):
        r = Zs.loc[z]
        zb.text(max(r["share below flip %"], r["median dealer-gamma pct"]) + 1.5, yy,
                f"{int(r.days)} days · freed {r['share freed %']:.0f}% of them · next 20 sessions {r['next-20-session return % (in-sample)']:+.1f}% (in-sample)",
                va="center", fontsize=8, color=INK)
    zb.set_yticks(y, order)
    zb.set_xlim(0, 175)
    zb.set_xlabel("%")
    zb.legend(loc="lower right", frameon=False, fontsize=8)
    zb.set_title("By channel zone: the lower lines are where TSLA sits below the flip with gamma at its most negative; the upper half is long-gamma territory",
                 loc="left", fontsize=10, color=INK, pad=26)
    f.suptitle("TSLA in your channel, Aug 2022 - Oct 2026, with the options state underneath (lines lightly smoothed for display)",
               x=0.01, ha="left", fontsize=12, color=INK, weight="bold", y=0.91)
    f.savefig(OUT / "channel_gamma.png", dpi=140, bbox_inches="tight", facecolor=SURF)


def main():
    OUT.mkdir(exist_ok=True)
    D = data()
    Z = zones(D)
    Z.to_csv(OUT / "zones.csv", index=False)
    figure(D, Z)
    return D, Z


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 20)
    D, Z = main()
    print(Z.round(1).to_string(index=False))
    print("\nnow:", D.iloc[-1][["close", "A upper", "B mid", "C second lowest", "D lowest", "pos", "zone", "dist", "gpct", "near_pct"]].to_dict())
