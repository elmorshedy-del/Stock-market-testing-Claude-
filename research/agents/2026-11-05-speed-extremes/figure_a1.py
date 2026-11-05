import json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np
from pathlib import Path
O = Path(__file__).resolve().parent / "out"; R = json.load(open(O / "per_name.json"))
CTX = {"1997-10-27": "Asian crisis mini-crash", "2008-09-29": "Lehman / TARP vote fails", "2011-08-04": "euro crisis", "2011-08-08": "US downgrade",
       "2016-06-24": "Brexit", "2017-05-17": "Comey memo", "2018-02-05": "Volmageddon", "2018-10-10": "rates spike", "2018-10-24": "Q4-2018 selloff",
       "2019-05-13": "China trade war", "2020-02-24": "COVID starts", "2020-03-09": "COVID", "2020-03-12": "COVID", "2020-03-16": "COVID", "2025-04-03": "tariff shock", "2025-10-10": "China tariff threat"}
fig = plt.figure(figsize=(16, 15), dpi=150); gs = fig.add_gridspec(2, 2, height_ratios=[0.85, 1.25], hspace=0.22, wspace=0.32)
# A: index signature days
a = fig.add_subplot(gs[0, :]); sig = R["index signature (S&P z<=-4 & SOX z<=-3)"]; ks = list(sig); y = np.arange(len(ks))[::-1]
s20 = [sig[k]["S&P +1/+5/+20/+60 %"][2] for k in ks]; x20 = [sig[k]["SOX +1/+5/+20/+60 %"][2] for k in ks]; s1 = [sig[k]["S&P +1/+5/+20/+60 %"][0] for k in ks]
a.barh(y + 0.2, s20, 0.38, color=["#2e7d32" if v > 0 else "#c62828" for v in s20], label="S&P next 20 days")
a.barh(y - 0.2, x20, 0.38, color=["#81c784" if v > 0 else "#ef9a9a" for v in x20], label="chips (SOX) next 20 days")
a.set_yticks(y); a.set_yticklabels([f"{k}  {CTX.get(k, '')}  (S&P {sig[k]['S&P day %']:+.1f}%, SOX {sig[k]['SOX day %']:+.1f}%; next day S&P {v1:+.1f}%)" for k, v1 in zip(ks, s1)], fontsize=8.3)
a.axvline(0, color="k", lw=0.8); a.set_xlim(-34, 34); a.set_xlabel("% return over the next 20 sessions")
t = R["TODAY index"]
a.set_title(f"A. TODAY, on its own: every day since 1994 when the S&P (≤ −4σ) and chips (≤ −3σ) both fell this hard. Today: S&P {t['S&P z']:+.1f}σ, SOX {t['SOX z']:+.1f}σ (live)", loc="left", fontweight="bold", fontsize=11)
a.legend(frameon=False, fontsize=8.5, loc="lower right")
up = sum(v > 0 for v in s20); a.text(33, len(ks) - 0.6, f"S&P higher 20 days later: {up} of {len(ks)}\nthe 2 disasters: Lehman 2008, COVID start 2020", ha="right", va="top", fontsize=9, bbox=dict(fc="white", ec="#ccc"))
# B, C per-name strips
def strip(ax, kind, title):
    d = R[kind]; names = sorted(d, key=lambda s: d[s]["today value"])[::-1]
    for i, s in enumerate(names):
        e = [v for v in d[s]["episodes"].values() if v["fwd20 %"] is not None and v["lower close within 20"] is not None]
        for v in e:
            ax.scatter(np.clip(v["fwd20 %"], -60, 60), i + np.random.uniform(-0.18, 0.18), s=16, color="#c62828" if v["lower close within 20"] else "#2e7d32", alpha=0.75, lw=0)
        nb = sum(v["best bounce within 20 %"] >= 5 for v in e); nl = sum(not v["lower close within 20"] for v in e)
        ax.text(62, i, f"{nb}/{len(e)} bounced ≥5% · low held {nl}/{len(e)}", va="center", fontsize=7.6)
    ax.set_yticks(range(len(names))); ax.set_yticklabels([f"{s.replace('^','')} ({d[s]['today value']:+.1f})" for s in names], fontsize=8.3)
    ax.axvline(0, color="k", lw=0.8); ax.set_xlim(-62, 105); ax.set_xticks([-60, -30, 0, 30, 60]); ax.set_xlabel("% return 20 sessions later (each dot = one past episode)")
    ax.set_title(title, loc="left", fontweight="bold", fontsize=10.5); ax.spines[["top", "right"]].set_visible(False)
strip(fig.add_subplot(gs[1, 0]), "today", "B. Each name's own days as bad as TODAY (1-day σ in brackets)\n    green dot = low held 20 days · red dot = a lower close came first")
strip(fig.add_subplot(gs[1, 1]), "weeks", "C. Each name's own months as bad as the PAST 4 WEEKS (20-day σ)\n    same colours")
a.spines[["top", "right", "left"]].set_visible(False)
fig.suptitle("Yes, it's extreme, today and over the weeks. History: a bounce usually comes, but a lower low usually comes first.", x=0.01, y=0.93, ha="left", fontsize=13.5, fontweight="bold")
fig.text(0.01, 0.003, "Yahoo daily closes; σ = prior 60-day stdev; episodes declustered 20 sessions; each name judged against its own history (survivors only). Today's values live ~12:00 ET. Pre-registered @ a482c6b.", fontsize=7.5, color="#555")
plt.savefig(O / "speed_extremes.png", bbox_inches="tight"); print("ok")
