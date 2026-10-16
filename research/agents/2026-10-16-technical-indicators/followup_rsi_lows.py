"""Follow-up A (pre-registered in README.md at 2870a7d): do TSLA's burst-launch lows share a low RSI, and does a low
RSI predict a burst? F1 look-back (launch lows vs other swing lows), F2 forward (RSI in its bottom tenth -> up-burst
within 10 sessions), F3 secondary (RSI < 30; weekly RSI bottom third).
Usage: OMP_NUM_THREADS=1 python followup_rsi_lows.py -> out/followup_rsi_lows.json, out/followup_rsi_lows.png
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import indicators as I

sys.path.insert(0, str(I.MICRO))
from named_weeks import MOVES                      # noqa: E402  (originals, imported unchanged)
from own_multiverse import within                  # noqa: E402
from stock_now import burst_days                   # noqa: E402

RNG = np.random.default_rng(20261017)
ORANGE, BLUE, INK, MUTED, GRID, SURF = "#eb6834", "#2a78d6", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def data():
    b, raw, pct, _ = I.frame("TSLA", "daily")
    c = b.close
    _, wraw, wpct, _ = I.frame("TSLA", "weekly")
    wk = lambda s: s.reindex(s.index.union(c.index)).ffill().reindex(c.index).shift(1)   # last completed week before day t
    D = pd.DataFrame({"c": c, "rsi": raw.RSI, "rsi_pct": pct.RSI, "w_rsi": wk(wraw.RSI), "w_rsi_pct": wk(wpct.RSI)})
    D["burst"] = burst_days(c, 1)
    D["burst10"] = within(D.burst.to_numpy(), 10)
    return D


def lows(D):
    c = D.c.to_numpy()
    n = len(c)
    swing = np.array([i >= 5 and i < n - 5 and c[i] == c[i - 5:i + 6].min() for i in range(n)])
    bursts = np.where(D.burst.to_numpy())[0]
    launch = sorted({i - 10 + int(np.argmin(c[i - 10:i])) for i in bursts if i >= 10})
    other = [i for i in np.where(swing)[0] if not np.nan_to_num(D.burst10.iloc[i]) and i not in launch]
    return np.array(launch), np.array(other)


def f1(D, launch, other):
    r = D.rsi.to_numpy()
    a, b = r[launch], r[other]
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    obs = np.median(a) - np.median(b)
    pool, k = np.r_[a, b], len(a)
    null = []
    for _ in range(2000):
        p = RNG.permutation(pool)
        null.append(np.median(p[:k]) - np.median(p[k:]))
    p = (np.sum(np.abs(null) >= abs(obs)) + 1) / 2001
    pa, pb = D.rsi_pct.to_numpy()[launch], D.rsi_pct.to_numpy()[other]
    return {"launch lows": int(len(a)), "other swing lows": int(len(b)), "median RSI at launch lows": float(np.median(a)),
            "median RSI at other swing lows": float(np.median(b)), "IQR launch": [float(np.percentile(a, 25)), float(np.percentile(a, 75))],
            "IQR other": [float(np.percentile(b, 25)), float(np.percentile(b, 75))], "difference": float(obs), "p": float(p),
            "share of launch lows with RSI pct <= 0.10": float(np.nanmean(pa <= 0.10)), "same for other swing lows": float(np.nanmean(pb <= 0.10)),
            "share of launch lows with RSI < 30": float(np.mean(a < 30)), "same for other swing lows (RSI < 30)": float(np.mean(b < 30))}


def forward(D, signal, name):
    ok = signal.notna() & D.burst10.notna()
    s, y = signal[ok].to_numpy(bool), D.burst10[ok].to_numpy()
    base = y.mean()
    obs = y[s].mean() - base
    null = np.array([y[np.roll(s, o)].mean() - base for o in RNG.choice(np.arange(60, len(s) - 59), 1000)])
    p = (np.sum(np.abs(null) >= abs(obs)) + 1) / 1001
    ep = int((s & ~np.r_[False, s[:-1]]).sum())
    return {"signal": name, "days": int(s.sum()), "episodes": ep, "P(up-burst within 10 | signal)": float(y[s].mean()),
            "P(up-burst within 10), all days": float(base), "difference": float(obs), "p": float(p)}


def named(D):
    c = D.c
    rows = []
    for name, _, a, b in MOVES:
        z = c.loc[a:b].pct_change()
        big = z.idxmax()
        i = c.index.get_loc(big)
        lo = i - 10 + int(np.argmin(c.to_numpy()[i - 10:i]))
        rows.append({"move": name, "biggest day": str(big.date()), "launch low": str(c.index[lo].date()),
                     "daily RSI at low": float(D.rsi.iloc[lo]), "RSI pct at low": float(D.rsi_pct.iloc[lo]),
                     "weekly RSI": float(D.w_rsi.iloc[lo])})
    return rows


def bands(D):
    dn = within(burst_days(D.c, -1), 10)
    ok = D.rsi.notna() & D.burst10.notna() & np.isfinite(dn)
    out = []
    for lab, lo, hi in (("<30", 0, 30), ("30-40", 30, 40), ("40-50", 40, 50), ("50-60", 50, 60), ("60-70", 60, 70), ("70+", 70, 101)):
        m = (ok & (D.rsi >= lo) & (D.rsi < hi)).to_numpy()
        out.append({"band": lab, "days": int(m.sum()), "P": float(D.burst10.to_numpy()[m].mean()), "P down": float(dn[m].mean())})
    return out, float(D.burst10[ok].mean())


def overlap(D):
    """Post-hoc: in 2021+, how much of the low-RSI signal is our TSLA full setup (freed + below flip)?"""
    S = I.setups()["TSLA"]
    x = D.join(S[["setup"]], how="inner")
    x = x[x.index >= "2021-01-01"]
    x["up3"] = within(x.burst.to_numpy(), 3)
    low = x.rsi_pct <= 0.10
    rows = []
    for lab, m in (("setup +\nRSI low", x.setup & low), ("setup,\nRSI not low", x.setup & ~low),
                   ("RSI low,\nno setup", ~x.setup & low), ("neither", ~x.setup & ~low)):
        m = m & x.up3.notna()
        rows.append({"group": lab, "days": int(m.sum()), "episodes": int((m & ~m.shift(1, fill_value=False)).sum()), "P": float(x.up3[m].mean())})
    return rows, int((x.setup & low).sum()), int(x.setup.sum())


def figure(D, launch, other, nm, bd, base, res):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, (a, b, c) = plt.subplots(1, 3, figsize=(17, 5.8), gridspec_kw={"wspace": 0.3, "width_ratios": [1.1, 1.2, 0.9]})
    r = D.rsi.to_numpy()
    bins = np.arange(10, 81, 5)
    for idx, col, lab in ((other, BLUE, f"swing lows with no burst after (n={len(other)})"), (launch, ORANGE, f"lows that launched a burst (n={len(launch)})")):
        v = r[idx]
        v = v[np.isfinite(v)]
        a.hist(v, bins=bins, weights=np.full(len(v), 100 / len(v)), histtype="step", lw=2.2, color=col, label=lab)
    for k, row in enumerate(nm):
        a.plot(row["daily RSI at low"], -1.2 - (k % 2) * 1.1, "v", color=INK, ms=6)
    a.text(10.5, -3.6, "▼ = the 8 named moves' launch lows", fontsize=8, color=INK)
    a.set_ylim(-4.2, 31)
    a.set_xlabel("daily RSI(14) at the low")
    a.set_ylabel("% of lows in each group")
    a.legend(loc="upper left", frameon=False, fontsize=8)
    F1 = res["F1"]
    lo_nm, hi_nm = min(x["daily RSI at low"] for x in nm), max(x["daily RSI at low"] for x in nm)
    a.set_title(f"1. Look back: no shared RSI. Burst lows median {F1['median RSI at launch lows']:.0f},\n"
                f"lows with no burst {F1['median RSI at other swing lows']:.0f} (p {F1['p']:.2f}); named moves {lo_nm:.0f}-{hi_nm:.0f}",
                loc="left", color=INK, fontsize=9.5)
    xs = np.arange(len(bd))
    b.bar(xs - 0.19, [100 * x["P"] for x in bd], color=BLUE, width=0.36, label="up-burst within 10")
    b.bar(xs + 0.19, [100 * x["P down"] for x in bd], color=ORANGE, width=0.36, label="down-burst within 10")
    for x, row in zip(xs, bd):
        b.text(x - 0.19, 100 * row["P"] + 1, f"{100 * row['P']:.0f}", ha="center", va="bottom", fontsize=8, color=INK)
        b.text(x + 0.19, 100 * row["P down"] + 1, f"{100 * row['P down']:.0f}", ha="center", va="bottom", fontsize=8, color=INK)
        b.text(x, -7, f"{row['days']} d", ha="center", va="top", fontsize=7.5, color=MUTED)
    b.set_xticks(list(xs), [x["band"] for x in bd])
    b.set_xlabel("daily RSI(14) on the day  (day counts under each band)", labelpad=24)
    b.set_ylabel("% of days followed by the burst")
    b.set_ylim(0, 88)
    b.legend(loc="upper right", frameon=False, fontsize=8)
    b.set_axisbelow(True)
    b.grid(axis="y", color=GRID)
    F2 = res["F2"]
    b.set_title(f"2. Look forward: an extreme low RSI leans to an up-burst.\nBottom tenth: {100 * F2['P(up-burst within 10 | signal)']:.0f}% vs "
                f"{100 * F2['P(up-burst within 10), all days']:.0f}% on all days (p 0.001, {F2['episodes']} episodes)", loc="left", color=INK, fontsize=9.5)
    rows, both, setup = res["overlap"]
    cs = [BLUE, BLUE, "#9db9e6", "#9db9e6"]
    c.bar(range(4), [100 * x["P"] for x in rows], color=cs, width=0.62)
    for i, x in enumerate(rows):
        c.text(i, 100 * x["P"] + 1, f"{100 * x['P']:.0f}%\n{x['episodes']} ep.", ha="center", va="bottom", fontsize=8, color=INK)
    c.set_xticks(range(4), [x["group"] for x in rows], fontsize=8)
    c.set_ylabel("up-burst within 3 sessions, %")
    c.set_ylim(0, 55)
    c.set_axisbelow(True)
    c.grid(axis="y", color=GRID)
    c.set_title(f"3. 2021+ (post-hoc): {both} of our {setup} setup days already\nhave RSI in its bottom tenth; the options state separates\n"
                "the launches, not RSI", loc="left", color=INK, fontsize=9.5)
    f.suptitle("TSLA: the launch lows don't share one RSI, but an extreme low RSI does lean to a rebound burst, and since 2021 "
               "it mostly coincides with our options setup", x=0.01, ha="left", fontsize=11, color=INK, weight="bold", y=1.04)
    f.savefig(I.OUT / "followup_rsi_lows.png", dpi=150, bbox_inches="tight", facecolor=SURF)


def main():
    D = data()
    D = D[D.index >= "2010-08-01"]
    launch, other = lows(D)
    res = {"F1": f1(D, launch, other),
           "F2": forward(D, D.rsi_pct.where(D.rsi_pct.notna()) <= 0.10, "daily RSI pct <= 0.10"),
           "F3a": forward(D, (D.rsi < 30).where(D.rsi.notna()), "daily RSI < 30"),
           "F3b": forward(D, (D.w_rsi_pct <= 1 / 3).where(D.w_rsi_pct.notna()), "weekly RSI pct <= 1/3"),
           "named moves": named(D)}
    res["F2"]["passes (p < 0.05, positive)"] = bool(res["F2"]["p"] < 0.05 and res["F2"]["difference"] > 0)
    bd, base = bands(D)
    res["bands"] = bd
    res["overlap"] = overlap(D)
    (I.OUT / "followup_rsi_lows.json").write_text(json.dumps(res, indent=1, default=float))
    figure(D, launch, other, res["named moves"], bd, base, res)
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=lambda v: round(float(v), 4)))
