"""Calendar-mechanics figure: (a) late-September weakness by market and era, (b) S&P around the 3rd Friday by era,
(c) hemisphere test, (d) single-name tests. Usage: python figure.py -> out/calendar_mechanics.png"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; O = HERE / "out"
FD, PR, PA, PC = (json.load(open(O / f)) for f in ("figdata.json", "profiles.json", "partA.json", "partC.json"))
PB = json.load(open(O / "partB.json")) if (O / "partB.json").exists() else None
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
C1, C2 = "#2a78d6", "#eb6834"        # categorical slots 1, 2
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(2, 2, figsize=(15.5, 10.5)); plt.subplots_adjust(hspace=0.42, wspace=0.55)


def clean(a):
    for s in ("top", "right"): a.spines[s].set_visible(False)
    a.grid(axis="x", color=GRID, lw=0.6); a.set_axisbelow(True)


# (a) late September by market and era
a = ax[0, 0]; L = FD["late_sep"]
for i, r in enumerate(L):
    pre = r["group"].startswith("S&P 1928") or r["group"].startswith("S&P 1950")
    col = C1 if pre else C2
    a.plot([r["lo"], r["hi"]], [i, i], color=col, lw=2, alpha=0.7); a.plot(r["est"], i, "o", ms=8, color=col, mec="white", mew=2)
    a.text(max(r["hi"], 0) + 1.5, i, f"{r['est']:+.0f} bp/day  ({r['years']} yrs)", va="center", fontsize=8, color=INK)
a.set_yticks(range(len(L))); a.set_yticklabels([r["group"] for r in L], color=INK); a.invert_yaxis(); a.axvline(0, color=INK2, lw=0.8); clean(a)
a.set_xlabel("late September (sessions after the 3rd Friday) minus all other days, bp per day, 95% CI")
a.set_title("(a) Late-September weakness predates index derivatives and buybacks (blue = before 1983)\nand appears abroad", loc="left", color=INK, fontsize=10)
# (b) S&P around the 3rd Friday, cumulative bp, quarterly months, two eras
a = ax[0, 1]
for key, col, ls in (("1950-1982 quarterly", C1, "-"), ("1983-2025 quarterly", C2, "-"), ("1950-1982 monthly", C1, ":"), ("1983-2025 monthly", C2, ":")):
    p = PR[key]; ks = sorted(int(k) for k in p)
    y = np.cumsum([p[str(k)] for k in ks])                         # cumulative mean return from session -10
    a.plot(ks, y, color=col, ls=ls, lw=2 if ls == "-" else 1.5, label=key)
a.axvline(0.5, color=INK2, lw=0.8); a.text(0.7, a.get_ylim()[1] * 0.9 if a.get_ylim()[1] > 0 else 1, "3rd Friday", fontsize=8, color=INK2)
a.axhline(0, color=GRID, lw=0.8); clean(a); a.legend(fontsize=8, frameon=False)
a.set_xlabel("sessions relative to the 3rd Friday (1 = first session after)"); a.set_ylabel("cumulative mean return from session -10, bp")
a7 = PA["A7 dose: Spearman(GEX roll-off, S&P sessions 2-6 after expiry)"]
a.set_title(f"(b) S&P around expiry: no era break. Dose test (GEX roll-off vs next week):\nρ {a7['est']:+.2f} [{a7['ci95'][0]:+.2f}, {a7['ci95'][1]:+.2f}], Holm p {a7['p_holm']:.2f}", loc="left", color=INK, fontsize=10)
# (c) hemisphere test
a = ax[1, 0]
north = PC["C4 northern control: late-Sep minus late-Mar (bp/day)"]["by_index"]; south = PC["C3 southern pooled (AU, NZ, ZA): late-Mar minus late-Sep (bp/day)"]["by_index"]
names = {"SPX": "S&P 500", "DAX": "DAX", "FTSE": "FTSE", "N225": "Nikkei", "AU": "Australia", "NZ": "New Zealand", "ZA": "South Africa"}
rows = [(names[k], v, C2) for k, v in north.items()] + [(names[k], v, C1) for k, v in south.items()]
for i, (nm, v, col) in enumerate(rows):
    a.barh(i, v, color=col, height=0.6); a.text(0.6 if v < 0 else v + 0.6, i, f"{v:+.0f}", va="center", ha="left", fontsize=8, color=INK)
a.set_yticks(range(len(rows))); a.set_yticklabels([r[0] for r in rows], color=INK); a.invert_yaxis(); a.axvline(0, color=INK2, lw=0.8); clean(a)
a.set_xlabel("local autumn window minus local spring window (10 sessions from the equinox), bp per day")
a.set_title("(c) Seasonal-mood test: northern autumns are weak (orange), southern autumns are not (blue).\nThe south does not mirror, so mood is not the origin", loc="left", color=INK, fontsize=10)
# (d) single-name tests
a = ax[1, 1]
if PB:
    T = PB["family"]; ks = list(T)
    for i, k in enumerate(ks):
        v = T[k]; lo, hi = v["ci95"]; e = v["est"]
        a.plot([lo, hi], [i, i], color=INK2, lw=1.6); a.plot(e, i, "o", ms=8, mfc=INK if v["sign_as_predicted"] else "white", mec=INK, mew=1.6)
        a.text(max(hi, 0) + 0.03 * (abs(hi - lo) + 0.1), i, ("  PASSES Holm" if v["pass"] else f"  Holm p {v['p_holm']:.2f}") + (f"  n={v.get('n_context', v.get('n', ''))}"), va="center", fontsize=8, color=INK if v["pass"] else INK2)
    SH = {"B1": "B1 gap-up after a quarterly expiry", "B2": "B2 earnings gap-up, 9 new names", "B3": "B3 call-wall cap (MSFT, MU)",
          "B4": "B4 options-unwind pressure", "B5": "B5 last 30 min before a report"}
    a.set_yticks(range(len(ks))); a.set_yticklabels([SH[k[:2]] for k in ks], fontsize=8.5, color=INK); a.invert_yaxis(); a.axvline(0, color=INK2, lw=0.8); clean(a)
    a.set_xlabel("effect (B1-B3: first-hour σ; B4: ρ; B5: % in the last 30 min)\nfilled = sign as predicted")
a.set_title("(d) Single names: scheduled flows at the open and the close", loc="left", color=INK, fontsize=10)
fig.suptitle("Tracing calendar weakness to its origin: expiry, buybacks, cash drains and seasonal mood tested against each other", fontsize=12, color=INK, x=0.01, ha="left")
fig.savefig(O / "calendar_mechanics.png", dpi=130, bbox_inches="tight", facecolor="#fcfcfb"); print("saved")
