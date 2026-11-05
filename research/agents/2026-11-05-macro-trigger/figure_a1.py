"""Descriptive picture for A1 (the test itself is a1.py). Re-derives the event table the same way."""
import json, sys, runpy, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parent; R = json.load(open(H / "out" / "a1.json"))
sys.argv = ["a1.py", sys.argv[1]]; import io, contextlib
with contextlib.redirect_stdout(io.StringIO()): ns = runpy.run_path(str(H / "a1.py"))
S = ns["S"]; E = ns["E"]
fig, ax = plt.subplots(1, 2, figsize=(13, 5.4), dpi=150, gridspec_kw=dict(width_ratios=[1.1, 1]))
a = ax[0]; bins = [0, 0.5, 1.5, 9]; lab = ["in line\n(|z| < 0.5)", "moderate\n(0.5–1.5)", "big surprise\n(> 1.5)"]
for grp, m, c, off in (("high gamma (GEX ≥ 50th pct)", S.LOW <= 0.5, "#1565c0", -0.2), ("low gamma (GEX ≤ 30th pct)", S.LOW >= 0.7, "#c62828", 0.2)):
    X = S[m]; k = pd.cut(X.az, bins, labels=False, right=False); v = [100 * X[k == i].gap.abs().mean() for i in range(3)]; n = [int((k == i).sum()) for i in range(3)]
    a.bar(np.arange(3) + off, v, 0.38, color=c, label=grp)
    for i in range(3): a.text(i + off, v[i] + 0.01, f"{v[i]:.2f}%\nn={n[i]}", ha="center", fontsize=7.5)
a.set_xticks(range(3)); a.set_xticklabels(lab, fontsize=9); a.set_ylabel("average opening gap size, % (either direction)")
a.set_title("PASSES: low gamma makes the data reaction bigger", loc="left", fontweight="bold", fontsize=11)
a.legend(frameon=False, fontsize=8.5, loc="upper left"); a.set_ylim(0, None)
b = ax[1]; J = E[E.type == "jobs"].tail(6)
for r in J.itertuples():
    c = "#2e7d32" if r.gap > 0 else "#c62828"
    b.scatter(r.z, 100 * r.gap, s=70, color=c, zorder=3); b.annotate(r.date.strftime("%b"), (r.z, 100 * r.gap), xytext=(6, 4), textcoords="offset points", fontsize=8.5)
b.axhline(0, color="k", lw=0.8); b.axvline(0, color="#999", lw=0.8)
b.set_xlabel("payrolls surprise (z):  ← weaker than expected  |  stronger →"); b.set_ylabel("SPY opening gap, %")
b.set_title("Last 6 jobs reports: weak prints gapped up 3 of 3, strong 1 of 3", loc="left", fontweight="bold", fontsize=11)
b.text(0.02, 0.04, "only 6 points; over 24 reports the link is ~0\n(the market's 'good news' keeps flipping)", transform=b.transAxes, fontsize=8, color="#555")
for x in ax: x.spines[["top", "right"]].set_visible(False)
fig.suptitle("Your amplification point holds. 'Surge after drops' and 'extends after the open' do not.", x=0.01, ha="left", fontsize=12.5, fontweight="bold")
fig.text(0.01, 0.01, f"SPY, 339 jobs/CPI days 2012–2026; surprise = actual vs consensus (ForexFactory). A passes (Holm 0.047; strongest 2012–19). B relief asymmetry fails (p 0.95). C follow-through fails (p 0.57). Pre-registered @ 1e8f568.", fontsize=7.3, color="#555")
plt.tight_layout(rect=(0, 0.03, 1, 0.93)); plt.savefig(H / "out" / "macro_trigger_a1.png"); print("ok")
