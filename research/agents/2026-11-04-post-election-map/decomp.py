"""How much of TSLA's Nov 4 premarket drop is Musk/Texas-specific? TSLA log return since Tue close split into:
QQQ beta part + AI-infrastructure factor part (mean QQQ-residual of CRWV, ORCL, VST, PLTR, IREN) + leftover. Betas: 1y daily (Yahoo).
Usage: python decomp.py -> out/decomp.json, out/tsla_decomp.png"""
import datetime as dt
import json
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; O = HERE / "out"; TUE = dt.date(2026, 11, 3)
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE, RED, GREEN = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834", "#c8372d", "#2f8f5b"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRAY, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.titleweight": "bold", "axes.titlesize": 11})


def ch(s, rng, iv, pp=False):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range={rng}&interval={iv}" + ("&includePrePost=true" if pp else "")
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    return [(dt.datetime.utcfromtimestamp(t) - dt.timedelta(hours=5), c) for t, c in zip(r["timestamp"], q["close"]) if c]


GROUPS = {"Mega-cap platforms": ["MSFT", "AAPL", "AMZN", "GOOGL", "META"], "AI chips": ["NVDA", "AVGO", "AMD"],
          "AI infrastructure / Texas power": ["ORCL", "PLTR", "CRWV", "IREN", "VST"], "Musk / Trump politics": ["TSLA", "SPCX", "DJT"],
          "Index": ["SPY", "QQQ", "RSP", "IWM"]}
INFRA = ["CRWV", "ORCL", "VST", "PLTR", "IREN"]
now = {}
for s in sum(GROUPS.values(), []):
    d = ch(s, "5d", "1d"); tue = [c for t, c in d if t.date() == TUE][0]; p = ch(s, "1d", "1m", True)[-1]; now[s] = (tue, p[1], p[0])
asof = max(v[2] for v in now.values())
H = {s: {t.date(): c for t, c in ch(s, "1y", "1d")} for s in ["QQQ", "TSLA"] + INFRA}
ds = sorted(set.intersection(*[set(v) for v in H.values()])); ds = [d for d in ds if d <= TUE]
R = {s: np.diff(np.log([H[s][d] for d in ds])) for s in H}; q = R["QQQ"]; bq = {s: np.polyfit(q, R[s], 1)[0] for s in R}
AI = np.mean([R[s] - bq[s] * q for s in INFRA], axis=0)
X = np.column_stack([np.ones_like(q), q, AI]); b = np.linalg.lstsq(X, R["TSLA"], rcond=None)[0]; e = R["TSLA"] - X @ b
m = lambda s: float(np.log(now[s][1] / now[s][0]))
ai_now = float(np.mean([m(s) - bq[s] * m("QQQ") for s in INFRA])); pq, pai = b[1] * m("QQQ"), b[2] * ai_now; left = m("TSLA") - pq - pai
res = {"as of (ET)": f"{asof:%Y-%m-%d %H:%M}", "TSLA = a + bQ*QQQ + bAI*AIfactor (1y daily)": {"bQ": round(b[1], 2), "bAI": round(b[2], 2), "resid sd %": round(100 * e.std(), 2), "n": len(q)},
       "today log %": {"TSLA": round(100 * m("TSLA"), 2), "QQQ part": round(100 * pq, 2), "AI-infra part": round(100 * pai, 2), "leftover (Musk/Texas)": round(100 * left, 2),
                       "leftover in resid sd": round(left / e.std(), 1), "AI-infra factor today": round(100 * ai_now, 2)},
       "moves % since Tue close": {s: round(100 * (v[1] / v[0] - 1), 2) for s, v in now.items()}}
json.dump(res, open(O / "decomp.json", "w"), indent=1); print(json.dumps(res["TSLA = a + bQ*QQQ + bAI*AIfactor (1y daily)"]), json.dumps(res["today log %"]))

fig, ax = plt.subplots(1, 2, figsize=(14.5, 5.8), facecolor=BG, gridspec_kw={"width_ratios": [1.7, 1]})
for a in ax: a.set_facecolor(BG); a.grid(True, axis="y", color=GRID, lw=0.8); a.spines[["top", "right"]].set_visible(False)
a = ax[0]; x = 0; ticks, labs = [], []; gcol = {"Mega-cap platforms": GREEN, "AI chips": BLUE, "AI infrastructure / Texas power": ORANGE, "Musk / Trump politics": RED, "Index": GRAY}
for g, ss in GROUPS.items():
    x0 = x
    for s in ss:
        v = res["moves % since Tue close"][s]; a.bar(x, v, 0.8, color=gcol[g]); a.text(x, v + (0.25 if v >= 0 else -0.25), f"{v:+.1f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=8, color=INK2)
        ticks.append(x); labs.append(s); x += 1
    a.text((x0 + x - 1) / 2, 9.6, g, ha="center", fontsize=8.5, color=gcol[g], fontweight="bold"); x += 0.8
a.axhline(0, color=INK2, lw=1); a.set_xticks(ticks, labs, fontsize=8.5, rotation=45); a.set_ylim(-12.5, 10.5); a.set_ylabel("% since Tue close (premarket)")
a.set_title("(a) It isn't 'all AI'. Platforms are up, chips are slightly red,\nand data centers, Texas power and Musk/Trump names are hit", loc="left")
a = ax[1]; parts = [("QQQ beta\n(1.43 x QQQ)", 100 * pq, GRAY), ("AI-infra factor\n(loading 0.01)", 100 * pai, ORANGE), ("Musk / Texas\nleftover", 100 * left, RED)]
cum = 0
for i, (nm, v, col) in enumerate(parts):
    a.bar(i, v, 0.6, bottom=cum, color=col); a.text(i, cum + v + (0.15 if v >= 0 else -0.15), f"{v:+.1f}%", ha="center", va="bottom" if v >= 0 else "top", fontsize=10, fontweight="bold", color=col); cum += v
a.bar(3, 100 * m("TSLA"), 0.6, color=INK); a.text(3, 100 * m("TSLA") - 0.15, f"{100 * m('TSLA'):+.1f}%", ha="center", va="top", fontsize=10, fontweight="bold")
a.axhline(0, color=INK2, lw=1); a.set_xticks(range(4), [p[0] for p in parts] + ["TSLA\ntotal"], fontsize=9); a.set_ylim(-7.5, 1.5)
a.set_title(f"(b) TSLA: essentially all of it is Musk/Texas.\nLeftover = {left / e.std():.1f} standard deviations of a normal TSLA day", loc="left")
fig.suptitle(f"How much of TSLA's drop is the Musk/Texas story? ({asof:%H:%M} ET premarket vs Tue close)", x=0.01, ha="left", fontsize=13.5, fontweight="bold", color=INK)
fig.text(0.01, 0.01, "Betas: 250 daily returns to Tue Nov 3 (Yahoo). AI-infra factor = mean QQQ-residual of CRWV, ORCL, VST, PLTR, IREN; TSLA's loading on it over the year is 0.01 (no link). Log returns in (b).", fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.03, 1, 0.93)); plt.savefig(O / "tsla_decomp.png", dpi=150, facecolor=BG)
