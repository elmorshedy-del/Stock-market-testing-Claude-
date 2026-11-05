import json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, pandas as pd, numpy as np
from pathlib import Path
O = Path(__file__).resolve().parent / "out"; R = json.load(open(O / "trigger.json"))
X = pd.DataFrame(R["SETUP release days"]).T; X["r"] = X["S&P %"].astype(float); X = X.sort_values("r")
fig, ax = plt.subplots(figsize=(11, 6), dpi=150)
for i, (t, row) in enumerate(X.iterrows()):
    c = "#2e7d32" if row.r > 0 else "#c62828"; shock = t.startswith("2020-03") or t.startswith("2025-04")
    ax.barh(i, row.r, color=c, alpha=0.35 if shock else 0.9, height=0.75)
    ax.text(row.r + (0.08 if row.r > 0 else -0.08), i, f"{t[:7]} {row.what.upper()}" + ("  (COVID/tariff)" if shock else ""), va="center", ha="left" if row.r > 0 else "right", fontsize=7.2)
ax.axvline(0, color="k", lw=0.8); ax.set_yticks([]); ax.set_xlim(-8.5, 4.5)
ax.set_xlabel("S&P return on the release day, %")
h = R["H1 SETUP"]
ax.set_title("After a 3%+ drop in low gamma, jobs/CPI days move big, but not reliably up", loc="left", fontweight="bold")
ax.text(-8.3, len(X) - 1.5, f"33 release days (2012–2026)\nup: 14 of 33 · big up ≥1%: 9 · big down ≤−1%: 14\nnon-release days in the same setup: {100*h['non-release share up']:.0f}% up\n\nJobs days: 3 of 12 up\nCPI days: 11 of 21 up\nWithout COVID / tariff days: 48% up (coin flip)",
        fontsize=9, va="top", bbox=dict(fc="white", ec="#ccc"))
ax.spines[["top", "right", "left"]].set_visible(False)
fig.text(0.01, 0.01, "Release dates: FRED (Employment Situation, CPI). Setup = S&P ≥3% below 10-day high and GEX ≤30th pct at prior close. Pre-registered @ f7efce9. H1 fails (p 0.98).", fontsize=7.5, color="#555")
plt.tight_layout(rect=(0, 0.03, 1, 1)); plt.savefig(O / "macro_trigger.png"); print("ok")
