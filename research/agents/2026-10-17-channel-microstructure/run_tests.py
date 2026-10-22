"""T1-T3 of the channel thesis (README.md, pre-registered at a9b309f).
T1: are rolling cost-basis lines (rolling VWAP) respected more than placebo curves of the same shape?
T2: at VWAP(200) touches, does the options state (own flip, freed) decide hold vs break?
T3: how close do the objective lines come to the owner's TSLA and SPY lines? (descriptive)
Usage: OMP_NUM_THREADS=1 python run_tests.py -> out/t1.json, out/t2.json, out/t3_gaps.csv, out/events.csv.gz, out/tests.png, out/lines.png"""
import json
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
sys.path.insert(0, str(HERE.parent / "2026-10-16-owner-channel-gamma"))
sys.path.insert(0, str(HERE.parent / "2026-10-16-spy-channel"))
import channel_gamma as C                          # noqa: E402  (owner's TSLA lines, as reconstructed there)
import spy_channel as SC                           # noqa: E402  (owner's SPY lines, read from the screenshot there)
from burst_gamma import state                      # noqa: E402  (originals, imported unchanged)
from channels import detect                        # noqa: E402
from common import DATA, load_bars                 # noqa: E402

START = "2010-01-01"                               # first touch date counted; earlier bars only warm up the averages
NS, PRIMARY = (50, 200, 500), 200
SHIFTS = (-2, -1, 0, 1, 2)                         # ATR(20) offsets; 0 = the real line, the rest are placebos
H, BAND, SNAP = 20, 0.5, 10
NBOOT, NPERM = 2000, 2000
OPT = ["TSLA", "MSFT", "NVDA", "SPY", "QQQ", "MU"]
RNG = np.random.default_rng(20261017)
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF, CHAN = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb", "#3b5bdb"


def tickers():
    return sorted(p.name[:-8] for p in DATA.glob("*_1d.json") if not p.name.startswith("^"))


def bars(sym):
    return load_bars(sym).iloc[:-1]                # the last committed bar can be an intraday snapshot


def vwap(b, n):
    tp = (b.high + b.low + b.close) / 3
    return (tp * b.volume).rolling(n).sum() / b.volume.rolling(n).sum()


def atr(b):
    pc = b.close.shift(1)
    tr = pd.concat([b.high, pc], axis=1).max(axis=1) - pd.concat([b.low, pc], axis=1).min(axis=1)
    return tr.rolling(20).mean()


def events(sym, b, n, k):
    """Touches of the line V(n) + k*ATR(20), both as of the prior close; first passage on closes within H sessions."""
    a = atr(b).shift(1).to_numpy()
    L = vwap(b, n).shift(1).to_numpy() + k * a
    hi, lo, c, cp = (x.to_numpy() for x in (b.high, b.low, b.close, b.close.shift(1)))
    ok = np.isfinite(L) & np.isfinite(a) & (a > 0) & np.isfinite(cp) & (lo <= L) & (L <= hi) & (cp != L) & (b.index >= START)
    rows, free = [], 0
    for i in np.nonzero(ok)[0]:
        if i < free:                               # the line is busy until the previous touch resolves
            continue
        side = 1 if cp[i] > L[i] else -1           # +1: approached from above (support), -1: from below (resistance)
        x = side * (c[i:i + H] - L[i]) / a[i]
        rj, bk = np.nonzero(x >= BAND)[0], np.nonzero(x <= -BAND)[0]
        r, q = (rj[0] if len(rj) else H), (bk[0] if len(bk) else H)
        if r == q:                                 # unresolved within H sessions (or the data ends): dropped
            free = i + H
            continue
        j = i + min(r, q)
        snap = np.nan
        if q < r and j + SNAP < len(c):
            snap = float((side * (c[j + 1:j + 1 + SNAP] - L[i]) >= 0).any())
        rows.append((sym, n, k, b.index[i], b.index[i - 1], side, int(r < q), snap))
        free = j + 1
    return rows


def all_events():
    rows = []
    for sym in tickers():
        b = bars(sym)
        for n in NS:
            for k in SHIFTS:
                rows += events(sym, b, n, k)
    E = pd.DataFrame(rows, columns=["sym", "N", "k", "date", "prev", "side", "reject", "snap"])
    E["year"] = E.date.dt.year
    return E


def boot_excess(E):
    """Real-line reject rate minus the mean placebo rate, with a ticker-year block bootstrap."""
    blocks = E.groupby(["sym", "year"])
    keys = list(blocks.groups)
    M = np.zeros((len(keys), len(SHIFTS), 2))
    for bi, key in enumerate(keys):
        g = blocks.get_group(key)
        for ki, k in enumerate(SHIFTS):
            s = g.reject[g.k == k]
            M[bi, ki] = s.sum(), len(s)
    stat = lambda S: S[..., 2, 0] / S[..., 2, 1] - np.mean([S[..., j, 0] / S[..., j, 1] for j in (0, 1, 3, 4)], axis=0)
    tot = M.sum(0)
    obs = float(stat(tot))
    draws = M[RNG.integers(0, len(keys), (NBOOT, len(keys)))].sum(1)
    bs = stat(draws)
    return {"excess_pts": 100 * obs, "ci95_pts": [100 * float(np.quantile(bs, 0.025)), 100 * float(np.quantile(bs, 0.975))],
            "p_one_sided": float((bs <= 0).mean()), "blocks": len(keys),
            "reject_rate_by_shift": {str(k): float(tot[i, 0] / tot[i, 1]) for i, k in enumerate(SHIFTS)},
            "events_by_shift": {str(k): int(tot[i, 1]) for i, k in enumerate(SHIFTS)}}


def t1(E):
    res = {}
    for n in NS:
        e = E[E.N == n]
        res[f"N={n}"] = {"all": boot_excess(e), "support (from above)": boot_excess(e[e.side == 1]),
                         "resistance (from below)": boot_excess(e[e.side == -1])}
    p = res[f"N={PRIMARY}"]["all"]["p_one_sided"]
    res["verdict (primary N=200, p<0.025)"] = "pass" if p < 0.025 else "fail"
    return res


def perm(y, g, strata, sign=1):
    """Reject-rate difference (group True minus False) and a one-sided label permutation p, shuffled within strata."""
    y, g, strata = np.asarray(y, float), np.asarray(g, bool), np.asarray(strata)
    if g.sum() == 0 or (~g).sum() == 0:
        return {"n_true": int(g.sum()), "n_false": int((~g).sum()), "diff_pts": np.nan, "p_one_sided": np.nan}
    d = lambda gg: y[gg].mean() - y[~gg].mean()
    obs = d(g)
    idx = [np.nonzero(strata == s)[0] for s in np.unique(strata)]
    null = np.empty(NPERM)
    for i in range(NPERM):
        gg = g.copy()
        for ix in idx:
            gg[ix] = RNG.permutation(g[ix])
        null[i] = d(gg)
    return {"n_true": int(g.sum()), "n_false": int((~g).sum()), "rate_true": float(y[g].mean()), "rate_false": float(y[~g].mean()),
            "diff_pts": 100 * float(obs), "p_one_sided": float((sign * null >= sign * obs).mean())}


def t2_frame(E, ns=(PRIMARY,)):
    e = E[E.N.isin(ns) & (E.k == 0) & E.sym.isin(OPT) & (E.date >= "2020-01-02")].copy()
    parts = []
    for sym in OPT:
        s = state(sym)
        x = e[e.sym == sym].copy()
        x["to_flip_pct"] = s.to_flip_pct.reindex(x.prev).to_numpy()
        x["near_pct"] = s.near_pct.reindex(x.prev).to_numpy() if "near_pct" in s else np.nan
        parts.append(x)
    x = pd.concat(parts)
    x = x[x.to_flip_pct.notna()]
    x["above"] = x.to_flip_pct > 0
    x["freed"] = x.near_pct <= 1 / 3
    return x


def t2(E):
    res = {}
    for label, ns in (("primary N=200", (PRIMARY,)), ("secondary: N=50, 200, 500 pooled", NS)):
        x = t2_frame(E, ns)
        r = {}
        for who, m in [("TSLA", x.sym == "TSLA"), ("all 6", np.ones(len(x), bool))] + [(s, x.sym == s) for s in OPT if s != "TSLA"]:
            xx = x[m]
            fr = xx[xx.near_pct.notna()]
            setup = fr.freed & ~fr.above
            brk = fr[fr.reject == 0]
            r[who] = {"touches": int(len(xx)),
                      "above vs below flip (reject rate)": perm(xx.reject, xx.above, xx.sym),
                      "freed vs not (reject rate; prediction: freed lower)": perm(fr.reject, fr.freed, fr.sym, sign=-1),
                      "below flip & freed vs the rest (reject rate; prediction: lower)": perm(fr.reject, setup, fr.sym, sign=-1),
                      "snap-back within 10 sessions after a break: below&freed vs rest": perm(brk.snap.fillna(0), (brk.freed & ~brk.above), brk.sym)}
        res[label] = r
    p = res["primary N=200"]["TSLA"]["above vs below flip (reject rate)"]["p_one_sided"]
    res["verdict (TSLA above vs below, p<0.05)"] = "pass" if p < 0.05 else "fail"
    return res


def objective(raw, days):
    """Objective lines on each day, from data through the prior close: rolling VWAPs, channels.py bands, VWAP from its anchor."""
    tp = (raw.high + raw.low + raw.close) / 3
    ctv, cv = (tp * raw.volume).cumsum().to_numpy(), raw.volume.cumsum().to_numpy()
    O = pd.DataFrame(index=days)
    for n in NS:
        O[f"VWAP{n}"] = vwap(raw, n).shift(1).reindex(days)
    rows = []
    for d in days:
        i = raw.index.get_loc(d)
        w = raw.iloc[max(0, i - 800):i]
        ch = detect(w)
        if ch is None:
            rows.append((np.nan,) * 4)
            continue
        lo, mid, up = (float(v[0]) for v in ch.lines([len(w)]))
        s = i - len(w) + ch.start
        av = (ctv[i - 1] - (ctv[s - 1] if s else 0)) / (cv[i - 1] - (cv[s - 1] if s else 0))
        rows.append((up, mid, lo, av))
    O[["channel upper", "channel mid", "channel lower", "VWAP from channel anchor (extra)"]] = rows
    return O


def gaps(O, Lo):
    out = []
    for c in O:
        r = {"objective line": c}
        for k in Lo:
            g = np.log(O[c] / Lo[k]).dropna()
            r[k] = round(100 * float(g.abs().median()), 1) if len(g) else np.nan
        out.append(r)
    return pd.DataFrame(out).set_index("objective line")


def t3():
    raw = bars("TSLA")
    td = raw.index[(raw.index >= C.START) & (raw.index <= "2026-10-14")]
    To = objective(raw, td)
    Tl = pd.DataFrame({k: C.line(td, k) for k in C.LINES}, index=td)
    D, L, *_ = SC.frame()
    sraw = bars("SPY")
    sd = sraw.index[(sraw.index >= D.index[0]) & (sraw.index <= "2026-10-14")]
    So = objective(sraw, sd)
    Sl = L.loc[sd, ["upper", "mid", "lower"]].rename(columns=lambda k: f"SPY {k}")
    G = gaps(To, Tl).join(gaps(So, Sl))
    return G, (raw, To, Tl), (sraw, So, Sl)


def style():
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})


def fig_tests(r1, r2):
    style()
    f, (a, b) = plt.subplots(1, 2, figsize=(15, 5.6), gridspec_kw={"width_ratios": [1.1, 1], "wspace": 0.22})
    for n, col, dx in zip(NS, (MUTED, INK, BLUE), (-0.08, 0, 0.08)):
        v = r1[f"N={n}"]["all"]
        y = [100 * v["reject_rate_by_shift"][str(k)] for k in SHIFTS]
        a.plot(np.array(SHIFTS) + dx, y, "-o", color=col, lw=1.6 if n == PRIMARY else 1.1, ms=6 if n == PRIMARY else 4,
               label=f"{n}-day VWAP: real minus placebo {v['excess_pts']:+.1f} pts (95% {v['ci95_pts'][0]:+.1f} to {v['ci95_pts'][1]:+.1f}), p {v['p_one_sided']:.3f}")
    a.axvline(0, color=GRID, lw=8, zorder=0)
    a.axhline(50, color=MUTED, lw=0.8, ls=":")
    a.set_xticks(SHIFTS, ["-2 ATR\n(placebo)", "-1 ATR\n(placebo)", "real\nVWAP line", "+1 ATR\n(placebo)", "+2 ATR\n(placebo)"])
    a.set_ylabel("touches that held (bounced 0.5 ATR\nbefore going 0.5 ATR through), %")
    a.legend(loc="lower center", frameon=False, fontsize=8)
    ev = r1[f"N={PRIMARY}"]["all"]["events_by_shift"]["0"]
    a.set_title(f"T1: does price respect holders' cost basis more than a fake line of the same shape?\n41 tickers, 2010-2026; {ev:,} touches of the real 200-day line",
                loc="left", fontsize=9.5, color=INK)
    a.set_ylim(38, 60)
    groups = [("TSLA", "above vs below flip (reject rate)", ("above flip", "below flip")),
              ("all 6", "above vs below flip (reject rate)", ("above flip", "below flip")),
              ("TSLA", "freed vs not (reject rate; prediction: freed lower)", ("freed", "not freed")),
              ("all 6", "freed vs not (reject rate; prediction: freed lower)", ("freed", "not freed")),
              ("TSLA", "below flip & freed vs the rest (reject rate; prediction: lower)", ("below flip\n& freed", "rest")),
              ("all 6", "below flip & freed vs the rest (reject rate; prediction: lower)", ("below flip\n& freed", "rest"))]
    P = r2["primary N=200"]
    for i, (who, key, (lt, lf)) in enumerate(groups):
        v = P[who][key]
        x0 = i * 1.3
        for dx, rate, n, lab, col in ((-0.2, v.get("rate_true", np.nan), v["n_true"], lt, GREEN if i < 2 else ORANGE),
                                      (0.2, v.get("rate_false", np.nan), v["n_false"], lf, MUTED)):
            b.bar(x0 + dx, 100 * rate, width=0.36, color=col, alpha=0.85)
            b.text(x0 + dx, 100 * rate + 1, f"{100 * rate:.0f}%\nn={n}", ha="center", va="bottom", fontsize=6.8, color=INK)
            b.text(x0 + dx, 2, lab, ha="center", va="bottom", fontsize=7, color="white" if col != MUTED else INK, rotation=90)
        b.text(x0, -3, f"{who}\n{v['diff_pts']:+.0f} pts\np {v['p_one_sided']:.2f}", ha="center", va="top", fontsize=8, color=INK)
    b.axhline(50, color=MUTED, lw=0.8, ls=":")
    b.set_xticks([])
    b.set_ylim(0, 100)
    b.set_ylabel("touches of the 200-day VWAP that held, %")
    b.set_title("T2: does the options state decide hold or break? 200-day VWAP touches, 2020-2026\n(6 options tickers; 'freed' only where the file has it: TSLA, MSFT, NVDA, MU)",
                loc="left", fontsize=9.5, color=INK)
    f.savefig(OUT / "tests.png", dpi=140, bbox_inches="tight", facecolor=SURF)


def fig_lines(T, S):
    style()
    f, (a, b) = plt.subplots(1, 2, figsize=(17, 6.8), gridspec_kw={"width_ratios": [1.6, 1], "wspace": 0.12})
    for ax, (raw, O, Lo), title in ((a, T, "TSLA: your lines (blue) vs the objective set"), (b, S, "SPY: your lines (blue) vs the objective set")):
        d = Lo.index
        for k in Lo:
            ax.plot(d, Lo[k], color=CHAN, lw=1.6, alpha=0.6)
        ax.semilogy(d, raw.close.reindex(d), color=INK, lw=1.3)
        ax.plot(d, O["VWAP200"], color=MUTED, lw=1.5, ls="--", label="200-day VWAP (rolling cost basis)")
        ax.plot(d, O["VWAP500"], color=MUTED, lw=1.2, ls=":", label="500-day VWAP")
        ax.plot(d, O["VWAP50"], color=MUTED, lw=1.0, ls="-.", label="50-day VWAP")
        ax.plot(d, O["channel upper"], color=ORANGE, lw=1.1, label="channels.py upper / lower band (point in time)")
        ax.plot(d, O["channel lower"], color=ORANGE, lw=1.1)
        ax.minorticks_off()
        ax.set_title(title, loc="left", fontsize=9.5, color=INK)
    a.set_ylim(95, 720)
    b.set_ylim(655, 835)
    a.set_yticks([100, 150, 200, 300, 400, 500, 700], ["100", "150", "200", "300", "400", "500", "700"])
    b.set_yticks([660, 700, 740, 780, 820], ["660", "700", "740", "780", "820"])
    b.text(S[2].index[3], 658, f"off the chart: 500-day VWAP ${S[1]['VWAP500'].iloc[-1]:.0f}", fontsize=8, color=MUTED)
    for k, lab in zip(T[2], "ABCD"):
        a.text(T[2].index[-1], T[2][k].iloc[-1], f" {lab}", color=CHAN, fontsize=10, weight="bold", va="center")
    b.xaxis.set_major_locator(mdates.MonthLocator())
    b.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    a.legend(loc="upper center", bbox_to_anchor=(0.8, -0.06), ncol=3, frameon=False, fontsize=8.5)
    f.suptitle("T3 (descriptive): how close do lines computed from data alone come to your hand-drawn channels?", x=0.01, ha="left",
               fontsize=11.5, color=INK, weight="bold")
    f.savefig(OUT / "lines.png", dpi=140, bbox_inches="tight", facecolor=SURF)


def main():
    OUT.mkdir(exist_ok=True)
    E = all_events()
    E.to_csv(OUT / "events.csv.gz", index=False)
    r1 = t1(E)
    (OUT / "t1.json").write_text(json.dumps(r1, indent=1))
    r2 = t2(E)
    (OUT / "t2.json").write_text(json.dumps(r2, indent=1, default=float))
    fig_tests(r1, r2)
    G, T, S = t3()
    G.to_csv(OUT / "t3_gaps.csv")
    fig_lines(T, S)
    return E, r1, r2, G


if __name__ == "__main__":
    E, r1, r2, G = main()
    for n in NS:
        for side, v in r1[f"N={n}"].items():
            print(n, side, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k != "events_by_shift"})
    print(r1["verdict (primary N=200, p<0.025)"])
    print(json.dumps(r2["primary N=200"]["TSLA"], indent=1, default=float))
    print(json.dumps(r2["primary N=200"]["all 6"], indent=1, default=float))
    print(r2["verdict (TSLA above vs below, p<0.05)"])
    print(G.to_string())
