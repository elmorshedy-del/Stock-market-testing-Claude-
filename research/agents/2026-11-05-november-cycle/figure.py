import json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np
from pathlib import Path
O = Path(__file__).resolve().parent / "out"; R = json.load(open(O / "cycle.json"))
fig, ax = plt.subplots(1, 3, figsize=(16, 6), dpi=150, gridspec_kw=dict(width_ratios=[1, 1.25, 1.25]))
G, Rd, B, Gy = "#2e7d32", "#c62828", "#1565c0", "#9e9e9e"
# A: November
a = ax[0]; n1 = R["N1"]; p1 = R["P1"]
vals = [100 * n1["all months share >= -1%"], 100 * n1["share >= -1%"], 100 * n1["bear share >= -1%"]]
a.bar([0, 1, 2], vals, color=[Gy, G, "#f9a825"], width=0.6)
for i, v in enumerate(vals): a.text(i, v + 1.5, f"{v:.0f}%", ha="center", fontweight="bold")
a.set_xticks([0, 1, 2]); a.set_xticklabels(["any month", "Novembers\n(76)", "bear-market\nNovembers (24)"], fontsize=9)
a.set_ylim(0, 105); a.set_ylabel("% closing flat or up (≥ −1%)")
a.set_title("A. November is better than average…", loc="left", fontweight="bold", fontsize=11)
a.text(0.5, 0.17, f"…but after a weak first 4 days,\nNovember's rest of month: {p1['Nov rest mean %']:+.1f}%\nother months: {p1['other rest mean %']:+.1f}%\n→ no special November rescue\n(13 cases, p = {p1['p (one-sided, permutation)']:.2f})",
       transform=a.transAxes, ha="center", fontsize=9, bbox=dict(fc="white", ec="#ccc"))
a.text(0.5, -0.2, "7 of 24 bear Novembers lost >1%\n(1973 −11%, 1987 −9%, 2000 −8%, 2008 −7%)", transform=a.transAxes, ha="center", fontsize=8.5, color=Rd)
# B: tech-rotation Novembers
b = ax[1]; n3 = R["N3"]; yrs = sorted(n3, key=int); y = np.arange(len(yrs))
spx = [n3[k]["SPX rest %"] for k in yrs]; rat = [n3[k]["NDX/SPX rest %"] for k in yrs]
b.barh(y + 0.2, spx, 0.38, color=G, label="S&P, rest of November")
b.barh(y - 0.2, rat, 0.38, color=["#7b1fa2" if v > 0 else "#ce93d8" for v in rat], label="tech vs S&P, rest of November")
b.axvline(0, color="k", lw=0.8)
b.set_yticks(y); b.set_yticklabels([f"{k}  (tech start {n3[k]['NDX/SPX start %']:+.1f}%)" for k in yrs], fontsize=8.5)
b.set_xlabel("% from session 4 to month end")
b.set_title("B. Novembers that opened with tech lagging", loc="left", fontweight="bold", fontsize=11)
b.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
t = R["TODAY Nov 2026 (live)"]
b.text(0.03, 0.985, f"S&P recovered 7/7. Tech's lead came back only 3/7.\nBut today's tech start ({t['NDX/SPX start %']:+.1f}%) is deeper than any November\n(prior worst 2022 −2.3%). Exploratory: all 17 months that\nopened ≤ −3% (8 in 2000–02): S&P rest of month up only 41%.",
       transform=b.transAxes, fontsize=8.3, va="top", color="#333", bbox=dict(fc="white", ec="#ccc"))
b.set_ylim(-0.8, len(yrs) + 2.2)
# C: monthly cycle
c = ax[2]; sp = R["segment profile"]; segs = ["S1", "S2", "S3", "S4"]; x = np.arange(4)
bu = [sp["bull"][s]["ret bp/day"] for s in segs]; be = [sp["bear"][s]["ret bp/day"] for s in segs]
c.bar(x - 0.2, bu, 0.38, color=G, label=f"bull months ({sp['bull']['n months']})")
c.bar(x + 0.2, be, 0.38, color=Rd, label=f"bear months ({sp['bear']['n months']})")
c.axhline(0, color="k", lw=0.8)
c.set_xticks(x); c.set_xticklabels(["days 1–4", "to expiry wk", "expiry week", "after expiry"], fontsize=9)
c.set_ylabel("S&P average return, bp per day")
c.set_title("C. The monthly cycle (S&P 1950–2026)", loc="left", fontweight="bold", fontsize=11)
c.legend(fontsize=8, frameon=False, loc="lower center", ncol=2)
c.text(0.03, 0.97, "PASS  bull: first 4 days strongest (passes)\nFAIL  'moves slow into expiry': small, not proven\nFAIL  bear = opposite? No: first days still best;\n           bear weakness sits mid-month, into expiry",
       transform=c.transAxes, fontsize=8.5, va="top")
c.set_ylim(-5, 19)
for a_ in ax: a_.spines[["top", "right"]].set_visible(False)
fig.suptitle("November alone won't rescue this. In similar Novembers the S&P recovered but tech's lead mostly didn't; today is more extreme than all of them.", x=0.01, ha="left", fontsize=13, fontweight="bold")
fig.text(0.01, 0.005, f"Source: Yahoo ^GSPC 1950–, ^NDX 1985–; regime = S&P vs 200-day at prior month end. Pre-registered @ c4e27cf. Today is live (session 4, S&P start {t['SPX start %']:+.2f}%), provisional.", fontsize=7.5, color="#555")
plt.tight_layout(rect=(0, 0.03, 1, 0.94)); plt.savefig(O / "november_cycle.png"); print("ok")
