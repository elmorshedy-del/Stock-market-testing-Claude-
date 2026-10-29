"""House-of-cards figure: (a) average path of forced vs genuine index runs, (b) cliff rate, (c) gap-day open->close and
violent-fade rate, (d) 7-day ATM call held from open to close. Usage: python figure_hoc.py <scratchpad> -> out/house_of_cards.png"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; O = HERE / "out"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"; GEN, FOR = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
IR, GR = json.load(open(O / "index_runs.json")), json.load(open(O / "gap_runs.json"))
E = pd.read_csv(O / "index_events.csv", parse_dates=["date"]); G = pd.read_csv(O / "gap_events.csv", parse_dates=["date"])


def close(p):
    r = json.load(open(p))["chart"]["result"][0]
    c = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna(); return c[~c.index.duplicated(keep="last")]


px = {"SPX": close(S / "ladder28" / "data" / "^GSPC_1d.json"), "NDX": close(S / "ctx" / "intl" / "%5ENDX.json")}
paths = {0: [], 1: []}
for r in E.itertuples():
    c = px[r.index]; i = c.index.get_loc(r.date); w = c.iloc[i - 10:i + 11].to_numpy()
    if len(w) == 21: paths[r.forced].append((w - w[0]) / (w[10] - w[0]))
fig, ax = plt.subplots(2, 2, figsize=(14, 9.5)); plt.subplots_adjust(hspace=0.45, wspace=0.3)


def clean(a, axis="y"):
    for s in ("top", "right"): a.spines[s].set_visible(False)
    a.grid(axis=axis, color=GRID, lw=0.6); a.set_axisbelow(True)


a = ax[0, 0]; k = np.arange(-10, 11)
for f, col, lab in ((0, GEN, "genuine run (implied vol fell)"), (1, FOR, "forced run (implied vol rose)")):
    P = np.array(paths[f]); m = np.median(P, axis=0); q1, q3 = np.percentile(P, [25, 75], axis=0)
    a.plot(k, m, color=col, lw=2, label=f"{lab}, n={len(P)}"); a.fill_between(k, q1, q3, color=col, alpha=0.15)
a.axvline(0, color=INK2, lw=0.8); a.axhline(1, color=GRID, lw=0.8); a.axhline(0.5, color=GRID, lw=0.8, ls=":")
a.set(xlabel="sessions from the run's high", ylabel="share of the run (0 = start, 1 = high)"); a.legend(fontsize=8, frameon=False, loc="lower center"); clean(a)
a.set_title("(a) Top-decile 10-day index rallies, S&P 1990-2025 + Nasdaq-100 2001-2025:\nmedian path and middle half", loc="left", color=INK, fontsize=10)
a = ax[0, 1]; D = {"S&P 500": IR["describe_spx"], "Nasdaq-100": IR["describe_ndx"]}
for j, (nm, d) in enumerate(D.items()):
    for i, (key, col) in enumerate((("genuine", GEN), ("forced", FOR))):
        v = 100 * d[key]["cliff_rate"]; x = j * 3 + i
        a.bar(x, v, color=col, width=0.85); a.text(x, v + 1.5, f"{v:.0f}%\nn={d[key]['n']}", ha="center", fontsize=8, color=INK)
a.set_xticks([0.5, 3.5]); a.set_xticklabels(list(D), color=INK); a.set_ylim(0, 75); a.set_ylabel("% of runs giving back half or more within 10 sessions"); clean(a)
t = IR["tests"]
a.set_title(f"(b) The cliff: forced runs give back half more often, but forced runs are rare\n"
            f"(H1 S&P give-back p {t[list(t)[0]]['p']:.2f}; H3 Nasdaq p {t[list(t)[2]]['p']:.2f}: not significant)", loc="left", color=INK, fontsize=10)
a = ax[1, 0]; T = GR["tests"]; h5 = T["H5 gap-up after a forced run: open -> close (sigma)"]
grp = [("not forced", G[G.forced == 0]), ("forced", G[G.forced == 1])]
for i, (nm, x) in enumerate(grp):
    col = FOR if nm == "forced" else GEN
    a.bar(i, x.oc_pct.median(), color=col, width=0.6); a.text(i, x.oc_pct.median() + (0.03 if x.oc_pct.median() >= 0 else -0.08), f"median {x.oc_pct.median():+.2f}%\nmean {x.oc_pct.mean():+.2f}%\nviolent fade {100*(x.cls=='VF').mean():.0f}%\nn={len(x)}", ha="center", va="bottom" if x.oc_pct.median() >= 0 else "top", fontsize=8, color=INK)
a.axhline(0, color=INK2, lw=0.8); a.set_xticks([0, 1]); a.set_xticklabels(["after a genuine run", "after a forced run"], color=INK); a.set_ylabel("gap-day open -> close, %"); clean(a)
a.set_ylim(-0.6, 0.6)
a.set_title(f"(c) Gap-ups ≥ 0.5σ, TSLA/NVDA/QQQ/MSFT/MU 2020-2026: the day after a forced run\nopen -> close {h5['est']:+.2f}σ vs the rest [{h5['ci95'][0]:+.2f}, {h5['ci95'][1]:+.2f}], raw p {h5['p']:.2f} (Holm 0.20)", loc="left", color=INK, fontsize=10)
a = ax[1, 1]; bins = np.linspace(-80, 120, 41)
for nm, x in grp:
    col = FOR if nm == "forced" else GEN; v = x.call7_open_to_close_pct.dropna()
    a.hist(v, bins=bins, color=col, alpha=0.45, density=True, label=f"{'after a forced run' if nm == 'forced' else 'after a genuine run'}: median {v.median():+.1f}%, {100*(v<=-25).mean():.0f}% lose ≥25%")
    a.axvline(v.median(), color=col, lw=2)
a.axvline(0, color=INK2, lw=0.8); a.legend(fontsize=8, frameon=False); clean(a, "x"); a.set_xlabel("7-day at-the-money call bought at the open, value at the close, % (prior-close IV held constant)")
a.set_title("(d) The exit decision in option terms: holding a short call from the gap's open to the close", loc="left", color=INK, fontsize=10)
fig.suptitle("House of cards: rallies made with rising implied vol (forced) vs falling implied vol (genuine)", fontsize=12, color=INK, x=0.01, ha="left")
fig.savefig(O / "house_of_cards.png", dpi=130, bbox_inches="tight", facecolor="#fcfcfb"); print("saved")
