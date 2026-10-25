"""Amendment 4 in one picture: out/breadth_multiverse.png (reads out/breadth_multiverse.csv, out/breadth_multiverse.json)."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import dossier as Dz

INK, MUTED, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
R = pd.read_csv(Dz.OUT / "breadth_multiverse.csv")
J = json.loads((Dz.OUT / "breadth_multiverse.json").read_text())
R5 = R[R.reading == "5-day mean"]
looks = [f"above {L}-day" for L in (10, 20, 50, 100, 150, 200)]
unis = ["U1 panel 41", "U3 panel ex-mega (35)", "U2 panel + 40 (81)", "U4 81 ex-mega (73)"]
A = np.array([[R5[(R5.measure == m) & (R5.universe == u)]["AUC (broader -> correction)"].iloc[0] for u in unis] for m in looks])
T = np.array([[R5[(R5.measure == m) & (R5.universe == u)]["today percentile among 21 dips"].iloc[0] for u in unis] for m in looks])
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF})
fig, (a, b) = plt.subplots(1, 2, figsize=(15, 6.2), gridspec_kw={"wspace": 0.62})
im = a.imshow(A, cmap="RdYlGn", vmin=0.4, vmax=1.0, aspect="auto")
for i in range(A.shape[0]):
    for j in range(A.shape[1]):
        a.text(j, i, f"{A[i, j]:.2f}", ha="center", va="center", fontsize=10, color=INK, weight="bold" if A[i, j] >= 0.7 else "normal")
a.set_xticks(range(4), ["41 panel", "41 ex-mega", "81 stocks", "81 ex-mega"])
a.set_yticks(range(6), [m.replace("above ", "% above ") + " avg" for m in looks])
a.set_title(f"Is 50 magic? No: it sits on a plateau. 50- to 200-day breadth separates corrections\nfrom bounces in every universe (AUC 0.73-0.90). Short 10-20 day breadth does not, which fails\n"
            f"the pre-set rule. All 58 versions together beat luck: median AUC {J['median AUC, all versions']:.2f}, p {J['multiverse p (shuffled medians >= observed)']:.3f}",
            loc="left", fontsize=9.5, color=INK)
fig.colorbar(im, ax=a, fraction=0.046, pad=0.03, label="AUC (0.5 = coin flip)")
im2 = b.imshow(T * 100, cmap="RdYlGn_r", vmin=0, vmax=100, aspect="auto")
for i in range(T.shape[0]):
    for j in range(T.shape[1]):
        b.text(j, i, f"{100 * T[i, j]:.0f}", ha="center", va="center", fontsize=10, color=INK)
b.set_xticks(range(4), ["41 panel", "41 ex-mega", "81 stocks", "81 ex-mega"])
b.set_yticks(range(6), [m.replace("above ", "% above ") + " avg" for m in looks])
b.set_title("Today's dip (start Oct 16): percentile of its breadth among the 21 past dips\n"
            "On every version that works (50-200 day), today sits at the 5th-24th percentile:\n"
            "narrower than almost every dip, and below all 8 corrections in about half of all versions", loc="left", fontsize=9.5, color=INK)
fig.colorbar(im2, ax=b, fraction=0.046, pad=0.03, label="percentile (low = narrow = bounce side)")
fig.savefig(Dz.OUT / "breadth_multiverse.png", dpi=140, bbox_inches="tight", facecolor=SURF)
