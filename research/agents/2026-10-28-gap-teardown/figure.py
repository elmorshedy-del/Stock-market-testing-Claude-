"""Gap-teardown figure: VF vs SC anatomy (price, cumulative aggressor delta, book imbalance, ask depth) and the T2/T3 effect sizes.
Usage: python figure.py -> out/gap_teardown.png"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
A = pd.read_csv(HERE / "out" / "anatomy.csv", parse_dates=["date"])
R = json.load(open(HERE / "out" / "tests.json"))
COL = {"VF": "#c0392b", "SC": "#1f77b4", "mid": "#7f7f7f"}
A = A[(A.min_from_open >= -330) & (A.min_from_open <= 60)].copy()
A["key"] = A.sym + A.date.dt.strftime("%Y%m%d")
# cumulative delta as % of each event's 09:30-10:30 volume, starting at 09:30
rth = A[A.min_from_open >= 0]
vol = rth.groupby("key").vol.sum()
rth = rth.assign(cd=rth.groupby("key").delta.cumsum() / rth.key.map(vol) * 100)
fig, ax = plt.subplots(2, 4, figsize=(23, 10))
DG = json.load(open(HERE / "out" / "diag.json")); RU = json.load(open(HERE / "out" / "rule.json"))
foc = {("TSLA", "2026-10-26"): ("TSLA Oct 26 (SC)", "-"), ("AAPL", "2020-09-02"): ("AAPL 2020-09-02 (VF)", "--"), ("QQQ", "2020-09-02"): ("QQQ 2020-09-02 (VF)", ":")}


def band(a, df, col, cls, lab=True, pm=False):
    d = df[df.cls == cls]
    g = d.groupby("min_from_open")[col]
    med, lo, hi = g.median(), g.quantile(0.25), g.quantile(0.75)
    a.plot(med.index, med.values, color=COL[cls], lw=2, label=f"{cls} median (n={d.key.nunique()})" if lab else None)
    a.fill_between(med.index, lo.values, hi.values, color=COL[cls], alpha=0.15)


def focal(a, df, col):
    for (s, d), (lab, ls) in foc.items():
        z = df[(df.sym == s) & (df.date == d)]
        if len(z): a.plot(z.min_from_open, z[col], color="k", ls=ls, lw=1.2, label=lab)


for cls in ("VF", "SC"): band(ax[0, 0], A, "ret_sig", cls)
focal(ax[0, 0], A, "ret_sig")
ax[0, 0].axvline(0, color="k", lw=0.6); ax[0, 0].axhline(0, color="k", lw=0.4)
ax[0, 0].set(title="Price vs the open, in sigma (04:00 to 10:30)", xlabel="minutes from 09:30", ylabel="sigma"); ax[0, 0].legend(fontsize=8)
for cls in ("VF", "SC"): band(ax[0, 1], rth, "cd", cls)
focal(ax[0, 1], rth, "cd")
ax[0, 1].axhline(0, color="k", lw=0.4); ax[0, 1].set(title="Cumulative aggressor delta from 09:30, % of first-hour volume", xlabel="minutes from 09:30", ylabel="%")
ax[0, 1].legend(fontsize=8)
if "imb" in rth:
    for cls in ("VF", "SC"): band(ax[0, 2], rth, "imb", cls)
    ax[0, 2].axhline(0, color="k", lw=0.4); ax[0, 2].set(title="Book imbalance within 0.5% of mid\n(bid - ask) / (bid + ask), 1-min mean", xlabel="minutes from 09:30")
    ax[0, 2].legend(fontsize=8)
    # ask depth relative to the event's own 09:30-09:35 ask depth
    base = rth[rth.min_from_open < 5].groupby("key").ask_d.mean()
    r2 = rth.assign(adr=rth.ask_d / rth.key.map(base))
    for cls in ("VF", "SC"): band(ax[1, 0], r2, "adr", cls)
    base = rth[rth.min_from_open < 5].groupby("key").bid_d.mean()
    r3 = rth.assign(bdr=rth.bid_d / rth.key.map(base))
    for cls in ("VF", "SC"):
        g = r3[r3.cls == cls].groupby("min_from_open").bdr.median(); ax[1, 0].plot(g.index, g.values, color=COL[cls], ls="--", lw=1.4, label=f"{cls} bid depth")
    ax[1, 0].axhline(1, color="k", lw=0.4); ax[1, 0].set(title="Resting depth within 0.5% vs its 09:30-09:35 level\n(solid = ask side, dashed = bid side)", xlabel="minutes from 09:30", ylabel="x first 5 min")
    ax[1, 0].legend(fontsize=8)


for cls in ("VF", "SC"): band(ax[0, 3], rth, "spr_bp", cls)
ax[0, 3].set(title="Quoted spread (bp), 1-min mean", xlabel="minutes from 09:30"); ax[0, 3].legend(fontsize=8)


def bars(a, rows, key, title, xl):
    rows = [r for r in rows if key in r]
    lab = [r["measure"][:44] for r in rows]; v = [r[key] for r in rows]
    c = ["#2ca02c" if r.get("pass") else "#bbbbbb" for r in rows]
    a.barh(range(len(v)), v, color=c); a.set_yticks(range(len(v))); a.set_yticklabels(lab, fontsize=8); a.invert_yaxis()
    for i, r in enumerate(rows): a.text(v[i], i, f"  Holm p={r['p_holm']:.3f}", va="center", fontsize=7)
    a.set(title=title, xlabel=xl)


bars(ax[1, 1], R["T2_all"], "auc_vf_gt_sc", "T2 before the open: VF vs SC (AUC; 0.5 = no separation)\ngreen = passes Holm", "AUC (VF values above SC)")
ax[1, 1].axvline(0.5, color="k", lw=0.6); ax[1, 1].set_xlim(0.2, 0.8)
a = ax[1, 2]; rows = R["T3_all"]; yy = np.arange(len(rows))
a.barh(yy - 0.27, [r["rho"] for r in rows], 0.26, color=["#2ca02c" if r["pass"] else "#bbbbbb" for r in rows], label="pre-registered (green = Holm pass)")
a.barh(yy, [DG["weighted"][r["measure"]]["rho"] for r in rows], 0.26, color="#8c564b", label="weighted to the population")
a.barh(yy + 0.27, [DG["weighted_partial_on_first5m_return"][r["measure"]]["rho"] for r in rows], 0.26, color="#17becf", label="weighted, after removing the 5-min price move")
a.set_yticks(yy); a.set_yticklabels([r["measure"][:40] for r in rows], fontsize=8); a.invert_yaxis(); a.axvline(0, color="k", lw=0.6)
a.set(title="T3 at 09:35: Spearman with the 09:35-10:30 return\nflow 'passes' only as a proxy for the first 5 minutes' price move", xlabel="rho"); a.legend(fontsize=7, loc="lower right")
a = ax[1, 3]; tb = RU["table"]; xx = np.arange(len(tb))
a.bar(xx - 0.2, [100 * r["P(next < 0)"] for r in tb], 0.4, color="#c0392b", label="P(09:35-10:30 down) %")
a.bar(xx + 0.2, [100 * r["P(next > +0.5 sig)"] for r in tb], 0.4, color="#1f77b4", label="P(up > 0.5 sigma) %")
for i, r in enumerate(tb):
    a.text(i, 62, f"mean {r['mean next (sig)']:+.2f}σ\nn={r['n']}", ha="center", fontsize=8)
a.set_xticks(xx); a.set_xticklabels([r["first 5 min (sig)"] for r in tb]); a.axhline(50, color="k", lw=0.5, ls=":")
a.set_ylim(0, 72); a.set(title="First 5 minutes vs the next 55 (exploratory)\nall gap-ups ≥ 0.5σ, weighted", xlabel="09:30-09:35 move (sigma)", ylabel="%"); a.legend(fontsize=8)
n = R["n"]
fig.suptitle(f"Gap-up opens ≥ 0.5σ, TSLA / AAPL / NVDA / QQQ 2018-2026, Nasdaq trades + 10-level book: violent fade (VF, n={n['VF']}) vs violent continuation (SC, n={n['SC']}); middle n={n['mid']}", fontsize=12)
fig.tight_layout(); fig.savefig(HERE / "out" / "gap_teardown.png", dpi=130)
print("saved")
